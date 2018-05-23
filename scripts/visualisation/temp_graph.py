#!/usr/bin/python
# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('Cp1252')
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import datetime
import time
import numpy as np
import os
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

def check_commandline_options(graph_path,
                              log_location,
                              hours_to_show,
                              show_from,
                              toocold,
                              dangercold,
                              toohot,
                              dangerhot,
                              temp_unit="c",
                              ymin="default",
                              ymax="default",
                              log_temp_pos=0,
                              log_date_pos=2,
                              colour_graph="true",
                              box_plot_graph='true',
                              line_graph='true',
                              danger_hours='true',
                              pie_chart='true'):
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
                colour_graph = theval.lower()
            elif thearg == "make_box_plot":
                box_plot_graph = theval.lower()
            elif thearg == "make_line_graph":
                line_graph = theval.lower()
            elif thearg == "make_danger_hours":
                danger_hours = theval.lower()
            elif thearg == "make_pie_chart":
                 pie_chart = theval.lower()
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
            print("                       these are useful when animating")
            print("                       or making graphs for comparing")
            print("Graph choices")
            print("  make_box_plot=true     -enable or disable making the box plot")
            print("  make_line_graph=true   -enable or disable making line graph")
            print("  make_danger_hours=true -enable or disable making danger hours")
            print("  make_pie_chart=true    -enable or disable pie chart")
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
            print("make_box_plot=[true, false]")
            print("make_line_graph=[true, false]")
            print("make_danger_hours=[true,false]")
            print("make_pie_chart=[true,false])
            sys.exit()
        else:
            print(" No idea what you mean by; " + str(argu))
    return graph_path,
           log_location,
           hours_to_show,
           show_from,
           toocold,
           dangercold,
           toohot,
           dangerhot,
           temp_unit,
           ymin,
           ymax,
           log_temp_pos,
           log_date_pos,
           colour_graph,
           box_plot_graph,
           line_graph
           danger_hours,
           pie_chart

def set_date_values(hours_to_show, show_from):
    # if hours_to_show is set then works out when to start the Graph
    # show_from is set then converts it into a datetime object for later use
    # show_from should be set using the format YY-mm-dd-HH:MM note the - instead of a space between dd and HH
    thetime = datetime.datetime.now()
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

def render_line_graph(date_list,temp_list, graph_path, ymin="default", ymax="default", toocold=None, dangercold=None, toohot=None, dangerhot=None):
    print("Making basic line graph")
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

def render_pie(date_list, temp_list, graph_path, ymin, ymax, toocold, dangercold, toohot, dangerhot):
    print("Making EpiphanyHermit's pie...")
    from matplotlib.lines import Line2D

    sliceColors = ['xkcd:red',
                   'xkcd:orange',
                   'xkcd:light green',
                   'xkcd:light blue',
                   'xkcd:purplish blue']

    tempThresholds = [('%.2f°' % dangerhot).replace(".00°","°")
        , ('%.2f°' % toohot).replace(".00°","°")
        , ('{:.2f}° < > {:.2f}°'.format(toohot,toocold)).replace(".00°","°")
        , ('%.2f°' % toocold).replace(".00°","°")
        , ('%.2f°' % dangercold).replace(".00°","°")]

    # Group the data by classification
    tempCount = [0,0,0,0,0]
    for i in range(len(date_list)):
        if temp_list[i] >= dangerhot:
            tempCount[0] += 1
        elif temp_list[i] >= toohot:
            tempCount[1] += 1
        elif temp_list[i] <= dangercold:
            tempCount[4] += 1
        elif temp_list[i] <= toocold:
            tempCount[3] += 1
        else:
            tempCount[2] += 1

    # The slices will be ordered and plotted counter-clockwise.
    temps = list()
    colors = list()
    for i in range(5):
        if tempCount[i] == 0:
            continue
        temps.append(tempCount[i])
        colors.append(sliceColors[i])

    plt.pie(temps, colors=colors, autopct='%1.1f%%', pctdistance=1.16)

    #draw a circle at the center of the pie
    centre_circle = plt.Circle((0,0), 0.75, color='black', fc='white',linewidth=0)
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    fig.suptitle('Temperature Groups', fontsize=14, fontweight='bold')
    plt.title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10, y=1.07)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    plt.axis('equal')

    # legend
    custom_lines = [Line2D([0], [0], color=sliceColors[0], lw=2),
                    Line2D([0], [0], color=sliceColors[1], lw=2),
                    Line2D([0], [0], color=sliceColors[2], lw=2),
                    Line2D([0], [0], color=sliceColors[3], lw=2),
                    Line2D([0], [0], color=sliceColors[4], lw=2)]

    fig.legend(custom_lines, [tempThresholds[0]
            , tempThresholds[1]
            , tempThresholds[2]
            , tempThresholds[3]
            , tempThresholds[4]]
            , bbox_to_anchor=(.97,.97)
            , loc="upper right")

    fig.subplots_adjust(right=0.85, top=0.83)
    plt.savefig(graph_path)

def render_danger_temps_graph(date_list, temp_list, graph_path, ymin, ymax, toocold, dangercold, toohot, dangerhot):
    print("Making EpiphanyHermit's damger temps by hour graph...")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from matplotlib.ticker import StrMethodFormatter

    # Colors for the danger temps
    dangercoldColor = 'xkcd:purplish blue'
    toocoldColor = 'xkcd:light blue'
    toohotColor = 'xkcd:orange'
    dangerhotColor = 'xkcd:red'

    # Group the data by hour
    dangerhotArray = [0]*24
    toohotArray = [0]*24
    toocoldArray = [0]*24
    dangercoldArray = [0]*24
    for i in range(len(date_list)):
        h = int(date_list[i].strftime('%H'))
        if temp_list[i] >= dangerhot:
            dangerhotArray[h] += 1
        elif temp_list[i] >= toohot:
            toohotArray[h] += 1
        elif temp_list[i] <= dangercold:
            dangercoldArray[h] += 1
        elif temp_list[i] <= toocold:
            toocoldArray[h] += 1

    ind = np.arange(24)  # the x locations for the groups
    width = 0.25  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, dangercoldArray, width, yerr=None, color=dangercoldColor, label='DC')
    rects2 = ax.bar(ind - width/4, toocoldArray, width, yerr=None, color=toocoldColor, label='TC')
    rects3 = ax.bar(ind + width/4, toohotArray, width, yerr=None, color=toohotColor, label='TH')
    rects4 = ax.bar(ind + width/2, dangerhotArray, width, yerr=None, color=dangerhotColor, label='DH')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    fig.suptitle('Dangerous Temperature by Hour', fontsize=14, fontweight='bold')
    ax.set_ylabel('Counts')
    ax.set_title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10)
    ax.set_xticks(ind)
    labels = ('00:00', '01:00', '02:00', '03:00', '04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00')
    ax.set_xticklabels(labels,rotation=45)
    ax.legend()
    plt.savefig(graph_path)

def render_box_plot(date_list, temp_list, graph_path, ymin, ymax, toocold, dangercold, toohot, dangerhot):
    print("Making EpiphanyHermit's competition winning box plot...")
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from matplotlib.ticker import StrMethodFormatter

    # Start and End colors for the gradient
    startColor = (118,205,38)
    endColor = (38,118,204)
    dangercoldColor = 'xkcd:purplish blue'
    toocoldColor = 'xkcd:light blue'
    toohotColor = 'xkcd:orange'
    dangerhotColor = 'xkcd:red'

    # Group the data by hour
    hours = [[] for i in range(24)]
    for i in range(len(date_list)):
        h = int(date_list[i].strftime('%H'))
        hours[h].append(temp_list[i])

    # give the graph a rectangular formatr
    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
    fig.suptitle('Median Temperature by Hour', fontsize=14, fontweight='bold')

    bp = ax1.boxplot(hours,whis=0,widths=1,showfliers=False,showcaps=False,medianprops=dict(linestyle=''),boxprops=dict(linestyle=''))
    ax1.set_axisbelow(True)
    ax1.set_title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10)

    # x-axis
    labels = [item.get_text() for item in ax1.get_xticklabels()]
    for i in range(24):
        labels[i] = str(i).zfill(2) + ':00'
    ax1.set_xticklabels(labels,rotation=45,fontsize=8)
    ax1.set_xlim(0, 25)
    ax1.set_xlabel('Hour of the Day')

    # y-axis
    fmt = StrMethodFormatter('{x:,g}°')
    ax1.yaxis.set_major_formatter(fmt)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
    ax1.set_ylabel('Temperature in Celsius')

    # legend
    custom_lines = [Line2D([0], [0], color=dangerhotColor, lw=2),
                    Line2D([0], [0], color=toohotColor, lw=2),
                    Line2D([0], [0], color=toocoldColor, lw=2),
                    Line2D([0], [0], color=dangercoldColor, lw=2)]

    plt.legend(custom_lines, [('%.2f°' % dangerhot).replace(".00°","°")
            , ('%.2f°' % toohot).replace(".00°","°")
            , ('%.2f°' % toocold).replace(".00°","°")
            , ('%.2f°' % dangercold).replace(".00°","°")]
            , bbox_to_anchor=(1.02,1)
            , loc="upper left")

    plt.subplots_adjust(right=0.85)

    # given a defined start and stop, calculate 24 shade gradient
    boxColors = [[] for i in range(24)]
    for i in range(24):
        for j in range(3):
            newColor = 0
            step = abs(startColor[j] - endColor[j]) / 24
            if startColor[j] > endColor[j]:
                newColor = (startColor[j] - (i * step)) / 255
            else:
                newColor = (startColor[j] + (i * step)) / 255
            boxColors[i].append(newColor)

    # Apply box specific info: color, median, warning
    minEdge = 100
    maxEdge = 0
    medians = list(range(24))
    for i in range(24):
        box = bp['boxes'][i]
        boxX = []
        boxY = []
        for j in range(5):
            boxX.append(box.get_xdata()[j])
            boxY.append(box.get_ydata()[j])
        boxCoords = np.column_stack([boxX, boxY])

        # Find min & max box edges to set y-axis limits
        if minEdge > min(boxY):
            minEdge = min(boxY)
        if maxEdge < max(boxY):
            maxEdge = max(boxY)

        # Alert user to dangerous temps
        warning = 'none'
        if min(hours[i]) <= toocold and min(hours[i]) > dangercold:
            warning = toocoldColor
        if min(hours[i]) <= dangercold:
            warning = dangercoldColor
        if max(hours[i]) >= toohot and max(hours[i]) < dangerhot:
            warning = toohotColor
        if max(hours[i]) >= dangerhot:
            warning = dangerhotColor

        # Color the box and set the edge color, if applicable
        boxPolygon = Polygon(boxCoords, facecolor=boxColors[i],edgecolor=warning)
        ax1.add_patch(boxPolygon)

        # add median data
        med = bp['medians'][i]
        medians[i] = med.get_ydata()[0]

    top = maxEdge + 1
    bottom = minEdge - 1
    ax1.set_ylim(bottom, top)

    # Add the medians just above the hour marks
    pos = np.arange(24) + 1
    upperLabels = [str(np.round(s, 2)) for s in medians]
    weights = ['bold', 'semibold']
    k = -1
    for tick, label in zip(range(24), ax1.get_xticklabels()):
        w = tick % 2
        k = k + 1
        ax1.text(pos[tick],bottom + (bottom*0.02),upperLabels[tick],horizontalalignment='center',size='x-small',weight=weights[w],color=boxColors[k])

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
    graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit, ymin, ymax, log_temp_pos, log_date_pos, colour_graph, box_plot_graph, line_graph = check_commandline_options(graph_path, log_location, hours_to_show, show_from, toocold, dangercold, toohot, dangerhot, temp_unit)
    # find dates to use for cut off
    oldest_allowed_date = set_date_values(hours_to_show, show_from)
    # add the log file, by default uses DHT22 log
    log_date, log_temp = add_log(log_location, temp_unit, oldest_allowed_date, log_temp_pos, log_date_pos)
    print "----------------------------------"
    print "most recent temp - " + str(log_temp[-1])[0:4] + " " + temp_unit
    print "----------------------------------"
    # the competition winning graph, each hour's temp ranges shown.
    if box_plot_graph == 'true':
        graph_hours_path = graph_path[:-4] + "_hours.png"
        try:
            render_box_plot(log_date, log_temp, graph_hours_path, ymin, ymax, toocold, dangercold, toohot, dangerhot)
        except Exception as e:
            print("!!! couldn't render box plot, " + str(e))
    # Orignal Graph, simple temp to date line plot with optional colors
    if line_graph == 'true':
        if colour_graph == "true":
            print "Colouring graph using temp range; " + str(dangercold) + ", " + str(toocold) + " -- " + str(toohot) + ", " + str(dangerhot) + " "
            render_line_graph(log_date, log_temp, graph_path, ymin, ymax, toocold, dangercold, toohot, dangerhot)
        else:
            render_line_graph(log_date, log_temp, graph_path, ymin, ymax, None, None, None, None)
        print("Temp data created and saved to " + graph_path)
    #
    if danger_hours = 'true'
        graph_danger_hours_path = graph_path[:-4] + "_danger_hours.png"
        render_danger_temps_graph(log_date, log_temp, graph_danger_hours_path, ymin, ymax, toocold, dangercold, toohot, dangerhot)
    if pie_chart = 'true':
        pie_hours_path = graph_path[:-4] + "_pie.png"
        render_pie(log_date, log_temp, graph_danger_hours_path, ymin, ymax, toocold, dangercold, toohot, dangerhot)
    #
