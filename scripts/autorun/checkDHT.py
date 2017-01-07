#!/usr/bin/python
#
#         This script it designed to be run in a continuous loop
#
#
#

#defaults to be changed with args eventually


log_time = 30
log_non = True #tests switch conditions even if no switich present.

use_heat    = True
use_humid   = True
use_dehumid = True

heat_use_fan   = True
hum_use_fan  = False
dehum_use_fan  = False



script = 'chechDHT.py'
import os, sys
import datetime, time
import Adafruit_DHT
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs
sys.path.append('/home/pi/Pigrow/scripts/switches/')
import heater_on, heater_off, humid_on, humid_off, dehumid_on, dehumid_off, fans_on, fans_off, lamp_on, lamp_off
loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
#print set_dic


def read_and_log(loc_dic):
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, set_dic['gpio_dht22sensor'])
        if humidity == None or temperature == None:
            print("--problem reading sensor on GPIO:"+set_dic['gpio_dht22sensor']+"--")
            return '-1','-1','-1'
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            timno = datetime.datetime.now()
            try:
                with open(loc_dic['loc_dht_log'], "a") as f:
                    line = str(temperature) + '>' + str(humidity) + '>' + str(timno) + '\n'
                    f.write(line)
            except:
                print["-LOG ERROR-"]
                pigrow_defs.write_log('checkDHT.py', 'writing dht log failed', loc_dic['loc_switchlog'])
            return humidity, temperature, timno
    except:
        print("--problem reading sensor on GPIO:"+set_dic['gpio_dht22sensor']+"--")
        return '-1','-1','-1'


def heater_control(temp, use_fans=True):
    global heater_state
    #checks to see if current temp should result in heater on or off
    templow  = float(set_dic['heater_templow'])
    temphigh = float(set_dic['heater_templow'])  ## plan is to add buffer zones or some something
    if temp < templow and heater_state != 'on':
        message = "It's cold,  temp is" + str(temp) + " degrees! the low limit is " + str(templow) + " so turning heater on."
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking heater's on"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_on.heater_on(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'on'
    elif temp > temphigh and heater_state != 'off':
        message = "it's warm, temp is " + str(temp) + " degrees, the high limit is " + str(temphigh) + " so turning heater off"
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking heater's off"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_off.heater_off(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'off'
    else:
        message = "doing nothing, it's " + str(temp) + " degrees and the heater is " + heater_state
        #print(" --not worth logging but, " + message)

def humid_contol(humid,use_fans=False):
    global humid_state
    humid_low  = float(set_dic['humid_low'])
    if humid < humid_low and humid_state != 'up_on':
        msg = "should turn the humidifer on, it's " + str(humid) + " and the low limit is " + str(humid_low)
        if humid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", low limit is " + str(humid_low) + " checking humidifier is on"
        humid_state = 'up_on'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        humid_on.humid_on(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])
    elif humid > humid_low and humid_state !='up_off':
        msg = ("should turn the humidifier off, it's " + str(humid) + " and the low limit is " + str(humid_low))
        if humid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", low limit is " + str(humid_low) + " checking humidifier is off"
        humid_state = 'up_off'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        humid_off.humid_off(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])

def dehumid_control(humid,use_fans=False):
    global dehumid_state
    humid_high = float(set_dic['humid_high'])
    if humid > humid_high and dehumid_state != 'down_on':
        msg = "should turn dehumidifer on, it's " + str(humid) + " and the high limit is " + str(humid_high)
        if dehumid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", the high limit is " + str(humid_high) + " checking it's on"
        dehumid_state = 'down_on'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        dehumid_on.dehumid_on(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])
    elif humid < humid_high and dehumid_state != 'down_off':
        msg = "should turn dehumid off, it's " + str(humid) + " and the high limit is " + str(humid_high)
        if dehumid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", high limit is " + str(humid_high) + " checking it's off"
        dehumid_state = 'down_off'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        dehumid_off.dehumid_off(set_dic, loc_dic['loc_switchlog'])
        if use_fans == True:
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])



dehumid_state = 'unknown'
humid_state = 'unknown'
heater_state = 'unknown'

## checks light is in correct state on restart

def check_lamp(on_time, off_time):
    current_time = datetime.datetime.now().time()
    msg = 'Script initialised, performing lamp state check;'
    pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
    if True:
        if on_time > off_time:
            if current_time > on_time or current_time < off_time:
                lamp_on.lamp_on(set_dic, loc_dic['loc_switchlog'])
                return 'a lamp on', True
            else:
                lamo_off.lamp_off(set_dic, loc_dic['loc_switchlog'])
                return 'a lamp off', True

        elif on_time < off_time:
            if current_time > on_time and current_time < off_time:
                lamo_on.lamp_on(set_dic, loc_dic['loc_switchlog'])
                return 'the lamp on', True
            else:
                lamo_off.lamp_off(set_dic, loc_dic['loc_switchlog'])
                return 'the lamp off', True

        elif current_time == on_time:
            return 'changing', False
        return 'magness', False

time_on = set_dic['time_lamp_on'].split(":")
time_off = set_dic['time_lamp_off'].split(":")
on_time = datetime.time(int(time_on[0]),int(time_on[1]))
off_time = datetime.time(int(time_off[0]), int(time_off[1]))

state, change = check_lamp(on_time, off_time)

if change:
    print state
else:
    print("Not matching, problem with time thingy! ir was " + str(state) + " having a rest then trying again...")


#
#      THE ETERNAL LOOP
#
#

while True:
    try:
        humid, temp, timno = read_and_log(loc_dic)
        print(" -- " + str(timno) + ' temp: ' + str(temp) + ' humid: ' + str(humid))
        if not timno == '-1':
            if not str(set_dic['gpio_heater']).strip() == '' or log_non == True or heat_use_fan == True:
                if use_heat == True:
                    heater_control(temp,heat_use_fan)
            if not str(set_dic['gpio_humid']).strip() == '' or log_non == True or hum_use_fan == True:
                if use_humid == True:
                    humid_contol(humid,hum_use_fan)
            if not str(set_dic['gpio_dehumid']).strip() == '' or log_non == True or dehum_use_fan == True:
                if use_dehumid == True:
                    dehumid_control(humid, dehum_use_fan)
            time.sleep(log_time)
        else:
            print("Sensor didn't read...")
            time.sleep(1)
    except Exception as e:
        print("#######SOME FORM OF PIGROW ERROR Pigrow error pigrow error in checldht, probably sensor being shonk")
        print("         or some file thing??       user intervention?          i'm spooked, whatever.")
        print e
        raise
        time.sleep(1)
