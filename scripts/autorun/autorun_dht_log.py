#!/usr/bin/python

loc_settings = '/home/pi/Pigrow/config/pigrow_config.txt'
loc_log = '/home/pi/Pigrow/logs/sensor_log.txt'
loc_switch_log = '/home/pi/Pigrow/logs/switch_log.txt'

#the on time must come before the off time
time_lamp_off = 1 #number between 0 and 23
time_lamp_on = 7 #number between 0 and 23
gpio_lamp = 8 #lamp relay
gpio_heater = 12 #heater relay
templow = 20  #temp to turn on heater
temphigh = 25 #temp at which to turn heater off
sensor_pin = 18 #sensor gpio number
log_frequency = 60

#load settings
try:
    with open(loc_settings, "r") as f:
        c_item = f.read()
        c_item = c_item.split("\n")
    box_name = str(c_item[0].split('=')[1])
    time_lamp_on = int(c_item[1].split('=')[1])
    time_lamp_off = int(c_item[2].split('=')[1])
    gpio_lamp = int(c_item[3].split('=')[1])
    gpio_heater = int(c_item[4].split('=')[1])
    gpio_fan_in = int(c_item[5].split('=')[1])
    gpio_fan_off = int(c_item[6].split('=')[1])
    sensor_pin = int(c_item[7].split('=')[1])
    templow = int(c_item[8].split('=')[1])
    temphigh = int(c_item[9].split('=')[1])
    log_frequency = int(c_item[10].split('=')[1])
except:
    pass

print "Logging every " + str(log_frequency) + " seconds"

import datetime
import time
import Adafruit_DHT
sensor = Adafruit_DHT.DHT22

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_lamp, GPIO.OUT)
GPIO.setup(gpio_heater, GPIO.OUT)

#not user settings, don't change these
heater_state = False
fan_state = False


#next bit happens once on start up to check light is in
#correct state other light switching is done by cron

#get datetime for todays lamp switches
now = datetime.datetime.now()
day = now.date()
light_out = datetime.time(hour = time_lamp_off)
out_today = datetime.datetime.combine(day, light_out)
light_on = datetime.time(hour = time_lamp_on)
on_today = datetime.datetime.combine(day, light_on)
timno = datetime.datetime.now()

#for now the following only works if
#the ON time happens before the OFF time
#this will change soon :)

while True:
    try:
        print("be cool if this tested the internet is up and the time updated")
        break
    except:
        time.sleep(15)
        pass

if timno < out_today:
    print "before offtime - light on"
    with open(loc_switch_log, "a") as f:
        f.write('auto@' + str(timno) + '@fter outtime, before ontime - light off\n')
    GPIO.output(gpio_lamp, GPIO.LOW)

if timno > out_today and datetime.datetime.now() < on_today:
    print "after outtime, before ontime - light off"
    with open(loc_switch_log, "a") as f:
        f.write('auto@' + str(timno) +'@after outtime, before ontime - light off\n')
    GPIO.output(gpio_lamp, GPIO.HIGH)

if timno > on_today:
    print "after ontime, - light on"
    with open(loc_switch_log, "a") as f:
        f.write('auto@' + str(timno) + '@after ontime, - light on \n')
    GPIO.output(gpio_lamp, GPIO.LOW)

#loop that runs constantly

##

##
#                  THIS NEEDS REWRITING BECAUSE IT IS ALL WRONG AND STUPID AND OLD AND BAD AND IT MAKES ME SAD
##

##

while True:
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_pin)
        if humidity is not None and temperature is not None:
            timno = datetime.datetime.now()
            if temperature <= templow and heater_state == False:
                with open(loc_switch_log, "a") as f:
                    f.write('auto@' + str(timno) + '@heater on - this code is old and outdated for new system \n')
                GPIO.output(gpio_heater, GPIO.LOW)
                heater_state = True
            if temperature >= temphigh and heater_state == True:
                with open(loc_switch_log, "a") as f:
                    f.write('auto@' + str(timno) + '@turning heater off, need to rewrite this\n')
                GPIO.output(gpio_heater, GPIO.HIGH)
                heater_state = False
            #record log
            with open(loc_log, "a") as f:
                line = str(temperature) + '>' + str(humidity) + '>' + str(timno) + '\n'
                f.write(line)
        else:
            print('Failed to get reading. Try again!')
        time.sleep(log_frequency)
    except:
        timno = datetime.datetime.now()
        with open(loc_switch_log, "a") as f:
            f.write('fauto@' + str(timno) + '@this is old and outdated code, it broke for some reason, rewrite it asap\n')
        pass
