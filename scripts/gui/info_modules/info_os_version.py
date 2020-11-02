#!/usr/bin/python3
import os

def show_info():
    #check pi to determin os version
    os_name = "Undetermined"
    out =  os.popen("cat /etc/os-release").read()
    for line in out.split("\n"):
        if "PRETTY_NAME=" in line:
            os_name = line.split('"')[1]
    return os_name

if __name__ == '__main__':
    print(show_info())
