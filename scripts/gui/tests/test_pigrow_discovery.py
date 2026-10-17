"""Discovery tests use fake probes; they never scan the test machine's network."""

import importlib.util
import json
from pathlib import Path
import subprocess
import threading
import unittest
from unittest import mock

MODULE = Path(__file__).resolve().parents[1] / "panels" / "pigrow_discovery.py"
spec = importlib.util.spec_from_file_location("pigrow_discovery", MODULE)
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


class TargetTests(unittest.TestCase):
    def test_prefix_cidr_hostname_and_single_ip(self):
        targets = discovery.parse_targets("10.20.30.0/30, grow.local; 10.20.30.1 10.20.31.")
        self.assertEqual(targets[:3], ["10.20.30.1", "10.20.30.2", "grow.local"])
        self.assertEqual(len(targets), 257)
        self.assertIn("10.20.31.254", targets)
        self.assertNotIn("10.20.31.255", targets)

    def test_exact_hosts_and_ipv6(self):
        self.assertEqual(discovery.parse_targets("192.168.1.2 ::1 pi.local."),
                         ["192.168.1.2", "::1", "pi.local"])

    def test_reject_oversized_invalid_or_shell_inputs(self):
        for target in ("10.0.0.0/8", "::/64", "1.2.3.999", "pi$(id)", "-bad", "1.2.3.0/no", ""):
            with self.subTest(target=target):
                with self.assertRaises(ValueError):
                    discovery.parse_targets(target)
        with self.assertRaises(ValueError):
            discovery.parse_targets("10.0.0.0/30 10.0.1.0/30", max_hosts=3)

    def test_default_targets_use_interfaces_routed_subnets_and_saved_locations(self):
        interfaces = [{"ifname": "eth0", "addr_info": [{"local": "10.42.3.17", "prefixlen": 16}]},
                      {"ifname": "docker0", "addr_info": [{"local": "172.17.0.1", "prefixlen": 16}]}]
        routes = [{"dst": "default", "dev": "eth0"}, {"dst": "192.168.60.0/24", "dev": "eth0"},
                  {"dst": "192.168.61.0/24", "dev": "veth123"}]
        with mock.patch.object(discovery.shutil, "which", return_value="/usr/bin/ip"), \
                mock.patch.object(discovery, "_run_command", side_effect=[json.dumps(interfaces), json.dumps(routes)]):
            targets = discovery.local_default_targets(["10.42.3.100", "192.168.80.2", "grow.local", ""])
        self.assertEqual(targets, ["10.42.3.0/24", "192.168.60.0/24", "192.168.80.0/24", "grow.local"])


class IdentificationTests(unittest.TestCase):
    def test_multiple_pi_mac_prefixes_and_names(self):
        for prefix in discovery.PI_MAC_PREFIXES:
            self.assertTrue(discovery.is_pi_mac(prefix.upper().replace(":", "-") + "-12-34-56"))
        self.assertFalse(discovery.is_pi_mac("00:11:22:33:44:55"))
        for name in ("raspberrypi.local", "raspberry-pi-4.local", "Pigrow.local", "Raspberry Pi"):
            self.assertTrue(discovery.is_pi_hostname(name))
        for name in ("spigot.local", "printer.local", "laptop.local"):
            self.assertFalse(discovery.is_pi_hostname(name))

    def test_neighbour_parser_supports_linux_windows_and_macos(self):
        output = ("192.168.1.2 dev eth0 lladdr dc:a6:32:01:02:03 REACHABLE\n"
                  "  192.168.1.3  e4-5f-01-01-02-03  dynamic\n"
                  "? (192.168.1.4) at b8:27:eb:01:02:03 on en0 ifscope\n"
                  "192.168.1.5 dev eth0 FAILED\n")
        with mock.patch.object(discovery.shutil, "which", return_value="ip"), \
                mock.patch.object(discovery, "_run_command", return_value=output):
            neighbours = discovery.read_neighbours()
        self.assertEqual(len(neighbours), 3)
        self.assertTrue(discovery.is_pi_mac(neighbours["192.168.1.3"]))

    def test_mdns_provides_hostname_and_tentative_identification(self):
        output = ("+;eth0;IPv4;Service;_ssh._tcp;local\n"
                  "=;eth0;IPv4;Raspberry\\032Pi;_ssh._tcp;local;grow.local;10.1.2.4;22;\n"
                  "=;eth0;IPv4;Service;_workstation._tcp;local;desktop.local;10.1.2.5;9;\n"
                  "=;eth0;IPv4;Raspberry Pi;_ssh._tcp;local;grow.local;10.1.2.4;22;\n")
        devices = discovery.parse_avahi_output(output)
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0]["hostname"], "grow.local")
        self.assertTrue(devices[0]["is_pi"])
        self.assertFalse(devices[1]["is_pi"])

    def test_dns_resolution_uses_cancellable_bounded_subprocess(self):
        cancel = threading.Event()
        with mock.patch.object(discovery, "_run_command", return_value='["10.0.0.7", "fe80::1"]') as command:
            self.assertEqual(discovery.resolve_hostname("grow.local", cancel), ["10.0.0.7", "fe80::1"])
        self.assertEqual(command.call_args.args[0][-1], "grow.local")
        self.assertEqual(command.call_args.kwargs["timeout"], 2)
        self.assertIs(command.call_args.kwargs["cancel_event"], cancel)

    def test_frozen_forward_resolution_never_launches_gui_executable(self):
        output = "10.0.0.7 STREAM grow.local\n10.0.0.7 DGRAM grow.local\nfe80::1 STREAM grow.local\n"
        cancel = threading.Event()
        with mock.patch.object(discovery.sys, "frozen", True, create=True), \
                mock.patch.object(discovery.sys, "executable", "PigrowGUI.exe"), \
                mock.patch.object(discovery.shutil, "which", side_effect=lambda name: "/usr/bin/getent" if name == "getent" else None), \
                mock.patch.object(discovery, "_run_command", return_value=output) as command:
            self.assertEqual(discovery.resolve_hostname("grow.local", cancel), ["10.0.0.7", "fe80::1"])
        self.assertEqual(command.call_args.args[0], ["getent", "ahosts", "grow.local"])
        self.assertIs(command.call_args.kwargs["cancel_event"], cancel)
        self.assertEqual(command.call_args.kwargs["timeout"], 2)

    def test_frozen_reverse_resolution_uses_windows_nslookup(self):
        output = "Server: router.local\nAddress: 10.0.0.1\n\nName: raspberrypi.local\nAddress: 10.0.0.7\n"
        with mock.patch.object(discovery.sys, "frozen", True, create=True), \
                mock.patch.object(discovery.sys, "executable", "PigrowGUI.exe"), \
                mock.patch.object(discovery.shutil, "which", side_effect=lambda name: "nslookup.exe" if name == "nslookup" else None), \
                mock.patch.object(discovery, "_run_command", return_value=output) as command:
            self.assertEqual(discovery.reverse_hostname("10.0.0.7"), "raspberrypi.local")
        self.assertEqual(command.call_args.args[0], ["nslookup", "10.0.0.7"])
        self.assertEqual(command.call_args.kwargs["timeout"], 1.5)

    def test_frozen_forward_nslookup_excludes_dns_server_address(self):
        output = "Server: router.local\nAddress: 10.0.0.1\n\nName: grow.local\nAddresses: 10.0.0.7\n          fe80::1\n"
        with mock.patch.object(discovery.sys, "frozen", True, create=True), \
                mock.patch.object(discovery.shutil, "which", side_effect=lambda name: "nslookup.exe" if name == "nslookup" else None), \
                mock.patch.object(discovery, "_run_command", return_value=output):
            self.assertEqual(discovery.resolve_hostname("grow.local"), ["10.0.0.7", "fe80::1"])

    def test_frozen_without_optional_tools_safely_skips_dns(self):
        with mock.patch.object(discovery.sys, "frozen", True, create=True), \
                mock.patch.object(discovery.sys, "executable", "PigrowGUI.exe"), \
                mock.patch.object(discovery.shutil, "which", return_value=None), \
                mock.patch.object(discovery, "_run_command") as command:
            self.assertEqual(discovery.resolve_hostname("grow.local"), [])
            self.assertEqual(discovery.reverse_hostname("10.0.0.7"), "")
        command.assert_not_called()

    def test_ssh_open_does_not_imply_raspberry_pi(self):
        connection = mock.MagicMock()
        with mock.patch.object(discovery.socket, "create_connection", return_value=connection), \
                mock.patch.object(discovery, "reverse_hostname", return_value="server.local"), \
                mock.patch.object(discovery, "_run_command") as command:
            device = discovery.probe_address("10.0.0.8", ssh_port=2222)
        self.assertFalse(device["is_pi"])
        self.assertEqual(device["evidence"], "SSH port open")
        command.assert_not_called()


class ScanTests(unittest.TestCase):
    def make_device(self, address):
        return {"address": address, "hostname": "", "is_pi": False, "evidence": "SSH port open"}

    def test_discovery_adds_mac_identified_pi_even_without_ssh_or_ping(self):
        target = "10.0.0.1"
        neighbours = [{}, {target: "dc:a6:32:11:22:33"}]
        with mock.patch.object(discovery, "read_neighbours", side_effect=neighbours):
            devices = discovery.discover_devices([target], use_mdns=False, probe=lambda *args: None)
        self.assertEqual(len(devices), 1)
        self.assertTrue(devices[0]["is_pi"])
        self.assertIn("neighbour cache", devices[0]["evidence"])

    def test_hostname_and_mdns_are_merged_and_pi_devices_sorted_first(self):
        mdns = [{"address": "10.0.0.9", "hostname": "raspberrypi.local", "is_pi": True, "evidence": "mDNS"}]
        seen = []
        with mock.patch.object(discovery, "discover_mdns", return_value=mdns), \
                mock.patch.object(discovery, "resolve_hostname", return_value=["10.0.0.9"]), \
                mock.patch.object(discovery, "read_neighbours", return_value={}):
            devices = discovery.discover_devices(["raspberrypi.local", "10.0.0.2"],
                                                  probe=lambda address, *args: self.make_device(address),
                                                  on_device=seen.append)
        self.assertEqual([device["address"] for device in devices], ["10.0.0.9", "10.0.0.2"])
        self.assertEqual(devices[0]["hostname"], "raspberrypi.local")
        self.assertIn("mDNS", devices[0]["evidence"])
        self.assertIn("SSH port open", devices[0]["evidence"])
        self.assertTrue(seen)

    def test_pre_cancelled_scan_sends_no_probes(self):
        cancel = threading.Event()
        cancel.set()
        probe = mock.Mock()
        with mock.patch.object(discovery, "discover_mdns") as mdns:
            self.assertEqual(discovery.discover_devices(["10.0.0.1"], cancel, probe=probe), [])
        probe.assert_not_called()
        mdns.assert_not_called()

    def test_cancel_retains_partial_results_and_does_not_queue_rest(self):
        cancel = threading.Event()
        calls = []

        def probe(address, *args):
            calls.append(address)
            return self.make_device(address)

        def on_device(device):
            cancel.set()

        with mock.patch.object(discovery, "read_neighbours", return_value={}):
            devices = discovery.discover_devices(["10.0.0." + str(x) for x in range(1, 101)],
                                                  cancel, use_mdns=False, workers=1,
                                                  probe=probe, on_device=on_device)
        self.assertEqual(calls, ["10.0.0.1"])
        self.assertEqual(len(devices), 1)

    def test_probe_failures_do_not_abort_other_devices(self):
        def probe(address, *args):
            if address.endswith("1"):
                raise OSError("probe failed")
            return self.make_device(address)
        with mock.patch.object(discovery, "read_neighbours", return_value={}):
            devices = discovery.discover_devices(["10.0.0.1", "10.0.0.2"],
                                                  use_mdns=False, probe=probe)
        self.assertEqual([device["address"] for device in devices], ["10.0.0.2"])

    def test_scan_limits_concurrent_network_probes(self):
        state = {"active": 0, "peak": 0}
        lock = threading.Lock()
        release = threading.Event()

        def probe(address, *args):
            with lock:
                state["active"] += 1
                state["peak"] = max(state["peak"], state["active"])
                if state["active"] == 3:
                    release.set()
            release.wait(0.5)
            with lock:
                state["active"] -= 1
            return self.make_device(address)

        with mock.patch.object(discovery, "read_neighbours", return_value={}):
            devices = discovery.discover_devices(["10.0.0." + str(x) for x in range(1, 20)],
                                                  use_mdns=False, workers=3, probe=probe)
        self.assertEqual(state["peak"], 3)
        self.assertEqual(len(devices), 19)

    def test_subprocess_cancellation_kills_and_reaps_child(self):
        cancel = threading.Event()
        process = mock.Mock()

        def communicate(timeout=None):
            if timeout:
                cancel.set()
                raise subprocess.TimeoutExpired("fake", timeout)
            return "partial", None

        process.communicate.side_effect = communicate
        with mock.patch.object(discovery.subprocess, "Popen", return_value=process) as popen:
            self.assertEqual(discovery._run_command(["fake", "literal;target"], cancel_event=cancel), "partial")
        process.kill.assert_called_once()
        self.assertEqual(popen.call_args.args[0], ["fake", "literal;target"])
        self.assertNotIn("shell", popen.call_args.kwargs)


if __name__ == "__main__":
    unittest.main()
