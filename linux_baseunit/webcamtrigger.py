#!/usr/bin/python
import time
import os
import sys

homedir = os.getenv("HOME")
print("")
print("")
print(" USE l=3 to take a photo every 3 somethings")
print("      t  to take triggered photos ")
print("     cap=" + homedir + "/folder/ to set caps path other than current dir")
print("      picam to use picam to take photos ")
print("      np to stop it trying to change the wallpaper")
print("   EXIT using ctrl-c or whatever")
pi_paper = True  #updates pi wall paper, use -nopaper to turn it off.
cam_to_use = "webcam"
s_val = "20"
c_val = "20"
g_val = "20"
b_val = "20"
x_dim = 1600
y_dim = 1200
additonal_commands = "-d/dev/video0 -w"

try:
    cappath = os.getcwd()
    cappath += '/'
except:
    cappath = homedir + "/webcamview/"

#cappath = "./"   #wont update wallpaper if, i dunno, it just don't
loc_settings = homedir + "/Pigrow/config/camera_settings.txt"
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
def set_picam(x_dim, y_dim, b_val, c_val, s_val, g_val):
    try:
        photo.camera = PiCamera()
        photo.camera.resolution = (int(x_dim),int(y_dim))
        photo.camera.brightness = int(b_val)
        photo.camera.contrast   = int(c_val)
        photo.camera.saturation = int(s_val)
        photo.camera.iso        = int(g_val)
        time.sleep(2)
        #camera.close()
        #return saved_filename
    except:
        print("!!!  Using Picam failed  !!!")
        raise
def photo():
    timenow = time.time()
    timenow = str(timenow)[0:10]
    filename = cappath + "cap_"+str(timenow)+".jpg"
    if cam_to_use == "webcam":
        os.system("uvccapture "+additonal_commands+" -S"+s_val+" -C" + c_val + " -G"+ g_val +" -B"+ b_val +" -x"+str(x_dim)+" -y"+str(y_dim)+" -v -t0 -o"+filename)
    elif cam_to_use == "picam":
        photo.camera.capture(filename)
    elif cam_to_use == "raspistill":
        os.system("raspistill -o " + filename)

    print("Image taken and saved to "+filename)
    #os.system("gpicview " + cappath+filename)
    if pi_paper == True:
        os.system("export DISPLAY=:0 && pcmanfm --set-wallpaper "+filename)

def TRIGGERED():
    while True:
        red = raw_input("press return to take picture")
        if red == "q":
            exit()
        else:
            photo()

def LOOPED(num=10):
    while True:
        photo()
        time.sleep(num)

if 'np'in sys.argv or 'nopaper' in sys.argv:
    pi_paper = False
    print(" Not going to try changing wall paper")

loop = False
trig = False
for argu in sys.argv[1:]:
    try:
        thearg = str(argu).split('=')[0]
    except:
        thearg = str(argu)

    if thearg == 'cap' or thearg =='cappath':
        cappath = str(argu).split('=')[1]

    if thearg == 'l' or thearg == 'looped':
        try:
            num = float(str(argu).split('=')[1])
        except:
            print("No speed supplied, taking every 10")
            num = 10
        loop = True

    if thearg == 't' or thearg == 'TRIGGERED':
        trig = True

    if thearg == "picam":
        cam_to_use = "picam"
        print(" Using Picam")
        from picamera import PiCamera
        set_picam(x_dim, y_dim, b_val, c_val, s_val, g_val)

    if thearg == "raspistill":
        cam_to_use = "raspistill"    



print(" Saving files to, " + str(cappath))

if loop == True:
    LOOPED(num)
elif trig == True:
    TRIGGERED()
else:
    photo()
