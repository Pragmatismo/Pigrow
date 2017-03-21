#!/usr/bin/python
import os
import sys
import numpy
from PIL import Image

cappath = '/home/pi/Pigrow/caps/'
logpath = '/home/pi/Pigrow/logs/caps_log.txt'

for argu in sys.argv[1:]:
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
line = str(r_sum) + '>' + str(g_sum) + '>' + str(b_sum) + '>' + str(tot_sum) + '\n'
with open(logpath, "a") as f:
    f.write(line)
print("Log written; " + str(logpath))
