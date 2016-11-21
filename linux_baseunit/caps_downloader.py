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
capsdir = "/home/"+user_name+"/camcaps/"
print "Copying images to "+capsdir

target_address = "pi@192.168.1.2"
target_pass = "raspberry"
target_files = "/home/pi/cam_caps/text_*.jpg"

graph_dir = "/home/"+user_name+"/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/"
#end of user settings


#finding how many files there are to start with on the local computer
fcounter = 0
for filefound in os.listdir(capsdir):
    if filefound.endswith("jpg"):
        fcounter = fcounter + 1
print "Starting with; " + str(fcounter)

#Grabbing Files from pi
try:
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
    if filefound.endswith("jpg"):
        filelist.append(filefound)
filelist.sort()

for thefile in filelist:
    datelist.append(int(str(thefile).split(".")[0].split('_')[2]))
    thefile = os.stat(capsdir + thefile)
    fsize = thefile.st_size
    facounter = facounter + 1
    fsize_log.append(fsize)
    facounter_log.append(facounter)

#output info to the command line
print "Now got; " + str(facounter)
print "so that's " + str(facounter - fcounter) + " more than we had before"
print "with a list of file sizes " + str(len(fsize_log)) + " long!"
print "and " + str(len(datelist)) + " dates taken from the filename's"


#optional file size of captured image graph
#images taken in darkness have a significantly lower filesize than full images
def file_size_graph():
    plt.figure(1)
    ax = plt.subplot()
    #ax.plot(facounter_log, fsize_log, color='darkblue', lw=3)
    ax.bar(facounter_log, fsize_log, width=0.1, color='green')
    plt.title("filesize")
    plt.ylabel("filesize")
    plt.xlabel("file number")
    #plt.show() #hash this line out to stop it shoinw the plot, unhash tp show plot
    plt.savefig (graph_dir+"file_size_graph.png") #will be blank if plt.show is active
    print("Graph saved to"+graph_dir+" file_size_graph.png")


#optional time difference between captured image graph
pic_dif_log = []
def image_time_diff_graph():
    global pic_dif_log
    print("Gathering data for time diff graph")
    for x in range(1, len(datelist)):
        cur_pic = datelist[x]
        las_pic = datelist[x-1]
        pic_dif = cur_pic - las_pic
        pic_dif_log.append(pic_dif)
    print('We now have ' + str(len(pic_dif_log)) + ' up time differnces from the pictures to work with.')
    print('most recent date: ' + str(datelist[-1]))
    plt.figure(2)
    ax = plt.subplot()
    #ax.plot(facounter_log, fsize_log, color='darkblue', lw=3)
    ax.bar(facounter_log[1:], pic_dif_log, width=0.1, color='green')
    plt.title("Time Diff Between Images")
    plt.ylabel("seconds between images")
    plt.xlabel("file number")
    #plt.show() #hash this line out to stop it shoinw the plot, unhash to show plot
    plt.savefig (graph_dir+"file_time_diff_graph.png") #will be blank if plt.show is active
    print("Graph saved to "+graph_dir+"file_time_diff_graph.png")

#optionally updates the ububtu background with the most recent script.
def update_ubuntu_background():
    #import subprocess
    print("Updating background image with most recent file...")
    newstbk = capsdir + filelist[-1]
    print newstbk

    cmd = "sudo -u "+user_name+" DISPLAY=:0 GSETTINGS_BACKEND=dconf gsettings set org.gnome.desktop.background picture-uri file://" + newstbk
    print cmd
    os.system(cmd)

#but a hash [#] before the following to stop them happening;
image_time_diff_graph()
file_size_graph()
#update_ubuntu_background() use the cron script instead it works better.
