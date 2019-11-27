#!/usr/bin/python3
import os
import sys
import RPi.GPIO as GPIO

def check_command_line_args():
    """
    Check the system command line for settings information
    """
    log = 'dirlocs'
    gpio_pin = "not set"
    for argu in sys.argv[1:]:
        if "=" in argu:
            val = argu.split("=")[0].lower()
            key = argu.split("=")[1]
            if val == 'gpio':
                if key.isdigit() == True:
                    gpio_pin = key
                else:
                    print("GPIO pins must be a number")
            elif val == 'log':
               log = key.lower()
        elif argu == '-h' or argu == '--help':
            print("        Pigrow GPIO pin Low")
            print("")
            print("This turns a GPIO pin to Low, which is")
            print("the same as turning it into a gnd pin")
            print("")
            print("Set the gpio pin using the flad")
            print("   gpio=<num>")
            print("")
            print("   log=")
            print("       none         - don't log")
            print("       dirlocs      - use the default log")
            print("       <path>       - specify the path to a log")
            sys.exit()
        elif argu == '-flags':
            print("GPIO=<num>")
            print("log=[none,dirlocs,<PATH>]")
        return gpio_pin, log

def generic_low(gpio_pin, switch_log):
    """
    Set the board mode to GPIO.BMC and set the gpio_pin to Low
    log can equal none or a path to the log.
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(int(gpio_pin), GPIO.OUT)
    script = 'generic_low.py'
    msg = ("")
    msg +=("      #################################################\n")
    msg +=("      ##         gpio pin " + gpio_pin)
    msg +=(                                      " is now Low   ##\n")
    msg +=("      #################################################\n")
    GPIO.output(int(gpio_pin), GPIO.LOW)
    if not switch_log == "none":
        pigrow_defs.write_log(script, "GPIO pin " + gpio_pin + " set to low", switch_log)
    return msg


if __name__ == '__main__':
    gpio_pin, log = check_command_line_args()
    if log == "dirlocs":
        homedir = os.getenv("HOME")
        sys.path.append(homedir + '/Pigrow/scripts/')
        import pigrow_defs
        loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
        msg = generic_low(gpio_pin, loc_dic['loc_switchlog'])
    else:
        msg = generic_low(gpio_pin, log)
    print (msg)
