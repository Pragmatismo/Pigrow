
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
             "show_time_period":"true",
             "log_window_size":"251",  # set the size of the window when scanning through the log to determine up-down trends
                                      # larger numbers result in less groups, smaller numbers make it more likely to split groups
                                      # when there's a small blip.
             "show_value_in_per":"hour",   # 'hour' 'min' 'second'
                                         # Show the rate of change per second, min, or hour
             "show_grey_bestfit":"true",  # True or False
                                         # shows the simplified logs gray line over the basic line graph
                                         # this can make it more obvious if you want to increase of decrease window size
            "show_grid":"true",
            "bar_width":"0.1"

             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    #
    # User changable options

    #

    #
    #
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import numpy             as np
    from numpy.polynomial.polynomial import polyfit
    #
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text        = extra['title_text']
    show_time_period  = extra["show_time_period"]
    log_window_size   = int(extra["log_window_size"])
    show_value_in_per = extra["show_value_in_per"]
    show_grey_bestfit = extra["show_grey_bestfit"]
    show_grid         = extra['show_grid'].lower()
    bar_width         = float(extra['bar_width'])

    # this ignores other datasets and only uses the first one because otherwise it would just look too messy and stupid
    date_list   = list_of_datasets[0][0]
    value_list  = list_of_datasets[0][1]
    key_list    = list_of_datasets[0][2]

    def generate_slope(data, window_size=3, mode='edge'):
    	# mode could be 'constant' for zero padding
    	assert((window_size % 2) == 1)
    	assert(len(data) >= 1)

    	# pad the data so we don't have edge gaps
    	pad_width = window_size // 2
    	padded_data = np.pad(data, pad_width=pad_width, mode=mode)

    	# slide a window across the padded data
    	result = []
    	for i in range(pad_width, len(padded_data) - pad_width):
    		window = padded_data[i-pad_width:i+pad_width+1]
    		assert(len(window) == window_size)
    		# find the line across the data in the window
    		b, m = polyfit(range(window_size), window, 1)
    		# regenerate the window values to fit the line instead of being the raw_input
    		# data
    		slope = b + m * range(window_size)
    		# see if the first item in the slope array is bigger than the last
    		# that tells use the direction
    		if slope[0] > slope[-1]:
    			result.append('blue')
    		else:
    			result.append('red')

    	assert(len(result) == len(data))

    	return result


    if not (log_window_size % 2) == 1:
        log_window_size = log_window_size + 1
    z = generate_slope(value_list, window_size=log_window_size)
    # set start group
    current_color = z[0]
    red_group_dic = {}
    blue_group_dic = {}
    red_group_num = 1
    blue_group_num = 1
    red_group_name = "red_" + str(red_group_num)
    blue_group_name = "blue_" + str(blue_group_num)
    current_group_v = []
    current_group_d = []
    if current_color == "red":
        current_group = red_group_name
    else:
        current_group = blue_group_name
    # cycle and sort
    for item_pos in range(1, len(z)):
        if z[item_pos] == current_color:
            current_group_v.append(value_list[item_pos])
            current_group_d.append( date_list[item_pos])
        else:
            print("Finishing " + current_group + " with " + str(len(current_group_v)))
            if current_color == "red":
                red_list = [current_group_v.copy(), current_group_d.copy()]
                red_group_dic[current_group]=red_list
                red_group_num = red_group_num + 1
                current_group = "blue_" + str(blue_group_num)
                current_color = "blue"
                current_group_v.clear()
                current_group_d.clear()
            else:
                blue_list = [current_group_v.copy(), current_group_d.copy()]
                blue_group_dic[current_group]=blue_list
                blue_group_num = blue_group_num + 1
                current_group = "red_" + str(red_group_num)
                current_color = "red"
                current_group_v.clear()
                current_group_d.clear()

    # define empty lists to fill
    simple_dates = []
    simple_values = []
    value_ranges = []
    v_range_dates = []
    date_ranges = []
    vcpm = []
    b_simple_dates = []
    b_simple_values = []
    b_value_ranges = []
    b_v_range_dates = []
    b_date_ranges = []
    b_vcpm = []
    # cycle though all the items in the red dictionary ( for rising values )
    for key, value in red_group_dic.items():
        if len(value[0]) > 1:
            # Take the two lists from the dictionaries
            up_value_list = value[0]
            up_date_list = value[1]
            # get first and last dates and values for this group
            first_date = up_date_list[0]
            last_date = up_date_list[-1]
            first_value = up_value_list[0]
            last_value = up_value_list[-1]
            # create a simple log to show the line of best fit
            if show_grey_bestfit == True:
                simple_dates.append(first_date)
                simple_dates.append(last_date)
                simple_values.append(first_value)
                simple_values.append(last_value)
            # Generate value and date range values for this
            value_range = last_value - first_value
            date_range = last_date - first_date
            date_range = date_range.total_seconds()
            # convert date range to min or hour
            if show_value_in_per == "hour" or show_value_in_per == "min":
                date_range = float(date_range / 60)
            if show_value_in_per == "hour":
                date_range = float(date_range / 60)
            # determine the value change per timeunit ( hour, min, sec )
            per_timeunit = value_range / date_range
            if value_range > 0: # ignore minus ones because they cause division errors
                # add everything into lists we'll use to graph things
                value_ranges.append(value_range)
                v_range_dates.append(first_date)
                date_ranges.append(date_range)
                vcpm.append(per_timeunit)
                #v_range_dates.append(last_date)
            else:
                print(" ignoring due to negative value - ", value_range, date_range, per_timeunit, len(up_value_list))
    # cycle through all the items in the blue dictionary ( for falling values )
    for key, value in blue_group_dic.items():
        if len(value[0]) > 1:
            # Take the two lists from the dictionaries
            up_value_list = value[0]
            up_date_list = value[1]
            # get first and last dates and values for this group
            first_date = up_date_list[0]
            last_date = up_date_list[-1]
            first_value = up_value_list[0]
            last_value = up_value_list[-1]
            # create a simple log to show the line of best fit
            if show_grey_bestfit == True:
                b_simple_dates.append(first_date)
                b_simple_dates.append(last_date)
                b_simple_values.append(first_value)
                b_simple_values.append(last_value)
            # Generate value and date range values for this
            value_range = first_value - last_value # because this set the values go down the first value will be higher
                                                   # than last value so to avoid negative numbers we deduct first from last
            date_range = last_date - first_date
            date_range = date_range.total_seconds()
            # Convert date range to min or hour
            if show_value_in_per == "hour" or show_value_in_per == "min":
                date_range = float(date_range / 60)
            if show_value_in_per == "hour":
                date_range = float(date_range / 60)
            # determine the value change per timeunit ( hour, min, sec )
            per_timeunit = value_range / date_range
            if value_range > 0:
                # add back the negative we removed earlier
                minus_value_range = value_range - value_range - value_range
                minus_date_range = date_range - date_range - date_range
                per_timeunit = per_timeunit - per_timeunit - per_timeunit
                # add everything into lists we'll use to graph things
                b_value_ranges.append(minus_value_range)
                b_v_range_dates.append(first_date)
                b_date_ranges.append(minus_date_range)
                b_vcpm.append(per_timeunit)
                #b_v_range_dates.append(last_date)
            else:
                print(" ignoring due to negative value - ", value_range, date_range, per_timeunit, len(up_value_list))

    # Create the Graphs
    fig, ax = plt.subplots(figsize=(size_h, size_v*2))
    ax1 = plt.subplot(411)
    # Top Graph - Change Per Time Unit (hour, min, sec)
    if show_time_period == "true":
        title_text = title_text + "\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M"))
    plt.title(title_text)
    ax1.bar(v_range_dates, vcpm, width=bar_width, color="red")
    ax1.bar(b_v_range_dates, b_vcpm, width=bar_width, color="blue")
    if show_grid == "true":
        plt.grid(axis='y')
    ax1.xaxis_date()
    plt.ylabel("Change of " + key_list[0] + " per "+ show_value_in_per + ".")
    # Second Graph - Basic line graph with markers for change of temp direction
    ax2 = plt.subplot(412, sharex=ax1)
    ax2.plot(date_list, value_list, lw=1, color="black")
    if show_grid == "true":
        plt.grid(axis='y')
    if show_grey_bestfit == True:
        ax2.plot(simple_dates, simple_values, lw=1, color="grey")        # turn these on if you want to show the simplified graph
        ax2.plot(b_simple_dates, b_simple_values, lw=1, color="grey")    # which displays the lines of best fit and can help determine window size
    plt.ylabel(key_list[0])
    for x in b_v_range_dates:
        plt.axvline(x, color="blue")#d62728')
    for x in v_range_dates:
        plt.axvline(x, color='red')
    # Thrid Graph - Total value ranges per group
    ax3 = plt.subplot(413, sharex=ax1)
    ax3.bar(v_range_dates, value_ranges, width=bar_width, color="red")
    ax3.bar(b_v_range_dates, b_value_ranges, width=bar_width, color="blue")
    if show_grid == "true":
        plt.grid(axis='y')
    plt.title("Total " + key_list[0] + " Change")
    plt.ylabel(key_list[0])
    # Duration of each group in selected time unit (hours, min, sec)
    ax4 = plt.subplot(414, sharex=ax1)
    ax4.bar(v_range_dates, date_ranges, width=bar_width, color="red")
    ax4.bar(b_v_range_dates, b_date_ranges, width=bar_width, color="blue")
    if show_grid == "true":
        plt.grid(axis='y')
    plt.ylabel("Duration in " + show_value_in_per)
    plt.title("Duration of each " + key_list[0] + " change")
    # Final graphing config
    fig.autofmt_xdate()
    # I think each graph needs a copy of this for it to work?
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("ups and downs created and saved to " + graph_path)
    fig.clf()
