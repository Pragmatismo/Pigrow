
script = 'chechDHT.py'
import os, sys
import datetime, time
import Adafruit_DHT
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs
sys.path.append('/home/pi/Pigrow/scripts/switches/')
import heater_on, heater_off
loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
#print set_dic


def read_and_log(loc_dic):
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, set_dic['gpio_dht22sensor'])
        if humidity is not None and temperature is not None:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            timno = datetime.datetime.now()
            try:
                with open(loc_dic['loc_dht_log'], "a") as f:
                    line = str(temperature) + '>' + str(humidity) + '>' + str(timno) + '\n'
                    f.write(line)
            except:
                print["-LOG ERROR-"]
                pigrow_defs.write_log('checkDHT.py', 'writing dht failed', loc_dic['loc_switchlog'])
            return humidity, temperature, timno
    except:
        print("--problem reading sensor on GPIO:"+set_dic['gpio_dht22sensor']+"--")
        return '-1','-1','-1'


def heater_control(temp):
    global heater_state
    #checks to see if current temp should result in heater on or off
    templow  = set_dic['heater_templow']
    temphigh = set_dic['heater_temphigh']
    if temp > templow and heater_state != 'on':
        message = "It's bloody cold," + str(temp) + " degrees! the low limit is " + str(templow)
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking it's on"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_on.heater_on(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'on'
    elif temp < temphigh and heater_state != 'off':
        message = "fucking 'ell it's well hot in here, " + str(temp) + " degrees! the high limit is " + str(temphigh)
        if heater_state == 'unknown':
            message = "Script initialised, it's " + str(temp) + " degrees! the low limit is " + str(templow) + " so checking it's off"
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_off.heater_off(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'off'
    else:
        message = "doing nothing, it's " + str(temp) + " degrees and the heater is " + heater_state
        #print(" --not worth logging but, " + message)

def humid_contol(humid):
    global humid_state, dehumid_state
    humid_low  = set_dic['humid_low']
    humid_high = set_dic['humid_high']

    if humid > humid_low and humid_state != 'up_on':
        print("lol should turn the humidifer on, it's " + str(humid) + " and the low limit is " + str(humid_low))
        humid_state = 'up_on'
    elif humid < humid_low and humid_state !='up_off':
        print("should turn the humidifier off, it's " + str(humid) + " and the low limit is " + str(humid_low))
        humid_state = 'up_off'

    if humid > humid_high and dehumid_state != 'down_on':
        print("should turn dehumidifer on, it's " + str(humid) + " and the high limit is " + str(humid_high))
        dehumid_state = 'down_on'
    elif humid < humid_high and dehumid_state != 'down_off':
        print("should turn dehumid off, it's " + str(humid) + " and the high limit is " + str(humid_high))
        dehumid_state = 'down_off'



dehumid_state = 'unknown'
humid_state = 'unknown'
heater_state = 'unknown'

##needs to check light is in correct state on restart

while True:
    humid, temp, timno = read_and_log(loc_dic)
    print(" -- " + str(timno) + ' temp: ' + str(temp) + ' humid: ' + str(humid))
    if not timno == '-1':
        #if not set_dic['gpio_heater'] == '': #(silences if no heater but probably nicer to know, rite?)
        heater_control(temp)
        humid_contol(humid)
        time.sleep(15)
    else:
        print("Sensor didn't read...")
        time.sleep(1)
