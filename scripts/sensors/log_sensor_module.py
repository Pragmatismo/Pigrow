#!/usr/bin/python3
import sys, os
import datetime

# Set name from command line
sensor_name = None
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'name':
            sensor_name = thevalue
    elif 'help' in argu or argu == '-h':
        print(" Script for logging modular sensors")
        print(" ")
        print(" This requres the sensor to be configured in the remote gui.")
        print(" ")
        print(" name=sensor unique name")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("name=")
        sys.exit(0)

if sensor_name == None:
    print("Sensor not identified, please include name= in the commandline arguments.")
    sys.exit()

# Read the settings file
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
    script = 'selflog_graph.py'
except:
    print("pigrow_defs.py not found, unable to continue.")
    print("make sure pigrow software is installed correctly")
    sys.exit()
loc_dic = pigrow_defs.load_locs(homedir + '/Pigrow/config/dirlocs.txt')
pigrow_settings = pigrow_defs.load_settings(loc_dic['loc_settings'])

### TESTING
print (pigrow_settings)

# Read the sensor info from the settigns file
sensor_type = None
sensor_log = None
sensor_loc = None
sensor_extra = None
for key, value in list(pigrow_settings.items()):
    sensor_key = "sensor_" + sensor_name
    if sensor_key in key:
        if "type" in key:
            sensor_type = value
        elif "log" in key:
            sensor_log = value
        elif "loc" in key:
            sensor_loc = value
        elif "extra" in key:
            sensor_extra = value
if sensor_type == None or sensor_log == None or sensor_loc == None or sensor_extra == None:
    err_msg = "Sensor settings not found in " + loc_dic['loc_settings']
    print(err_msg)
    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])

### TESTING
print (sensor_type, sensor_log, sensor_loc)

# Import Sensor Module
try:
    sys.path.append(homedir + '/Pigrow/scripts/gui/sensor_modules')
    module_name = "sensor_" + sensor_type + ".py"
    exec('import ' + module_name + ' as sensor_module', globals())
except:
    err_msg = "Failed to import sensor module for " + sensor_type
    print(err_msg)
    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])

# Read Sensor
sensor_values = read_sensor()

# Create log line containing each returned value
line = ""
for x in sensor_values:
    line = str(x[0]) + "=" + str(x[1])
line = line + "\n"

# Write log line to log
try:
    with open(sensor_log, "a") as f:
        f.write(line)
except:
    err_msg = "Error writing to log, " + sensor_log
    print[err_msg]
    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])
    raise

# Report to user
print("Written log; " + line)
