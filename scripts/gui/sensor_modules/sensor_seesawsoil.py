#!/usr/bin/python3
import sys
import time
class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x36,0x37x0x38,0x39")
        print("default_connection_address=0x36")


def read_moist(sensor):
    # read a selection of values
    moist_list = []
    for x in range(0,10):
        moist_list.append(sensor.moisture_read())
        if x == 0:
            moist0 = moist_list[-1]
        time.sleep(0.05)

    # find average
    culm = 0
    for mv in moist_list:
        culm = culm + mv
    moist = round(culm / len(moist_list), 2)

    # make list of a-b diffs
    diffs = []
    for x in range(0, len(moist_list)-1):
        dif = moist_list[x] - moist_list[x+1]
        diffs.append(abs(dif))

    # find average value difference
    culm_dif = 0
    for x in range(0, len(diffs)):
        culm_dif = culm_dif + diffs[x]
    av_dif = culm_dif / len(diffs)

    # find erratics
    to_remove =[]
    dif_fac = 1.5
    for x in range(0, len(diffs) -1):
        pairA = diffs[x]
        pairB = diffs[x+1]
        if pairA > av_dif * dif_fac and pairB > av_dif * dif_fac:
            to_remove.append(x+1)

    # remove erratics
    to_remove = sorted(to_remove, reverse=True)
    for p in to_remove:
        del moist_list[p]

    # make average value with erratics removed
    culm_moist = 0
    for x in moist_list:
        culm_moist = culm_moist + x
    erraticrem = round(culm_moist / len(moist_list), 2)

    return moist, moist0, erraticrem, len(to_remove)

def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        from adafruit_seesaw.seesaw import Seesaw
    except:
        print("adafruit seesaw module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-seesaw")
        return None

    # set up and read the sensor
    try:
        i2c = board.I2C()
        sensor = Seesaw(i2c, addr=location)
        moist, moist0, erraticrem, removed = read_moist(sensor)
        temp = sensor.get_temp()
        temp = round(temp, 2)
        logtime = datetime.datetime.now()
        return [['time',logtime], ['moist', moist], ['spotmoist',moist0], ['remerat', erraticrem], ['removed', removed], ['temp', temp]]
    except:
        print("--problem reading SeeSaw Stemma soil moisture sensor")
        return None


if __name__ == '__main__':
    '''
      The SeeSaw stemma has four selectable addresses
          ##
          ##
          ##  THIS DOES NOT YET LET YOU SET DIFFERENT ADDRESSES
          ##
          ##
      '''
     # check for command line arguments
    sensor_location = "0x36"
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for SeeSaw Stemma soil moisture sensors")
            print(" ")
            print("")
            print(" -config  ")
            print("        display the config information")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            sys.exit(0)
        elif argu == "-config":
            sensor_config.find_settings()
            sys.exit()
    # read sensor
    output = read_sensor(location=sensor_location)
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
