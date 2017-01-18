#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import time
import os, sys

sys.path.append('/home/pi/Pigrow/scripts/')
sys.path.append('/home/pi/Pigrow/scripts/cron/')
import pigrow_defs
import camcap
script = 'camcap_text_simple.py'
loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
loc_dic = pigrow_defs.load_locs(loc_locs)
loc_settings = loc_dic['loc_settings']
set_dic = pigrow_defs.load_settings(loc_settings)


box_name = set_dic['box_name']
dht22_sensor_pin = set_dic['dht22_sensor_pin']   #need to use settings file
caps_path = loc_dic['caps_path']

rot_val = 90 #useful if your webcam is on it's side.
t_red = 100    #0-255 text colour
t_green= 100   #0-255 text colour
t_blue = 220   #0-255 text colour
t_alpha = 255 #0-255 text opacity
font_name = loc_dic['path'] + '/resources/Caslon.ttf'
font_size = 55
leftdist = 3 # percentage left of image to start text
downdist = 4 # [ercentage down the image to start test]
rmfile = True  #if True then removes the unannotated image set to False to keep them
show_anyway = "text" #set to 'text' or 'num' to show sensor data even when none readings
                     #     -this stops anoying blinking if sensor isn't reliable
#get the current sensor data using adafruits's dht module
try:
    import Adafruit_DHT
    sensor = Adafruit_DHT.DHT22
    count = 0
    while humidity == None and count <= 5:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, dht22_sensor_pin)
        count = count + 1
    if humidity is not None and temperature is not None:
        temp = temperature
        humid = humidity
    else:
        print("no reading from sensor...")
        temp = None
        humid = None
except:
    print("Sensor software not installed")

#--captures image using camcap.py module
s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path = camcap.load_camera_settings(loc_dic)
caps_path, filename = camcap.take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path)

# load the image
source = Image.open(caps_path + filename).convert('RGBA')
base = source.rotate(rot_val)
timeofpic = float(str(filename).split("_")[1].split(".")[0])
time_text = str(time.strftime('%H:%M %d-%b-%Y', time.localtime(timeofpic)))

# create text layer
txt = Image.new('RGBA', base.size, (255,255,255,0))
fnt = ImageFont.truetype(font_name, font_size)
d = ImageDraw.Draw(txt)
temp = round(temp,2)
huimid = round(humid,2)
xpos = base.size[0] / 100 * leftdist
ypos = base.size[1] / 100 * downdist

d.text((xpos,ypos), box_name, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((xpos,ypos+font_size), time_text, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
if not temp == None:
    d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
    d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
elif show_anyway == "num":
        d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha/50))
        d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha/50))
elif show_anyway == "text":
        d.text((xpos,ypos+(font_size*2)), "Temp: no data", font=fnt, fill=(t_red,t_green,t_blue,t_alpha/50))
        d.text((xpos,ypos+(font_size*3)), "Humid: no data", font=fnt, fill=(t_red,t_green,t_blue,t_alpha/50))


#save image to filesystem
out = Image.alpha_composite(base, txt)
out.save(caps_path + "text_" + filename)
print("Modified image saved to " + caps_path + "text_" + filename)
if rmfile == True:
    os.system("rm " + caps_path + filename + " -f" ) #removes un modified jpg, -f means it doesn't ever prompt for user input
    print(" - Original cap file discarded")
