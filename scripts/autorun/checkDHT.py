
script = 'chechDHT.py'
import os, sys
import datetime
import Adafruit_DHT
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs
sys.path.append('/home/pi/Pigrow/scripts/switches/')
import heater_on, heater_off
loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
#print set_dic


def read_and_log():
    try:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, set_dic['gpio_dht22sensor'])
        if humidity is not None and temperature is not None:
            timno = datetime.datetime.now()
            with open(loc_dic['loc_dht_log'], "a") as f:
                line = str(temperature) + '>' + str(humidity) + '>' + str(timno) + '\n'
                f.write(line)
            return humidity, temperature, timno
    except:
        print("--problem reading sensor--")
        return '-1','-1','-1'


def heater_control(temp):
    #checks to see if current temp should result in heater on or off
    templow  = set_dic['heater_templow']
    temphigh = set_dic['heater_temphigh']
    if temp > templow and heater_state == 'off':
        message = "It's bloody cold," + str(temp) + " degrees! the low limit is " + str(templow)
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_on.heater_on(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'on'
    elif temp < temphigh and heater_state == 'off':
        message = "fucking 'ell it's well hot in here," + str(temp) + " degrees! the high limit is " + str(temphigh)
        pigrow_defs.write_log(script, message,loc_dic['loc_switchlog'])
        heater_off.heater_off(set_dic, loc_dic['loc_switchlog'])
        heater_state = 'off'
    else:
        message = "This is a nice temperateure, no it is, don't you think?" + str(temp) + " degrees"
        print(" --not worth logging but, " + message)


heater_state = 'unknown'
while True;
    hum, temp, timno = read_and_log()
    heater_control(temp)
