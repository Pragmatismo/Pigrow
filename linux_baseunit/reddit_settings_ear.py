#!/usr/bin/python
import datetime
import praw           #pip install --pre praw   #remove the --pre if it's now the future and praw4 is standard
import os
import time
import socket
print("")
print("        #############################################")
print("      ##       Listens for reddit messages           ##")
print("")

trusted_users = ['The3rdWorld', 'Pigrow_salad']

#print reddit.read_only

## REMEMBER TO REMOVE PASSWORD IF SHARING THE CODE!!!!
thetime = datetime.datetime.now()
#logs
loc_settings = "/home/pi/Pigrow/config/pigrow_config.txt"
loc_switchlog = '/home/pi/Pigrow/logs/switch_log.txt'
err_log = './err_log.txt'

#Settings for validation rules
hour_only = ['time_lamp_off', 'time_lamp_on'] #name os script that only accepts hours
valid_gpio=[8,12,21]  #valid gpio numbers using the gpio NOT the board numbering system
intonly= ['heater_templow','heater_temphigh','log_frequency']

###     DON'T UPLOAD TO GITHUB WITH ALL THE SECRET CODES IN!
##       THESE WILL BE STORED AS A CONFIG FILE OR SOMETHING
#


reddit = praw.Reddit(user_agent=my_user_agent,
                     client_id=my_client_id,
                     client_secret=my_client_secret,
                     username=my_username,
                     password=my_password)
print("logging in")
subreddit = reddit.subreddit("Pigrow")
wiki_title='livegrow_test_settings'
print(subreddit.title)
inbox = reddit.inbox

pi_set = {}
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

def write_set_wiki():
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
    page_text += '|Script|Time|Event  \n'
    page_text += '|---|:-:|---  \n'
    for a in switch_list:
        page_text += '|'+a[0]+']|'+ str(a[1]) +'|'+a[2]+'  \n'
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
    praw.models.WikiPage(reddit, subreddit, wiki_title).edit(page_text)


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
                write_set_wiki()
                print reply
        else:
            print("THIS IS NOT A TRUSTED USED - THEY CAN NOT EDIT SETTINGS!")
            print("")
        msg.mark_read()


load_settings()
while True:
    try:
        check_msg()
        time.sleep(6)
        print("Looping again...")
    except:
        print("There was an error in the loop, trying again")
