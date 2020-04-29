#!/usr/bin/python3
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
        print(" It also deletes the Pigrow/logs/trigger_conditions.txt file")
        print(" to ensure that relays are set to their correct state the")
        print(" next time the sensor is read to the associated log.")
        print("")
        print(" If you want to set the relays right away after a reboot then call")
        print("the sensors logging script directly after this one on boot. ")
        print("  - an .sh file listing the commands makes this process simpler")
        sys.exit(0)
    elif argu == '-flags':
        sys.exit()

def clear_conditions():
    cmd = "rm " + homedir + "/Pigrow/logs/trigger_conditions.txt"
    os.system(cmd)

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
    cron_text = os.popen('crontab -l').read() # os.system("crontab -l")
    cron_text = cron_text.split('\n')
    timing_dict = {}
    for cron_line in cron_text:
        cron_line = cron_line.strip()
        # ignore start up jobs
        if len(cron_line) > 10:
            if not "@reboot" in cron_line:
                # ignore muted jobs
                if not cron_line[0] == '#':
                    # determine if it's a daily job
                    split_cron = cron_line.split(' ')
                    if split_cron[2] == "*" and split_cron[3] == "*" and split_cron[4] == "*":
                        if split_cron[0].isdigit() and split_cron[1].isdigit():
                            # find device settings
                            if "_on.py" in cron_line:
                                on_time = datetime.time(int(split_cron[1]),int(split_cron[0]))
                                device = cron_line.split("_on.py")[0].split("/")[-1]
                                timing_dict[device + "| on"] = on_time
                            elif "_off.py" in cron_line:
                                off_time = datetime.time(int(split_cron[1]),int(split_cron[0]))
                                device = cron_line.split("_off.py")[0].split("/")[-1]
                                timing_dict[device + "| off"] = off_time
    return timing_dict

# empty the conditions file
clear_conditions()
# check cron for timed jobs and flip them
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
