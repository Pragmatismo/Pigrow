#!/usr/bin/python

#This will turn the LED on for thirty seconds
# then turn it off.

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
print "LED on"
GPIO.output(16,GPIO.HIGH)
time.sleep(30)
print "LED off"
GPIO.output(16,GPIO.LOW)
