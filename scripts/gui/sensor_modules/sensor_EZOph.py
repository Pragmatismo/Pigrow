#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=")
        print("default_connection_address=99")
        print("available_info=slope,calibrated")

    def run_request(request_name, sensor_location):
        request_name = request_name.lower()
        if request_name == "slope":
            sensor_config.read_slope(sensor_location)
        elif request_name in ["calibrated", "cal", "cal?"]:
            sensor_config.read_if_calibrated(sensor_location)
        else:
            print(" Request not recognised")


    def read_slope(sensor_location):
        from AtlasI2C import AtlasI2C
        device = AtlasI2C()
        device.set_i2c_address(int(sensor_location))
        slope_output = device.query("Slope")
        text_slope = slope_output
        print(text_slope)
        return text_slope

    def read_if_calibrated(sensor_location):
        from AtlasI2C import AtlasI2C
        device = AtlasI2C()
        device.set_i2c_address(int(sensor_location))
        cal_q_output = device.query("Cal,?")
        if "Success" in cal_q_output:
            text_cal_q = str(cal_q_output).split("?CAL,")[1].strip()
            text_cal_q += " Calibration points set"
        else:
            text_cal_q = "Error - success not reported\n" + cal_q_output
        print(text_cal_q)
        return text_cal_q


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
                if "\00" in ph:
                    ph = ph.split("\00")[0]
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
            if thearg == 'request':
                request = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for EZO ph module")
            print(" ")
            print("")
            print(" -config  ")
            print("        display the config information")
            print(" request=")
            print("       requests config information from the sensor then exits")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("location=")
            print("request=slope,calibrated")
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()

    if not request == "":
        sensor_config.run_request(request, sensor_location)
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
