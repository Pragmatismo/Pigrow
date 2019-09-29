
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
    num_hours_to_show = 100

    #
    #
    import os
    import datetime
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    print("Want's to create an animated set using the graph_animate_hour_aves.py module...  ")

    # Hourly average
    # cycle through the date list sorting everything into hourly sets
    dictionary_of_sets = {}
    for log_item_pos in range(0, len(date_list)):
        hour_group = date_list[log_item_pos].strftime("%Y:%m:%d:%H")
        log_time = date_list[log_item_pos]
        if hour_group in dictionary_of_sets:
            # Read existing lists of dates and values
            values_to_graph = dictionary_of_sets[hour_group][0]
            dates_to_graph = dictionary_of_sets[hour_group][1]
            # add current value and date to lists
            values_to_graph.append(value_list[log_item_pos])
            dates_to_graph.append(log_time)
        else:
            # create new date and value lists if the hour_group doesn't exists yet
            values_to_graph = [value_list[log_item_pos]]
            dates_to_graph = [log_time]
        # put the lists of values and dates into the dictionary of sets under the hourgroup key
        dictionary_of_sets[hour_group]=[values_to_graph, dates_to_graph]

    # cycle though and create a list of hourly averages paired with the final date of that hour
    hourly_ave_dates = []
    hourly_ave_values = []
    for key, value in dictionary_of_sets.items():
        hours_date_list = value[1]
        hours_value_list = value[0]
        hour_total = sum(hours_value_list)
        hour_average = hour_total / len(hours_value_list)
        # mute the following two lines to stop squaring the graph
        hourly_ave_dates.append(hours_date_list[0])
        hourly_ave_values.append(hour_average)
        # add the values to the hourly average values list using the date of the final reading that day
        hourly_ave_dates.append(hours_date_list[-1])
        hourly_ave_values.append(hour_average)

    # find the min and max values so we can stabalise our graph
    ymin = hourly_ave_values[0]
    ymax = hourly_ave_values[0]
    for x in hourly_ave_values:
        if x > ymax:
            ymax = x
        if x < ymin:
            ymin = x
    # break down the path so we can edit the filename and create a folder for the animation
    graph_path, graph_name = os.path.split(graph_path)
    graph_name = graph_name.split(".png")[0]
    graph_path = os.path.join(graph_path, "animated_" + graph_name)
    if not os.path.isdir(graph_path):
        os.makedirs(graph_path)
    # cycle through making and saving a graph for each frame in the range
    for x in range(num_hours_to_show, len(hourly_ave_dates)):
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        plt.axis(ymin=ymin-1, ymax=ymax+1)
        ax.plot(hourly_ave_dates[x-num_hours_to_show:x], hourly_ave_values[x-num_hours_to_show:x], color='black', lw=1)
        rolling_last_datetime = str(datetime.datetime.timestamp(hourly_ave_dates[x])).split(".")[0]
        current_graph_name = graph_name + "_" + str(rolling_last_datetime) + ".png"
        current_graph_filepath = os.path.join(graph_path, current_graph_name)
        plt.title("Time Perod; " + str(hourly_ave_dates[x-num_hours_to_show].strftime("%b-%d %H:%M")) + " to " + str(hourly_ave_dates[x].strftime("%b-%d %H:%M")) + " ")
        plt.ylabel(key_list[0])
        ax.xaxis.set_major_locator(ticker.NullLocator())
        ax.xaxis.set_minor_locator(ticker.NullLocator())
        text = hourly_ave_dates[ x ].strftime("%b-%d %H:%M")
        ax.text(hourly_ave_dates[ x ], ymin-1.5, text, fontsize=14)
        plt.savefig(current_graph_filepath)
        print("Frame " + str(x) + " saved to " + current_graph_filepath)
        # tidying up after ourselves
        fig.clf()


    # start making the graph
    # Create graph with hourly averages
    #n, bins, patches = plt.hist(hourly_ave_values, 50, density=True, facecolor='cyan', alpha=0.75, label="Hourly Average")
    # unhash the next line to make a graph using the raw values instead
    #n, bins, patches = plt.hist(value_list, 50, density=True, facecolor='b', alpha=0.75, label="Raw Values")
    #plt.grid(axis='y')
    #ax.legend()

    print("animated set created and saved to " + graph_path)
