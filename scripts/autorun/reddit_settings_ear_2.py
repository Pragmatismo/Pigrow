#!/usr/bin/python
import datetime
import praw           #pip install --pre praw   #remove the --pre if it's now the future and praw4 is standard
import os
import time
import socket
import sys
sys.path.append('/home/pi/Pigrow/scripts/')
script = 'reddit_settings_ear_2.py'
import pigrow_defs

#logs default values
loc_settings = "/home/pi/Pigrow/config/pigrow_config.txt"
loc_switchlog = '/home/pi/Pigrow/logs/switch_log.txt'
err_log = './'
loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'


watcher_name = '' #default user to msg on script start set to '' for none
for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    if  thearg == 'to':
        watcher_name = str(argu).split('=')[1]
    elif thearg == 'loc_locs':
        loc_locs = str(argu).split('=')[1]
        print("\n\n LOCS LOGS = " + str(loc_locs) + "'\n\n")


#Settings for validation rules
hour_only = ['time_lamp_off', 'time_lamp_on'] #name os script that only accepts hour:min
valid_gpio=[2,3,4,17,27,22,10,9,11,0,5,6,13,19,26,14,15,18,23,24,25,8,7,1,12,16,20,21]  #valid gpio numbers using the gpio (BCM) NOT the board numbering system
intonly= ['heater_templow','heater_temphigh','log_frequency']


loc_dic = pigrow_defs.load_locs("/home/pi/Pigrow/config/dirlocs.txt")


if 'loc_switchlog' in loc_dic: loc_switchlog = loc_dic['loc_switchlog']
if 'loc_settings' in loc_dic: loc_settings = loc_dic['loc_settings']
if 'err_log' in loc_dic: err_log = loc_dic['err_log']
my_user_agent= 'Pigrow updater tester thing V0.6 (by /u/The3rdWorld)'
try:
    my_client_id = loc_dic['my_client_id']
    my_client_secret = loc_dic['my_client_secret']
    my_username = loc_dic['my_username']
    my_password = loc_dic['my_password']
except:
    message = "REDDIT SETTINGS NOT FOUND IN " + str(loc_locs)
    pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    raise
try:
    subreddit = loc_dic["subreddit"]
    wiki_title = loc_dic['wiki_title']
    live_wiki_title = loc_dic['live_wiki_title']
    use_wiki = True
except:
    message = "No subreddit details set, can't update live pages"
    pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    subreddit = ''
    wiki_title = ''
    live_wiki_title = ''
    use_wiki = False
try:
    watcher_name = loc_dic['watcher_name']
    use_watcher = True
except:
    watcher_name = ''
    use_watcher = False
    message = "No trusted user provided, can't recieve orderes"
    pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
if use_wiki == False and use_watcher == False:
    message = "Sorry but without a wiki OR a trusted user there's nothing i can do..."
    pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    sys.exit()


def is_connected():
    site = "www.reddit.com"
    try:
        host = socket.gethostbyname(site)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

def log_in():
    global reddit, inbox, subreddit
    try:
        print("logging in")
        reddit = praw.Reddit(user_agent=my_user_agent,
                             client_id=my_client_id,
                             client_secret=my_client_secret,
                             username=my_username,
                             password=my_password)
        inbox = reddit.inbox
        subreddit = reddit.subreddit(subreddit)
        print "Connected to reddit, found subreddit; " + str(subreddit.title)
        pigrow_defs.write_log(script, 'Initialized and logged into reddit.', loc_dic['loc_switchlog'])
        return True
    except Exception as e:
        message = 'Failed to log into reddit, ' + str(e)
    pigrow_defs.write_log(script, message, loc_dic['loc_switchlog'])
    return False

connected = False
while connected == False:
    connected = is_connected()
    if connected == False:
        print("no internet, waiting and trying again...")
        time.sleep(10)

logged_in = False
while logged_in == False:
    logged_in = log_in()
    if logged_in == False:
        print("can't log into reddit, waiting and trying again...")
    time.sleep(10)

#
#
#
#       End of initialization phase one....
#
#   we should now have all our location details set and be logged into reddit and have some messages to look at if any exist...
#
#print("Trying to message ---"+str(watcher_name)+"--- which should be you")
#whereto = praw.models.Redditor(reddit, watcher_name, _data=None)
#whereto.message('Pigrow Settings', "Hi,just thought you'd like to know it worked this time:")



def change_setting(setting,value):
    if setting[0:4]=='gpio':
        gpio_setting = setting.split('_')
        if len(gpio_setting)>2:
            if gpio_setting[2] == 'on':
                if value == 'low' or value == 'high':
                    pi_set[setting]=value
                    pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
                    return("GPIO on direction set to " + str(value))
                else:
                    return(" BAD VALUE - not changing the setting to a bad one!")
        else:
            try:
                if int(value) in valid_gpio:
                    #print("Valid GPIO pin selected")
                    pi_set[setting]=value
                    pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
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
            pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
            return("Set to " + str(value))
        except:
            return("Failed because this setting requires a number")

    elif setting in hour_only:
        try:
            value = int(value)
            if value in range(0,24):
                print("This is a valid hour setting, great job!")
                pi_set[setting]=value
                pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
                return("Hour set to " + str(value))
            else:
                return("needs to be between 0 and 24, like a clock, sorry dogstar people timezone update coming soon...")
        except:
            return('This setting only accepts a number')

    else:
        print("No Verification rules for that setting, changing it to whatever was requested...")
        pi_set[setting]=value
        pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
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



    with open(err_log, "a") as ef:
        line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ about to do the socket thing... \n'
        ef.write(line)
        print line



    #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
    #local_ip_address = s.getsockname()[0]
    #page_text += 'Current local network IP ' + str(local_ip_address)



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
        if msg.author == watcher_name:



            with open(err_log, "a") as ef:
                line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ FOUND AN UNREAD MESSAGE FROM TRUSTED USER\n'
                ef.write(line)




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
                print("Didn't understand what they wanted, if they wanted anything.")
        else:
            print("THIS IS NOT A TRUSTED USER - THEY CAN NOT EDIT SETTINGS!")
            print("")
        msg.mark_read()


###
##         Main Loop
#

#print reddit.read_only
thetime = datetime.datetime.now()
pi_set = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'])

print("")
print("        #############################################")
print("      ##       Listens for reddit messages           ##")
print("")
print(" - If you're me then maybe...")
print(" -    python reddit_settings_ear.py to=The3rdWorld loc_locs=/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt ")
print(" - is the command you need, maybe?")

###THIS SENDS INNITIAL MESSAGE WITH THE SETTIGNS ON EVERY BOOT
if not watcher_name == '':
    try:
        write_set(watcher_name)
    except Exception as err:
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ FAILED TO MESSAGE THE COMMANDER... '+str(watcher_name)+' \n'
            ef.write(line)

with open(err_log, "a") as ef:
    line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ GOT RIGHT TO THE about to start loop... \n'
    ef.write(line)


while True:
    try:
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ in loop ABOUT TO RUN CHECK MSG \n'
            ef.write(line)
        check_msg()
        time.sleep(30)
        print("all messages replied to, Looping again...")
    except  Exception as err:
        print("There was an error in the loop, " + str(err) + " trying again")
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ IT RUN BUT THERE WAS AN ERROR,'+str(err)+' RELOOPING...\n'
            ef.write(line)
        time.sleep(1)
        #raise
