
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
             "show_cumulative":"True",
             "show_daily":"True"
             }
    return graph_module_settings_dict

def make_graph(data_sets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create an averages graph using the graph_cumulative.py module...  ")
    #
    # Settings
    #
    # Load setting from extra
    if extra == {}:
        extra = read_graph_options()
    show_cumulative  = extra['show_cumulative'].lower()
    show_daily    = extra['show_daily'].lower()
    # derived values from settings
    #
    #

    def create_graphable_lists(date_list, value_list, key_list):
        # rolling cumulative
        rolling_cum_dates = []
        rolling_cum_values = []
        cum_value = 0
        for x in range(0, len(value_list)-1):
            cum_value = cum_value + value_list[x]
            rolling_cum_dates.append(date_list[x])
            rolling_cum_values.append(cum_value)


        # daily sets
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
        # daily cum
        daily_cum_dates = []
        daily_cum_values = []
        for key, value in dictionary_of_sets.items():
            days_date_list = value[1]
            days_value_list = value[0]
            day_total = sum(days_value_list)
            # mute the following two lines to stop squaring the graph
            daily_cum_dates.append(days_date_list[0])
            daily_cum_values.append(day_total)
            daily_cum_dates.append(days_date_list[-1])
            daily_cum_values.append(day_total)
        return rolling_cum_dates, rolling_cum_values, values_to_graph, dates_to_graph, daily_cum_dates, daily_cum_values, daily_cum_dates, daily_cum_values


    # create graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))

    # start making the graph
    for x in data_sets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        rolling_cum_dates, rolling_cum_values, values_to_graph, dates_to_graph, daily_cum_dates, daily_cum_values, daily_cum_dates, daily_cum_values = create_graphable_lists(date_list, value_list, key_list)
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        plt.ylabel(key_list[0])
        plt.grid(axis='y')
        # create plot
        if show_cumulative == "true":
            ax.plot(rolling_cum_dates, rolling_cum_values, color='blue', lw=1, label="Cumulative - " + key_list[0])
        if show_daily == "true":
            ax.plot(daily_cum_dates, daily_cum_values, color='green', lw=1, label="Cumlative Daily - " + key_list[0])
        ax.legend()

    # Set y axis min and max range
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # format x axis to date
    ax.xaxis_date()
    fig.autofmt_xdate()
    # save the graph
    plt.savefig(graph_path)
    # tidying up after ourselves
    plt.close(fig)

    print("Cumulative graph created and saved to " + graph_path)
