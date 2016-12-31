#!/usr/bin/python
import os
import sys

###  Requires MPV to be installed, use - sudo apt install mpv

#default user settings
time_skip = 1 #when making timelapse uses every Nth frame so 4 is 4x faster
darksize =50000   #all smaller files are removed assumed to be useless 50-75000 is a good value
infps = 10       #10 is a good value, between 2 and 60 is acceptable
outfps = 25      #frame-rate of output video
capsdir = "./"

outfile = "./timelapse.mp4" #directory to save output
file_type = "jpg"

already_existing = 'ask'

outvidc = "libx264"  #DISABLED
inpoint=0
outpoint=0 #use -10 to end at ten befor the end, 0 to show the whole thing and 10 to shopw only ten frames
#end of user settings

for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    try:
        theset = str(argu).split('=')[1]
    except:
        pass
    if  thearg == 'caps':
        capsdir = theset
    elif thearg == "of":
        outfile = theset
    elif thearg == "fps":
        infps = theset
    elif thearg == "ofps":
        outfps = theset
    elif thearg == "darksize" or thearg == 'ds':
        darksize = int(theset)
    elif thearg == "ts" or thearg == 'timeskip':
        time_skip = int(theset)
    elif thearg == "ft" or thearg == 'filetype':
        file_type = theset
    elif thearg == "ovc" or thearg == 'outvidc':
        outvidc = theset
    elif thearg == "inp" or thearg == 'inpoint':
        inpoint = int(theset)
    elif thearg == "op" or thearg == 'outpoint':
        outpoint = int(theset)
    elif thearg == "overwrite" or thearg == 'ow':
        if theset == 'ask':
            already_existing = 'ask'
        elif theset == 'r' or theset == 'overwrite' or theset == 'replace':
            already_existing = 'r'
        elif theset == 'e' or theset == 'extend':
            already_existing = 'e'
        elif theset == 'n' or theset == 'prompt for new name':
            already_existing = 'n'
        else:
            print("  !! Can't understand overwrite flag, ignoring")

### HELP TEXT

    elif thearg == "-h" or thearg == '--help':
        print(" Pigrow Timelapse maker thingy")
        print("")

        print("   caps=DIR         ")
        print("        folder to turn into a movie")

        print("   of=FILENAME")
        print("        location and name of outfile")

        print("   fps=NUMBER")
        print("         how long to show each photo in frames per second")

        print("   ofps=NUMBER")
        print("         frames per second of the out file, same as fps works well")

        print("   ds=SIZE")
        print("         SIZE in bites below which files are ignored")

        print("   ts=NUMBER")
        print("         uses every Nth frame")

        print("   ft=JPG/PNG/etc")
        print("         file type of images to look for, default jpg")

        #print(" ---   DISABLED  --- ovc=CODEC        -codec to use for video, normally defined by file type")

        print("   inp=NUMBER")
        print("          Starts at the Nth file, can use -N to count backwards from the end")

        print("   op=NUMBER")
        print("          Ends at the Nth file, can use -N to count backwards from the end.")

        print("   ow=ask")
        print("            =r - overwrite and replace.")
        print("            =e - automatically extend filename")
        print("          What to do in the event outfile exists already")

        print("   -h   ")
        print("            This menus (obviously)")
        print("")
        print("   Add arguments in any order, no spaces anywhere in them exceot to seperate them please.")
        print("")
        print(" Example command;")
        print("    ./timelapse_assemble.py of=wibble.gif fps=10 ds=1 inp=15 op=212")
        print("")
        print("             For more information visit www.reddit.com/r/pigrow")
        exit()


listfile = capsdir + "filelist.txt"

print(" ## ############################################ ##")

def grab_folder(capsdir='./', inpoint=0, outpoint=0, file_type='jpg'):
    #grab all the files in caps directory
    filelist = []
    fcounter = 0
    if outpoint == 0:
        outpoint = len(os.listdir(capsdir))
    for filefound in os.listdir(capsdir):
        if filefound.endswith(file_type):
            fcounter = fcounter + 1
            filelist.append(filefound)
    print " ##  Counted total; " + str(fcounter)
    filelist.sort()
    print " ##  Using: " + str(len(filelist[inpoint:outpoint]))
    return filelist[inpoint:outpoint]

def discard_dark(filelist):
    # make list ignoring the small images
    # because they're either broken or datk.
    no_dark = []
    for x in filelist:
        statinfo = os.stat(capsdir + x)
        if statinfo.st_size >= darksize: #increase or decrese as needed, 75000 works well for most
            no_dark.append(x)
    print(" ## After removing dark; " + str(len(no_dark)) + " using " +str(darksize)+" threashold")
    return no_dark

def skip_every(no_dark, time_skip=0):
    faster = []
    #make list every Nth file
    for x in range(0, len(no_dark), time_skip):
        faster.append(no_dark[x])
    print(" ##  After timeskip left with; " + str(len(faster)))
    return faster

def write_listfile(final_list, capsdir):
    #writes the file-list for mpv video encoder to use
    os.chdir(capsdir)
    ffTL = open(listfile, "w")
    for x in final_list:
        ffTL.write(x + "\n")
    ffTL.close()
    print(" ##     -filelist written")


def next_filename(outfile):
    num = 0
    end = str(outfile.split(".")[1])
    outfile_possible = str(outfile)
    while os.path.isfile(outfile_possible) == True:
        num = num + 1
        outfile_possible = outfile_possible.split(".")

        outfile_possible = str(outfile.split(".")[0]) + "_"+str(num)+"_." + end

        #outfile_possible = str(outfile_possible)
        print num, outfile, outfile_possible
    outfile = outfile.split(".")
    outfile[0] = str(outfile[0]) + "_"+str(num)+"_"
    outfile = outfile[0] + "." + end
    print("filename is now, " + outfile)
    return outfile

def check_already_outfile(outfile):
    #checks if file exits, asks what to do.
    if os.path.isfile(outfile) == True and already_existing == 'ask':
        print(" ##  File "+str(outfile)+" already exists")
        print(" ##    r - overwrite and replace.")
        print(" ##    e - automatically extend filename")
        print(" ##    n - pick a new filename")
        print(" ##      - anything else to exit")
        overwrite = raw_input("Choose option;")
        if overwrite == 'r':
            print("Replacing file")
        elif overwrite == 'e':
            outfile = next_filename(outfile)
        elif overwrite == 'n':
            outfile = raw_input("Choose name for outfile, include extention; ")
            outfile = check_already_outfile(outfile)
        else:
           print("Exiting")
           exit()
    elif already_existing == 'r':
        return outfile
    elif already_existing == 'e':
        print(" ##  automatically updating filename")
        outfile = next_filename(outfile)
    return outfile




outfile = check_already_outfile(outfile)
filelist = grab_folder(capsdir, inpoint, outpoint, file_type)
no_dark = discard_dark(filelist)
faster = skip_every(no_dark, time_skip)
write_listfile(faster, capsdir)


#runs the video encouder
print " ##  making you a timelapse video..."
os.system("mpv mf://@"+listfile+" -mf-fps="+str(infps)+" -o "+outfile+" --ofps="+str(outfps))

try:
    os.remove(listfile)
    print(" ##     -filelist removed")
except:
    print(" !!     -filelist not removed")

if os.path.isfile(outfile) == True:
    print " ## there you go; "+outfile+" ready to roll.."
else:
    print " !! for some reason the file wasn't created, sorry..."
