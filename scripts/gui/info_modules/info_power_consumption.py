#!/usr/bin/python3
import os
import sys
import datetime
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def show_info():
    #
    switch_log_path = homedir + "/Pigrow/logs/switch_log.txt"
    if not os.path.isfile(switch_log_path):
        return "No switch log."
    cmd = "cat " + switch_log_path
    out =  os.popen(cmd).read()
    switch_log = out.splitlines()
    switch_dict = {}
    # read the switch log into lists
    timing_dict = {}
    for line in switch_log:
        line = line.split("@")
        script = line[0]
        time   = line[1]
        message = line[2]
        if "_on.py" in script:
            device = script.split("_on.py")[0]
            device_timing = ["on", time]
            if device in timing_dict:
                timing_dict[device] = timing_dict[device] + [device_timing]
            else:
                timing_dict[device] = [device_timing]
        elif "_off.py" in script:
            device = script.split("_off.py")[0]
            device_timing = ["off", time]
            if device in timing_dict:
                timing_dict[device] = timing_dict[device] + [device_timing]
            else:
                timing_dict[device] = [device_timing]
    # if last switch was on then calculate to current time
    for key, value in timing_dict.items():
        if value[-1][0] == "on":
            #print(key, " is currently on")
            time_now = datetime.datetime.now()
            timing_dict[key] = timing_dict[key] + [["off", str(time_now)]]


    #print (timing_dict[lamp])
    duration_dict = {}
    for key, value in timing_dict.items():
        #print( key, value)
        duration = datetime.timedelta(minutes=0)
        time_on = None
        for item in value:
            if item[0] == "on":
                time_on = datetime.datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S.%f')
            else:
                if not time_on == None:
                    time_off = datetime.datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S.%f')
                    step_duration = time_off - time_on
                    duration = duration + step_duration
                    time_on = None
            duration_dict[key] = duration

    # Read config for power settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    # cost per kwh from settings dict
    if "cost_kwh_cent" in set_dic:
        cost_kwh_cent = float(set_dic["cost_kwh_cent"])
    else:
        cost_kwh_cent = None
    # device power
    #device_power_dict = {"lamp":300, "heater":20}
    device_power_dict = {}
    for key, value in set_dic.items():
        if "_watts" in key:
            device = key.split("_watts")[0]
            device_power_dict[device] = float(value)
    #
    text_out = ""
    for key, value in duration_dict.items():
        #print(key, value)
        text_out += key + " has been on for " + str(value) + "\n"
        if key in device_power_dict:
            duration_in_hours = (value.total_seconds() / 60) / 60
            kwhs = (duration_in_hours * device_power_dict[key]) / 1000
            text_out += "using " + str(round(kwhs, 3)) + " KWh\n"
            if not cost_kwh_cent == None:
                cost_of_device = kwhs * cost_kwh_cent
                text_out += "At a cost of " + str(round((cost_of_device /100) , 2)) + "\n"
        text_out += "\n"

    return text_out


if __name__ == '__main__':
    print(show_info())
