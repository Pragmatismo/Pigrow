#!/usr/bin/python
import os
import sys
homedir = os.getenv("HOME") #discovers home directory location use in default path generation
temp_cron_path = homedir + "/Pigrow/temp/temp_cron.txt" # this will get turned into a string containing the settings file path
script = None
pause = None


setting_to_change = []
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Mute Cron Script")
        print("")
        print("This tool allows you to pause and unpause a script in cron, ")
        print("useful if you don't want to take night images")
        print("")
        print(" usage: cam_pause.py script=camcap.py pause=true")
        print("     ")
        print(" in this instance it will mute any lines that contain the words 'camcap.py' ")
        print(" if you want you can use any other identifier that's included in the line")
        print(" including unique group names added as comments.")
        sys.exit(0)
    elif argu == '-flags':
        print("script=camcap.py")
        print("pause=[true|false]")
        sys.exit()
    if "=" in argu:
        arg = str(argu).split('=')[0]
        val = str(argu).split('=')[1]
        if arg == 'pause':
            pause = val.lower()
        if arg == 'script' or arg == "keyword":
            script = val

if script == None or pause == None:
    print(" You need to supply a keyword or sciprt name and say if you want to pause or unpause")
    print(" use -h or --help for more information")
    sys.exit(1)

current_cron = os.popen('crontab -l').read().strip().splitlines()
print("    ")
print(" Read cron, looking for lines containing " + script + " to change...")
cron_text = ""
for line in current_cron:
    if not "cron_pause" in line:
        if script in line:
            if pause == "true":
                if not "#" in line.split(" ")[0]:
                    line = "#" + line
                    print(" paused - " + line)
                else:
                    print("line was already paused - " + line)
            elif pause == "false":
                if "#" in line.split(" ")[0]:
                    after_hash = line.split("#")[1]
                    line = after_hash + line.split(after_hash)[1]
                    print(" unpaused - " + line)
                else:
                    print(" line was already unpaused - " + line)
    cron_text = cron_text + line + "\n"

#print cron_text

with open(temp_cron_path, "w") as temp_cron:
    temp_cron.write(cron_text)
result = os.popen("crontab " + temp_cron_path).read()
print(result)
