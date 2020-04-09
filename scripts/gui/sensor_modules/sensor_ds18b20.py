#!/usr/bin/python3
class sensor_config():
    connection_type="1wire"
    connection_address_list=["28-021312cdd1aa"]
    default_connection_address=""


def read_sensor(location="", *args):
    import datetime
    print(location)
    # set up and read the sensor
    sensor_path = "/sys/bus/w1/devices/" + location + "/w1_slave"
    try:
        with open(sensor_path, "r") as sensor_data:
            sensor_reading = sensor_data.read()
        temp = sensor_reading.split("\n")[1].split(" ")[9]
        temp = float(temp[2:]) / 1000
    except:
        print("--problem reading ds18b20")
        temp = None
        return None

    logtime = datetime.datetime.now()
    return [['time',logtime], ['temp', temp]]


if __name__ == '__main__':
    '''
      The ds18b20
      '''

    output = read_sensor()
    if output == None:
        print("!! Failed to read !!")
    else:
        for x in output:
            print(str(x[0]) + "=" + str(x[1]))
