



def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    print("Making a day/night graph graph...")
    latitude = 51.50
    longitude = 0.12
    light_on_time_hour = "7"
    light_on_time_min = "0"
    light_off_time_hour = "22"
    light_off_time_min = "00"
    day_color = "yellow"
    night_color = "darkblue"
    from suntime import Sun #, SunTimeException
    sun = Sun(latitude, longitude)
    #import the tools we'll be using
    import matplotlib
    import datetime
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    def make_dict_of_sets(date_list, value_list, key_list):
        # make a dictionary containing every day's list of dates and values'
        dictionary_of_sets = {}
        light_markers = []
        day_light_markers = []
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
                # creat light on and off values for lamp
                light_on = day_group + " " + light_on_time_hour + ":" + light_on_time_min + ":00"
                light_off = day_group + " " + light_off_time_hour + ":" + light_off_time_min + ":00"
                light_on = datetime.datetime.strptime(light_on, "%Y:%m:%d %H:%M:%S")
                light_off = datetime.datetime.strptime(light_off, "%Y:%m:%d %H:%M:%S")
                light_markers.append(light_on)
                light_markers.append(light_off)
                # create sunrise and set markers
                day_text_split = day_group.split(":")
                ymd_dayname = datetime.date(int(day_text_split[0]), int(day_text_split[1]), int(day_text_split[2]))
                sunrise = sun.get_local_sunrise_time(ymd_dayname)
                sunset = sun.get_local_sunset_time(ymd_dayname)
                day_light_markers.append(sunrise)
                day_light_markers.append(sunset)
            # put the lists of values and dates into the dictionary of sets under the daygroup key
            dictionary_of_sets[day_group]=[values_to_graph, dates_to_graph]
        return dictionary_of_sets, day_light_markers


    # define a graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    ax.set_prop_cycle(color=['black', 'blue', 'red', 'green'])

    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]

        dictionary_of_sets, day_light_markers = make_dict_of_sets(date_list, value_list, key_list)
        ax.plot(date_list, value_list, label=key_list[0], lw=1)


        flip_color = day_color
        for x in range(0, len(day_light_markers)-1):
            pos1 = mdates.date2num(day_light_markers[x])
            pos2 = mdates.date2num(day_light_markers[x+1])
            ax.axvspan(pos1, pos2, color=flip_color, alpha=0.3)
            if flip_color == night_color:
                flip_color = day_color
            else:
                print(day_light_markers[x], day_light_markers[x+1])
                flip_color = night_color
            #plt.axvline(x, color='darkblue', linewidth=5,alpha=0.3)


    # add legend, title and axis information
    if len(list_of_datasets) > 1:
        ax.legend()
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
