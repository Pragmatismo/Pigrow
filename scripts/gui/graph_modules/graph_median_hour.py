
#

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "title_text":"",
             "include_daterange_in_title":"true",
             "use_gradiant":"false"

             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from matplotlib.ticker import StrMethodFormatter
    import numpy as np

    print("creating EpiphanyHermit's thresholds pie graph...  ")
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    use_gradiant   = extra['use_gradiant']
    include_daterange = extra['include_daterange_in_title'].lower()
    if dh == "" or th == "" or tc=="" or dc=="":
        msg = " Thresholds not set \n please set danger high, danger low, too high and too low"
        print(msg)
        plt.figure(figsize=(size_h, size_v))
        plt.text(0.2, 0.8, msg)
        #plt.plot(x)
        plt.savefig(graph_path)
        return None

    dangercold = float(dc)
    toocold = float(tc)
    toohot = float(th)
    dangerhot = float(dh)

    date_list   = list_of_datasets[0][0]
    value_list  = list_of_datasets[0][1]
    key_list    = list_of_datasets[0][2]
    if len(date_list) == 0:
        print("No data to make a graph with...")
        return None


    print("Making EpiphanyHermit's competition winning box plot...")
    # Start and End colors for the gradient
    startColor = (118,205,38)
    endColor = (38,118,204)
    dangercoldColor = 'xkcd:purplish blue'
    toocoldColor = 'xkcd:light blue'
    toohotColor = 'xkcd:orange'
    dangerhotColor = 'xkcd:red'
    acceptableColor = "xkcd:green"

#    dangercoldColor = (20,20,200)
#    toocoldColor =    (100,100,250)
#    toohotColor =     (200,100,100)
#    dangerhotColor =  (250,20, 20)
#    acceptableColor = (100,250,100)

    # Group the data by hour
    hours = [[] for i in range(24)]
    for i in range(len(date_list)):
        h = int(date_list[i].strftime('%H'))
        hours[h].append(value_list[i])

    # give the graph a rectangular formatr
    fig, ax1 = plt.subplots(figsize=(size_h, size_v))
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
    fig.suptitle('Median Value by Hour', fontsize=14, fontweight='bold')

    bp = ax1.boxplot(hours,whis=0,widths=1,showfliers=False,showcaps=False,medianprops=dict(linestyle=''),boxprops=dict(linestyle=''))
    ax1.set_axisbelow(True)
    title_msg = title_text
    if include_daterange == "true":
        title_msg = title_msg + "\n" + str(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"))
    ax1.set_title(title_msg, fontsize=10)

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
    #ax1.set_ylabel('Value')

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
    #    if use_gradiant == 'true':
            # create gradiant colours
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
        if min(hours[i]) <= toocold:
            warning_c = toocoldColor
        if min(hours[i]) <= dangercold:
            warning_c = dangercoldColor
        if not min(hours[i]) <= toocold:
            warning_c = acceptableColor

        if max(hours[i]) >= toohot:
            warning_h = toohotColor
        elif max(hours[i]) >= dangerhot:
            warning_h = dangerhotColor
        if not max(hours[i]) >= toohot:
            warning_h = acceptableColor

        # Color the box and set the edge color, if applicable
        if use_gradiant == "true":
            if not warning_c == acceptableColor:
                warning = warning_c
            else:
                warning = warning_h
            boxPolygon = Polygon(boxCoords, facecolor=boxColors[i], edgecolor=warning)
        else:
            boxPolygon = Polygon(boxCoords, facecolor=warning_h, edgecolor=warning_c)
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
    print("Box plot created and saved to " + graph_path)
    plt.savefig(graph_path)
    plt.close(fig)
