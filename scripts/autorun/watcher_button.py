#!/usr/bin/python3
import os, sys, time, datetime
from gpiozero import Button
import subprocess

button_name = None
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'name':
            button_name = thevalue
    elif 'help' in argu or argu == '-h':
        print(" Script for logging the duration or position of button presses")
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
    setting_path = homedir + '/Pigrow/config/pigrow_config.txt'
    pigrow_settings = pigrow_defs.load_settings(setting_path)
    return pigrow_settings

def read_button_settings(pigrow_settings, button_name):
    # Read the sensor info from the settigns file
    possible_keys = ["button_" + button_name + "_type",
                     "button_" + button_name + "_loc",
                     "button_" + button_name + "_log",
                     "button_" + button_name + "_logtype",
                     "button_" + button_name + "_cmdD",
                     "button_" + button_name + "_cmdU"]
    butt_settings = []
    for possible_key in possible_keys:
        if possible_key in pigrow_settings:
            butt_settings.append(pigrow_settings[possible_key])
        else:
            butt_settings.append(None)

    if butt_settings[1] == None:
        err_msg = button_name + " location not found in settings file."
        print(err_msg)
        sys.exit()

    return butt_settings

pigrow_settings = load_config()
b_type, loc, log, log_as_switch, cmdD, cmdU = read_button_settings(pigrow_settings, button_name)
if log_as_switch == "True":
    log_as_switch = "switch"
if log == "" or log.lower() == "false":
    log = None


def pressed():
    print( " Button Pressed " )
    # run command
    if listen.cmdD is not None and listen.cmdD != "":
        print(" RUNNING - " + listen.cmdD)
        try:
            subprocess.run(listen.cmdD, shell=True, check=True)
        except subprocess.CalledProcessError:
            print("Failed to run command: " + listen.cmdD)

    # log
    if not listen.log == None:
        if listen.log_as_switch == "switch":
            # record each press individual from release
            log_switch(listen.log, "1")
        else:
            # record press duration
            listen.press_start = time.time()

def released():
    print( " Button released " )
    # run command
    if listen.cmdU is not None and listen.cmdU != "":
        print(" RUNNING - " + listen.cmdU)
        try:
            subprocess.run(listen.cmdU, shell=True, check=True)
        except subprocess.CalledProcessError:
            print("Failed to run command: " + listen.cmdU)

    # log
    if not listen.log == None:
        if listen.log_as_switch == "switch":
            # record each press and release
            log_switch(listen.log, "0")
        else:
            # record press duration
            listen.press_end = time.time()

def listen(gpio_num, log, log_as_switch, cmdD, cmdU, *args):
    button = Button(gpio_num)
    listen.cmdD = cmdD
    listen.cmdU = cmdU
    listen.log  = log
    listen.log_as_switch = log_as_switch

    button.wait_for_press()
    pressed()
    time.sleep(0.1)
    button.wait_for_release()
    released()
    time.sleep(0.1)

    if not log == None and not log_as_switch == "switch":
        duration = listen.press_end - listen.press_start
        print("Pressed for", duration)
        log_button_presss(log, duration)

def log_switch(log_path, label):
    timenow = str(datetime.datetime.now())
    line = "time=" + str(timenow)
    line += ">pos=" + str(label) + "\n"
    with open(log_path, "a") as f:
        f.write(line)
    print("Written; " +  line)

def log_button_presss(log_path, duration):
    timenow = str(datetime.datetime.now())
    line = "time=" + str(timenow)
    line += ">duration=" + str(duration) + "\n"
    with open(log_path, "a") as f:
        f.write(line)
    print("Written; " +  line)

if b_type == "GND":
    while True:
        listen(loc, log, log_as_switch, cmdD, cmdU)
else:
    print("Sensor type not recognised, sorry currently only 'GND' is supported.")
