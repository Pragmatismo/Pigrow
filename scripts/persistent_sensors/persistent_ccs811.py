#!/usr/bin/env python3
import os
import sys
import datetime
import time
try:
    import board
    import busio
    import adafruit_ccs811
except:
    print("ccs811 module not installed, install using the gui")
    sys.exit()


homedir = os.getenv("HOME")
sensor_log = homedir + "/Pigrow/logs/persistCCS811.txt"
'''
#  Currently no settings file information is stored for consistent sensors
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
except:
    print("pigrow_defs.py not found, unable to continue.")
    print("make sure pigrow software is installed correctly")
    sys.exit()
loc_dic = pigrow_defs.load_locs(homedir + '/Pigrow/config/dirlocs.txt')
pigrow_settings = pigrow_defs.load_settings(loc_dic['loc_settings'])
'''

# set up and read the sensor
print("Initalising CCS811 sensor")
i2c = busio.I2C(board.SCL, board.SDA)
ccs811 = adafruit_ccs811.CCS811(i2c)
# Wait for the sensor to be ready
while not ccs811.data_ready:
    time.sleep(0.1)
    pass

# Wait some more for a valid reading after it's initalised
time.sleep(10) # this value is a guess

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x5a")
        print("default_connection_address=0x5a")


def read_sensor(location="", extra="", sensor_name="", *args):

    print("Reading Sensor...")
    # start read attempts
    read_attempt = 1
    co2 = None
    while read_attempt < 5:
        try:
            test_data = []

            # second test val

            test_val = 0
            y = 0
            min = 99999999999
            max = 0
            for x in range(0, 50):
                co2 = ccs811.eco2
                if not co2 == 0:
                    y = y + 1
                    test_val = test_val + co2
                    if max < co2:
                        max = co2
                    if min > co2:
                        min = co2
                time.sleep(0.25)
            test_val = round(test_val / y, 2)
            v_range = max - min
            test_data.append(["co2_ave", test_val])
            test_data.append(["co2_ave_range", v_range])
            test_data.append(["co2_ave_datapoints", y])

            # test again

            test2_val = 0
            y = 0
            for x in range(0, 50):
                co2 = ccs811.eco2
                if not co2 == 0:
                    y = y + 1
                    test2_val = test2_val + co2
                time.sleep(0.25)
            test2_val = round(test2_val / y, 2)
            #print("after delay value ", test2_val)
            test_data.append(["co2_ave_2", test2_val])

            # final read and log single entry

            co2 = ccs811.eco2
            tvoc = ccs811.tvoc
            if co2 == "None":
                print("--problem reading CCS811, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                data = [['time',logtime], ['co2_spot', co2], ['tvoc_spot',tvoc]]
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
    sensor_location = "0x5a"
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Constant loop for the CCS811 Sensor")
            print(" ")
            print("  For best results the ccs811 should be run on a ")
            print("   constant loop, add this script to the startup cron")
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
    while True:
        sensor_values = read_sensor(location=sensor_location)
        if sensor_values == None:
            print("!! Failed to read five times !!")
            # shold write to the error log here
            time.sleep(1)
        else:
            line = ""
            for x in sensor_values:
                line = line + str(x[0]) + "=" + str(x[1]) + ">"
            line = line[:-1] + "\n"
            with open(sensor_log, "a") as f:
                f.write(line)
        time.sleep(47.5) # the process has about 12.5 seconds of delays in it already
