#!/usr/bin/python
import matplotlib.pyplot as plt
import datetime
import numpy as np

##User Settings  -- It's ok to change these
##Temperature measured in C 

dangercold = 15 
toocold = 23
toohot = 30
dangerhot = 36
hours_to_show = 24*5 #hours from the end of the log, use absurdly high number to see all
log_location = "/home/pi/Pigrow/logs/sensor_log.txt"

##Change the above numbers as required, 

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,


log_temp = []
log_humid = []
log_date = []
cut_list_date = []

print "----------------------------------"
print "-------Preparing To Graph---------"
print "--------Temp and Humitiy----------"
print "----------------------------------"

def add_log(linktolog):
    with open(linktolog, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Adding ' + str(len(logitem)) + ' readings from log.')
    for item in logitem:
        item = item.split(">")
        if len(item) >= 3:
            try:
                log_temp.append(float(item[0])) 
                log_humid.append(float(item[1]))
                date = item[2]
                date = date.split(".")       
                date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
                log_date.append(date)
            except:
                print('--failed loading item, no drama, ignored.')
    print('We now have ' + str(len(log_temp)) + ' temp and humidity readings to work with.')
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
 #  ax.fill_between(da, ta, 0,where=ta > av, alpha=0.4)
 #  ax.fill_between(da, ta, 0,where=ta < av, alpha=0.4, color='darkblue')
    ax.xaxis_date()
    maxh = ta
    plt.show()

add_log(log_location)
cut_list_last_hours(hours_to_show)
print "----------------------------------"
print "most recent temp - " + str(log_temp[-1])[0:4]
print "most recent humidity - " + str(log_humid[-1])[0:4]
print "----------------------------------"
#make_graph(log_date, log_temp)
make_graph(cut_list_date, log_temp[-len(cut_list_date):])

