#!/usr/bin/python
import os
import sys
import time
import datetime
from Adafruit_GPIO import I2C

#sensor_path = "/sys/bus/w1/devices/28-000004a9f218/w1_slave"
log_path = "/home/pi/Pigrow/logs/chirp_log.txt"

for argu in sys.argv[1:]:
    thearg = str(argu).split('=')[0]
    thevalue = str(argu).split('=')[1]
    if thearg == 'log' or thearg == 'log_path':
        log_path = thevalue
    elif thearg == 'help' or thearg == '-h' or thearg == '--help':
        print(" Script for logging the Chirp Soil Moisture Sensor")
        print(" ")
        print(" ")
        print(" ")
        print(" log=/home/pi/Pigrow/logs/chirp_log.txt")
        print("      - path to write the log")
        print("")
        print(" --You will need I2C support enabled on the pi")
        print("     (do it with sudo raspi-config ")
        print("")
        exit()

def read_chirp_sensor():
    chirp_address = 0x20
    chirp = I2C.get_i2c_device(chirp_address)
    #print str(chirp)
    chirp.write8( chirp_address, 0x06 ) #reset
    time.sleep(5) #waits for reset

    chirp.write8(chirp_address, 3)
    time.sleep(3)
    light = chirp.readU16(4, False)
    temp = chirp.readS16(5, False)/float(10)
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


moist, temp, light = read_chirp_sensor()
#crazy americans might want to temp =  temp_c_to_f(temp) about here.
log_chirp_sensor(log_path, moist, temp, light)
