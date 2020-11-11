#!/usr/bin/env python3
import os
import sys
import time
import datetime
from pushover import init, Client

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
    script = 'po-notify.py'
except:
    print("pigrow_defs not found, can't survive without...")
    print("make sure pigrow software is installed correctly")
    sys.exit()

#    This script looks in dirlocs.txt for the Pushover user information

# Default locations
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
message = "po-notify.py has been triggered "
##
title = "This is latest message from your pigrow"
message = "Something needs your attention"
priority = 0 # -2,-1,0,1,2
# pushover.net/api for full docs


for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if thearg == 'title' or thearg == 't':
            title = thevalue
        elif thearg == 'message' or thearg == 'm':
            message = thevalue
        elif thearg == 'priority' or 'p':
            priority = thevalue
        elif thearg == 'loc_locs' or thearg == "path_dirloc":
            loc_locs = theval

    elif argu == 'help' or argu == '-h' or argu == '--help':
        print(" Script for sending trigger notification to devices (mobile) using the PushOver API/ App")
        print("                    sign up for an account at https://pushover.net/")
        print("                   (this is a paid service unconnected to the pigrow)")
        print(" ")
        print("     associated api key and user key as found in ~/Pigrow/config/dirlocs.txt")
        print("     this must include ")
        print("          pushover_apikey=")
        print("          pushover_userkey=")
        print(" ")
        print(" title='Title of message here'")
        print(" or t='Title of message here'")
        print(" message='Content of message here'")
        print(" or m='Content of message here'")
        print(" priority='priority of message here'")
        print(" or s='priority of message here -2 lowest (no notification), -1 no sound, 0 normal, 1 high bypasses quiiet hours, 2 Emergency - repeats until acknowledged'")
        print("")
        print("")
        sys.exit(0)
    elif argu == "-flags":
        print("title='title sample'")
        print("message='message sample'")
        print("priority='-2,-1,0,1,2'")
        sys.exit(0)

#
# load location information and pushover API details
#
def load_settings(loc_locs):
    loc_dic = pigrow_defs.load_locs(loc_locs)
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'])
    if 'err_log' in loc_dic:
        err_log = loc_dic['err_log']
    else:
        err_log = 'emergency_error_log.txt'
    if 'box_name' in set_dic:
        box_name = set_dic['box_name']
    else:
        box_name = "undetermined"

    return loc_dic, set_dic, err_log, box_name

def load_pushover_login(loc_dic):
    try:
        apiKey = loc_dic['pushover_apikey']
        clientKey = loc_dic['pushover_clientkey']
    except:
        print("PUSHOVER SETTINGS NOT SET - Edit into the file " + str(loc_locs))
        print("                        - This is not yet done in the remote_gui")
        raise
    return apiKey,clientKey

def SendMessage(apiKey,clientkey,tit,mess,pri):
    init(apiKey)
    if pri == 2 or pri == "2":
        Client(clientKey).send_message(mess, title=tit, priority=pri, expire=120, retry=60)
    else:
        Client(clientKey).send_message(mess, title=tit, priority=pri)


if __name__ == '__main__':
    loc_dic, set_dic, err_log, box_name = load_settings(loc_locs)
    apiKey,clientKey = load_pushover_login(loc_dic)

    SendMessage(apiKey, clientKey, title,message,priority)
