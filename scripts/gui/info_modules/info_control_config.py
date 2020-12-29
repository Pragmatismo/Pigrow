#!/usr/bin/python3
import os
import sys
import subprocess
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def show_info():
    # Read config
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])

    text_out = ""
    checkdht_start = False
    trigger_watcher_start = False
    watcher_button_start = False
    # determine which control method is enabled
    out = subprocess.getoutput("crontab -l")
    for line in out.splitlines():
        if not line.strip()[0] == "#":
            if "@reboot" in line:
                if "checkDHT.py" in line:
                    checkdht_start = True
                    dht_cronline = line
                elif "trigger_watcher.py" in line:
                    trigger_watcher_start = True
                    tw_cronline = line
                elif "watcher_button.py" in line:
                    watcher_button_start = True
    if not checkdht_start and not trigger_watcher_start:
        text_out += "No control script set, if you wish to control devices then enable"
        text_out += " trigger_watcher.py to start on reboot."
    elif checkdht_start and trigger_watcher_start:
        text_out += "trigger_watcher.py and checkDHT.py are both set to run on reboot, these"
        text_out += "will conflict and may cause problems, it's highly recomended you remove one. "
        text_out += "Keep trigger_watcher to use log based triggers."
    elif checkdht_start:
        text_out += "Using checkDHT.py - this is now obsolete, to use log based triggers switch to using trigger_watcher.py"
    elif trigger_watcher_start:
        text_out += "Using trigger_watcher.py"
    text_out += "\n\n"
    # Add check to see if sctipt is running

    #
    if checkdht_start:
        #
        # old code for obsolete system
        #

        dht_msg = ""
        #heater on and off temps
        if "gpio_heater" in set_dic:
            dht_msg += "heater enabled, "
        else:
            dht_msg += "no heater gpio, "
        # low
        if "heater_templow" in set_dic:
            heater_templow =  set_dic["heater_templow"]
            dht_msg += "Temp low; " + str(heater_templow) + " "
        else:
            dht_msg += "\nheater low temp not set\n"
            heater_templow = None
        # high
        if "heater_temphigh" in set_dic:
            heater_temphigh = set_dic["heater_temphigh"]
            dht_msg += "temp high: " + str(heater_temphigh) + " (Centigrade)\n"
        else:
            dht_msg += "\nheater high temp not set\n"
            heater_temphigh = None

        #
        # read humid info
        if "gpio_humid" in set_dic or "gpio_dehumid" in set_dic:
            dht_msg += "de/humid linked, "
        else:
            dht_msg += "de/humid NOT linked, "
        # low
        if "humid_low" in set_dic:
            humid_low = set_dic["humid_low"]
            dht_msg += "humidity low; " + str(humid_low)
        else:
            dht_msg += "\nHumid low not set\n"
            humid_low = None
        # high
        if "humid_high" in set_dic:
            humid_high = set_dic["humid_high"]
            dht_msg += " humidity high: " + str(humid_high) + "\n"
        else:
            dht_msg += "humid high not set\n\n"
            humid_high = None

        #
        #add gpio message to the message text
        if "dht22sensor" in set_dic:
            dht_msg += "DHT Sensor on pin " + str(set_dic['dht22sensor'] + "\n")
            if "log_frequency" in set_dic:
                log_frequency = set_dic["log_frequency"]
                dht_msg += "Logging dht every " + str(log_frequency) + " seconds. \n"
            else:
                log_frequency = ""
                dht_msg += "DHT Logging frequency not set\n"
            #check to see if log location is set in dirlocs.txt
            try:
                dht_msg += "logging to; " + dirlocs_dict['loc_dht_log'] + "\n"
            except:
                dht_msg += "No DHT log locaion in pigrow dirlocs\n"
        else:
            dht_msg += "DHT Sensor not set up for checkDHT.py\n"


        #extra args used to select options modes, if to ignore heater, etc.
        cmd_string = dht_cronline[8:]
        first_space = cmd_string.find(" ")
        extra_args = cmd_string[first_space:]

        if not extra_args == ""
            dht_msg += "extra args = " + extra_args + "\n"

         #heater
        if "use_heat=true" in extra_args:
            dht_msg += "heater enabled, "
        elif "use_heat=false" in extra_args:
            dht_msg += "heater disabled, "
        else:
            dht_msg += "heater enabled, "

         #humid
        if "use_humid=true" in extra_args:
            dht_msg += "humidifier enabled, "
        elif "use_humid=false" in extra_args:
            dht_msg += "humidifier disabled, "
        else:
            dht_msg += "humidifier enabled, "

         #dehumid
        if "use_dehumid=true" in extra_args:
            dht_msg += "dehumidifier enabled, "
        elif "use_dehumid=false" in extra_args:
            dht_msg += "dehumidifier disabled, "
        else:
            dht_msg += "dehumidifier enabled, "

         #who controls fans
        if "use_fan=heat" in extra_args:
            dht_msg += "fan switched by heater "
        elif "use_fan=hum" in extra_args:
            dht_msg += "fan switched by humidifer "
        elif "use_fan=dehum" in extra_args:
            dht_msg += "fan switched by dehumidifer "
        elif "use_fan=hum" in extra_args:
            dht_msg += "dht control of fan disabled "
        else:
            dht_msg += "fan swtiched by heater"

    if trigger_watcher_start:
        text_out += ""



    return text_out + dht_msg


if __name__ == '__main__':
    print(show_info())
