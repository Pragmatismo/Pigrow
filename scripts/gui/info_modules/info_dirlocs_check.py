#!/usr/bin/python3
import os
homedir = os.getenv("HOME")

def show_info():
    #
    #read pigrow locations file
    pigrow_dirlocs = homedir + "/Pigrow/config/dirlocs.txt"
    out =  os.popen("cat " + pigrow_dirlocs).read()
    dirlocs = out.splitlines()
    dirlocs_dict = {}
    if len(dirlocs) > 1:
        for item in dirlocs:
            if "=" in item:
                item = item.split("=")
                dirlocs_dict[item[0]] = item[1]
    else:
        return "diclocs.txt file is blank"

    # check for required values
    list_of_required_fields = ['path', 'log_path', 'loc_settings', 'err_log', 'loc_switchlog']
    list_of_optional_firelds = ['camera_settings', 'caps_path', 'self_log', 'graph_path']
    msg = ""
    # Add mising required fields
    for item in list_of_required_fields:
        if item not in dirlocs_dict:
            msg += "Missing " + item + "\n"
    # Add missing optional fields
    for item in list_of_optional_firelds:
        if item not in dirlocs_dict:
            msg += "Missing " + item + " (optional)\n"
    return msg



if __name__ == '__main__':
    print(show_info())
