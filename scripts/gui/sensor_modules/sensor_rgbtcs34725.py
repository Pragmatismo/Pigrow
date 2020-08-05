#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=")
        print("default_connection_address=")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    try:
        import board
        import busio
        import adafruit_tcs34725
    except:
        print("adafruit_tcs34725 module not installed, install using the command;")
        print("   sudo pip3 install adafruit-circuitpython-tcs34725   ")
        return None


    # set up and read the sensor
    read_attempt = 1
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tcs34725.TCS34725(i2c)
    gain = 1
    sensor.gain = gain  # 1, 4, 16, 60
    sensor.integration_time = 50  # The integration time of the sensor in milliseconds.  Must be a value between 2.4 and 614.4.
    while read_attempt < 5:
        try:
            color_temp = sensor.color_temperature
            lux = sensor.lux
            rgb = sensor.color_rgb_bytes
            #
            if lux == None:
                print("--problem reading tcs34725, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                logtime = datetime.datetime.now()
                return [['time',logtime], ['lux', str(lux / gain)], ['color_temp', color_temp], ['r', rgb[0]], ['g', rgb[1]], ['b', rgb[2]]]
        except Exception as e:
            print("--exception while reading tcs34725, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The tcs34725 only has one possible i2c addresses,
      '''
     # check for command line arguments
    sensor_location = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'location':
                sensor_location = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Modular control for tcs34725 RGB color sensors")
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
    #if not sensor_location == "":
    output = read_sensor(location=sensor_location)
    #else:
    #    print(" No sensor address supplied, this requries a sensor address.")
    #    sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
