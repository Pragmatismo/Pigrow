
def make_graph(date_list, value_list, key_list, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc=""):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    print("Want's to create a fun new line graph...  ")
    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
    plt.ylabel(key_list[0])
    # create plot
    ax.plot(date_list, value_list, color='red', lw=1)
    # Set axis
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    ax.xaxis_date()
    fig.autofmt_xdate()
    # save the graph
    plt.savefig(graph_path)
    # tidying up after ourselves
    fig.clf()

    print("fun new line graph created and saved to " + graph_path)
