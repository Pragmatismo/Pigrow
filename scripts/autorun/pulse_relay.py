#!/usr/bin/env python3
import sys, os
import time
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import atexit
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


device = ""
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'device':
            device = theval
    elif argu == '-h' or argu == '--help':
        print("Pigrow relay pulse control")
        print("")
        print("This turns the power on and off for set durations in an eternal loop")
        print("")
        print("To use this program you must have the devices GPIO and wiring direction")
        print("set in the pigrow configuration file /config/pigrow_config.txt")
        print("You can use the remote gui to do this simply")
        print("")
        print("You must spesify the device to control using device=device name")
        print("")
        print(" pigrow_config.txt must contain the line pulse_[device name]=x:y")
        print("                                                 x = on duration")
        print("                                                 y = off duration")
        print("    =10:10 will turn on for ten seconds then off for ten seconds")
        print("    =1:0   will set it to steady on")
        print("    =0:1   will set it to steady off")
        sys.exit()
    elif argu == "-flags":
        print("device=")
        print("")
        sys.exit()
if device == "":
    print(" You need to set a device to control using device=device name")
    sys,exit()

class config:
    def __init__(self):
        config.on_duration = 0
        config.off_duration = 0
        config.gpio_pin, config.gpio_pin_on = config.load_settings()


    def load_settings():
        setting_path = homedir + "/Pigrow/config/pigrow_config.txt"
        if os.path.isfile(setting_path):
            set_dic = pigrow_defs.load_settings(setting_path)
        gpio_pin = ""
        gpio_pin_on = ""
        if 'gpio_' + device in set_dic:
            if not str(set_dic['gpio_' + device]).strip() == '':
                gpio_pin = int(set_dic['gpio_' + device])
                gpio_pin_on = set_dic['gpio_' + device + '_on']
                GPIO.setup(gpio_pin, GPIO.OUT)
        if 'pulse_' + device in set_dic:
            if not str(set_dic['pulse_' + device]).strip() == '':
                pulse = set_dic['pulse_' + device]
                try:
                    config.on_duration  = int(pulse.split(":")[0])
                    config.off_duration = int(pulse.split(":")[1])
                except:
                    print("pulse_" + device + "= needs to be set as on_time:off_time in pigrow_config.txt")
                    config.on_duration = 0
                    config.off_duration = 0
            else:
                print("pulse_" + device + "= needs to be set with on_time:off_time in pigrow_config.txt")
                config.on_duration = 0
                config.off_duration = 0
        else:
            print("pigrow_config.txt needs to have pulse_" + device + "= set with on_time:off_time")
            config.on_duration = 0
            config.off_duration = 0
        return gpio_pin, gpio_pin_on


def device_on():
    if config.gpio_pin_on == "low":
        GPIO.output(config.gpio_pin, GPIO.LOW)
    elif config.gpio_pin_on == "high":
        GPIO.output(config.gpio_pin, GPIO.HIGH)

def device_off():
    if config.gpio_pin_on == "high":
        GPIO.output(config.gpio_pin, GPIO.LOW)
    elif config.gpio_pin_on == "low":
        GPIO.output(config.gpio_pin, GPIO.HIGH)

def config_change(event):
    if "pigrow_config.txt" in event.src_path:
        print("reloading_config")
        config.gpio_pin, config.gpio_pin_on = config.load_settings()

def observe_config_file():
    print(" - Enabling Config File Observation")
    path = homedir + "/Pigrow/config/"
    print(path)
    conf_events_handler = PatternMatchingEventHandler("*.txt", "", True, False)
    conf_events_handler.on_created = config_change
    conf_events_handler.on_modified = config_change
    conf_events_ob = Observer()
    conf_events_ob.schedule(conf_events_handler, path, recursive=True)
    conf_events_ob.start()

if __name__ == '__main__':
    config()
    observe_config_file()
    atexit.register(device_off)
    steady = ""
    while True:
        if not config.on_duration == 0 and not config.off_duration == 0:
            device_on()
            time.sleep(config.on_duration)
            device_off()
            time.sleep(config.off_duration)
            steady = ""
        elif not config.on_duration == 0 and config.off_duration == 0:
            if not steady == "on":
                print(" Steady on")
                device_on()
                steady = "on"
            time.sleep(1)
        else:
            if not steady == "off":
                print(" Steady off")
                device_off()
                steady = "off"
            time.sleep(1)
