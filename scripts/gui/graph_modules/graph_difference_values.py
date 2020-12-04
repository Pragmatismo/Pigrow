
#
# This is an example script which can be used as a template to make your own graphs which intergrate with the pigrow remote gui
#
# Copy this file, remane it something that fits the pattern  graph_[name].py and save it into the graph_modules folder
#
# All code must happen within the make_graph function,
# Save the graph using the exact path given by graph_path
#
#
#
def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "title_text":"Value difference between log entries",
             "include_daterange_in_title":"true",
             "color_cycle":"false",
             "line_style":"-",
             "line_width":"1",
             "marker":"o",
             "show_grid":"true",
             "major_ticks":"",
             "minor_ticks":""
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    #import matplotlib
    #matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker

    # load defaults if no settings supplied
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    include_daterange = extra['include_daterange_in_title'].lower()
    color_cycle  = extra['color_cycle'].lower()
    if ',' in color_cycle:
        color_cycle.split(",")
    line_style   = extra['line_style']
    line_width   = float(extra['line_width'])
    marker       = extra['marker']
    line_flags   = marker + line_style
    show_grid    = extra['show_grid'].lower()
    major_ticks  = extra['major_ticks']
    minor_ticks  = extra['minor_ticks']


    print("creating a value differnce graph...  ")
    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    # read data from logs
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]

        # make list of diffs
        if len(date_list) < 2:
            print(" Not enough datapoints to work with for difference graph" + key_list[0])
            # create list of Value diffs
        value_dif_list = []
        prior_value = value_list[0]
        for current_value in value_list[1:]:
            value_diff = prior_value - current_value
            value_dif_list.append(value_diff)
            prior_value = current_value
        # plot to graph
        ax.plot(date_list[1:], value_dif_list, line_flags, lw=line_width, label=key_list[0])


        # organise the graphing area
    if include_daterange == "true":
        title_text = title_text + "\n" + str(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"))
        ax.set_title(title_text, fontsize=16)
    if not major_ticks == "":
        loc = plticker.MultipleLocator(base=float(major_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_major_locator(loc)
    if not minor_ticks == "":
        loc = plticker.MultipleLocator(base=float(minor_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_minor_locator(loc)
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        print("Setting color cycle " + color_cycle)
        ax.set_prop_cycle(color=color_cycle)
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    if show_grid == "true":
        plt.grid(axis='y')

    if len(list_of_datasets) > 1:
        ax.legend()
    else:
        plt.ylabel(key_list[0] + "Value difference")

    ax.xaxis_date()
    fig.autofmt_xdate()
    plt.savefig(graph_path)
    fig.clf()


    # create plot for each dataset
#    for x in list_of_datasets:
#        date_list = x[0]
#        value_list = x[1]
#        key_list = x[2]
#        ax.plot(date_list, value_list, line_flags, label=key_list[0], lw=1)


    #
