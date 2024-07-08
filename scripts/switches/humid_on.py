#!/usr/bin/env python3
import datetime, sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Humidifier switch")
        print("")
        print("This turns the Humidifier ON")
        print("To use this program you must have the devices GPIO and wiring direction")
        print("set in the pigrow configuration file /config/pigrow_config.txt")
        print("use the setup tool in the remote gui")
        sys.exit()

def humid_on(set_dic, switch_log):
    script = 'humid_on.py'
    msg = ("")
    msg +=("      #############################################\n")
    msg +=("      ##         Turning the humidifier - ON     ##\n")
    if 'gpio_humid' in set_dic and not str(set_dic['gpio_humid']).strip() == '':
        gpio_pin = int(set_dic['gpio_humid'])
        gpio_pin_on = set_dic['gpio_humid_on']
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            GPIO.output(gpio_pin, GPIO.LOW)
        elif gpio_pin_on == "high":
            GPIO.output(gpio_pin, GPIO.HIGH)
        else:
            msg +=("      !!       CAN'T DETERMINE GPIO DIRECTION    !!\n")
            msg +=("      !!  run config program or edit config.txt  !!\n")
            msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            pigrow_defs.write_log(script, 'Failed - no direction set in config', switch_log)
            return msg

    else:
        msg +=("      !!               NO humid SET             !!\n")
        msg +=("      !!  run config program or edit config.txt  !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, 'Failed - due to none set in config', switch_log)
        return msg

    msg +=("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##\n")
    msg +=("      #############################################\n")
    pigrow_defs.set_condition(condition_name="humid", trig_direction="on", cooldown="none")
    pigrow_defs.write_log(script, 'Humidifier turned on', switch_log)
    return msg

if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    msg = humid_on(set_dic, loc_dic['loc_switchlog'])
    print (msg)
