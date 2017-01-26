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
from crontab import CronTab   #  pip install python-crontab
cron = CronTab(user=True)  #can be user+True, 'yourusername' or 'root' all work.

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
        print("\n\n -- using LOCS LOGS = " + str(loc_locs) + "'\n\n")

loc_dic = pigrow_defs.load_locs(loc_locs)
#Settings for validation rules
hour_only = ['time_lamp_off', 'time_lamp_on'] #name os script that only accepts hour:min
valid_gpio=[2,3,4,17,27,22,10,9,11,0,5,6,13,19,26,14,15,18,23,24,25,8,7,1,12,16,20,21]  #valid gpio numbers using the gpio (BCM) NOT the board numbering system
intonly= ['heater_templow','heater_temphigh','log_frequency']




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
                    return(str(setting) + " GPIO on direction set to " + str(value), "pass")
                else:
                    return(" BAD VALUE - not changing the setting to a bad one!", "fail")
        else:
            try:
                if int(value) in valid_gpio:
                    #print("Valid GPIO pin selected")
                    pi_set[setting]=value
                    pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
                    return(setting + " GPIO Pin set to " + str(value), "pass")
                else:
                    return("Invalid GPIO pin, not changing anything.", "fail")
            except:
                return("Invalid GPIO pin, has to be a number. No change","fail")
    elif setting in intonly:
        try:
            value = int(value)
            #print("This is a number, great job!")
            pi_set[setting]=value
            pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
            return(str(setting) + " set to " + str(value), "pass")
        except:
            return("Failed because this setting requires a number", "fail")

    elif setting in hour_only:
        try:
            value = value.split(":")
            value_h = int(value[0])
            value_m = int(value[1])
            if value_h in range(0,24) and value_m in range(0,59):
                print("This is a valid time setting, great job!")
                value = str(value_h) + ":" + str(value_m)
                pi_set[setting]=value
                pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
                return("time set to " + str(value), "fail")
            else:
                return("should be in 24hour clock HH:MM format, 14:03 for example", "fail")
        except:
            return('should be in 24hour clock HH:MM format, 15:45 for example', "fail")

    else:
        print("No Verification rules for that setting, changing it to whatever was requested...")
        pi_set[setting]=value
        pigrow_defs.save_settings(pi_set, loc_dic['loc_settings'], err_log=loc_dic['err_log'])
        return(str(setting) + " set to " + str(value),"pass")

def write_set(whereto='wiki'):
    page_text = '#Pigrow Settings  \n\n'
    page_text += 'This displays the current settings from the pigrow,  \n'
    page_text += 'to change these settings you can message your pigrow'
    page_text += 'via reddit by simply clicking on the link in the table  \n'
    page_text += 'leave the subject as the setting you wish to change and'
    page_text += 'put the new value in the body of the message.  \n'
    page_text += '  \n'
    page_text += '|Name|Setting|  \n'
    page_text += '|--:|---|  \n'
    for key, value in pi_set.iteritems() :
        #print key, value
        page_text += '|['+key+'](https://www.reddit.com/message/compose/?to='+my_username+'&subject=set:' +str(key)+ '&message='+str(value)+')|' + str(value)  + '  \n'
    page_text +=("")
    page_text +=("To view an explanation of each setting go see [configuring the pigrow](wiki link goes here) in the documentation ")
    ###
    ##    LOAD SWITCH FILE
    #
    switch_list = []
    days_to_show = 7
    switch_list_limit = 10
    try:
        with open(loc_switchlog, "r") as f:
            logitem = f.read()
            logitem = logitem.split("\n")
        print('There are ' + str(len(logitem)) + ' readings in the switch log.')
        oldest_allowed_date = thetime - datetime.timedelta(days=days_to_show)
        curr_line = len(logitem) - 1
    except:
        print("switch not loaded, try running pi_setup")
        pigrow_defs.write_log(script, 'switch log file error', loc_dic['err_log'])
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
            if len(switch_list) >= switch_list_limit:
                break
            curr_line = curr_line - 1

        except:
            print("line"+str(curr_line)+" didn't parse, ignoring")
            curr_line = curr_line - 1
        #print item
        switch_item = item
    page_text += '  \n  \n'
    page_text += '#Cron'
    page_text += '  \n  \n'
    page_text += 'Current Cron file;  \n  \n'
    page_text += 'Enabled|time|Command|Comment|-|Line  \n'
    page_text += ':-:|---|---|---|--:|---  \n'
    cjob=0
    for job in cron:
        modlink = 'https://www.reddit.com/message/compose/?to='+my_username+'&subject=cronmod:' + str(cjob) + '&message=updated_line_here'
        enabledlink = 'https://www.reddit.com/message/compose/?to='+my_username+'&subject=crontog:' + str(cjob) + '&message=plz'
        enabled = job.is_enabled()
        page_text += "["+str(enabled)+"]("+enabledlink+")|" + str(job.slices) + "|"
        page_text += str(job.command) + "|" + str(job.comment) + "|"
        page_text += "[modify]("+modlink+")|" + str(job) + "  \n"
        cjob=cjob+1
    page_text += "  \n  \n"
    page_text += '[Add New Cron Job;](https://www.reddit.com/message/compose/?to='+my_username+'&subject=cmd:addcron&message=plz)'


    page_text += '  \n  \n'
    page_text += '#Switch Log  \n  \n'
    page_text += 'Showing the last ' + str(days_to_show) + ' days of activity.  \n  \n'
    page_text += '|Script|Time|Event  \n'
    page_text += '|---|:-:|---  \n'
    for a in switch_list:
        page_text += '|'+a[0]+'|'+ str(a[1]) +'|'+a[2]+'  \n'
    page_text += '  \n'
    ###
    cmdlink = "(https://www.reddit.com/message/compose/?to="+my_username+"&subject=cmd:"
    page_text += '  \n'
    page_text += '  \n'
    page_text += '  The following settings are not yet all implimented'
    page_text += '  They will run functions found in pigrow_defs'
    page_text += '  \n  \n'
    page_text += '|Pi Command|Action|Notes  \n'
    page_text += '|:-:|:-:|---  \n'
    page_text += '|Power Off|Remotely shuts down the pi|passwrod protected, if enabled include password in body of text  \n'
    page_text += '|Reboot|Remotely reboots the pi|password protected  \n'
    page_text += '|Factory Reset|Restores Pigrow Defaults|password protected  \n'
    page_text += '|Update Pigrow|Automatically updates software|password protected  \n'
    page_text += "|[Log]"+cmdlink+"log)|Create a custom log event|Include the text of the log event in the body of the message  \n"
    page_text += "|[update_wiki]"+cmdlink+"update_wiki)|Updates or creates the settings wiki|Replies with a link to it.  \n"
    page_text += "|[Archive Grow]"+cmdlink+"archive_grow)|Stores all the data for the current grow in an archive folder and starts a new grow|password protected  \n"
    page_text += "|Generate System Report|Creates a current pigrow system report and sends it to the user|Includes diskfull, uptime, etc  \n"
    page_text += "|[Generate Data Wall]"+cmdlink+"datawall)|Create visual display of pigrow status from logs|  \n"
    page_text += "|[Generate Timelapse Hour]"+cmdlink+"timelapse_hour)|Creates a timelapse gif of the current day so far, uploads it and sends a link to the user|  \n"
    page_text += "|[Generate Timelapse 5Hours]"+cmdlink+"timelapse_5hour)|Creates video of last five hours, uploads and links user|size limited due to upload restrictions  \n"
    page_text += "|[Generate Timelapse day]"+cmdlink+"timelapse_day)|Creates video of last day, applies timeskip to limit size.  \n"
    page_text += "|[Generate Timelapse week]"+cmdlink+"timelapse_week)|Creates video of last week, applies large timeskip to limit size.  \n"
    page_text += "|[send_settings]"+cmdlink+"send_settings)|Replies to the user with the settings menu|  \n"
    page_text += "  \n  \n"
    page_text += "*this section work in progress, links will be added as the functions are*   \n"
    page_text += "  \n  \n"

    #determine local ip - apparently this works on macs if you change the 0 to a 1 but i don't buy apple products so...
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 0))  # connecting to a UDP address doesn't send packets
        local_ip_address = s.getsockname()[0]
        page_text += 'Current local network IP ' + str(local_ip_address)
    except:
        page_text += 'Local IP not deduced, sorry...'

    print("writing " + str(len(page_text)) + " characters to reddit")
    if whereto == 'wiki':
        praw.models.WikiPage(reddit, subreddit, wiki_title).edit(page_text[0:524288])
    else:
        try:
            whereto = praw.models.Redditor(reddit, name=whereto, _data=None)
            whereto.message('Pigrow Settings', page_text[0:10000])   #, from_subreddit=subreddit)
        except:
            pigrow_defs.write_log(script, "couldn't contact redditor, wrong naem?", loc_dic['err_log'])


def make_cron_from(income):
    cron_request = CronTab(tab=income)
    if len(cron_request) == 1:
        print("requested cron is valid")
        cron_request = cron_request[0]
        cronslice = cron_request.slices
        croncommand = cron_request.command
        croncomment = cron_request.comment
        cronenabled = cron_request.enabled
        new_job = cron.new(command=croncommand,  comment=croncomment)
        if cronslice == "@reboot":
            #print("Reboot script")
            new_job.every_reboot()
        else:
            #print("not a reboot script...")
            new_job.setall(cronslice)
        new_job.enabled = cronenabled
        return new_job
    elif len(cron_request) == 0:
        print("Job not valid")
        return False
    else:
        print("Something odd happened, a problem..")
        return False

def check_msg():
    path = '/home/pi/Pigrow/'
    wikilink = "[Settings Wiki](https://www.reddit.com/r/" + str(subreddit) + "/wiki/"+str(wiki_title)+ ")"
    for msg in reddit.inbox.unread():
        print("")
        print ('  - ' +msg.author)
        print ('  - ' +msg.subject)
        print ('  - ' +msg.body)
        if msg.author == watcher_name:
            print("Trusted User settings access enabled.")
            try:
                msgsub = msg.subject.split(":")
            except:
                print("Not a valid format")
            msgfrom = praw.models.Redditor(reddit, name=msg.author, _data=None)

            if msgsub[0] == "set":
                if msgsub[1] in pi_set:
                    reply, passed = change_setting(str(msgsub[1]),str(msg.body))
                    write_set('wiki')
                    reply += "  \n  \nvisit " + wikilink + " for more info"
                    msgfrom.message('Pigrow Settings', reply[0:10000])
                    if passed == "pass":
                        pigrow_defs.write_log(script, reply, loc_dic['loc_switchlog'])
            elif msgsub[0] == "cmd":
                if msgsub[1] == "reboot":
                    print("User requests reboot!")
                elif msgsub[1] == "power off":
                    print("User Requests Power Off!")
                elif msgsub[1] == "restore defaults":
                    print("User want to resotore defauls")
                elif msgsub[1] == "update pigrow":
                    print("User want to update pigrow!")
                elif msgsub[1] == "archive_grow":
                    print("--Archiving grow")
                    responce = pigrow_defs.archive_grow(loc_dic, str(msg.body))
                    pigrow_defs.write_log(script, "Prior grow data archived.", loc_dic['loc_switchlog'])
                    msgfrom.message('Pigrow Settings', responce)
                elif msgsub[1] == "log":
                    print("--User has something they want to add to the log...")
                    pigrow_defs.write_log("User via Reddit", str(msg.body), loc_dic['loc_switchlog'])
                elif msgsub[1] == "send_settings":
                    print("--User want to see settings!")
                    write_set(msg.author)
                elif msgsub[1] == "update_wiki":
                    print("--User want to see settings!")
                    write_set('wiki')
                    msgfrom.message('Pigrow Control', "Settings Wiki written at " + wikilink)
                elif msgsub[1] == 'datawall':
                    print("--User want's a datawall!")
                    datawalllink = "[Settings Wiki](https://www.reddit.com/r/" + str(subreddit) + "/wiki/"+str(wiki_title)+ "datawall)"
                    os.system(path+"scripts/visualisation/caps_graph.py")
                    os.system(path+"scripts/visualisation/temp_graph.py hours=24")
                    os.system(path+"scripts/visualisation/humid_graph.py hours=24")
                    os.system(path+"scripts/visualisation/selflog_graph.py")
                    os.system(path+"scripts/visualisation/assemble_datawall.py")
                    photo_loc = subreddit.stylesheet.upload('datawall', path+"graphs/datawall.jpg")
                    page_text = "#Datawall  \n  \n"
                    page_text += '![datawall](%%datawall%%)  \n  \n'
                    praw.models.WikiPage(reddit, subreddit, live_wiki_title).edit(page_text)
                    live_wikilink = "[Settings Wiki](https://www.reddit.com/r/" + str(subreddit) + "/wiki/"+str(live_wiki_title)+ ")"
                    msgfrom.message('Pigrow Control', "Datawall uploaded to " + str(live_wikilink))

                elif msgsub[1] == "timelapse_hour":
                    print("Generating the last hour into a timelapse, this will take a while...")
                    os.system(path+"scripts/visualisation/timelapse_assemble.py of=/home/pi/Pigrow/graphs/hour.gif dc=hour1 ds=1 fps=5 ow=r")
                    msgfrom.message('Pigrow Control', "Gif created ")#at " + giflink)
                elif msgsub[1] == "timelapse_5hours":
                    print("Generating the last five hours into a timelapse, this will take a while...")
                    os.system(path+"scripts/visualisation/timelapse_assemble.py of=/home/pi/Pigrow/graphs/5hours.gif dc=hour5 ds=1 fps=5 ow=r")
                    msgfrom.message('Pigrow Control', "Gif created ")#at " + giflink)
                elif msgsub[1] == "timelapse_day":
                    print("Generating the last day into a timelapse, this will take a while...")
                    os.system(path+"scripts/visualisation/timelapse_assemble.py of=/home/pi/Pigrow/graphs/day.gif dc=day1 ds=1 fps=5 ts=8 ow=r")
                    msgfrom.message('Pigrow Control', "Gif created ")#at " + giflink)
                elif msgsub[1] == "timelapse_week":
                    print("Generating the last week into a timelapse, this will take a while...")
                    os.system(path+"scripts/visualisation/timelapse_assemble.py of=/home/pi/Pigrow/graphs/week.gif dc=hour5 ds=1 fps=5 ow=r")
                    msgfrom.message('Pigrow Control', "Gif created ")#at " + giflink)
                elif msgsub[1] == "addcron":
                    print("User wants to add job to cron;")
                    new_job = make_cron_from(msg.body)
                    print new_job
                    if new_job != False:
                        cron.write()
                        msgfrom.message('Pigrow Control', "Cron job " + str(new_job) + " added.")
                    else:
                        msgfrom.message('Pigrow Control', "Sorry, that wasn't a valid cron job")
            elif msgsub[0] == "crontog":
                job = cron[int(msgsub[1])]
                if job.enabled == True:
                    job.enable(False)
                    truefalse = "False"
                else:
                    job.enable(True)
                    truefalse = "True"
                cron.write()
                msgfrom.message('Pigrow Control', "toggled to " + truefalse)
            elif msgsub[0] == "cronmod":
                job = cron[int(msgsub[1])]
                print("Attempting to alter cron job" + str(job))
                new_job = make_cron_from(msg.body)
                print new_job
                if new_job != False:
                    #if job.command == new_job.command:
                    cron.remove(job)
                    cron.write()
                    msgfrom.message('Pigrow Control', "Cron job " + str(job) + " changed to " + str(new_job))
                    #else:
                    #    cron.remove(new_job)
                    #    msgfrom.message('Pigrow Control', "Sorry, can't change scripts when modifying cron job, it's dangerous")
                else:
                    msgfrom.message('Pigrow Control', "Sorry, that wasn't a valid cron job")

            else:
                reply =  "Sorry, couldn't understand what you wanted, "
                reply += "visit " + wikilink + " for more info"
                whereto = praw.models.Redditor(reddit, name=msg.author, _data=None)
                whereto.message('Pigrow Settings', reply[0:10000])
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

while True:
    try:
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
