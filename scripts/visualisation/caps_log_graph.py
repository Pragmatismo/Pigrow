#!/usr/bin/python
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import datetime
import numpy as np

try:
    sys.path.append('/home/pi/Pigrow/scripts/')
    import pigrow_defs
    script = 'cap_data_graph.py'
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    graph_path = loc_dic['graph_path']
    graph_path_total = graph_path + "cap_data_total_graph.png"
    graph_path_RGB = graph_path + "cap_data_RGB_graph.png"
    log_location = loc_dic['cap_data_log']
    #loc_settings = loc_dic['loc_settings']
    #set_dic = pigrow_defs.load_settings(loc_settings)
except:
    #graph_path = "./cap_data_graph.png"
    #log_location = "./cap_data_log.txt"
    graph_path_total   = "/home/pi/Pigrow/graphs/cap_data_total_graph.png"
    graph_path_RGB   = "/home/pi/Pigrow/graphs/cap_data_RGB_graph.png"
    log_location = "/home/pi/Pigrow/logs/cap_data_log.txt"


hours_to_show = 24*7*52 #hours from the end of the log.
include_split_on_tot = False

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'log':
            log_location = str(argu).split('=')[1]
        elif thearg == 'out_total':
            graph_path_total = str(argu).split('=')[1]
        elif thearg == 'out_RGB':
                graph_path_RGB = str(argu).split('=')[1]
        elif thearg == "hours":
            hours_to_show = int(str(argu).split('=')[1])
        elif thearg == "combine" or 'combine=True':
            include_split_on_tot = True
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  log=DIR/LOG_FILE          - point to a different log file than mentioned in dirlocs")
        print("  out_total=DIR/NAME.png    - totals graph location, can use ./tset.png ")
        print("  out_RGB=DIR/NAME.png      - rgb graph location, can use ./tset.png ")
        print("  out_RGB or out_total=show - only works if not using in matplotlib in Agg mode")
        print("  out_RGB or out_total=none - dnot make that graph")
        print("  hours=NUM                 - Hours of the logs graph, 168 for a week")
        sys.exit()
    elif argu == '-flags':
        print("log=" + log_location)
        print("out_tptal=" + graph_path_total)
        print("out_RGB=" + graph_path_RGB)
        print("hours=NUM")
        sys.exit()
    else:
        print("!!!! No idea what you mean by; " + str(argu))


def add_cap_data_log(linktolog, hours_to_show):
    with open(linktolog, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Adding ' + str(len(logitem)) + ' readings from log.')
    thetime = datetime.datetime.now()
    oldest_allowed_date = thetime - datetime.timedelta(hours=hours_to_show)
    curr_line = len(logitem) - 1
    log_red = []
    log_green = []
    log_blue = []
    log_total = []
    log_date = []
    while curr_line >= 0:
        try:
            item = logitem[curr_line]
            item = item.split(">")
            date = float(item[4].split(".")[0].split("_")[-1])
            date = datetime.datetime.utcfromtimestamp(date)
            if date < oldest_allowed_date:
                print("End of selected date range, ignoring " + str(curr_line) + " more log entries")
                break
            red   = float(item[0])
            green = float(item[1])
            blue  = float(item[2])
            total = float(item[3])
            log_red.append(red)
            log_green.append(green)
            log_blue.append(blue)
            log_total.append(total)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item " + str(curr_line) + " failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    log_red.reverse()
    log_green.reverse()
    log_blue.reverse()
    log_total.reverse()
    log_date.reverse()

    print('We have ' + str(len(log_total)) + ' Caps data readings to work with.')
    if len(log_date) >= 2:
        print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
        return log_red, log_green, log_blue, log_total, log_date
    else:
        print("No data, no graph...")
        exit()

def make_graph(dates, values, graph_path_tot):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(dates, values, width=0.01, color='k', linewidth = 0)
    ax.plot(dates, values, color='darkblue', lw=3)
    ax.xaxis_date()
    plt.title("Time Perod; " + str(dates[0].strftime("%b-%d %H:%M")) + " to " + str(dates[-1].strftime("%b-%d %H:%M")) + " ")
    plt.ylabel("Sum of pixel values")
    fig = plt.gcf()
    fig.canvas.set_window_title('Caps Data Graph')
    fig.autofmt_xdate()
    if graph_path_tot == 'show':
        print("SHowing graph on screen, if possible")
        plt.show()
    else:
        plt.savefig(graph_path_tot)
        print("Graph saved to " + str(graph_path_tot))


def make_RGB_graph(dates, red, green, blue, graph_path_rgb):
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(dates, values, width=0.01, color='k', linewidth = 0)
    ax.plot(dates, red, color='red', lw=3)
    ax.plot(dates, green, color='green', lw=3)
    ax.plot(dates, blue, color='blue', lw=3)
    ax.xaxis_date()
    plt.title("Time Perod; " + str(dates[0].strftime("%b-%d %H:%M")) + " to " + str(dates[-1].strftime("%b-%d %H:%M")) + " ")
    plt.ylabel("Sum of pixel values")
    fig = plt.gcf()
    fig.canvas.set_window_title('Caps Data Graph')
    fig.autofmt_xdate()
    if graph_path_rgb == 'show':
        print("SHowing graph on screen, if possible")
        plt.show()
    else:
        if include_split_on_tot == False:
            plt.savefig(graph_path_rgb)
            print("Graph saved to " + str(graph_path_rgb))
        else:
            print("RGB grpah made, going to combine with totals graph...")

log_red, log_green, log_blue, log_total, log_date = add_cap_data_log(log_location, hours_to_show)
if not graph_path_RGB == 'none':
    make_RGB_graph(log_date, log_red, log_green, log_blue, graph_path_RGB)
if not graph_path_total == 'none':
    if not include_split_on_tot == True:
        plt.clf()
    make_graph(log_date, log_total, graph_path_total)
