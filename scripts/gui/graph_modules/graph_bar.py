
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
             "color_cycle":"false",
             "bar_width":"0.0005",
             "bar_alpha":"0.5",
             "show_grid":"false",
             "major_ticks":"",
             "minor_ticks":""
             }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    print("Want's to create a bar graph using the graph_bar.py module...  ")

    # settings
    # load defaults if no settings supplied
    if extra == {}:
        extra = read_graph_options()
    # set variables to settings from dictionary converting to the appropriate type
    title_text       = extra['title_text']
    show_time_period = extra['show_time_period'].lower()
    color_cycle = extra['color_cycle'].lower()
    if ',' in color_cycle:
        color_cycle.split(",")
    bar_width    = float(extra['bar_width'])
    bar_alpha    = float(extra['bar_alpha'])
    show_grid    = extra['show_grid'].lower()
    major_ticks  = extra['major_ticks']
    minor_ticks  = extra['minor_ticks']

    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    if not color_cycle == 'false' and not color_cycle.strip() == '':
        ax.set_prop_cycle(color=color_cycle)

    # create plot for each dataset
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        ax.bar(date_list, value_list, label=key_list[0], width=bar_width, linewidth=0, alpha=bar_alpha)

    # organise the graphing area
    if not major_ticks == "":
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if not minor_ticks == "":
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)
    if show_grid == "true":
        plt.grid(axis='y')
    if len(list_of_datasets) > 1:
        ax.legend()
    else:
        plt.ylabel(key_list[0])
    if show_time_period == "true":
        title_text = title_text + "\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M"))
    plt.title(title_text)
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
    # tidy up after ourselves
    plt.close(fig)
    print("bar graph created and saved to " + graph_path)
