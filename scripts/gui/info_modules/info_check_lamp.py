#!/usr/bin/python3
import os, sys
import datetime
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def show_info():
    pigrow_config_path = homedir + "/Pigrow/config/pigrow_config.txt"
    '''
    # Check lamp
    '''
    # check config file
    config_dict = pigrow_defs.load_settings(pigrow_config_path)
    lamp_config_set = False
    lamp_msg = ""
    if "gpio_lamp" in config_dict:
        lamp_config_set = True
        # Lamp on
        if "time_lamp_on" in config_dict:
            time_lamp_on = config_dict["time_lamp_on"]
            if ":" in time_lamp_on:
                lamp_on_hour = int(time_lamp_on.split(":")[0])
                lamp_on_min  = int(time_lamp_on.split(":")[1])
            else:
                lamp_msg += "Lamp on time not valid"
                lamp_config_set = False
        else:
            lamp_msg += "Lamp on time not set in config dict"
            lamp_config_set = False

        # Lamp off
        if "time_lamp_off" in config_dict:
            time_lamp_off = config_dict["time_lamp_off"]
            if ":" in time_lamp_off:
                lamp_off_hour = int(time_lamp_off.split(":")[0])
                lamp_off_min  = int(time_lamp_off.split(":")[1])
            else:
                lamp_msg += "Lamp off time not valid\n"
                lamp_config_set = False
        else:
            lamp_msg += "Lamp off time not set\n"
            lamp_config_set = False
    else:
        lamp_msg += "No lamp set in pigrow_config.txt\n"

    # Time gap
    if lamp_config_set == True:
        on_time = datetime.time(int(lamp_on_hour),int(lamp_on_min))
        off_time = datetime.time(int(lamp_off_hour), int(lamp_off_min))
        aday = datetime.timedelta(days=1)
        if on_time > off_time:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + aday))
        else:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))

        length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))
        # message
        lamp_msg += "Lamp turning on at " + str(on_time)[:-3] + " and off at " + str(off_time)[:-3]
        lamp_msg += "\n     (duration " + str(length_lamp_on)[:-3] + " on, "  +str(aday - length_lamp_on)[:-3] + " off)\n"


    # check cron

    out =  os.popen("crontab -l").read()
    cronlines = out.splitlines()
    on_cron  = 0
    off_cron = 0

    def check_time_is_valid(line, hour, min):
        cron_stars = line.split(' ')
        cron_min = cron_stars[0]
        cron_hour = cron_stars[1]
        if not cron_stars[2] == "*" and not cron_stars[3] == "*" and not cron_stars[4] == "*":
            return "Cron contains lamp time not set as daily\n", "bad", ""
        else:
            if hour == int(cron_hour) and min == int(cron_min):
                return "", "good", "match"
            return "", "good", "no match"

    if lamp_config_set == True:
        for line in cronlines:
            if "lamp_on.py" in line:
                msg, valid, on_match = check_time_is_valid(line, lamp_on_hour, lamp_on_min)
                if valid == "good":

                    on_cron += 1
            elif "lamp_off.py" in line:
                msg, valid, off_match = check_time_is_valid(line, lamp_off_hour, lamp_off_min)
                if valid == "good":
                    off_cron += 1
                lamp_msg += msg

    if on_cron == 1 and off_cron == 1:
        if on_match == "match" and off_match == "match":
            lamp_msg += "Config and Cron lamp timing synced."
        else:
            lamp_msg += "Warning! Config and Cron lamp timing not synced."
    # erors
    elif on_cron > 1 or off_cron > 1:
        lamp_msg += "Too many lamp switchings in cron to use all features."
    else:
        if lamp_config_set == True:
            lamp_msg += "Lamp on and off times not set in cron."


    return lamp_msg


if __name__ == '__main__':
    print(show_info())
