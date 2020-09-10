#!/usr/bin/python
import sys, os
import datetime
import Adafruit_DHT

homedir = os.getenv("HOME")
sensor_gpio = None
log_path = homedir + "/Pigrow/logs/auxdht22_log.txt"
try_attempts = 5

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'gpio':
            sensor_gpio = thevalue
        elif thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging extra dht22 sensors ")
        print(" ")
        print(" gpio=[number]")
        print("      - gpio pin of the sensor")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/auxdht22_log.txt")
        print("      - path to write the log")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("gpio=")
        print("log=" + str(log_path))
        sys.exit(0)


def read_temp_sensor(sensor):
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, sensor_gpio)
        if humidity == None or temperature == None or humidity > 101:
            print("--problem reading sensor on GPIO:"+sensor_gpio+"--")
            return '-1','-1','-1'
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return humidity, temperature, logtime
    except:
        print("--problem reading sensor on GPIO:"+sensor_gpio+"--")
        return '-1','-1','-1'

def log_sensor(log_path, humidity, temperature, logtime):
    try:
        with open(log_path, "a") as f:
            line = str(temperature) + '>' + str(humidity) + '>' + str(logtime) + '\n'
            f.write(line)
    except:
        print["-LOG ERROR-"]

    print("logged temp of " + str(temperature) + " and humidity of " + str(humidity) + " at " + str(logtime))


def temp_c_to_f(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

if not sensor_gpio == None:
    count = 0
    valid_reading = False
    while valid_reading == False:
        hum, temp, logt = read_temp_sensor(sensor_gpio)
        if not logt == '-1':
            valid_reading = True
        count = count + 1
        if count >= try_attempts:
            valid_reading = True     
    log_sensor(log_path, hum, temp, logt)
else:
    print("please set a gpio using the gpio=[number] flag")
