#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x44,0x45")
        print("default_connection_address=0x44")
        
        
        
def read_sensor(location=""):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        import busio
        import adafruit_sht31d
    except:
        print("adafruit_sht31d module not installed, install using the command;")
        print("   sudo pip3 install adafruit-circuitpython-sht31d")
        return None

    # set up and read the sensor
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_sht31d.SHT31D(i2c, location)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        if humidity == None or temperature == None or humidity > 101:
            print("--problem reading sht31d")
            return None
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return [['time',logtime], ['humid', humidity], ['temperature', temperature]]
    except:
        print("--problem reading sht31d")
        return None


if __name__ == '__main__':
      '''
      Not implemented: The sht31d can be configured to enable the heater 
      Implemented: and switch addresses between 0x44 and 0x45'''
     # check for command line arguments
    sensor_location = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for AdaSHT31D")
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
    output = read_sensor(location=sensor_location)
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
