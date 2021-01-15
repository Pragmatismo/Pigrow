#!/usr/bin/python3
import os
homedir = os.getenv("HOME")

def show_info():
    # conected network
    # Read the currently connected network name
    caps_path = homedir + "/Pigrow/caps/"
    file_list = []
    if os.path.isdir(caps_path):
        out =  os.popen("ls " + caps_path).read()
        file_list = out.split()
        file_list.sort()

    if len(file_list) > 0:
        return caps_path + file_list[-1]
    else:
        return "none"


if __name__ == '__main__':
    print(show_info())
