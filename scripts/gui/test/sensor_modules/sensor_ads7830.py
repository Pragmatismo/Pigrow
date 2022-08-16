#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x4b")
        print("default_connection_address=0x4b")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        from smbus import SMBus
    except:
        print("can't import SMBus module")
        print("  It should be installed by default on RaspiOS")
        return None

    # set up and read the sensor
    try:
        bus = SMBus(1)
        bus.write_byte(0x4b, 0x84)
        a0 = bus.read_byte(0x4b)
        #a0 = round(a0, 2)
        logtime = datetime.datetime.now()
        return [['time',logtime], ['a0', a0]]
    except:
        print("--problem reading ads7830")
        return None


if __name__ == '__main__':
    '''
      early testing version, no settings can be changed

      ads7830_commands = (0x84, 0xc4, 0x94, 0xd4, 0xa4, 0xe4, 0xb4, 0xf4)
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
            print(" Modular control for ads7830 Analogue to Digital Converter")
            print("")
            print(" WARNING! ")
            print("    This only reads sensors on 0x4b at the moment")
            print("    it will read that location regardless.")
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
