#!/usr/bin/python3
import os, sys, time, datetime
from gpiozero import Button

button_name = None
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'name':
            button_name = thevalue
    elif 'help' in argu or argu == '-h':
        print(" Script for logging the duration of button presses")
        print(" ")
        print(" This requres the button to be configured in the remote gui.")
        print(" ")
        print(" name=button unique name")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("name=")
        sys.exit(0)

if button_name == None:
    print("Button not identified, please include name= in the commandline arguments.")
    sys.exit()

def load_config():
    # Read the settings file
    homedir = os.getenv("HOME")
    sys.path.append(homedir + '/Pigrow/scripts/')
    try:
        import pigrow_defs
        script = 'button_watcher.py'
    except:
        print("pigrow_defs.py not found, unable to continue.")
        print("make sure pigrow software is installed correctly")
        sys.exit()
    loc_dic = pigrow_defs.load_locs(homedir + '/Pigrow/config/dirlocs.txt')
    pigrow_settings = pigrow_defs.load_settings(loc_dic['loc_settings'])
    return pigrow_settings

def read_button_settings(pigrow_settings, button_name):
    # Read the sensor info from the settigns file
    possible_keys = ["button_" + button_name + "_type",
                     "button_" + button_name + "_loc",
                     "button_" + button_name + "_log",
                     "button_" + button_name + "_cmdD",
                     "button_" + button_name + "_cmdU"]
    butt_settings = []
    for possible_key in possible_keys:
        if possible_key in pigrow_settings:
            butt_settings.append(pigrow_settings[possible_key])
        else:
            butt_settings.apend(None)

    if butt_settings[1] == None:
        err_msg = button_name + " location not found in settings file."
        print(err_msg)
    #    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])
        sys.exit()
    return butt_settings

pigrow_settings = load_config()
type, loc, log, cmdD, cmdU = read_button_settings(pigrow_settings, button_name)

def pressed():
    print( " Button Pressed " )
    if not listen.cmdD == None:
        print(" RUNNING - " + cmdD)
        os.system(cmdD + " &")
    if not listen.log == None:
        listen.press_start = time.time()

def released():
    print( " Button released " )
    if not listen.cmdU == None:
        print(" RUNNING - " + cmdU)
        os.system(cmdU + " &")
    if not listen.log == None:
        listen.press_end = time.time()

def listen(gpio_num, log, cmdD, cmdU, *args):
    button = Button(gpio_num)
    listen.cmdD = cmdD
    listen.cmdU = cmdU
    listen.log  = log

    button.wait_for_press()
    pressed()
    button.wait_for_release()
    released()

    if not log == None:
        duration = listen.press_end - listen.press_start
        print("Pressed for", duration)
        log_button_presss(log, duration)


def log_button_presss(log_path, duration):
    timenow = str(datetime.datetime.now())
    line = "time=" + str(timenow)
    line += ">duration=" + str(duration) + "\n"
    with open(log_path, "a") as f:
        f.write(line)
    print("Written; " +  line)

if type == "GND":
    while True:
        listen(loc, log, cmdD, cmdU)
else:
    print("Sensor type not recognised, currently only 'GND' is supported.")
