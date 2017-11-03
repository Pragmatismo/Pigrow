#!/usr/bin/python

sensor = ""

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Test dht sensor")
        print("")
        print("This attempts to use to the Adafruit_DHT library to read the sensor ")
        print("set the pin with the command line option gpio=[GPIO NUMBER]")
        print("to set the sensor use sensor=[DHT11, DHT22, AM2302]")
        print("for example;")
        print("             ./test_dht.py gpio=18 sensor=DHT22)
        sys.exit()
    elif argu.split('=')[0] == "gpio":
        gpio = argu.split('=')[1]
    elif argu.split('=')[0] == "sensor":
        if argu.split('=')[1].lower() == 'dth22':
            sensor = "dht22"
        elif argu.split('=')[1].lower() == 'dth11':
            sensor = "dht11"
        elif argu.split('=')[1].lower() == 'am2302':
            sensor = "am2302"
# try loading adafruit module
try:
    import Adafruit_DHT
except:
    print("required Adafruit DHT code not installed.")
    sys.exit()
# set sensor for ada fruit module
if sesnor == "dht22":
    sensor = Adafruit_DHT.DHT22
elif sensor == "dht11":
    sensor = Adafruit_DHT.DHT11
elif sensor == "am2302":
    sensor = Adafruit_DHT.AM2302
else:
    sensor = Adafruit_DHT.DHT22

try:
    gpio = int(gpio)
except:
    print("GPIO must be a number, e.g. gpio=18")
    sys.exit()

humid, temp = Adafruit_DHT.read_retry(sensor, gpio)

if not humid == None and not temp == None:
    print("temp:" + temp + " humid=" humid)
else:
    print("reading failed")
