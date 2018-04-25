#!/usr/bin/python
import datetime, sys, os
# import numpy as np    #only needed for colouring
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
homedir = os.getenv("HOME")

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'chirp_graph.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
#    loc_dic = pigrow_defs.load_locs(loc_locs)
    # set graph paths
    graph_path = loc_dic['graph_path']
    graph_path = graph_path + "chirp_graph.png"
    moist_graph_path = graph_path + "chirp_mositure_graph.png"
    moist_percent_graph_path = graph_path + "chirp_soil_moisture_percentage_graph.png"
    temp_graph_path = graph_path + "chirp_temp_graph.png"
    light_graph_path = graph_path + "chirp_light_graph.png"
    # set log location
    log_location = loc_dic['chirp_log']
    # find
    loc_settings = loc_dic['loc_settings']
#    set_dic = pigrow_defs.load_settings(loc_settings)
#    toolow = int(set_dic['chirp_low'])
#    toohigh = int(set_dic['chirp_high'])
except Exception as e:
    print(" Couldn't load setting from config file; " + str(e))
    graph_path = homedir + "/Pigrow/graphs/chirp_graph.png"
    moist_graph_path = homedir + "/Pigrow/graphs/chirp_mositure_graph.png"
    moist_percent_graph_path = homedir + "/Pigrow/graphs/chirp_soil_moisture_percentage_graph.png"
    temp_graph_path = homedir + "/Pigrow/graphs/chirp_temp_graph.png"
    light_graph_path = homedir + "/Pigrow/graphs/chirp_light_graph.png"
    log_location = homedir + "/Pigrow/logs/chirp_log.txt"
    toolow = 30
    toohigh = 70

make_light = "true"
make_temp = "true"
make_moist = "true"
make_moist_p = "true"
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
            make_multi = theval.lower()
        elif thearg == 'out':
            graph_path = theval
            if "." in graph_path:
                graph_base_path = theval.split(".")[0]
                file_type = theval.split(".")[1]
            else:
                graph_base_path = graph_path
                file_type = "png"
            moist_graph_path = graph_base_path + "_mositure." + file_type
            moist_percent_graph_path = graph_base_path + "_moisture_percentage." + file_type
            temp_graph_path = homedir + graph_base_path + "_temp." + file_type
            light_graph_path = homedir + graph_base_path + "_light." + file_type
        elif thearg == "hours":
            hours_to_show = int(theval)
        elif thearg == 'cold':
            toocold = int(theval)
        elif thearg == 'hot':
            toohot = int(theval)
        elif thearg == 'make_light':
            make_light = theval.lower()
        elif thearg == 'make_temp':
            make_temp = theval.lower()
        elif thearg == 'make_moist':
            make_moist = theval.lower()
        elif thearg == 'make_moist_p':
            make_moist_p = theval.lower()

    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE  - point to a different log file than mentioned in dirlocs")
        print("                      for multi use a comma to seperate the logs. no spaces")
        print("                         log=log1.txt,log2.txt,/path/to/log/log3.txt")
        print("  out=DIR/NAME.png  - path to graph, can use ./ ")
        print("  make_multi=true   - Combine all into one image")
        print("  hours=NUM         - Hours of the logs graph, 168 for a week")
        print("  cold=NUM          - set's the cold point at which graph colors change")
        print("  hot=NUM           - set's the hot point for graph")
        print("  make_light=true   -  ")
        sys.exit()
    elif argu == '-flags':
        print("log=" + log_location)
        print("out=" + graph_path)
        print("make_multi=[true,false]")
        print("hours=NUM")
        print("cold=NUM")
        print("hot=NUM")
        print("make_light=[true,false]")
        print("make_temp=[true,false]")
        print("make_moist=[true,false]")
        print("make_moist_p=[true,false]")
        sys.exit()
    else:
        print(" No idea what you mean by; " + str(argu))

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,

thetime = datetime.datetime.now()

log_moist = []
log_moist_p = []
log_temp = []
log_light = []
log_date = []

print "----------------------------------"
print "-------Preparing To Graph---------"
print "---Chirp Soil Moisture Sensor-----"
print "----------------------------------"

def add_log(linktolog):
    print("-----------------")
    log_moist = []
    log_moist_p = []
    log_temp = []
    log_light = []
    log_date = []
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

            moist = float(item[1])
            moist_p = float(item[2])
            temp = float(item[3])
            light = float(item[4])
            log_moist.append(moist)
            log_moist_p.append(moist_p)
            log_temp.append(temp)
            log_light.append(light)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_moist.reverse()
    log_moist_p.reverse()
    log_temp.reverse()
    log_light.reverse()
    log_date.reverse()

    print('We have ' + str(len(log_moist)) + ' soil Moisture readings to work with.')
    if len(log_date) >= 1:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
    else:
        print("No data, no graph...")
        exit()
    # text output
    print "      ----------------------------------"
    sec_ago = thetime - log_date[-1]
    print "           most recent Soil moisture - " + str(log_moist[-1])[0:4] + " - " + str(sec_ago) + " seconds ago"
    print "      ----------------------------------"
    return log_moist, log_moist_p, log_temp, log_light, log_date

def make_graph(da,ta, path, colour='darkblue', axislabel='Chirp Sensor', line_label=''):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(da, ta, width=0.01, color='k', linewidth = 0)
    if not line_label == '':
        ax.plot(da, ta, color=colour, lw=2, label=line_label)
    else:
        ax.plot(da, ta, color=colour, lw=2)
    #ta = np.array(ta)
    #ax.fill_between(da, ta, 0,where=ta < dangerlow, alpha=0.6, color='darkblue')
    #ax.fill_between(da, ta, 0,where=ta > dangerlow, alpha=0.6, color='blue')
    #ax.fill_between(da, ta, 0,where=ta > toolow, alpha=0.6, color='green')
    #ax.fill_between(da, ta, 0,where=ta > toohigh, alpha=0.6, color='red')
    #ax.fill_between(da, ta, 0,where=ta > dangerhigh, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title("Time Perod; " + str(da[0].strftime("%b-%d %H:%M")) + " to " + str(da[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel(axislabel)
    plt.legend()
    #
    fig = plt.gcf()
    fig.autofmt_xdate()
    # saving
    if not path == None:
        plt.savefig(path)
        info  = "Graph of last " + str(hours_to_show)
        info += " hours of Chirp data created and saved to "
        info += path
        print(info)
    else:
        print("Made but not saved..")

#
#
#  Doing things bit of the script
#
#

if "," in log_location:
    log_list = log_location.split(",")
    make_multi = "logs"
#
# sticking all the data on the same graphs
#   ugly because of different scales
#   Hacky messy ugly way for now will do proper multigraph option soon
#
if make_multi == "true":
    make_graph(log_date, log_moist, None, 'darkblue', 'Soil Moisture')
    make_graph(log_date, log_light, None, 'yellow', 'Light Numbers')
    make_graph(log_date, log_temp, graph_path, 'red', 'Temp in Centigrade')
#
#  Multi logs in the same graph
# MOISTURE ONLY AT THE MO
#
elif make_multi == "logs":
    counter = -1
    colours = ['darkblue', 'green', 'red', 'yellow', 'black', 'orange']
    for log in log_list[:-1]:
        print("adding log; " + str(log))
        log_moist, log_moist_p, log_temp, log_light, log_date = add_log(log)
        counter = counter + 1
        if counter >= 5:
            counter = 0
        print colours[counter]
        line_label = str(log.split("/")[-1].split(".")[0])
        make_graph(log_date, log_moist_p, None, colours[counter], "mositure", line_label)
    counter = counter + 1
    if counter >= 5:
        counter = 0
    line_label = str(log_list[-1].split("/")[-1].split(".")[0])
    log_moist, log_moist_p, log_temp, log_light, log_date = add_log(log_list[-1])
    make_graph(log_date, log_moist_p, moist_graph_path, colours[counter], "moisture", line_label)
else:
    #
    # single log making a differnt graph for each data
    #
    log_moist, log_moist_p, log_temp, log_light, log_date = add_log(log_location)
    #fig = plt.gcf()
    if make_moist == "true":
        make_graph(log_date, log_moist, moist_graph_path, 'darkblue', 'Soil Moisture')
        fig.clf()
    if make_moist_p == "true":
        make_graph(log_date, log_moist_p, moist_percent_graph_path, 'darkgreen', 'Soil Moisture Percentage')
        fig.clf()
    if make_light == 'true':
        make_graph(log_date, log_light, light_graph_path, 'yellow', 'Light Numbers')
        fig.clf()
    if make_temp == "true":
        make_graph(log_date, log_temp, temp_graph_path, 'red', 'Temp in Centigrade')
