



def make_graph(date_list, value_list, key_list, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    print("Making a colourful graph graph...")
    #import the tools we'll be using
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    # make a dictionary containing every day's list of dates and values'
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
    # define a graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    # cycle through the dictionary and add each set with a new colour
    for key, value in dictionary_of_sets.items():
        days_date_list = value[1]
        days_value_list = value[0]
        ax.plot(days_date_list, days_value_list, lw=1, label=key)
    # add legend, title and axis information
    #ax.legend() #no need for this it just takes up space
    plt.title("Daily Values\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    ax.xaxis_date()
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()
    plt.ylabel(key_list[0]) # + " in " + key_unit)
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("divided days created and saved to " + graph_path)
    fig.clf()
