#!/usr/bin/python3
import os
import sys
#
# setting defaults and blank variables
#
homedir = os.getenv("HOME")

# Handle command line arguments
setting_to_change = []
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("               Change setting")
        print("")
        print("This tool allows you to change a value in a setting file")
        print("")
        print("it's especially useful if you want to change brightness for night time")
        print("")
        print(" usage: ")
        print("      change_setting.py conf=camera_settings.txt b_val=200")
        print("     ")
        print(" this changes the b_val in " + homedir + "/Pigrow/config/camera_settings.txt")
        print(" to 200.")
        sys.exit(0)
    elif argu == '-flags':
        print("conf=" + homedir + "/Pigrow/config/camera_settings.txt")
        print("<setting_name>=<new value>")
        sys.exit()
    if "=" in argu:
        epos = argu.find("=")
        arg_key = argu[:epos]
        arg_val = argu[epos+1:]
        if arg_key == 'conf':
            if not "/" in arg_val:
                settings_file_path = homedir + "/Pigrow/config/" + arg_val
            else:
                settings_file_path = arg_val
        else:
            setting_to_change.append(argu)

def find_and_change(old_conf, item):
    new_conf = ""
    for line in old_conf.splitlines():
        if "=" in line:
            if line.split("=")[0] == item.split("=")[0]:
                line = item
        new_conf += line + "\n"
    return new_conf

if len(setting_to_change) == 0:
    print("Didn't give any settings to change, use --help for more informaiton.")
    sys.exit()
if not os.path.isfile(settings_file_path):
    print("Settings file doesn't exist, check the path and try again")
    sys.exit()

# load settings file
with open(settings_file_path, "r") as file:
    config_text = file.read()

for setting in setting_to_change:
    config_text = find_and_change(config_text, setting)

with open(settings_file_path, "w") as file:
    file.write(config_text)
print(config_text)
print("Saved to " + settings_file_path)
