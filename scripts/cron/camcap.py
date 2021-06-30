#!/usr/bin/python3
import time
import os
import sys
#
# setting defaults and blank variables
#
homedir = os.getenv("HOME") #discovers home directory location use in default path generation
#Setting Blank Variables
cam_opt = "uvccapture" # here in case it doesn't get set later.
settings_file = None # this will get turned into a string containing the settings file path
caps_path = None     # this likewise gets turned into a string containing the output path
                     # both start as None and if they aren't set by command line arguments
                     # the program tries to locate or guess what they should be
loc_dic = {}         # the blank location dictionary which contains settings file into and etc
attempts = 3         # number of extra attempts if image fails 0-999
retry_delay = 2      #time in seconds to wait before trying to take another image when failed
log_error = True     # set to False if you don't want to note failure in the error log.
max_disk_percent = 95 # only fill 90% of the disk

#
# Handle command line arguments
#
for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Pigrow Image Capture Script")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        print(" attempts=3")
        print("     amount of tries before giving up")
        sys.exit(0)
    elif argu == '-flags':
        print("settings_file=" + homedir + "/Pigrow/config/camera_settings.txt")
        print("caps_path=" + homedir + "/Pigrow/caps/")
        print("attempts=3")
        sys.exit()
    if "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                settings_file = theval
            elif thearg == 'caps_path' or thearg == 'caps':
                caps_path = theval
            elif thearg == "attempts" or thearg == "tries":
                try:
                    attempts = int(theval)
                    print("Will try " + str(attempts) + " addional times before giving up")
                except:
                    print("Attempts must be a number value, using defailt")
        except:
            print("Didn't undertand " + str(argu))
#
# Set locations and load settings
#
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

def new_load_camera_settings(settings_file):
    sets_dict = {}
    if not settings_file == None:
        with open(settings_file, "r") as f:
            for line in f:
                if "=" in line:
                    e_pos = line.find("=")
                    key = line[:e_pos].strip()
                    val = line[e_pos+1:].strip()
                    sets_dict[key] = val
    return sets_dict

def load_camera_settings(settings_file):
    s_val = ''
    c_val = ''
    g_val = ''
    b_val = ''
    x_dim = '100000'  #arbitary big number or it defaults to nothing
    y_dim = '100000'  #this just takes the largest possible image
    cam_num = ''
    cam_opt = ''
    fsw_extra = ''
    uvc_extra = ''
    #Grabbing all the relevent data from the settings file
    if not settings_file == None:
        try: #this is a try because corrupt or weird config files might crash it out
            with open(settings_file, "r") as f:
                for line in f:
                    #for every line in the setting file see if it's any of these
                    #settings and if so assign the value, if something is not set at all then it
                    #remains at the default or blank value over all passes (i.e. none of the lines contain it)
                    #then it gets delivered as a default beside any set values, this makes sure
                    #that all values are set with something that will parse for all camera tools.
                    s_item = line.split("=")
                    key = s_item[0].strip()
                    val = s_item[1].strip()
                    if key == "s_val":
                        s_val = val
                    elif key == "c_val":
                        c_val = val
                    elif key == "g_val":
                        g_val = val
                    elif key == "b_val":
                        b_val = val
                    elif key == "x_dim":
                        x_dim = val
                    elif key == "y_dim":
                        y_dim = val
                    elif key == "resolution":
                        if "x" in val:
                            x_dim, y_dim = val.split("x")
                    elif key == "cam_num":
                        cam_num = val
                    elif key == "cam_opt":
                            cam_opt = val
                    elif key == "fsw_extra":
                        try:
                            fsw_extra = ''                  ##
                            for cmdv in s_item[1:]:         ##
                                if not cmdv == '':          ##  this just puts it
                                    fsw_extra += cmdv + "=" ##  back together again
                            fsw_extra = fsw_extra[:-1]      ##
                        except:
                            print("couldn't read fsw extra commands, trying without...")
                            fsw_extra = ''
                    elif key == "uvc_extra":
                        uvc_extra = val
        except Exception as e:
            print (e)
            print("looked at " + settings_file)
            print("but couldn't load config data for camera, resorting to default values")
            print("  - Use the remote gui to create a new config file")
            print("  or Run cam_config.py to create a new config file")
            print("  or make sure you're pointing to the correct file in dirlocs.")
        # check to ensure a valid option is set, if not selects default
        if not cam_opt == 'fswebcam' and not cam_opt == 'uvccapture':
            print("setting cam opt to uvccapture as unspecified")
            cam_opt = 'uvccapture'
    return (s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra)
#
# take and save photo
#
def take_with_uvccapture(s_val="", c_val="", g_val="", b_val="", x_dim=100000, y_dim=100000, cam_num='/dev/video0', uvc_extra="", caps_path=""):
    #determine time stamped name
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    #write command string for taking a photo with uvc
    cmd = "uvccapture"
    if not cam_num == "":
        cmd  += " -d" + cam_num
    if not s_val == "":
        cmd += " -S" + s_val #saturation
    if not c_val == "":
        cmd += " -C" + c_val #contrast
    if not g_val == "":
        cmd += " -G" + g_val #gain
    if not b_val == "":
        cmd += " -B" + b_val #brightness
    if not x_dim == "":
        cmd += " -x" + str(x_dim)
    if not y_dim == "":
        cmd += " -y" + str(y_dim)
    cmd += " " + uvc_extra.strip()
    cmd += " -v -t0" #-v verbose, -t0 take single shot
    cmd += " -o" + caps_path + filename
    # show the command line user what command you're running
    print("----")
    print(cmd)
    print("----")
    #run the command
    os.system(cmd)
    # tell the user we're back in controll of the computer after uvc finishes
    print("Capture Finished, Image path : "+caps_path+filename)
    #hand back the filename so we can check was created or pass it on for editing
    #or other mantipulation when this is being run from other scripts as a module
    return filename


def fs_sets_trim(sets_dict):
    # Add settings from fs_extra
    if 'fsw_extra' in sets_dict:
        extra = sets_dict['fsw_extra']
        if '--set' in extra:
            print(" - Adding fs_extra settings to sets dict")
            extra_sets = sets_dict['fsw_extra'].split('--set')
            for item in extra_sets:
                if "=" in item:
                    key, val = item.split("=")
                    sets_dict[key] = val
    # remove unused opts
    to_remove = ['uvc_extra', 'fsw_extra', 'cam_opt']
    for key in to_remove:
        if key in sets_dict:
            del sets_dict[key]
    # add defaults
    if not 'resolution' in sets_dict:
        if 'x_dim' in sets_dict and 'y_dim' in sets_dict:
            sets_dict['resolution'] = sets_dict['x_dim'] + "x" + sets_dict['y_dim']
        else:
            print(" Resolution not set, using default 1920x1080")
            sets_dict['resolution'] = '1920x1080'
    if not 'fs_delay' in sets_dict:
        sets_dict['fs_delay'] = '2'
    if not 'fs_fskip' in sets_dict:
        sets_dict['fs_fskip'] = '5'
    if not 'fs_jpg_q' in sets_dict:
        sets_dict['fs_jpg_q'] = '90'
    # add legacy
    if "s_val" in sets_dict:
        if not 'saturation' in sets_dict:
            sets_dict['saturation'] = sets_dict['s_val']
    if "c_val" in sets_dict:
        if not 'contrast' in sets_dict:
            sets_dict['contrast'] = sets_dict['c_val']
    if "g_val" in sets_dict:
        if not 'gain' in sets_dict:
            sets_dict['gain'] = sets_dict['g_val']
    if "b_val" in sets_dict:
        if not 'brightness' in sets_dict:
            sets_dict['brightness'] = sets_dict['b_val']
    #
    return sets_dict

def new_take_with_fswebcam(sets_dict, caps_path=""):
    sets_dict = fs_sets_trim(sets_dict)
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    # Set the  command string for fswebcam
    cam_cmd  = "fswebcam -r " + sets_dict['resolution']
    cam_cmd += " -d v4l2:" + sets_dict['cam_num']
    cam_cmd += " -D " + sets_dict['fs_delay']     # the delay in seconds before taking photo
    cam_cmd += " -S " + sets_dict['fs_fskip']     # number of frames to skip before taking image
    ignore_list = ['resolution', 'cam_num', 'fs_delay', 'fs_fskip']
    for key, val in sets_dict.items():
        if not key in ignore_list:
            cam_cmd += ' --set "' + key + '"="' + val + '"'
    cam_cmd += " --jpeg " + sets_dict['fs_jpg_q'] # jpeg quality
    cam_cmd += " " + caps_path + filename  #output filename
    # Take picture
    os.system(cam_cmd)
    print("Capture Finished, Saving image to:" + caps_path + filename)
    #
    return filename

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

#
#
# main program which runs unless we've imported this as a module via another script
if __name__ == '__main__':
    #when running as a script import pigrow_defs and find file path info
    sys.path.append(homedir + '/Pigrow/scripts/')
    try:
        import pigrow_defs
        script = 'camcap.py'  #used with logging module
        loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
        loc_dic = pigrow_defs.load_locs(loc_locs)
    except:
        print("Pigrow localisation module failed to initalize, unable to load settings")

    #load setting from settings file
    if settings_file == None:
        if "camera_settings" in loc_dic:
            settings_file = loc_dic['camera_settings']
            print("loading settings from settings file referenced in dirlocs ")
            s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, = load_camera_settings(settings_file)
        else:
            #if dirlocs doesn't contain settings file info for the camera
            print("Settings file not found, using default values instead")
            s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, = "", "", "", "", "100000", "100000", "", "uvccapture", "", ""
    else:
        #i.e. if the user spesified their own settigns file at the command line
        print("Loading settings from file " + str(settings_file))
        s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, = load_camera_settings(settings_file)

    # set the destination path for photos
    caps_path = set_caps_path(loc_dic, caps_path)
    check_disk_percentage(caps_path)
    #Taking the photo with the selected camera program
    #first attempt
    if cam_opt == "uvccapture":
        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
    elif cam_opt ==  "fswebcam":
        settings_dict = new_load_camera_settings(settings_file)
        filename = new_take_with_fswebcam(settings_dict, caps_path)
    else:
        print("unknown capture option -" + str(cam_opt) + "- sorry")
    # testing if file was made
    if os.path.isfile(caps_path + filename):
        print("Done!")
        sys.exit()
    else:
        #if the file doesn't exist check if we should try again and if so try again
        print("Error: Image file not found")
        # If trying more than once
        if attempts > 1:
            for attempt in range(1,attempts+1):
                time.sleep(retry_delay)
                if not os.path.isfile(caps_path + filename):
                    print("-- Trying attempt " + str(attempt) + " of " + str(attempts))
                    if cam_opt == "uvccapture":
                        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
                        if os.path.isfile(caps_path + filename):
                            print("Done on extra attempt " + str(attempt))
                            sys.exit()
                    elif cam_opt ==  "fswebcam":
                        settings_dict = new_load_camera_settings(settings_file)
                        filename = new_take_with_fswebcam(settings_dict, caps_path)
                        if os.path.isfile(caps_path + filename):
                            print("Done on try " + str(attempt))
                            sys.exit()
    #once all extra attempts have been made give it one last check then tell
    #the user we failed to create the file and try to write a error log entry
    if not os.path.isfile(caps_path + filename):
        print("FAILED no photos taken.")
        errmsg = "Failed with " + str(attempts) + " extra attempts, no photo saved."
        if log_error == True:
            try:
                pigrow_defs.write_log(script, errmsg, loc_dic['err_log'])
            except Exception as e:
                print("couldn't log error :( " + str(e))
