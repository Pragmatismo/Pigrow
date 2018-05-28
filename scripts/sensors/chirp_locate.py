#!/usr/bin/python
import subprocess
import time
import sys
import os
# Gpio setup
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# config data loading
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def find_i2c_bus():
    out = subprocess.check_output(["ls /dev/*i2c*"], shell=True);
    if "/dev/i2c-1" in out:
        i2c_text = ("found i2c bus 1")
        i2c_bus_number = 1
    elif "/dev/i2c-0" in out:
        i2c_bus_number = 0
        i2c_text = ("found i2c bus 0")
    elif "/dev/i2c-" in out:
        try:
            i2c_bus_number = int(out.split("/dev/i2c-")[1])
            print (i2c_bus_number)
            print(("trying using bus " + str(i2c_bus_number)))
            print("i2c not found on most likely busses, but maybe it's on")
        except:
            print("can't find i2c bus at all!")
    else:
        print("!!! i2c bus not found !!!")
        return "not found"
    return i2c_bus_number

def find_i2c_devices(i2c_bus_number):
    # check i2c bus with i2cdetect and list found i2c devices
    out = subprocess.check_output(["/usr/sbin/i2cdetect -y " + str(i2c_bus_number)], shell=True)
    #print(out)
    # trimming text and sorting into a list
    i2c_devices_found = out.splitlines()
    i2c_addresses = []
    for line in i2c_devices_found[1:]: #first line is table header so skip it
        line = line[3:].replace("--", "").strip()
        if not line == "":
            if not len(line) > 2: #only lines with 1 item in
                i2c_addresses.append(line)
            else: #lines with more than one item
                for item in line.split("  "):
                    i2c_addresses.append(item)
    # returning a list of i2c device addresses
    return i2c_addresses

def list_chirps_in_settings_file(set_dic):
    # find all chirp sensors in list
    sensor_name_list = []
    for key, value in list(set_dic.items()):
        if "sensor_" in key:
            if "_type" in key:
                if value == "chirp":
                    sensor_name_list.append(key.split("_")[1])
    # get gpio location and i2c locations
    listed_chirps = []
    for chirp_sensor in sensor_name_list:
        power_gpio = None
        loc = set_dic['sensor_' + chirp_sensor + "_loc"]
        loc = loc.split("i2c:")[1]
        extra = set_dic['sensor_' + chirp_sensor + "_extra"]
        extra = extra.split(",")
        for set in extra:
            if 'power_gpio:' in set:
                power_gpio = set.split('power_gpio:')[1]
                listed_chirps.append([power_gpio, loc])
        if power_gpio == None:
            print("No gpio power pin location for " + chirp_sensor)
        else:
            print(" Chirp sensor " + chirp_sensor + " at address " + loc + " power gpio pin " + power_gpio)
    return listed_chirps

def unpower_all_chirp(chirp_list):
    #print("-- Unpowering all chirp gpio pins")
    for chirp in chirp_list:
        gpio_power_pin = chirp[0]
        GPIO.setup(int(gpio_power_pin), GPIO.IN)

def enable_all_chirp(chirp_list):
    #print("-- enabling all chirp gpio pins")
    for chirp in chirp_list:
        gpio_power_pin = chirp[0]
        i2c_chirp_address = chirp[1]
        GPIO.setup(int(gpio_power_pin), GPIO.OUT)
        GPIO.output(int(gpio_power_pin), GPIO.HIGH)

def change_chirp_i2c_address(old, new):
    print(" attempting to change address of chirp at 0x" + old + " to " + new)
    chirp_address_script = homedir + '/Pigrow/scripts/sensors/chirp_i2c_address.py'
    out = subprocess.check_output([chirp_address_script, "current=0x" + str(old), "new=" + str(new)])
    if "Chirp address changed" in out:
        print(out)
        return True
    else:
        return False


def check_and_set_chirp_locations(listed_chirps, i2c_bus_number):
    for chirp in listed_chirps:
        unpower_all_chirp(listed_chirps)
        # turn on this chirp sensor via it's gpio power pin
        gpio_power_pin = chirp[0]
        i2c_chirp_address = chirp[1]
        print(" -power gpio pin " + gpio_power_pin)
        GPIO.setup(int(gpio_power_pin), GPIO.OUT)
        GPIO.output(int(gpio_power_pin), GPIO.HIGH)
        time.sleep(1)
        # check to see if it appeared at the right place in it i2c table
        i2c_list = find_i2c_devices(i2c_bus_number) # read i2c table and return list of devices
        #print( " checking for " + str(i2c_chirp_address[2:]) + " in " + str(i2c_list))
        if i2c_chirp_address[2:] in i2c_list:
            print(" Chirp sensor powered from gpio pin " + gpio_power_pin + " found where it belongs at i2c " + i2c_chirp_address)
        elif len(i2c_list) == 0:
            print(" Chirp sensor powered from gpio pin " + gpio_power_pin + " not showing up on i2c table, might be in hidden location")
            # try to change 0x01, 0x00, 0x02
            changed = change_chirp_i2c_address("01", i2c_chirp_address)
            if not changed == True:
                changed = change_chirp_i2c_address("00", i2c_chirp_address)
            if not changed == True:
                changed = change_chirp_i2c_address("02", i2c_chirp_address)
            if not changed == True:
                print(" !!! couldn't find chirp sensor that should be at " + i2c_chirp_address + " and gpio power pin " + gpio_power_pin)
                print("     make sure it's plugged in correctly.")
        else:
            if len(i2c_list) > 1:
                print(" error with i2c table, maybe more than one i2c device is powered up?")
                print(i2c_list)
            else:
                # change i2c address from current to correct
                changed = change_chirp_i2c_address(i2c_list[0], i2c_chirp_address)
                if changed == False:
                    print("Error: unable to change chirp address from " + str(i2c_list) + " to " + str(i2c_chirp_address))
    print("Finished check and set for chirp sensors ")



# find i2c bus
i2c_bus_number = find_i2c_bus()
#
#      NEEDS TO TURN OFF ALL NON CHIRP I2C DEVICES
#                  - which means if you're going to use this script_text
#                    all i2c must be powered by a gpio pin
#                    which is kinda annoying so sorry about that...
#
# list all chirps in settings file with i2c address and gpio power pin
loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
listed_chirps = list_chirps_in_settings_file(set_dic)
print("Found " + str(len(listed_chirps)) + " listed in Pigrow config file")
if not len(listed_chirps) == 0:
    # cycle through list of chirps and check they're on the right i2c pin
    check_and_set_chirp_locations(listed_chirps, i2c_bus_number)
    # turn them all on and check to see if we've sucseeded in setting them allows
    enable_all_chirp(listed_chirps)
    chirp_list = find_i2c_devices(i2c_bus_number)
    for chirp in chirp_list:
        print("   Chirp sucsessfully located at at " + str(chirp))
else:
    print("    Make sure your sensors are correctly listed in the Pigrow config file")
    print("    easiest way of doing this in with the remote gui's sensor tab")
    print("    or manually edit the /Pigow/config/pigrow_config.txt")
    print("       the format it expects is;")
    print("          sensor_chirp01_type=chirp")
    print("          sensor_chirp01_log=/home/pi/Pigrow/logs/chirp01.txt")
    print("          sensor_chirp01_loc=i2c:0x20")
    print("          sensor_chirp01_extra=min:1,max:1000,power_gpio:20,etc")

#
#      NEEDS TO TURN ON ALL NON CHIRP I2C DEVICES
#
