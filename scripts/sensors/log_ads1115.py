#!/usr/bin/python
import os
import sys
import time
import datetime
try:
    import Adafruit_ADS1x15 #Requires adafruit ads1x15 installed
except:
    print("Adafruit ADS1x15 python module not installed, instructions can be found easily via goodle")
    sys.exit()
#default values for setting up the adafruit ads1x15 module
GAIN0 = 1
GAIN1 = 1
GAIN2 = 1
GAIN3 = 1
samples_per_second0 = 8
samples_per_second1 = 8
samples_per_second2 = 8
samples_per_second3 = 8
show_as_0 = "raw" #"volt", "percent"
show_as_1 = "raw"
show_as_2 = "raw"
show_as_3 = "raw"
centralise0 = False
centralise1 = False
centralise2 = False
centralise3 = False
pin_address = "gnd"  #gnd,vdd,sda,sdl - use lower case because argu gets lowercased
i2c_busnum = 1
sensor_type = "ads1115"
convert_volt = True #set false to record results without conversion
centralise = False #set false not to centralise

homedir = os.environ['HOME']

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'log_ads1115.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    log_path = loc_dic['log_path']
    log_path = log_path + "ads1115_log.txt"
except Exception as e:
    print("Using Defaults because - " + str(e))
    log_path = homedir + "/Pigrow/logs/ads1115_log.txt"

for argu in sys.argv[1:]:
    argu_l = str(argu).lower()
    if argu_l == 'help' or argu_l == '-h' or argu_l == '--help':
        print(" Script for logging ADS1115 Analogue to Digital Converter ")
        print(" ")
        print(" log=" + homedir + "/Pigrow/logs/ads1115_log.txt")
        print(" ")
        print(" gain=1")
        print("      use gain to set input voltage range; ")
        print("      2/3 = +/-6.144V/\n      1 = +/-4.096V\n      2 = +/-2.048V\n      4 = +/-1.024V\n      8 = +/-0.512V\n      16 = +/-0.256V")
        print("      if you're unsure then set to 1 and increase")
        print("      if all values are towards the bottom of the graph.")
        print("    gain0, GAIN0, GAIN1, GAIN2 all apply to individual channels")
        print("")
        print(" address=gnd ")
        print("      the address of the ADS1115 on the i2c register as")
        print("      determined by connecting the ADDR pin to one of the following options")
        print("      GND - (0x48)\n      VDD - (0x49)\n      SDA - (0x4A)\n      SCL - (0x4B)")
        print("")
        print(" sensor_type=ads1115")
        print("            select either ads1015 or ads1115 ")
        print("")
        print(" sps=8")
        print("     samples per second")
        print("       ads1015 - 128, 250, 490, 920, 1600, 2400, 3300")
        print("       ads1115 - 8, 16, 32, 64, 128, 250, 475, 860")
        print("     at low values the average voltage is taken over")
        print("     a longer period which can be useful in some")
        print("     situations, for faster readings use a higher value.")
        print("   sps0, sps1, sps2, sps3 all apply to individual channels")
        print("")
        print(" show=volt / percent / raw")
        print("             Shows either the raw data, volts or a percentage ")
        print("             -volt calculations reference the gain value. ")
        print("  show0, show1, show2, show3 apply to individual channels")
        print("")
        print(" centralise=true")
        print("             Centralises the data for sensors with +- values")
        print("  centralise0, centralise1, centralise2, centralise3 for individual channels")
        sys.exit()
    elif argu_l == '-flags':
        print("log=[LOG_PATH]")
        print("pin_address=[0,1]")
        print("i2c_busnum=[gnd,vdd,sda,scl]")
        print("sensor_type=[ads1115, ads1015]")
        print("gain=[2/3,1,2,4,8,16]")
        print("gain0=[2/3,1,2,4,8,16]")
        print("gain1=[2/3,1,2,4,8,16]")
        print("gain2=[2/3,1,2,4,8,16]")
        print("gain3=[2/3,1,2,4,8,16]")
        print("sps=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("sps0=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("sps1=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("sps2=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("sps3=[8,16,32,64,128,250,475,860,/ads1015,128,250,490,920,1600,2400,3300]")
        print("show=[volt,percent,raw]")
        print("show0=[volt,percent,raw]")
        print("show1=[volt,percent,raw]")
        print("show2=[volt,percent,raw]")
        print("show3=[volt,percent,raw]")
        print("centralise=[true,false]")
        print("centralise0=[true,false]")
        print("centralise1=[true,false]")
        print("centralise2=[true,false]")
        print("centralise3=[true,false]")
        sys.exit()
    elif "=" in argu_l:
        thearg = argu_l.split('=')[0]
        thevalue = argu_l.split('=')[1]
        if thearg == 'log' or thearg == 'log_path':
            log_path = argu.split('=')[1]
        elif thearg == 'address':
            pin_address = thevalue
        elif thearg == 'bus' or thearg == 'busnum':
            i2c_busnum = int(thevalue)
        elif thearg == 'sensor_type' or thearg == 'sensor':
            sensor_type = thevalue
        elif thearg == 'gain':
            GAIN0 = int(thevalue)
            GAIN1 = int(thevalue)
            GAIN2 = int(thevalue)
            GAIN3 = int(thevalue)
        elif thearg == 'gain0':
            GAIN0 = int(thevalue)
        elif thearg == 'gain1':
            GAIN1 = int(thevalue)
        elif thearg == 'gain2':
            GAIN2 = int(thevalue)
        elif thearg == 'gain3':
            GAIN3 = int(thevalue)
        elif thearg == 'samples_per_second' or thearg == 'sps':
            samples_per_second0 = int(thevalue)
            samples_per_second1 = int(thevalue)
            samples_per_second2 = int(thevalue)
            samples_per_second3 = int(thevalue)
        elif thearg == 'samples_per_second0' or thearg == 'sps0':
            samples_per_second0 = int(thevalue)
        elif thearg == 'samples_per_second1' or thearg == 'sps1':
            samples_per_second1 = int(thevalue)
        elif thearg == 'samples_per_second2' or thearg == 'sps2':
            samples_per_second2 = int(thevalue)
        elif thearg == 'samples_per_second3' or thearg == 'sps3':
            samples_per_second3 = int(thevalue)
        elif thearg == 'show' or thearg == 'show_as':
            show_as_0 = thevalue
            show_as_1 = thevalue
            show_as_2 = thevalue
            show_as_3 = thevalue
        elif thearg == 'show0' or thearg == 'show_as':
            show_as_0 = thevalue
        elif thearg == 'show1' or thearg == 'show_as':
            show_as_1 = thevalue
        elif thearg == 'show2' or thearg == 'show_as':
            show_as_2 = thevalue
        elif thearg == 'show3' or thearg == 'show_as':
            show_as_3 = thevalue
        elif thearg == "centralise":
            centralise0 = thevalue
            centralise1 = thevalue
            centralise2 = thevalue
            centralise3 = thevalue
        elif thearg == "centralise0":
            centralise0 = thevalue
        elif thearg == "centralise1":
            centralise1 = thevalue
        elif thearg == "centralise2":
            centralise2 = thevalue
        elif thearg == "centralise3":
            centralise3 = thevalue

#setting up the adafruit sensor drivers
adc = Adafruit_ADS1x15.ADS1115()
if sensor_type == "ads1115":
    if pin_address == "gnd":
        adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=i2c_busnum)
    elif pin_address == "vdd":
        adc = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=i2c_busnum)
    elif pin_address == "sda":
        adc = Adafruit_ADS1x15.ADS1115(address=0x4A, busnum=i2c_busnum)
    elif pin_address == "scl":
        adc = Adafruit_ADS1x15.ADS1115(address=0x4B, busnum=i2c_busnum)
    else:
        print("invalid pin address, try gnd vdd sda or scl instead")
        sys.exit()
elif sensor_type == "ads1015":
    if pin_address == "gnd":
        adc = Adafruit_ADS1x15.ADS1015(address=0x48, busnum=i2c_busnum)
    elif pin_address == "vdd":
        adc = Adafruit_ADS1x15.ADS1015(address=0x49, busnum=i2c_busnum)
    elif pin_address == "sda":
        adc = Adafruit_ADS1x15.ADS1015(address=0x4A, busnum=i2c_busnum)
    elif pin_address == "scl":
        adc = Adafruit_ADS1x15.ADS1015(address=0x4B, busnum=i2c_busnum)
    else:
        print("invalid pin address, try gnd vdd sda or scl instead")
        sys.exit()


print("using log path : " + str(log_path))


def read_adc():
    try:
        val0 = adc.read_adc(0, gain=GAIN0, data_rate=samples_per_second0)
        val1 = adc.read_adc(1, gain=GAIN1, data_rate=samples_per_second1)
        val2 = adc.read_adc(2, gain=GAIN2, data_rate=samples_per_second2)
        val3 = adc.read_adc(3, gain=GAIN3, data_rate=samples_per_second3)
        #print val0, val1, val2, val3
        return [val0, val1, val2, val3]
    except Exception as e:
        print("Reading sensor failed - " + str(e))
        return None

def convert_to_volt(vals):
    # 2/3 gain =  0.1875mV (default) ###(not actually default from what i can tell)
    # chan 1
    if "volt" in show_as_0:
        if GAIN0 == 1:
            vals[0] = vals[0] * 0.125
        if GAIN0 == 2:
            vals[0] = vals[0] * 0.0625
        if GAIN0 == 4:
            vals[0] = vals[0] * 0.03125
        if GAIN0 == 8:
            vals[0] = vals[0] * 0.015625
        if GAIN0 == 16:
            vals[0] = vals[0] * 0.0078125
    # chan 2
    if "volt" in show_as_1:
        if GAIN1 == 1:
            vals[1] = vals[1] * 0.125
        if GAIN1 == 2:
            vals[1] = vals[1] * 0.0625
        if GAIN1 == 4:
            vals[1] = vals[1] * 0.03125
        if GAIN1 == 8:
            vals[1] = vals[1] * 0.015625
        if GAIN1 == 16:
            vals[1] = vals[1] * 0.0078125
    # chan 3
    if "volt" in show_as_2:
        if GAIN2 == 1:
            vals[2] = vals[2] * 0.125
        if GAIN2 == 2:
            vals[2] = vals[2] * 0.0625
        if GAIN2 == 4:
            vals[2] = vals[2] * 0.03125
        if GAIN2 == 8:
            vals[2] = vals[2] * 0.015625
        if GAIN2 == 16:
            vals[2] = vals[2] * 0.0078125
    # chan 4
    if "volt" in show_as_3:
        if GAIN3 == 1:
            vals[3] = vals[3] * 0.125
        if GAIN3 == 2:
            vals[3] = vals[3] * 0.0625
        if GAIN3 == 4:
            vals[3] = vals[3] * 0.03125
        if GAIN3 == 8:
            vals[3] = vals[3] * 0.015625
        if GAIN3 == 16:
            vals[3] = vals[3] * 0.0078125
    return vals

def convert_to_percent(vals):
    if show_as_0 == "percent":
        print("Converting to percent is not yet an option, sorry")
    if show_as_1 == "percent":
        print("Converting to percent is not yet an option, sorry")
    if show_as_2 == "percent":
        print("Converting to percent is not yet an option, sorry")
    if show_as_3 == "percent":
        print("Converting to percent is not yet an option, sorry")
    return vals

def centralise_posneg(vals):
    max_value = 1635.625 * 2
    halfway_point = max_value / 2
    if centralise0 == "true":
        vals[0] = vals[0] - halfway_point
    if centralise1 == "true":
        vals[1] = vals[1] - halfway_point
    if centralise2 == "true":
        vals[2] = vals[2] - halfway_point
    if centralise3 == "true":
        vals[3] = vals[3] - halfway_point
    return vals

def log_ads1115(log_path, vals):
    if not vals == None:
        timenow = str(datetime.datetime.now())
        log_entry  = timenow + ">"
        log_entry += str(vals[0]) + ">"
        log_entry += str(vals[1]) + ">"
        log_entry += str(vals[2]) + ">"
        log_entry += str(vals[3]) + "\n"
        if not log_path.lower() == "none":
            with open(log_path, "a") as f:
                f.write(log_entry)
        print("Written; " +  log_entry)


if __name__ == '__main__':
    vals = read_adc()
    if not vals == None:
        vals = centralise_posneg(vals)
        vals = convert_to_volt(vals)
        vals = convert_to_percent(vals)
        log_ads1115(log_path, vals)
        #print vals
    else:
        print("failed to find results")
