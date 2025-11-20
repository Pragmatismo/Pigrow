#!/usr/bin/python3
import os
import shutil
import subprocess

def is_bookworm():
    """
    Check if the OS release indicates Debian Bookworm.
    """
    try:
        with open("/etc/os-release", "r") as f:
            data = f.read().lower()
        return "bookworm" in data
    except Exception:
        return False


def interpret_gpio_status(gpio_status, on_power_state):
    """
    Given a GPIO status string ("0" or "1") and the desired on_power_state
    ('low' or 'high'), return a human-readable device status.
    """
    if gpio_status == "1":
        if on_power_state == 'low':
            return "OFF"
        elif on_power_state == 'high':
            return "ON"
        else:
            return "settings error"
    elif gpio_status == "0":
        if on_power_state == 'low':
            return "ON"
        elif on_power_state == 'high':
            return "OFF"
        else:
            return "settings error"
    else:
        return "read error -" + gpio_status


def run_cmd(cmd):
    """
    Helper: run a command, return stdout as stripped string or "" on error.
    """
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return ""


def check_gpio_status(gpio_pin, on_power_state):
    """
    Check the status of a given GPIO pin without changing its configuration.

    Strategy:
      1. If available, use 'raspi-gpio get N' (Raspberry Pi specific, no side effects).
      2. Else, if /sys/class/gpio/gpioN/value exists, read that.
      3. Else, if 'gpioget' is present, use 'gpioget --numeric --chip 0 N'.
    """
    # 1) Prefer raspi-gpio on Raspberry Pi systems
    if shutil.which("raspi-gpio"):
        line = run_cmd(["raspi-gpio", "get", str(gpio_pin)])
        # Typical output contains 'level=0' or 'level=1'
        if line:
            tokens = line.replace(",", " ").split()
            for t in tokens:
                if t.startswith("level="):
                    level = t.split("=", 1)[1]
                    if level in ("0", "1"):
                        return interpret_gpio_status(level, on_power_state)
            # If we couldn't parse level, fall through to other methods

    # 2) Sysfs, **only** if already exported
    gpio_sys_path = f"/sys/class/gpio/gpio{gpio_pin}"
    value_path = os.path.join(gpio_sys_path, "value")

    if os.path.exists(value_path):
        try:
            with open(value_path, "r") as f:
                gpio_status = f.read().strip()
            if gpio_status in ("0", "1"):
                return interpret_gpio_status(gpio_status, on_power_state)
        except Exception:
            pass  # fall through to gpioget

    # 3) libgpiod / gpioget (new GPIO character device API)
    if shutil.which("gpioget"):
        # --numeric gives plain 0/1, --chip 0 scopes to gpiochip0
        line = run_cmd(["gpioget", "--numeric", "--chip", "0", str(gpio_pin)])
        if line in ("0", "1"):
            return interpret_gpio_status(line, on_power_state)
        elif line:
            # Some kind of unexpected text (probably an error to stdout)
            return f"gpioget unexpected output for GPIO {gpio_pin}: {line}"
        else:
            # Errors usually go to stderr, so stdout is empty
            return f"gpioget returned empty output for GPIO {gpio_pin}"

    # If we got here, nothing worked
    return f"GPIO {gpio_pin} not accessible (raspi-gpio, sysfs, and gpioget all failed)."


def show_info():
    """
    Load GPIO settings from a configuration file, check each device’s GPIO status,
    and return a summary.
    """
    homedir = os.getenv("HOME")

    gpio_dict = {}
    gpio_on_dict = {}
    pigrow_config_file = os.path.join(homedir, "Pigrow/config/pigrow_config.txt")

    if not os.path.exists(pigrow_config_file):
        return "Config file not found: " + pigrow_config_file

    with open(pigrow_config_file, "r") as f:
        pigrow_settings = f.read().splitlines()

    for item in pigrow_settings:
        equals_pos = item.find("=")
        if equals_pos == -1:
            continue  # Skip malformed lines.
        setting_name = item[:equals_pos].strip()
        setting_value = item[equals_pos + 1:].strip()

        if "gpio_" in setting_name:
            # Assume format like gpio_device or gpio_device_on.
            parts = setting_name.split("_")
            if len(parts) >= 2:
                device_name = parts[1]
                if "on" not in setting_name:
                    gpio_dict[device_name] = setting_value
                else:
                    gpio_on_dict[device_name] = setting_value

    # Generate a status report for each device.
    text_out = ""
    for key in sorted(gpio_on_dict):
        if key in gpio_dict:
            status = check_gpio_status(gpio_dict[key], gpio_on_dict[key])
            text_out += key + " is " + status + "\n"

    return text_out.strip()


if __name__ == '__main__':
    print(show_info())
