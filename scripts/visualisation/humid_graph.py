#!/usr/bin/python
import matplotlib.pyplot as plt
import datetime
import numpy as np

##User Settings  -- It's ok to change these
##Temperature measured in C 

dangerlow = 30 
toolow = 40
toohigh = 70
dangerhigh = 80
hours_to_show = 48 #hours from the end of the log, use absurdly high number to see all
#log_location = "home/pi/Pigrow/logs/sensor_log.txt"
log_location = "/home/pi/pigrow3/logs/glog.txt"

##Change the above numbers as required, 

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,


log_humid = []
log_date = []
cut_list_date = []
thetime = datetime.datetime.now()
print "----------------------------------"
print "-------Preparing To Graph---------"
print "-------------Humidity-------------"
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
            
            hum = float(item[1])
            log_humid.append(hum)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_humid.reverse()
    log_date.reverse()

    print('We have ' + str(len(log_humid)) + ' humidity readings to work with.')
    print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))


def make_graph(da,ta):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(da, ta, width=0.01, color='k', linewidth = 0)
    ax.plot(da, ta, color='darkblue', lw=3)
    ave = 0
    for x in ta:
        ave = ave + x
    av = ave / len(ta)
    ta = np.array(ta)
    ax.fill_between(da, ta, 0,where=ta < dangerlow, alpha=0.6, color='darkblue')
    ax.fill_between(da, ta, 0,where=ta > dangerlow, alpha=0.6, color='blue')
    ax.fill_between(da, ta, 0,where=ta > toolow, alpha=0.6, color='green')
    ax.fill_between(da, ta, 0,where=ta > toohigh, alpha=0.6, color='red')
    ax.fill_between(da, ta, 0,where=ta > dangerhigh, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title("Time Perod; " + str(da[0].strftime("%b-%d %H:%M")) + " to " + str(da[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("Humidity")
    fig = plt.gcf()
    fig.canvas.set_window_title('Humidity Graph')
    maxh = ta
    fig.autofmt_xdate()
    plt.show()
    #plt.savefig("./saved_humid_fig.jpg")

add_log(log_location)

print "----------------------------------"
secago = thetime - log_date[-1]
print "most recent humidity - " + str(log_humid[-1])[0:4] + " - " + str(secago) + " seconds ago" 
print "----------------------------------"
make_graph(log_date, log_humid)
#make_graph(cut_list_date, log_humid[-len(cut_list_date):])

