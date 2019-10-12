
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

def make_graph(date_list, value_list, key_list, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create a line graph using the graph_line.py module...  ")
    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    plt.ylabel(key_list[0])
    # create plot
    ax.plot(date_list, value_list, color='blue', lw=1)
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

    print("line graph created and saved to " + graph_path)
