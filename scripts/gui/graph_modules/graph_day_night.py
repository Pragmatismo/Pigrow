

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "use_time":"lamp",       # sun or lamp
             "latitude":"51.50",
             "longitude":"0.12",
             "light_on_time_hour":"7",
             "light_on_time_min":"0",
             "light_off_time_hour":"22",
             "light_off_time_min":"00",
             "label_duration":"false",
             "title_text":"",
             "show_time_period":"true",
             "color_cycle":"false",
             "line_style":"-",
             "marker":"",
             "show_grid":"true",
             "major_ticks":"",
             "minor_ticks":"1",
             "ylabel":""
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    print("Making a day/night graph graph...")
    import matplotlib
    import datetime
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker

    day_color = "yellow"
    night_color = "darkblue"

    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    use_time            = extra['use_time'].lower()
    latitude            = float(extra['latitude'])
    longitude           = float(extra['longitude'])
    light_on_time_hour  = extra['light_on_time_hour']
    light_on_time_min   = extra['light_on_time_min']
    light_off_time_hour = extra['light_off_time_hour']
    light_off_time_min  = extra['light_off_time_min']
    label_duration      = extra['label_duration']
    title_text          = extra['title_text']
    color_cycle         = extra['color_cycle'].lower()
    if ',' in color_cycle:
        color_cycle.split(",")
    line_style          = extra['line_style']
    marker              = extra['marker']
    line_flags = marker + line_style
    show_grid           = extra['show_grid'].lower()
    major_ticks         = extra['major_ticks']
    minor_ticks         = extra['minor_ticks']
    show_time_period    = extra["show_time_period"]
    ylabel              = extra['ylabel']

    #import the tools we'll be using
    if use_time == "sun":
        from suntime import Sun # to install run the command pip3 install suntime
        sun = Sun(latitude, longitude)

    def make_dict_of_sets(date_list, value_list, key_list):
        # make a dictionary containing every day's list of dates and values'
        dictionary_of_sets = {}
        light_markers = []
        durations = []
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
                # create sunrise and set markers
                day_text_split = day_group.split(":")
                ymd_dayname = datetime.date(int(day_text_split[0]), int(day_text_split[1]), int(day_text_split[2]))
                if use_time == "sun":
                    sunrise = sun.get_local_sunrise_time(ymd_dayname)
                    sunset = sun.get_local_sunset_time(ymd_dayname)
                    light_markers.append(sunrise)
                    light_markers.append(sunset)
                    duration = sunset - sunrise
                    print(duration)
                    durations.append(duration)
                    durations.append("")
                else:
                    light_on = day_group + " " + light_on_time_hour + ":" + light_on_time_min + ":00"
                    light_off = day_group + " " + light_off_time_hour + ":" + light_off_time_min + ":00"
                    light_on = datetime.datetime.strptime(light_on, "%Y:%m:%d %H:%M:%S")
                    light_off = datetime.datetime.strptime(light_off, "%Y:%m:%d %H:%M:%S")
                    light_markers.append(light_on)
                    light_markers.append(light_off)
                    duration = light_off - light_on
                    print(duration)
                    durations.append(duration)
                    durations.append("")
            # put the lists of values and dates into the dictionary of sets under the daygroup key
            dictionary_of_sets[day_group]=[values_to_graph, dates_to_graph]
        return dictionary_of_sets, light_markers, durations


    # define a graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        ax.set_prop_cycle(color=color_cycle)
    # cycle through and make plot
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        dictionary_of_sets, light_markers, durations = make_dict_of_sets(date_list, value_list, key_list)
        print(len(light_markers), len(durations))
        ax.plot(date_list, value_list, label=key_list[0], lw=1)
        flip_color = day_color
        for x in range(0, len(light_markers)-1):
            pos1 = mdates.date2num(light_markers[x])
            pos2 = mdates.date2num(light_markers[x+1])
            ax.axvspan(pos1, pos2, color=flip_color, alpha=0.3)
            text_pos = pos2
            if label_duration == "true":
                if not ymin == "":
                    label_height = float(ymin)
                else:
                    label_height = 0
                ax.text(text_pos, label_height, " " + str(durations[x]), rotation=90,va='bottom',ha='right')
            if flip_color == night_color:
                flip_color = day_color
            else:
                flip_color = night_color
            #plt.axvline(x, color='darkblue', linewidth=5,alpha=0.3)

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
    if len(list_of_datasets) > 1:
        ax.legend()
    ax.xaxis_date()
    fig.autofmt_xdate()
    plt.ylabel(ylabel)
    if not ymax == "":
        plt.ylim(ymax=float(ymax))
    if not ymin == "":
        plt.ylim(ymin=float(ymin))
    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("divided days created and saved to " + graph_path)
    fig.clf()
