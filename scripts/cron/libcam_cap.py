#!/usr/bin/python3
import time
import os, sys

with open("/home/pi/piclog.txt", "a") as f:
    f.write("running at " + str(time.time()))

dangermode = False

# default settings
max_disk_percent = 95 # only fill 90% of the disk
homedir = os.getenv("HOME")
settings_file = homedir + "/Pigrow/config/libcam_settings.txt" # default changed with argu settings
caps_path = None
user_filename = None

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print(" llbcam capture script")
        print(" ")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        print(" filename=<file path>")
        print("     to set a spesific title, for testing without messing the caps folder")
        print(" ")
        sys.exit(0)
    elif argu == "-flags":
        print("settings_file=" + homedir + "/Pigrow/config/libcam_settings.txt")
        print("caps_path=" + homedir + "/Pigrow/caps/")
        sys.exit(0)
    elif "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                settings_file = theval
            elif thearg == 'caps_path' or thearg == 'caps':
                caps_path = theval
            elif thearg == 'filename':
                user_filename = theval
            #elif thearg == "attempts" or thearg == "tries":
            #    try:
            #        attempts = int(theval)
            #        print("Will try " + str(attempts) + " addional times before giving up")
            #    except:
            #        print("Attempts must be a number value, using defailt")
        except:
            print("Didn't undertand " + str(argu))

def load_libcam_set(setloc= homedir + "/Pigrow/config/libcam_settings.txt"):
    libcam_dic = {}
    with open(setloc, "r") as f:
        for line in f:
            s_item = line.split("=")
            libcam_dic[s_item[0]]=s_item[1].rstrip('\n')
    del libcam_dic["cam_opt"]
    return libcam_dic

def create_set_string(libcam_dic):
    # set resolution to usable form
    if "resolution" in libcam_dic:
        w,h = libcam_dic["resolution"].split("x")
        libcam_dic["width"] = w
        libcam_dic["height"] = h
        del libcam_dic["resolution"]
    elif not "width" in libcam_dic or not "height" in libcam_dic:
        libcam_dic["width"] = 0
        libcam_dic["height"] = 0

    # set camera choice
    cam_choice = libcam_dic["cam_num"]
    del libcam_dic["cam_num"]

    # remove any settings that aren't in the white list
    if dangermode == False:
        new_dict = {}
        whitelist = ["width", "height", "brightness", "contrast",
                     "saturation", "sharpness", "awb", "roi",
                     "gain", "shutter", "rotation", "vflip", "hflip",
                     "metering", "exposure", "ev", "denoise", "encoding", "quality" ]
        for item in libcam_dic:
            if item in whitelist:
                new_dict[item] = libcam_dic[item]
        libcam_dic = new_dict


    # create text string
    extra_cmds = ""
    for item in libcam_dic:
        print(item)
        extra_cmds += " --" + item + ' "' + libcam_dic[item] + '"'
        print (extra_cmds)
    libcam_dic["extra_commands"] = extra_cmds
    print (extra_cmds)
    return libcam_dic



def take_libcamera(libcam_dic, caps_path):
    ## take and save photo
    # create filename
    timenow = str(time.time())[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    # get config setting string
    try:
        extra_commands = libcam_dic['extra_commands']
    except:
        extra_commands = ''
    # set filename
    if user_filename == None:
        save_filename = caps_path+filename
    else:
        save_filename = user_filename
    # create and run command
    cmd = '/usr/local/bin/libcamera-still -t 5000 -o ' +save_filename+ ' --autofocus ' + extra_commands
    print (cmd)
    os.system(cmd)
    # return filename of saved file
    return save_filename

def set_caps_path(loc_dic, caps_path):
    # Select location to save images
    if caps_path == None:
        #check for caps path in the loctions dictionary (of dirlocs.txt)
        try:
            caps_path = loc_dic['caps_path']
        #if not then see if the default exists
        except:
            caps_path = homedir + '/Pigrow/caps/'
            if os.path.exists(caps_path):
                print("Using default folder; " + str(caps_path))
            else:
                # if not then try to create it
                try:
                    os.mkdir(caps_path)
                    print("created default folder at " + str(caps_path))
                except Exception as e:
                    # if nothing works try using the local folder instead
                    print("Couldn't create default folder at " + str(caps_path) + " resorting to local folder instead.")
                    caps_path = ""
    else:
        # i.e. if user has selected a caps path with a command line argument
        # check it exists, if no try making it if not then tell them and
        # resort to using local folder.
        if os.path.exists(caps_path):
            print("saving to; " + str(caps_path))
        else:
            try:
                os.mkdir(caps_path)
                print("created caps_path")
            except Exception as e:
                print("Couldn't create " + str(caps_path) + " using local folder instead.")
                caps_path = ""
    return caps_path


#
# System checks
#

def check_disk_percentage(caps_path):
    st = os.statvfs(caps_path)
    #free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    print("   Used " + str(percent) + "%, max limit " + str(max_disk_percent) + "%")
    if percent > max_disk_percent:
        print(" - You do not have enough space on the drive to store more images, cancelling attempt.")
        sys.exit()

if __name__ == '__main__':
    sys.path.append(homedir + '/Pigrow/scripts/')
    script = 'libcam_cap.py'
    import pigrow_defs
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    caps_path = set_caps_path(loc_dic, caps_path)
    check_disk_percentage(caps_path)
    libcam_dic = load_libcam_set(setloc=settings_file)
    libcam_dic = create_set_string(libcam_dic)
    filename = take_libcamera(libcam_dic, caps_path)
    print("Saving image to:" + filename)
