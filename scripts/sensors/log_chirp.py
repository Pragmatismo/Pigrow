#!/usr/bin/python
import os
import sys
import time
import datetime
homedir = os.getenv("HOME")
sys.path.append(homedir + '/chirp-rpi/')
import chirp

homedir = os.getenv("HOME")
log_path = homedir + "/Pigrow/logs/chirp_log.txt"
chirp_address = 0x20
min_m = 1
max_m = 1000
temp_offset = 0
sensor_name = ''

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
        elif thearg == 'address' or thearg == 'chirp_address':
            chirp_address = int(thevalue, 16)
        elif thearg == 'min_m':
            min_m = int(thevalue)
        elif thearg == 'max_m':
            max_m = int(thevalue)
        elif thearg == 'temp_offset':
            temp_offset = int(thevalue)
        elif thearg == 'name' or thearg == 'sensor_name':
            sensor_name = thevalue
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for logging the Chirp Soil Moisture Sensor")
        print("     this uses the module chirp-rpi")
        print("     many thanks to Goran Lundberg")
        print("     https://github.com/ageir/chirp-rpi/")
        print(" ")
        print("     You will need I2C support enabled on the pi")
        print("            ( sudo raspi-config )")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/chirp_log.txt")
        print("      - path to write the log")
        print(" chirp_address=0x20")
        print("      - i2c address of the chirp")
        print(" min_m=1")
        print(" max_m=1000")
        print("      - min and max moisture calibration")
        print(" temp_offset=0")
        print("      - temp correction")
        print(" sensor_name=chirp")
        print("      - for sensors named in the config file")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("log=" + str(log_path))
        print("chirp_address=0x20")
        print("min_m=1")
        print("max_m=1000")
        print("temp_offset=0")
        print("sensor_name=chirp")
        sys.exit(0)

if not sensor_name == "":
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    try:
        log_path = set_dic['sensor_' + sensor_name + '_log']
        chirp_text_address = str(set_dic['sensor_' + sensor_name + '_loc'].split(":")[1])
        chirp_address = int(chirp_text_address, 16)
        extras = set_dic['sensor_' + sensor_name + '_extra'].split(",")
        for item in extras:
            if "min:" in item:
                min_m = int(item.split(":")[1])
            elif "max:" in item:
                max_m = int(item.split(":")[1])
            elif "temp_offset" in item:
                temp_offset = int(item.split(":")[1])
    except Exception as e:
        print(" - - - - ! ! ! ! - - - - ! ! ! ! - - - -")
        print("Problem loading settings from config file, ")
        print("    " + log_path)
    print(" -------- ")
    print("   Found Chirp sensor " + sensor_name)
    print("             log path " + log_path)
    print("              address " + str(chirp_text_address) + "  (" + str(chirp_address) + ")")
    print("             moisture min:" + str(min_m) + " max:" + str(max_m))
    print("          temp offset " + str(temp_offset))
    print(" --------                       -------")




def read_chirp_sensor(chirp_address, min_moist, max_moist, temp_offset=0):
    # Initialize the sensor.
    chirp_sensor = chirp.Chirp(address=chirp_address,
                        read_moist=True,
                        read_temp=True,
                        read_light=True,
                        min_moist=min_moist,
                        max_moist=max_moist,
                        temp_scale='celsius',
                        temp_offset=0)
    chirp_sensor.trigger()
    moist = chirp_sensor.moist
    moist_p = chirp_sensor.moist_percent
    temp = chirp_sensor.temp
    light = chirp_sensor.light
    return moist, moist_p, temp, light

def log_chirp_sensor(log_path, moist, moist_p, temp, light):
    timenow = str(datetime.datetime.now())
    log_entry  = timenow + ">"
    log_entry += str(moist) + ">"
    log_entry += str(moist_p) + ">"
    log_entry += str(temp) + ">"
    log_entry += str(light) + "\n"
    with open(log_path, "a") as f:
        f.write(log_entry)
    print("Written; " +  log_entry)


if __name__ == '__main__':
    moist, moist_p, temp, light = read_chirp_sensor(chirp_address, min_m, max_m, temp_offset)
    log_chirp_sensor(log_path, moist, moist_p, temp, light)
