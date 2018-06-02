#!/usr/bin/python
#
#         This script it designed to be run in a continuous loop
#
#
#

log_time = 600
log_non = True #tests switch conditions even if no switich present.

use_heat    = True
use_humid   = True
use_dehumid = True

heat_use_fan   = True
hum_use_fan  = False
dehum_use_fan  = False

script = 'checkDHT.py'
import os
import sys
import datetime
import time
import Adafruit_DHT
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
sys.path.append(homedir + '/Pigrow/scripts/switches/')
import heater_on, heater_off, humid_on, humid_off, dehumid_on, dehumid_off, fans_on, fans_off, lamp_on, lamp_off
loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])
#print set_dic
if 'log_frequency' in set_dic:
    log_time = set_dic['log_frequency']

for argu in sys.argv[1:]:
    if '=' in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'log_time' or thearg == 'delay':
            log_time = int(thevalue)
        elif thearg == 'log_non':
            if thevalue.lower() == 'true' or thevalue == '0':
                log_non = True
            else:
                log_non = False
        elif thearg == 'use_heat':
            if thevalue.lower() == 'true' or thevalue == '0':
                use_heat = True
            else:
                use_heat = False
        elif thearg == 'use_humid':
            if thevalue.lower() == 'true' or thevalue == '0':
                use_humid = True
            else:
                use_humid = False
        elif thearg == 'use_dehumid':
            if thevalue.lower() == 'true' or thevalue == '0':
                use_dehumid = True
            else:
                use_dehumid = False
        elif thearg == 'usefan':
            if thevalue.lower() == 'heat':
                heat_use_fan = True
                hum_use_fan  = False
                dehum_use_fan  = False
            elif thevalue.lower() == 'hum' or thevalue.lower() == 'humid':
                heat_use_fan = False
                hum_use_fan  = True
                dehum_use_fan  = False
            elif thevalue.lower() == 'dehum' or thevalue.lower() == 'dehumid':
                heat_use_fan = False
                hum_use_fan  = False
                dehum_use_fan  = True
            elif thevalue.lower() == 'none':
                heat_use_fan = False
                hum_use_fan  = False
                dehum_use_fan  = False
    elif argu == '-h' or 'help' in argu:
        print("")
        print("  Pigrow DHT log and control loop")
        print(" ")
        print(" This is designed to be run on start-up as a continual loop")
        print(" it reads the dht sensor, writes a log and switches heater,")
        print(" humid, dehumid and/or fans on or off as appropriate.")
        print("")
        print(" Cut-off and trigger values are set in " + str(loc_dic['loc_settings']))
        print("")
        print(" log_time=TIME IN SECONDS   - the delay between log recordings")
        print(" log_non=false              - doesn't log switches you don't have")
        print("")
        print(" use_heat=false             - disable heater control in this script")
        print(" use_humid=false            - disable humidifier in this script")
        print(" use dehumid=false          - disable dehumidifer in this script")
        print(" ")
        print(" usefan=heat                -heter controlls fan (best)")
        print("       =humid               -humid controls fan")
        print("       =dehumid             -dehumid controls fan")
        print("       =none                -fan is ignored by all")
        sys.exit()
    elif argu == '-flags':
        print("log_time=60")
        print("log_non=[true,false]")
        print("use_heat=[true,false]")
        print("use_humid=[true,false]")
        print("use_dehumid=[true,false]")
        print("usefan=[heat,humid,dehumid,none]")
        sys.exit()

def read_and_log(loc_dic):
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, set_dic['gpio_dht22sensor'])
        if humidity == None or temperature == None or humidity > 101:
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
                pigrow_defs.write_log('checkDHT.py', 'writing dht log failed', loc_dic['err_log'])
            return humidity, temperature, timno
    except:
        print("--problem reading sensor on GPIO:"+set_dic['gpio_dht22sensor']+"--")
        return '-1','-1','-1'

#
#   Device control logic
#

def heater_control(temp):
    global heater_state
    #checks to see if current temp should result in heater on or off
    templow  = float(set_dic['heater_templow'])
    temphigh = float(set_dic['heater_templow'])  ## using templow here is not a mistake, plan is to add buffer zones or some something
    print(" ~ ~ ~ heater controll function started ~ ~ ~")
    print("temp = " + temp)
    print(" templow = " + templow)
    print(" temphigh = " + temphigh)
    print("Use Fans = " + str(use_fans))
    print("heater state = " + str(heater_state))
    # if too cool
    if temp < templow and heater_state != 'on':
        message = "It's cold,  temp is" + str(temp) + " degrees! the low limit is " + str(templow) + " so turning heater on."
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking heater's on"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_on.heater_on(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'on'
    # if too hot
    elif temp > temphigh and heater_state != 'off':
        print(" temp greater than temphigh and the heater is off ")
        message = "it's warm, temp is " + str(temp) + " degrees, the high limit is " + str(temphigh) + " so turning heater off"
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking heater's off"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_off.heater_off(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'off'
    else:
        message = "doing nothing, it's " + str(temp) + " degrees and the heater is " + heater_state
        #print(" --not worth logging but, " + message)
    print("")
    print(" ~ ~ ~ heater controll function finished ~ ~ ~")

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
    elif humid > humid_low and humid_state !='up_off':
        msg = ("should turn the humidifier off, it's " + str(humid) + " and the low limit is " + str(humid_low))
        if humid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", low limit is " + str(humid_low) + " checking humidifier is off"
        humid_state = 'up_off'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        humid_off.humid_off(set_dic, loc_dic['loc_switchlog'])

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
    elif humid < humid_high and dehumid_state != 'down_off':
        msg = "should turn dehumid off, it's " + str(humid) + " and the high limit is " + str(humid_high)
        if dehumid_state == 'unknown':
            msg = "Script initialised, humid " + str(humid) + ", high limit is " + str(humid_high) + " checking it's off"
        dehumid_state = 'down_off'
        pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
        dehumid_off.dehumid_off(set_dic, loc_dic['loc_switchlog'])

def fan_control(temp, humid, heat_use_fan=True, hum_use_fan=False, dehum_use_fan=False):
    global fans_state
    print(" -- Fan controll")
    if heat_use_fan == True:
        temphigh = float(set_dic['heater_temphigh'])
        if temp > temphigh and fans_state != 'on':
            message = "too hot, temp is " + str(temp) + " degrees, the high limit is " + str(temphigh) + " so turning the fans on"
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'off'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
        elif temp < temphigh and fans_state != 'off':
            message = "not too hot, temp is " + str(temp) + " degrees, the high limit is " + str(temphigh) + " so turning the fans off"
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'off'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    # humid up
    if hum_use_fan == True:
        hum_low = float(set_dic['humid_low'])
        if humid < hum_low and fans_state != 'on':
            message = "not humid enough, humidity is " + str(humid) + " %, the low limit is " + str(hum_low) + " so turning the fans on"
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'on'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
        elif temp > hum_low and fans_state != 'off':
            message = "humid enough, humidity is " + str(humid) + " %, the low limit is " + str(hum_low) + " so turning the fans off"
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'off'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    # humid down
    if dehum_use_fan == True:
        hum_high = float(set_dic['humid_high'])
        if humid > hum_high and fans_state != 'on':
            message = "too humid, humidity is " + str(humid) + " %, the high limit is " + str(hum_high) + " so turning the fans on"
            fans_on.fans_on(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'on'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
        elif humid < hum_high and fans_state != 'off':
            message = "humid low enough, humidity is " + str(humid) + " %, the high limit is " + str(hum_high) + " so turning the fans off"
            fans_off.fans_off(set_dic, loc_dic['loc_switchlog'])
            fans_state = 'off'
            pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])

#
#   Set the initial states of everything on script start
#                                    script written to be started on boot

dehumid_state = 'unknown'
humid_state = 'unknown'
heater_state = 'unknown'
fans_state = 'unknown'

## checks light is in correct state on restart

def check_lamp(on_time, off_time):
    current_time = datetime.datetime.now().time()
    msg = 'Script initialised, performing lamp state check;'
    pigrow_defs.write_log(script, msg,loc_dic['loc_switchlog'])
    if True:
        if on_time > off_time:
            if current_time > on_time or current_time < off_time:
                lamp_on.lamp_on(set_dic, loc_dic['loc_switchlog'])
                return 'lamp on', True
            else:
                lamp_off.lamp_off(set_dic, loc_dic['loc_switchlog'])
                return 'lamp off', True

        elif on_time < off_time:
            if current_time > on_time and current_time < off_time:
                lamp_on.lamp_on(set_dic, loc_dic['loc_switchlog'])
                return 'the lamp on', True
            else:
                lamp_off.lamp_off(set_dic, loc_dic['loc_switchlog'])
                return 'the lamp off', True

        elif current_time == on_time:
            return 'crazy coincidence, exact time match! cron will switch it for us', False
        return 'error', False

print(" -- Initializing checkDHT.py conditions monitoring script ")

time_on = set_dic['time_lamp_on'].split(":")
time_off = set_dic['time_lamp_off'].split(":")
on_time = datetime.time(int(time_on[0]),int(time_on[1]))
off_time = datetime.time(int(time_off[0]), int(time_off[1]))

state, change = check_lamp(on_time, off_time)

if change:
    print(" Determenined the lamp should be -" + state)
else:
    print("Not matching, problem with time thingy! it was " + str(state) + " having a rest then trying again...")

#
#      THE ETERNAL LOOP
#
#
print(" ---  STarting temp and humid checking cycle --- ")

while True:
    try:
        humid, temp, timno = read_and_log(loc_dic)
        print(" -- " + str(timno) + ' temp: ' + str(temp) + ' humid: ' + str(humid))
        if not humid > 101:
            # heat up and down
            if 'gpio_heater' in set_dic:
                if str(set_dic['gpio_heater']).strip() != '' or log_non == True:
                    if use_heat == True:
                        heater_control(temp)
            # fans used for heat or humid
            if 'gpio_fans' in set_dic:
                fan_control(temp, humid, heat_use_fan, hum_use_fan, dehum_use_fan)
            # Humidity up and down
            if 'gpio_humid' in set_dic:
                if not str(set_dic['gpio_humid']).strip() == '' or log_non == True or hum_use_fan == True:
                    if use_humid == True:
                        humid_contol(humid,hum_use_fan)
            if 'gpio_dehumid' in set_dic:
                if not str(set_dic['gpio_dehumid']).strip() == '' or log_non == True or dehum_use_fan == True:
                    if use_dehumid == True:
                        dehumid_control(humid, dehum_use_fan)
            # rest for the length of the log_time delay
            time.sleep(int(log_time))
        else:
            print("Sensor didn't read...")
            time.sleep(1)
    except Exception as e:
        print("#######SOME FORM OF PIGROW ERROR Pigrow error pigrow error in checkDHT.py, probably sensor being shonk")
        print("         or some file thing??       user intervention?          i'm spooked, whatever.")
        print e
        #raise
        time.sleep(1)
