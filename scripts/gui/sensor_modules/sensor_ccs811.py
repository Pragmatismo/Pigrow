#!/usr/bin/env python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x5a")
        print("default_connection_address=0x5a")


def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    try:
        import board
        import busio
        import adafruit_ccs811
    except:
        print("ccs811 module not installed, install using the gui")
        return None

    # set up and read the sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    ccs811 = adafruit_ccs811.CCS811(i2c)
    # Wait for the sensor to be ready
    while not ccs811.data_ready:
        pass
    # Wait some more for a valid reading
    time.sleep(10) # this value is a guess
    # start read attempts
    read_attempt = 1
    co2 = None
    while read_attempt < 5:
        try:
            #
                        # Wait some more for a valid reading
            #print("Reading Sensor...")
            test_data = []
            test_val = 0
            y = 0
            for x in range(0, 50):
                time.sleep(0.25)
                co2 = ccs811.eco2
                if not co2 == 0:
                    y = y + 1
                    test_val = test_val + co2
            test_val = test_val / y
            #print("Run in test value ", test_val)
            test_data.append(["co2_run_in", test_val])
            test2_val = 0
            y = 0
            for x in range(0, 50):
                co2 = ccs811.eco2
                if not co2 == 0:
                    y = y + 1
                    test2_val = test2_val + co2
                time.sleep(0.25)
            test2_val = test2_val / y
            #print("test2 value ", test2_val)
            test_data.append(["co2_test_2", test2_val])
            # sleep while the sensor warms up
            time.sleep(20) # this value is a guess
            test2_val = 0
            y = 0
            for x in range(0, 50):
                co2 = ccs811.eco2
                if not co2 == 0:
                    y = y + 1
                    test2_val = test2_val + co2
                time.sleep(0.25)
            test2_val = test2_val / y
            #print("after delay value ", test2_val)
            test_data.append(["co2_after_delay", test2_val])
            #
            co2 = ccs811.eco2
            tvoc = ccs811.tvoc
            if co2 == "None":
                print("--problem reading CCS811, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                data = [['time',logtime], ['co2', co2], ['tvoc',tvoc]]
                data = data + test_data
                #print(data)
                return data
        except Exception as e:
            print("--exception while reading CCS811, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None

if __name__ == '__main__':
    '''
      The CCS811 requires no configureation
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
            print(" Modular control for CCS811 Sensor")
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
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
