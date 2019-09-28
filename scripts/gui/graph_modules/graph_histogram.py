
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
    num_of_bins = 20
    #
    #
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create a histogram using the graph_histogram.py module...  ")
    # Hourly average
    dictionary_of_sets = {}
    # cycle through the date list sorting everything into hourly sets
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
    hourly_ave_dates = []
    hourly_ave_values = []
    # now go through all the hourly sets we made and average them to crate a new list
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

    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    # Create graph with hourly averages
    n, bins, patches = plt.hist(hourly_ave_values, num_of_bins, density=True, facecolor='green', alpha=0.75, label="Hourly Average")
    # unhash the next line to make a graph using the raw values instead
    #n, bins, patches = plt.hist(value_list, 50, density=True, facecolor='b', alpha=0.75, label="Raw Values")
    plt.title("Histogram of Values\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    plt.xlabel(key_list[0])
    #plt.grid(axis='y')
    ax.legend()
    # Set y axis min and max range
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # save the graph
    plt.savefig(graph_path)
    # tidying up after ourselves
    fig.clf()
    print("Histogram graph created and saved to " + graph_path)
