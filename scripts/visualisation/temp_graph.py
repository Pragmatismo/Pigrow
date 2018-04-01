#!/usr/bin/python
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import datetime
import numpy as np
import sys, os
homedir = os.getenv("HOME")

#This code is designed to work with a pigrow using a dht22 sensor, but use it for whatever you like,,,


#  Default Settings  -- It's ok to change these
temp_unit = "c"
show_from = "start"
hours_to_show = "all" #hours from the end of the log, use "all" to choose all


def find_paths_from_dirlocs():
    try:
        sys.path.append(homedir + '/Pigrow/scripts/')
        import pigrow_defs
        script = 'temp_graph.py'
        loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
        loc_dic = pigrow_defs.load_locs(loc_locs)
        graph_path = loc_dic['graph_path']
        graph_path = graph_path + "dht_temp_graph.png"
        log_location = loc_dic['loc_dht_log']
        loc_settings = loc_dic['loc_settings']
    except:
        graph_path = "./dht_temp_graph.png"
        log_location = "./dht22_log.txt"
        loc_settings = ""
    return graph_path, log_location, loc_settings

def get_warning_ranges_from_settings(loc_settings):
    try:
        set_dic = pigrow_defs.load_settings(loc_settings)
        toocold = int(set_dic['heater_templow'])
        toohot = int(set_dic['heater_temphigh'])
    except:
        toocold = 17
        toohot = 30
    dangercold = (float(toocold) / 100) * 85
    dangerhot = (float(toohot) / 100) * 115
    return toocold, dangercold, toohot, dangerhot

def check_commandline_options(graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit, ymin="default",ymax="default", log_temp_pos=0, log_date_pos=2, colour_graph="true"):
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0].lower()
            theval = str(argu).split('=')[1]
            if  thearg == 'log':
                log_location = theval
            elif thearg == 'out':
                graph_path = theval
            elif thearg == "hours":
                hours_to_show = int(theval)
            elif thearg == "show_from":
                show_from = theval
            elif thearg == 'cold':
                toocold = int(theval)
                dangercold = float(toocold) / 100 * 85
            elif thearg == 'hot':
                toohot = int(theval)
                dangerhot = float(toohot) / 100 * 115
            elif thearg == "unit" or thearg == "temp_unit":
                temp_unit = theval.lower()
            elif thearg == "ymin":
                ymin = int(theval)
            elif thearg == "ymax":
                ymax = int(theval)
            elif thearg == "log_temp_pos":
                log_temp_pos = int(theval)
                print("Using log location " + str(log_temp_pos) + " for temp info")
            elif thearg == "log_date_pos":
                log_date_pos = int(theval)
                print("Using log location " + str(log_date_pos) + " for date info")
            elif thearg == "colour_graph" or thearg == "color_graph":
                colour_graph = thearg.lower()
        elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
            print("")
            print("  log=DIR/LOG_FILE  - point to a different log file than mentioned in dirlocs")
            print("  log_temp_pos=num  - position of temp data in log file")
            print("  log_date_pos=num  - position of date data in log file")
            print("  out=DIR/NAME.png  - folder to make graphs in, can use ./ ")
            print("  hours=NUM         - Hours of the logs graph, 168 for a week")
            print("  show_from=DATE    - The start date you want to graph from ")
            print("                      must use format YYYY-mm-dd-HH:MM")
            print("                                e.g.  2018-12-25-16:20")
            print("  cold=NUM          - set's the cold point at which graph colors change")
            print("  hot=NUM           - set's the hot point for graph")
            print("  color_graph=false - turn off high/low graph coloring")
            print("  temp_unit=c or f  - when f converts to Fahrenheit before graphing ")
            print("  ymin=0            - Set position of bottom of Y Axis")
            print("  ymax=50           - Set position of top of Y Axis")
            print("                         these are useful when animating")
            print("                         or making graphs for comparing")
            sys.exit()
        elif argu == '-flags':
            print("log=" + log_location)
            print("log_temp_pos=0")
            print("log_date_pos=2")
            print("out=" + graph_path)
            print("hours=NUM")
            print("show_from=2018-12-25-16:20")
            print("cold=NUM")
            print("hot=NUM")
            print("temp_unit=[c,f]")
            print("ymin=0")
            print("ymax=50")
            print("colour_graph=[true,false]")
            sys.exit()
        else:
            print(" No idea what you mean by; " + str(argu))
    return graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit, ymin, ymax, log_temp_pos, log_date_pos, colour_graph

def set_date_values(hours_to_show, show_from):
    # if hours_to_show is set then works out when to start the Graph
    # show_from is set then converts it into a datetime object for later use
    # show_from should be set using the format YY-mm-dd-HH:MM note the - instead of a space between dd and HH
    if not hours_to_show == "all":
        oldest_allowed_date = thetime - datetime.timedelta(hours=hours_to_show)
    elif not show_from == "start":
        try:
            oldest_allowed_date = datetime.datetime.strptime(show_from, '%Y-%m-%d-%H:%M')
        except:
            print("!! you datetiemed wrong, format is YY-mm-dd-HH:MM")
            print("|||" + show_from + "|||")
            print("!! showing all instead")
            raise
            oldest_allowed_date = "all"
    else:
        oldest_allowed_date = "all"
    return oldest_allowed_date

def add_log(linktolog, temp_unit, oldest_allowed_date, temp_pos=0, date_pos=2):
    log_date = []
    log_temp = []
    with open(linktolog, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Log contains ' + str(len(logitem)) + ' lines.')
    curr_line = len(logitem) - 1
    while curr_line >= 0:
        try:
            item = logitem[curr_line]
            item = item.split(">")
            date = item[date_pos].split(".")
            date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            if not oldest_allowed_date == "all":
                if date < oldest_allowed_date:
                    print("Stopping reading log at " + str(oldest_allowed_date))
                    break
            temp = item[temp_pos]
            if ":" in temp:
                temp = temp.split(":")[0]
            temp = float(temp)
            if temp_unit == 'f':
                temp = (1.8*temp) + 32
            log_temp.append(temp)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            if not logitem[curr_line] == "":
                print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1
    # pit the lists back into the right order because we started at the end and worked backwards
    log_temp.reverse()
    log_date.reverse()
    print(' We now have ' + str(len(log_temp)) + ' temp readings to work with.')
    if len(log_date) >= 1:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
    else:
        print("Couldn't find any valid data, sorry no data, no graph...")
        exit()
    return log_date, log_temp

def make_graph(date_list,temp_list, graph_path, ymin="default", ymax="default", toocold=None, dangercold=None, toohot=None, dangerhot=None):
    # define graph space
    plt.figure(1)
    ax = plt.subplot()
    # make the graph
    #ax.bar(date_list, temp_list, width=0.01, color='green', linewidth = 1) #this is horribly processor intensive don't use it
    ax.plot(date_list, temp_list, color='black', lw=2)
    # colour hot and cold porions of the graph
    temp_list = np.array(temp_list)
    if not dangercold == None:
        ax.fill_between(date_list, temp_list, 0,where=temp_list < dangercold, alpha=0.6, color='darkblue')
    if not toocold == None:
        ax.fill_between(date_list, temp_list, 0,where=temp_list < toocold, alpha=0.6, color='blue')
    if not toohot == None:
        ax.fill_between(date_list, temp_list, 0,where=temp_list > toohot, alpha=0.6, color='red')
    if not dangerhot == None:
        ax.fill_between(date_list, temp_list, 0,where=temp_list > dangerhot, alpha=0.6, color='darkred')
    # add titles and axis labels
    fig = plt.gcf()
    fig.canvas.set_window_title('Temperature Graph')
    plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    # Y temp axis
    plt.ylabel("Temp in " + temp_unit)
    if not ymax == "default":
        plt.ylim(ymax=ymax)
    if not ymin == "default":
        plt.ylim(ymin=ymin)
    # X date axis
    ax.xaxis_date()
    # i should write some code here to only show the parts of the date that are needed
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d-%b %H:%M'))
    fig.autofmt_xdate()
    # show or save graph
    #plt.show()
    plt.savefig(graph_path)


if __name__ == '__main__':
    print "----------------------------------"
    print "-------Preparing To Graph---------"
    print "--------------Temp----------------"
    print "----------------------------------"
    # find the log location and graph ourput path from the dirlocs file or use defaults
    graph_path, log_location, settings_location = find_paths_from_dirlocs()
    # try to load temp settings from pigrows config file where they're also used fo other things
    toocold, dangercold, toohot, dangerhot = get_warning_ranges_from_settings(settings_location)
    # check if user wants to alter any settings
    graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit, ymin, ymax, log_temp_pos, log_date_pos, colour_graph = check_commandline_options(graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit)
    # find dates to use for cut off
    oldest_allowed_date = set_date_values(hours_to_show, show_from)
    # add the log file, by default uses DHT22 log
    log_date, log_temp = add_log(log_location, temp_unit, oldest_allowed_date, log_temp_pos, log_date_pos)
    print "----------------------------------"
    print "most recent temp - " + str(log_temp[-1])[0:4] + " " + temp_unit
    print "----------------------------------"
    if colour_graph == "true":
        print "Colouring graph using temp range; " + str(dangercold) + ", " + str(toocold) + " -- " + str(toohot) + ", " + str(dangerhot) + " "
        make_graph(log_date, log_temp, graph_path, ymin, ymax, toocold, dangercold, toohot, dangerhot)
    else:
        make_graph(log_date, log_temp, graph_path, ymin, ymax, None, None, None, None)
    print("Temp data created and saved to " + graph_path)
