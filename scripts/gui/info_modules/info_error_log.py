#!/usr/bin/python3
import os
homedir = os.getenv("HOME")

def show_info():
    #
    error_log_path = homedir + "/Pigrow/logs/err_log.txt"
    if not os.path.isfile(error_log_path):
        return "No error log, hopefully that means there have been no errors."
    cmd = "tail -25 " + error_log_path
    out =  os.popen(cmd).read()
    error_log = out.splitlines()
    error_dict = {}
    # read the error log into a dictionary
    for line in error_log:
        line = line.split("@")
        script = line[0]
        time   = line[1]
        message = line[2]
        if not script in error_dict:
            #print( "   adding " + script)
            error_dict[script]=[[message, 1, time]]
        else:
            count = 0
            list = []
            for script_error in error_dict[script]:
                #print(" --- reading " + script_error)
                dict_message = script_error[0]
                if message == dict_message:
                    #print(" - already exists ")
                    count = script_error[1]
                    count = count + 1
                    script_error=[message, count, time]
                # create list to replace this scripts error dict entry
                list.append(script_error)
            # after cycling through all items in this scripts error dict
            if count == 0:
                error_dict[script].append([message, 1, time])
            else:
                error_dict[script] = list
    # create text output
    text_out = "Recent errors; \n"
    text_out += " Count  -  Last Seen  -  Message\n"
    for key, value in error_dict.items():
        text_out += " -- " + key + ": \n"
        for problem in value:
            text_out += "  " + str(problem[1]) + "  " + problem[2] + "   " + str(problem[0]) + "\n"


# log_sensor_module.py@2020-07-03 19:40:01.631992@Failed to import sensor module for EZOph


    return text_out

if __name__ == '__main__':
    print(show_info())
