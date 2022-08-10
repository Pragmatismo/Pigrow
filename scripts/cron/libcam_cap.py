#!/usr/bin/python3
import time
import os, sys


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
    return libcam_dic


def take_libcamera(libcam_dic, caps_path):
    # take and save photo
    timenow = str(time.time())[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    try:
        extra_commands = libcam_dic['extra_commands']
    except:
        extra_commands = ''
    if user_filename == None:
#        libcamera-still -t 5000 -o testn7.jpg --autofocus

        os.system("libcamera-still -t 5000 -o "+caps_path+filename+" --autofocus " + extra_commands)
        saved_filename = caps_path+filename
    else:
        os.system("libcamera-still -t 5000 -o " + user_filename + " --autofocus " + extra_commands)
        saved_filename = user_filename
    return saved_filename

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
    filename = take_libcamera(libcam_dic, caps_path)
    print("Saving image to:" + filename)
