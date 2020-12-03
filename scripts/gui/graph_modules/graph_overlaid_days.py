
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
             "title_text":"",
             "include_daterange_in_title":"true",
             "color_cycle":"false",
             "line_style":"-",
             "marker":"o",
             "show_legend":"false",
             "show_grid":"true",
             "major_ticks":"",
             "minor_ticks":""
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
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
    marker       = extra['marker']
    line_flags   = marker + line_style
    show_legend  = extra['show_legend'].lower()
    show_grid    = extra['show_grid'].lower()
    major_ticks  = extra['major_ticks']
    minor_ticks  = extra['minor_ticks']

    # read log
    date_list   = list_of_datasets[0][0]
    value_list  = list_of_datasets[0][1]
    key_list    = list_of_datasets[0][2]
    if len(date_list) == 0:
        print("No data to make a graph with...")
        return None
    # read graph settings from ui boxes
    # start making graph
    print("Making divided daily graph...")
    dictionary_of_sets = {}
    for log_item_pos in range(0, len(date_list)):
        day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
        log_time = date_list[log_item_pos]
        log_time = log_time.replace(year=1980, month=1, day=1)
        if day_group in dictionary_of_sets:
            # Read existing lists of dates and values
            values_to_graph = dictionary_of_sets[day_group][0]
            dates_to_graph = dictionary_of_sets[day_group][1]
            # add current value and date to lists
            values_to_graph.append(value_list[log_item_pos])
            dates_to_graph.append(log_time)
        else:
            # create new date and value lists if the day_group doesn't exists yet
            values_to_graph = [value_list[log_item_pos]]
            dates_to_graph = [log_time]
        # put the lists of values and dates into the dictionary of sets under the daygroup key
        dictionary_of_sets[day_group]=[values_to_graph, dates_to_graph]

    fig, ax = plt.subplots(figsize=(size_h, size_v))
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        ax.set_prop_cycle(color=color_cycle)

    for key, value in dictionary_of_sets.items():
        days_date_list = value[1]
        days_value_list = value[0]
        ax.plot(days_date_list, days_value_list, line_flags, label=key)
    if show_legend == "true":
        ax.legend()
    # organise the graphing area
    if not major_ticks == "":
        loc = plticker.MultipleLocator(base=float(major_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_major_locator(loc)
    if not minor_ticks == "":
        loc = plticker.MultipleLocator(base=float(minor_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_minor_locator(loc)
    #
    if show_grid == "true":
        plt.grid(axis='y')
    if title_text == "":
        title_msg = "Daily Values"
    else:
        title_msg = title_text
    if include_daterange == "true":
        title_msg = title_msg + "\n" + str(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"))
    plt.title(title_msg, fontsize=16)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    plt.ylabel(key_list[0]) # + " in " + key_unit)
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    plt.savefig(graph_path)
    print("divided days created and saved to " + graph_path)
    fig.clf()
