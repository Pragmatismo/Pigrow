#!/usr/bin/python
import datetime
import praw           #pip install --pre praw   #remove the --pre if it's now the future and praw4 is standard
import os
import time
import socket
import sys
print("")
print("        #############################################")
print("      ##       Listens for reddit messages           ##")
print("")


trusted_users = ['The3rdWorld', 'Pigrow_salad']
loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'

print(" - If you're me then maybe...")
print(" -    python rediit_settings_ear.py to=The3rdWorld loc_locs=/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt ")
print(" - is the command you need, maybe?")

commander = '' #default user to msg on script start set to '' for none
for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    if  thearg == 'to':
        commander = str(argu).split('=')[1]
    elif thearg == 'loc_locs':
        loc_locs = str(argu).split('=')[1]
        print("\n\n LOCS LOGS = " + str(loc_locs) + "'\n\n")
############################

#Settings for validation rules
hour_only = ['time_lamp_off', 'time_lamp_on'] #name os script that only accepts hours
valid_gpio=[2,3,4,17,27,22,10,9,11,0,5,6,13,19,26,14,15,18,23,24,25,8,7,1,12,16,20,21]  #valid gpio numbers using the gpio (BCM) NOT the board numbering system
intonly= ['heater_templow','heater_temphigh','log_frequency']

#logs default values
loc_settings = "/home/pi/Pigrow/config/pigrow_config.txt"
loc_switchlog = '/home/pi/Pigrow/logs/switch_log.txt'
err_log = './err_log.txt'
loc_dic = {}
def load_locs():
    print("Loading location details")
    try:
        with open(loc_locs, "r") as f:
            for line in f:
                s_item = line.split("=")
                loc_dic[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
    except:
        print("Settings not loaded, try running pi_setup")
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ dir locs file load error\n'
            ef.write(line)
        print("Log writen:" + line)
load_locs()
if 'loc_switchlog' in loc_dic: loc_switchlog = loc_dic['loc_switchlog']
if 'loc_settings' in loc_dic: loc_settings = loc_dic['loc_settings']
if 'err_log' in loc_dic: err_log = loc_dic['err_log']
my_user_agent= 'Pigrow updater tester thing V0.5 (by /u/The3rdWorld)'
try:
    my_client_id = loc_dic['my_client_id']
    my_client_secret = loc_dic['my_client_secret']
    my_username = loc_dic['my_username']
    my_password = loc_dic['my_password']
    subreddit = loc_dic["subreddit"]
    wiki_title = loc_dic['wiki_title']
except:
    print("REDDIT SETTINGS NOT SET - EDIT THE FILE " + str(loc_locs))
    raise



reddit = praw.Reddit(user_agent=my_user_agent,
                     client_id=my_client_id,
                     client_secret=my_client_secret,
                     username=my_username,
                     password=my_password)
print("logging in")
print(subreddit.title)
inbox = reddit.inbox
subreddit = reddit.subreddit(subreddit)

def load_settings():
    print("Loading current Settings")
    try:
        with open(loc_settings, "r") as f:
            for line in f:
                s_item = line.split("=")
                pi_set[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
    except:
        print("Settings not loaded, try running pi_setup")
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ settings file load error\n'
            ef.write(line)
        print("Log writen:" + line)


def save_settings():
    print("Saving Settings...")
    try:
        with open(loc_settings, "w") as f:
            for a,b in pi_set.iteritems():
                try:
                    s_line = str(a) +"="+ str(b) +"\n"
                    f.write(s_line)
                    print(" - Settings saved to file - ")
                    #print s_line
                except:
                    print("ERROR SETTINGS FILE ERROR SETTING NOT SAVED _ SERIOUS FAULT!")
    except:
        print("Settings not saved!")
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ settings file save error\n'
            ef.write(line)
        print("Log writen:" + line)

def change_setting(setting,value):
    if setting[0:4]=='gpio':
        gpio_setting = setting.split('_')
        if len(gpio_setting)>2:
            if gpio_setting[2] == 'on':
                if value == 'low' or value == 'high':
                    pi_set[setting]=value
                    save_settings()
                    return("GPIO on direction set to " + str(value))
                else:
                    return(" BAD VALUE - not changing the setting to a bad one!")
        else:
            try:
                if int(value) in valid_gpio:
                    #print("Valid GPIO pin selected")
                    pi_set[setting]=value
                    save_settings()
                    return("GPIO Pin set to " + str(value))
                else:
                    return("Invalid GPIO pin, not changing anything.")
            except:
                return("Invalid GPIO pin, has to be a number. No change")
    elif setting in intonly:
        try:
            value = int(value)
            #print("This is a number, great job!")
            pi_set[setting]=value
            save_settings()
            return("Set to " + str(value))
        except:
            return("Failed because this setting requires a number")

    elif setting in hour_only:
        try:
            value = int(value)
            if value in range(0,24):
                print("This is a valid hour setting, great job!")
                pi_set[setting]=value
                save_settings()
                return("Hour set to " + str(value))
            else:
                return("needs to be between 0 and 24, like a clock, sorry dogstar people timezone update coming soon...")
        except:
            return('This setting only accepts a number')

    else:
        print("No Verification rules for that setting, changing it to whatever was requested...")
        pi_set[setting]=value
        save_settings()
        return("Set to " + str(value))

def write_set(whereto='wiki'):
    page_text = '#Pigrow Settings  \n\n'
    page_text += 'This displays the current settings from the pigrow,  \n'
    page_text += 'to change these settings you can message your pigrow via reddit by simply clicking on the link in the table  \n'
    page_text += 'leave the subject as the setting you wish to change and put the new value in the body of the message.  \n'
    page_text += '  \n'
    page_text += '|Name|Setting|  \n'
    page_text += '|--:|---|  \n'
    for key, value in pi_set.iteritems() :
        #print key, value
        page_text += '|['+key+'](https://www.reddit.com/message/compose/?to='+my_username+'&subject=' +str(key)+ '&message='+str(value)+')|' + str(value)  + '  \n'
    page_text +=("")
    page_text +=("To view an explanation of each setting go see [configuring the pigrow](wiki link goes here) in the documentation ")
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
        return("FAILED DUE TO NO SWTICH LOG FILE")

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
    page_text += '|Script|Time|Event  \n'
    page_text += '|---|:-:|---  \n'
    for a in switch_list:
        page_text += '|'+a[0]+']|'+ str(a[1]) +'|'+a[2]+'  \n'
    page_text += '  \n'
    ###

    page_text += '  \n'
    page_text += '  \n'
    #determine local ip - apparently this works on macs if you change the 0 to a 1 but i don't buy apple products so...
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    local_ip_address = s.getsockname()[0]
    page_text += 'Current local network IP ' + str(local_ip_address)
    print page_text
    #return page_text
    if whereto == 'wiki':
        praw.models.WikiPage(reddit, subreddit, wiki_title).edit(page_text[0:524288])
    else:
        try:
            whereto = praw.models.Redditor(reddit, name=whereto, _data=None)
            whereto.message('Pigrow Settings', page_text[0:10000])   #, from_subreddit=subreddit)
        except:
            print("meh, some bullshit happened.")


def check_msg():
    for msg in reddit.inbox.unread():
        print("")
        print ('  - ' +msg.author)
        print ('  - ' +msg.subject)
        print ('  - ' +msg.body)
        if msg.author in trusted_users:
            print("Trusted User settings access enabled.")
            text = msg.subject
            if text in pi_set:
                reply = change_setting(str(msg.subject),str(msg.body))
                write_set('wiki')
                print(reply)
            elif text == "update wiki":
                print("wants me to update wiki... should do it themselves.")
            elif text == "msg_settings":
                write_set(msg.author)
        else:
            print("THIS IS NOT A TRUSTED USER - THEY CAN NOT EDIT SETTINGS!")
            print("")
        msg.mark_read()


###
##         Main Loop
#
pi_set = {}
#print reddit.read_only
thetime = datetime.datetime.now()

load_settings()
if not commander == '':
    write_set(commander)
while True:
    try:
        check_msg()
        time.sleep(30)
        print("all messages replied to, Looping again...")
    except:
        print("There was an error in the loop, trying again")
        #raise
