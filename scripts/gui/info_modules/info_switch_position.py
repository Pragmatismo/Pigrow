#!/usr/bin/python3
import os


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


def check_gpio_status(gpio_pin, on_power_state):
    """
    Check the status of a given GPIO pin.

    This function first tries the legacy sysfs method. If the sysfs GPIO
    directory for the pin exists, it will read the value as before.

    If the path does not exist or an error occurs—and if the newer interface
    is available (i.e. /dev/gpiochip0 exists)—then it falls back to reading
    the pin value using the "gpioget" command.
    """
    gpio_sys_path = "/sys/class/gpio/gpio" + gpio_pin
    value_path = gpio_sys_path + "/value"

    # Try sysfs method if the GPIO directory exists.
    if os.path.isdir(gpio_sys_path):
        try:
            # Check the GPIO direction so we can only read input pins.
            direction_path = gpio_sys_path + "/direction"
            if os.path.exists(direction_path):
                with open(direction_path, "r") as f:
                    direction = f.read().strip()
                if direction == "out":
                    return "GPIO " + gpio_pin + " is set as OUTPUT and cannot be read."
            # Read the GPIO value.
            if os.path.exists(value_path):
                with open(value_path, "r") as f:
                    gpio_status = f.read().strip()
            else:
                return "GPIO " + gpio_pin + " value file does not exist."
            return interpret_gpio_status(gpio_status, on_power_state)
        except Exception:
            # If any error occurs in the sysfs method, fall through to the new method.
            pass
    else:
        # On older systems (non-Bookworm) try exporting the GPIO pin via sysfs.
        if not is_bookworm():
            try:
                cmd = "echo " + gpio_pin + " > /sys/class/gpio/export"
                os.popen(cmd).read()
                # Check if exporting worked.
                if os.path.isdir(gpio_sys_path) and os.path.exists(value_path):
                    with open(value_path, "r") as f:
                        gpio_status = f.read().strip()
                    return interpret_gpio_status(gpio_status, on_power_state)
            except Exception:
                pass

    # Fallback: Try using the new GPIO interface (via libgpiod) using "gpioget".
    if os.path.exists("/dev/gpiochip0"):
        try:
            cmd = "gpioget gpiochip0 " + gpio_pin
            gpio_status = os.popen(cmd).read().strip()
            if gpio_status == "":
                return "gpioget returned empty output for GPIO " + gpio_pin
            return interpret_gpio_status(gpio_status, on_power_state)
        except Exception as e:
            return "Error using gpioget: " + e

    return "GPIO " + gpio_pin + " not accessible via sysfs or new interface."


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
