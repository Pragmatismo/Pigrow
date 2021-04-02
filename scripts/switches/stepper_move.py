#!/usr/bin/python3
import sys, os
import time
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
import RPi.GPIO as GPIO

# motor control functions
def advance_step(pins, steps, delay):
    for i in range(0, steps):
        set_step(1,0,1,0, pins)
        time.sleep(delay)
        set_step(0,1,1,0, pins)
        time.sleep(delay)
        set_step(0,1,0,1, pins)
        time.sleep(delay)
        set_step(1,0,0,1, pins)
        time.sleep(delay)

def reverse_step(pins, steps, delay):
    for i in range(0, steps):
        set_step(1,0,0,1, pins)
        time.sleep(delay)
        set_step(0,1,0,1, pins)
        time.sleep(delay)
        set_step(0,1,1,0, pins)
        time.sleep(delay)
        set_step(1,0,1,0, pins)
        time.sleep(delay)

def set_step(w_a0, w_a1, w_b0, w_b1, pins):
    GPIO.output(pins[0], w_a0)
    GPIO.output(pins[1], w_a1)
    GPIO.output(pins[2], w_b0)
    GPIO.output(pins[3], w_b1)

# activity function
def move_stepper(set_dic, switch_log):
    script = 'stepper_move.py'
    msg = ("")
    msg +=("      #############################################\n")
    msg +=("      ##        Moving the stepper motor         ##\n")
    # read stepper gpio settings
    a0, a1, b0, b1 = "","","",""
    stepper_pin_key = "stepper_" + stepper_name
    if not stepper_pin_key in set_dic:
        pigrow_defs.write_log(script, 'Failed - no stepper gpio set in config', switch_log)
        return ("No stepper pins set in config file")
    gpio_pins = set_dic[stepper_pin_key].split(",")
    for item in gpio_pins:
        key, value = item.split(":")
        if key == "a0":
            a0 = int(value)
        elif key == "a1":
            a1 = int(value)
        elif key == "b0":
            b0 = int(value)
        elif key == "b1":
            b1 = int(value)
    # check settings
    if a0 == "" or a1 == "" or b0 == "" or b1 == "":
        pigrow_defs.write_log(script, 'Failed - gpio set incorrectly in config', switch_log)
        return ("Gpio set incorrectly in config")
    pins = [a0, a1, b0, b1]

    # activate pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(a0, GPIO.OUT)
    GPIO.setup(a1, GPIO.OUT)
    GPIO.setup(b0, GPIO.OUT)
    GPIO.setup(b1, GPIO.OUT)
    # move the motor
    print (" Moving stepper ", move_steps, " with delay of ", delay)
    if move_steps > 0:
        advance_step(pins, move_steps, delay)
    else:
        reverse_step(pins, abs(move_steps), delay)
    msg = 'Stepper moved ' + str(move_steps) + " with delay " + str(delay)
    pigrow_defs.write_log(script, 'stepper moved ', switch_log)
    return msg

if __name__ == '__main__':

    stepper_name = None
    move_steps = None
    delay = 0.01
    # command line arguements
    for argu in sys.argv[1:]:
        if argu == '-h' or argu == '--help':
            print("Pigrow Stepper Moving")
            print("")
            print("This moves a stepper motor using an L298N or similar H-bridge controller")
            print("")
            print("To use this program you must have the devices GPIO pins")
            print("set in the pigrow configuration file /config/pigrow_config.txt")
            print("use the setup tool in the remote gui to add the line")
            print("stepper_NAME=a0:gpionum,a1:gpionum,b0:gpionum,b1:gpionum")
            sys.exit()
        elif argu == '-flags':
            print("name=")
            print("move_steps=int")
            print("delay=0.01")
            sys.exit()
        if "=" in argu:
            try:
                thearg = str(argu).split('=')[0]
                theval = str(argu).split('=')[1]
                if thearg == 'name':
                    stepper_name = theval
                elif thearg == 'move_steps' or thearg == "steps" or thearg == "s" or thearg == "move":
                    move_steps = int(theval)
                elif thearg == 'delay' or thearg == "d":
                    delay = float(theval)
            except:
                print(" Failed to understand setting ", argu)

    if stepper_name == None or move_steps == None:
        print(" Requires name and move_steps value")
        print(" name=motor1 move_steps=10")
        sys.exit()
    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    msg = move_stepper(set_dic, loc_dic['loc_switchlog'])
    print (msg)
