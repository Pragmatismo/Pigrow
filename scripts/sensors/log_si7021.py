#!/usr/bin/python3
import sys, os
import datetime
try:
    import board
    import busio
    import adafruit_si7021
except:
    print("adafruit_si7021 module not installed, install using the command:")
    print("     sudo pip3 install adafruit-circuitpython-si7021")

homedir = os.getenv("HOME")
sensor_gpio = None
log_path = homedir + "/Pigrow/logs/si7021_log.txt"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
    elif 'help' in argu or argu == '-h':
        print(" Script for logging Si7021 sensors ")
        print(" ")
        print(" This requres i2c enabled and the adafruit_si7021 module installed.")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/auxdht22_log.txt")
        print("      - path to write the log")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("log=" + str(log_path))
        sys.exit(0)


def read_sensor(sensor):
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_si7021.SI7021(i2c)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        if humidity == None or temperature == None or humidity > 101:
            print("--problem reading sensor on GPIO: "+sensor_gpio+"--")
            return '-1','-1','-1'
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return humidity, temperature, logtime
    except:
        print("--problem reading si7021")
        return '-1','-1','-1'

def log_sensor(log_path, humidity, temperature, logtime):
    try:
        with open(log_path, "a") as f:
            line = str(temperature) + '>' + str(humidity) + '>' + str(logtime) + '\n'
            f.write(line)
    except:
        print["-LOG ERROR-"]
        raise

    print("logged temp of " + str(temperature) + " and humidity of " + str(humidity) + " at " + str(logtime))


def temp_c_to_f(temp_c):
    temp_f = temp_c * 9.0 / 5.0 + 32.0
    return temp_f

# run functions
hum, temp, logt = read_sensor(sensor_gpio)
log_sensor(log_path, hum, temp, logt)
