#!/usr/bin/python3
import datetime
import time
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'timed_water.py'
duration = None

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Water Timing Tool")
        print("")
        print("This turns the Water ON for a given duration then OFF again.")
        print("")
        print("   To use this program you must have the watering devices location and wiring direction")
        print("   set in the pigrow configuration file /config/pigrow_config.txt")
        print("        gpio_water=GPIO PIN NUMBER   gpio_pin_on=WIRING DIRECTION ")
        print("   the easiest way to do this is to use the remote gui")
        print("")
        print(" Command line options")
        print("")
        print("  duration=number in seconds")
        print("     Runs the water for that amount of seconds")
        print("")
        sys.exit()
    elif "=" in argu:
        thearg = str(argu).split('=')[0].lower()
        thevalue = str(argu).split('=')[1]
        if  thearg == 'duration' or thearg == 'd' or thearg == 's':
            try:
                duration = int(thevalue)
            except:
                print("The duration must be a number value, the time to run the water in seconds")

def run_water(set_dic, switch_log, duration):
    print ("")
    print ("      #############################################\n")
    print ("      ##        Preparing to Water Plants        ##\n")
    if 'gpio_water' in set_dic and not str(set_dic['gpio_water']).strip() == '':
        gpio_pin = int(set_dic['gpio_water'])
        gpio_pin_on = set_dic['gpio_water_on']
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            print("      ##         Turning the Water - ON         ##\n")
            print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##\n")
            GPIO.output(gpio_pin, GPIO.LOW)
            print("      ##     Waiting " + str(duration) + " seconds                  ##\n")
            time.sleep(duration)
            print("      ##         Turning the Water - OFF         ##\n")
            GPIO.output(gpio_pin, GPIO.HIGH)
            print ("      #############################################\n")
        elif gpio_pin_on == "high":
            print("      ##         Turning the Water - ON         ##\n")
            print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##\n")
            GPIO.output(gpio_pin, GPIO.HIGH)
            print("      ##     Waiting " + str(duration) + " seconds                  ##\n")
            time.sleep(duration)
            print("      ##         Turning the Water - OFF         ##\n")
            GPIO.output(gpio_pin, GPIO.LOW)
            print ("      #############################################\n")
        else:
            msg =("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            msg +=("      !!            CAN'T DETERMINE GPIO DIRECTION           !!\n")
            msg +=("      !!  Fix with the Remote Gui or edit pigrow_config.txt  !!\n")
            msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            pigrow_defs.write_log(script, 'Failed - no direction set in config', switch_log)
            return msg

    else:
        msg =("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        msg +=("      !!             No water control device set             !!\n")
        msg +=("      !!  Fix with the Remote Gui or edit pigrow_config.txt  !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, 'Failed - due to no gpio pin set in config', switch_log)
        return msg
    msg = 'watered for ' + str(duration) + ' seconds.'
    pigrow_defs.write_log(script, msg, switch_log)
    return msg


if __name__ == '__main__':

    # load settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    try:
        loc_switchlog = loc_dic['loc_switchlog']
    except:
        default_log_path = homedir + '/Pigrow/logs'
        if os.path.exists(default_log_path):
            loc_switchlog = path.join(default_log_path, 'switch_log.txt')
        else:
            loc_switchlog = "switch_log.txt"
        print(" Switch Log path not found in dirlocs.txt, using " + loc_switchlog + " instead.")

    # run the water
    if not duration == None:
        msg = run_water(set_dic, loc_switchlog, duration)
        print(msg)
    else:
        print(" - You must use the duration= flag to set a duration in seconds")
    # output result
