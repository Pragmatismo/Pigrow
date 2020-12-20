#!/usr/bin/python3
import os

def show_info():
    # conected network
    # Read the currently connected network name
    out =  os.popen("/sbin/iwgetid").read()
    try:
        network_name = out.split('"')[1]
        return network_name
    except Exception as e:
        return "Unable to read network."

    return network_name


if __name__ == '__main__':
    print(show_info())
