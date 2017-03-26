
import os
import time
import datetime

sensor_path = "/sys/bus/w1/devices/28-000004a9f218/w1_slave"
log_path = "/home/pi/Pigrow/logs/dstemp_log.txt"

for argu in sys.argv[1:]:
    thearg = str(argu).split('=')[0]
    thevalue = str(argu).split('=')[1]
    if  thearg == 'sp' or thearg == 'sensor_path':
        sensor_path = thevalue
    elif thearg == 'log' or thearg == 'log_path':
        log_path = thevalue
    elif thearg == 'help' or thearg == '-h' or thearg == '--help':
        print(" Script for logging l2c temperature sensor ")
        print(" ")
        print(" sp=/sys/bus/w1/devices/SENSORNUMBER/w1_slave")
        print("      - path to the temp sensor")
        print(" ")
        print(" log=/home/pi/Pigrow/logs/dstemp_log.txt")
        print("      - path to write the log")
        print("")
        print(" --You will need 1 wire support enabled on the pi")
        print("   make sure l2c is enabled in the pi set up program")
        print("")
        exit()


def read_temp_sensor(sensor_path):
    with open(sensor_path, "r") as sensor_data:
        sensor_reading = tempfile.read()
        tempfile.close()
        temperature = sensor_reading.split("\n")[1].split(" ")[9]
        temperature = float(temperature[2:]) / 1000
        return temperature

def log_temp_sensor(log_path, temp):
    timenow = str(datetime.datetime.timenow())
    with open(log_path, "w") as f:
        f.write(temp + ">" + timenow + "\n")
    print("Saved temp of " + temp + " to the log at " + timenow)

def temp_c_to_f(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

temp = read_temp_sensor(sensor_path)
#crazy americans might want to temp =  temp_c_to_f(temp) about here.
log_temp_sensor(log_path, temp)
