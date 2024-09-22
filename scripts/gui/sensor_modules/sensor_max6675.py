#!/usr/bin/env python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=SPI")
        print("connection_address_list=")
        print("default_connection_address=5")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    import RPi.GPIO as GPIO
    # set up and read the sensor
    GPIO.setmode(GPIO.BCM)
    cs = int(location)
    sck = 11
    so = 9
    GPIO.setup(cs, GPIO.OUT, initial = GPIO.HIGH)
    GPIO.setup(sck, GPIO.OUT, initial = GPIO.LOW)
    GPIO.setup(so, GPIO.IN)

    read_attempt = 1
    while read_attempt < 5:
        try:
            # ask for value
            GPIO.output(cs, GPIO.LOW)
            time.sleep(0.002)
            GPIO.output(cs, GPIO.HIGH)
            time.sleep(0.22)
            GPIO.output(cs, GPIO.LOW)
            GPIO.output(sck, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(sck, GPIO.LOW)
            # read value
            value = 0
            for i in range(11, -1, -1):
                GPIO.output(sck, GPIO.HIGH)
                value = value + (GPIO.input(so) * (2 ** i))
                temperature = value * 0.25
                GPIO.output(sck, GPIO.LOW)

            # finish up
            GPIO.output(sck, GPIO.HIGH)
            error_tc = GPIO.input(so)
            GPIO.output(sck, GPIO.LOW)
            for i in range(2):
                GPIO.output(sck, GPIO.HIGH)
                time.sleep(0.001)
                GPIO.output(sck, GPIO.LOW)
            GPIO.output(cs, GPIO.HIGH)
            #
            GPIO.cleanup()
            #
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return [['time',logtime], ['temperature', temperature]]
        except Exception as e:
            print("--exception while reading MAX6675, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The MAX6675,
      '''
     # check for command line arguments
    sensor_location = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for MAX6675 temp sensors")
            print(" ")
            print(" SPI must be enabled. ")
            print("      SO on GPIO pin 9")
            print("      SCK on GPIO pin 11")
            print("      CS to location pin")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()
    # read sensor
    if not sensor_location == "":
        output = read_sensor(location=sensor_location)
    else:
        print(" No sensor address supplied, this requries a sensor address.")
        sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
