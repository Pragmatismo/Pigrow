#!/usr/bin/python3
import sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=dt_pin:sck_pin")
        print("connection_address_list=")
        print("default_connection_address=")
        print("available_info=cal_values")
        print("available_settings=cal_zero")

    def run_request(request_name, sensor_location, sensor_name=""):
        request_name = request_name.lower()
        if request_name == "cal_values":
            sensor_config.read_cal(sensor_name)
        else:
            print(" Request not recognised")

    def run_setting(setting_string, location, sensor_name=""):
        if "=" in setting_string:
            equals_pos = setting_string.find("=")
            setting_name = setting_string[:equals_pos]
            setting_value = setting_string[equals_pos + 1:]
            if setting_name == "cal_zero":
                sensor_config.cal_zero(location, sensor_name, setting_value)
        # settings without value

    # Change Settings
    def cal_zero(location, sensor_name, value):
        if sensor_name == "":
            print(" No sensor name supplied, can not calibrate")
            return("No sensor name supplied, can not calibrate")
        # calibrating from sensor or supplied value
        if value == "":
            reading0 = read_sensor(location, raw_only=True)
            if not reading0 == "none":
                offset = float(reading0)
            else:
                return "Sensor failed to read"
        else:
            try:
                offset = float(value)
            except:
                print(" Unable to understand supplied offset value")
                return(" Unable to understand supplied offset value")
        # writing to config file
        text_out = " Zero offset value set to " + str(offset)
        sensor_config.set_extra("zero_offset", offset, sensor_name)
        print(text_out)
        return text_out

    # Information Requests - these do not change any settings.
    def read_cal(sensor_name, quiet=False):
        loc_settings = homedir + "/Pigrow/config/pigrow_config.txt"
        extra = pigrow_defs.read_setting(loc_settings, "sensor_" + sensor_name + "_extra")
        if extra == "":
            msg = " - No extra string set for sensor " + sensor_name
            print(msg)
            return msg, {}
        zero_offset =   "Not set"
        known_grams =   "Not set"
        known_g_value = "Not set"
        if ":" in extra:
            settings = extra.split(":")
        else:
            settings = [extra]
        #
        for set in settings:
            if "=" in set:
                key = set.split("=")[0]
                val = set.split("=")[1]
                if key == "zero_offset":
                    zero_offset = val
                if key == "known_grams":
                    known_grams = val
                if key == "known_g_value":
                    known_g_value = val

        text_info = "zero_offset = " + str(zero_offset)
        text_info += "\nKnown value " + str(known_grams) + " grams"
        text_info += "\n            " + str(known_g_value) + " raw sensor value"
        if not quiet == True:
            print(text_info)
        return text_info, {"zero_offset":zero_offset, "known_grams":known_grams, "known_g_value":known_g_value}

    # Read and Write extra string to config
    def set_extra(key, value, sensor_name):
        text, extra_settings = sensor_config.read_cal(sensor_name, quiet=True)
        extra_settings[key]=value
        # make extra string
        extra_string = ""
        for setting, set_value in extra_settings.items():
            extra_string += setting + "=" + str(set_value) + ":"
        extra_string = extra_string[:-1]
        # write to config file
        loc_settings = homedir + "/Pigrow/config/pigrow_config.txt"
        pigrow_defs.change_setting(loc_settings, "sensor_" + sensor_name + "_extra", extra_string)



def read_sensor(location="", sensor_name="", raw_only=False, *args):
    # read settings
    if not raw_only == True and not sensor_name == "":
        text, extra_settings = sensor_config.read_cal(sensor_name, quiet=True)
        if extra_settings["zero_offset"] in extra_settings:
            try:
                zero_offset = float(extra_settings["zero_offset"])    # raw value when there is no added weight on the sensor
            except:
                print(" Cant convert zero_offset to float, defaulting to zero")
                zero_offset = 0
        known_grams = 497      # weight of known value measurement in grams
        known_g_value = 494493 - zero_offset # raw value when the known value weight is applied to the sensor

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
            #
            if valid_result == "None":
                print("--problem reading HX711, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                if raw_only == True:
                    return valid_result
                logtime = datetime.datetime.now()
                weight = find_weight(zero_offset, known_grams, valid_result)
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
    sensor_name = ""
    request = ""
    setting_string = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            equals_pos = argu.find("=")
            thearg = argu[:equals_pos]
            thevalue = argu[equals_pos + 1:]
            if thearg == 'location':
                sensor_location = thevalue
            if thearg == 'request':
                request = thevalue
            if thearg == 'set':
                setting_string = thevalue
            if thearg == "name":
                sensor_name = thevalue
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

    if not request == "":
        sensor_config.run_request(request, sensor_location, sensor_name)
        sys.exit()
    if not setting_string == "":
        sensor_config.run_setting(setting_string, sensor_location, sensor_name)
        sys.exit()


    # read sensor
    #if not sensor_location == "":
    output = read_sensor(location=sensor_location, name=sensor_name)
    #else:
    #    print(" No sensor address supplied, this requries a sensor address.")
    #    sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
