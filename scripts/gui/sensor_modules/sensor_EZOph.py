#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=")
        print("default_connection_address=99")


def read_sensor(location="", extra="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    try:
        from AtlasI2C import AtlasI2C
    except:
        print("Unable to import AtlasI2C, make sure this is installed")
        print("Clone from https://github.com/Atlas-Scientific/Raspberry-Pi-sample-code.git")
        sys.exit()

    device = AtlasI2C()
    device.set_i2c_address(int(location))
    #device_address_list = device.list_i2c_devices()
    read_attempt = 1
    valid_result = "None"
    while read_attempt < 5:
        try:
            ph = device.query("R")
            if "Success" in ph:
                valid_result = "True"
                ph = ph.split(":")[1].strip()
            #
            if valid_result == "None":
                print("--problem reading Atlas Scientific EZO ph, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                data = [['time',logtime], ['ph', ph]]
                return data
        except Exception as e:
            print("--exception while reading Atlas Scientific EZO ph, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The EZO ph can use any i2c address and has various Calibration
      and temperature compensation options
      '''
     # check for command line arguments
    sensor_location = "99"
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for EZO ph module")
            print(" ")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("location=")
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()
    # read sensor
    #if not sensor_location == "":
    output = read_sensor(location=sensor_location)
    #else:
    #    print(" No sensor address supplied, this requries a sensor address.")
    #    sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
        print(" Check sensor location is correct")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
