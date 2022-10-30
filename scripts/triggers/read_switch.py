#!/usr/bin/python3
import os
import sys
import datetime


def load_config():
    # Read the settings file
    homedir = os.getenv("HOME")
    sys.path.append(homedir + '/Pigrow/scripts/')
    try:
        import pigrow_defs
        script = 'read_switch.py'
    except:
        print("pigrow_defs.py not found, unable to continue.")
        print("make sure pigrow software is installed correctly")
        sys.exit()
    loc_dic = pigrow_defs.load_locs(homedir + '/Pigrow/config/dirlocs.txt')
    pigrow_settings = pigrow_defs.load_settings(loc_dic['loc_settings'])
    return pigrow_settings

def read_button_settings(pigrow_settings, button_name):
    # Read the sensor info from the settigns file
    button_type = None
    button_log = None
    button_loc = None
    #
    button_key = "button_" + button_name
    type_key = button_key + "_type"
    log_key = button_key + "_log"
    loc_key = button_key + "_loc"
    if type_key in pigrow_settings:
        button_type = pigrow_settings[type_key]
    if log_key in pigrow_settings:
        button_log = pigrow_settings[log_key]
    if loc_key in pigrow_settings:
        button_loc = pigrow_settings[loc_key]

    if button_loc == None:
        err_msg = button_name + " location not found in settings file."
        print(err_msg)
    #    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])
        sys.exit()
    return button_name, button_type, button_loc, button_log

def read_switch_pos(name, type, loc):
    if not output == "short":
        print("Reading switch " + name)
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    if type == "HIGH":
        GPIO.setup(int(loc),GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    else:
        GPIO.setup(int(loc),GPIO.IN, pull_up_down=GPIO.PUD_UP)
    input = GPIO.input(int(loc))
    return str(input)


if __name__ == '__main__':

    switch_name = None
    gpio_pos = None
    gpio_type = None
    output = "long"
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'name':
                switch_name = thevalue
            if thearg == "gpio":
                gpio_pos = thevalue
            if thearg == "type":
                gpio_type = thevalue
            if thearg == "output":
                output = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Returns the state of a switch")
            print(" ")
            print(" This requres the switch to be configured in the remote gui.")
            print(" ")
            print(" name=switch unique name")
            print("   or ")
            print(" gpio=NUM")
            print(" type=GND or HIGH")
            print("")
            print(" output=short   - return only on/off")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("name=")
            print("gpio=NUM")
            print("type=[GND, HIGH]")
            print("output=[short,long]")
            sys.exit(0)

    if switch_name == None and gpio_pos == None:
        print("Switch not identified, please include name= in the commandline arguments.")
        sys.exit()

    if gpio_pos == None:
        pigrow_settings = load_config()
        name, type, loc, log = read_button_settings(pigrow_settings, switch_name)
        position = read_switch_pos(name, type, loc)
    else:
        name = "gpio " + str(gpio_pos)
        position = read_switch_pos(name, gpio_type, gpio_pos)
    if output == "short":
        if position == 0:
            print("off")
        else:
            print("on")
    else:
        print(name + " is currently " + position)
        if position == "1":
            print("activate=True")
