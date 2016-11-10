#!/usr/bin/python
import time
import os

s_val = "60"
c_val = "60"
g_val = "60"
b_val = "60"
x_dim = 1600
y_dim = 1200
additonal_commands = "-d/dev/video0 -w"
cappath = "/home/pi/cam_caps/"
loc_settings = "/home/pi/Pigrow/config/camera_settings.txt"
try:
    with open(loc_settings, "r") as f:
        for line in f:
            s_item = line.split("=")
            if s_item[0] == "s_val":
                s_val = s_item[1].split("\n")[0]
            elif s_item[0] == "c_val":
                c_val = s_item[1].split("\n")[0]
            elif s_item[0] == "g_val":
                g_val = s_item[1].split("\n")[0]
            elif s_item[0] == "b_val":
                b_val = s_item[1].split("\n")[0]
            elif s_item[0] == "x_dim":
                x_dim = s_item[1].split("\n")[0]
            elif s_item[0] == "y_dim":
                y_dim = s_item[1].split("\n")[0]
            elif s_item[0] == "additonal_commands":
                additonal_commands = s_item[1].split("\n")[0]
except:
    print("No config file for camera, using default")
    print("Run cam_config.py to create one")

# take and save photo
timenow = time.time()
timenow = str(timenow)[0:10]
filename= "cap_"+str(timenow)+".jpg"
os.system("sudo uvccapture "+additonal_commands+" -S"+s_val+" -C" + c_val + " -G"+ g_val +" -B"+ b_val +" -x"+str(x_dim)+" -y"+str(y_dim)+" -v -t0 -o"+cappath+filename)
print("Image taken and saved to "+cappath+filename)
