import os, sys, time, datetime
from gpiozero import Button

button_name = None
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'log' or thearg == 'name':
            button_name = thevalue
    elif 'help' in argu or argu == '-h':
        print(" Script for logging the duration of button presses")
        print(" ")
        print(" This requres the button to be configured in the remote gui.")
        print(" ")
        print(" name=button unique name")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("name=")
        sys.exit(0)

# Read the settings file
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
    script = 'button_watcher.py'
except:
    print("pigrow_defs.py not found, unable to continue.")
    print("make sure pigrow software is installed correctly")
    sys.exit()
loc_dic = pigrow_defs.load_locs(homedir + '/Pigrow/config/dirlocs.txt')
pigrow_settings = pigrow_defs.load_settings(loc_dic['loc_settings'])

# Read the sensor info from the settigns file
button_type = None
button_log = None
button_loc = None
for key, value in list(pigrow_settings.items()):
    button_key = "button_" + button_name
    if button_key in key:
        if "type" in key:
            button_type = value
        elif "log" in key:
            button_log = value
        elif "loc" in key:
            button_loc = value

if button_type == None or button_log == None or button_loc == None:
    err_msg = "Button settings not found in " + loc_dic['loc_settings']
    print(err_msg)
    pigrow_defs.write_log('log_sensor_module.py', err_msg, loc_dic['err_log'])
    sys.exit()



def listen(gpio_num, log_path, *args):
    button = Button(gpio_num)

    def pressed():
         #print( " Button Pressed " )
         listen.press_start = time.time()

    def released():
        #print( " Button released " )
        listen.press_end = time.time()

    button.wait_for_press()
    pressed()
    button.wait_for_release()
    released()
    duration = listen.press_end - listen.press_start
    print(duration)
    log_button_presss(log_path, duration)

def log_button_presss(log_path, duration):
    timenow = str(datetime.datetime.now())
    line = "time=" + str(timenow)
    line += ">duration=" + str(duration) + "\n"
    with open(log_path, "a") as f:
        f.write(line)
    print("Written; " +  line)

if button_type == "gnd":
    while True:
        listen(button_loc, button_log)
else:
    print("Sensor type not recognised, currently only 'gnd' is supported.")
