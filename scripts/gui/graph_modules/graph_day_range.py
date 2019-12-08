

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "title_text":"Min - Max Values",
             "show_time_period":"true",
             "show_grid":"false",
             "major_ticks":"",
             "minor_ticks":"1"
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    print("Making a day range graph graph...")
    #import the tools we'll be using
    import matplotlib
    import datetime
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker

    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text   = extra['title_text']
    show_grid    = extra['show_grid'].lower()
    major_ticks  = extra['major_ticks']
    minor_ticks  = extra['minor_ticks']
    show_time_period = extra["show_time_period"].lower()


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

    def find_values_from_dics(dictionary_of_sets):
        # loop through each set finding min-max values and adding them to lists.
        day_names = []
        day_min_val = []
        day_max_val = []
        day_range = []
        for key, value in dictionary_of_sets.items():
            days_date_list = value[1]
            days_value_list = value[0]
            #ax.plot(days_date_list, days_value_list, lw=1, label=key, color="black")
            #find min max values
            val_range=0
            min_val = days_value_list[0]
            max_val = days_value_list[0]
            for x in range(1, len(days_value_list)):
                current_value = days_value_list[x]
                if  current_value > max_val:
                    max_val = current_value
                if current_value < min_val:
                    min_val = current_value
                val_range = max_val - min_val
            day_names.append(key)
            day_min_val.append(min_val)
            day_max_val.append(max_val)
            day_range.append(val_range)
        return day_names, day_min_val, day_max_val, day_range

    # define a graph space and plot bars
    fig, ax = plt.subplots(figsize=(size_h, size_v))

    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        dictionary_of_sets = make_dict_of_sets(date_list, value_list, key_list)
        day_names, day_min_val, day_max_val, day_range = find_values_from_dics(dictionary_of_sets)
        ax.bar(day_names, day_max_val, color="red")
        ax.bar(day_names, day_min_val, color="blue")
        #ax.bar(day_names, day_range, color="black")
        fig.autofmt_xdate()
        plt.ylabel(key_list[0]) # + " in " + key_unit)

    #
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
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("day range days created and saved to " + graph_path)
    plt.close(fig)
