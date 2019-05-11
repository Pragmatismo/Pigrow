#!/usr/bin/python3
import datetime
import praw           #sudo pip3 install praw
import sys
import os

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
    script = 'reddit_message.py'
except:
    print("pigrow_defs not found, can't survive without...")
    print("make sure pigrow software is installed correctly")
    sys.exit()

#    This script looks in dirlocs.txt for the reddit user information


# Default locations
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
message = "Reddit_message.py has been triggered "

#
# Command line arguments
#
for argu in sys.argv:
    argu_l = argu.lower()
    if argu_l == '-h' or argu_l == '--help':
        print(" Reddit Message Trigger Script")
        print(" ")
        print("     Use this to send a message on reddit via the pigrows")
        print("     associated account as found in ~/Pigrow/config/dirlocs.txt")
        print("     this must include ")
        print("                       my_client_id=")
        print("                       my_client_secret=")
        print("                       my_username=")
        print("                       my_password=")
        print("                       watcher_name=")
        print("     watcher_name is who you send the message to")
        print("     ")
        print('  message="message here"')
        ptint("             The message which is sent to the watcher")
        sys.exit(0)
    elif argu_l == "-flags":
        print("path_dirloc=" + str(loc_locs))
        print("message=")
        sys.exit(0)
    elif "=" in argu:
        thearg = str(argu_l).split('=')[0]
        theval = str(argu).split('=')[1]
        if thearg == 'loc_locs' or thearg == "path_dirloc":
            loc_locs = theval
        elif thearg == "message":
            message=theval

print("")
print("        #############################################")
print("      ##           Reddit Message Trigger            ##")
print("       ##                                           ##")
print("")

#
# load location information and reddit log in details
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

def load_reddit_login(loc_dic):
    my_user_agent= 'Pigrow sensor driven message trigger (by /u/The3rdWorld)'
    try:
        my_client_id = loc_dic['my_client_id']
        my_client_secret = loc_dic['my_client_secret']
        my_username = loc_dic['my_username']
        my_password = loc_dic['my_password']
        watcher_name = loc_dic['watcher_name']
    except:
        print("REDDIT SETTINGS NOT SET - Edit into the file " + str(loc_locs))
        print("                        - This is easiest done in the remote_gui")
        raise
    return my_user_agent, my_client_id, my_client_secret, my_username, my_password, watcher_name

def log_in_reddit(my_user_agent, my_client_id, my_client_secret, my_username, my_password):
    print("logging in as " + str(my_username))
    reddit = praw.Reddit(user_agent=my_user_agent,
                         client_id=my_client_id,
                         client_secret=my_client_secret,
                         username=my_username,
                         password=my_password)
    return reddit

def send_message(reddit, box_name, watcher_name):
    title = "Message from PiGrow " + box_name
    reddit.redditor(watcher_name).message(title, message)
    print("Message has been sent to " + watcher_name)
    print("    " + message)


if __name__ == '__main__':
    ## Load logs and log on
    loc_dic, set_dic, err_log, box_name = load_settings(loc_locs)
    my_user_agent, my_client_id, my_client_secret, my_username, my_password, watcher_name = load_reddit_login(loc_dic)
    reddit = log_in_reddit(my_user_agent, my_client_id, my_client_secret, my_username, my_password)
    send_message(reddit, box_name, watcher_name)
