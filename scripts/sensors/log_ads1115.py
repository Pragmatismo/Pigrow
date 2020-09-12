#!/usr/bin/python3
import os
import sys
import time
import datetime
try:
    import board
    import busio
    import adafruit_ads1x15
    from adafruit_ads1x15.analog_in import AnalogIn
except:
    print("Adafruit ADS1x15 python module not installed, use the remote gui to do so")
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
max_volt = 3.2767
round_to = 4
val0_max_trigger = ""
val1_max_trigger = ""
val2_max_trigger = ""
val3_max_trigger = ""
val0_min_trigger = ""
val1_min_trigger = ""
val2_min_trigger = ""
val3_min_trigger = ""
val0_max_script = ""
val1_max_script = ""
val2_max_script = ""
val3_max_script = ""
val0_min_script = ""
val1_min_script = ""
val2_min_script = ""
val3_min_script = ""

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
        print("      use gain to set input voltage range: ")
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
        print("     situations. For faster readings use a higher value.")
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
        print("")
        print(" max_volt=3.2767")
        print("            set the maximum voltage used to calculate percent and centralise")
        print("")
        print(" round=4")
        print("            Round log values to N decimal places")
        print("")
        print(" max_trigger=2.5 max_script=/home/pi/Pigrow/scripts/...")
        print("           Set a max value above which it'll trigger the script")
        print("           Values are in the same units as the log is recorded, ")
        print("           If you want to call a script and supply command line arguments")
        print("           you should create a .sh file containing the path and those arguments")
        print(" val0_max_trigger, val0_max_script, val1_max_trigger, etc for individual channels")
        print("")
        print(" min_trigger=2.5 min_script=/home/pi/Pigrow/scripts/...")
        print("           Same as above but triggers using minimum values")
        print(" val0_min_trigger, val0_min_script, val1_min_trigger, etc for individual channels")
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
        print("max_volt=3.2767")
        print("round=4")
        print("max_trigger=")
        print("val0_max_trigger=")
        print("val1_max_trigger=")
        print("val2_max_trigger=")
        print("val3_max_trigger=")
        print("min_trigger=")
        print("val0_min_trigger=")
        print("val1_min_trigger=")
        print("val2_min_trigger=")
        print("val3_min_trigger=")
        print("max_script=")
        print("val0_max_script=")
        print("val1_max_script=")
        print("val2_max_script=")
        print("val3_max_script=")
        print("min_script=")
        print("val0_min_script=")
        print("val1_min_script=")
        print("val2_min_script=")
        print("val3_min_script=")
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
        elif thearg == "max_volt":
            try:
                max_volt=float(thevalue)
            except:
                print("!!! max_volt= must be a number, using default ")
        elif thearg == "round":
            try:
                round_to = int(thevalue)
            except:
                print("!!! round= must be a number, using default of 4")
        # Settings for triggering scripts
        # max
        elif thearg == "max_trigger":
            val0_max_trigger = float(thevalue)
            val1_max_trigger = float(thevalue)
            val2_max_trigger = float(thevalue)
            val3_max_trigger = float(thevalue)
        elif thearg == "val0_max_trigger":
            val0_max_trigger = float(thevalue)
        elif thearg == "val1_max_trigger":
            val1_max_trigger = float(thevalue)
        elif thearg == "val2_max_trigger":
            val2_max_trigger = float(thevalue)
        elif thearg == "val3_max_trigger":
            val3_max_trigger = float(thevalue)
        # min
        elif thearg == "min_trigger":
            val0_min_trigger = float(thevalue)
            val1_min_trigger = float(thevalue)
            val2_min_trigger = float(thevalue)
            val3_min_trigger = float(thevalue)
        elif thearg == "val0_min_trigger":
            val0_min_trigger = float(thevalue)
        elif thearg == "val1_min_trigger":
            val1_min_trigger = float(thevalue)
        elif thearg == "val2_min_trigger":
            val2_min_trigger = float(thevalue)
        elif thearg == "val3_min_trigger":
            val3_min_trigger = float(thevalue)
        # setting script paths
        # max
        elif thearg == "max_script":
            val0_max_script = argu.split('=')[1]
            val1_max_script = argu.split('=')[1]
            val2_max_script = argu.split('=')[1]
            val3_max_script = argu.split('=')[1]
        elif thearg == "val0_max_script":
            val0_max_script = argu.split('=')[1]
        elif thearg == "val1_max_script":
            val1_max_script = argu.split('=')[1]
        elif thearg == "val2_max_script":
            val2_max_script = argu.split('=')[1]
        elif thearg == "val3_max_script":
            val3_max_script = argu.split('=')[1]
        # min
        elif thearg == "min_script":
            val0_min_script = argu.split('=')[1]
            val1_min_script = argu.split('=')[1]
            val2_min_script = argu.split('=')[1]
            val3_min_script = argu.split('=')[1]
        elif thearg == "val0_min_script":
            val0_min_script = argu.split('=')[1]
        elif thearg == "val1_min_script":
            val1_min_script = argu.split('=')[1]
        elif thearg == "val2_min_script":
            val2_min_script = argu.split('=')[1]
        elif thearg == "val3_min_script":
            val3_min_script = argu.split('=')[1]


#setting up the adafruit sensor drivers
i2c = busio.I2C(board.SCL, board.SDA)
invalid_pin_message = "invalid pin address, try gnd vdd sda or scl instead"

if sensor_type == "ads1115":
    import adafruit_ads1x15.ads1115 as ADS
    if pin_address == "gnd":
        adc = ADS.ADS1115(i2c, address=0x48)
    elif pin_address == "vdd":
        adc = ADS.ADS1115(i2c, address=0x49)
    elif pin_address == "sda":
        adc = ADS.ADS1115(i2c, address=0x4A)
    elif pin_address == "scl":
        adc = ADS.ADS1115(i2c, address=0x4B)
    else:
        print(invalid_pin_message)
        sys.exit()
elif sensor_type == "ads1015":
    import adafruit_ads1x15.ads1015 as ADS
    if pin_address == "gnd":
        adc = ADS.ADS1015(i2c, address=0x48)
    elif pin_address == "vdd":
        adc = ADS.ADS1015(i2c, address=0x49)
    elif pin_address == "sda":
        adc = ADS.ADS1015(i2c, address=0x4A)
    elif pin_address == "scl":
        adc = ADS.ADS0115(i2c, address=0x4B)
    else:
        print(invalid_pin_message)
        sys.exit()


print("using log path: " + str(log_path))

def set_channels():
    chan0 = AnalogIn(adc, ADS.P0)
    chan1 = AnalogIn(adc, ADS.P1)
    chan2 = AnalogIn(adc, ADS.P2)
    chan3 = AnalogIn(adc, ADS.P3)
    return [chan0, chan1, chan2, chan3]

def read_adc(channels):
    vals=["","","",""]
    # chan 0
    adc.gain = GAIN0
    if show_as_0 == "volt" or show_as_0 == "percent":
        vals[0] = channels[0].voltage
    else:
        vals[0] = channels[0].value
    # chan 1
    adc.gain = GAIN1
    if show_as_1 == "volt" or show_as_1 == "percent":
        vals[1] = channels[1].voltage
    else:
        vals[1] = channels[1].value
    # chan 2
    adc.gain = GAIN2
    if show_as_2 == "volt" or show_as_2 == "percent":
        vals[2] = channels[2].voltage
    else:
        vals[2] = channels[2].value
    # chan 3
    adc.gain = GAIN3
    if show_as_3 == "volt" or show_as_3 == "percent":
        vals[3] = channels[3].voltage
    else:
        vals[3] = channels[3].value
    return vals


def convert_to_percent(vals):
    max_value = max_volt
    
    if show_as_0 == "percent":
        vals[0] = float(vals[0]) / float(max_volt) * 100
    if show_as_1 == "percent":
        vals[1] = float(vals[1]) / float(max_volt) * 100
    if show_as_2 == "percent":
        vals[2] = float(vals[2]) / float(max_volt) * 100
    if show_as_3 == "percent":
        vals[3] = float(vals[3]) / float(max_volt) * 100
    return vals

def centralise_posneg(vals):
    halfway_point = max_volt / 2
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
    if not vals == ["","","",""]:
        # add date
        timenow = str(datetime.datetime.now())
        log_entry  = timenow + ">"
        # list vals
        for val in vals:
            log_entry += str(round(val, round_to)) + ">"
        log_entry = log_entry[:-1]
        log_entry += "\n"
        # write to file
        if not log_path.lower() == "none":
            with open(log_path, "a") as f:
                f.write(log_entry)
        print("Written: " +  log_entry)


def trigger_on_value(vals):
    # check to see if high thresholds have been broken
    if not val0_max_trigger == "" and not val0_max_script == "":
        if vals[0] > val0_max_trigger:
            print("Channel 0 exceeded it's maximum threshold, running " + val0_max_script)
            os.system(val0_max_script)
    if not val1_max_trigger == "" and not val1_max_script == "":
        if vals[1] > val1_max_trigger:
            print("Channel 1 exceeded it's maximum threshold, running " + val1_max_script)
            os.system(val1_max_script)
    if not val2_max_trigger == "" and not val2_max_script == "":
        if vals[2] > val2_max_trigger:
            print("Channel 2 exceeded it's maximum threshold, running " + val2_max_script)
            os.system(val2_max_script)
    if not val3_max_trigger == "" and not val3_max_script == "":
        if vals[3] > val3_max_trigger:
            print("Channel 3 exceeded it's maximum threshold, running " + val3_max_script)
            os.system(val3_max_script)
    # Check to see if low threashold has been broken
    if not val0_min_trigger == "" and not val0_min_script == "":
        if vals[0] < val0_min_trigger:
            print("Channel 0 went under it's minimum threshold, running " + val0_min_script)
            os.system(val0_min_script)
    if not val1_min_trigger == "" and not val1_min_script == "":
        if vals[1] < val1_min_trigger:
            print("Channel 1 went under it's minimum threshold, running " + val1_min_script)
            os.system(val1_min_script)
    if not val2_min_trigger == "" and not val2_min_script == "":
        if vals[2] < val2_min_trigger:
            print("Channel 2 went under it's minimum threshold, running " + val2_min_script)
            os.system(val2_min_script)
    if not val3_min_trigger == "" and not val3_min_script == "":
        if vals[3] < val3_min_trigger:
            print("Channel 3 went under it's minimum threshold, running " + val3_min_script)
            os.system(val3_min_script)



if __name__ == '__main__':
    channels = set_channels()
    vals = read_adc(channels)
    if not vals == ["","","",""]:
        vals = centralise_posneg(vals)
        vals = convert_to_percent(vals)
        log_ads1115(log_path, vals)
        trigger_on_value(vals)
        #print vals
    else:
        print("failed to find results")
