#!/usr/bin/python3
import time
import os
import sys
#
# setting defaults and blank variables
#
homedir = os.getenv("HOME") #discovers home directory location use in default path generation

#Setting Blank Variables
settings_file = None # this will get turned into a string containing the settings file path


# Handle command line arguments
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Starts motion using the settings in the motion config file")
        print("")
        print(" Supply the pigrow camera config file which points to the motion config file")
        print("   set=" + homedir + "/Pigrow/config/motion_start.txt")
        sys.exit(0)
    elif argu == '-flags':
        print("settings_file=" + homedir + "/Pigrow/config/camera_settings.txt")
        sys.exit()
    if "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                settings_file = theval
        except:
            print("Didn't undertand " + str(argu))


# load settings
def load_settings(settings_file):
    sets_dict = {}
    if not settings_file == None:
        with open(settings_file, "r") as f:
            for line in f:
                if "=" in line:
                    e_pos = line.find("=")
                    key = line[:e_pos].strip()
                    val = line[e_pos+1:].strip()
                    sets_dict[key] = val
    return sets_dict

def create_cmd(sets_dict):
    if "config_path" in sets_dict:
        cmd = "motion -b -c " + sets_dict["config_path"]
        if "log_path" in sets_dict:
            cmd += " -l " + sets_dict["log_path"]
            if "log_level" in sets_dict:
                cmd += " -k " + sets_dict["log_level"]
    return cmd


if __name__ == '__main__':
    if not settings_file == None:
        sets_dict = load_settings(settings_file)
        cmd = create_cmd(sets_dict)
        print(cmd)

    else:
        print("No pigrow camera settings file set, set using")
        print("set=<path to file>")
