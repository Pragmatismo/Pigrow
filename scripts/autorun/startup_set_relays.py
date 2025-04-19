#!/usr/bin/env python3
import os
import sys
import datetime
homedir = os.getenv("HOME")

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Start up relay script")
        print("")
        print(" This script should be run at start up to ensure that the ")
        print(" lamp and other timed devices are turned to the correct state ")
        print(" this checks cron for any timed jobs paired device_on.py and _off.py")
        print(" then set's the device to the appropriate state depending on the time.")
        print("")
        print("")
        sys.exit(0)
    elif argu == '-flags':
        sys.exit()



def check_device(device, on_time, off_time):
    current_time = datetime.datetime.now().time()
    # on period spans over midnight
    if on_time > off_time:
        if current_time > on_time or current_time < off_time:
            # replace with cmd call to appropriate device
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_on.py"
            os.system(cmd)
            return 'on', True
        else:
            # replace with cmd call to appropriate device
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_off.py"
            os.system(cmd)
            return 'off', True
    # On period is in the same day
    elif on_time < off_time:
        if current_time > on_time and current_time < off_time:
            # replace with cmd call to appropriate device
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_on.py"
            os.system(cmd)
            return 'on', True
        else:
            # replace with cmd call to appropriate device
            cmd = homedir + "/Pigrow/scripts/switches/" + device + "_off.py"
            os.system(cmd)
            return 'off', True

    elif current_time == on_time:
        return ' - Actually it was a crazy coincidence, exact time match! cron will switch it for us', False
    return 'error', False

def read_cron():
    cron_lines = os.popen('crontab -l').read().splitlines()
    timing_dict = {}

    for line in cron_lines:
        line = line.strip()
        # skip too‑short, blank, reboot or commented out
        if len(line) <= 10 or not line or line.startswith('#') or '@reboot' in line:
            continue

        # split on any whitespace—no empty strings in the result
        parts = line.split()
        # we expect at least 6 parts: minute, hour, dom, mon, dow, command...
        if len(parts) < 6:
            continue

        minute, hour, dom, month, dow = parts[:5]
        cmd = ' '.join(parts[5:])

        # only daily jobs (dom, month, dow all “*”) and numeric time
        if dom == month == dow == '*' and minute.isdigit() and hour.isdigit():
            t = datetime.time(int(hour), int(minute))

            # pick on/off by filename suffix
            if '_on.py' in cmd:
                device = cmd.split('_on.py')[0].split('/')[-1]
                timing_dict[f"{device}| on"] = t
            elif '_off.py' in cmd:
                device = cmd.split('_off.py')[0].split('/')[-1]
                timing_dict[f"{device}| off"] = t

    return timing_dict


# check cron for timed jobs
job_dict = read_cron()
for key, value in job_dict.items():
    if "| on" in key:
        device = key.split("| on")[0]
        counterpart = key.replace("| on", "| off")
        if counterpart in job_dict:
            on_time = job_dict[key]
            off_time = job_dict[counterpart]
            print (device, on_time, off_time)
            condition = check_device(device, on_time, off_time)
        else:
            print(" - No counterpart detected - ")
