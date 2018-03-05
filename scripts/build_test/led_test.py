#!/usr/bin/python

#This will turn the LED on for thirty seconds
# then turn it off.

import wiringpi
import time
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(16,1)

print "LED on"
wiringpi.digitalWrite(16,1)
time.sleep(30)
print "LED off"
wiringpi.digitalWrite(16,0)
