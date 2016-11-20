#!/usr/bin/python
import matplotlib.pyplot as plt
import datetime
import numpy as np
import sys
##User Settings  -- It's ok to change these
##Temperature measured in C

dangercold = 15
toocold = 23
toohot = 30
dangerhot = 36
##Change the above numbers as required,

hours_to_show = 24*5 #hours from the end of the log, use absurdly high number to see all
log_location = "/home/pi/Pigrow/logs/fht22_.txt"
graph_path = "../../graphs/saved_humid_fig.jpg"       #default use o= to set via command line


for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    if  thearg == 'log':
        log_location = str(argu).split('=')[1]
    elif thearg == 'o':
        graph_path = str(argu).split('=')[1]
    elif thearg == "h":
        hours_to_show = int(str(argu).split('=')[1])

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,

log_temp = []
log_date = []
cut_list_date = []
thetime = datetime.datetime.now()

print "----------------------------------"
print "-------Preparing To Graph---------"
print "--------------Temp----------------"
print "----------------------------------"

def add_log(linktolog):
    with open(linktolog, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Adding ' + str(len(logitem)) + ' readings from log.')
    oldest_allowed_date = thetime - datetime.timedelta(hours=hours_to_show)
    curr_line = len(logitem) - 1

    while curr_line >= 0:
        try:
            item = logitem[curr_line]
            item = item.split(">")
            date = item[2].split(".")
            date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            if date < oldest_allowed_date:
                break

            temp = float(item[0])
            log_temp.append(temp)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_temp.reverse()
    log_date.reverse()

    print('We now have ' + str(len(log_temp)) + ' temp readings to work with.')
    print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))

def cut_list_last_hours(hours_to_show):
    print("Shortening list to show only last " + str(hours_to_show) + " hours")
    final_time = log_date[-1]
    hours_shown = datetime.timedelta(hours=hours_to_show)
    start_time = final_time-hours_shown
    for x in log_date:
        if x >= start_time:
            cut_list_date.append(x)
        else:
            pass
    print("-now working with " + str(len(cut_list_date)) + " log entries starting from " + str(cut_list_date[0].strftime("%b-%d %H:%M")))


def make_graph(da,ta):
    plt.figure(1)
    ax = plt.subplot()
 #   ax.bar(da, ta, width=0.01, color='green', linewidth = 0)
    ax.plot(da, ta, color='darkblue', lw=3)
    ave = 0
    for x in ta:
        ave = ave + x
    av = ave / len(ta)
    ta = np.array(ta)
    ax.fill_between(da, ta, 0,where=ta < dangercold, alpha=0.6, color='darkblue')
    ax.fill_between(da, ta, 0,where=ta > dangercold, alpha=0.6, color='blue')
    ax.fill_between(da, ta, 0,where=ta > toocold, alpha=0.6, color='green')
    ax.fill_between(da, ta, 0,where=ta > toohot, alpha=0.6, color='red')
    ax.fill_between(da, ta, 0,where=ta > dangerhot, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title("Time Perod; " + str(da[0].strftime("%b-%d %H:%M")) + " to " + str(da[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("Temp")
    fig = plt.gcf()
    fig.canvas.set_window_title('Temperature Graph')
    maxh = ta
    fig.autofmt_xdate()
    #plt.show()
    plt.savefig(graph_path)

add_log(log_location)
cut_list_last_hours(hours_to_show)
print "----------------------------------"
print "most recent temp - " + str(log_temp[-1])[0:4]
print "----------------------------------"
#make_graph(log_date, log_temp)
make_graph(cut_list_date, log_temp[-len(cut_list_date):])

print("Graph of last " + str(hours_to_show) + " hours of temp data created and saved to " + graph_path)
