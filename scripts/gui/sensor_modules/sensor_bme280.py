#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=i2c")
        print("connection_address_list=0x77, 0x76")
        print("default_connection_address=0x76")



def read_sensor(location="", extra="", sensor_name="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    try:
        import board
        import busio
        import adafruit_bme280
    except:
        print("bme280 module not installed, install using the command;")
        print("   sudo pip3 install adafruit-circuitpython-bme280   ")
        return None


    # set up and read the sensor
    read_attempt = 1
    i2c = busio.I2C(board.SCL, board.SDA)
    i2c_address = location
    if location == "0x76":
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x76)
    elif location == "0x77":
        bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, 0x77)

    while read_attempt < 5:
        try:
            temperature = bme280.temperature
            humidity = bme280.humidity
            pressure = bme280.pressure
            #
            if humidity == None or temperature == None or humidity > 101:
                print("--problem reading bme280, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                humidity = round(humidity,2)
                temperature = round(temperature, 2)
                pressure = round(pressure, 2)
                logtime = datetime.datetime.now()
                return [['time',logtime], ['humid', humidity], ['temperature', temperature], ['pressure', pressure]]
        except Exception as e:
            print("--exception while reading bme280, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The BME280 has to possible i2c addresses,
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
            print(" Modular control for BME280 temp sensors")
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
    if not sensor_location == "":
        output = read_sensor(location=sensor_location)
    else:
        print(" No sensor address supplied, this requries a sensor address.")
        sys.exit()
    #
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
