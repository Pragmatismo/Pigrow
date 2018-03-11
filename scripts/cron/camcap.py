#!/usr/bin/python
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
            print e
            print("looked at " + settings_file)
            print("but couldn't load config data for camera, resorting to default values")
            print("  - Run cam_config.py to automatically create a new config file")
            print("    or make sure you're pointing to the correct file in dirlocs.")
        # check to ensure a valid option is set, if not selects default
        if not cam_opt == 'fswebcam' or not cam_opt == 'uvccapture':
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

def take_with_fswebcam(s_val="", c_val="", g_val="", b_val="", x_dim=100000, y_dim=100000, cam_num='/dev/video0', fsw_extra='', caps_path=""):
    #     fswebcam is a great little program
    #     because it's reliable, quick and
    #     gives loads of control especiully
    #     cool is it's ability to grab webcam
    #     control's from your camera using
    # # #       fswebcam -d v4l2:/dev/video0 --list-controls
    #     this is how the camera config
    #     scripts determine the extra controls
    #     you can use.
    #     # cam_cmd += ' --info "HELLO INFO TEXT"'
    #     is another interesting one to experiment with at some point
    ####
    #
    #determine the time to use in the photos name
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    # set the  important command string values for fswebcam
    cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
    cam_cmd += " -d v4l2:" + cam_num
    cam_cmd += " -D 2"      #the delay in seconds before taking photo
    cam_cmd += " -S 5"      #number of frames to skip before taking image
    # add extra options when set
    if not b_val == '':
        cam_cmd += " --set brightness=" + str(b_val)
    if not c_val == '':
        cam_cmd += " --set contrast=" + str(c_val)
    if not s_val == '':
        cam_cmd += " --set Saturation=" + str(s_val)
    if not g_val == '':
        cam_cmd += " --set gain=" + str(g_val)
    cam_cmd += " " + fsw_extra.strip()
    cam_cmd += " --jpeg 90" #jpeg quality
    cam_cmd += " " + caps_path + filename  #output filename
    # show user command on command line
    print("----")
    print(cam_cmd)
    print("----")
    # run the command on the system
    os.system(cam_cmd)
    #tell the user we're back in control after fsw has finished.
    print("Capture Finished, Image Path : " + caps_path + filename)
    #hand back the filename so we can check was created or pass it on for editing
    #or other mantipulation when this is being run from other scripts as a module
    return filename

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
            print("loading settings from settings file referencesd in dirlocs ")
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
    #Taking the photo with the selected camera program
    #first attempt
    if cam_opt == "uvccapture":
        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
    elif cam_opt ==  "fswebcam":
        filename = take_with_fswebcam(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, fsw_extra, caps_path)
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
                        filename = take_with_fswebcam(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, fsw_extra, caps_path)
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
