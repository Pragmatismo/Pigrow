#!/usr/bin/python3
import os
import sys
import time
import subprocess
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = "blink_led.py"
dirlocs_path = homedir + "/Pigrow/config/dirlocs.txt"
loc_dic = pigrow_defs.load_locs(dirlocs_path)

def read_config(name):
    '''
      to make this more efficent and as i only need one line i should probably
      just use grep instead of importing pigrow_defs, though error logging is important i guess?
    '''
    # load settings dict
    if os.path.isfile(dirlocs_path):
        set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    else:
        print("Unable to read config details, dirlocs or pigrow_config may not exist or be corrupt")
        sys.exit()
    # find gpio number
    loc_key = "led_" + name + "_loc"
    if loc_key in set_dic:
        gpio = set_dic["led_" + name + "_loc"]
    else:
        print(loc_key, "not set in pigrow_config.txt, this should be set to the gpio number")
        pigrow_defs.write_log(script, 'LED ' + name + "called but no gpio set in pigrow_setting.txt", loc_dic['err_log'])
        sys.exit()
    return gpio

def read_speed(speed):
    # break string into two values
    if ":" in speed:
        try:
            on, off = speed.split(":")
        except:
            fail_speed()
    else:
        on, off = speed, speed
    # convert to numbers
    try:
        on  = int(on)  / 1000
        off = int(off) / 1000
    except:
        fail_speed()
    return on, off

def fail_speed():
    print("Speed setting was not valid numbers, e.g.")
    print("           speed=500")
    print("           speed=500:1000")
    pigrow_defs.write_log(script, 'unable to understand speed=' + str(speed), loc_dic['err_log'])
    sys.exit()

def kill_clones(name):
    script_path = homedir + "/Pigrow/scripts/persistent/blink_led.py"
    cmd = "pidof -x " + str(script_path)
    pid_text = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    pid_text = pid_text.stdout.strip()
    our_pid = str(os.getpid())
    if pid_text == our_pid:
        print("only this one running")
        return None
    # make list of  pids
    if " " in pid_text:
        pids = pid_text.split(" ")
    else:
        pids = [pid_text]
    # check list for name=NAME
    named_list = []
    for pid in pids:
        if not pid == our_pid:
            cmd = "ps -fp " + pid
            stdout = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if "name=" + name + " " in stdout.stdout + " ":
                named_list.append(pid)
    # kill processes
    for pid in named_list:
        cmd = "kill " + pid
        subprocess.run(cmd, shell=True)


def blink_led(gpio, on, off):
    # set up pin
    GPIO.setup(gpio, GPIO.OUT)
    # loop until someone kills the script
    while true:
        GPIO.output(gpio, GPIO.HIGH)
        time.sleep(on)
        GPIO.output(gpio, GPIO.LOW)
        time.sleep(off)

if __name__ == '__main__':
    name = ""
    speed = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'name':
                name = thevalue.strip()
            if thearg == "speed":
                speed = thevalue.lower().strip()

        elif 'help' in argu or argu == '-h':
            print(" blinks a named LED")
            print(" this script is designed to be called by ")
            print("          triggers/set_led.py")
            print(" ")
            print(" name=LED_NAME    name as set in pigrow_config.txt")
            print(" speed=ON:OFF     time in ms")
            print("                  if : is omitted both are equal value")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("name=LED NAME")
            print("speed=ON ms:OFF ms")
            sys.exit(0)

    if not name == "":
        if not speed == "":
            gpio = read_config(name)
            on, off = read_speed(speed)
            kill_clones(name)
            blink_led(gpio, on, off)
        else:
            print("requires arg speed=")
            print("   e.g. speed=500")
            print("        speed=500:1000")
    else:
        print("requires arg name=LED_NAME same as in pigrow_config.txt")
