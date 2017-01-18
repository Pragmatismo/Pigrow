#!/usr/bin/python
import time
import os, sys
try:
    from picamera import PiCamera
except:
    print("Picamera is not installed, is this even a raspberry pi?!")
    exit()

def load_picam_set(setloc="/home/pi/Pigrow/config/picam_settings.txt"):
    picam_dic = {}
    with open(setloc, "r") as f:
        for line in f:
            s_item = line.split("=")
            picam_dic[s_item[0]]=s_item[1].rstrip('\n')
    return picam_dic

def take_picam_py(picam_dic, caps_path):
    # take and save photo
    timenow = str(time.time())[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    try:
        camera = PiCamera()
        #camera.resolution = (2592,1944)
        camera.resolution = (int(picam_dic['x_dim']),int(picam_dic['y_dim']))
        camera.brightness = int(picam_dic['b_val'])
        camera.contrast = int(picam_dic['c_val'])
        camera.saturation = int(picam_dic['s_val'])
        camera.iso =  int(picam_dic['g_val'])
        time.sleep(2)
        print ("resolution = " + str(camera.resolution))
        print ("analog_gain = " + str(camera.analog_gain))
        print ("digital_gain = " + str(camera.digital_gain))
        print ("iso =" + str(camera.iso))
        print ("brightness = " + str(camera.brightness))
        print ("contrast =  " + str(camera.contrast))
        print ("saturation = " + str(camera.saturation))
        print ("sharpness = " + str(camera.sharpness))
        print ("zoom = " + str(camera.zoom))
        print ("drc_strength = " + str(camera.drc_strength))
        print ("exposure_compensation = " + str(camera.exposure_compensation))
        print ("exposure_mode = " + str(camera.exposure_mode))
        print ("exposure_speed = " + str(camera.exposure_speed))
        print ("hflip = " + str(camera.hflip))
        print ("vflip = " + str(camera.vflip))
        print ("rotation = " + str(camera.rotation))
        print ("meter_mode = " + str(camera.meter_mode))
        print ("image_denoise = " + str(camera.image_denoise))
        print ("image_effect = " + str(camera.image_effect))
        print ("image_effect_params = " + str(camera.image_effect_params))
        print ("awb_mode = " + str(camera.awb_mode))
        camera.capture(caps_path+filename)
        camera.close()
        return filename
    except:
        print("Sorry, picture not taken :(")
        raise

def take_picam_raspistill(picam_dic, caps_path):
    # take and save photo
    timenow = str(time.time())[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    try:
        extra_commands = picam_dic['extra_commands']
    except:
        extra_commands = ''
    os.system("raspistill -o "+caps_path+filename+" "+extra_commands)


if __name__ == '__main__':
    sys.path.append('/home/pi/Pigrow/scripts/')
    script = 'picamcap.py'
    import pigrow_defs
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    caps_path = loc_dic["caps_path"]

    picam_dic = load_picam_set(setloc="/home/pi/Pigrow/config/picam_settings.txt")
    filename = take_picam_py(picam_dic, caps_path)
    #filename = take_picam_raspistill(picam_dic, caps_path)
    print("Image taken and saved to "+caps_path+filename)
