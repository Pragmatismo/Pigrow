
#

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "title_text":"",
             "include_daterange_in_title":"true"

             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import numpy as np

    print("creating EpiphanyHermit's thresholds pie graph...  ")
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    include_daterange = extra['include_daterange_in_title'].lower()
    if dh == "" or th == "" or tc=="" or dc=="":
        msg = " Thresholds not set \n please set danger high, danger low, too high and too low"
        print(msg)
        plt.figure(figsize=(size_h, size_v))
        plt.text(0.2, 0.8, msg)
        #plt.plot(x)
        plt.savefig(graph_path)
        plt.close(fig)
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


    print("Making EpiphanyHermit's pie...")
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
        if value_list[i] >= dangerhot:
            tempCount[0] += 1
        elif value_list[i] >= toohot:
            tempCount[1] += 1
        elif value_list[i] <= dangercold:
            tempCount[4] += 1
        elif value_list[i] <= toocold:
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

    fig, ax = plt.subplots(figsize=(size_h, size_v))
    plt.pie(temps, colors=colors, autopct='%1.1f%%', pctdistance=1.16)

    #draw a circle at the center of the pie
    centre_circle = plt.Circle((0,0), 0.75, color='black', fc='white',linewidth=0)
    fig.gca().add_artist(centre_circle)
    fig.suptitle('Value Groups', fontsize=14, fontweight='bold')
    title_msg = title_text
    if include_daterange == "true":
        title_msg = title_msg + "\n" + str(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"))
    plt.title(title_msg, fontsize=10)
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
    print("pie created and saved to " + graph_path)
    plt.savefig(graph_path)
    plt.close(fig)
