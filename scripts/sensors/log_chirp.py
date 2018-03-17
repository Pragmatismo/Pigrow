#!/usr/bin/python
import os
import sys
import time
import datetime
homedir = os.getenv("HOME")
sys.path.append(homedir + '/chirp-rpi/')
import chirp

homedir = os.getenv("HOME")
log_path = homedir + "/Pigrow/logs/chirp_log.txt"
chirp_address = 0x20
min_m = 1
max_m = 1000
temp_offset = 0

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
        elif thearg == 'address' or thearg == 'chirp_address':
            chirp_address = int(thevalue, 16)
        elif thearg == 'min_m':
            min_m = int(thevalue)
        elif thearg == 'max_m':
            max_m = int(thevalue)
        elif thearg == 'temp_offset':
            temp_offset = int(thevalue)
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging the Chirp Soil Moisture Sensor")
        print("     this uses the module chirp-rpi")
        print("     many thanks to Goran Lundberg")
        print("     https://github.com/ageir/chirp-rpi/")
        print(" ")
        print("     You will need I2C support enabled on the pi")
        print("            ( sudo raspi-config )")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/chirp_log.txt")
        print("      - path to write the log")
        print(" chirp_address=0x20")
        print("      - i2c address of the chirp")
        print(" min_m=1")
        print(" max_m=1000")
        print("      - min and max moisture calibration")
        print(" temp_offset=0")
        print("      - temp correction")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("log=" + str(log_path))
        print("chirp_address=0x20")
        print("min_m=1")
        print("max_m=1000")
        print("temp_offset=0")
        sys.exit(0)

def read_chirp_sensor(chirp_address, min_moist, max_moist, temp_offset=0):
    # Initialize the sensor.
    chirp_sensor = chirp.Chirp(address=chirp_address,
                        read_moist=True,
                        read_temp=True,
                        read_light=True,
                        min_moist=min_moist,
                        max_moist=max_moist,
                        temp_scale='celsius',
                        temp_offset=0)
    chirp_sensor.trigger()
    moist = chirp_sensor.moist
    moist_p = chirp_sensor.moist_percent
    temp = chirp_sensor.temp
    light = chirp_sensor.light
    return moist, moist_p, temp, light

def log_chirp_sensor(log_path, moist, moist_p, temp, light):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    log_entry += str(moist) + ">"
    log_entry += str(moist_p) + ">"
    log_entry += str(temp) + ">"
    log_entry += str(light) + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)


if __name__ == '__main__':
    moist, moist_p, temp, light = read_chirp_sensor(chirp_address, min_m, max_m, temp_offset)
    log_chirp_sensor(log_path, moist, moist_p, temp, light)
