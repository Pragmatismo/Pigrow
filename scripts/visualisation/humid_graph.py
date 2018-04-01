#!/usr/bin/python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import datetime, sys, os
import numpy as np
homedir = os.getenv("HOME")

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'humid_graph.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    graph_path = loc_dic['graph_path']
    graph_path = graph_path + "dht_humid_graph.png"
    log_location = loc_dic['loc_dht_log']
    loc_settings = loc_dic['loc_settings']
    set_dic = pigrow_defs.load_settings(loc_settings)
    toolow = int(set_dic['humid_low'])
    toohigh = int(set_dic['humid_high'])
except:
    graph_path = "./dht_humid_graph.png"
    log_location = "./dht22_log.txt"
    toolow = 30
    toohigh = 70

dangerlow = float(toolow) / 100 * 85
dangerhigh = float(toohigh) / 100 * 115

hours_to_show = 24*7*52 #hours from the end of the log, use absurdly high number to see all

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'log':
            log_location = theval
        elif thearg == 'out':
            graph_path = theval
        elif thearg == "hours":
            hours_to_show = int(theval)
        elif thearg == 'too_low':
            toolow = int(theval)
            dangerlow = float(toolow) / 100 * 85
            print toolow, dangerlow
        elif thearg == 'too_high':
            toohigh = int(theval)
            dangerhigh = float(toohigh) / 100 * 115
            print toohigh, dangerhigh
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE  - point to a different log file than mentioned in dirlocs")
        print("  out=DIR/NAME.png  - folder to make graphs in, can use ./ ")
        print("  hours=NUM         - Hours of the logs graph, 168 for a week")
        print("  too_low=NUM          - set's the cold point at which graph colors change")
        print("  too_high=NUM           - set's the hot point for graph")
        sys.exit()
    elif argu == '-flags':
        print("log=" + log_location)
        print("out=" + graph_path)
        print("hours=NUM")
        print("too_low=NUM")
        print("too_high=NUM")
        sys.exit()
    else:
        print(" No idea what you mean by; " + str(argu))

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
    if len(log_date) >= 1:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
    else:
        print("No data, no graph...")
        exit()

def make_graph(da,ta):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(da, ta, width=0.01, color='k', linewidth = 0)
    ax.plot(da, ta, color='black', lw=2)
    #ave = 0
    #for x in ta:
    #     ave = ave + x
    #av = ave / len(ta)
    ta = np.array(ta)
    ax.fill_between(da, ta, 0,where=ta < dangerlow, alpha=0.6, color='darkblue')
    ax.fill_between(da, ta, 0,where=ta < toolow, alpha=0.6, color='blue')
    ax.fill_between(da, ta, 0,where=ta > toohigh, alpha=0.6, color='red')
    ax.fill_between(da, ta, 0,where=ta > dangerhigh, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title("Time Perod; " + str(da[0].strftime("%b-%d %H:%M")) + " to " + str(da[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("Humidity")
    fig = plt.gcf()
    fig.canvas.set_window_title('Humidity Graph')
    maxh = ta
    fig.autofmt_xdate()
    #plt.show()
    plt.savefig(graph_path)

add_log(log_location)

print "----------------------------------"
secago = thetime - log_date[-1]
print "most recent humidity - " + str(log_humid[-1])[0:4] + " - " + str(secago) + " seconds ago"
print "----------------------------------"
make_graph(log_date, log_humid)

print("Graph of last " + str(hours_to_show) + " hours of humidity data created and saved to " + graph_path)

#make_graph(cut_list_date, log_humid[-len(cut_list_date):])
