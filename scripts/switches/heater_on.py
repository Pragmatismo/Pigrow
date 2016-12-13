#!/usr/bin/python
import datetime, sys
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs



print("")
print("      #############################################")
print("      ##         Turning the heater - ON         ##")




def heater_on(set_dic, switch_log):
    if 'gpio_heater' in set_dic and not set_dic['gpio_heater'] == '':
        gpio_pin = int(set_dic['gpio_heater'])
        gpio_pin_on = set_dic['gpio_heater_on']
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio_pin, GPIO.OUT)
        if gpio_pin_on == "low":
            GPIO.output(gpio_pin, GPIO.LOW)
        elif gpio_pin_on == "high":
            GPIO.output(gpio_pin, GPIO.HIGH)
        else:
            print("      !!       CAN'T DETERMINE GPIO DIRECTION    !!")
            print("      !!  run config program or edit config.txt  !!")
            print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            pigrow_defs.write_log('heater_on.py', 'Failed - no direction set in config', switch_log)
            exit()

    else:
        print("      !!               NO HEATER SET             !!")
        print("      !!  run config program or edit config.txt  !!")
        print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pigrow_defs.write_log('heater_on.py', 'Failed - due to none set in config', switch_log)
        exit()

    print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##")
    print("      #############################################")
    pigrow_defs.write_log('heater_on.py', 'Heater turned on', switch_log)
    print("Log writen:" + line)

if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    heater_on(set_dic, loc_dic['loc_switchlog'])
