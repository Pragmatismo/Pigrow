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
            print(" Resolution not set, using default 1920x1080")
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

    print("Base cmd set to - ", cam_cmd)
    return cam_cmd

def take_with_fswebcam(cam_cmd):
    timenow  = str(time.time())[0:10]
    filepath = settings.out_folder + settings.set_name + "_" + str(timenow) + ".jpg"
    cam_cmd += " " + filepath

    os.system(cam_cmd)
    print("Capture Finished:" + filepath)

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
    #print(settings.sdict)


# Capture Thread
class FswCaptureThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        base_cmd = set_for_with_fswebcam()
        while settings.active == True:
            take_with_fswebcam(base_cmd)
            time.sleep(settings.delay)

def start_capture_loop(received_input):
    print("Starting capture loop.")
    settings.active = True
    new_load_camera_settings(settings.camera_settings)

    if settings.camera_opt == "fsw":
        capture_thread = FswCaptureThread()
        capture_thread.start()
    elif settings.camera_opt == "picam":
        print("Sorry picam capture is not yet written")

def stop_capture_loop(received_input):
    print("Stopping capture loop.")
    settings.active = False


# Settings
def use_picam(received_input):
    settings.camera_opt = "picam"
    print("Camera Set to Picam")

def use_fsw(received_input):
    settings.camera_opt = "fsw"
    print("Camera Set to FSWebcam")

def set_outfolder(received_input):
    settings.out_folder = received_input[1]
    print("Outfolder Set to", received_input[1])

def set_setname(received_input):
    settings.set_name = received_input[1]
    print("set_name Set to", received_input[1])

def set_camset(received_input):
    settings.camera_settings = received_input[1]
    print("camera_settings Set to", received_input[1])

def set_delay(received_input):
    try:
        settings.delay = float(received_input[1])
        print(f"set delay of {received_input[1]}")
    except:
        print(f"delay value '{received_input[1]}' invalid")

def set_flimit(received_input):
    try:
        settings.frame_limit = int(received_input[1])
        print(f"set frame_limit of {received_input[1]}")
    except:
        print(f"frame_limit value '{received_input[1]}' invalid")

def show_help(received_input):
    help_text =  "Camera Timelapse Quick Capture Tool\n"
    help_text += "A remote trigger for making short timelapse sets\n\n"
    help_text += "Commands; "
    #help_text += str(commands)
    print(help_text)


# Main Loop
commands = {'start':start_capture_loop,
            'stop':stop_capture_loop,
            'use_picam':use_picam,
            'use_fsw':use_fsw,
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
            print("Command", received_input[0], "not recognised, use help to get a list of commands")

        # Confirm input recieved, only needed for testing
        # output = f"recieved input {received_input[0]}"
        # print(output)
        # sys.stdout.flush()


except KeyboardInterrupt:
    pass
