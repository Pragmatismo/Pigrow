"""Bounded local-network discovery and its selectable wx dialog.

The backend has no wx dependency. Scanning only runs when the user clicks Scan;
Raspberry Pi identification is tentative until an authenticated connection.
"""

import concurrent.futures
import ipaddress
import json
import platform
import queue
import re
import shutil
import socket
import subprocess
import sys
import threading
import time

try:
    import wx
except ImportError:
    wx = None

PI_MAC_PREFIXES = (
    "b8:27:eb", "dc:a6:32", "e4:5f:01", "d8:3a:dd", "2c:cf:67", "28:cd:c1",
)
MAX_SCAN_HOSTS = 4096
HOSTNAME_PATTERN = re.compile(r"(?=.{1,253}$)[a-zA-Z0-9_](?:[a-zA-Z0-9_.-]*[a-zA-Z0-9_])?\.?$")


def _run_command(argv, timeout=2.0, cancel_event=None):
    """Run an optional system utility without a shell, retaining timed-out output."""
    if cancel_event is not None and cancel_event.is_set():
        return ""
    try:
        process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   text=True, errors="replace",
                                   creationflags=(getattr(subprocess, "CREATE_NO_WINDOW", 0)
                                                  if platform.system() == "Windows" else 0))
    except (OSError, ValueError):
        return ""
    deadline = time.monotonic() + timeout
    while True:
        try:
            output, _ = process.communicate(timeout=0.1)
            return output
        except subprocess.TimeoutExpired:
            if time.monotonic() < deadline and not (cancel_event and cancel_event.is_set()):
                continue
            process.kill()
            output, _ = process.communicate()
            return output


def parse_targets(text, max_hosts=MAX_SCAN_HOSTS):
    """Expand CIDRs, legacy IPv4 prefixes, IPs and hostnames into bounded targets."""
    targets = []
    seen = set()
    for value in re.split(r"[\s,;]+", text.strip()):
        if not value:
            continue
        if re.fullmatch(r"(?:\d{1,3}\.){3}", value):
            value += "0/24"
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            if "/" in value or not HOSTNAME_PATTERN.fullmatch(value) or re.fullmatch(r"[\d.]+", value):
                raise ValueError("Invalid IP, subnet or hostname: " + value)
            values = [value.rstrip(".")]
        else:
            if network.version == 6 and network.prefixlen != 128:
                raise ValueError("Enter individual IPv6 addresses; IPv6 subnet sweeps are too large.")
            if network.num_addresses > max_hosts + 2:
                raise ValueError("Use smaller subnets (at most {} addresses per scan).".format(max_hosts))
            values = (str(host) for host in network.hosts())
        for target in values:
            key = target.lower()
            if key not in seen:
                seen.add(key)
                targets.append(target)
                if len(targets) > max_hosts:
                    raise ValueError("Limit each scan to {} addresses; scan other subnets separately.".format(max_hosts))
    if not targets:
        raise ValueError("Enter an IP address, hostname or subnet to scan.")
    return targets


def _small_network(address, prefix=None):
    try:
        ip = ipaddress.ip_address(address)
        if ip.version != 4 or ip.is_loopback or ip.is_link_local or not ip.is_private:
            return None
        # Avoid silently sweeping very large routed networks.
        return str(ipaddress.ip_network("{}/{}".format(ip, max(24, int(prefix or 24))), strict=False))
    except (ValueError, TypeError):
        return None


def local_default_targets(addresses=None):
    """Read local interfaces/routes and known locations, without sending probes."""
    defaults = []

    def add(value):
        if value and value not in defaults:
            defaults.append(value)

    if shutil.which("ip"):
        try:
            interfaces = json.loads(_run_command(["ip", "-j", "-4", "address", "show"], timeout=1))
        except (ValueError, TypeError):
            interfaces = []
        for interface in interfaces:
            if interface.get("ifname", "").startswith(("lo", "docker", "veth", "br-")):
                continue
            for address in interface.get("addr_info", []):
                add(_small_network(address.get("local", ""), address.get("prefixlen")))
        try:
            routes = json.loads(_run_command(["ip", "-j", "-4", "route", "show"], timeout=1))
        except (ValueError, TypeError):
            routes = []
        for route in routes:
            if route.get("dev", "").startswith(("lo", "docker", "veth", "br-")):
                continue
            destination = route.get("dst", "")
            try:
                network = ipaddress.ip_network(destination)
            except ValueError:
                continue
            if network.version == 4 and network.is_private and 24 <= network.prefixlen < 32:
                add(str(network))
    elif platform.system() == "Windows":
        config = _run_command(["ipconfig"], timeout=2)
        for address in re.findall(r"(?:IPv4[^:\n]*:|IP Address[^:\n]*:)\s*([\d.]+)", config):
            add(_small_network(address))
    elif shutil.which("ifconfig"):
        config = _run_command(["ifconfig"], timeout=2)
        for address in re.findall(r"\binet\s+(?:addr:)?([\d.]+)", config):
            add(_small_network(address))
    for address in addresses or []:
        address = str(address or "").strip()
        if not address:
            continue
        network = _small_network(address)
        if network:
            add(network)
        else:
            try:
                parse_targets(address, max_hosts=1)
            except ValueError:
                continue
            add(address)
    return defaults or ["192.168.1.0/24"]


def is_pi_mac(mac):
    return str(mac or "").lower().replace("-", ":").startswith(PI_MAC_PREFIXES)


def is_pi_hostname(hostname):
    return bool(re.search(r"(?:^|[ ._-])(?:raspberry[ _-]?pi|pigrow)(?:[ ._-]|\d|$)", hostname or "", re.I))


def read_neighbours(cancel_event=None):
    if shutil.which("ip"):
        text = _run_command(["ip", "neigh", "show"], cancel_event=cancel_event)
    else:
        text = _run_command(["arp", "-a"], cancel_event=cancel_event)
    neighbours = {}
    for line in text.splitlines():
        mac = re.search(r"\b(?:[\da-fA-F]{2}[:-]){5}[\da-fA-F]{2}\b", line)
        if not mac:
            continue
        # The cache may contain FAILED entries, which have no MAC and are skipped.
        for word in line.split():
            try:
                address = str(ipaddress.ip_address(word.strip("()")))
            except ValueError:
                continue
            neighbours[address] = mac.group().lower().replace("-", ":")
            break
    return neighbours


def _system_resolve(value, reverse=False, cancel_event=None):
    """Use bounded native tools when sys.executable is a bundled GUI executable."""
    tools = [
        ("getent", ["getent", "hosts" if reverse else "ahosts", value]),
        ("dscacheutil", ["dscacheutil", "-q", "host", "-a", "ip_address" if reverse else "name", value]),
        ("dig", ["dig", "+short", "-x", value] if reverse else ["dig", "+short", value]),
        ("nslookup", ["nslookup", value]),
    ]
    for tool, argv in tools:
        if cancel_event and cancel_event.is_set():
            break
        if not shutil.which(tool):
            continue
        output = _run_command(argv, timeout=1.5 if reverse else 2, cancel_event=cancel_event)
        addresses = []
        names = []
        if tool == "getent":
            for line in output.splitlines():
                words = line.split()
                if words:
                    addresses.append(words[0])
                    names.extend(words[1:])
        elif tool == "dscacheutil":
            addresses = re.findall(r"^\s*(?:ip_address|ipv6_address):\s*(\S+)", output, re.M)
            names = re.findall(r"^\s*name:\s*(\S+)", output, re.M)
        elif tool == "dig":
            addresses = output.splitlines()
            names = output.splitlines()
        else:
            names = re.findall(r"(?:name\s*=|^\s*Name:)\s*(\S+)", output, re.I | re.M)
            # Discard the leading DNS server's own Address: line. It is never a
            # result for the hostname being sought, even if the query fails.
            answer = re.search(r"^\s*Name:.*$", output, re.I | re.M)
            if answer:
                addresses = output[answer.end():].split()
        if reverse:
            for name in names:
                name = name.rstrip(".")
                if HOSTNAME_PATTERN.fullmatch(name) and name != value and not re.fullmatch(r"[\d.]+", name):
                    return name
        else:
            result = []
            for address in addresses:
                try:
                    address = str(ipaddress.ip_address(address))
                except ValueError:
                    continue
                if address not in result:
                    result.append(address)
            if result:
                return result
    return "" if reverse else []


def resolve_hostname(hostname, cancel_event=None):
    """Bound DNS/mDNS resolution by running the system resolver in a subprocess."""
    if getattr(sys, "frozen", False):
        return _system_resolve(hostname, cancel_event=cancel_event)
    script = ("import json,socket,sys; "
              "print(json.dumps(list(dict.fromkeys(x[4][0] for x in "
              "socket.getaddrinfo(sys.argv[1],None,0,socket.SOCK_STREAM)))))")
    output = _run_command([sys.executable, "-c", script, hostname], timeout=2, cancel_event=cancel_event)
    try:
        return [str(ipaddress.ip_address(value)) for value in json.loads(output)]
    except (ValueError, TypeError):
        return []


def reverse_hostname(address, cancel_event=None):
    if getattr(sys, "frozen", False):
        return _system_resolve(address, reverse=True, cancel_event=cancel_event)
    script = ("import json,socket,sys; print(json.dumps(socket.gethostbyaddr(sys.argv[1])[0]))")
    output = _run_command([sys.executable, "-c", script, address], timeout=1.5, cancel_event=cancel_event)
    try:
        hostname = json.loads(output).rstrip(".")
    except (ValueError, TypeError, AttributeError):
        return ""
    return hostname if HOSTNAME_PATTERN.fullmatch(hostname) and hostname != address else ""


def parse_avahi_output(text):
    devices = []
    seen = set()
    for line in text.splitlines():
        parts = line.split(";")
        if len(parts) < 9 or parts[0] != "=":
            continue
        # Avahi's machine-readable output escapes spaces and punctuation as
        # decimal byte codes, including the "Raspberry Pi" service label.
        unescape = lambda value: re.sub(r"\\(\d{3})", lambda match: chr(int(match.group(1))), value)
        hostname = unescape(parts[6]).rstrip(".")
        try:
            address = str(ipaddress.ip_address(parts[7]))
        except ValueError:
            continue
        if (address, hostname) in seen:
            continue
        seen.add((address, hostname))
        pi = is_pi_hostname(hostname) or is_pi_hostname(unescape(parts[3]))
        devices.append({"address": address, "hostname": hostname, "is_pi": pi,
                        "evidence": "mDNS" + (", Raspberry Pi name" if pi else "")})
    return devices


def discover_mdns(cancel_event=None):
    if shutil.which("avahi-browse"):
        output = _run_command(["avahi-browse", "--all", "--resolve", "--parsable", "--terminate"],
                              timeout=3, cancel_event=cancel_event)
        return parse_avahi_output(output)
    # Hostnames entered in the targets still use the platform resolver, including
    # .local names on systems with Avahi, Bonjour or native mDNS support.
    return []


def probe_address(address, ssh_port=22, ping=True, cancel_event=None):
    if cancel_event and cancel_event.is_set():
        return None
    ssh_open = False
    try:
        with socket.create_connection((address, ssh_port), timeout=0.6):
            ssh_open = True
    except (OSError, ValueError):
        pass
    reachable = ssh_open
    if not reachable and ping and not (cancel_event and cancel_event.is_set()) and shutil.which("ping"):
        system = platform.system()
        args = ["ping", "-n", "1", "-w", "700", address] if system == "Windows" else ["ping", "-n", "-c", "1", address]
        output = _run_command(args, timeout=1, cancel_event=cancel_event)
        reachable = bool(re.search(r"(?:ttl[=:]|bytes from|bytes=)", output, re.I))
    if not reachable or (cancel_event and cancel_event.is_set()):
        return None
    hostname = reverse_hostname(address, cancel_event)
    pi = is_pi_hostname(hostname)
    evidence = ["SSH port open" if ssh_open else "Ping reply"]
    if pi:
        evidence.append("Raspberry Pi name")
    return {"address": address, "hostname": hostname, "is_pi": pi, "evidence": ", ".join(evidence)}


def discover_devices(targets, cancel_event=None, ssh_port=22, ping=True, use_mdns=True,
                     on_progress=None, on_device=None, workers=32, probe=None):
    """Discover selected targets with bounded concurrency and cooperative cancellation."""
    cancel_event = cancel_event or threading.Event()
    probe = probe or probe_address
    devices = {}
    resolved_targets = []
    hostname_hints = {}

    def emit(device):
        device = dict(device)
        previous = devices.get(device["address"])
        if previous:
            device["hostname"] = device.get("hostname") or previous.get("hostname", "")
            device["is_pi"] = bool(device.get("is_pi") or previous.get("is_pi"))
            evidence = list(dict.fromkeys((previous.get("evidence", "") + ", " + device.get("evidence", "")).split(", ")))
            device["evidence"] = ", ".join(item for item in evidence if item)
        devices[device["address"]] = device
        if on_device:
            on_device(dict(device))

    if cancel_event.is_set():
        return []
    if use_mdns:
        if on_progress:
            on_progress("Looking for local mDNS announcements...")
        for device in discover_mdns(cancel_event):
            emit(device)
            resolved_targets.append(device["address"])
            if device.get("hostname"):
                hostname_hints[device["address"]] = device["hostname"]
    for target in targets:
        if cancel_event.is_set():
            break
        try:
            addresses = [str(ipaddress.ip_address(target))]
        except ValueError:
            addresses = resolve_hostname(target, cancel_event)
            for address in addresses:
                hostname_hints[address] = target
        resolved_targets.extend(addresses)
    resolved_targets = list(dict.fromkeys(resolved_targets))
    if len(resolved_targets) > MAX_SCAN_HOSTS:
        raise ValueError("Too many resolved addresses; use smaller scan targets.")
    neighbours = read_neighbours(cancel_event)

    def add_cached_pis():
        # A Pi may answer ARP while ICMP is blocked and SSH is not installed yet.
        # Keep this evidence tentative; connection authenticates the device later.
        for address in resolved_targets:
            if not is_pi_mac(neighbours.get(address)):
                continue
            device = devices.get(address)
            if device is None:
                emit({"address": address, "hostname": hostname_hints.get(address, ""),
                      "is_pi": True, "evidence": "Raspberry Pi MAC (neighbour cache)"})
            elif "Raspberry Pi MAC" not in device["evidence"]:
                device = dict(device)
                device["is_pi"] = True
                device["evidence"] += ", Raspberry Pi MAC"
                emit(device)

    add_cached_pis()
    done = 0
    # Only workers are submitted initially; do not queue thousands of jobs after a
    # cancel. Every outstanding network operation has its own short timeout.
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 32)))
    pending = {}
    targets_iter = iter(resolved_targets)

    def submit_next():
        if cancel_event.is_set():
            return
        address = next(targets_iter, None)
        if address is not None:
            pending[executor.submit(probe, address, ssh_port, ping, cancel_event)] = address

    try:
        for _ in range(max(1, min(workers, 32))):
            submit_next()
        while pending and not cancel_event.is_set():
            finished, _ = concurrent.futures.wait(pending, timeout=0.1,
                                                   return_when=concurrent.futures.FIRST_COMPLETED)
            for future in finished:
                address = pending.pop(future)
                done += 1
                try:
                    device = future.result()
                except Exception:
                    device = None
                if device:
                    device["hostname"] = hostname_hints.get(address) or device.get("hostname", "")
                    device["is_pi"] = bool(device.get("is_pi") or is_pi_hostname(device["hostname"]))
                    if is_pi_mac(neighbours.get(address)):
                        device["is_pi"] = True
                        device["evidence"] += ", Raspberry Pi MAC"
                    emit(device)
                submit_next()
            if finished and on_progress:
                on_progress("Checked {}/{} addresses; found {} devices.".format(done, len(resolved_targets), len(devices)))
    finally:
        for future in pending:
            future.cancel()
        executor.shutdown(wait=True)
    # Pinging / opening SSH populates ARP; refresh after probes to see new MACs.
    if not cancel_event.is_set():
        neighbours.update(read_neighbours(cancel_event))
        add_cached_pis()
    return sorted(devices.values(), key=lambda item: (not item["is_pi"], item["address"]))


if wx is not None:
    class DiscoverIPDialog(wx.Dialog):
        def __init__(self, parent, title="Seek IPs", addresses=None, ssh_port=22):
            super().__init__(parent, title=title, size=(760, 600), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            self.ssh_port = int(ssh_port)
            self.devices = []
            self._choices = []
            self._queue = queue.Queue()
            self._cancel = threading.Event()
            self._worker = None
            self._devices_by_address = {}
            main = wx.BoxSizer(wx.VERTICAL)
            info = wx.StaticText(self, label="Find devices on this LAN or other routed subnets. Enter IPs, hostnames or CIDRs,\n"
                                             "separated by spaces or commas (for example 192.168.1.0/24, raspberrypi.local).\n"
                                             "Devices behind another router need a route or port forwarding; scans cannot cross NAT.\n"
                                             "Pi identification is tentative until you connect. Highlight IPs or hostnames to use.")
            main.Add(info, 0, wx.ALL | wx.EXPAND, 10)
            main.Add(wx.StaticText(self, label="Scan targets:"), 0, wx.LEFT | wx.RIGHT, 10)
            self.targets = wx.TextCtrl(self, value=", ".join(local_default_targets(addresses)), style=wx.TE_MULTILINE, size=(-1, 55))
            main.Add(self.targets, 0, wx.ALL | wx.EXPAND, 10)
            options = wx.BoxSizer(wx.HORIZONTAL)
            self.ping = wx.CheckBox(self, label="Ping devices without SSH")
            self.ping.SetValue(True)
            self.mdns = wx.CheckBox(self, label="Look for mDNS hostnames (Avahi when available)")
            self.mdns.SetValue(True)
            options.Add(self.ping, 0, wx.RIGHT, 15)
            options.Add(self.mdns)
            main.Add(options, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
            self.results = wx.ListCtrl(self, style=wx.LC_REPORT)
            self.results.InsertColumn(0, "IP address / hostname", width=250)
            self.results.InsertColumn(1, "Device", width=110)
            self.results.InsertColumn(2, "Evidence", width=330)
            main.Add(self.results, 1, wx.ALL | wx.EXPAND, 10)
            self.status = wx.StaticText(self, label="Ready to scan. No network probes run until Scan is clicked.")
            main.Add(self.status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
            buttons = wx.BoxSizer(wx.HORIZONTAL)
            self.scan_button = wx.Button(self, label="Scan")
            self.stop_button = wx.Button(self, label="Stop")
            self.stop_button.Disable()
            self.use_button = wx.Button(self, wx.ID_OK, label="Use results")
            self.cancel_button = wx.Button(self, wx.ID_CANCEL, label="Cancel")
            buttons.Add(self.scan_button, 0, wx.RIGHT, 5)
            buttons.Add(self.stop_button, 0, wx.RIGHT, 5)
            buttons.AddStretchSpacer()
            buttons.Add(self.use_button, 0, wx.RIGHT, 5)
            buttons.Add(self.cancel_button)
            main.Add(buttons, 0, wx.ALL | wx.EXPAND, 10)
            self.SetSizer(main)
            self.SetMinSize((650, 470))
            self.scan_button.Bind(wx.EVT_BUTTON, self.on_scan)
            self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop)
            self.use_button.Bind(wx.EVT_BUTTON, self.on_use)
            self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)
            self.Bind(wx.EVT_CLOSE, self.on_cancel)
            self.timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._poll, self.timer)
            self.timer.Start(100)

        def on_scan(self, event):
            if self._worker and self._worker.is_alive():
                return
            try:
                targets = parse_targets(self.targets.GetValue())
            except ValueError as error:
                wx.MessageBox(str(error), "Scan targets", wx.OK | wx.ICON_WARNING, self)
                return
            self._cancel.clear()
            self.devices = []
            self._devices_by_address = {}
            self._choices = []
            self.results.DeleteAllItems()
            self.scan_button.Disable()
            self.targets.Disable()
            self.ping.Disable()
            self.mdns.Disable()
            self.stop_button.Enable()
            self.use_button.Disable()
            # Capture all wx values here. Workers only use the queue and backend.
            ping = self.ping.GetValue()
            mdns = self.mdns.GetValue()
            port = self.ssh_port
            self.status.SetLabel("Starting scan...")

            def worker():
                try:
                    result = discover_devices(targets, self._cancel, port, ping, mdns,
                                              on_progress=lambda message: self._queue.put(("status", message)),
                                              on_device=lambda device: self._queue.put(("device", device)))
                    self._queue.put(("done", result))
                except Exception as error:
                    self._queue.put(("error", str(error)))

            self._worker = threading.Thread(target=worker, name="pigrow-discovery", daemon=True)
            self._worker.start()

        def on_stop(self, event):
            self._cancel.set()
            self.stop_button.Disable()
            self.status.SetLabel("Stopping scan; keeping devices already found...")

        def _render_results(self):
            selected = set(self.get_selected_addresses())
            self.results.DeleteAllItems()
            self._choices = []
            self.devices = sorted(self._devices_by_address.values(), key=lambda item: (not item["is_pi"], item["address"]))
            seen = set()
            for device in self.devices:
                for address in (device["address"], device.get("hostname", "")):
                    if not address or address.lower() in seen:
                        continue
                    seen.add(address.lower())
                    row = self.results.InsertItem(self.results.GetItemCount(), address)
                    self.results.SetItem(row, 1, "Raspberry Pi" if device["is_pi"] else "Network device")
                    self.results.SetItem(row, 2, device["evidence"])
                    self._choices.append(address)
                    if address in selected:
                        self.results.Select(row)

        def _poll(self, event):
            changed = False
            while True:
                try:
                    kind, value = self._queue.get_nowait()
                except queue.Empty:
                    break
                if kind == "device":
                    self._devices_by_address[value["address"]] = value
                    changed = True
                elif kind == "status":
                    if not self._cancel.is_set():
                        self.status.SetLabel(value)
                else:
                    if kind == "done":
                        self._devices_by_address = {device["address"]: device for device in value}
                        changed = True
                        self.status.SetLabel(("Scan stopped" if self._cancel.is_set() else "Scan complete") + "; {} devices found. Select locations and click Use results.".format(len(value)))
                    else:
                        self.status.SetLabel("Scan failed: " + value)
                    self.scan_button.Enable()
                    self.targets.Enable()
                    self.ping.Enable()
                    self.mdns.Enable()
                    self.stop_button.Disable()
                    self.use_button.Enable()
            if changed:
                self._render_results()

        def get_devices(self):
            return [dict(device) for device in self.devices]

        def get_selected_addresses(self):
            selected = []
            row = self.results.GetFirstSelected()
            while row != -1:
                if row < len(self._choices):
                    selected.append(self._choices[row])
                row = self.results.GetNextSelected(row)
            return selected

        def get_ip_list(self):
            return self.get_selected_addresses()

        def on_use(self, event):
            if self._worker and self._worker.is_alive():
                return
            self.timer.Stop()
            self.EndModal(wx.ID_OK)

        def on_cancel(self, event):
            self._cancel.set()
            self.timer.Stop()
            if self.IsModal():
                self.EndModal(wx.ID_CANCEL)
            else:
                self.Destroy()
else:
    class DiscoverIPDialog:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("wxPython is required to open the discovery dialog.")
