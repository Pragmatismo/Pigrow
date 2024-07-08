#!/usr/bin/env python3
import sys
import time

print("This will turn the LED on for thirty seconds")
print("then turn it off.")
answer = raw_input("Which GPIO is the LED linked to? ")

try:
    LED = int(answer)
except:
    print("Must be a number")
    sys.exit()

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED, GPIO.OUT)
print ("LED on")
GPIO.output(LED, GPIO.HIGH)
time.sleep(30)
print ("LED off")
GPIO.output(LED, GPIO.LOW)
