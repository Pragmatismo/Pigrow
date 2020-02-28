#!/usr/bin/python3
class sensor_config():
    print(" Sensor config module run ")
    connection_type="i2c"
    connection_address_list=["0x40"]
    default_connection_address="0x40"


def read_sensor():
    # Try importing the modules then give-up and report to user if it fails
    import datetime
    try:
        import board
        import busio
        import adafruit_si7021
    except:
        print("adafruit_si7021 module not installed, install using the command;")
        print("     sudo pip3 install adafruit-circuitpython-si7021")
        return None

    # set up and read the sensor
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        sensor = adafruit_si7021.SI7021(i2c)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        if humidity == None or temperature == None or humidity > 101:
            print("--problem reading si7021")
            return None
        else:
            humidity = round(humidity,2)
            temperature = round(temperature, 2)
            logtime = datetime.datetime.now()
            return [['time',logtime], ['humid', humidity], ['temperature', temperature]]
    except:
        print("--problem reading si7021")
        return None


if __name__ == '__main__':
    '''
      The si7021 requires no configuration because it has no settings and can't change address
      '''
    output = read_sensor()
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
