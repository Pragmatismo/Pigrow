#!/usr/bin/env python3
#Flags output enabled
import os
import sys
import subprocess
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = "set_led.py"
config_path = homedir + "/Pigrow/config/pigrow_config.txt"
err_path    = homedir + "/Pigrow/logs/err_log.txt"

def read_config(name):
    if os.path.isfile(config_path):
        set_dic = pigrow_defs.load_settings(config_path, err_log=err_path)
    else:
        print("Unable to read config details, pigrow_config may not exist or be corrupt")
        sys.exit()

    loc_key = "led_" + name + "_loc"
    if loc_key in set_dic:
        gpio = set_dic["led_" + name + "_loc"]
    else:
        print(loc_key, "not set in pigrow_config.txt, this should be set to the gpio number")
        pigrow_defs.write_log(script, 'LED ' + name + "called but no gpio set in pigrow_setting.txt", err_path)
        sys.exit()

    onboot_key = "led_" + name + "_reboot"
    if onboot_key in set_dic:
        onboot = set_dic[onboot_key]
    else:
        print("reboot flag not set in pigrow_config, assuming you want it on.")
        onboot = "true"

    return gpio, onboot

def kill_blink(name):
    script_path = homedir + "/Pigrow/scripts/persistent/blink_led.py"

    # 1) Try the old pidof -x <script_path>
    p = subprocess.run(
        ["pidof", "-x", script_path],
        capture_output=True, text=True
    )
    pid_text = p.stdout.strip()

    # 2) If nothing found, fall back to pgrep -f <script_path>
    if not pid_text:
        p2 = subprocess.run(
            ["pgrep", "-f", script_path],
            capture_output=True, text=True
        )
        pid_text = p2.stdout.strip()

    if not pid_text:
        # no processes running for that script
        return

    # 3) Split into a list of PIDs
    pids = pid_text.split()

    # 4) Filter by the command-line argument name=<name>
    named_pids = []
    for pid in pids:
        ps = subprocess.run(
            ["ps", "-fp", pid],
            capture_output=True, text=True
        )
        # add trailing space so we catch "name=foo " even if at end
        if f"name={name} " in ps.stdout + " ":
            named_pids.append(pid)

    # 5) Kill each matching PID
    for pid in named_pids:
        subprocess.run(["kill", pid])


def set_led_solid(mode, gpio):
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio, GPIO.OUT)
    if mode == 'on':
        GPIO.output(gpio, GPIO.HIGH)
        print("LED set to on")
    elif mode == 'off':
        GPIO.output(gpio, GPIO.LOW)
        print("LED set to off")

def set_led_blink(name, mode, gpio):
    mode_dict = {'blink':'500',
                 'slow':'1000',
                 'fast':'100',
                 'dash':'250:1000'}
    if mode in mode_dict:
        speed = mode_dict[mode]
    elif 'time:' in mode:
        speed = mode.replace('time:', "")
    else:
        print("set= is not a valid option")
        print("     set=blink")
        print("     blink, slow, fast, dash, time:500:2000")
        sys.exit()
    cmd = "nohup " + homedir + "/Pigrow/scripts/persistent/blink_led.py" + " name=" + name + " speed=" + speed + " > /dev/null 2>&1 &"
    subprocess.Popen(cmd, shell=True)
    print("Set LED" + name + " to blink at speed " + speed)

def write_onboot(name, made):
    led_stat_path = homedir + "/Pigrow/logs/ledstat_" + name + ".txt"
    ledstat_txt = "mode=" + made
    with open(led_stat_path, "w") as f:
        f.write(ledstat_txt)
    print(" Written;")
    print(ledstat_txt, "to", led_stat_path)

def remove_state_file(name):
    if name == "":
        return None
    homedir = os.getenv("HOME")
    led_stat_path = homedir + "/Pigrow/logs/ledstat_" + name + ".txt"
    if os.path.isfile(name):
        os.system('rm ' + led_stat_path)
        print("Removed obsolete", led_stat_path)

def list_leds(as_list=False):
    config_path = homedir + "/Pigrow/config/pigrow_config.txt"
    set_dic = pigrow_defs.load_settings(config_path, err_log=err_path)
    led_list = []
    for item in set_dic:
        if "led_" in item:
            name = item.split("_")[1]
            if name not in led_list:
                led_list.append(name)
    if len(led_list) == 0:
        print("No LEDs found in pigrow_setting.txt")
    else:
        if as_list == False:
            print(" Found", len(led_list), "available LEDs")
            for item in led_list:
                print(item)
        else:
            msg = ""
            for item in led_list:
                msg += item + ","
            return msg[:-1]

if __name__ == '__main__':
    name = ""
    mode = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'name':
                name = thevalue
            if thearg == "set":
                mode = thevalue.lower()

        elif 'help' in argu or argu == '-h':
            print(" Set ta a named LED to a new state")
            print("")
            print(" ")
            print(" name=led name")
            print(" set=    on")
            print("         off")
            print("         slow")
            print("         blink")
            print("         fast")
            print("         dash")
            print("         time:ON time ms:OFF time ms")
            print("              duration of blink")
            print("              if off ommited they're even")
            print("")
            print(" When any type of blink is set this script will start a ")
            print(" second background script which controls the blinking. ")
            print(" ")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("name=[" + list_leds(as_list=True) + "]")
            print("set=[on, off, slow, blink, fast, dash, time:ON:OFF]")
            sys.exit(0)
        elif argu == "-defaults":
            print("name=")
            print("set=")
            sys.exit(0)

    if not name=="":
        if not mode == "":
            gpio, onboot = read_config(name)
            # gpio to int
            try:
                gpio = int(gpio)
            except:
                print("listed gpio pin is not a valid number, check pigrow_config.txt")
                sys.exit()
            # select mode
            if mode == 'on' or mode == 'off':
                kill_blink(name)
                set_led_solid(mode, gpio)
            else:
                set_led_blink(name, mode, gpio)
            # file used to reset status on reboot
            if onboot.lower() == 'true':
                write_onboot(name,mode)
            else:
                remove_state_file(name)
        else:
            print("Needs to have set= on/off/slow/blink/fast/dash/time:ON:OFF")
    else:
        print(" Need's to have name= the led as named in pigrow_config.txt")
        list_leds()
