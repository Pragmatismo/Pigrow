#!/usr/bin/python3
import os

from info_switch_position import check_gpio_status


def load_settings(settings_path):
    """Load key=value settings into a dictionary."""
    if not os.path.exists(settings_path):
        return None, "Config file not found: " + settings_path

    settings = {}
    with open(settings_path, "r") as f:
        for line in f.read().splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip().strip("\"")
    return settings, ""


def latest_switch_log(script_name, log_path):
    """Return the most recent switch log message for a given script."""
    if not os.path.exists(log_path):
        return None

    with open(log_path, "r") as f:
        lines = f.read().splitlines()

    for line in reversed(lines):
        if "@" not in line:
            continue
        parts = line.split("@", 2)
        if len(parts) < 3:
            continue
        script, timestamp, message = parts
        if script == script_name:
            ts = timestamp.split(".")[0]
            return f"{message} (at {ts})"
    return None


def collect_gpio_status(settings):
    gpio_pins = {}
    gpio_on_map = {}
    for key, value in settings.items():
        if not key.startswith("gpio_"):
            continue
        tail = key[len("gpio_"):]
        if tail.endswith("_on") and tail.count("_") == 1:
            device = tail[:-3]
            gpio_on_map[device] = value
            continue
        if "_" in tail:
            continue
        gpio_pins[tail] = value

    status_lines = []
    for device in sorted(gpio_on_map):
        if device not in gpio_pins:
            continue
        status = check_gpio_status(gpio_pins[device], gpio_on_map[device])
        status_lines.append(f"{device}: {status}")
    return status_lines


def collect_pulse_intervals(settings):
    pulses = []
    for key, value in settings.items():
        if key.startswith("pulse_"):
            device = key[len("pulse_"):]
            pulses.append(f"{device}: {value}")
    return sorted(pulses)


def collect_pwm_devices(settings, switch_log_path):
    pwm_lines = []

    for key, value in settings.items():
        if key.startswith("hwpwm_") and key.endswith("_loc"):
            name = key.split("_")[1]
            freq = settings.get(f"hwpwm_{name}_freq", "")
            last = latest_switch_log("hwpwm_set.py", switch_log_path)
            line = f"hwpwm {name}: pin {value}"
            if freq:
                line += f", freq {freq} Hz"
            if last:
                line += f" | Last action: {last}"
            pwm_lines.append(line)

        if key.startswith("pca_") and key.endswith("_loc"):
            name = key.split("_")[1]
            freq = settings.get(f"pca_{name}_freq", "")
            last = latest_switch_log("pca9685_set.py", switch_log_path)
            line = f"pca9685 {name}: address {value}"
            if freq:
                line += f", freq {freq} Hz"
            if last:
                line += f" | Last action: {last}"
            pwm_lines.append(line)

    return sorted(pwm_lines)


def collect_stepper(settings, switch_log_path):
    stepper_lines = []
    for key, value in settings.items():
        if key.startswith("stepper_"):
            name = key.split("_", 1)[1]
            last = latest_switch_log("stepper_move.py", switch_log_path)
            pins = value.replace(",", ", ")
            line = f"stepper {name}: pins {pins}"
            if last:
                line += f" | Last action: {last}"
            stepper_lines.append(line)
    return sorted(stepper_lines)


def collect_watering(settings, switch_log_path):
    if "gpio_water" not in settings:
        return []

    gpio = settings.get("gpio_water", "")
    direction = settings.get("gpio_water_on", "")
    control = settings.get("water_control", "")
    last = latest_switch_log("timed_water.py", switch_log_path)

    line = "watering: "
    details = []
    if gpio:
        details.append(f"gpio {gpio}")
    if direction:
        details.append(f"active-{direction}")
    if control:
        details.append(f"control {control}")
    if details:
        line += ", ".join(details)
    else:
        line += "not configured"
    if last:
        line += f" | Last action: {last}"
    return [line]


def collect_leds(settings, homedir):
    led_names = set()
    for key in settings:
        if key.startswith("led_"):
            parts = key.split("_")
            if len(parts) >= 3:
                led_names.add(parts[1])

    lines = []
    for name in sorted(led_names):
        loc = settings.get(f"led_{name}_loc", "")
        reboot = settings.get(f"led_{name}_reboot", "")
        state_file = os.path.join(homedir, f"Pigrow/logs/ledstat_{name}.txt")
        state = "unknown"
        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                state = f.read().strip()
        line = f"LED {name}: gpio {loc}" if loc else f"LED {name}: gpio not set"
        if reboot:
            line += f", onboot {reboot}"
        line += f" | Last state file: {state}"
        lines.append(line)
    return lines


def collect_buttons(settings):
    buttons = {}
    for key, value in settings.items():
        if not key.startswith("button_"):
            continue
        parts = key.split("_")
        if len(parts) < 3:
            continue
        name = parts[1]
        suffix = parts[2]
        if name not in buttons:
            buttons[name] = {}
        buttons[name][suffix] = value

    lines = []
    for name in sorted(buttons):
        info = buttons[name]
        loc = info.get("loc", "")
        type_ = info.get("type", "")
        log = info.get("log", "")
        parts = []
        if loc:
            parts.append(f"gpio {loc}")
        if type_:
            parts.append(f"type {type_}")
        if log:
            parts.append(f"log {log}")
        if not parts:
            parts.append("no details set")
        lines.append(f"button {name}: " + ", ".join(parts))
    return lines


def show_info():
    homedir = os.getenv("HOME")
    settings_path = os.path.join(homedir, "Pigrow/config/pigrow_config.txt")
    switch_log_path = os.path.join(homedir, "Pigrow/logs/switch_log.txt")

    settings, err = load_settings(settings_path)
    if settings is None:
        return err

    output = []

    gpio_lines = collect_gpio_status(settings)
    if gpio_lines:
        output.append("GPIO devices:")
        output.extend("  " + line for line in gpio_lines)

    pulse_lines = collect_pulse_intervals(settings)
    if pulse_lines:
        output.append("Pulse intervals:")
        output.extend("  " + line for line in pulse_lines)

    pwm_lines = collect_pwm_devices(settings, switch_log_path)
    if pwm_lines:
        output.append("PWM devices:")
        output.extend("  " + line for line in pwm_lines)

    stepper_lines = collect_stepper(settings, switch_log_path)
    if stepper_lines:
        output.append("Steppers:")
        output.extend("  " + line for line in stepper_lines)

    water_lines = collect_watering(settings, switch_log_path)
    if water_lines:
        output.append("Watering:")
        output.extend("  " + line for line in water_lines)

    led_lines = collect_leds(settings, homedir)
    if led_lines:
        output.append("LEDs:")
        output.extend("  " + line for line in led_lines)

    button_lines = collect_buttons(settings)
    if button_lines:
        output.append("Buttons:")
        output.extend("  " + line for line in button_lines)

    if not output:
        return "No devices configured in pigrow_config.txt"

    return "\n".join(output)


if __name__ == '__main__':
    print(show_info())
