#!/usr/bin/python

print("This program will test the relays")
print(" -- uses gpio pins 23,8,12,21 -- "
print(" each will turn on one after the other")
print(" until all are lit, then they'll start")
print(" to turn off one after the other.")
print("")
print("note- all on or all off relates to")
print("the internal relays not the socket")
print("this is dependent on the wiring of")
print("the relays, i.e. normally open or closed")
print("")
print("The sequence will repeat five times")
from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(8, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
for x in range(1, 5):
    print x
    GPIO.output(23, GPIO.HIGH)
    sleep(2)
    GPIO.output(8, GPIO.HIGH)
    sleep(2)
    GPIO.output(12, GPIO.HIGH)
    sleep(2)
    GPIO.output(21, GPIO.HIGH)
    sleep(2)
    print("all should be on")
    GPIO.output(23, GPIO.LOW)
    sleep(2)
    GPIO.output(8, GPIO.LOW)
    sleep(2)
    GPIO.output(12, GPIO.LOW)
    sleep(2)
    GPIO.output(21, GPIO.LOW)
    sleep(2)
    print("all should be off")
GPIO.cleanup()
