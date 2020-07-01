#!/usr/bin/python3
import sys
import os

class sensor_config():
    # find connected sensors
    def find_settings():
        temp_sensor_list = ""
        w1_bus_folders = os.listdir("/sys/bus/w1/devices")
        for folder in w1_bus_folders:
            if folder[0:3] == "28-":
                temp_sensor_list += folder + ","
        if temp_sensor_list [-1:] == ",":
            temp_sensor_list = temp_sensor_list[:-1]
        # ouput
        print("connection_type=1wire")
        print("connection_address_list=" + temp_sensor_list)
        print("default_connection_address=")


def read_sensor(location="", extra="", *args):
    import datetime
    print(location)
    # read the sensor
    sensor_path = "/sys/bus/w1/devices/" + location + "/w1_slave"
    try:
        with open(sensor_path, "r") as sensor_data:
            sensor_reading = sensor_data.read()
        temp = sensor_reading.split("\n")[1].split(" ")[9]
        temp = float(temp[2:]) / 1000
    except:
        print("--problem reading ds18b20")
        return None
    logtime = datetime.datetime.now()
    return [['time',logtime], ['temp', temp]]


if __name__ == '__main__':
    '''
      The ds18b20
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
            print(" Modular control for ds18b20 temp sensors")
            print(" ")
            print(" location=sensors 1wire location")
            print("          - find using the command")
            print("            ls /sys/bus/w1/devices/")
            print("            it should start with 28-")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("        including currently connected devices")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("location=")
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()


    # Read the sesnor
    if not sensor_location == "":
        output = read_sensor(location=sensor_location)
    else:
        print(" No sensor address supplied, this requries a sensor address.")
        sys.exit()
    # Display the output
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
