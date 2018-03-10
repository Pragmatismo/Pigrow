#!/usr/bin/python
import time
import os
import sys

homedir = os.getenv("HOME")
#Setting Blank Variables
settings_file = None
caps_path = None
loc_dic = {}

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow Image Capture Script")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        sys.exit(0)
    try:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if thearg == 'settings_file' or thearg == 'set':
            settings_file = theval
        elif thearg == 'caps_path' or thearg == 'caps':
            caps_path = theval
    except:
        print("Didn't undertand " + str(argu))

def load_camera_settings(loc_dic, caps_path, settings_file):
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
    # caps folder path from loc_dic file -annoying for multicam
    #check for caps path in dirlocs if none then tries to set default or finally resorts ot using local folder
    if caps_path == None:
        try:
            caps_path = loc_dic['caps_path']
        except:
            caps_path = homedir + '/Pigrow/caps/'
            if os.path.exists(caps_path):
                print("Using default folder; " + str(caps_path))
            else:
                caps_path = "./"
                print("default path doesn't work, using current directory (sorry)")
    else:
        print("saving to; " + str(caps_path))
    # finding camera settings file in loc_dic
    if settings_file == None:
        try:
            settings_file = loc_dic['camera_settings']
            print("using camera settings file as directed by dirlocs file; " + settings_file)
        except:
            settings_file = homedir + "/Pigrow/config/camera_settings.txt"
            print("camera settings file not found in dirlocs, trying default; " + settings_file)
    else:
        print("Using settings file; " + str(settings_file))
    #Grabbing all the relevent data from the settings file
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
        print("  - Run cam_config.py to create one")
        print("     - or edit dirlocs config file to point to the config file.")
    if not cam_opt == 'fswebcam' or not cam_opt == 'uvccapture':
        print("setting cam opt to uvccapture as unspecified")
        cam_opt = 'uvccapture'
    #
    #
    #  done to this point
    #
    #

    return (s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, caps_path)

# take and save photo
def take_with_uvccapture(s_val="", c_val="", g_val="", b_val="", x_dim=1600, y_dim=1200, cam_num='/dev/video0', uvc_extra="", caps_path="./"):
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

def take_with_fswebcam(s_val=None, c_val=None, g_val=None, b_val=None, x_dim=1600, y_dim=1200, cam_num='/dev/video0', fsw_extra='', caps_path="./"):
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

if __name__ == '__main__':

    sys.path.append(homedir + '/Pigrow/scripts/')
    try:
        import pigrow_defs
        #script = 'camcap.py'  #used with logging module
        loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
        loc_dic = pigrow_defs.load_locs(loc_locs)
    except:
        print("Pigrow localisation module failed to initilize, unable to load settings")


    s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, cam_opt, fsw_extra, uvc_extra, caps_path = load_camera_settings(loc_dic, caps_path, settings_file)
    if cam_opt == "uvccapture":
        filename = take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, uvc_extra, caps_path)
    elif cam_opt ==  "fswebcam":
        filename = take_with_fswebcam(s_val, c_val, g_val, b_val, x_dim, y_dim, cam_num, fsw_extra, caps_path)
    else:
        print("unknown capture option -" + str(cam_opt) + "- sorry")
