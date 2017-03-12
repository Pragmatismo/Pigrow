#!/usr/bin/python
import os
import sys

import matplotlib.pyplot as plt

# import time #only used for line below
# time.sleep(30) #delay to give pi a chance to make the image before you
# download it

print("---Pigrow Timelapse Image Download and Graph Tool---")
print("   ----------------------------------------------")
print("      ----------------------------------------")
# user settings
# user_name = "pragmo" #can be used instead of the following
# hash this line out if it causes problem, autograbs username
user_name = str(os.getlogin())
target_address = "pi@192.168.1.6"
target_pass = "raspberry"
target_files = "/home/pi/Pigrow/caps/*.jpg"
cap_type = "jpg"
capsdir = "/home/" + user_name + "/frompigrow/caps/"

for argu in sys.argv[1:]:
    thearg = str(argu).split('=')[0]
    if thearg == 'to' or thearg == 'capsdir':
        capsdir = str(argu).split('=')[1]
    elif thearg == 'ta':
        target_address = str(argu).split('=')[1]
    elif thearg == 'tp':
        target_pass = str(argu).split('=')[1]
    elif thearg == 'tl':
        target_files = str(argu).split('=')[1]


if not os.path.exists(capsdir):
    os.makedirs(capsdir)
# end of user settings

print "Copying images to " + capsdir
# finding how many files there are to start with on the local computer
fcounter = 0
for filefound in os.listdir(capsdir):
    if filefound.endswith(cap_type):
        fcounter = fcounter + 1
print "Starting with; " + str(fcounter)

# Grabbing Files from pi
try:
    print("Copying files...   (this may time some time)")
    #os.system("rsync -a --password-file=pipass.txt --ignore-existing pi@192.168.1.12:/home/pi/cam_caps/*.txt ./")
    os.system(
        "rsync --ignore-existing -ratlz --rsh=\"/usr/bin/sshpass -p " +
        target_pass +
        " ssh -o StrictHostKeyChecking=no -l " +
        target_address +
        "\" " +
        target_address +
        ":" +
        target_files +
        " " +
        capsdir)
    print("Files Grabbed")
except OSError as err:
    print("OS error: {0}".format(err))
except Exception:
    print("Unexpected error:", sys.exc_info()[0])
    raise


# Making lists of the files on local computer we have now
facounter = 0
for filefound in os.listdir(capsdir):
    if filefound.endswith(cap_type):
        facounter = facounter + 1

# output info to the command line
print "Now got; " + str(facounter)
print "so that's " + str(facounter - fcounter) + " more than we had before"

# optionally updates the ububtu background with the most recent script.


def update_ubuntu_background():
    #import subprocess
    print("Updating background image with most recent file...")
    newstbk = capsdir + filelist[-1]
    print newstbk

    cmd = "sudo -u " + user_name + \
        " DISPLAY=:0 GSETTINGS_BACKEND=dconf gsettings set org.gnome.desktop.background picture-uri file://" + newstbk
    print cmd
    os.system(cmd)

# you can graph the downloaded caps using
#        /Pigrow/scripts/visualisation/caps_graph.py
#
# update_ubuntu_background() use the cron script instead it works better.
