#!/usr/bin/python3
import os, sys
import datetime
homedir = os.getenv("HOME")

def show_info(duration):
    #
    def check_data_range(time, cut_off):
        if cut_off == "none":
            return True
        time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        if time > cut_off:
            return True
        # if no conditions are true
        return False
    #
    if duration == "all" or duration == "":
        cut_off = "none"
    else:
        timenow = datetime.datetime.now()
        if "hour" in duration:
            duration = duration.replace("hour", "")
            limit = datetime.timedelta(hours=int(duration))
            cut_off = timenow - limit
        elif "day" in duration:
            duration = duration.replace("day", "")
            limit = datetime.timedelta(days=int(duration))
            cut_off = timenow - limit
        else:
            print(" duration arg not understood, defaulting to none")
            cut_off == "none"

    #
    switch_log_path = homedir + "/Pigrow/logs/switch_log.txt"
    if not os.path.isfile(switch_log_path):
        return "No switch log."
    cmd = "cat " + switch_log_path
    out =  os.popen(cmd).read()
    switch_log = out.splitlines()
    switch_dict = {}
    # read the error log into a dictionary
    for line in switch_log:
        line = line.split("@")
        script = line[0]
        time   = line[1].split(".")[0]
        message = line[2]
        if check_data_range(time, cut_off):
            if not script in switch_dict:
                #print( "   adding " + script)
                switch_dict[script]=[[message, 1, time]]
            else:
                count = 0
                list = []
                for switch_info in switch_dict[script]:
                    #print(" --- reading " + switch_info)
                    dict_message = switch_info[0]
                    if message == dict_message:
                        #print(" - already exists ")
                        count = switch_info[1]
                        count = count + 1
                        switch_info=[message, count, time]
                    # create list to replace this scripts error dict entry
                    list.append(switch_info)
                # after cycling through all items in this scripts error dict
                if count == 0:
                    switch_dict[script].append([message, 1, time])
                else:
                    switch_dict[script] = list
    # create text output
    text_out = "Recent actions; \n"
    text_out += " Count  -  Last Seen  -  Message\n"
    for key, value in switch_dict.items():
        text_out += " -- " + key + ": \n"
        for switch_info in value:
            text_out += "    " + str(switch_info[1]) + "  " + switch_info[2] + "   " + str(switch_info[0]) + "\n"


# log_sensor_module.py@2020-07-03 19:40:01.631992@Failed to import sensor module for EZOph


    return text_out

if __name__ == '__main__':
    duration = "all"
    for argu in sys.argv:
        argu_l = argu.lower()
        if argu_l == '-h' or argu_l == '--help':
            print("   Switch log viewer ")
            print(" ")
            print("     This is mostly used by the datawall and phone app")

            print("     ")
            print('  duration=all      -entire script log')
            print('          =hourN    -last N hours of script log')
            print('          =dayN     -last N days of script log')
            sys.exit(0)
        elif argu_l == "-flags":
            print("duration=all,hourN,dayN")
            sys.exit(0)
        elif "=" in argu:
            thearg = str(argu_l).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'duration':
                duration = theval

    print(show_info(duration))
