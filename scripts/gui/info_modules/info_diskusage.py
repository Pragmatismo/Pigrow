#!/usr/bin/python3
import os

def show_info():
    #check pi for hdd/sd card space
    out =  os.popen("df -l /").read()
    if len(out) > 1:
        responce_list = []
        for item in out.split(" "):
            if len(item) > 0:
                responce_list.append(item)

        hdd_total = responce_list[-5]
        hdd_percent = responce_list[-2]
        hdd_available = responce_list[-3]
        hdd_used = responce_list[-4]

        info  = "Total     = " + hdd_total + " KB\n"
        info += "Available = " + hdd_available + " KB\n"
        info += "Used      = " + hdd_available + " KB ("+ hdd_percent +"%)\n"

    return info

if __name__ == '__main__':
    print(show_info())
