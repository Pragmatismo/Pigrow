#!/usr/bin/python3
import datetime, sys, os
import board
import busio
from adafruit_pca9685 import PCA9685
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

def check_command_line_args():
    """
    Check the system command line for settings information
    """
    name  = ""
    chan  = ""
    value = ""
    freq  = ""
    i2c   = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            key = argu.split("=")[0].lower()
            val = argu.split("=")[1]

            if key == 'name':
                   name = val
            elif key == 'chan':
                   chan = val
            elif key == 'value':
                   value = val
            elif key == 'freq':
                   freq = val
            elif key == 'i2c':
                   i2c = val

        elif argu == '-h' or argu == '--help':
            print("   pca9685 PWM switch")
            print("")
            print("   name=  ")
            print("   value= percentage to set pwm to")
            print("   chan=  channel number")
            print("   i2c=   use instead of name to select device")
            print("   freq=  PWM freqience in Hz")
            print("")
            sys.exit()
        elif argu == '-flags':
            print("name=")
            print("chan=")
            print("value=")
            print("i2c=")
            print("freq=")
    return name, chan, value, freq, i2c

def enable_pca(freq, i2c):
    i2c_bus = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c_bus)
    pca.frequency = int(freq)
    return pca

def pca_switch(name, i2c, freq, chan, value, set_dic, switch_log):
    pca = enable_pca(freq, i2c)
    script = 'pca9685_set.py'
    pca.channels[int(chan)].duty_cycle = int(value)
    log_msg = "Set " + name + " channel " + chan + " to " + str(value)
    pigrow_defs.write_log(script, log_msg, switch_log)


def read_from_settings(name):
    #msg =(" PCA9685 \n")
    name_i2c  = "pca_" + name + "_loc"
    name_freq = "pca_" + name + "_freq"
    if name_i2c in set_dic and name_freq in set_dic:
        i2c  = set_dic[name_i2c]
        freq = set_dic[name_freq]
        if not i2c == "":
            return i2c, freq
        else:
            return "", ""
    else:
        print("")
        return "", ""


if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
    name, chan, value, freq, i2c = check_command_line_args()

    s_freq = ""
    if not name == "":
        i2c, s_freq = read_from_settings(name)
    else:
        name = "i2c " + str(i2c)
        if i2c == "":
            print("Must set name= or i2c=")
            sys.exit()

    if i2c == "":
        print("i2c address for " + name + " not set in " + loc_dic['loc_settings'])

    if freq == "":
        if s_freq == "":
            print(" - Using default frequency of 150 Hz")
            freq = "150"
        else:
            freq = s_freq

    if chan == "":
        print(" - No channel set, use chan=")
        sys.exit()

    if value == "":
        print(" no value set, use value= to set a power level percentage")
        sys.exit()

    value = int(value) / 100 * 65534

    pca_switch(name, i2c, freq, chan, value, set_dic, loc_dic['loc_switchlog'])
