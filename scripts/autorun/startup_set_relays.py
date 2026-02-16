#!/usr/bin/env python3
import os
import sys
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Start up relay script")
        print("")
        print(" This script should be run at start up to ensure that the ")
        print(" lamp and other timed devices are turned to the correct state ")
        print(" this checks cron for any timed jobs paired device_on.py and _off.py")
        print(" then set's the device to the appropriate state depending on the time.")
        print("")
        print(" lamp_confirm.py jobs are also checked in the same way")
        print("")
        sys.exit(0)
    elif argu == '-flags':
        sys.exit()

def make_switch_cmd(device, direction, swit):
    cmd = None
    if direction == "on":
        if swit == "relay":
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_on.py"
        elif swit == "lampcon":
            cmd = homedir + f"/Pigrow/scripts/switches/lamp_confirm.py name={device} direction=on"

    elif direction == "off":
        if swit == "relay":
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_off.py"
        elif swit == "lampcon":
            cmd = homedir + f"/Pigrow/scripts/switches/lamp_confirm.py name={device} direction=off"

    return cmd


timed_devices = pigrow_defs.detect_timed_devices()

for device, on_time, off_time, swit in timed_devices:
    print(device, on_time, off_time)
    target_state = pigrow_defs.device_schedule_state(on_time, off_time)

    if target_state:
        cmd = make_switch_cmd(device, target_state, swit)
        if cmd:
            os.system(cmd)
            print(f" --- {device} switched {target_state} by startup script")
        else:
            print(f" --- Unable to determine command for {device}")
    else:
        print(f" --- Unable to determine target state for {device}")

