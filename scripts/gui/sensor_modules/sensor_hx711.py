#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=dt_pin:sck_pin")
        print("connection_address_list=")
        print("default_connection_address=")


def read_sensor(location="", extra="", *args):
    zero_offset = 63776
    known_grams = 500
    known_g_value = 494443

    # find weight from value
    def find_weight(zero_offset, known_grams, value):
        zeroed = value - zero_offset
        raw_per_gram = known_g_value / known_grams
        weight = zeroed / raw_per_gram
        #print("Weight : ", weight, " grams")
        return round(weight, 2)

    # sanity check on values
    def check_measures(measures):
        #print("Testing Measures")
        range_buff = 100
        range_min = measures[0] - range_buff
        range_max = measures[0] + range_buff
        limited_list = []
        for x in measures:
            if x < range_max and x > range_min:
                limited_list.append(x)
        if not len(limited_list) > 1:
            limited_list = []
            range_min = measures[1] - range_buff
            range_max = measures[1] + range_buff
            for x in measures:
                if x < range_max and x > range_min:
                    limited_list.append(x)
            if len(limited_list) == 1:
                #print(" Readings are bad" )
                return "None"
        # got list minus crazy values
        if not len(limited_list) > 3:
            return "None"
        total = 0
        for m in limited_list:
            total = total + m
        average = total / len(limited_list)
        return average
        #print("Average ", average)
        #for m in limited_list:
        #    print(m)



    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    import RPi.GPIO as GPIO
    try:
        from hx711 import HX711

    except:
        print("HX711 module not installed, install using the command;")
        print("   sudo pip3 install HX711 ")
        return None


    # set up and read the sensor
    read_attempt = 1
    if not ":" in location:
        print(" - Location should be in the format 'dt_pin:sck_pin' ")
        return None
    dt_pin = int(location.split(":")[0])
    sck_pin = int(location.split(":")[1])
    hx711 = HX711(dout_pin=dt_pin, pd_sck_pin=sck_pin, channel='A', gain=64)
    measures = "None"
    while read_attempt < 5:
        try:
            hx711.reset()
            measures = hx711.get_raw_data()
            valid_result = check_measures(measures)
            weight = find_weight(zero_offset, known_grams, valid_result)
            #
            if valid_result == "None":
                print("--problem reading HX711, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                GPIO.cleanup()
                data = [['time',logtime], ['weight', weight], ['average',valid_result]]
                for pos in range(0, len(measures)):
                    data.append(["reading" + str(pos), measures[pos]])
                return data
        except Exception as e:
            print("--exception while reading HX711, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    GPIO.cleanup()
    return None




if __name__ == '__main__':
    '''
      The HX711 has two wires that need gpio address
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
            print(" Modular control for HX711 weight sensor interface")
            print(" ")
            print(" Location should be in the format 'dt pin:sck_pin")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("location=dt_pin:sck_pin")
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
