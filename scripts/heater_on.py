print("")
print("      #############################################")
print("      ##         Turning the heater - ON         ##")


### user settings

loc_settings = "/home/pragmo/pigitgrow/Pigrow/config/pigrow_config.txt"

### defining variables

pi_set = {}   #the dictionary of settings

### loading settings

try:
    with open(loc_settings, "r") as f:
        for line in f:
            s_item = line.split("=")
            pi_set[s_item[0]]=s_item[1].rstrip('\n')
except:
    print("Settings not loaded, try running pi_setup")
    raise

# Using settings to do whatever it's supposed to do with them...

gpio_pin = int(pi_set['gpio_heater'])
gpio_pin_on = pi_set['gpio_heater_on']

if 'gpio_heater' in pi_set and not pi_set['gpio_heater'] == '':
    #import RPi.GPIO as GPIO
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(gpio_pin, GPIO.OUT)
    print("skipping gpio module as TESTING TEST TEST TEST")
    if gpio_pin_on == "low":
        #GPIO.output(gpio_pin, GPIO.LOW)
        print("skipping setting gpio LOW as TESTING TEST TEST TEST")
    elif gpio_pin_on == "high":
        #GPIO.output(gpio_pin, GPIO.HIGH)
        print("skipping settubg gpio HIGH as TESTING TEST TEST TEST")
    else:
        print("      !!       CAN'T DETERMINE GPIO DIRECTION   !!")
        print("      !!  run config program or edit config.txt !!")
        print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

else:
            print("      !!               NO HEATER SET            !!")
            print("      !!  run config program or edit config.txt !!")
            print("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

print("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_on+"  ##")
print("      #############################################")
