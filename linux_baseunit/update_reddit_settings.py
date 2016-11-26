#!/usr/bin/python
import datetime
import socket
import praw           #pip install --pre praw   #remove the --pre if it's now the future and praw4 is standard
import os
print("")
print("        #############################################")
print("      ##       Automatic Reddit Grow Info Updater    ##")
print("")
#print reddit.read_only

## REMEMBER TO REMOVE PASSWORD IF SHARING THE CODE!!!!
thetime = datetime.datetime.now()
#logs
loc_settings = "/home/pragmo/pigitgrow/Pigrow/config/pigrow_config.txt"
loc_switchlog = '/home/pragmo/pigitgrow/Pigrow/logs/switch_log.txt'
err_log = './err_log.txt'

###     DON'T UPLOAD TO GITHUB WITH ALL THE SECRET CODES IN!
##       THESE WILL BE STORED AS A CONFIG FILE OR SOMETHING
#

my_user_agent = "Pigrow updater tester thing V0.5 (by /u/The3rdWorld)"


print("logging in")
reddit = praw.Reddit(user_agent=my_user_agent,
                     client_id=my_client_id,
                     client_secret=my_client_secret,
                     username=my_username,
                     password=my_password)
subreddit = reddit.subreddit("Pigrow")
print(subreddit.title)


page_text = '#Pigrow Settings  \n\n'
page_text += 'This displays the current settings from the pigrow,  \n'
page_text += 'to change these settings you can message your pigrow via reddit  \n'
page_text += 'this makes it really easy to configure your device.  \n'
page_text += '  \n'

###
##     LOAD PIGROW SETTINGS file
#
pi_set = {}   #the dictionary of settings
try:
    with open(loc_settings, "r") as f:
        for line in f:
            s_item = line.split("=")
            pi_set[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
except:
    print("Settings not loaded, try running pi_setup")
    with open(err_log, "a") as f:
        line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ settings file error\n'
        f.write(line)
    print("Log writen:" + line)
page_text += '|Name|Setting|  \n'
page_text += '|---|---|  \n'
for key, value in pi_set.iteritems() :
    #print key, value
    page_text += '|' +str(key)+ '|' + str(value)  + '  \n'
###
##    LOAD SWITCH FILE
#
switch_list = []
days_to_show = 7
try:
    with open(loc_switchlog, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('There are ' + str(len(logitem)) + ' readings in the switch log.')
    oldest_allowed_date = thetime - datetime.timedelta(days=days_to_show)
    curr_line = len(logitem) - 1
except:
    print("switch not loaded, try running pi_setup")
    with open(err_log, "a") as f:
        line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ switch log file error\n'
        f.write(line)
    print("Log writen:" + line)
    raise

while curr_line >= 0:
    try:
        item = logitem[curr_line]
        item = item.split("@")
        switch_date = item[1].split(".")[0]
        w_script = item[0]
        err_detail = item[2]
        date = datetime.datetime.strptime(switch_date, '%Y-%m-%d %H:%M:%S')
        if date < oldest_allowed_date:
            break
        switch_list.append([w_script, switch_date, err_detail])
        curr_line = curr_line - 1

    except:
        print("line"+str(curr_line)+" didn't parse, ignoring")
        curr_line = curr_line - 1
    #print item
    switch_item = item

page_text += '  \n  \n'
page_text += '#Switch Log  \n  \n'
page_text += 'Showing the last ' + str(days_to_show) + ' days of activity.  \n  \n'
page_text += '|Script|Action|Time  \n'
page_text += '|---|---|---  \n'
for a in switch_list:
    page_text += '|'+a[0]+'|'+ str(a[1]) +'|'+a[2]+'  \n'
page_text += '  \n'
###

page_text += '  \n'
page_text += ' to change a setting message your pigrow (i\'m still writing this bit so...) at /u/Pigrow_salad  \n'
#determine local ip - apparently this works on macs if you change the 0 to a 1 but i don't buy apple products so...
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
local_ip_address = s.getsockname()[0]
page_text += 'Current local network IP ' + str(local_ip_address)

print page_text
praw.models.WikiPage(reddit, subreddit, 'livegrow_test_settings').edit(page_text)
