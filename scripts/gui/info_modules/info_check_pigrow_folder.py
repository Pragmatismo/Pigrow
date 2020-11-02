#!/usr/bin/python3
import os

def show_info():
    folder_path = "~/Pigrow/"
    # get diskfull, required to determine percent
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

    #check Pigrow folder
    out =  os.popen("du -s " + folder_path).read().strip()
    if not "No such file or directory" in out:
        pigrow_size = out.split("\t")[0]
        try:
            folder_pcent = float(pigrow_size) / float(hdd_total) * 100
            folder_pcent = format(folder_pcent, '.2f')
        except: #mostly like due to not being a number
            folder_pcent = "Undetermined"
    else: #i.e. when no such file or directory is the error
        pigrow_size = "not found"

    if not pigrow_size == "not found":
        info = folder_path + " " + str(pigrow_size) + " (" + str(folder_pcent) +"% of total)"
    else:
        info = folder_path + " not found."


    return info

if __name__ == '__main__':
    print(show_info())
