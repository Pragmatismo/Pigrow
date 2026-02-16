#!/usr/bin/env python3
import sys
import os

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs


def parse_args():
    name = None
    for argu in sys.argv[1:]:
        if argu in ('-h', '--help'):
            print("Pigrow Relay switch - OFF")
            print("")
            print("This turns a relay OFF based on settings in pigrow_config.txt")
            print("Set relay settings using the config tool or edit config.txt")
            print("")
            print("Usage:")
            print("  relay_off.py name=<relay name>")
            print("")
            print("Example:")
            print("  relay_off.py name=lamp")
            sys.exit(0)
        if "=" in argu:
            key, value = argu.split("=", 1)
            if key == "name":
                name = value.strip()
    return name


def relay_off(set_dic, switch_log, name):
    script = 'relay_off.py'
    msg = ("")
    msg +=("      #############################################\n")
    msg +=("      ##        Turning relay - OFF ({})       ##\n".format(name))

    gpio_key = f"gpio_{name}"
    gpio_on_key = f"gpio_{name}_on"

    if not name:
        msg +=("      !!              NO RELAY NAME             !!\n")
        msg +=("      !!   use name=<relay name> to specify     !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, 'Failed - no relay name supplied', switch_log)
        return msg

    if gpio_key in set_dic and str(set_dic[gpio_key]).strip() != '':
        gpio_pin = int(set_dic[gpio_key])
        gpio_pin_on = set_dic.get(gpio_on_key, '').strip().lower()
        if gpio_pin_on == '':
            msg +=("      !!       NO GPIO DIRECTION SET IN CONFIG   !!\n")
            msg +=("      !!  run config program or edit config.txt  !!\n")
            msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            pigrow_defs.write_log(script, 'Failed - no direction set in config', switch_log)
            return msg
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            GPIO.output(gpio_pin, GPIO.HIGH)
        elif gpio_pin_on == "high":
            GPIO.output(gpio_pin, GPIO.LOW)
        else:
            msg +=("      !!       CAN'T DETERMINE GPIO DIRECTION    !!\n")
            msg +=("      !!  run config program or edit config.txt  !!\n")
            msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            pigrow_defs.write_log(script, 'Failed - invalid direction in config', switch_log)
            return msg
    else:
        msg +=("      !!             RELAY NOT SET              !!\n")
        msg +=("      !!  run config program or edit config.txt  !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, f'Failed - no gpio set for {name}', switch_log)
        return msg

    msg +=("      ##    Switched GPIO {} to OFF (was {})   ##\n".format(gpio_pin, gpio_pin_on))
    msg +=("      #############################################\n")
    pigrow_defs.set_condition(condition_name=name, trig_direction="off", cooldown="none")
    pigrow_defs.write_log(script, f"relay '{name}' turned off", switch_log)
    return msg


if __name__ == '__main__':
    relay_name = parse_args()
    settings_path = os.path.join(homedir, 'Pigrow/config/pigrow_config.txt')
    err_path = os.path.join(homedir, 'Pigrow/logs/err_log.txt')
    sl_path  = os.path.join(homedir, 'Pigrow/logs/switch_log.txt')
    if os.path.isfile(settings_path):
        set_dic = pigrow_defs.load_settings(settings_path, err_log=err_path,)
        msg = relay_off(set_dic, sl_path, relay_name)
        print(msg)
    else:
        print("!!!! Settings file does not exist at " + settings_path)
