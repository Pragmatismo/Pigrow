#!/usr/bin/python
import datetime, sys, os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
homedir = os.getenv("HOME")

graph_path = homedir + "/Pigrow/graphs/ads1115_graph.png"
log_location = homedir + "/Pigrow/logs/ads1115_log.txt"
make_a0 = "yes"
make_a1 = "yes"
make_a2 = "yes"
make_a3 = "yes"
a0_title = "a0"
a1_title = "a1"
a2_title = "a2"
a3_title = "a3"
graph_legend = "default"

hours_to_show = 24*7*52*10 #hours from the end of the log, use absurdly high number to see all

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        thevalue = str(argu).split('=')[1]
        if  thearg == 'log':
            log_location = str(argu).split('=')[1]
        elif thearg == 'out':
            graph_path = thevalue
        elif thearg == "hours":
            hours_to_show = int(str(argu).split('=')[1])
        elif thearg == "a0":
            make_a0 = thevalue
        elif thearg == "a1":
            make_a1 = thevalue
        elif thearg == "a2":
            make_a2 = thevalue
        elif thearg == "a3":
            make_a3 = thevalue
        elif thearg == 'a0_title':
            a0_title = thevalue
        elif thearg == 'a1_title':
            a1_title = thevalue
        elif thearg == 'a2_title':
            a2_title = thevalue
        elif thearg == 'a3_title':
            a3_title = thevalue
        elif thearg == "legend":
            graph_legend = thevalue
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE    - point to a different log file than mentioned in dirlocs")
        print("  out=DIR/NAME.png    - folder to make graphs in, can use ./  ")
        print("  hours=NUM           - Hours back of the log to graph, e.g. 168 to show the last weeks data")
        print("  a0=yes/no           - set no to hide analog data pin a0 data, yes to show")
        print("  a1=yes/no")
        print("  a2=yes/no")
        print("  a3=yes/no")
        print("  a0_title=TEXT       - set the legend text for the a0 data stream")
        print("  a1_title=TEXT       ")
        print("  a2_title=TEXT       ")
        print("  a3_title=TEXT       ")
        print("  legend=default, none - set none to disable graph legend")
        print(" -flags                -show all argu flags and their options")
        sys.exit()
    elif argu == '-flags':
        print("log=" + log_location)
        print("out=" + graph_path)
        print("hours=")
        print("a0=[yes,no]")
        print("a1=[yes,no]")
        print("a2=[yes,no]")
        print("a3=[yes,no]")
        print("a0_title=")
        print("a1_title=")
        print("a2_title=")
        print("a3_title=")
        print("legend=[default,none]")
        sys.exit()
    else:
        print(" No idea what you mean by; " + str(argu))

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,

log_a0 = []
log_a1 = []
log_a2 = []
log_a3 = []
log_date = []
thetime = datetime.datetime.now()

print "----------------------------------"
print "-------Preparing To Graph---------"
print "-------------ADS1115--------------"
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
            date = item[0].split(".")
            date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            if date < oldest_allowed_date:
                break
            a0 = float(item[1])
            a1 = float(item[2])
            a2 = float(item[3])
            a3 = float(item[4])
            log_a0.append(a0)
            log_a1.append(a1)
            log_a2.append(a2)
            log_a3.append(a3)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_a0.reverse()
    log_a1.reverse()
    log_a2.reverse()
    log_a3.reverse()
    log_date.reverse()

    print('We have ' + str(len(log_a0)) + ' readings to work with.')
    if len(log_date) >= 1:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
    else:
        print("No data, no graph... log length less than 1 ")
        exit()

def make_graph(date,ta, colour, name):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(da, ta, width=0.01, color='k', linewidth = 0)
    ax.plot(date, ta, color=colour, lw=1, label=name)
    ave = 0
    for x in ta:
        ave = ave + x
    av = ave / len(ta)
    ta = np.array(ta)
    ax.xaxis_date()
    plt.title("Time Perod; " + str(date[0].strftime("%b-%d %H:%M")) + " to " + str(date[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("ADS1115 Value")
    fig = plt.gcf()
    fig.canvas.set_window_title('Raw ADS1115 Graph')
    maxh = ta
    fig.autofmt_xdate()
    #plt.show()

add_log(log_location)

print "----------------------------------"
secago = thetime - log_date[-1]
print "most recent log entry from " + str(secago) + " seconds ago"
if not make_a0 == 'no':
    make_graph(log_date, log_a0, "darkblue", a0_title)
if not make_a1 == 'no':
    make_graph(log_date, log_a1, "red", a1_title)
if not make_a2 == 'no':
    make_graph(log_date, log_a2, "green", a2_title)
if not make_a3 == 'no':
    make_graph(log_date, log_a3, "black", a3_title)
if not graph_legend == "none":
    plt.legend()
plt.savefig(graph_path)

print("Graph of last " + str(hours_to_show) + " hours of ads1115 data created and saved to " + graph_path)
