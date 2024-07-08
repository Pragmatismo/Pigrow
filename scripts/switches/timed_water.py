#!/usr/bin/env python3
import datetime
import atexit
import time
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'timed_water.py'
duration = None
safety = "on"

active = ""
gpio_pin = None
def exit_handler():
    if active == "high":
        GPIO.output(gpio_pin, GPIO.LOW)
        print ('Pump has been teminated mid use.')
    if active == "low":
        GPIO.output(gpio_pin, GPIO.HIGH)
        print ('Pump has been teminated mid use.')

atexit.register(exit_handler)

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Water Timing Tool")
        print("")
        print("This turns the Water ON for a given duration then OFF again.")
        print("")
        print("   To use this program you must have the watering devices location and wiring direction")
        print("   set in the pigrow configuration file /config/pigrow_config.txt")
        print("        gpio_water=GPIO PIN NUMBER   gpio_water_on=WIRING DIRECTION ")
        print("     also water_control=timed or =any to select who controls the watering device.")
        print("")
        print("   The easiest way to do this is to use the remote gui's config watering button")
        print("")
        print(" Command line options")
        print("")
        print("  duration=number in seconds")
        print("     Runs the water for that amount of seconds")
        print("")
        print("  safety=off")
        print("     Ignore the config file's water_control option")
        print("     This is only for testing purposes, if you want open control")
        print("     select 'any' as the water_control option.")
        sys.exit()
    elif "flags" in argu:
        print("duration=time in seconds")
        print("safety=off")
    elif "=" in argu:
        thearg = str(argu).split('=')[0].lower()
        thevalue = str(argu).split('=')[1]
        if  thearg == 'duration' or thearg == 'd' or thearg == 's':
            try:
                duration = int(thevalue)
            except:
                print("The duration must be a number value, the time to run the water in seconds")
        if  thearg == 'safety':
            safety = thevalue

def run_water(set_dic, switch_log, duration):
    print ("")
    print ("      #############################################\n")
    print ("      ##        Preparing to Water Plants        ##\n")
    if 'gpio_water' in set_dic and not str(set_dic['gpio_water']).strip() == '':
        global gpio_pin
        gpio_pin = int(set_dic['gpio_water'])
        gpio_water_on = set_dic['gpio_water_on']
        global GPIO
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        global active
        if gpio_water_on == "low":
            active = "low"
            print("      ##         Turning the Water - ON         ##\n")
            print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_water_on+"  ##\n")
            GPIO.output(gpio_pin, GPIO.LOW)
            print("      ##     Waiting " + str(duration) + " seconds                  ##\n")
            time.sleep(duration)
            print("      ##         Turning the Water - OFF         ##\n")
            GPIO.output(gpio_pin, GPIO.HIGH)
            active = ""
            print ("      #############################################\n")
        elif gpio_water_on == "high":
            active = "high"
            print("      ##         Turning the Water - ON         ##\n")
            print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_water_on+"  ##\n")
            GPIO.output(gpio_pin, GPIO.HIGH)
            print("      ##     Waiting " + str(duration) + " seconds                  ##\n")
            time.sleep(duration)
            print("      ##         Turning the Water - OFF         ##\n")
            GPIO.output(gpio_pin, GPIO.LOW)
            active = ""
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
    # check for control option
    if 'water_control' in set_dic:
        water_control_option = set_dic['water_control']
        if water_control_option == 'all' or water_control_option == 'timed' or safety == 'off':
            # run the water
            if not duration == None:
                msg = run_water(set_dic, loc_switchlog, duration)
                print(msg)
            else:
                print(" - You must use the duration= flag to set a duration in seconds")
        else:
            print(" - water_control not set to 'timed' or 'all', not running pump")
    else:
        print(" - water_control option not found, for safety this must be set")
        print("   use the gui or manually add water_control=timed to pigrow_config.txt" )
    # output result
