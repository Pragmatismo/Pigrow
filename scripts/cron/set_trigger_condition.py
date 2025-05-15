#!/usr/bin/env python3
#Flags output enabled
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

# setting defaults and blank variables
trigger_name = None
set_direct = None
cooldown = "none"

def get_trig_names():
    trig_path = homedir + "/Pigrow/config/trigger_events.txt"
    names = ""
    with open(trig_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
        first_comma = line.find(",")
        second_comma = first_comma + 1 + line[first_comma + 1:].find(",")
        third_comma = second_comma + 1 + line[second_comma + 1:].find(",")
        fourth_comma = third_comma + 1 + line[third_comma + 1:].find(",")
        fifth_comma = fourth_comma + 1 + line[fourth_comma + 1:].find(",")
        sixth_comma = fifth_comma + 1 + line[fifth_comma + 1:].find(",")
        seventh_comma = sixth_comma + 1 + line[sixth_comma + 1:].find(",")
        eighth_comma = seventh_comma + 1 + line[seventh_comma + 1:].find(",")
        # find values between commas
        log_name = line[:first_comma].strip()
        value_label = line[first_comma + 1:second_comma].strip()
        trigger_type = line[second_comma + 1:third_comma].strip()
        trigger_value = line[third_comma + 1:fourth_comma].strip()
        condition_name = line[fourth_comma + 1:fifth_comma].strip()
        trig_direction = line[fifth_comma + 1:sixth_comma].strip()
        trig_cooldown = line[sixth_comma + 1:seventh_comma].strip()
        cmd = line[seventh_comma + 1:].strip()
        names += condition_name + ","
    return names[:-1]


# Handle command line arguments
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Set Trigger Condition")
        print("")
        print("This tool allows you to manually set a trigger to pause, on, off, or unset")
        print("")
        print(" usage: set_trigger_condition.py name=trigger_name set=pause")
        print("     ")
        print(" use; cam_change_setting.py -flags")
        print("                to see a list of settings")
        sys.exit(0)
    elif argu == '-flags':
        print("name=" + get_trig_names())
        print("set=[on,off,pause]")
        print('cooldown=<INT>')
        sys.exit()
    elif argu == "-defaults":
        print("name=")
        print("set=")
    if "=" in argu:
        key = str(argu).split('=')[0]
        value = str(argu).split('=')[1]
        if key == 'set':
            set_direct = value
        elif key == 'name':
            trigger_name = value
        elif key == "cooldown":
            cooldown = value

#  Check name was supplied
if trigger_name == None:
    print("No trigger name supplied, use --help for more informaiton.")
    print("trigger names;" + get_trig_names())
    sys.exit()
if set_direct == None:
    print("It was not specified what to set the condition to, use set=on,off,pause")
    print(" or use --help for more information.")
    sys.exit()

#set the condition
pigrow_defs.set_condition(condition_name=trigger_name, trig_direction=set_direct, cooldown=cooldown)
