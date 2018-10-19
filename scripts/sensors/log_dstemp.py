#!/usr/bin/python
import os
import sys
import time
import datetime
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
homedir = os.getenv("HOME")
try:
    list_of_sensors = os.listdir("/sys/bus/w1/devices/")
    print list_of_sensors
except:
    print("Can't list sensors, sorry.")
    list_of_sensors = ['']

#sensor_path = "/sys/bus/w1/devices/28-000004a9f218/w1_slave"
log_path = homedir + "/Pigrow/logs/dstemp_log.txt"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'sp' or thearg == 'full_path':
            sensor_path = thevalue
        is thearg == "sensor":
            senor_path = "/sys/bus/w1/devices/" + thevalue + "/w1_slave"    
        elif thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging one wire temperature sensor ")
        print(" ")
        print(" You will need to have one wire support enabled")
        print("  edit the file /boot/config.txt to contain the")
        print("  line; ")
        print("      dtoverlay=w1-gpio")
        print(" ")
        print(" sensor=SENSORNUMBER")
        print("      - The sensor number, 28-xxxxxxxxxx")
        print(" full_path=/sys/bus/w1/devices/SENSORNUMBER/w1_slave")
        print("      - alternatively to use full path to the temp sensor")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/dstemp_log.txt")
        print("      - path to write the log")
        print("")
        print(" --You will need 1 wire support enabled on the pi")
        print("  ")
        print("")
        sys.exit()
    elif argu == "-flags":
        print("sensor=28-xxxxxxxxxx")
        print("full_path=/sys/bus/w1/devices/SENSORNUMBER/w1_slave")
        print("log_path=" + str(log_path))
        sys.exit()


def read_temp_sensor(sensor):
    sensor_path = "/sys/bus/w1/devices/" + sensor + "/w1_slave"
    try:
        with open(sensor_path, "r") as sensor_data:
            sensor_reading = sensor_data.read()
        temperature = sensor_reading.split("\n")[1].split(" ")[9]
        temperature = float(temperature[2:]) / 1000
    except:
        return None
    return temperature

def log_temp_sensor(log_path, temp_list):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    for temp in temp_list:
        sensor = str(temp[1])
        temp = str(temp[0])
        log_entry += temp + ":" + sensor + ">"
        print("logged temp of " + temp + " from " + sensor + " at " + timenow)
    log_entry = log_entry[:-1] + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)

def temp_c_to_f(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f


temp_list = []
for sensor in list_of_sensors:
    if not sensor == 'w1_bus_master1':
        temp = read_temp_sensor(sensor)
        if not temp == None:
            #crazy americans might want to temp =  temp_c_to_f(temp) about here.
            temp_list.append([temp, sensor])

if len(temp_list) >= 1:
    log_temp_sensor(log_path, temp_list)
