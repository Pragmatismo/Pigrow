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
caps_path = loc_dic['caps_path']
box_name = set_dic['box_name']
try:
    dht22_sensor_pin = set_dic['gpio_dht22sensor']   #need to use settings file
except:
    print("No sensor pin set...")
    dht22_sensor_pin = None
if dht22_sensor_pin.strip() == "":
    dht22_sensor_pin = None



rot_val = 90 #useful if your webcam is on it's side.
t_red = 220    #0-255 text colour
t_green= 220   #0-255 text colour
t_blue = 220   #0-255 text colour
t_alpha = 255 #0-255 text opacity
font_name = loc_dic['path'] + '/resources/Caslon.ttf'
font_size = 55
leftdist = 3 # percentage left of image to start text
downdist = 4 # [ercentage down the image to start test]
rmfile = True  #if True then removes the unannotated image set to False to keep them
show_anyway = "blank" #set to 'text' or 'num' to show sensor data even when none readings
                     #     -this stops anoying blinking if sensor isn't reliable
nulsensorshow=False #when True shows sensor even when it's not enabled, when False hides sensors not enabled in settings
                    #       -if it stil shows it means it's got a gpio address listed but no sensor connected
                    #        in this case set show_anyway to false.

#get the current sensor data using adafruits's dht module
# -this shoul be swapped out into a module...
temp = "99999"
humid = "99999"
if not dht22_sensor_pin == None:
    try:
        import Adafruit_DHT
    except:
        print("sensor software not installed")
    try:
        sensor = Adafruit_DHT.DHT22
        count = 0
        while count <= 5:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, int(dht22_sensor_pin))
            if humidity == None:
                count = count + 1
            else:
                break
            print("failed to read sensor")
        if humidity is not None and temperature is not None:
            temp = temperature
            humid = humidity
        else:
            print("no reading from sensor...")
    except:
        print("error while trying to read sensor")
        raise
else:
    print("Skipping reading sensor...")

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
xpos = base.size[0] / 100 * leftdist
ypos = base.size[1] / 100 * downdist

d.text((xpos-1, ypos-1), box_name, font=fnt, fill=(0,0,0,t_alpha))
d.text((xpos,ypos), box_name, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
d.text((xpos-1, ypos+font_size-1), time_text, font=fnt, fill=(0,0,0,t_alpha))
d.text((xpos,ypos+font_size), time_text, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))

if not dht22_sensor_pin == None or nulsensorshow==True:
    if not temp == "99999":
        temp = str(round(temp,2))
        humid = str(round(humid,2))
        d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
    elif temp == "99999" and show_anyway == "num":
        d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*2)), "Temp: " + temp, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: " + humid, font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
    elif temp == "99999" and show_anyway == "text":
        d.text((xpos,ypos+(font_size*2)), "Temp: no data", font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: no data", font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*2)), "Temp: no data", font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: no data", font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
    elif temp == "99999" and show_anyway == "blank":
        d.text((xpos,ypos+(font_size*2)), "Temp: ", font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: ", font=fnt, fill=(0,0,0,t_alpha))
        d.text((xpos,ypos+(font_size*2)), "Temp: ", font=fnt, fill=(t_red,t_green,t_blue,t_alpha))
        d.text((xpos,ypos+(font_size*3)), "Humid: ", font=fnt, fill=(t_red,t_green,t_blue,t_alpha))


#save image to filesystem
out = Image.alpha_composite(base, txt)
out.save(caps_path + "text_" + filename)
print("Modified image saved to " + caps_path + "text_" + filename)
if rmfile == True:
    os.system("rm " + caps_path + filename + " -f" ) #removes un modified jpg, -f means it doesn't ever prompt for user input
    print(" - Original cap file discarded")
