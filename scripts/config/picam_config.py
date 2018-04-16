#!/usr/bin/python
import os, sys
import time
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
script = 'picamcap.py'
import pigrow_defs
try:
    from picamera import PiCamera
except:
    print("Picamera is not installed, is this even a raspberry pi?!")
    exit()
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
loc_dic = pigrow_defs.load_locs(loc_locs)
caps_path = loc_dic["caps_path"]
camera = PiCamera()
s_val = "10"
c_val = "10"
g_val = "800"
b_val = "10"
x_dim = 1920
y_dim = 1080
additonal_commands = ""
loc_settings = homedir + "/Pigrow/config/"
if not os.path.exists(loc_settings):
    os.makedirs(loc_settings)
loc_settings = loc_settings + "picam_settings.txt"

start_v = 10 #between 1-255
end_v = 100 #between 1-255
skip_v = 10 #ten represents value increase by ten

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
    pass


def show_menu():
    global s_val
    global c_val
    global g_val
    global b_val
    print("----------------------------")
    print("---Camera test and config---")
    print("----------------------------")
    print("This will take a series of images with the camera")
    print("varying one of the settings to create a range from")
    print("which you can select the best configuration.")
    print("")
    print("Current settings; S = " + str(s_val) + "  C = " + str(c_val) + "  iso = " + str(g_val) + "  B = " + str(b_val))
    print("  _______________________")
    print(" |Set value              |")
    print(" | 1 - Saturation        |")
    print(" | 2 - Contrast          |")
    print(" | 3 - iso              ----------------------|")
    print(" | 4 - Brightness                              |")
    print(" |                      t - take and show test |")
    print(" |Take Range            r - range test         |")
    print(" | 5 - Saturation        ----------------------|")
    print(" | 6 - Contrast          |")
    print(" | 7 - iso              |")
    print(" | 8 - Brightness        |")
    print(" |                       -------------")
    print(" | s - Save Config File to Disk      |")
    print(" | 0 - Delete Images       q to quit |")
    print("  ___________________________________|")
    print("")
    option = raw_input("Type the number and press return; ")
    if option == "1":
        s_val = raw_input("Input value to use for Saturation.. ")
        show_menu()
    elif option == "2":
        c_val = raw_input("Input value to use for Contrast.. ")
        show_menu()
    elif option == "3":
        g_val = raw_input("Input value to use for ISO (100 to 900).. ")
        show_menu()
    elif option == "4":
        b_val = raw_input("Input value to use for Brightness.. ")
        show_menu()

    elif option == "5":
        print("Capturing range of Saturation images...")
        for s in range(start_v,end_v,skip_v):
            print("---Doing:Saturation;" + str(s))
            camera.saturation = int(s)
            camera.contrast = int(c_val)
            camera.brightness = int(b_val)
            camera.iso = int(g_val)
            time.sleep(2)
            camera.capture(caps_path+"test_range_s_" + str(s) + ".jpg")
        print("Range captured, view and select best value..")
        os.system("gpicview "+caps_path+"test_range_s_"+str(start_v)+".jpg")
        s_val = raw_input("Input value to use for Saturation.. ")
        show_menu()

    elif option == "6":
        print("Capturing range of Contrast images...")
        for c in range(start_v,end_v,skip_v):
            print("---Doing: Contrast=" + str(c))
            camera.contrast = int(c)
            camera.saturation = int(s_val)
            camera.iso = int(g_val)
            camera.brightness = int(b_val)
            time.sleep(2)
            camera.capture(caps_path+"test_range_c_" + str(c) + ".jpg")
        print("Range captured, view and select best value..")
        os.system("gpicview "+caps_path+"test_range_c_"+str(start_v)+".jpg")
        c_val = raw_input("Input value to use for Contrast..")
        show_menu()

    elif option == "7":
        print("Capturing range of ISO images...")
        for g in range(100,900,100):
            print("---Doing: analog_iso=" + str(g))
            camera.saturation = int(s_val)
            camera.contrast = int(c_val)
            camera.brightness = int(b_val)
            camera.iso = int(g)
            time.sleep(2)
            camera.capture(caps_path+"test_range_iso_" + str(g) + ".jpg")
        print("Range captured, view and select best value..")
        os.system("gpicview "+caps_path+"test_range_iso_100.jpg")
        g_val = raw_input("Input value to use for iso..")
        show_menu()

    elif option == "8":
        print("Capturing range of Brightness images...")
        for b in range(start_v,end_v,skip_v):
            print("---Doing: broghtness=" + str(b))
            camera.brightness = int(b)
            camera.saturation = int(s_val)
            camera.contrast = int(c_val)
            camera.iso = int(g_val)
            time.sleep(2)
            camera.capture(caps_path+"test_range_b_" + str(b) + ".jpg")
        print("Range captured, view and select best value..")
        os.system("gpicview "+caps_path+"test_range_b_"+str(start_v)+".jpg")
        b_val = raw_input("Input value to use for Brightness..")
        show_menu()

    elif option == "0":
        os.system("sudo rm "+caps_path+"test_range_*.jpg")
        print("Images deleted")
        show_menu()
    elif option == "t":
        print("Using current configuration to take image...")
        camera.saturation = int(s_val)
        camera.iso = int(g_val)
        camera.brightness = int(b_val)
        camera.saturation = int(c_val)
        time.sleep(2)
        camera.capture(caps_path+"test_range_.jpg")
        os.system("gpicview "+caps_path+"test_range_.jpg")
        show_menu()

    elif option == "r":
        print("Testing stability using current configuration to take range...")
        camera.saturation = int(s_val)
        camera.iso = int(g_val)
        camera.brightness = int(b_val)
        camera.saturation = int(c_val)
        for x in range(1,10):
            time.sleep(2)
            camera.capture(caps_path+"test_range_"+str(x)+".jpg")
        os.system("gpicview "+caps_path+"test_range_1.jpg")
        show_menu()

    elif option == "s":
        print("Saving configuration file...")
        with open(loc_settings, "w") as f:
            f.write("s_val="+s_val+"\n")
            f.write("c_val="+c_val+"\n")
            f.write("g_val="+g_val+"\n")
            f.write("b_val="+b_val+"\n")
            f.write("x_dim="+str(x_dim)+"\n")
            f.write("y_dim="+str(y_dim)+"\n")
            f.write("additonal_commands="+additonal_commands+ "\n")
        print("Config Saved")
        show_menu()
    elif option == "q" or option == "Q" or option == "":
        exit()
    else:
        print("That wasn't an option...")
        show_menu()

show_menu()

print "done"
