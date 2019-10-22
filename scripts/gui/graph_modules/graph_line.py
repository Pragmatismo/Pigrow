
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

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create a line graph using the graph_line.py module...  ")
    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    # create plot
    ax.set_prop_cycle(color=['black', 'blue', 'red', 'green'])
    for x in list_of_datasets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        ax.plot(date_list, value_list, label=key_list[0], lw=1)
    # Set y axis min and max range
    if len(list_of_datasets) > 1:
        ax.legend()
    else:
        plt.ylabel(key_list[0])

    plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
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

    print("line graph created and saved to " + graph_path)
