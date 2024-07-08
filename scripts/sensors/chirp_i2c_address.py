#!/usr/bin/env python3
import os, sys
homedir = os.getenv("HOME")
sys.path.append(homedir + '/chirp-rpi/')
sys.path.append(homedir + '/Pigrow/scripts/gui/sensor_modules/chirp-rpi/')

import chirp

chirp_address = None
new_addr = None

def show_help():
    print(" Script for re-addressing the Chirp soil moisture sensor ")
    print(" ")
    print(" current=")
    print("      - The current location of the chirp")
    print("        if the chirp is not shown by 'sudo i2cdetect -y 1' ")
    print("        then it's likey at location 0x01 or possibly 0x00, 0x02")
    print("        Use the format 0x01, 0x45 or etc")
    print(" ")
    print(" new=")
    print("      - The address you want to put the chirp sensor")
    print("")
    print("")

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'current' or thearg == 'c':
            chirp_address = int(thevalue, 16)
            text_address = thevalue
        elif thearg == 'new' or thearg == 'n':
            new_addr = int(thevalue, 16)
            text_new_address = thevalue
    elif argu == 'help' or argu == '-h' or argu == '--help':
        show_help()
        sys.exit(0)
    elif argu == "-flags":
        print("current=[0x01]")
        print("new=[0x20]" + str(log_path))
        sys.exit(0)

if chirp_address == None or new_addr == None:
    print(" You need specify both the current and new address")
    print("")
    print("")
    show_help()
    sys.exit(1)


chirp_sensor = chirp.Chirp(address=chirp_address,
                    read_moist=True,
                    read_temp=True,
                    read_light=True,
                    min_moist=0,
                    max_moist=1000,
                    temp_scale='celsius',
                    temp_offset=0)


try:
    chirp_sensor.sensor_address = new_addr
    print(" Chirp address changed from " + str(text_address) + " to " + str(text_new_address))
except IOError:
    print("   Attempted to change chirp sensor at " + str(text_address) + " to " + str(text_new_address))
    print(" Chirp module reported an IOError, either the address was wrong")
    print(" or the chirp sensor isn't responding correctly.")
    print(" ")
    raise
except:
    print(" Unexpected error ")
    raise
