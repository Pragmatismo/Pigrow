#!/usr/bin/python
import os
import sys
import time

cappath = ""
delay = 0

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Script for running camcap.py on a delayed loop ")
        print("")
        print("This is useful tool for making short timelapses")
        print("unlike cron it allows delays of less than 1 min")
        print("")
        print(" folder=<folderpath>")
        print("     folder to save images to")
        print(" delay=<NUM>")
        print("    Delay in seconds between each photo")
        print("      (extra delay will be caused by the picture taking process)")
        sys.exit(0)
    if argu == '-flags':
        print("folder=" + cappath)
        print("delay=" + delay)
        print("image=")
        sys.exit(0)
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if thearg == 'cap' or thearg =='caps' or thearg == 'folder':
            cappath = str(argu).split('=')[1]
        elif thearg == 'delay':
            logpath = int(argu).split('=')[1]

if not cappath == "":
    if not os.path.isdir(cappath):
        os.mkdir(cappath)
        print("created " + cappath)
    print("Using camcap.py default caps folder")
    cmd = "./camcap.py caps=" + cappath
else:
    print("Saving to " + cappath)
    cmd = "./camcap.py"

while True:
    os.system(cmd)
    time.sleep(delay)
