#!/usr/bin/python3
import datetime, sys, os
import RPi.GPIO as GPIO
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def check_command_line_args():
    """
    Check the system command line for settings information
    """
    name = ""
    dir  = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            key = argu.split("=")[0].lower()
            val = argu.split("=")[1]

            if key == 'direction' or key == "d":
                   dir = val.lower()
            elif key == 'name':
                   name = val.lower()

        elif argu == '-h' or argu == '--help':
            print("   Pigrow H-Bridge motor controller switch")
            print("")
            print("   name=  ")
            print("")
            print("   direction=")
            print("              off    - both pins 0")
            print("              a      - gpioA 1, gpioB 0")
            print("              b      - gpioA 0, gpioB 1")
            sys.exit()
        elif argu == '-flags':
            print("name=")
            print("direction=[off,a,b]")
    return name, dir

def enable_pins(gpio_A, gpio_B):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(gpio_A, GPIO.OUT)
    GPIO.setup(gpio_B, GPIO.OUT)

def set_pins(gpio_A, gpio_B, dir_A, dir_B):
    if dir_A == 1:
        GPIO.output(gpio_A, GPIO.HIGH)
    else:
        GPIO.output(gpio_A, GPIO.LOW)

    if dir_B == 1:
        GPIO.output(gpio_B, GPIO.HIGH)
    else:
        GPIO.output(gpio_B, GPIO.LOW)

def hbridge_switch(name, direction, set_dic, switch_log, err_log):
    script = 'hbridge_set.py'
    msg = ("")
    msg +=(" H-Bridge \n")
    nameA = "hbridge_" + name + "_gpioA"
    nameB = "hbridge_" + name + "_gpioB"
    log_msg = "Could not find h-bridge settings for " + name

    if nameA in set_dic and nameB in set_dic:
        gpio_A = int(set_dic[nameA])
        gpio_B = int(set_dic[nameB])
        enable_pins(gpio_A, gpio_B)
        if direction == 'off':
            msg = "Turning off motor"
            set_pins(gpio_A, gpio_B, 0, 0)
        elif direction == 'a':
            msg = "Setting motor direction to A"
            set_pins(gpio_A, gpio_B, 1, 0)
        elif direction == 'b':
            msg = "Setting motor direction to B"
            set_pins(gpio_A, gpio_B, 0, 1)
        else:
            log_msg = "H-Bridge " + name + " couldn't understand direction, " + str(direction)
            pigrow_defs.write_log(script, log_msg, err_log)
            return log_msg

        log_msg = "H-Bridge " + name + " " + msg
        pigrow_defs.write_log(script, log_msg, switch_log)

    return log_msg


if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    name, direction = check_command_line_args()
    if not name == "" and not direction == "":
        msg = hbridge_switch(name, direction, set_dic, loc_dic['loc_switchlog'], err_log=loc_dic['err_log'])
    else:
        msg = "hbridge_set.py could not run, make sure name and direction are set."
    print (msg)
