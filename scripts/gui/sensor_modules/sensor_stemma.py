#!/usr/bin/env python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x36,0x37x0x38,0x39")
        print("default_connection_address=0x36")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        from adafruit_seesaw.seesaw import Seesaw
    except:
        print("adafruit seesaw module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-seesaw")
        return None

    # set up and read the sensor
    try:
        i2c = board.I2C()
        sensor = Seesaw(i2c, addr=0x36)
        moist = sensor.moisture_read()
        temp = sensor.get_temp()
        moist = round(moist,2)
        temp = round(temp, 2)
        logtime = datetime.datetime.now()
        return [['time',logtime], ['moist', moist], ['temp', temp]]
    except:
        print("--problem reading Stemma soil moisture sensor")
        return None


if __name__ == '__main__':
    '''
      The stemma has four selectable addresses
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
            print(" Modular control for Stemma soil moisture sensors")
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
