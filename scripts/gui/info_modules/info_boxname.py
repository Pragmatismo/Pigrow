#!/usr/bin/python3
import os

def show_info():
    # conected network
    # Read the currently connected network name
    out =  os.popen("cat ~/Pigrow/config/pigrow_config.txt | grep box_name").read()
    out = out.replace("box_name=", "").strip()

    return out


if __name__ == '__main__':
    print(show_info())
