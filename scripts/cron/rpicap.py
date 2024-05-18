#!/usr/bin/python3
import time
import os, sys


# default settings
max_disk_percent = 95 # only fill 90% of the disk
homedir = os.getenv("HOME")
settings_file = homedir + "/Pigrow/config/rpi_settings.txt" # default changed with argu settings
caps_path = None
user_filename = None

def display_picam_settings():
    print (" Display Settings has not been coded.")
    # --list-cameras


for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print(" Rpi cam capture script")
        print(" ")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        print(" filename=<file path>")
        print("     to set a spesific title, for testing without messing the caps folder")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("settings_file=" + homedir + "/Pigrow/config/rpi_settings.txt")
        print("caps_path=" + homedir + "/Pigrow/caps/")
        sys.exit(0)
    elif argu == "--settings" or argu == "-s":
        display_picam_settings()
    elif "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                if "/" in theval:
                    settings_file = theval
                else:
                    settings_file = homedir + "/Pigrow/config/" + theval
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

def load_picam_set(setloc):
    picam_dic = {}
    with open(setloc, "r") as f:
        for line in f:
            s_item = line.split("=")
            picam_dic[s_item[0]]=s_item[1].rstrip('\n')
    return picam_dic

def make_config_text(save_filename):
    picam_dic = load_picam_set(setloc=settings_file)
    conf_text = ""
    print("picam_dic;", picam_dic, " ----")

    # set image res for camera's main stream
    if "Resolution" in picam_dic:
        x_dim, y_dim = picam_dic["Resolution"].split("x")
        picam_dic["width"] = x_dim
        picam_dic["height"] = y_dim

    # set metadata flag
    # --metadata arg  Save captured image metadata to a file or "-" for stdout
    if "metadata" in picam_dic:
        if picam_dic["metadata"] == "each":
            picam_dic["metadata"] = os.path.splitext(save_filename)[0] + ".json"
        elif picam_dic["metadata"] == "off":
            picam_dic.pop("metadata", None)
        elif picam_dic["metadata"] == "$path":
            picam_dic["metadata"] = homedir + '/Pigrow/logs/cap_metadata.json'

    # check if raw is set
    if "raw" in picam_dic:
        if picam_dic["raw"] == "True":
            conf_text += " --raw"

    # remove script opts
    to_remove = ["Resolution", "cam_opt", "cam_num", "raw"]
    for item in to_remove:
        picam_dic.pop(item, None)


    for item in picam_dic.keys():
            if not picam_dic[item] == "":
                conf_text += " --" + item + " " + picam_dic[item]

    return conf_text


def take_rpi(caps_path):
    '''
     Take and save photo
    '''
    try:
        # set save path
        if user_filename == None:
            #get current time and set filename
            timenow = str(time.time())[0:10]
            filename= "cap_"+str(timenow)+".jpg"
            save_filename = caps_path+filename
        else:
            save_filename = user_filename

        # take photo
        conf_text = make_config_text(save_filename)
        cam_cmd = "rpicam-still --nopreview -o " + save_filename + conf_text
        print("cam_cmd:", cam_cmd)
        os.system(cam_cmd)

        print("Saving image to:", save_filename)
        return save_filename
    except:
        print("Sorry, picture not taken :(")
        raise

def set_caps_path(caps_path):
    # Select location to save images
    if caps_path == None:
        caps_path = homedir + '/Pigrow/caps/'
    else:
        if not caps_path[-1] == "/":
            caps_path = caps_path + "/"

    # if user has selected a caps path with a command line argument
    # check it exists, if not try making it, if can't then tell them and
    # resort to using local folder.
    if os.path.exists(caps_path):
        print("saving to; " + str(caps_path))
    else:
        try:
            os.mkdir(caps_path)
            print("created caps_path")
        except Exception as e:
            print("Couldn't create " + str(caps_path) + " using local folder instead.")
            caps_path = "./"

    return caps_path


## System checks
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
    #script = 'picam2cap.py'
    #import pigrow_defs
    caps_path = set_caps_path(caps_path)
    check_disk_percentage(caps_path)

    filename = take_rpi(caps_path)
