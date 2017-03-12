#!/usr/bin/python
import os
import sys
import time


def load_camera_settings(loc_dic):
    # defaults for when config file not found
    s_val = "20"
    c_val = "20"
    g_val = "20"
    b_val = "50"
    x_dim = 1600
    y_dim = 1200
    additonal_commands = "-d/dev/video0 -w"
    loc_settings = "/home/pi/Pigrow/config/camera_settings.txt"
    caps_path = "/home/pi/Pigrow/caps/"
    try:
        caps_path = loc_dic['caps_path']
    except Exception: if os.exists(caps_path):
            print("Using default")
        else:
            caps_path = "./"
            print("default path doesn't work, using current directory (sorry)")
    try:
        loc_setting = loc_dic['camera_settings']
        print("using camera settings file as directed by dirlocs file.")
    except Exception:        print("camera settings file not mentioned in dirlocs file, using defaults.")
    try:
        with open(loc_settings, "r") as f:
            for line in f:
                s_item = line.split("=")
                if s_item[0] == "s_val":
                    s_val = s_item[1].strip()
                elif s_item[0] == "c_val":
                    c_val = s_item[1].strip()
                elif s_item[0] == "g_val":
                    g_val = s_item[1].strip()
                elif s_item[0] == "b_val":
                    b_val = s_item[1].strip()
                elif s_item[0] == "x_dim":
                    x_dim = s_item[1].strip()
                elif s_item[0] == "y_dim":
                    y_dim = s_item[1].strip()
                elif s_item[0] == "additonal_commands":
                    additonal_commands = s_item[1].strip()
    except Exception:        print("looked at " + loc_settings)
        print("but couldn't find config file for camera, so default values")
        print("  - Run cam_config.py to create one")
        print("     - or edit dirlocs config file to point to the config file.")
    return (s_val, c_val, g_val, b_val, x_dim,
            y_dim, additonal_commands, caps_path)

# take and save photo

def take_with_uvccapture(s_val="20", c_val="20", g_val="20", b_val="20", x_dim=1600, y_dim=1200, additonal_commands="", caps_path="./"):
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename = "cap_"+str(timenow)+".jpg"
    os.system("uvccapture "+additonal_commands+" -S"+s_val+" -C" + c_val + " -G" + g_val +" -B"+ b_val +" -x"+str(x_dim)+" -y"+str(y_dim)+" -v -t0 -o"+caps_path+filename)
    print("Image taken and saved to " +caps_path+filename)
    return filename


if __name__ == '__main__':

    sys.path.append('/home/pi/Pigrow/scripts/')
    import pigrow_defs
    # script = 'camcap.py'  #used with logging module
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)

    s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path = load_camera_settings(
        loc_dic)
    filename = take_with_uvccapture(
    s_val,
    c_val,
    g_val,
    b_val,
    x_dim,
    y_dim,
    additonal_commands,
     caps_path)
