#!/usr/bin/python
import os, sys
s_val = "60"
c_val = "60"
g_val = "60"
b_val = "60"
x_dim = 1280
y_dim = 720
additonal_commands = "-d/dev/video0 -w"
loc_settings = "/home/pi/Pigrow/config/"
if not os.path.exists(loc_settings):
    os.makedirs(loc_settings)
loc_settings = loc_settings + "camera_settings.txt"
 #for taking ranges
start_v = 10 #between 1-255 (depending on camera)
end_v = 100 #between 1-255 (depnding on camera)
skip_v = 10 #ten represents value increase by ten

for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    if  thearg == 'locpath':
        loc_settings = str(argu).split('=')[1]
    elif  thearg == 'loc':
        loc_settings = loc_settings + str(argu).split('=')[1]
    elif  thearg == 'srange':
        start_v = int(str(argu).split('=')[1])
    elif  thearg == 'erange':
        end_v = int(str(argu).split('=')[1])
    elif  thearg == 'rangejump':
        skip_v = int(str(argu).split('=')[1])
    elif  thearg == 'rangeS':
        start_v = int(str(argu).split('=')[1])


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

def capture_image(s_cap, c_cap, g_cap, b_cap, x_cap, y_cap, output_file, additonal=""):
    cam_cmd = "sudo uvccapture " + additonal      #additional commands (camera select)
    cam_cmd += " -S" + str(s_cap) + " -C" + str(c_cap) + " -G" + str(g_cap) + " -B" + str(b_cap)
    cam_cmd += " -x"+str(x_cap)+" -y"+str(y_cap) + " "  #x and y dimensions of photo
    cam_cmd += "-v -t0 -o" + output_file          #verbose, no delay, output
    print("---Doing: " + cam_cmd)
    os.system(cam_cmd)
    print("Captured, " + output_file)

def show_menu():
    global s_val, c_val, g_val, b_val
    global x_dim, y_dim
    global additonal_commands

    print("----------------------------")
    print("---Camera test and config---")
    print("----------------------------")
    print("This will take a series of images with the camera")
    print("varying one of the settings to create a range from")
    print("which you can select the best configuration.")
    print("")
    print("Current settings; S = " + str(s_val) + "  C = " + str(c_val) + "  G = " + str(g_val) + "  B = " + str(b_val))
    print("  ______________________________________________")
    print(" |Set value             dim - show camera dims  |")
    print(" | 1 - Saturation         x - set x dim         |")
    print(" | 2 - Contrast           y - set y dim         |")
    print(" | 3 - Gain              -----------------------|")
    print(" | 4 - Brightness       t - take and show test  |")
    print(" |                      d - take camera default |")
    print(" |Take Range            r - range test          |")
    print(" | 5 - Saturation        -----------------------|")
    print(" | 6 - Contrast          |")
    print(" | 7 - Gain              |")
    print(" | 8 - Brightness        |")
    print(" |                       -------------")
    print(" | s - Save Config File to Disk      |")
    print(" | 0 - Delete Images       q to quit |")
    print("  ___________________________________|")
    print("")
    option = raw_input("Type the number and press return;")
    if option == "1":
        s_val = raw_input("Input value to use for Saturation..")
        show_menu()
    elif option == "2":
        c_val = raw_input("Input value to use for Contrast..")
        show_menu()
    elif option == "3":
        g_val = raw_input("Input value to use for Gain..")
        show_menu()
    elif option == "4":
        b_val = raw_input("Input value to use for Brightness..")
        show_menu()
    elif option == "x":
        x_dim = raw_input("Input value to use for X dim; ")
        show_menu()
    elif option == "y":
        y_dim = raw_input("Input value to use for Y dim; ")
        show_menu()
    elif option == "dim":
        print("ok, this list is ugly...")
          # if using more than one webcam at a time lsusb to find bus and device number
          # then add -s BUS:DEVICE e.g. -s 001:005 to only search that device
          #e.g. os.system("lsusb -s 001:002 -v | egrep "Width|Height")
        os.system('lsusb -v | egrep "Width|Height"')
        print("    ")
        raw_input("Press return to continue...")
        show_menu()

    elif option == "5":
        print("Capturing range of Saturation images...")
        for s in range(start_v,end_v,skip_v):
            output_file = "test_range_s_"+str(s)+".jpg"
            capture_image(s, c_val, g_val, b_val, x_dim, y_dim, output_file, additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_s_"+str(start_v)+".jpg")
        s_val = raw_input("Input value to use for Saturation..")
        show_menu()

    elif option == "6":
        print("Capturing range of Contrast images...")
        for c in range(start_v,end_v,skip_v):
            output_file = "test_range_c_"+str(c)+".jpg"
            capture_image(s_val, c, g_val, b_val, x_dim, y_dim, output_file, additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_c_"+str(start_v)+".jpg")
        c_val = raw_input("Input value to use for Contrast..")
        show_menu()

    elif option == "7":
        print("Capturing range of Gain images...")
        for g in range(start_v,end_v,skip_v):
            output_file = "test_range_g_"+str(g)+".jpg"
            capture_image(s_val, c_val, g, b_val, x_dim, y_dim, output_file, additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_g_"+str(start_v)+".jpg")
        g_val = raw_input("Input value to use for Gain..")
        show_menu()

    elif option == "8":
        print("Capturing range of Brightness images...")
        for b in range(start_v,end_v,skip_v):
            output_file = "test_range_b_"+str(b)+".jpg"
            capture_image(s_val, c_val, g_val, b, x_dim, y_dim, output_file, additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_b_"+str(start_v)+".jpg")
        b_val = raw_input("Input value to use for Brightness..")
        show_menu()

    elif option == "0":
        os.system("sudo rm test_range_*.jpg")
        print("Images deleted")
        show_menu()
    elif option == "t":
        print("Using current configuration to take image...")
        output_file = "test_current.jpg"
        capture_image(s_val, c_val, g_val, b_val, x_dim, y_dim, output_file, additonal_commands)
        os.system("gpicview " + output_file)
        show_menu()
    elif option == "d":
        print("Using camera deafults to take image...")
        output_file = "test_defaults.jpg"
        cam_cmd = "sudo uvccapture " + additonal_commands   #additional commands (camera select)
        cam_cmd += " -x"+str(x_dim)+" -y"+str(y_dim) + " "  #x and y dimensions of photo
        cam_cmd += "-v -t0 -o" + output_file          #verbose, no delay, output
        print("---Doing: " + cam_cmd)
        os.system(cam_cmd)
        os.system("gpicview " + output_file)

    elif option == "r":
        print("Testing stability using current configuration to take range...")
        for x in range(1,10):
            output_file = "test_range_"+str(x)+".jpg"
            capture_image(s_val, c_val, g_val, b_val, x_dim, y_dim, output_file, additonal_commands)
        os.system("gpicview test_range_1.jpg")
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

while True:
    show_menu()

print "done"
