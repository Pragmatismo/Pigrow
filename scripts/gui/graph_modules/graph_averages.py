
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

def make_graph(date_list, value_list, key_list, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc=""):
    #
    # Settings
    #
    average_size = 500
    has = int(average_size / 2)
    #
    #
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create an averages graph using the graph_aves.py module...  ")
    # create aveages
    # total average
    running_total = 0
    for x in range(0, len(value_list)):
        running_total = running_total + value_list[x]
    average_value = running_total / len(value_list)
    print (average_value)
    # rolling average
    rolling_ave_dates = []
    rolling_ave_values = []
    for x in range(has, len(value_list)-has):
        rolling_total = sum(value_list[x-has:x+has])
        rolling_average = rolling_total / average_size
        rolling_ave_dates.append(date_list[x])
        rolling_ave_values.append(rolling_average)
    # daily average
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
    daily_ave_dates = []
    daily_ave_values = []
    for key, value in dictionary_of_sets.items():
        days_date_list = value[1]
        days_value_list = value[0]
        day_total = sum(days_value_list)
        day_average = day_total / len(days_value_list)
        # mute the following two lines to stop squaring the graph 
        daily_ave_dates.append(days_date_list[0])
        daily_ave_values.append(day_average)
        daily_ave_dates.append(days_date_list[-1])
        daily_ave_values.append(day_average)
    #


    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    plt.ylabel(key_list[0])
    # create plot
    ax.plot(date_list, value_list, color='black', lw=1, label="Raw Data")
    ax.plot(rolling_ave_dates, rolling_ave_values, color='blue', lw=1, label="Rolling Average")
    ax.plot(daily_ave_dates, daily_ave_values, color='green', lw=1, label="Daily Average")
    ax.axhline(y=average_value, label="Average")
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
    fig.clf()

    print("Averages graph created and saved to " + graph_path)
