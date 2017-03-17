#!/usr/bin/python
import os

import configparser

#  Create configparser object
config = configparser.ConfigParser()

#  Read config settings from config.ini
config.read('../../config/config.ini')

# Viewing key from config file
saturation = config['CAMERA']['saturation']
contrast = config['CAMERA']['contrast']
gain = config['CAMERA']['gain']
brightness = config['CAMERA']['brightness']
x_dim = config['CAMERA']['x_dim']
y_dim = config['CAMERA']['y_dim']

s_val = saturation
c_val = contrast
g_val = gain
b_val = brightness

additional_commands = config['CAMERA']['additional_commands']

# for taking ranges
start_v = config['CAMERA']['start_v']  # between 1-255 (depending on camera)
end_v = config['CAMERA']['end_v']  # between 1-255 (depnding on camera)
skip_v = config['CAMERA']['end_v']  # ten represents value increase by ten


def capture_image(s_cap, c_cap, g_cap, b_cap, x_cap,
                  y_cap, output_file, additional=""):
    '''
    Method for capturing images from system webcams
    '''
    # additional commands (camera select)
    cam_cmd = "sudo uvccapture " + additional
    cam_cmd += " -S" + str(s_cap) + " -C" + str(c_cap) + \
        " -G" + str(g_cap) + " -B" + str(b_cap)
    cam_cmd += " -x" + str(x_cap) + " -y" + str(y_cap) + \
        " "  # x and y dimensions of photo
    cam_cmd += "-v -t0 -o" + output_file  # verbose, no delay, output
    print("---Doing: " + cam_cmd)
    os.system(cam_cmd)
    print("Captured, " + output_file)


def show_menu():
    """
    Display Menu for Camera testing and configuration
    """
    #  This would be a good place to implement a class instead of using global
    #  variables.
    global s_val
    global c_val
    global g_val
    global b_val
    global x_dim
    global y_dim
    global additional_commands
    global start_v
    global end_v
    global skip_v
    print("----------------------------")
    print("---Camera test and config---")
    print("----------------------------")
    print("This will take a series of images with the camera")
    print("varying one of the settings to create a range from")
    print("which you can select the best configuration.")
    print("")
    print(
        "Current settings: S = " +
        str(s_val) +
        "  C = " +
        str(c_val) +
        "  G = " +
        str(g_val) +
        "  B = " +
        str(b_val))
    print("                  x = " + str(x_dim) + "  y = " + str(y_dim))
    print("  ______________________________________________")
    print(" |Set value             dim - Show camera dims  |")
    print(" | 1 - Saturation         x - Set x dim         |")
    print(" | 2 - Contrast           y - Set y dim         |")
    print(" | 3 - Gain              -----------------------|")
    print(" | 4 - Brightness       t - Take and show test  |")
    print(" |                      d - Take camera default |")
    print(" |Take Range            r - Range test          |")
    print(" | 5 - Saturation                               |")
    print(" | 6 - Contrast         cam - Camera select     |")
    print(" | 7 - Gain                                     |")
    print(" | 8 - Brightness                               |")
    print(" |                                              |")
    print(" | s - Save Config File to Disk                 |")
    print(" | 0 - Delete Images               q - quit     |")
    print(" |______________________________________________|")
    print("")
    option = raw_input("Type the number and press return:")
    if option == "1":
        s_val = raw_input("Input value to use for Saturation..")
    elif option == "2":
        c_val = raw_input("Input value to use for Contrast..")
    elif option == "3":
        g_val = raw_input("Input value to use for Gain..")
    elif option == "4":
        b_val = raw_input("Input value to use for Brightness..")
    elif option == "x":
        x_dim = raw_input("Input value to use for X dim: ")
    elif option == "y":
        y_dim = raw_input("Input value to use for Y dim: ")
    elif option == "dim":
        print("Generating list of connected webcams...")
        # if using more than one webcam at a time lsusb to find
        # bus and device number
        # then add -s BUS:DEVICE e.g. -s 001:005 to only search that device
        # e.g. os.system("lsusb -s 001:002 -v | egrep "Width|Height")
        os.system('lsusb -v | egrep "Width|Height"')
        print("    ")
        raw_input("Press return to continue...")
    elif option == "cam":
        cam_opt = []
        for name in os.listdir("/dev/"):
            if name[0:5] == "video":
                cam_opt.append(name)
        print("Choice of:")
        print cam_opt
        cam_num = raw_input("Input camera number: ")
        additonal_commands = "-d/dev/video" + str(cam_num)

    elif option == "5":
        print("Capturing range of Saturation images...")
        for s in range(start_v, end_v, skip_v):
            output_file = "test_range_s_" + str(s) + ".jpg"
            capture_image(
                s,
                c_val,
                g_val,
                b_val,
                x_dim,
                y_dim,
                output_file,
                additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_s_" + str(start_v) + ".jpg")
        s_val = raw_input("Input value to use for Saturation...")

    elif option == "6":
        print("Capturing range of Contrast images...")
        for c in range(start_v, end_v, skip_v):
            output_file = "test_range_c_" + str(c) + ".jpg"
            capture_image(
                s_val,
                c,
                g_val,
                b_val,
                x_dim,
                y_dim,
                output_file,
                additonal_commands)
        print("Range captured, view and select best value..")
        os.system("gpicview test_range_c_" + str(start_v) + ".jpg")
        c_val = raw_input("Input value to use for Contrast...")

    elif option == "7":
        print("Capturing range of Gain images...")
        for g in range(start_v, end_v, skip_v):
            output_file = "test_range_g_" + str(g) + ".jpg"
            capture_image(
                s_val,
                c_val,
                g,
                b_val,
                x_dim,
                y_dim,
                output_file,
                additonal_commands)
        print("Range captured, view and select best value...")
        os.system("gpicview test_range_g_" + str(start_v) + ".jpg")
        g_val = raw_input("Input value to use for Gain...")

    elif option == "8":
        print("Capturing range of Brightness images...")
        for b in range(start_v, end_v, skip_v):
            output_file = "test_range_b_" + str(b) + ".jpg"
            capture_image(
                s_val,
                c_val,
                g_val,
                b,
                x_dim,
                y_dim,
                output_file,
                additonal_commands)
        print("Range captured, view and select best value...")
        os.system("gpicview test_range_b_" + str(start_v) + ".jpg")
        b_val = raw_input("Input value to use for Brightness...")

    elif option == "0":
        os.system("sudo rm test_*.jpg")
        print("Images deleted")
    elif option == "t":
        print("Using current configuration to take image...")
        output_file = "test_current.jpg"
        capture_image(
            s_val,
            c_val,
            g_val,
            b_val,
            x_dim,
            y_dim,
            output_file,
            additonal_commands)
        os.system("gpicview " + output_file)
    elif option == "d":
        print("Using camera defaults to take image...")
        output_file = "test_defaults.jpg"
        # additional commands (camera select)
        cam_cmd = "sudo uvccapture " + additonal_commands
        # x and y dimensions of photo
        cam_cmd += " -x" + str(x_dim) + " -y" + str(y_dim) + " "
        cam_cmd += "-v -t0 -o" + output_file  # verbose, no delay, output
        print("---Doing: " + cam_cmd)
        os.system(cam_cmd)
        os.system("gpicview " + output_file)

    elif option == "r":
        print("Testing stability using current configuration to take range...")
        for x in range(1, 10):
            output_file = "test_range_" + str(x) + ".jpg"
            capture_image(
                s_val,
                c_val,
                g_val,
                b_val,
                x_dim,
                y_dim,
                output_file,
                additonal_commands)
        os.system("gpicview test_range_1.jpg")

    elif option == "s":
        print("Saving configuration file...")
        #  Saving config file
        config['CAMERA']['saturation'] = s_val
        config['CAMERA']['contrast'] = c_val
        config['CAMERA']['gain'] = g_val
        config['CAMERA']['brightness'] = b_val
        config['CAMERA']['x_dim'] = x_dim
        config['CAMERA']['y_dim'] = y_dim
        config['CAMERA']['additional_commands'] = additional_commands

        with open('../../config/config.ini', 'w') as configfile:
                config.write(configfile)
        print("Config Saved")

    elif option == "q" or option == "Q":
        exit()
    else:
        print("That wasn't an option...")


while True:
    show_menu()

print "Configuration complete."
