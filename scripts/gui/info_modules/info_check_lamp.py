#!/usr/bin/python3
import os, sys
import datetime

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
from info_switch_position import check_gpio_status

def show_info():
    pigrow_config_path = homedir + "/Pigrow/config/pigrow_config.txt"
    config_dict = pigrow_defs.load_settings(pigrow_config_path)
    lamp_msg = ""

    gpio_pin = config_dict.get("gpio_lamp")
    on_power_state = config_dict.get("gpio_lamp_on")

    timed_devices = pigrow_defs.detect_timed_devices()
    lamp_device = None
    for device, on_time, off_time, timer_type in timed_devices:
        if device == "lamp":
            lamp_device = (on_time, off_time, timer_type)
            break

    if lamp_device is None:
        return "No lamp set in pigrow_config.txt\n" if not gpio_pin else "Lamp timing not found in cron."

    on_time, off_time, timer_type = lamp_device
    controller = "Lamp Confirm" if timer_type == "lampcon" else "cron relay"
    aday = datetime.timedelta(days=1)
    if on_time > off_time:
        dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + aday))
    else:
        dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))

    length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))

    lamp_msg += (
        "Lamp controlled using "
        + controller
        + ", on: "
        + str(on_time)[:-3]
        + " off: "
        + str(off_time)[:-3]
    )
    lamp_msg += (
        "\n     (duration "
        + str(length_lamp_on)[:-3]
        + " on, "
        + str(aday - length_lamp_on)[:-3]
        + " off)\n"
    )

    if gpio_pin and on_power_state:
        expected_state = pigrow_defs.device_schedule_state(on_time, off_time)
        gpio_status = check_gpio_status(gpio_pin, on_power_state)

        if expected_state is None:
            lamp_msg += "Lamp schedule does not define distinct on/off periods.\n"
            lamp_msg += "GPIO is set to " + gpio_status
        else:
            desired = "ON" if expected_state == "on" else "OFF"
            if gpio_status.upper() == desired:
                lamp_msg += "GPIO is set to " + gpio_status
            else:
                lamp_msg += (
                    "Should be "
                    + desired.lower()
                    + " but gpio pin reads "
                    + gpio_status.lower()
                )

    return lamp_msg


if __name__ == '__main__':
    print(show_info())
