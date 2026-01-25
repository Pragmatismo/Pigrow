#!/usr/bin/python3
import os
import re
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

def parse_gpio_line(line):
    """
    Parse a GPIO status line, returning (level, is_output).
    """
    level = None
    is_output = False

    match = re.search(r"\blevel=(0|1)\b", line, re.IGNORECASE)
    if match:
        level = match.group(1)
    else:
        if re.search(r"\bhi(gh)?\b", line, re.IGNORECASE):
            level = "1"
        elif re.search(r"\blo(w)?\b", line, re.IGNORECASE):
            level = "0"

    if re.search(r"\bfunc=output\b", line, re.IGNORECASE):
        is_output = True
    elif re.search(r"\b(output|out|op)\b", line, re.IGNORECASE):
        is_output = True

    return level, is_output


def check_gpio_status(gpio_pin, on_power_state):
    """
    Check the status of a given GPIO pin without changing its configuration.

    Strategy:
      1. If available, use 'raspi-gpio get N' (Raspberry Pi specific, no side effects).
      2. Else, if available, use 'pinctrl get N'.
      3. Else, if /sys/class/gpio/gpioN/value exists, read that.
      4. Else, if 'gpioget' is present, use 'gpioget --numeric --chip 0 N'.
    """
    output_hint = False
    raspi_available = shutil.which("raspi-gpio")
    pinctrl_available = shutil.which("pinctrl")

    # 1) Prefer raspi-gpio on Raspberry Pi systems
    if raspi_available:
        line = run_cmd(["raspi-gpio", "get", str(gpio_pin)])
        if line:
            level, is_output = parse_gpio_line(line)
            output_hint = output_hint or is_output
            if level in ("0", "1"):
                return interpret_gpio_status(level, on_power_state)
            # If we couldn't parse level, fall through to other methods

    # 2) Fallback to pinctrl if raspi-gpio is not available
    if not raspi_available and pinctrl_available:
        line = run_cmd(["pinctrl", "get", str(gpio_pin)])
        if line:
            level, is_output = parse_gpio_line(line)
            output_hint = output_hint or is_output
            if level in ("0", "1"):
                return interpret_gpio_status(level, on_power_state)

    # 3) Sysfs, **only** if already exported
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

    # 4) libgpiod / gpioget (new GPIO character device API)
    if shutil.which("gpioget"):
        # --numeric gives plain 0/1, --chip 0 scopes to gpiochip0
        line = run_cmd(["gpioget", "--numeric", "--chip", "0", str(gpio_pin)])
        if line in ("0", "1"):
            status = interpret_gpio_status(line, on_power_state)
            if output_hint:
                return (
                    f"{status} (warning: GPIO {gpio_pin} is configured as output; "
                    "read may be unreliable)"
                )
            return status
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
