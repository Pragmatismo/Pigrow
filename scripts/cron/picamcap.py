#!/usr/bin/python3
import time
import os, sys
try:
    from picamera import PiCamera
except:
    print("Picamera is not installed, is this even a raspberry pi?!")
    exit()

# default settings
max_disk_percent = 95 # only fill 90% of the disk
homedir = os.getenv("HOME")
settings_file = homedir + "/Pigrow/config/picam_settings.txt" # default changed with argu settings
caps_path = None
user_filename = None

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print(" Picam capture script")
        print(" ")
        print(" this will be rewritten soon - you might need to manually edit the python code to make it do what you want")
        print("")
        print(" set=<filepath>")
        print("     choosing which settings file to use")
        print(" caps=<folder path>")
        print("     choose where to save the captured image")
        print(" filename=<file path>")
        print("     to set a spesific title, for testing without messing the caps folder")
        print(" ")
        print(" -- this script is in the process of an update, don't expect perfection --")
        sys.exit(0)
    elif argu == "-flags":
        print("settings_file=" + homedir + "/Pigrow/config/picamera_settings.txt")
        print("caps_path=" + homedir + "/Pigrow/caps/")
        sys.exit(0)
    elif "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg == 'settings_file' or thearg == 'set':
                settings_file = theval
            elif thearg == 'caps_path' or thearg == 'caps':
                caps_path = theval
            elif thearg == 'filename':
                user_filename = theval
            #elif thearg == "attempts" or thearg == "tries":
            #    try:
            #        attempts = int(theval)
            #        print("Will try " + str(attempts) + " addional times before giving up")
            #    except:
            #        print("Attempts must be a number value, using defailt")
        except:
            print("Didn't undertand " + str(argu))

def load_picam_set(setloc= homedir + "/Pigrow/config/picam_settings.txt"):
    picam_dic = {}
    with open(setloc, "r") as f:
        for line in f:
            s_item = line.split("=")
            picam_dic[s_item[0]]=s_item[1].rstrip('\n')
    return picam_dic

def display_picam_settings(camera):
    print ("  Picamera Settings")
    print ("   resolution = " + str(camera.resolution))
    print ("   analog_gain = " + str(camera.analog_gain))
    print ("   digital_gain = " + str(camera.digital_gain))
    print ("   iso =" + str(camera.iso))
    print ("   brightness = " + str(camera.brightness))
    print ("   contrast =  " + str(camera.contrast))
    print ("   saturation = " + str(camera.saturation))
    print ("   sharpness = " + str(camera.sharpness))
    print ("   zoom = " + str(camera.zoom))
    print ("   drc_strength = " + str(camera.drc_strength))
    print ("   exposure_compensation = " + str(camera.exposure_compensation))
    print ("   exposure_mode = " + str(camera.exposure_mode))
    print ("   exposure_speed = " + str(camera.exposure_speed))
    print ("   hflip = " + str(camera.hflip))
    print ("   vflip = " + str(camera.vflip))
    print ("   rotation = " + str(camera.rotation))
    print ("   meter_mode = " + str(camera.meter_mode))
    print ("   image_denoise = " + str(camera.image_denoise))
    print ("   image_effect = " + str(camera.image_effect))
    print ("   image_effect_params = " + str(camera.image_effect_params))
    print ("   awb_mode = " + str(camera.awb_mode))
    print ("   awb_gains = " + str(camera.awb_gains))
    print ("   flash_mode = " + str(camera.flash_mode))
    #print ("   color_effect = " + str(camera.color_effect))
    print ("   sensor_mode = " + str(camera.sensor_mode))

def take_picam_py(picam_dic, caps_path):
    #
    # take and save photo
    #
    #get current time and set filename
    timenow = str(time.time())[0:10]
    filename= "cap_"+str(timenow)+".jpg"
    try:
        camera = PiCamera()
        #camera.resolution = (2592,1944)
        if "x_dim" in picam_dic and "y_dim" in picam_dic:
            camera.resolution = (int(picam_dic['x_dim']),int(picam_dic['y_dim']))
        if "resolution" in picam_dic:
            x,y = picam_dic['resolution'].split("x")
            camera.resolution = (int(x),int(y))
        # old basic vals settings
        if "b_val" in picam_dic:
            camera.brightness = int(picam_dic['b_val'])
        if "c_val" in picam_dic:
            camera.contrast = int(picam_dic['c_val'])
        if "s_val" in picam_dic:
            camera.saturation = int(picam_dic['s_val'])
        if "g_val" in picam_dic:
            camera.iso =  int(picam_dic['g_val'])
        # for proper named values
        if "brightness" in picam_dic:
            camera.brightness = int(picam_dic['brightness'])
        if "contrast" in picam_dic:
            camera.contrast = int(picam_dic['contrast'])
        if "saturation" in picam_dic:
            camera.saturation = int(picam_dic['saturation'])
        if "iso" in picam_dic:
            camera.iso =  int(picam_dic['iso'])
        #
        #print ("analog_gain = " + str(camera.analog_gain))
        # optional settings
        #if "iso" in picam_dic:
        #    camera.iso = int(picam_dic['iso'])
        if "digital_gain" in picam_dic:
            camera.digital_gain = int(picam_dic['digital_gain'])
        if "sharpness" in picam_dic:
            camera.sharpness = int(picam_dic['sharpness'])
        if "zoom" in picam_dic:
            camera.zoom = picam_dic['zoom']
        if "drc_strength" in picam_dic:
            camera.drc_strength = picam_dic['drc_strength']
        if "exposure_compensation" in picam_dic:
            camera.exposure_compensation = int(picam_dic['exposure_compensation'])
        if "exposure_mode" in picam_dic:
            camera.exposure_mode = picam_dic['exposure_mode']
        if "exposure_speed" in picam_dic:
            camera.exposure_speed = int(picam_dic['exposure_speed'])
        if "hflip" in picam_dic:
            if picam_dic['hflip'] == "True":
                camera.hflip = True
            else:
                camera.hflip = False
        if "vflip" in picam_dic:
            if picam_dic['vflip'] == "True":
                camera.vflip = True
            else:
                camera.vflip = False
        if "rotation" in picam_dic:
            camera.rotation = int(picam_dic['rotation'])
        if "meter_mode" in picam_dic:
            camera.meter_mode = picam_dic['meter_mode']
        if "image_denoise" in picam_dic:
            if picam_dic['image_denoise'] == "True":
                camera.image_denoise = True
            else:
                camera.image_denoise = False
        if "image_effect" in picam_dic:
            camera.image_effect = picam_dic['image_effect']
        if "image_effect_params" in picam_dic:
            camera.image_effect_params = picam_dic['image_effect_params']
        if "awb_mode" in picam_dic:
            camera.awb_mode = picam_dic['awb_mode']
        time.sleep(2)
        display_picam_settings(camera)
        if user_filename == None:
            camera.capture(caps_path+filename)
            saved_filename = caps_path+filename
        else:
            camera.capture(user_filename)
            saved_filename = user_filename
        camera.close()
        return saved_filename
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
    if user_filename == None:
        os.system("raspistill -o "+caps_path+filename+" "+extra_commands)
        saved_filename = caps_path+filename
    else:
        os.system("raspistill -o " + user_filename + " " + extra_commands)
        saved_filename = user_filename
    return saved_filename

def set_caps_path(loc_dic, caps_path):
    # Select location to save images
    if caps_path == None:
        #check for caps path in the loctions dictionary (of dirlocs.txt)
        try:
            caps_path = loc_dic['caps_path']
        #if not then see if the default exists
        except:
            caps_path = homedir + '/Pigrow/caps/'
            if os.path.exists(caps_path):
                print("Using default folder; " + str(caps_path))
            else:
                # if not then try to create it
                try:
                    os.mkdir(caps_path)
                    print("created default folder at " + str(caps_path))
                except Exception as e:
                    # if nothing works try using the local folder instead
                    print("Couldn't create default folder at " + str(caps_path) + " resorting to local folder instead.")
                    caps_path = ""
    else:
        # i.e. if user has selected a caps path with a command line argument
        # check it exists, if no try making it if not then tell them and
        # resort to using local folder.
        if os.path.exists(caps_path):
            print("saving to; " + str(caps_path))
        else:
            try:
                os.mkdir(caps_path)
                print("created caps_path")
            except Exception as e:
                print("Couldn't create " + str(caps_path) + " using local folder instead.")
                caps_path = ""
    return caps_path


#
# System checks
#

def check_disk_percentage(caps_path):
    st = os.statvfs(caps_path)
    #free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    print("   Used " + str(percent) + "%, max limit " + str(max_disk_percent) + "%")
    if percent > max_disk_percent:
        print(" - You do not have enough space on the drive to store more images, cancelling attempt.")
        sys.exit()

if __name__ == '__main__':
    sys.path.append(homedir + '/Pigrow/scripts/')
    script = 'picamcap.py'
    import pigrow_defs
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    caps_path = set_caps_path(loc_dic, caps_path)
    check_disk_percentage(caps_path)
    picam_dic = load_picam_set(setloc=settings_file)
    filename = take_picam_py(picam_dic, caps_path)
    #filename = take_picam_raspistill(picam_dic, caps_path)
    print("Saving image to:" + filename)
