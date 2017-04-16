#!/usr/bin/python
import os
import sys
import time
import datetime

import Adafruit_ADS1x15 #Requires adafruit ads1x15 installed
adc = Adafruit_ADS1x15.ADS1115()
adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=1)
GAIN = 1

try:
    sys.path.append('/home/pi/Pigrow/scripts/')
    import pigrow_defs
    script = 'log_ads1115.py'
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    log_path = loc_dic['log_path']
    log_path = log_path + "ads1115_log.txt"
    #log_path = loc_dic['loc_adc1115_log']
    loc_settings = loc_dic['loc_settings']
    set_dic = pigrow_defs.load_settings(loc_settings)

except Exception as e:
    print("Using Defaults because - " + str(e))
    log_path = "/home/pi/Pigrow/logs/ads1115_log.txt"

for argu in sys.argv[1:]:
    thearg = str(argu).split('=')[0]
    thevalue = str(argu).split('=')[1]
    if thearg == 'log' or thearg == 'log_path':
        log_path = thevalue
    elif thearg == 'gain':
        GAIN = int(thevalue)
    elif thearg == 'help' or thearg == '-h' or thearg == '--help':
        print(" Script for logging ADS1115 Analogue to Digital Converter ")
        print(" ")
        print(" log=/home/pi/Pigrow/logs/ads1115_log.txt")
        print(" ")
        print(" gain=1")
        print()
        exit()

print("log path : " + str(log_path))


def read_adc():
    try:
        val1 = adc.read_adc(1, gain=GAIN)
        print val1
        val2 = adc.read_adc(2, gain=GAIN)
        val3 = adc.read_adc(3, gain=GAIN)
        val4 = adc.read_adc(4, gain=GAIN)
        return [val1, val2, val3, val4]
    except:
        print("Reading sensor failed")
        return None


def log_ads1115(log_path, vals):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    log_entry += str(vals[0]) + ">"
    log_entry += str(vals[1]) + ">"
    log_entry += str(vals[2]) + ">"
    log_entry += str(vals[3]) + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)


if __name__ == '__main__':
    vals = read_adc()
    if not vals == None:
        log_ads1115(log_path, vals)
