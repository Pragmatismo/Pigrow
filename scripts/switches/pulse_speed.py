#!/usr/bin/env python3
import sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

device = ""
on_duration = ""
off_duration = ""
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow relay interval control")
        print("")
        print("This changes the pigrow_config.txt setting used by pulse_relay.py")
        print("")
        print("  device=[device name] e.g. fans, lamp, dehumid")
        print("  duration=[on duration]:[off duration]")
        print("           =30:60  - on for thirty seconds then off for sixty")
        print("           =0:1    - solid off")
        print("           =1:0    - solid on")
        print("")
        sys.exit()
    elif "flags" in argu:
        print("device=device name")
        print("duration=on time in seconds:off time in seconds")
        sys.exit()
    elif "=" in argu:
        thearg = str(argu).split('=')[0].lower()
        thevalue = str(argu).split('=')[1]
        if  thearg == 'duration':
            try:
                on_duration = int(thevalue.split(":")[0])
                off_duration = int(thevalue.split(":")[1])
            except:
                on_duration = ""
                off_duration = ""
        if  thearg == 'device':
            device = thevalue

if not device == "":
    if not on_duration == "" and not off_duration == "":
        value = str(on_duration) + ":" + str(off_duration)

        loc_settings = homedir + "/Pigrow/config/pigrow_config.txt"
        setting = "pulse_" + device
        pigrow_defs.change_setting(loc_settings, setting, value)
    else:
        print("No duration spesified, use duration=[on seconds]:[off seconds]")
        print("The duration must be two number values seperated by a : ")
        print("   e.g. duration=10:30")
else:
    print(" No device supplied, use device=[device name]")
