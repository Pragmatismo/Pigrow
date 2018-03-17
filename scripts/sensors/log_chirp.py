#!/usr/bin/python
import os
import sys
import time
import datetime
from Adafruit_GPIO import I2C #https://github.com/adafruit/Adafruit_Python_GPIO

#
#
#  THIS IS NOW OBSOLUTE AND WILL BE REPALCED USING THE NEW CHIRP MODULE FROM THE CREATORS
#
#
#


homedir = os.getenv("HOME")
log_path = homedir + "/Pigrow/logs/chirp_log.txt"
chirp_address = 0x20

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging the Chirp Soil Moisture Sensor")
        print("     This script uses the Adafruit_GPIO i2c interface")
        print(" ")
        print("     You will need I2C support enabled on the pi")
        print("            ( sudo raspi-config )")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/chirp_log.txt")
        print("      - path to write the log")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("log=" + str(log_path))
        sys.exit(0)

def read_chirp_sensor(chirp_address):
    chirp = I2C.get_i2c_device(chirp_address)
    chirp.write8( chirp_address, 0x06 ) #sent reset command
    time.sleep(5) #waits for reset
    chirp.write8( chirp_address, 3)
    time.sleep(3) #waits for reading
    light = chirp.readU16(4, False)
    temp  = chirp.readS16(5, False)/float(10)
    moist = chirp.readU16(0, False)
    return moist, temp, light

def log_chirp_sensor(log_path, moist, temp, light):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    log_entry += str(moist) + ">"
    log_entry += str(temp) + ">"
    log_entry += str(light) + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)

def temp_c_to_f(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

if __name__ == '__main__':
    moist, temp, light = read_chirp_sensor(chirp_address)
    #crazy americans might want to temp =  temp_c_to_f(temp) about here.
    log_chirp_sensor(log_path, moist, temp, light)
