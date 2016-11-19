#!/usr/bin/python
import os

###  Requires MPV to be installed, use - sudo apt install mpv

#user settings
time_jump = 1 #when making timelapse uses every Nth frame so 4 is 4x faster
darksize =75000   #all smaller files are removed assumed to be useless 75000 is a good value
outfps = 10       #10 is a good value, between 2 and 60 is acceptable
capsdir = "/home/pragmo/camcaps/"
listfile = "/home/pragmo/ffTL.txt"
outfile = "/home/pragmo/timelapse16.mkv" #directory to save output
#end of user settings

filelist = []
no_dark = []
faster = []
fcounter = 0

#grab all the files in /caps directory
for filefound in os.listdir(capsdir):
    if filefound.endswith("jpg"):
        fcounter = fcounter + 1
        filelist.append(filefound)
print "Starting with; " + str(fcounter)
filelist.sort()
print "Filelist is now:" + str(len(filelist))
#make list ignoring the small image assuming they're the datk ones
for x in filelist:
    statinfo = os.stat(capsdir + x)
    if statinfo.st_size >= darksize: #increase or decrese as needed, 75000 works well for most
        no_dark.append(x)
print("There are - " + str(len(no_dark)) + " entries in no_dark")
#make list every Nth file
for x in range(0, len(no_dark), time_jump):
    faster.append(no_dark[x])
#writes the file-list for mpv video encoder to use
os.chdir(capsdir)
ffTL = open(listfile, "w")
for x in faster: #can also be no_dark: or to include dark images change to filelist:
    ffTL.write(x + "\n")
ffTL.close()
print "we have " + str(len(faster)) + " files in the faster version..."
#runs the video encouder
print "making you a timelapse video..."
os.system("mpv mf://@"+listfile+" -mf-fps="+str(outfps)+" --ovc libx264 --ovcopts=bitrate=1200:threads=2 -o "+outfile)
if os.path.isfile(outfile) == True:
    print "there you go; "+outfile+" ready to roll.."
else:
    print "for some reason the file wasn't created, sorry..."
