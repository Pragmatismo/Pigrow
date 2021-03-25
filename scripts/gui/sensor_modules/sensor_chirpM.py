#!/usr/bin/python3
import sys, os
import time
import datetime
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs


class sensor_config():
    # find connected sensors
    def find_settings():
        '''
        This is used by the GUI to determine which settings to make available,
        seperate with a comma.
        '''
        print("connection_type=i2c")
        print("connection_address_list=any")
        print("default_connection_address=0x20")
        print("available_info=calibration,temp_offset")
        print("available_settings=set_min_cal,set_max_cal,set_temp_offset")

    def run_request(request_name, sensor_location, sensor_name=""):
        '''
        This converts command line information requests to function calls,
        this allows the remote gui and other remote devices to read Information
        directly from the sensor, or from the pi's config files.
        '''
        request_name = request_name.lower()
        if request_name == "calibration":
            sensor_config.calibration_info(sensor_name)
        elif request_name == "temp_offset":
            sensor_config.temp_offset_info(sensor_name)
        else:
            print(" Request not recognised")



    def run_setting(setting_string, location, sensor_name=""):
        '''
          This converts command line setting change requests to function calls,
          It is used both for changing configuration on the sensor module or in
          the pigrow's config file.
        '''
        if "=" in setting_string:
            equals_pos = setting_string.find("=")
            setting_name = setting_string[:equals_pos]
            setting_value = setting_string[equals_pos + 1:]
            if setting_name == "set_min_cal":
                sensor_config.set_min_cal(location, sensor_name, setting_value)
            elif setting_name == "set_max_cal":
                sensor_config.set_max_cal(location, sensor_name, setting_value)
            elif setting_name == "set_temp_offset":
                sensor_config.set_temp_offset(location, sensor_name, setting_value)

    # Functions that Change Settings
    def set_min_cal(location, sensor_name, value):
        # Checks to see if a sensor name has been provided
        if sensor_name == "":
            print(" No sensor name supplied, can not calibrate")
            return("No sensor name supplied, can not calibrate")

        # Determine the setting to record,
        # when calibrating a sensor for example you would put a call to
        #    reading = read_sensor(location, raw_only=True)
        # here we're using the supplied value.
        min_cal = str(value)
        # For sensors using the config file to store settings information
        # use the fuction sensor.config.set_extra to save the new setting
        sensor_config.set_extra("min_cal", min_cal, sensor_name)

        # Once the change is made report to the user what has happened.
        text_out = "Set min_cal to " + value
        print(text_out)
        return text_out

    def set_max_cal(location, sensor_name, value):
        # Checks to see if a sensor name has been provided
        if sensor_name == "":
            print(" No sensor name supplied, can not calibrate")
            return("No sensor name supplied, can not calibrate")

        # Determine the setting to record,
        # when calibrating a sensor for example you would put a call to
        #    reading = read_sensor(location, raw_only=True)
        # here we're using the supplied value.
        max_cal = str(value)
        # For sensors using the config file to store settings information
        # use the fuction sensor.config.set_extra to save the new setting
        sensor_config.set_extra("max_cal", max_cal, sensor_name)

        # Once the change is made report to the user what has happened.
        text_out = "Set max_cal to " + value
        print(text_out)
        return text_out

    def set_temp_offset(location, sensor_name, value):
        # Checks to see if a sensor name has been provided
        if sensor_name == "":
            print(" No sensor name supplied, can not calibrate")
            return("No sensor name supplied, can not calibrate")

        # Determine the setting to record,
        # when calibrating a sensor for example you would put a call to
        #    reading = read_sensor(location, raw_only=True)
        # here we're using the supplied value.
        temp_offset = str(value)
        # For sensors using the config file to store settings information
        # use the fuction sensor.config.set_extra to save the new setting
        sensor_config.set_extra("temp_offset", temp_offset, sensor_name)

        # Once the change is made report to the user what has happened.
        text_out = "Set temp_offset to " + value
        print(text_out)
        return text_out

    # Functions that perform Information Requests - these do not change any settings.
    def calibration_info(sensor_name, quiet=False):
        '''
        Example of reading information from the config files, this can also be
        used to read information from the sensor if it has onboard settings
        such as the EZOph.
        '''
        # read the extra string
        extra = sensor_config.read_extra(sensor_name)

        # if required extract information from the extras string
        output = str(extra)

        # report found information to use user
        print (output)
        return output

    # Read and Write extra string to config
    def read_extra(sensor_name, quiet=False):
        '''
        This reads extra settings from the extras field of the config file,
        format should be sensor_name_extra=set1=val1:set2=val2:set3=val3
        it then hands back a dictionry of set=val
        '''
        #
        if sensor_name == "":
            print("Sensor Name must be supplied using name=")
            return None
        #
        loc_settings = homedir + "/Pigrow/config/pigrow_config.txt"
        extra = pigrow_defs.read_setting(loc_settings, "sensor_" + sensor_name + "_extra")
        #
        if extra == "":
            print(" No calibration information ")
            return []
        #
        if ":" in extra:
            extra_list = extra.split(":")
        else:
            extra_list = [extra]
        # add items into a dictionary called extra_settings
        extra_setings = {}
        for item in extra_list:
            if "=" in item:
                set, val = item.split("=")
                extra_setings[set] = val
        return extra_setings


    def set_extra(key, value, sensor_name):
        '''
        This changes a single setting in the extras string
        '''
        if sensor_name == "":
            print("Sensor Name must be supplied using name=")
            return None
        # Read current extra string
        extra_settings = sensor_config.read_extra(sensor_name)

        # change the required setting or add if not already present
        extra_settings[key]=value

        # remake the extra string using the new value
        extra_string = ""
        for setting, set_value in extra_settings.items():
            extra_string += setting + "=" + str(set_value) + ":"
        extra_string = extra_string[:-1]
        # write to config file
        loc_settings = homedir + "/Pigrow/config/pigrow_config.txt"
        pigrow_defs.change_setting(loc_settings, "sensor_" + sensor_name + "_extra", extra_string)

#
# Sensor code
#

def check_if_valid(reading):
    '''
    checks validity of results, for example excluding bad readings
    returns the reading if vaid or "None" if not
    '''
    if not reading == "":
        return reading
    else:
        return "None"


def read_sensor(location="", extra="", sensor_name="", raw_only=False, *args):
    '''
    This contains the code required to read the sensor,
    '''
    #
    min_moist   = 0
    max_moist   = 0
    temp_offset = 0
    chirp_address = int(location, 16)
    # read settings
    if not raw_only == True and not sensor_name == "":
        extra_settings = sensor_config.read_extra(sensor_name, quiet=True)
        # locate Chirp setting and test to see if it can be used as a number
        if "min_moist" in extra_settings:
            try:
                min_moist = int(extra_settings["min_moist"])
            except:
                print(" Cant convert min_moist to int, defaulting to zero")
                print(" !!!! add error log call here !!!! ")
                min_moist = 0
        if "max_moist" in extra_settings:
            try:
                max_moist = int(extra_settings["max_moist"])
            except:
                print(" Cant convert max_moist to int, defaulting to 10000")
                print(" !!!! add error log call here !!!! ")
                max_moist = 10000
        if "temp_offset" in extra_settings:
            try:
                temp_offset = int(extra_settings["temp_offset"])
            except:
                print(" Cant convert temp_offset to int, defaulting to temp_offset")
                print(" !!!! add error log call here !!!! ")
                temp_offset = 0

    # Try importing the modules then give-up and report to user if it fails
    # although PIP suggests all imports be at the top of the file these must be
    # here as they will only exist on the raspberry pi not the local system
    try:
        homedir = os.getenv("HOME")
        sensor_module_folder = homedir + "/Pigrow/scripts/gui/sensor_modules/"
        sys.path.append(sensor_module_folder + 'chirp-rpi/')
        import chirp
    except:
        print("chirp-rpi module could not be started;")
        print("   install using the gui - chirp-rpi ")
        return None

    # set up and read the sensor
    if True == False:
        chirp_sensor = chirp.Chirp(address=chirp_address,
                            read_moist=True,
                            read_temp=True,
                            read_light=True,
                            min_moist=min_moist,
                            max_moist=max_moist,
                            temp_scale='celsius',
                            temp_offset=0)
    else:
        chirp_sensor = chirp.Chirp(address=chirp_address,
                            read_moist=True,
                            read_temp=True,
                            read_light=True,
                            temp_scale='celsius',
                            temp_offset=0)

    #
    measures = "None"
    read_attempt = 1
    while read_attempt < 5:
        try:
            # replace with with code for function for reading the sensor
            chirp_sensor.trigger()
            moist = chirp_sensor.moist
            moist_p = chirp_sensor.moist_percent
            temp = chirp_sensor.temp
            light = chirp_sensor.light
            # check if result is valid
            valid_result = check_if_valid(moist)
            # retry if no valid result or report the good value
            if valid_result == "None":
                print("--problem reading Chirp, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                # for calibration, just return the values without other info
                if raw_only == True:
                    return valid_result
                # create list of values to return
                logtime = datetime.datetime.now()
                #            add code or functions here if needing to convert
                #            raw data into calibrated values.
                data = [['time',logtime], ['moist',valid_result], ['moist_p',moist_p], ['temp',temp], ['light',light]]
                return data
        # Handle problems with sensor module
        except Exception as e:
            print("--exception while reading Chirp, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    # if unable to find a reading after five attempts give up.
    return None




if __name__ == '__main__':
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
            print(" Modular control for BLANK TEMPLATE")
            print(" ")
            print("  NOTE HERE HOW THE SETTINGS WORK")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("name=")
            print("location=")
            print("request=request_name")
            print("set=setting_name=value")
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
    output = read_sensor(location=sensor_location, sensor_name=sensor_name)
    #else:
    #    print(" No sensor address supplied, this requries a sensor address.")
    #    sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
    else:
        # list all the readings that the sensor gave and print them onto the screen.
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
