#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x39")
        print("default_connection_address=0x39")


def read_sensor(location="", extra="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    import smbus

    # set up and read the sensor

    read_attempt = 1
    while read_attempt < 5:
        try:
            bus = smbus.SMBus(1)
            bus.write_byte_data(0x39, 0x00 | 0x80, 0x03)
            bus.write_byte_data(0x39, 0x01 | 0x80, 0x02)
            time.sleep(0.5)
            data = bus.read_i2c_block_data(0x39, 0x0C | 0x80, 2)
            data1 = bus.read_i2c_block_data(0x39, 0x0E | 0x80, 2)
            fullspect = data[1] * 256 + data[0]
            ir = data1[1] * 256 + data1[0]
            vis = fullspect - ir
            #
            if fullspect == None:
                print("--problem reading tsl2561, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                data = [['time',logtime], ['fullspectrum', fullspect], ['ir',ir], ['visible',vis]]
                return data
        except Exception as e:
            print("--exception while reading tsl2561, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The tsl2561 semetimes has changeable addreses but this does not yet support that because i've not got one that does to test
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
            print(" Modular control for tsl2561 light sensor")
            print(" ")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            #print("location=")
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
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
