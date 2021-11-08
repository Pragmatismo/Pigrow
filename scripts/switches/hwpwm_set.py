#!/usr/bin/python3
import datetime, sys, os
import pigpio

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
script = 'hwpwm_set.py'
import pigrow_defs

def check_command_line_args():
    """
    Check the system command line for settings information
    """
    name   = ""
    value  = ""
    freq   = ""
    pin    = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            key = argu.split("=")[0].lower()
            val = argu.split("=")[1]

            if key == 'name':
                name = val
            elif key == 'value':
                value = val
            elif key == 'pin':
                pin = val
            elif key == 'freq':
                freq = val

        elif argu == '-h' or argu == '--help':
            print("   Hardware PWM switch")
            print(" This triggers the pigpio demon")
            print("")
            print("   name=  ")
            print("   value= percentage to set pwm to")
            print("   freq=  PWM freqience in Hz")
            print("   pin=  gpio pin number")
            print("         must be a viable hw pwm pin")
            print("         e.g. 18, 19, 12, or 13 ")
            print("")
            sys.exit()

        elif argu == '-flags':
            print("name=")
            print("value=")
            print("freq=")
            print("pin=")
    return name, value, freq, pin


def hwpwm_switch(name, pin, freq, value, switch_log):

    duty_cycle = int(float(value) * 10000)

    pi = pigpio.pi()
    pi.hardware_PWM(pin, freq, duty_cycle)

    log_msg = "Set " + name + " to " + str(value)
    pigrow_defs.write_log(script, log_msg, switch_log)


def read_from_settings(name):
    #msg =(" PCA9685 \n")
    name_pin  = "hwpwm_" + name + "_loc"
    name_freq = "hwpwm_" + name + "_freq"

    if name_pin in set_dic and name_freq in set_dic:
        pin  = set_dic[name_i2c]
        freq = set_dic[name_freq]
        if not pin == "":
            return pin, freq
        else:
            return "", ""
    else:
        return "", ""


if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    name, value, freq, pin = check_command_line_args()

    s_freq = ""
    if not name == "":
        pin, s_freq = read_from_settings(name)
    else:
        name = "pin " + str(pin)
        if pin == "":
            print("Must set name= or pin=")
            sys.exit()

    if pin == "":
        print("pin for " + name + " not set in " + loc_dic['loc_settings'])

    if freq == "":
        if s_freq == "":
            print(" - Using default frequency of 150000 Hz")
            freq = "20000"
        else:
            freq = s_freq

    if value == "":
        print(" no value set, use value= to set a power level percentage")
        sys.exit()

    hwpwm_switch(name, int(pin), int(freq), value, loc_dic['loc_switchlog'])
