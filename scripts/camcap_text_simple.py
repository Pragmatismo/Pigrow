#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import time
import os

box_name = "Pigrow -"
temp = 9999999
humid = 9999999
rot_val = 90 #useful if your webcam is on it's side. 
t_red = 10    #0-255
t_green= 10   #0-255
t_blue = 220   #0-255
t_alpha = 255 #0-255


try:
    import Adafruit_DHT
    sensor = Adafruit_DHT.DHT22
    pin = 18
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        temp = temperature
        humid = humidity
except:
    print("Sensor software not installed")

s_val = "60"
c_val = "60"
g_val = "60"
b_val = "60"
x_dim = 1600
y_dim = 1200
additonal_commands = "-d/dev/video0 -w"
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
    print("No config file for camera, using defalt")

# take and save photo
timenow = time.time()
timenow = str(timenow)[0:10]
filename= "cap_"+str(timenow)+".jpg"
os.system("sudo uvccapture "+additonal_commands+" -S"+s_val+" -C" + c_val + " -G"+ g_val +" -B"+ b_val +" -x"+str(x_dim)+" -y"+str(y_dim)+" -v -t0 -o/home/pi/cam_caps/" + filename)


# load the image
source = Image.open("/home/pi/cam_caps/" + filename).convert('RGBA')
base = source.rotate(rot_val)

timeofpic = float(timenow)
time_text = str(time.strftime('%H:%M %d-%b-%Y', time.localtime(timeofpic)))

txt = Image.new('RGBA', base.size, (255,255,255,0))
fnt = ImageFont.truetype('/home/pi/Pigrow/scripts/Caslon.ttf', 55)
d = ImageDraw.Draw(txt)

temp = str(temp)[0:4]
humid = str(humid)[0:4]

d.text((10,10), box_name, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((10,70), time_text, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((10,120), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((10,170), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))

out = Image.alpha_composite(base, txt)
out.save("/home/pi/cam_caps/text_" + filename)
print("Modified image saved to /home/pi/cam_caps/text_" + filename)
#os.system("rm cap_"+filename+".jpg") #removes un modified jpg

