


def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "title_text":"",
             "show_time_period":"true",
             "color_cycle":"false",
             "line_style":"-",
             "marker":"",
             "show_grid":"true",
             "major_ticks":"",
             "minor_ticks":"1"
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    print("Making a colourful graph graph...")
    #import the tools we'll be using
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker
    #
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    color_cycle  = extra['color_cycle'].lower()
    if ',' in color_cycle:
        color_cycle.split(",")
    line_style   = extra['line_style']
    marker       = extra['marker']
    line_flags   = marker + line_style
    show_grid    = extra['show_grid'].lower()
    major_ticks  = extra['major_ticks']
    minor_ticks  = extra['minor_ticks']
    show_time_period = extra["show_time_period"]

    # make a dictionary containing every day's list of dates and values'
    def make_dict_of_sets(date_list, value_list, key_list):
        dictionary_of_sets = {}
        for log_item_pos in range(0, len(date_list)):
            day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
            log_time = date_list[log_item_pos]
            #log_time = log_time.replace(year=1980, month=1, day=1)
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
        return dictionary_of_sets

    # define a graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        ax.set_prop_cycle(color=color_cycle)
    # cycle through making sets of plots for each dataset
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        dictionary_of_sets = make_dict_of_sets(date_list, value_list, key_list)

        # cycle through the dictionary and add each set with a new colour
        for key, value in dictionary_of_sets.items():
            days_date_list = value[1]
            days_value_list = value[0]
            ax.plot(days_date_list, days_value_list, line_flags, lw=1, label=key)

    # organise the graphing area
    if not major_ticks == "":
        loc = plticker.MultipleLocator(base=float(major_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_major_locator(loc)
    if not minor_ticks == "":
        loc = plticker.MultipleLocator(base=float(minor_ticks)) # this locator puts ticks at regular intervals
        ax.yaxis.set_minor_locator(loc)
    if show_grid == "true":
        plt.grid(axis='y')
    if show_time_period == "true":
        title_text = title_text + "\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M"))
    plt.title(title_text)
    ax.xaxis_date()
    fig.autofmt_xdate()
    plt.ylabel(key_list[0])
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))

    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("divided days created and saved to " + graph_path)
    plt.close(fig)
