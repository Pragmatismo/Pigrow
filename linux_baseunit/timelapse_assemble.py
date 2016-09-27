#!/usr/bin/python
import os
#user settnigs
time_jump = 1 #when making timelapse uses every Nth frame so 4 is 4x faster
outfile = "/timelapse/timelapse.mkv" #directory to save output to default "/timelapse/timelapse.mkv" -this is a relative path starting one directiory above /caps
#          /../timelapse/outfile.mkv #would put the files in a directory called timelapse beside the one the script was run from
#   to use absolute directories to position the outfile alter line 41 removing the .. before "+outfile
#end of user settings

filelist = []
no_dark = []
faster = []
fcounter = 0

#grab all the files in /caps directory
for filefound in os.listdir("./caps/"):
    if filefound.endswith("jpg"):
        fcounter = fcounter + 1
        filelist.append(filefound)
print "Starting with; " + str(fcounter)
filelist.sort()
print "Filelist is now:" + str(len(filelist))
#make list ignoring the small image assuming they're the datk ones
for x in filelist:
    statinfo = os.stat("./caps/" + x)
    if statinfo.st_size >= 75000: #increase or decrese as needed, 75000 works well for most
        no_dark.append(x)
print("There are - " + str(len(no_dark)) + " entries in no_dark")
#make list every Nth file
for x in range(0, len(no_dark), time_jump):
    faster.append(no_dark[x])
#writes the file-list for mpv video encoder to use
os.chdir("./caps/")
ffTL = open("./ffTL.txt", "w")
for x in faster: #can also be no_dark: or to include dark images change to filelist:
    ffTL.write(x + "\n")
ffTL.close()
print "we have " + str(len(faster)) + " files in the faster version..."
#runs the video encouder
print "making you a timelapse video..."
os.system("mpv mf://@./ffTL.txt -mf-fps=10 --ovc libx264 --ovcopts=bitrate=1200:threads=2 -o .."+outfile)
print "there you go; ."+outfile+" ready to roll.."
