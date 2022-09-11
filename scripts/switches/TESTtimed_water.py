#!/usr/bin/python3
import datetime
import atexit
import time
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'TESTtimed_water.py'

# terminate activity on close
active = ""
gpio_pin = None
def exit_handler():
    if active == "high":
        GPIO.output(gpio_pin, GPIO.LOW)
        print ('Pump has been teminated mid use.')
        pigrow_defs.write_log(script, "Terminated mid use", switch_log)
    if active == "low":
        GPIO.output(gpio_pin, GPIO.HIGH)
        print ('Pump has been teminated mid use.')
        pigrow_defs.write_log(script, "Terminated mid use", switch_log)

atexit.register(exit_handler)

# read settings
duration = None
safety = "on"
pumpname = None
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Watering Tool")
        print("")
        print("This turns the Water ON for a given duration then OFF again.")
        print("")
        print("  New version of the watering system, being tested ")
        print("")
        print("   Set up and control in the test gui's watering tab")
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
        print("pump=pump name")
        print("duration=time in seconds")
        print("safety=off")
    elif "=" in argu:
        thearg = str(argu).split('=')[0].lower()
        thevalue = str(argu).split('=')[1]
        if thearg == 'duration' or thearg == 'd' or thearg == 's':
            try:
                duration = int(thevalue)
            except:
                print("The duration must be a number value, the time to run the water in seconds")
                sys.exit()
        elif thearg == 'safety':
            safety = thevalue
        elif thearg == "pump":
            pumpname = thevalue

if pumpname == None or duration == None:
    print("pump and duration must be set, ")
    print("  pump=pumpname duration=15 ")
    print("to run the relay called pumpname for fifteen seconds")
    sys.exit()

def init_gpio(gpio_pin):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(gpio_pin, GPIO.OUT)
    return GPIO

def read_conf(pumpname):
    # load locations config file
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    # pick errlog
    try:
        loc_err_log=loc_dic['err_log']
    except:
        loc_err_log=homedir + "/Pigrow/logs/error_log.txt"

    # load settings from pigrow_config.txt
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_err_log)

    # pick switchlog
    try:
        loc_switchlog = loc_dic['loc_switchlog']
    except:
        default_log_path = homedir + '/Pigrow/logs'
        if os.path.exists(default_log_path):
            loc_switchlog = path.join(default_log_path, 'switch_log.txt')
        else:
            loc_switchlog = "switch_log.txt"

        print(" Switch Log path not found in dirlocs.txt, using " + loc_err_log + " instead.")

    # read data
    pin_key = "gpio_" + pumpname
    pin_dir = "gpio_" + pumpname + "_on"
    gpio_pin = None
    gpio_dir = None
    if pin_key in set_dic:
        if not set_dic[pin_key].strip() == "":
            gpio_pin = set_dic[pin_key]

    if pin_dir in set_dic:
        if not set_dic[pin_dir].strip() == "":
            gpio_dir = set_dic[pin_dir]

    if gpio_pin == None or gpio_dir == None:
        print(" Relay " + pumpname + " is not configured in pigrow_config.txt")
        print(" This should be done in the TEST GUI for best results")
        pigrow_defs.write_log(script, "Failed - relay " + pumpname + " not set in config", loc_err_log)
        sys.exit()

    return gpio_pin, gpio_dir, loc_switchlog, loc_err_log

def run_pump(GPIO, gpio_pin, gpio_dir, duration):
    global active
    # when wired so low is on
    if gpio_dir == "low":
        active = "low"
        print(" Turning on by switching GPIO " +str(gpio_pin)+ " to low")
        GPIO.output(gpio_pin, GPIO.LOW)
        print(" Waiting " + str(duration) + " seconds")
        time.sleep(duration)
        print(" Done! Turning the Water OFF")
        GPIO.output(gpio_pin, GPIO.HIGH)
        active = ""
    # when wired so high is on
    elif gpio_dir == "high":
        active = "high"
        print(" Turning on by switching GPIO " +str(gpio_pin)+ " to high")
        GPIO.output(gpio_pin, GPIO.HIGH)
        print(" Waiting " + str(duration) + " seconds")
        time.sleep(duration)
        print(" Done! Turning the Water OFF")
        GPIO.output(gpio_pin, GPIO.LOW)
        active = ""
    # when neither
    else:
        print (" ERROR! Can't determine RELAY wiring direction, unable to continue.")
        print ("        Fix with the Remote Gui or edit pigrow_config.txt")
        pigrow_defs.write_log(script, 'Failed - no direction set in config', err_log)

    # finally
    msg = "watered for " + str(duration) + " seconds."
    pigrow_defs.write_log(script, msg, switch_log)
    print(msg)


if __name__ == '__main__':

    # read config
    gpio_pin, gpio_dir, switch_log, err_log = read_conf(pumpname)
    gpio_pin = int(gpio_pin)
    # initalise gpio as output
    GPIO = init_gpio(gpio_pin)
    # run pump for set duration
    run_pump(GPIO, gpio_pin, gpio_dir, duration)
