#!/usr/bin/python3
import os

def show_info():
    # conected network
    # Read the currently connected network name
    out =  os.popen("/sbin/iwgetid").read()
    try:
        network_name = out.split('"')[1]
    except Exception as e:
        network_name = "Unable to read network."

    # read signal strength
    out =  os.popen("iwconfig wlan0 | grep -i quality").read()
    network_name += "\n" + out.strip()    

    return network_name


if __name__ == '__main__':
    print(show_info())
