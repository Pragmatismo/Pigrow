#!/usr/bin/python3
import os

def show_info():
    #check pi to determin hardware version
    out =  os.popen("cat /proc/device-tree/model").read()
    

    return out

if __name__ == '__main__':
    print(show_info())
