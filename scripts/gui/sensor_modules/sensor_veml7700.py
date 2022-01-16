#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x10")
        print("default_connection_address=0x10")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        import adafruit_veml7700
    except:
        print("adafruit_si7021 module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-si7021")
        return None

    # set up and read the sensor
    try:
        i2c = board.I2C()
        sensor = adafruit_veml7700.VEML7700(i2c)
        lux = sensor.light
        logtime = datetime.datetime.now()
        return [['time',logtime], ['lux', lux]]
    except:
        print("--problem reading veml7700 lux sensor;", e)
        return None


if __name__ == '__main__':
    '''
      Currently only works with veml7700 on the default address of 0x10
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
            print(" Modular control for veml7700 lux sensor")
            print(" ")
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
    output = read_sensor()
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
