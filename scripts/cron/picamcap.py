#!/usr/bin/python
import time
import os, sys
try:
    from picamera import PiCamera
except:
    print("Picamera is not installed, is this even a raspberry pi?!")
    exit()

homedir = os.getenv("HOME")
settings_file = homedir + "/Pigrow/config/picam_settings.txt" # default changed with argu settings
caps_path = None

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
    return filename

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

if __name__ == '__main__':
    sys.path.append(homedir + '/Pigrow/scripts/')
    script = 'picamcap.py'
    import pigrow_defs
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    caps_path = set_caps_path(loc_dic, caps_path)
    picam_dic = load_picam_set(setloc=settings_file)
    filename = take_picam_py(picam_dic, caps_path)
    #filename = take_picam_raspistill(picam_dic, caps_path)
    print("Image taken and saved to "+caps_path+filename)
