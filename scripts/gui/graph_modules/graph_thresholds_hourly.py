
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
    #import matplotlib.ticker as plticker
    import numpy as np

    print("creating EpiphanyHermit's thresholds by hour graph...  ")
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    include_daterange = extra['include_daterange_in_title'].lower()
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

    # start making graph
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
        if value_list[i] >= dangerhot:
            dangerhotArray[h] += 1
        elif value_list[i] >= toohot:
            toohotArray[h] += 1
        elif value_list[i] <= dangercold:
            dangercoldArray[h] += 1
        elif value_list[i] <= toocold:
            toocoldArray[h] += 1
    ind = np.arange(24)  # the x locations for the groups
    width = 0.25  # the width of the bars
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    rects1 = ax.bar(ind - width/2, dangercoldArray, width, yerr=None, color=dangercoldColor, label='DC')
    rects2 = ax.bar(ind - width/4, toocoldArray, width, yerr=None, color=toocoldColor, label='TC')
    rects3 = ax.bar(ind + width/4, toohotArray, width, yerr=None, color=toohotColor, label='TH')
    rects4 = ax.bar(ind + width/2, dangerhotArray, width, yerr=None, color=dangerhotColor, label='DH')
    # Add some text for labels, title and custom x-axis tick labels, etc.
    fig.suptitle('Dangerous Values by Hour', fontsize=14, fontweight='bold')
    ax.set_ylabel('Counts')
    title_msg = title_text
    if include_daterange == "true":
        title_msg = title_msg + "\n" + str(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"))
    ax.set_title(title_msg, fontsize=10)

    ax.set_xticks(ind)
    labels = ('00:00', '01:00', '02:00', '03:00', '04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00')
    ax.set_xticklabels(labels,rotation=45)
    ax.legend()
    plt.savefig(graph_path)
    print("danger values graph created and saved to " + graph_path)
    plt.close(fig)
