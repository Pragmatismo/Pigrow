#!/usr/bin/python3
import datetime
import atexit
import time
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'TESTtimed_water.py'

'''

This require several settings to be in place

         pigrow/config/pigrow_config.txt
              gpio_PUMPNAME=GPIO PIN
              gpio_PUMPNAME_on=relay dir
              pump_PUMPNAME_mlps= flow rate in ml per second
              wtank_TANKNAME_pumps=PUMPNAME
              wtank_TANKNAME_vol=volume in ml

    there should also be a file called
                Pigrow/logs/tankstat_TANKNAME.txt
                     current_ml= current ml volume
                     last_watered= date of last watering
                     active=true (anything but true and it won't work)

'''

# terminate activity on close
active = ""
gpio_pin = None
def exit_handler():
    if active == "high":
        GPIO.output(gpio_pin, GPIO.LOW)
        print ('Pump has been teminated mid use.')
        pigrow_defs.write_log(script, "Terminated mid use", switch_log)
    if active == "low":
        GPIO.output(gpio_pin, GPIO.HIGH)
        print ('Pump has been teminated mid use.')
        pigrow_defs.write_log(script, "Terminated mid use", switch_log)

atexit.register(exit_handler)

# read settings
duration = None
safety = "on"
pumpname = None
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Watering Tool")
        print("")
        print("This turns the Water ON for a given duration then OFF again.")
        print("")
        print("  New version of the watering system, being tested ")
        print("")
        print("   Set up and control in the test gui's watering tab")
        print("")
        print(" Command line options")
        print("")
        print("  duration=number in seconds")
        print("     Runs the water for that amount of seconds")
        print("")
        print("  safety=off")
        print("     Ignore the config file's water_control option")
        print("     This is only for testing purposes, if you want open control")
        print("     select 'any' as the water_control option.")
        sys.exit()
    elif "flags" in argu:
        print("pump=pump name")
        print("duration=time in seconds")
        print("safety=off")
    elif "=" in argu:
        thearg = str(argu).split('=')[0].lower()
        thevalue = str(argu).split('=')[1]
        if thearg == 'duration' or thearg == 'd' or thearg == 's':
            try:
                duration = int(thevalue)
            except:
                print("The duration must be a number value, the time to run the water in seconds")
                sys.exit()
        elif thearg == 'safety':
            safety = thevalue
        elif thearg == "pump":
            pumpname = thevalue

if pumpname == None or duration == None:
    print("pump and duration must be set, ")
    print("  pump=pumpname duration=15 ")
    print("to run the relay called pumpname for fifteen seconds")
    sys.exit()

def init_gpio(gpio_pin):
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(gpio_pin, GPIO.OUT)
    return GPIO

def read_conf(pumpname):
    # load locations config file
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    # pick errlog
    try:
        loc_err_log=loc_dic['err_log']
    except:
        loc_err_log=homedir + "/Pigrow/logs/error_log.txt"

    # load settings from pigrow_config.txt
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_err_log)

    # pick switchlog
    try:
        loc_switchlog = loc_dic['loc_switchlog']
    except:
        default_log_path = homedir + '/Pigrow/logs'
        if os.path.exists(default_log_path):
            loc_switchlog = path.join(default_log_path, 'switch_log.txt')
        else:
            loc_switchlog = "switch_log.txt"

        print(" Switch Log path not found in dirlocs.txt, using " + loc_err_log + " instead.")

    # read data
    pin_key = "gpio_" + pumpname
    pin_dir = "gpio_" + pumpname + "_on"
    gpio_pin = None
    gpio_dir = None
    if pin_key in set_dic:
        if not set_dic[pin_key].strip() == "":
            gpio_pin = set_dic[pin_key]

    if pin_dir in set_dic:
        if not set_dic[pin_dir].strip() == "":
            gpio_dir = set_dic[pin_dir]

    if gpio_pin == None or gpio_dir == None:
        print(" Relay " + pumpname + " is not configured in pigrow_config.txt")
        print(" This should be done in the TEST GUI for best results")
        pigrow_defs.write_log(script, "Failed - relay " + pumpname + " not set in config", loc_err_log)
        sys.exit()

    # flow_rate
    flow_key = "pump_" + pumpname + "_mlps"
    try:
        flow_rate = int(set_dic[flow_key])
        print("Pump flow rate =", flow_rate)
    except:
        flow_rate = None
        print("Pump flow rate not set, unable to calculate water used.")

    return gpio_pin, gpio_dir, flow_rate, loc_switchlog, loc_err_log, set_dic

def get_tank_link(pumpname, set_dic):
    tankname = None
    for item in set_dic:
        if "wtank_" in item:
            if "_pumps" in item:
                tankname = item.split("_")[1]
    if tankname == None:
        print("pump " + pumpname + " is not linked to any water tanks, not doing volume calculations.")
    else:
        print("pump " + pumpname + " linked to water tank " + tankname)
    # get tank size
    try:
        size_key = "wtank_" + tankname + "_vol"
        tank_size = int(set_dic[size_key])
    except:
        print(" Can not determine tank size, ")
        tank_size = None
    return tankname, tank_size

def read_tank_status(tank):
    print("reading tank status right now, lol")
    current_ml = None
    tank_active = "false"
    tank_s_dic = {}
    # read logs/tankstat_TANKNAME.txt
    t_stat_path = homedir + "/Pigrow/logs/tankstat_" + tank + ".txt"
    if os.path.isfile(t_stat_path):
        with open(t_stat_path, "r") as f:
            t_stat_txt = f.read()
        for line in t_stat_txt.splitlines():
            pos = line.find("=")
            if not pos == -1:
                key = line[:pos]
                value = line[pos+1:]
                tank_s_dic[key] = value
    # check if values present
    if "current_ml" in tank_s_dic:
        try:
            current_ml = int(tank_s_dic["current_ml"])
        except:
            print(" Unable to read current_ml from ", t_stat_path, "continuing without")
            current_ml = None
        print (" Starting tank level =", str(current_ml))
    if "active" in tank_s_dic:
        tank_active = tank_s_dic['active']
    # return values
    return current_ml, tank_active

def write_updated_tankstat(tank, tank_level):
    # read fresh in case edited since we started running
    # only change the lines we need to in case there's other info in the file
    c_ml = False
    l_w = False
    t_stat_path = homedir + "/Pigrow/logs/tankstat_" + tank + ".txt"
    if os.path.isfile(t_stat_path):
        with open(t_stat_path, "r") as f:
            t_stat_txt = f.read()
        t_stat_txt = t_stat_txt.splitlines()
        new_txt = []
        for line in t_stat_txt:
            if "current_ml=" in line:
                line = "current_ml=" + str(tank_level)
                c_ml = True
            if "last_watered=" in line:
                line = "last_watered=" + str(datetime.datetime.now())
                l_w = True
            new_txt.append(line)
    # make text
    if c_ml == False:
        new_txt.append("current_ml=" + str(tank_level))
    if l_w == False:
        new_txt.append("last_watered=" + str(datetime.datetime.now()))

    # write file
    tankstat = ""
    for line in new_txt:
        if not line.strip() == "":
            tankstat += line.strip() + "\n"
    t_stat_path = homedir + "/Pigrow/logs/tankstat_" + tank + ".txt"
    with open(t_stat_path, "w") as f:
        f.write(tankstat)

    print(" Written;")
    print(tankstat)
    #

def run_pump(GPIO, gpio_pin, gpio_dir, duration):
    global active
    # when wired so low is on
    if gpio_dir == "low":
        active = "low"
        print(" Turning on by switching GPIO " +str(gpio_pin)+ " to low")
        GPIO.output(gpio_pin, GPIO.LOW)
        print(" Waiting " + str(duration) + " seconds")
        time.sleep(duration)
        print(" Done! Turning the Water OFF")
        GPIO.output(gpio_pin, GPIO.HIGH)
        active = ""
    # when wired so high is on
    elif gpio_dir == "high":
        active = "high"
        print(" Turning on by switching GPIO " +str(gpio_pin)+ " to high")
        GPIO.output(gpio_pin, GPIO.HIGH)
        print(" Waiting " + str(duration) + " seconds")
        time.sleep(duration)
        print(" Done! Turning the Water OFF")
        GPIO.output(gpio_pin, GPIO.LOW)
        active = ""
    # when neither
    else:
        print (" ERROR! Can't determine RELAY wiring direction, unable to continue.")
        print ("        Fix with the Remote Gui or edit pigrow_config.txt")
        pigrow_defs.write_log(script, 'Failed - no direction set in config', err_log)

    # finally
    msg = "watered for " + str(duration) + " seconds."
    pigrow_defs.write_log(script, msg, switch_log)
    print(msg)


if __name__ == '__main__':

    # read config
    gpio_pin, gpio_dir, flow_rate, switch_log, err_log, set_dic = read_conf(pumpname)
    gpio_pin = int(gpio_pin)
    # read tank config
    tank, tank_size = get_tank_link(pumpname, set_dic)
    if not tank == None:
        tank_level, tank_active = read_tank_status(tank)
        if not tank_active.lower() == 'true':
            print("Tank is not set to active, pump will not be run at this time")
            pigrow_defs.write_log(script, 'did not run - tank not set to active', err_log)
            sys.exit()
    # initalise gpio as output
    GPIO = init_gpio(gpio_pin)
    # run pump for set duration
    run_pump(GPIO, gpio_pin, gpio_dir, duration)
    # calculate water use and amend current level
    time.sleep(2) #wait two seconds just to check the low level float sensor isn't taking over this job and killing the process
    if not tank == None:
        if not flow_rate == None:
            used_water = flow_rate * duration
            if not tank_level == None:
                tank_level = tank_level - used_water
                print("Used", used_water, "ml. Tank has", tank_level, "ml remaining")
            else:
                print("Tank level not set, assuming it's full")
                if not tank_size == None:
                    tank_level = tank_size - used_water
                else:
                    print(" Tank size not set, unable to approximate remaining water")
                    tank_level = None
            write_updated_tankstat(tank, tank_level)
