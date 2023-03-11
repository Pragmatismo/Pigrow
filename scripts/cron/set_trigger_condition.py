#!/usr/bin/python3
import sys
import os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

# setting defaults and blank variables
trigger_name = None
set_direct = None
cooldown = "none"

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
        print("name=")
        print("set=on,off,pause")
        print('cooldown=')
        sys.exit()
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
    sys.exit()
if set_direct == None:
    print("It was not specified what to set the condition to, use set=on,off,pause")
    print(" or use --help for more information.")
    sys.exit()

#set the condition
pigrow_defs.set_condition(condition_name=trigger_name, trig_direction=set_direct, cooldown=cooldown)
