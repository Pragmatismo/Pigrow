#!/usr/bin/python
import datetime
import sys

import pigrow_defs

sys.path.append('/home/pi/Pigrow/scripts/')


def fans_on(set_dic, switch_log):
    script = 'fans_on.py'
    msg = ("")
    msg += ("      #############################################\n")
    msg += ("      ##         Turning the fansifier - ON         ##\n")
    if 'gpio_fans' in set_dic and not str(set_dic['gpio_fans']).strip() == '':
        gpio_pin = int(set_dic['gpio_fans'])
        gpio_pin_on = set_dic['gpio_fans_on']
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            GPIO.output(gpio_pin, GPIO.LOW)
        elif gpio_pin_on == "high":
            GPIO.output(gpio_pin, GPIO.HIGH)
        else:
            msg += ("      !!       CAN'T DETERMINE GPIO DIRECTION    !!\n")
            msg += ("      !!  run config program or edit config.txt  !!\n")
            msg += ("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            pigrow_defs.write_log(
                script,
                'Failed - no direction set in config',
                switch_log)
            return msg

    else:
        msg += ("      !!               NO fans SET             !!\n")
        msg += ("      !!  run config program or edit config.txt  !!\n")
        msg += ("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(
            script,
            'Failed - due to none set in config',
            switch_log)
        return msg

    msg += ("      ##            by switching GPIO " +
            str(gpio_pin) + " to " + gpio_pin_on + "  ##")
    msg += ("      #############################################\n")
    pigrow_defs.write_log(script, 'fansifier turned on', switch_log)
    return msg

if __name__ == '__main__':

    # default settings
    loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(
        loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    msg = fans_on(set_dic, loc_dic['loc_switchlog'])
    print msg
