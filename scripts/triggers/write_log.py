#!/usr/bin/python3
import datetime
import sys
import os

homedir = os.environ['HOME']
log_path = homedir + "/Pigrow/logs/trigger_log.txt"
script = "write_log.py"
message = ""

for argu in sys.argv[1:]:
    argu_l = str(argu).lower()
    if argu_l == 'help' or argu_l == '-h' or argu_l == '--help':
        print(" Script for writing to a log file")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/trigger_log.txt")
        print(" ")
        print(' script="text with spaces"')
        print('        to include spaces ensure the text is in "speech marks"')
        print("")
        print(' message="text with spaces"')
        print('        to include spaces ensure the text is in "speech marks"')
        sys.exit()
    elif argu_l == '-flags':
        print("log=" + log_path)
        print("script=write_log.py")
        print('message="text to record here"')
        sys.exit()
    elif "=" in argu:
        thearg = argu_l.split('=')[0]
        thevalue = argu.split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = thevalue
        elif thearg == 'script':
            script = thevalue
        elif thearg == 'message':
            message = thevalue

line = script + "@" + str(datetime.datetime.now()) + "@" + message + '\n'

with open(log_path, "a") as f:
    f.write(line)

print("Log writen:" + line)
print("to " + log_path)
