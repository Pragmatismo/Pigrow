#!/usr/bin/python3
import sys

class sensor_config():
    # find connected sensors
    def find_settings():
        print("connection_type=gpio")
        print("connection_address_list=")
        print("default_connection_address=")



def read_sensor(location="", *args):
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    import time
    try:
        import board
        import adafruit_dht
    except:
        print("adafruit_dht22 module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-dht")
        return None


    # set up and read the sensor
    read_attempt = 1
    while read_attempt < 5:
        try:
            dht = adafruit_dht.DHT22(int(location))
            temperature = dht.temperature
            humidity = dht.humidity
            #
            if humidity == None or temperature == None or humidity > 101:
                print("--problem reading DHT22, try " + str(read_attempt))
                time.sleep(2)
                read_attempt = read_attempt + 1
            else:
                humidity = round(humidity,2)
                temperature = round(temperature, 2)
                logtime = datetime.datetime.now()
                return [['time',logtime], ['humid', humidity], ['temperature', temperature]]
        except Exception as e:
            print("--exception while reading DHT22, try " + str(read_attempt))
            print(" -- " + str(e))
            time.sleep(2)
            read_attempt = read_attempt + 1
    return None


if __name__ == '__main__':
    '''
      The DHT22 requires the location of it's signal wire
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
            print(" Modular control for dht22 temp sensors")
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
