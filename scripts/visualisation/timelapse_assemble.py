#!/usr/bin/env python3
import os
import sys
import datetime
###  Requires MPV to be installed, use - sudo apt install mpv
homedir = os.getenv("HOME")
try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'timelapse_assemble.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    capsdir = loc_dic['caps_path']
    resources_path = loc_dic['path'] + "/resources/"
except:
    print("Pigrow config not detected, using defaults")
    capsdir = "./"
    resources_path = "../../resources/"

#default user settings
audio_file = ""
time_skip = 1 #when making timelapse uses every Nth frame so 4 is 4x faster
darksize =50000   #all smaller files are removed assumed to be useless 30-75000 is a good value
infps = 10       #10 is a good value, between 2 and 60 is acceptable
outfps = 25      #frame-rate of output video
outfile = "./timelapse.mp4" #directory to save output
file_type = "jpg"
already_existing = 'ask'
extra_commands = ''
#outvidc = "libx264"  #DISABLED
inpoint=0
outpoint=0 #use -10 to end at ten befor the end, 0 to show the whole thing and 10 to shopw only ten frames
#end of user settings
datecheck = False
video_credits=30

for argu in sys.argv:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theset = str(argu).split('=')[1]
        if  thearg == 'caps':
            capsdir = theset
        elif thearg == "of":
            outfile = theset
        elif thearg == "fps":
            infps = theset
        elif thearg == "ofps":
            outfps = theset
        elif thearg == "extra":
            extra_commands = (argu)[7:]
        elif thearg == "darksize" or thearg == 'ds':
            darksize = int(theset)
        elif thearg == "datecheck" or thearg == 'dc':
            if not theset.lower() == "false":
                datecheck = theset
            else:
                datecheck=False
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
        elif thearg == 'video_credits' or thearg == 'credits':
            video_credits = int(theset)
        elif thearg == 'audio_file' or thearg == 'audio':
            audio_file = theset
   ### HELP TEXT
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
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
        print("   extra=CMD")
        print("         additional commands for MVP, eg; --of=mpjpeg ")
        print("                                          --vf=scale=480:270 ")
        print("                                          --vf=format=rgb24")
        print("                               --vf=format=rgb24,scale=160:120")
        print("   ds=SIZE")
        print("         SIZE in bites below which files are ignored")
        print("   dc=hour1  -- or day1, week1, month1")
        print("         datecheck's images before loading them")
        print("           hour1 shows last hour, hour5 last five hours, etc.")
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
        print("   credits=NUMBER")
        print("          number of extra frames to add as an end-buffer")
        print("   audio=PATH")
        print("          location of the audio file to use as a sound track")
        print("   -h   ")
        print("            This menus (obviously)")
        print("")
        print("   Add arguments in any order, no spaces anywhere in them exceot to seperate them please.")
        print("")
        print(" Example command;")
        print("    ./timelapse_assemble.py of=wibble.gif fps=10 ds=1 inp=15 op=212")
        print("")
        print("             For more information visit www.reddit.com/r/pigrow")
        sys.exit()
    elif argu == '-flags':
        print("-help=no flags information, view -help instead")
        sys.exit()


listfile = capsdir + "filelist.txt"

print(" ## ############################################ ##")

def grab_folder(capsdir='./', inpoint=0, outpoint=0, file_type='jpg', datecheck=False):
    #grab all the files in caps directory
    if not datecheck == False:
        if datecheck[0:3] == "day":
            days = int(datecheck[3:])
            datecheck=datetime.timedelta(days=days)
            datecheck=datetime.datetime.now() - datecheck
        elif datecheck[0:4] == "hour":
            hours = int(datecheck[4:])
            datecheck=datetime.timedelta(hours=hours)
            datecheck=datetime.datetime.now() - datecheck
        elif datecheck[0:4] == "week":
            weeks = int(datecheck[4:])
            datecheck=datetime.timedelta(weeks=weeks)
            datecheck=datetime.datetime.now() - datecheck
        elif datecheck[0:5] == "month":
            months = int(datecheck[5:])*4
            datecheck=datetime.timedelta(weeks=months)
            datecheck=datetime.datetime.now() - datecheck
        else:
            print(" !!!! couldn't understand datecheck flag, ignoring")
            datecheck = False
    filelist = []
    fcounter = 0
    if outpoint == 0:
        outpoint = len(os.listdir(capsdir))
    for filefound in os.listdir(capsdir):
        if filefound.endswith(file_type):
            fcounter = fcounter + 1
            if not datecheck == False:
                picdate = float(filefound.split(".")[0].split("_")[-1])
                picdate = datetime.datetime.utcfromtimestamp(picdate)
                if picdate >= datecheck:
                    filelist.append(filefound)
            elif datecheck == False:
                filelist.append(filefound)

    print (" ##  Counted total; " + str(fcounter))
    filelist.sort()
    print (" ##  Active timezone contains : " + str(len(filelist[inpoint:outpoint])))
    if len(filelist) >= 1:
        try:
            print(" ##     -Starting  " + str(datetime.datetime.utcfromtimestamp(float(filelist[0].split(".")[0].split("_")[-1]))))
            print(" ##     -Finishing " + str(datetime.datetime.utcfromtimestamp(float(filelist[-1].split(".")[0].split("_")[-1]))))
        except:
            try:
                print(" ##     -Finishing " + str(datetime.datetime.utcfromtimestamp(float(filelist[-1].split(".")[0].split("_")[-1]))))
            except:
                print(" ...messy caps folder,,,")
    else:
        print(" !!!! No files to make timelapse with...")
        exit()
    return filelist[inpoint:outpoint]


def discard_dark(filelist):
    # make list ignoring the small images
    # because they're either broken or datk.
    no_dark = []
    for x in filelist:
        statinfo = os.stat(capsdir + x)
        if statinfo.st_size >= darksize: #increase or decrese as needed, 75000 works well for most
            no_dark.append(x)
    print(" ##  After removing dark; " + str(len(no_dark)) + " remain    (using " +str(darksize)+" byte threashold)")
    return no_dark

def skip_every(image_list, time_skip=0):
    faster = []
    #make list every Nth file
    for x in range(0, len(image_list), time_skip):
        faster.append(image_list[x])
    print(" ##  Timeskip using every " + str(time_skip) + " frame, leaves us with; " + str(len(faster)))
    return faster

def create_credits_images(image_list, capsdir):
  #Settings which will oneday be settings
    credits_background_colour = "black"
    output_path = capsdir + "credits." + file_type

    persist_last_frame = True
    t_red = 180    #0-255 text colour
    t_green= 240   #0-255 text colour
    t_blue = 180   #0-255 text colour
    t_alpha = 200 #0-255 text opacity
    font_name = resources_path + 'Caslon.ttf'
    font_size = 45
    leftdist = 40 # percentage left of image to start text
    downdist = 96 # [ercentage down the image to start test]

  #test if it needs to be done
    if video_credits == 0:
        print("skipping making video credits")
        return image_list
    print("Crating video credits")
  #make the images
    try:
        from PIL import Image, ImageDraw, ImageFont
    except:
        print("loading PIL - Python Image Library failed")
        print("  - to enable video credits install PIL ")
        ##NEED TO ADD -- hold_final_frame = video_credits  #instead of credits persist final frame
        return image_list
    last_pic = capsdir + image_list[-1]
    image_for_size = Image.open(last_pic)
    # print (image_for_size.size)
    if persist_last_frame == True:
        base = image_for_size
    else:
        base = Image.new("RGBA", image_for_size.size, credits_background_colour)
 #this is where i need to add the code for writing stuff
    #txt = Image.new('RGBA', base.size, (255,255,255,0))
    fnt = ImageFont.truetype(font_name, font_size)
    d = ImageDraw.Draw(base)
    xpos = base.size[0] / 100 * leftdist
    ypos = base.size[1] / 100 * downdist
    d.text((xpos+2, ypos), "Created using a Pigrow", font=fnt, fill=(t_red,t_green,t_blue,t_alpha))

 #Save the cedits file and add to the file list
    base.save(output_path)
    print("File saved to " + str(output_path))
    for x in range(0, video_credits):
        image_list.append(output_path)
    print("-- Added " + str(video_credits) + " frames of credits at the end")
    return image_list


def write_listfile(final_list, capsdir):
    #writes the file-list for mpv video encoder to use
    os.chdir(capsdir)
    ffTL = open(listfile, "w")
    for x in final_list:
        ffTL.write(x + "\n")
    ffTL.close()
    print(" ##             -filelist written")


def next_filename(outfile):
    num = 0
    end = str(outfile.split(".")[1])
    outfile_possible = str(outfile)
    while os.path.isfile(outfile_possible) == True:
        num = num + 1
        outfile_possible = outfile_possible.split(".")

        outfile_possible = str(outfile.split(".")[0]) + "_"+str(num)+"_." + end

        #outfile_possible = str(outfile_possible)
        print (num, outfile, outfile_possible)
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
filelist = grab_folder(capsdir, inpoint, outpoint, file_type, datecheck)
no_dark = discard_dark(filelist)
faster = skip_every(no_dark, time_skip)
if len(faster) >= 1:
    print(" ##  Creating list file...")
    create_credits_images(faster, capsdir)
    write_listfile(faster, capsdir)
else:
    print(" !!  There are no files to make a timelapse from...")
    exit()

#runs the video encouder
print (" ##  making you a timelapse video...")
cmd = "mpv mf://@"+listfile+" -mf-fps="+str(infps)
if not audio_file == '':
    cmd += " --audiofile="+audio_file+" --frames=" + str(len(faster)+video_credits)
cmd += " -o "+outfile+" --ofps="+str(outfps)+" " + extra_commands
os.system(cmd)

try:
    os.remove(listfile)
    print(" ##     -filelist removed")
    os.remove((capsdir + "credits.jpg"))
except:
    print(" !!     -filelist not removed")

if os.path.isfile(outfile) == True:
    print (" ## there you go; "+outfile+" ready to roll..")
else:
    print (" !! for some reason the file wasn't created, sorry...")
