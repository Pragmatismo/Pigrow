#!/usr/bin/python3
import os

def show_info():
    temp_sensor_list = ""
    out =  os.popen("ls /sys/bus/w1/devices").read()
    w1_bus_folders = out.splitlines()
    for folder in w1_bus_folders:
        if folder[0:3] == "28-":
            temp_sensor_list += folder + "\n"
    if temp_sensor_list.strip() == "":
        return "No w1 ds18b temp sensors found"
    return temp_sensor_list.strip()

if __name__ == '__main__':
    print(show_info())
