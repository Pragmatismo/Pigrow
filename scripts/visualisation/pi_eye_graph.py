#!/usr/bin/python
import datetime
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import sys

print("    -------------------------------")
print("  -----------------------------------")
print("------Pi Spy Py Pi Uptime-Monitor------")
print("  -----------------------------------")

print(" -- still in basic version, danger! danger! ")


print ("time on this computer is now: " + str(datetime.datetime.now()))

#user_name = "your username goes here"
user_name = str(os.getlogin())  #hash this line out if it causes problem, autograbs username replace with username = "magimo" (or whatever)
                                #it will cause problems if for any reason you run this script via cron as root for example
fontloc = "/home/" + user_name +     "/pigitgrow/Pigrow/resources/Caslon.ttf"
graph_path = "/home/" + user_name +  "/pigitgrow/Pigrow/graphs/"
pi_eye_log = "/home/" + user_name +  "/pigitgrow/Pigrow/logs/pieye_log.txt"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'log':
            pi_eye_log = theval
        elif thearg == 'out':
            graph_path = theval
        elif thearg == "font":
            fontloc = theval
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE  - point to a  log file")
        print("  out=DIR/NAME.png  - folder to make graphs in, can use ./ ")
        print("  font=<PATH>       - font to use for text")
        sys.exit()
    elif argu == '-flags':
        print("log=" + pi_eye_log)
        print("out=" + graph_path)
        print("font=<PATH>")
        sys.exit()
    else:
        print(" No idea what you mean by; " + str(argu))

if not os.path.exists(graph_path):
    gq = raw_input("directory doens't exist, create it?")
    if gq == 'Y' or gq == 'y':
        os.makedirs(graph_path)
    else:
        print("Ok, ending program")
        sys.exit()

if not os.path.exists(pi_eye_log):
     print("Log file doesn't seem to exist, sorry...")
     sys.exit()

log_date = []
log_cm_date = []
log_comp_diff = []
log_diff_pitime = []
log_up_date = []
log_up_date_ago = []
uptim_diff_log = []
counter = []
pi_time_epoc = []

with open(pi_eye_log, "r") as f:
    logitem = f.read()
    logitem = logitem.split("\n")

print('Adding ' + str(len(logitem)) + ' lines in log.')
for item in logitem:
    item = item.split(">")
    if len(item) >= 5:
        try:
            pi_date = item[1] #output of date command on pi
            pi_eye_log_date = pi_date.split("=")[1]
            pi_eye_log_date = datetime.datetime.strptime(pi_eye_log_date, '%Y-%m-%d %H:%M:%S')
            log_date.append(pi_eye_log_date)

            cm_date = item[2] #output of this computer's date output
            cm_log_date = cm_date.split("=")[1]
            cm_log_date = datetime.datetime.strptime(cm_log_date, '%Y-%m-%d %H:%M:%S')
            log_cm_date.append(cm_log_date)

            up_date = item[5] #output of uptime on pi
            up_log_date = up_date.split("=")[1]
            up_log_date = datetime.datetime.strptime(up_log_date, '%Y-%m-%d %H:%M:%S')
            log_up_date.append(up_log_date)

        except:
            print("--failed to load line from log")
            #print item

print('We now have ' + str(len(log_date)) + ' date readings from the pi to work with.')
print('We now have ' + str(len(log_up_date)) + ' up time readings from the pi to work with.')
print('   From ' + str(log_date[0]) + ' to ' + str(log_date[-1]))

for x in range(0, len(log_date)):
    #make list of diffs for pi reported dates from log
    diff = log_date[x] - log_date[0]
    diff = diff.total_seconds()
    log_diff_pitime.append(diff)
    #counter for graphing the pi's reported time
    counter.append(x)
    pi_time_epoc.append(int(log_date[x].strftime('%s')))
    #make list of reported uptime in seconds
    up_ago = log_date[x] - log_up_date[x]
    up_ago = int(up_ago.total_seconds())
    log_up_date_ago.append(up_ago)
    #make list of differing times between both computers
    comps_time_diff = log_cm_date[x] - log_date[x] #to account for bst# - datetime.timedelta(hours=1)
    comps_time_diff = int(comps_time_diff.total_seconds())
    log_comp_diff.append(comps_time_diff)
#make list of uptime differences between each log entry
for x in range(1, len(log_up_date_ago)):
    cur_upt = log_up_date_ago[x]
    las_upt = log_up_date_ago[x-1]
    uptim_diff = cur_upt - las_upt
    uptim_diff_log.append(uptim_diff)
print('We now have ' + str(len(uptim_diff_log)) + ' up time differnces from the pi to work with.')

###The Graph Making Routines
# time as reported by pi
def make_pi_time_graph():
    plt.figure(1)
    ax = plt.subplot()
    ax.plot(counter, pi_time_epoc, color='darkblue', lw=3)
    plt.title("Seconds past since 1970 according to pi")
    plt.ylabel("seconds since the epoch")
    plt.xlabel("log entry number")
    plt.savefig (graph_path + "consecutive_pi_time_graph.png")

# time diff of most recent and first entry in log as reported by pi
def make_step_graph():
    plt.figure(2)
    ax = plt.subplot()
    ax.bar(log_date, log_diff_pitime, width=0.001, color='green', linewidth = 0.05)
    plt.title("Time from start of log")
    plt.ylabel("seconds")
    plt.gcf().autofmt_xdate()
    plt.savefig (graph_path + "step_graph.png")

# uptime of pi in seconds
def make_up_graph():
    plt.figure(3)
    ax = plt.subplot()
    ax.bar(log_date, log_up_date_ago, width=0.001, color='green', linewidth = 0)
    #ax.plot(log_date, log_up_date_ago, color='red', lw=1) #optional
    plt.title("Announced Uptime")
    plt.ylabel("seconds")
    plt.gcf().autofmt_xdate()
    plt.savefig(graph_path + "sec_since_up_graph.png")

# time between each logged uptime
def make_upd_graph():
    plt.figure(4)
    ax = plt.subplot()
    ax.plot(log_date[1:], uptim_diff_log, color='darkblue', lw=3)
    plt.title("Time between each logged uptime")
    plt.ylabel("seconds")
    plt.gcf().autofmt_xdate()
    plt.savefig(graph_path + "sec_between_up_graph.png")

# time between both computers time
def make_c_time_graph():
    plt.figure(5)
    ax = plt.subplot()
    ax.plot(log_date, log_comp_diff, color='darkblue', lw=3) #choice of this, below line or both.
    ax.bar(log_date, log_comp_diff, width=0.001, color='green', linewidth = 0.05) #optional
    plt.title("Time difference between both computers")
    plt.ylabel("seconds")
    plt.gcf().autofmt_xdate()
    plt.savefig(graph_path + "sec_between_comps.png")

make_step_graph()
make_up_graph()
make_upd_graph()
make_c_time_graph()
make_pi_time_graph()

#Graphs made and saved so moving on to making the final composite image,

from PIL import Image, ImageDraw, ImageFont

g1 = Image.open(graph_path + "step_graph.png")
g2 = Image.open(graph_path + "sec_since_up_graph.png")
g3 = Image.open(graph_path + "sec_between_up_graph.png")
g4 = Image.open(graph_path + "sec_between_comps.png")
g5 = Image.open(graph_path + "consecutive_pi_time_graph.png")
base = Image.new("RGBA", (2250, 1080), "white")
base.paste(g2,(0,535))
base.paste(g5,(0,-25))
base.paste(g1,(750,520))
base.paste(g4,(1500,-25))
base.paste(g3,(1500,520))

#Header Text
fnt = ImageFont.truetype(fontloc, 75)
d = ImageDraw.Draw(base)
d.text((800,3), "Pigrow2 Health Monitor", font=fnt, fill=(10,90,30,190))
fnt = ImageFont.truetype(fontloc, 40)
d.text((875,65), " - " + str(str(logitem[0]).split(">")[0]), font=fnt, fill=(30,50,40,100))
fnt = ImageFont.truetype(fontloc, 30)
#Data defined text
d.text((800,110), "Pigrow last seen; " + str(log_cm_date[-1]), font=fnt, fill=(10,10,10,190))
seenago = str((datetime.datetime.now() - log_cm_date[-1])).split(".")[0]
d.text((920,150), "which was; " + str(seenago) + " seconds ago ", font=fnt, fill=(10,10,10,190))
d.text((800,200), "Pigrow time at last log; " + str(log_date[-1]), font=fnt, fill=(10,10,10,190))
d.text((920,250), "which is a difference of " + str(log_cm_date[-1] - (log_date[-1]))+ " to this computer", font=fnt, fill=(10,10,10,190))
d.text((800,300), "Log contains; " + str(len(log_date)) + " entries", font=fnt, fill=(10,10,10,190))
d.text((920,350), "over a period of " + str(log_date[-1] - (log_date[0])) + " (hour:min:secs)", font=fnt, fill=(10,10,10,190))
#making the error text red if there are errors
#currently it doesn't record failed attempts so not currently working..
num_failed = 0
if num_failed >= 1:
     colour = (150, 30, 30, 150)
     msg = "uh i didn't count, but not much lol"
     msg_t = "i also forgot to look at the time..."
if num_failed >= 10:
     colour = (255, 30, 30, 255)
     msg = "uh i didn't count but loads lol"
     msg_t = "i also forgot to look at the time..."
else:
     colour = (30, 100, 40, 200)
     msg = "0"
     msg_t = "n/a"

d.text((800,400), "Number of failed attempts; " + str(msg), font=fnt, fill=colour)
d.text((920,450), "Last failed: " + str(msg_t), font=fnt, fill=colour)

#save and/or show
base.save(graph_path + "pigrow_health.png")
base.show()
