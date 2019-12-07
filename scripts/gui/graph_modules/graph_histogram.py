
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
             "num_of_bins":"20",
             "show_raw":"false",
             "show_hourly_ave":"true",
             "show_daily_ave":"true",
             "show_grid":"true",
             "color_cycle":"false",
             "alpha_val":"0.75"
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    #
    # Settings
    #
    if extra == {}:
        extra = read_graph_options()
    num_of_bins      = int(extra['num_of_bins'])
    show_raw         = extra['show_raw'].lower()
    show_hourly_ave  = extra['show_hourly_ave'].lower()
    show_daily_ave   = extra['show_daily_ave'].lower()
    show_grid        = extra['show_grid'].lower()
    color_cycle      = extra['color_cycle'].lower()
    if ',' in color_cycle:
        color_cycle.split(",")
    alpha_val        = float(extra['alpha_val'])

    #
    #
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create a histogram using the graph_histogram.py module...  ")

    def make_hour_averages(date_list, value_list, key_list):
        # Hourly average
        dictionary_of_sets = {}
        # cycle through the date list sorting everything into hourly sets
        for log_item_pos in range(0, len(date_list)):
            hour_group = date_list[log_item_pos].strftime("%Y:%m:%d:%H")
            if hour_group in dictionary_of_sets:
                # Read existing lists of dates and values
                values_to_graph = dictionary_of_sets[hour_group][0]
                # add current value and date to lists
                values_to_graph.append(value_list[log_item_pos])
            else:
                # create new date and value lists if the hour_group doesn't exists yet
                values_to_graph = [value_list[log_item_pos]]
            # put the lists of values and dates into the dictionary of sets under the hourgroup key
            dictionary_of_sets[hour_group]=[values_to_graph]
        hourly_ave_values = []
        # now go through all the hourly sets we made and average them to crate a new list
        for key, value in dictionary_of_sets.items():
            hours_value_list = value[0]
            hour_total = sum(hours_value_list)
            hour_average = hour_total / len(hours_value_list)
            hourly_ave_values.append(hour_average)
        return hourly_ave_values

    def make_day_averages(date_list, value_list, key_list):
        # Hourly average
        dictionary_of_sets = {}
        # cycle through the date list sorting everything into daily sets
        for log_item_pos in range(0, len(date_list)):
            day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
            if day_group in dictionary_of_sets:
                # Read existing lists of dates and values
                values_to_graph = dictionary_of_sets[day_group][0]
                # add current value and date to lists
                values_to_graph.append(value_list[log_item_pos])
            else:
                # create new date and value lists if the day_group doesn't exists yet
                values_to_graph = [value_list[log_item_pos]]
            # put the lists of values and dates into the dictionary of sets under the hourgroup key
            dictionary_of_sets[day_group]=[values_to_graph]
        daily_ave_values = []
        # now go through all the daily sets we made and average them to crate a new list
        for key, value in dictionary_of_sets.items():
            days_value_list = value[0]
            day_total = sum(days_value_list)
            day_average = day_total / len(days_value_list)
            daily_ave_values.append(day_average)
        return daily_ave_values

    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        ax.set_prop_cycle(color=color_cycle)
    # cycle through making the plots for each dataset
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        # Create graph with hourly averages
        if show_hourly_ave == "true":
            hourly_ave_values =  make_hour_averages(date_list, value_list, key_list)
            n, bins, patches = plt.hist(hourly_ave_values, num_of_bins, density=True, alpha=alpha_val, label="Hourly Average - " + key_list[0])
        if show_daily_ave == "true":
            daily_ave_values =  make_day_averages(date_list, value_list, key_list)
            n, bins, patches = plt.hist(daily_ave_values, num_of_bins, density=True, alpha=alpha_val, label="Daily Average - " + key_list[0])
        # make a graph using the raw values
        if show_raw == "true":
            n, bins, patches = plt.hist(value_list, num_of_bins, density=True, alpha=alpha_val, label="Raw Values - " + key_list[0])
    # finalize graph with labels and axis
    plt.title("Histogram of Values\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    plt.xlabel(key_list[0])
    if show_grid == "true":
        plt.grid(axis='y')
    ax.legend()
    # Set y axis min and max range
    if not ymax == "":
        plt.ylim(ymax=int(1))
        plt.xlim(xmax=int(ymax))
    if not ymin == "":
        plt.xlim(xmin=int(ymin))
        plt.ylim(ymin=int(0))
    # save the graph
    plt.savefig(graph_path)
    # tidying up after ourselves
    plt.close(fig)
    print("Histogram graph created and saved to " + graph_path)
