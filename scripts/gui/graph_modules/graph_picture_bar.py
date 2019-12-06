

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
             "use_val_set":"day average",    # day min, day max, day range, day average, last
             "title_extra":"",
             "pic_to_use":"flower.png",
             "middle_method":"repeat",       # stretch, repeat
             "top_cut_location":"175",
             "lower_cut_location":"335",
             "label_above":"true",
             "show_background":"true",
             "show_axis":"true",
             "rotate_label":"false"
             }
    return graph_module_settings_dict

def make_graph(data_sets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    print("Making a pretty picture graph...")
    #import the tools we'll be using
    import os
    import sys
    import datetime
    import matplotlib
    matplotlib.use('agg')
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.image import AxesImage
    from matplotlib.transforms import Bbox, TransformedBbox, BboxTransformTo

    # settings
    if extra == {}:
        extra = read_graph_options()
    use_val_set        = extra['use_val_set'].lower()
    title_extra        = extra['title_extra'].lower()
    pic_to_use         = extra['pic_to_use'].lower()
    middle_method      = extra['middle_method'].lower()
    top_cut_location   = int(extra['top_cut_location'])
    lower_cut_location = int(extra['lower_cut_location'])
    label_above        = extra['label_above'].lower()
    show_background    = extra['show_background'].lower()
    show_axis          = extra['show_axis'].lower()
    rotate_label       = extra['rotate_label'].lower()

    #middle_method = "stretch"
    #middle_method = "repeat"

    #
    # #
    # # # sort the data into the bits we need
    # #
    #
    # make a dictionary containing every day's list of dates and values'
    def make_dict_of_sets(date_list, value_list, key_list):
        dictionary_of_sets = {}
        for log_item_pos in range(0, len(date_list)):
            day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
            log_time = date_list[log_item_pos]
            if day_group in dictionary_of_sets:
                # If there's already an entry for this day
                # Read existing lists of dates and values
                values_to_graph = dictionary_of_sets[day_group][1]
                dates_to_graph = dictionary_of_sets[day_group][0]
                # add current value and date to lists
                values_to_graph.append(value_list[log_item_pos])
                dates_to_graph.append(log_time)
            else:
                # if there's no entry for this day yet
                # create new date and value lists if the day_group doesn't exists yet
                values_to_graph = [value_list[log_item_pos]]
                dates_to_graph = [log_time]
            # put the lists of values and dates into the dictionary of sets under the daygroup key
            dictionary_of_sets[day_group]=[dates_to_graph, values_to_graph]
        return dictionary_of_sets

    #
    # loop through each day's set finding min-max values and adding them to lists.
    def make_min_max_vals_lists(dictionary_of_days):
        day_names   = []
        day_min_val = []
        day_max_val = []
        day_range   = []
        day_averages= []
        counted     = []
        counter = 1
        for key, value in dictionary_of_days.items():
            days_date_list = value[0]
            days_value_list = value[1]
            #find min max values
            val_range=0
            min_val = days_value_list[0]
            max_val = days_value_list[0]
            total_of_vals = 0
            for x in range(1, len(days_value_list)):
                current_value = days_value_list[x]
                if  current_value > max_val:
                    max_val = current_value
                if current_value < min_val:
                    min_val = current_value
                total_of_vals = total_of_vals + current_value
            val_range = max_val - min_val
            day_average = total_of_vals / len(days_value_list)
            # add to lists
            counted.append(counter)
            counter += 1
            day_names.append(key)
            day_min_val.append(min_val)
            day_max_val.append(max_val)
            day_range.append(round(val_range, 2))
            day_averages.append(round(day_average, 2))
        if use_val_set == "day min":
            values = day_min_val
        if use_val_set == "day max":
            values = day_max_val
        if use_val_set == "day range":
            values = day_range
        if use_val_set == "day average":
            values = day_averages
        return counted, values, day_names
    #

    class PrettyBarImage(AxesImage):
        # This loads the image and stretches it neatly
        zorder = 1
        def __init__(self, ax, bbox, *, extent=(0, 1, 0, 1), **kwargs):
            super().__init__(ax, extent=extent, **kwargs)
            self._bbox = bbox
            self.set_transform(BboxTransformTo(bbox))

        def draw(self, renderer, *args, **kwargs):
            # load image
            pic_to_use_path = os.path.join(os.getcwd(), "graph_modules", pic_to_use)
            original_image = plt.imread(pic_to_use_path)
            #top_cut_location = original_image.shape[0] - 130 #600
            #lower_cut_location = original_image.shape[0] - 100 #600

            # determine amount it needs stretching by checking to see how deformed the bounding box is
            stretch_factor = round(self._bbox.height / self._bbox.width, 0)
            ny = int(stretch_factor * original_image.shape[1])
            #print(" --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---")
            #print("sizes -- original image; ", original_image.shape[0], original_image.shape[1], " bbox; ", self._bbox.height, self._bbox.width)
            #print("stretch factor; ", stretch_factor, "unrounded", self._bbox.height / self._bbox.width, " approximation of new height ", ny )

            #
            # try to find correct amount to repeat
            #
            # determine size of removed portion
            size_of_top_portion        = top_cut_location
            size_of_lower_portion      = original_image.shape[0] - lower_cut_location
            portion_of_image_removed   = size_of_top_portion + size_of_lower_portion
            portion_remains            = original_image.shape[0] - portion_of_image_removed
            #print("portion sizes; ", size_of_top_portion, size_of_lower_portion, " size of removed ", portion_of_image_removed, " size of remaining ", portion_remains, " added together ", portion_of_image_removed + portion_remains)
            new_h_approx = self._bbox.height * stretch_factor
            new_h_minus_removed = new_h_approx - portion_of_image_removed
            #print("new size of stretch secton", new_h_minus_removed, "old siize of stretch section", portion_remains)
            ratio_of_new_to_old = round(new_h_minus_removed / portion_remains, 0)
            #print("Ratio new h to old h", ratio_of_new_to_old)
            #
            ratio_of_image_to_removed = portion_remains / original_image.shape[0]
            #print( "ratio of image to removed ", ratio_of_image_to_removed)
            new_section_size = ratio_of_image_to_removed * ny
            #print("size of multiplied section ", new_section_size, "total vertical size of new area ", new_section_size + portion_remains)

            # find how much the middle section needs stretching or repeting
            new_y_minus_r_portions = ny - portion_of_image_removed
            ratio_of_change = new_y_minus_r_portions / portion_remains
            #print("ratio of change ", ratio_of_change, portion_remains, new_y_minus_r_portions)
            increase_size_of_removed_bit = portion_remains * stretch_factor
            #print(ny, " -------- ",  increase_size_of_removed_bit, increase_size_of_removed_bit + portion_of_image_removed)
            # stretch image if it needs it
            if self.get_array() is None or self.get_array().shape[0] != ny:
                # slice image into two pices
                top_part = original_image[:top_cut_location]
                middle_part = original_image[top_cut_location:lower_cut_location]
                lower_part = original_image[lower_cut_location:]
                # stretch the lower portion when that options selected
                if middle_method == "stretch":
                    if new_y_minus_r_portions > 0 and new_h_minus_removed > 0 and new_h_minus_removed > portion_remains:
                        edited_middle_part = np.repeat(middle_part, ratio_of_new_to_old, axis=0)
                    else:
                        edited_middle_part = middle_part
                if middle_method == "repeat":
                    edited_middle_part = middle_part.copy()
                    for x in range(1, int(ratio_of_new_to_old)):
                        edited_middle_part = np.append(edited_middle_part, middle_part, axis=0)
                # put it back together and display
                arr = np.vstack([top_part, edited_middle_part, lower_part])
                self.set_array(arr)
            super().draw(renderer, *args, **kwargs)

    # define graph space
    fig, ax = plt.subplots(figsize=(size_h, size_v))

    for x in data_sets:
        date_list = x[0]
        value_list = x[1]
        key_list = x[2]
        if use_val_set == "last":
            counted = [1]
            values = [value_list[-1]]
            day_names = [str(date_list[-1])]
        else:
            dict_of_sets = make_dict_of_sets(date_list, value_list, key_list)
            counted, values, day_names = make_min_max_vals_lists(dict_of_sets)

        # cycle through each value creating a correctly scaled image and placing it on the bar graph
        minh = values[0]
        maxh = values[0]
        for days_date, h, key in zip(counted, values, day_names):
            print(" -- Making bar for " + key)
            # get graph extents for y limit
            if h > maxh:
                maxh = h
            if h < minh:
                minh = h
            # find bounding box for image
            start_bar = days_date - 0.40
            end_bar = days_date + 0.40
            bbox0 = Bbox.from_extents(start_bar, 0., end_bar, h)
            bbox = TransformedBbox(bbox0, ax.transData)
            # add image to grpah
            ax.add_artist(PrettyBarImage(ax, bbox, interpolation="bicubic"))
            # write value above bar
            if label_above == "true":
                text = str(h) + "\n" + key
                ax.annotate(str(h), (days_date, h), va="bottom", ha="center")
            if rotate_label == "true":
                ax.text(days_date, 0, str(key), rotation=45,va='top',ha='right')
            else:
                ax.text(days_date, 0, str(key),va='top',ha='center')
            if show_axis == "false":
                ax.axis('off')
    plt.title(use_val_set + " " + title_extra + "\n")
    ax.set_xlim(counted[0] - 0.5, counted[-1] + 0.5)
    ax.set_ylim(0, maxh + 1)
    plt.xticks([])


    # add a pretty color to the background
    if show_background == "true":
        background_gradient = np.zeros((2, 2, 4))
        background_gradient[:, :, :3] = [1, 1, 0]
        background_gradient[:, :, 3] = [[0.1, 0.3], [0.3, 0.5]]  # alpha channel
        ax.imshow(background_gradient, interpolation="bicubic", zorder=0.1,
                  extent=(0, 1, 0, 1), transform=ax.transAxes, aspect="auto")


    # save the graph and tidy up our workspace
    plt.savefig(graph_path)
    print("pretty day bars created and saved to " + graph_path)
    plt.close(fig)
