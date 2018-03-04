#!/usr/bin/python
import os
import sys
import numpy
from PIL import Image

homedir = os.getenv("HOME")
cappath = homedir + '/Pigrow/caps/'
logpath = homedir + '/Pigrow/logs/caps_log.txt'

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Script for logging the pixel values of the most ")
        print("recent image in a folder, for best use call directly")
        print("adter taking an image. Use an sh script to do this.")
        print("")
        print(" caps=<folderpath>")
        print("     folder to find most recent image from")
        print(" log=<filepath>")
        print("    file to append data into")
        sys.exit(0)
    try:
        thearg = str(argu).split('=')[0]
    except:
        thearg = str(argu)
    if thearg == 'cap' or thearg =='caps':
        cappath = str(argu).split('=')[1]
    elif thearg == 'l' or thearg == 'log':
        logpath = str(argu).split('=')[1]

os.chdir(cappath)
c_photo = max(os.listdir('.'), key = os.path.getctime)

pil_c_photo = Image.open(c_photo)
numpy_pic = numpy.array(pil_c_photo)
r_sum = numpy_pic[:,:,0].sum()
g_sum = numpy_pic[:,:,1].sum()
b_sum = numpy_pic[:,:,2].sum()
tot_sum = r_sum + g_sum + b_sum

print " ---- Image Analysis, super basic version ---"
print c_photo
print "Red:" + str(r_sum)
print "Green:" + str(g_sum)
print "Blue:" + str(b_sum)
print "Total;" + str(tot_sum)
line = str(r_sum) + '>'
line += str(g_sum) + '>'
line += str(b_sum) + '>'
line += str(tot_sum) + '>'
line += str(c_photo) + '\n'
with open(logpath, "a") as f:
    f.write(line)
print("Log written; " + str(logpath))
