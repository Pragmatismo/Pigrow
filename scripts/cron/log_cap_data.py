#!/usr/bin/python3
import os
import sys
import numpy
import datetime
from PIL import Image
focus_check = True
try:
    import cv2
except:
    print("cv2 module not installed or not working, skipping focus check")
    print("")
    print(" To install cv2 use;")
    print("   sudo pip3 install opencv-python")
    print("   sudo apt-get install libatlas-base-dev")
    focus_check = False

homedir = os.getenv("HOME")
cappath = homedir + '/Pigrow/caps/'
logpath = homedir + '/Pigrow/logs/caps_log.txt'
image_to_process = None # set as None so we know not to look if the user
                         # sets it with a command line argument

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Script for logging the pixel values of the most ")
        print("recent image in a folder, for best use call directly")
        print("after taking an image. Use an sh script to do this.")
        print("")
        print(" folder=<folderpath>")
        print("     folder to find most recent image from")
        print(" log=<filepath>")
        print("    file to append data into")
        print(" focus=false")
        print("    skip the focus check")
        sys.exit(0)
    if argu == '-flags':
        print("folder=" + cappath)
        print("log=" + logpath)
        print("image=")
        print("focus=")
        sys.exit(0)
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if thearg == 'cap' or thearg =='caps' or thearg == 'folder':
            cappath = str(argu).split('=')[1]
        elif thearg == 'l' or thearg == 'log':
            logpath = str(argu).split('=')[1]
        elif thearg == 'image':
            image_to_process = theval
        elif thearg == 'focus':
            if theval.lower() == 'false':
                focus_check = False

def find_most_recent(cappath):
    os.chdir(cappath)
    c_photo = max(os.listdir('.'), key = os.path.getctime)
    return c_photo

def get_pixel_values(c_photo):
    '''
    This simlpy adds up all the red, green and blue pixel values in the image.
    '''
    pil_c_photo = Image.open(c_photo)
    numpy_pic = numpy.array(pil_c_photo)
    r_sum = numpy_pic[:,:,0].sum()
    g_sum = numpy_pic[:,:,1].sum()
    b_sum = numpy_pic[:,:,2].sum()
    tot_sum = r_sum + g_sum + b_sum
    print("Pixel Values of; " + str(c_photo))
    print("Red:" + str(r_sum))
    print("Green:" + str(g_sum))
    print("Blue:" + str(b_sum))
    print("Total;" + str(tot_sum))
    return r_sum, g_sum, b_sum, tot_sum

def get_cv_focus(image_to_process):
    '''
    This looks at each line of the image and adds up the amount of sharp edges
    when looking at the same subject higher numbers will tend to mean a more infocus image
    though this is very much just a test at this stage.
    '''
    image = cv2.imread(image_to_process)
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #
    def px(x, y):
        return int(gray[y, x])
    # cycle through vertical lines compairing focus
    sum = 0
    for x in range(width-1):
        for y in range(height):
            sum += abs(px(x, y) - px(x+1, y))
    print("Focus: " + str(sum))
    return sum


def log_pixel_values(logpath, r_sum, g_sum, b_sum, tot_sum, focus, image_to_process):

    line = "date=" + str(datetime.datetime.now()) + ">"
    line += "r=" + str(r_sum) + '>'
    line += "g=" + str(g_sum) + '>'
    line += "b=" + str(b_sum) + '>'
    line += "total=" + str(tot_sum) + '>'
    line += "focus=" + str(focus) + ">"
    line += "image=" + str(image_to_process) + '\n'
    with open(logpath, "a") as f:
        f.write(line)
    print("Log written; " + str(logpath))



#
# main program which runs unless we've imported this as a module via another script
#
if __name__ == '__main__':
    print(" ---- Image Analysis, super basic version ---")
    #if user didn't sepesify a file to ues select most recent from caps folder
    if image_to_process == None:
        image_to_process = find_most_recent(cappath)
        #print(" Using image: " + image_to_process)
    #collect pixel values for the image
    r,g,b,t = get_pixel_values(image_to_process)
    if focus_check == True:
        focus = get_cv_focus(image_to_process)
    else:
        focus = "unset"
    #save into log file
    log_pixel_values(logpath, r,g,b,t, focus, image_to_process)
