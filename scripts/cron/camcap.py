#!/usr/bin/python
import time
import os
import sys

homedir = os.getenv("HOME")
#Setting Blank Variables
cam_opt = "uvccapture"
settings_file = None
caps_path = None
loc_dic = {}
attempts = 3

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help' or argu == "-help" or argu == "--h":
        print("Pigrow Image Capture Script")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        sys.exit(0)
    elif argu == '-flags':
        print("settings_file=" + homedir + "/Pigrow/config/camera_settings.txt")
        print("caps_path=" + homedir + "/Pigrow/caps/")
        sys.exit()
    if "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                settings_file = theval
            elif thearg == 'caps_path' or thearg == 'caps':
                caps_path = theval
        except:
            print("Didn't undertand " + str(argu))

def set_caps_path(loc_dic, caps_path):
    # Select location to save images
    #  This would be better if the
    if caps_path == None:
        try:
            caps_path = loc_dic['caps_path']
        except:
            caps_path = homedir + '/Pigrow/caps/'
            if os.path.exists(caps_path):
                print("Using default folder; " + str(caps_path))
            else:
                caps_path = ""
                print("default path doesn't work, using current directory (sorry)")
    else:
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
        try:
            with open(settings_file, "r") as f:
                for line in f:
                    s_item = line.split("=")
                    val = s_item[1].strip()
                    if s_item[0] == "s_val":
                        s_val = val
                    elif s_item[0] == "c_val":
                        c_val = val
                    elif s_item[0] == "g_val":
                        g_val = val
                    elif s_item[0] == "b_val":
                        b_val = val
                    elif s_item[0] == "x_dim":
                        x_dim = val
                    elif s_item[0] == "y_dim":
                        y_dim = val
                    elif s_item[0] == "cam_num":
                        cam_num = val
                    elif s_item[0] == "cam_opt":
                            cam_opt = val
                    elif s_item[0] == "fsw_extra":
                        try:
                            fsw_extra = ''                  ##
                            for cmdv in s_item[1:]:         ##
                                if not cmdv == '':          ##  this just puts it
                                    fsw_extra += cmdv + "=" ##  back together again
                            fsw_extra = fsw_extra[:-1]      ##
                        except:
                            print("couldn't read fsw extra commands, trying without...")
                            fsw_extra = ''
                    elif s_item[0] == "uvc_extra":
                        uvc_extra = s_item[1].strip()
        except Exception as e:
            print e
            print("looked at " + settings_file)
            print("but couldn't find config file for camera, so using default values")
            print("  - Run cam_config.py to automatically create one")
        if not cam_opt == 'fswebcam' or not cam_opt == 'uvccapture':
            print("setting cam opt to uvccapture as unspecified")
            cam_opt = 'uvccapture'
    return (s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra)

# take and save photo
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
    print("----")
    print(cmd)
    print("----")
    os.system(cmd)
    print("Image taken and saved to "+caps_path+filename)
    return filename

def take_with_fswebcam(s_val="", c_val="", g_val="", b_val="", x_dim=100000, y_dim=100000, cam_num='/dev/video0', fsw_extra='', caps_path=""):
    focus_val = "10"
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename= "cap_"+str(timenow)+".jpg"

    cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
    cam_cmd += " -d v4l2:" + cam_num
    cam_cmd += " -D 2"      #the delay in seconds before taking photo
    cam_cmd += " -S 5"      #number of frames to skip before taking image
    # to list controls use fswebcam -d v4l2:/dev/video0 --list-controls
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
    # cam_cmd += ' --info "HELLO INFO TEXT"'
    cam_cmd += " " + caps_path + filename  #output filename'
    print("----")
    print(cam_cmd)
    print("----")
    os.system(cam_cmd)
    print("Image taken and saved to " + caps_path + filename)
    return filename

# main program
if __name__ == '__main__':
    #when running as a script import pigrow_defs and find file path info
    sys.path.append(homedir + '/Pigrow/scripts/')
    try:
        import pigrow_defs
        #script = 'camcap.py'  #used with logging module
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
            print("Settings file not found, using default values instead")
            s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, = "", "", "", "", "100000", "100000", "", "uvccapture", "", ""
    else:
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
        print("Error: Image file not found")
        # If trying more than once
        if attempts > 1:
            for attempt in range(0,attempts):
                if not os.path.isfile(caps_path + filename):
                    print("-- Trying attempt " + str(attempt) + " of " + str(attempts))
                    if cam_opt == "uvccapture":
                        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
                        if os.path.isfile(caps_path + filename):
                            print("Done on attempt " + str(attempt))
                            sys.exit()
                    elif cam_opt ==  "fswebcam":
                        filename = take_with_fswebcam(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, fsw_extra, caps_path)
                        if os.path.isfile(caps_path + filename):
                            print("Done on try " + str(attempt))
                            sys.exit()
    if not os.path.isfile(caps_path + filename):
        print("FAILED no photos taken.")
