#!/usr/bin/python
import os
import matplotlib.pyplot as plt
#import time #only used for line below
#time.sleep(30) #delay to give pi a chance to make the image before you download it

print("---Pigrow Timelapse Image Download and Graph Tool---")
print("   ----------------------------------------------")
print("      ----------------------------------------")
#user settings
#user_name = "pragmo" #can be used instead of the following
user_name = str(os.getlogin())  #hash this line out if it causes problem, autograbs username
target_address = "pi@192.168.1.10"
target_pass = "raspberry"
target_files = "/home/pi/Pigrow/caps/text_*.jpg"
cap_type = "jpg"

capsdir = "/home/"+user_name+"/frompigrow/caps/"
if not os.path.exists(capsdir):
    os.makedirs(capsdir)
#end of user settings

print "Copying images to "+capsdir
#finding how many files there are to start with on the local computer
fcounter = 0
for filefound in os.listdir(capsdir):
    if filefound.endswith(cap_type):
        fcounter = fcounter + 1
print "Starting with; " + str(fcounter)

#Grabbing Files from pi
try:
    print("Copying files...   (this may time some time)")
    #os.system("rsync -a --password-file=pipass.txt --ignore-existing pi@192.168.1.12:/home/pi/cam_caps/*.txt ./")
    os.system("rsync --ignore-existing -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass+" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_files+" "+capsdir)
    print("Files Grabbed")
except OSError as err:
    print("OS error: {0}".format(err))
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise


#Making lists of the files on local computer we have now
filelist = []
facounter = 0
fsize_log = []
facounter_log = []
datelist = []

for filefound in os.listdir(capsdir):
    if filefound.endswith(cap_type):
        facounter = facounter + 1

#output info to the command line
print "Now got; " + str(facounter)
print "so that's " + str(facounter - fcounter) + " more than we had before"
print "with a list of file sizes " + str(len(fsize_log)) + " long!"
print "and " + str(len(datelist)) + " dates taken from the filename's"

#optionally updates the ububtu background with the most recent script.
def update_ubuntu_background():
    #import subprocess
    print("Updating background image with most recent file...")
    newstbk = capsdir + filelist[-1]
    print newstbk

    cmd = "sudo -u "+user_name+" DISPLAY=:0 GSETTINGS_BACKEND=dconf gsettings set org.gnome.desktop.background picture-uri file://" + newstbk
    print cmd
    os.system(cmd)

#you can graph the downloaded caps using
#        /Pigrow/scripts/visualisation/caps_graph.py
#
#update_ubuntu_background() use the cron script instead it works better.
