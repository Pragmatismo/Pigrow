#!/usr/bin/python
import datetime, sys, os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
homedir = os.getenv("HOME")

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'chirp_graph.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    graph_path = loc_dic['graph_path']
    graph_path = graph_path + "chirp_graph.png"
    log_location = loc_dic['chirp_log']
    loc_settings = loc_dic['loc_settings']
    set_dic = pigrow_defs.load_settings(loc_settings)
    toolow = int(set_dic['chirp_low'])
    toohigh = int(set_dic['chirp_high'])
except:
    graph_path = homedir + "/Pigrow/graphs/chirp_graph.png"
    humid_graph_path = homedir + "/Pigrow/graphs/chirp_hum_graph.png"
    temp_graph_path = homedir + "/Pigrow/graphs/chirp_temp_graph.png"
    light_graph_path = homedir + "/Pigrow/graphs/chirp_light_graph.png"
    log_location = homedir + "/Pigrow/logs/chirp_log.txt"
    toolow = 30
    toohigh = 70

dangerlow = int(toolow) / 100 * 85
dangerhigh = int(toohigh) / 100 * 115
make_multi = False
hours_to_show = 24*7*52 #hours from the end of the log, use absurdly high number to see all

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'log':
            log_location = theval
        elif thearg == 'make_multi' or thearg == 'multi':
            make_multi = bool(theval)
        elif thearg == 'out':
            graph_path = theval
        elif thearg == "hours":
            hours_to_show = int(theval)
        elif thearg == 'cold':
            toocold = int(theval)
        elif thearg == 'hot':
            toohot = int(theval)
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE  - point to a different log file than mentioned in dirlocs")
        print("  out=DIR/NAME.png  - folder to make graphs in, can use ./ ")
        print("  make_multi=True   - Combine all into one image")
        print("  hours=NUM         - Hours of the logs graph, 168 for a week")
        print("  cold=NUM          - set's the cold point at which graph colors change")
        print("  hot=NUM           - set's the hot point for graph")
        sys.exit()
    elif argu == '-flags':
        print("log=" + log_location)
        print("out=" + graph_path)
        print("make_multi=[True,False]")
        print("hours=NUM")
        print("cold=NUM")
        print("hot=NUM")
        sys.exit()  
    else:
        print(" No idea what you mean by; " + str(argu))

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,

log_humid = []
log_temp = []
log_light = []
log_date = []
cut_list_date = []
thetime = datetime.datetime.now()

print "----------------------------------"
print "-------Preparing To Graph---------"
print "---Chirp Soil Moisture Sensor-----"
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

            hum = float(item[1])
            temp = float(item[2])
            light = float(item[3])
            log_humid.append(hum)
            log_temp.append(temp)
            log_light.append(light)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_humid.reverse()
    log_temp.reverse()
    log_light.reverse()
    log_date.reverse()

    print('We have ' + str(len(log_humid)) + ' soil humidity readings to work with.')
    if len(log_date) >= 1:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
    else:
        print("No data, no graph...")
        exit()

def make_graph(da,ta, path, colour='darkblue', axislabel='Chirp Sensor'):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(da, ta, width=0.01, color='k', linewidth = 0)
    ax.plot(da, ta, color=colour, lw=3)
    ave = 0
    for x in ta:
        ave = ave + x
    av = ave / len(ta)
    ta = np.array(ta)
    #ax.fill_between(da, ta, 0,where=ta < dangerlow, alpha=0.6, color='darkblue')
    #ax.fill_between(da, ta, 0,where=ta > dangerlow, alpha=0.6, color='blue')
    #ax.fill_between(da, ta, 0,where=ta > toolow, alpha=0.6, color='green')
    #ax.fill_between(da, ta, 0,where=ta > toohigh, alpha=0.6, color='red')
    #ax.fill_between(da, ta, 0,where=ta > dangerhigh, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title("Time Perod; " + str(da[0].strftime("%b-%d %H:%M")) + " to " + str(da[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel(axislabel)
    fig = plt.gcf()
    fig.canvas.set_window_title('Chirp Soil Humidity Temp and Light Level Sensor')
    maxh = ta
    fig.autofmt_xdate()
    #plt.show()
    if not path == None:
        plt.savefig(path)
        info  = "Graph of last " + str(hours_to_show)
        info += " hours of soil humidity data created and saved to "
        info += path
        print(info)
    else:
        print("Made but not saved..")

add_log(log_location)

print "----------------------------------"
secago = thetime - log_date[-1]
print "most recent Soil humidity - " + str(log_humid[-1])[0:4] + " - " + str(secago) + " seconds ago"
print "----------------------------------"

#Hacky messy ugly way for now will do proper multigraph option soon

if make_multi == True:
    make_graph(log_date, log_humid, None, 'darkblue', 'Soil Humidity')
    make_graph(log_date, log_light, None, 'yellow', 'Light Numbers')
    make_graph(log_date, log_temp, graph_path, 'red', 'Temp in Centigrade')
else:
    make_graph(log_date, log_humid, humid_graph_path, 'darkblue', 'Soil Humidity')
    fig = plt.gcf()
    fig.clf()
    make_graph(log_date, log_light, light_graph_path, 'yellow', 'Light Numbers')
    fig.clf()
    make_graph(log_date, log_temp, temp_graph_path, 'red', 'Temp in Centigrade')
