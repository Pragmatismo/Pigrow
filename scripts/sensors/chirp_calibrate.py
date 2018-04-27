#!/usr/bin/python
import os
import sys
syshomedir = os.getenv("HOME")
sys.path.append(homedir + '/chirp-rpi/')
import chirp

show = False
chirp_address = 0x20
number_of_attempts = 50
looking_for = "max" # "min"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'address' or thearg == 'chirp_address':
            chirp_address = int(thevalue, 16)
        if thearg == 'show':
            if thevalue.lower() == "true":
                show = True
        if thearg == "attempts":
            number_of_attempts = int(thevalue)
        if thearg == "looking_for":
            looking_for = thevalue
    elif argu == "max":
        looking_for = "max"
    elif argu == "min":
        looking_for = "min"
    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for calibrating the Chirp Soil Moisture Sensor")
        print("     this uses the module chirp-rpi")
        print("     many thanks to Goran Lundberg")
        print("     https://github.com/ageir/chirp-rpi/")
        print(" ")
        print("     You will need I2C support enabled on the pi")
        print("            ( sudo raspi-config )")
        print(" ")
        print(" looking_for=min")
        print("             max")
        print("      - find the min or max value")
        print(" chirp_address=0x20")
        print("      - i2c address of the chirp")
        print(" show=true")
        print("      - show ever reading as it comes in.")
        print(" attempts=50")
        print("      - the number of sensor reads used to obtain final value")
        print("        it takes about five seconds per read")
        print("")
        print("  This will read the sensor for a duration of xx then return the ")
        print("  highest/lowest value it read, this can be used in calibration of the ")
        print("  soil moisture percentage and is designed to work automatically with")
        print("  the pigrow's remote gui.")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("chirp_address=0x20")
        print("show=[true,false]")
        print("looking_for=[min,max]")
        sys.exit(0)

def init_sensor(chirp_address):
    # Initialize the sensor.
    chirp_sensor = chirp.Chirp(address=chirp_address,
                        read_moist=True,
                        read_temp=True,
                        read_light=True,
                        min_moist="0",
                        max_moist="1000",
                        temp_scale='celsius',
                        temp_offset=0)
    return chirp_sensor

if __name__ == '__main__':
    chirp_sensor = init_sensor(chirp_address)
    top_moist = 1
    bottom_moist = 10000
    for x in range(0, number_of_attempts):
        chirp_sensor.trigger()
        moist = chirp_sensor.moist
        # max
        if looking_for == "max":
            if moist > top_moist:
                top_moist = moist
                if show == True:
                    print("___^____^____^____ reading " + str(x) + " new top value")
            if show == True:
                print top_moist, moist
        # min
        elif looking_for == "min":
            if moist < bottom_moist:
                bottom_moist = moist
                if show == True:
                    print("----V----V----V----- reading " + str(x) + " new bottom value")
            if show == True:
                print bottom_moist, moist
        else:
            print("Not sure what you want from me?!")
            print(" should be set to min or max, currently set to " + str(looking_for))
            print("use the --help option for more information.")
            sys.exit()

if looking_for = 'max':
    print top_moist
elif looking_for = 'min':
    print bottom_moist
