



def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h=9, size_v=12, dh="", th="", tc="", dc="", extra=[]):
    print("Making a pretty picture graph...")
    #import the tools we'll be using
    import os
    import sys
    import datetime
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    #
    #
    pic_to_use = "thermometer.png"
    # bar_bottom_x = 193
    # bar_bottom_y = 350
    # bar_height = 334
    # bar_width = 87
    bar_bottom_x = 62
    bar_bottom_y = 350
    bar_height = 334
    bar_width = 87
    font_size = 18

    #
    # #
    # # # sort the data into the bits we need
    # #
    #
    # this ignores other datasets and only uses the first one
    date_list   = list_of_datasets[0][0]
    value_list  = list_of_datasets[0][1]
    key_list    = list_of_datasets[0][2]

    # loop through the values finding min-max values if not supplied
    if ymin == "" or ymax == "":
        val_range=0
        min_val = value_list[0]
        max_val = value_list[0]
        for current_value in value_list:
            if  current_value > max_val:
                max_val = current_value
            if current_value < min_val:
                min_val = current_value
            val_range = max_val - min_val
        print("min:", min_val, " max:", max_val, " range:", val_range)
    else:
        min_val = float(ymin)
        max_val = float(ymax)
        val_range = max_val - min_val
    # determine the percentage ratio
    percent_n = 100 / val_range

    # background image
    pic_to_use = os.path.join(os.getcwd(), "graph_modules", pic_to_use)
    img = plt.imread(pic_to_use)
    dpi = 100
    fig, ax = plt.subplots(figsize=(img.shape[1] / dpi, img.shape[0] / dpi), constrained_layout=False)
    ax.axis('off')
    plt.rc('font', size=font_size)
    ax.imshow(img)

    # determine size of bar
    value = value_list[-1]
    date  = date_list[-1]
    key   = key_list[-1]
    value_percent = (value - min_val) * percent_n
    bar_unit_size = bar_height / 100
    bar_value_height = bar_unit_size * value_percent
    bar_value_height = bar_value_height - bar_value_height - bar_value_height # flipping it to a negative
    # draw the bar on the image
    ax.add_patch(patches.Rectangle((bar_bottom_x, bar_bottom_y), bar_width, bar_value_height, fill=True, color="red"))

    # Label the values on image
    bar_middle = bar_bottom_y-(bar_height/2)
    middle_value = round((val_range / 2) + min_val,2)
    bar_quarter = bar_bottom_y-(bar_height/4)
    quarter_value = round((val_range / 4) + min_val,2)
    bar_3rd_quarter = bar_bottom_y-((bar_height/4)*3)
    top_quarter_value = round(((val_range / 4)*3) + min_val,2)
    ax.annotate(str(round(min_val, 2)), (bar_bottom_x+bar_width+10, bar_bottom_y), va="center", ha="left")
    ax.annotate(str(quarter_value), (bar_bottom_x+bar_width+10, bar_quarter), va="center", ha="left")
    ax.annotate(str(middle_value), (bar_bottom_x+bar_width+10, bar_middle), va="center", ha="left")
    ax.annotate(str(top_quarter_value), (bar_bottom_x+bar_width+10, bar_3rd_quarter), va="center", ha="left")
    ax.annotate(str(round(max_val, 2)), (bar_bottom_x+bar_width+10, bar_bottom_y-bar_height), va="center", ha="left")
    text = str(round(value,2)) # + " " + str(date)
    ax.annotate(str(text), (bar_bottom_x-10, bar_bottom_y + bar_value_height), va="bottom", ha="right")
    # add the key
    key = key_list[0]
    key_x = img.shape[1] / 2
    key_y = img.shape[0] - 1
    ax.annotate(key, (key_x, key_y), va="top", ha="center")

    # remove axis labels which describe image not the data
    plt.xticks([])
    plt.yticks([])
    # save the graph and tidy up our workspace
    #fig.tight_layout()
    fig.set_constrained_layout_pads(w_pad=0, h_pad=0, hspace=0., wspace=0.)
    plt.savefig(graph_path, transparent=True)
    print("icon created and saved to " + graph_path)
    plt.close(fig)
