#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x40")
        print("default_connection_address=0x40")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        import busio
        import adafruit_si7021
    except:
        print("adafruit_si7021 module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-si7021")
        return None

    # set up and read the sensor
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_si7021.SI7021(i2c)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        if humidity == None or temperature == None or humidity > 101:
            print("--problem reading si7021")
            return None
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return [['time',logtime], ['humid', humidity], ['temperature', temperature]]
    except:
        print("--problem reading si7021")
        return None


if __name__ == '__main__':
    '''
      The si7021 requires no configuration because it has no settings and can't change address
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
            print(" Modular control for si7021 temp sensors")
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
