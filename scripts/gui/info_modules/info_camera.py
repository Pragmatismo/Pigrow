#!/usr/bin/env python3
import os
import subprocess
import shutil
import re

def detect_cameras():
    cameras = []
    # Enumerate all /dev/video* devices
    video_devs = sorted([dev for dev in os.listdir("/dev") if re.match(r"video\d+$", dev)])
    for dev in video_devs:
        dev_path = f"/dev/{dev}"
        # Get udev info for the device
        try:
            result = subprocess.run(
                ["udevadm", "info", "--query=property", "--name", dev_path],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError:
            continue
        props = {key: val for line in result.stdout.splitlines() if '=' in line
                 for key, val in [line.split('=', 1)]}
        # Only consider video devices that can capture (i.e. camera inputs)
        if "capture" not in props.get("ID_V4L_CAPABILITIES", ""):
            continue

        # Check the product property
        product = props.get("ID_V4L_PRODUCT", "")
        # Exclude known auxiliary nodes from the ISP (e.g. "bcm2835-isp")
        if "bcm2835-isp" in product.lower():
            continue

        # Determine interface type and device name
        interface = "CSI"  # default assume CSI unless USB flag is found
        name = None
        if props.get("ID_BUS") == "usb" or "usb" in props.get("ID_PATH", "") or props.get("ID_USB_DRIVER"):
            interface = "USB"
            if props.get("ID_MODEL_FROM_DATABASE"):
                name = props["ID_MODEL_FROM_DATABASE"]
            elif props.get("ID_MODEL"):
                name = props["ID_MODEL"]
            elif product:
                name = product
            else:
                name = "USB Camera"
        else:
            if product:
                if "mmal" in product.lower() or "unicam" in product.lower():
                    name = "Raspberry Pi Camera Module"
                else:
                    name = product
            else:
                name = "Raspberry Pi Camera Module"
        if name:
            name = name.replace('_', ' ').strip()
        cameras.append((interface, name))
    # Legacy stack fallback using vcgencmd (if no CSI camera found above)
    has_csi = any(iface == "CSI" for iface, _ in cameras)
    vcgencmd = shutil.which("vcgencmd")
    if not has_csi and vcgencmd:
        try:
            vcg_output = subprocess.run(
                [vcgencmd, "get_camera"], capture_output=True, text=True, check=True
            ).stdout.strip()
            if "detected=1" in vcg_output:
                cameras.append(("CSI", "Raspberry Pi Camera Module"))
        except subprocess.CalledProcessError:
            pass
    return cameras

def summarize_cameras(cameras):
    count = len(cameras)
    if count == 0:
        return "Detected 0 cameras."
    # Group cameras by interface type
    grouped = {}
    for iface, name in cameras:
        grouped.setdefault(iface, []).append(name)
    type_order = {"CSI": 0, "USB": 1}
    parts = []
    for iface in sorted(grouped.keys(), key=lambda x: type_order.get(x, 2)):
        names = grouped[iface]
        n = len(names)
        if n == 1:
            desc = names[0]
        else:
            unique_names = set(names)
            if len(unique_names) == 1:
                desc = f"{names[0]} (x{n})"
            else:
                desc = ", ".join(names)
        label = f"{iface} camera" + ("" if n == 1 else "s")
        parts.append(f"{n} {label} ({desc})")
    summary = " and ".join(parts)
    return f"Detected {count} camera{'s' if count != 1 else ''}: {summary}."

if __name__ == "__main__":
    cams = detect_cameras()
    print(summarize_cameras(cams))
