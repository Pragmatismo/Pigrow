#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=")
        print("default_connection_address=99")
        print("available_info=calibrated,slope,info,temp_compensation,status,extended_scale,protocol_lock")
        print("available_settings=cal_clear,cal_mid,cal_low,cal_high,led,temp,i2c_address,factory_reset,sleep")

    def run_request(request_name, sensor_location):
        request_name = request_name.lower()
        if request_name == "slope":
            sensor_config.read_slope(sensor_location)
        elif request_name in ["calibrated", "cal?"]:
            sensor_config.read_if_calibrated(sensor_location)
        elif request_name == "info":
            sensor_config.read_info(sensor_location)
        elif request_name == "temp_compensation":
            sensor_config.read_temp_comp(sensor_location)
        elif request_name == "status":
            sensor_config.read_status(sensor_location)
        elif request_name == "extended_scale":
            sensor_config.read_extended_scale(sensor_location)
        elif request_name == "protocol_lock":
            sensor_config.read_plock(sensor_location)
        elif request_name == "find":
            print(" YOU HAVEN'T CODED THIS IN YET")
        else:
            print(" Request not recognised")

    def run_setting(setting_string, location):
        #settings = temp, led, cal_mid, cal_low, cal_high, i2c_address
        #witrhout equals = cal_clear, sleep, factory_reset
        if "=" in setting_string:
            equals_pos = setting_string.find("=")
            setting_name = setting_string[:equals_pos]
            setting_value = setting_string[equals_pos + 1:]
        # settings without value
        elif setting_string == "cal_clear":
            sensor_config.cal_clear(location)
        elif setting_string == "sleep":
            sensor_config.set_sleep(location)
        elif setting_string == "factory_reset":
            sensor_config.factory_reset(location)
        # settings with a value after an equals
        if setting_name == "temp":
            sensor_config.set_temp(location, setting_value)
        elif setting_name == "led":
            sensor_config.set_led(location, setting_value.lower())
        elif setting_name == "cal_mid":
            sensor_config.cal_mid(location, setting_value)
        elif setting_name == "cal_low":
            sensor_config.cal_low(location, setting_value)
        elif setting_name == "cal_high":
            sensor_config.cal_high(location, setting_value)
        elif setting_name == "i2c_address":
            sensor_config.change_i2c_address(location, setting_value)


    # run command
    def send_command(location, cmd):
        from AtlasI2C import AtlasI2C
        device = AtlasI2C()
        device.set_i2c_address(int(location))
        setting_output = device.query(cmd)
        text_out = setting_output.strip().strip('\x00')
        print(text_out)
        return text_out

    # Controlls for changing settings
    def change_i2c_address(location, setting):
        cmd = "I2C," + setting
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def factory_reset(location):
        cmd = "Factory"
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def set_sleep(location):
        cmd = "Sleep"
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def cal_clear(location):
        cmd = "Cal,clear"
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def cal_high(location, setting):
        cmd = "Cal,high," + setting
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def cal_low(location, setting):
        cmd = "Cal,low," + setting
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def cal_mid(location, setting):
        cmd = "Cal,mid," + setting
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def set_led(location, setting):
        if setting == "on":
            cmd = "L,1"
        elif setting == "off":
            cmd = "L,0"
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    def set_temp(location, temp):
        cmd = "T," + temp
        text_out = sensor_config.send_command(location, cmd)
        return text_out

    # Information Requests - these do not change any settings.
    def read_info(location):
        cmd = "I"
        text_info = sensor_config.send_command(location, cmd)
        if "Success" in text_info:
            text_info = text_info.split("?I,")[1]
            type = text_info.split(",")[0]
            version = text_info.split(",")[1]
            text_info = "Sensor Type: " + type + " Firmware Version: " + version
        print(text_info)
        return text_info

    def read_slope(location):
        cmd = "Slope,?"
        text_slope = sensor_config.send_command(location, cmd)
        if "Success" in text_slope:
            text_slope = text_slope.split("?SLOPE,")[1]
            acid_dif = text_slope.split(",")[0]
            base_dif = text_slope.split(",")[1]
            voltage_offset = text_slope.split(",")[2]
            text_slope = acid_dif + "acid calibration match to 'ideal' probe.\n"
            text_slope += base_dif + " base calibration match to 'ideal' probe.\n"
            text_slope += voltage_offset + "  millivolts the zero point is off from true 0"
        print(text_slope)
        return text_slope

    def read_plock(location):
        cmd = "Plock,?"
        plock_text = sensor_config.send_command(location, cmd)
        if "?PLOCK,0" in plock_text:
            plock_text = "Protocol lock Disabled"
        elif "?PLOCK,1" in text_ex:
            plock_text = "Protocol lock Enabled"
        print(plock_text)
        return plock_text

    def read_temp_comp(location):
        cmd = "T,?"
        text_temp = sensor_config.send_command(location, cmd)
        print(text_temp)
        return text_temp

    def read_extended_scale(location):
        cmd = "pHext,?"
        text_ex = sensor_config.send_command(location, cmd)
        if "?pHext,1" in text_ex:
            text_ex = "Extended pH Scale Enabled"
        elif "?pHext,0" in text_ex:
            text_ex = "Extended pH Scale Disabled"
        else:
            text_ex = "Error, unable to understand output - " + text_ex
        print(text_ex)
        return text_ex

    def read_status(location):
        cmd = "Status"
        text_status = sensor_config.send_command(location, cmd)
        if "Success" in text_status:
            text_status = text_status.split("?STATUS,")[1]
            reset_reason = text_status.split(",")[0]
            voltage = text_status.split(",")[1]
            if reset_reason == "P":
                reset_reason += " - Powered Off"
            elif reset_reason == "S":
                reset_reason += " - Software Reset"
            elif reset_reason == "B":
                reset_reason += " - Brown out"
            elif reset_reason == "W":
                reset_reason += " - Watchdog"
            elif reset_reason == "U":
                reset_reason += " - unknown"
            text_status = "Reset reason: " + reset_reason + "\nVoltage at Vcc: " + voltage
        print(text_status)
        return text_status

    def read_if_calibrated(location):
        cmd = "Cal,?"
        cal_q_output = sensor_config.send_command(location, cmd)
        if "Success" in cal_q_output:
            text_cal_q = cal_q_output.split("?CAL,")[1].strip().strip('\x00')
            text_cal_q += " Calibration points set"
        else:
            text_cal_q = "Error - success not reported\n" + cal_q_output
        print(text_cal_q)
        return text_cal_q


def read_sensor(location="", extra="", sensor_name="", *args):
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
    sensor_location = ""
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
        elif 'help' in argu or argu == '-h':
            print(" Modular control for EZO ph module")
            print(" ")
            print("")
            print(" -config  ")
            print("        display the config information")
            print(" request=")
            print("       calibrated, slope, info, temp_compensation, status, extended_scale, protocol_lock")
            print("       requests config information from the sensor then exits")
            print("")
            print(" set=[setting]=[value]")
            print("    settings requiring values = temp, led, cal_mid, cal_low, cal_high, i2c_address")
            print("              without values = cal_clear, sleep, factory_reset")
            print("       ")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("location=")
            print("request=calibrated,slope,info,temp_compensation,status,extended_scale,protocol_lock")
            print("set=[setting]=[value]")
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()

    if not request == "":
        sensor_config.run_request(request, sensor_location)
        sys.exit()
    if not setting_string == "":
        sensor_config.run_setting(setting_string, sensor_location)
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
