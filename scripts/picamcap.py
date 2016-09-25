#!/usr/bin/python
import time 
import os

#s_val = "60" c_val = "60" g_val = "60" b_val = "60" x_dim = 1600 y_dim = 
 
extra_commands = "" #"-vf " 
path = "/home/pi/batttest/"
  
# take and save photo
#timenow = time.time() 
timenow = str(time.time())[0:10] 
filename= "cap_"+str(timenow)+".jpg" 
os.system("raspistill -o "+path+filename+" "+extra_commands)

print("Image taken and saved to "+path+filename)
