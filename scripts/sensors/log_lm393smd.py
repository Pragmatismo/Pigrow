#!/usr/bin/env python3


import os
import sys
import time
import datetime
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
homedir = os.getenv("HOME")

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'log_lm393smd.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    log_path = loc_dic['log_path']
    log_path = log_path + "soilmoistD_log.txt"
    #log_path = loc_dic['loc_lm393smd_log']
    loc_settings = loc_dic['loc_settings']
    set_dic = pigrow_defs.load_settings(loc_settings)
    gpio_pins = (set_dic['lm393moistD_sensor'])
    gpio_pins = gpio_pins.split(",")
    gpio_pin_list = []
    for pin in gpio_pins:
        gpio_pin_list.append(str(pin))
except Exception as e:
    print("Using Defaults because - " + str(e))
    gpio_pin_list = ['21']
    log_path = homedir + "/Pigrow/logs/soilmoistD_log.txt"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'pin' or thearg == 'gpio' or thearg == 'gpio_pin':
            try:
                gpio_pin = thevalue.split(',')
                gpio_pin_list = []
                for pin in gpio_pin:
                    gpio_pin_list.append(str(pin))
            except:
                print(" !!!")
                print("    Couldn't understand gpio pin list")
                print(" !!!")
                sys.exit()
        elif thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
    elif thearg == 'help' or thearg == '-h' or thearg == '--help':
        print(" Script for logging LM393 Soil Moisture sensor ")
        print("    This script logs the state of a gpio pin set to input")
        print("    this can be used for logging a lm393smd soil moisture sensor")
        print("    set to digital mode, to use them in a much more useful analogue")
        print("    mode connect them through a ads1115 analogue to digital converter")
        print("    which can be logged and graphed in a similar fashion.")
        print(" ")
        print("    This script will also log other binary sensors and controls")
        print("    anything which is either a High or Low signal, threshold")
        print("    sensors and buttons are most likely to work.")
        print("")
        print(" ")
        print(" pin=NUM    - gpio pin to sensor data pin")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/soilmoistD_log.txt")
        print(" ")
        print(" The script reads from the DIGITAL pin and records")
        print(" only a 1 or 0 value, set the range using the screw")
        print(" on the potentiometer.")
        sys.exit()
    elif thearg == "-flags":
        print("gpio_pin=1,2,18")
        print("log_path=" + str(log_path))
        sys.exit()

print("  === == =   DIGITAL soil sensor logger  = == ===")
print("      =======================================")
print("GPIO pin list; " + str(gpio_pin_list))
print("log path : " + str(log_path))


def read_soil_moist_digital(gpio_pin):
    reading = False
    soil_value = None
    count = 0
    while reading == False:
        GPIO.setup(gpio_pin, GPIO.IN)
        try:
            soil_value = GPIO.input(gpio_pin)
        except Exception as e:
            print("!!! couldn't read sensor, error " + str(e))
            time.sleep(1)
        if not soil_value == None:
            print(" The sensor " +  str(gpio_pin) + " returned a value of: " + str(soil_value))
            return soil_value
        count = count + 1
        if count >= 10:
            print("Sensor failed to read ten times, giving up...")
            return 'none'

def log_soil_moist_digital(log_path, moist_list):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    for value in moist_list:
        moistness = value[0]
        sensor_pin = value[1]
        log_entry += str(moistness) + ":" + str(sensor_pin) + ">"
    log_entry = log_entry[:-1] + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)


if __name__ == '__main__':
    moist_list = []
    for sensor in gpio_pin_list:
        try:
            sensor = int(sensor)
        except:
            print("Must be an number")
        else:
            moist = read_soil_moist_digital(sensor)
        if not moist == 'none':
            moist_list.append([moist, sensor])

    if len(moist_list) >= 1:
        log_soil_moist_digital(log_path, moist_list)


##code to do something when the value changes

#GPIO.add_event_detect(gpio_pin, GPIO.RISING)
#def sensor_change():
#    print 'Triggered!'
#GPIO.add_event_callback(gpio_pin, sensor_change)
