#!/usr/bin/python3
import os

def show_info():



    # read /etc/wpa_supplicant/wpa_supplicant.conf for listed wifi networks
    out =  os.popen("sudo cat /etc/wpa_supplicant/wpa_supplicant.conf").read()
    out = out.splitlines()
    in_a_list = False
    network_items = []
    network_list = []
    for line in out:
        if "}" in line:
            in_a_list = False
            # list finished sort into fields
            ssid = ""
            psk = ""
            key_mgmt = ""
            other = ""
            for x in network_items:
                if "ssid=" in x:
                    ssid = x[5:]
                elif "psk=" in x:
                    psk = x[4:]
                    psk = "(password hidden)"
                elif "key_mgmt=" in x:
                    key_mgmt = x[9:]
                else:
                    other = other + ", "
            network_list.append([ssid, key_mgmt, psk, other])
            network_items = []
        if in_a_list == True:
            network_items.append(line.strip())
        if "network" in line:
            in_a_list = True
    network_text = "Networks saved in wpa_supplicant.conf; \n"
    for item in network_list:
        for thing in item:
            network_text += thing + " "
        network_text += "\n"
    return network_text

if __name__ == '__main__':
    print(show_info())
