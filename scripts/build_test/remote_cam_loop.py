#!/usr/bin/python3

'''
Runs on the raspberry pi and enables the gui to record short-duration timelapse
'''

import os
import sys
import time
import datetime
import threading

#sys.stdout.flush()

class Settings:
    def __init__(self):
        self.camera_opt = "fsw"
        self.delay = 5
        self.out_folder = "/home/pi/"
        self.set_name = "quick"
        self.camera_settings = "/home/pi/Pigrow/config/camera_config.txt"
        self.sdict = {}
        self.frame_limit = -1

        self.active = False

settings = Settings()

# Camera and Capture Tools
def set_for_with_fswebcam():
    sets_dict = settings.sdict
    # add defaults
    if not 'resolution' in sets_dict:
        if 'x_dim' in sets_dict and 'y_dim' in sets_dict:
            sets_dict['resolution'] = sets_dict['x_dim'] + "x" + sets_dict['y_dim']
        else:
            print(" Resolution not set, using default 1920x1080\n")
            sys.stdout.flush()
            sets_dict['resolution'] = '1920x1080'
    if not 'fs_delay' in sets_dict:
        sets_dict['fs_delay'] = '2'
    if not 'fs_fskip' in sets_dict:
        sets_dict['fs_fskip'] = '5'
    if not 'fs_jpg_q' in sets_dict:
        sets_dict['fs_jpg_q'] = '90'

    # Set the  command string for fswebcam
    cam_cmd  = "fswebcam -r " + sets_dict['resolution']
    cam_cmd += " -d v4l2:" + sets_dict['cam_num']
    cam_cmd += " -D " + sets_dict['fs_delay']     # the delay in seconds before taking photo
    cam_cmd += " -S " + sets_dict['fs_fskip']     # number of frames to skip before taking image
    if "fs_banner" in sets_dict:
        if sets_dict["fs_banner"].lower() == "false":
            cam_cmd += " --no-banner"
    ignore_list = ['resolution', 'cam_num', 'fs_delay', 'fs_fskip', 'fs_banner', 'uvc_extra', 'fsw_extra', 'cam_opt']
    for key, val in sets_dict.items():
        if not key in ignore_list:
            cam_cmd += ' --set "' + key + '"="' + val + '"'
    cam_cmd += " --jpeg " + sets_dict['fs_jpg_q'] # jpeg quality

    print("Base cmd set to - ", cam_cmd + "\n")
    sys.stdout.flush()
    return cam_cmd

def take_with_fswebcam(cam_cmd, count):
    timenow  = str(time.time())[0:10]
    filepath = settings.out_folder + settings.set_name + "_" + str(timenow) + ".jpg"
    cam_cmd += " " + filepath

    os.system(cam_cmd)
    print("Capture " + str(count) + " Finished:" + filepath + "\n")
    sys.stdout.flush()

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
    settings.sdict = sets_dict

# Capture Thread
class FswCaptureThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        base_cmd = set_for_with_fswebcam()
        count = 1
        while settings.active == True:
            take_with_fswebcam(base_cmd, count)
            count += 1
            if count > settings.frame_limit and not settings.frame_limit == -1:
                settings.active = False
            time.sleep(settings.delay)

def set_for_with_rpicam():
    sets_dict = settings.sdict

    conf_text = ""
    #print(";", sets_dict, " ----")

    # set image res for camera's main stream
    if "Resolution" in sets_dict:
        x_dim, y_dim = sets_dict["Resolution"].split("x")
        sets_dict["width"] = x_dim
        sets_dict["height"] = y_dim

    # set metadata flag
    # --metadata arg  Save captured image metadata to a file or "-" for stdout
    # if "metadata" in sets_dict:
    #     if sets_dict["metadata"] == "each":
    #         sets_dict["metadata"] = os.path.splitext(save_filename)[0] + ".json"
    #     elif sets_dict["metadata"] == "off":
    #         sets_dict.pop("metadata", None)
    #     elif sets_dict["metadata"] == "$path":
    #         sets_dict["metadata"] = homedir + '/Pigrow/logs/cap_metadata.json'

    # check if raw is set
    if "raw" in sets_dict:
        if sets_dict["raw"] == "True":
            conf_text += " --raw"

    # remove script opts
    to_remove = ["Resolution", "cam_opt", "cam_num", "raw", "metadata"]
    for item in to_remove:
        sets_dict.pop(item, None)


    for item in sets_dict.keys():
            if not sets_dict[item] == "":
                conf_text += " --" + item + " " + sets_dict[item]

    cam_cmd = "rpicam-still --nopreview " + conf_text + " -o "
    #
    print("Base cmd set to - ", cam_cmd + "\n")
    sys.stdout.flush()
    return cam_cmd

def take_with_rpicam(cam_cmd, count):
    timenow  = str(time.time())[0:10]
    filepath = settings.out_folder + settings.set_name + "_" + str(timenow) + ".jpg"
    cam_cmd += " " + filepath

    os.system(cam_cmd)
    print("Capture " + str(count) + " Finished:" + filepath + "\n")
    sys.stdout.flush()

class RpiCaptureThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        base_cmd = set_for_with_rpicam()
        count = 1
        while settings.active == True:
            take_with_rpicam(base_cmd, count)
            count += 1
            if count > settings.frame_limit and not settings.frame_limit == -1:
                settings.active = False
            time.sleep(settings.delay)

def start_capture_loop(received_input):
    print("Starting capture loop.\n")
    sys.stdout.flush()
    settings.active = True
    new_load_camera_settings(settings.camera_settings)

    if settings.camera_opt == "fsw":
        capture_thread = FswCaptureThread()
        capture_thread.start()
    elif settings.camera_opt == "rpicam":
        capture_thread = RpiCaptureThread()
        capture_thread.start()
    elif settings.camera_opt == "picam":
        print("Sorry picam capture is not yet written\n")
        sys.stdout.flush()

def stop_capture_loop(received_input):
    settings.active = False
    print("Stopping capture loop.\n")
    sys.stdout.flush()


# Settings
def use_picam(received_input):
    settings.camera_opt = "picam"
    print("Camera Set to Picam")
    sys.stdout.flush()

def use_fsw(received_input):
    settings.camera_opt = "fsw"
    print("Camera Set to FSWebcam")
    sys.stdout.flush()

def use_rpicam(received_input):
    settings.camera_opt = "rpicam"
    print("Camera Set to Rpicam")
    sys.stdout.flush()

def set_outfolder(received_input):
    settings.out_folder = received_input[1]
    print("Outfolder Set to", received_input[1] + "\n")
    sys.stdout.flush()

def set_setname(received_input):
    settings.set_name = received_input[1]
    print("set_name Set to", received_input[1] + "\n")
    sys.stdout.flush()

def set_camset(received_input):
    settings.camera_settings = received_input[1]
    print("camera_settings Set to", received_input[1] + "\n")
    sys.stdout.flush()

def set_delay(received_input):
    try:
        settings.delay = float(received_input[1])
        print("set delay of " + received_input[1] + "\n")
        sys.stdout.flush()
    except:
        print("delay value '" + received_input[1] + "' invalid\n")
        sys.stdout.flush()

def set_flimit(received_input):
    try:
        settings.frame_limit = int(received_input[1])
        print("set frame_limit of " + received_input[1] + "\n")
        sys.stdout.flush()
    except:
        print("frame_limit value '" + received_input[1] + "' invalid\n")
        sys.stdout.flush()

def show_help(received_input):
    help_text =  "Camera Timelapse Quick Capture Tool\n"
    help_text += "A remote trigger for making short timelapse sets\n\n"
    help_text += "Commands; \n"
    #help_text += str(commands)
    print(help_text)
    sys.stdout.flush()


# Main Loop
commands = {'start':start_capture_loop,
            'stop':stop_capture_loop,
            'use_picam':use_picam,
            'use_fsw':use_fsw,
            'use_rpicam':use_rpicam,
            'set_outfolder':set_outfolder,
            'set_name':set_setname,
            'set_camset':set_camset,
            'set_delay':set_delay,
            'set_flimit':set_flimit,
            'help':show_help}

try:
    while True:
        # Read input from stdin
        received_input = sys.stdin.readline().strip()
        if " " in received_input:
            received_input = received_input.split(" ", 1)
        else:
            received_input = [received_input, ""]

        # Run command from input
        if received_input[0] in commands:
            commands[received_input[0]](received_input)
        else:
            if not received_input[0].strip() == "":
                print("Command", received_input[0], "not recognised, use help to get a list of commands\n")
                sys.stdout.flush()

        # Confirm input recieved, only needed for testing
        # output = f"recieved input {received_input[0]}"
        # print(output)
        # sys.stdout.flush()


except KeyboardInterrupt:
    pass
