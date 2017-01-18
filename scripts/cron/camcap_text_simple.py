#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import time
import os

sys.path.append('/home/pi/Pigrow/scripts/')
sys.path.append('/home/pi/Pigrow/scripts/cron/')
import pigrow_defs
import camcap
script = 'temp_graph.py'
loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
loc_dic = pigrow_defs.load_locs(loc_locs)
graph_path = loc_dic['graph_path']
graph_path = graph_path + "dht_temp_graph.png"
log_location = loc_dic['loc_dht_log']
loc_settings = loc_dic['loc_settings']
set_dic = pigrow_defs.load_settings(loc_settings)

box_name = "Pigrow -"  #needs to use settings file
sensor_gpio = 18   #need to use settings file
caps_path = "/home/pi/Pigrow/cam_caps/"

rot_val = 90 #useful if your webcam is on it's side.
t_red = 10    #0-255 text colour
t_green= 10   #0-255 text colour
t_blue = 220   #0-255 text colour
t_alpha = 255 #0-255 text opacity
font_name = '/home/pi/Pigrow/resources/Caslon.ttf'
font_size = 55
rmfile = True  #if True then removes the unannotated image set to False to keep them

temp = 9999999
humid = 9999999
try:
    import Adafruit_DHT
    sensor = Adafruit_DHT.DHT22
    pin = sensor_gpio
    count = 0
    while humidity == None and count <= 5:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        count = count + 1
    if humidity is not None and temperature is not None:
        temp = temperature
        humid = humidity
except:
    print("Sensor software not installed")

#-------------------

s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path = camcap.load_camera_settings(loc_dic)
caps_path, filename = camcap.take_with_uvccapture(s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands, caps_path)

# load the image
source = Image.open(caps_path + filename).convert('RGBA')
base = source.rotate(rot_val)
timeofpic = float(str(filename).split("_")[1].split(".")[0])
time_text = str(time.strftime('%H:%M %d-%b-%Y', time.localtime(timeofpic)))

txt = Image.new('RGBA', base.size, (255,255,255,0))
fnt = ImageFont.truetype(font_name, font_size)
d = ImageDraw.Draw(txt)

#temp = temp.round()
#humid = humid.round()
temp = str(temp)[0:4]
humid = str(humid)[0:4]

d.text((800,10), box_name, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((800,70), time_text, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((800,120), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((800,170), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))

out = Image.alpha_composite(base, txt)
out.save(caps_path + "text_" + filename)
print("Modified image saved to " + caps_path + "text_" + filename)
if rmfile == True:
    os.system("rm " + caps_path + filename + " -f" ) #removes un modified jpg, -f means it doesn't ever prompt for user input
