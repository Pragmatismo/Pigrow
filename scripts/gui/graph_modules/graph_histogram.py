try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    import matplotlib.cm as cm
except:
    print("Matplotlib not installed, can't create graphs on this device")

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui.
    '''
    graph_module_settings_dict = {
        # Histogram-specific settings
        "num_of_bins":"20",
        "show_raw":"false",
        "show_hourly_ave":"true",
        "show_daily_ave":"true",
        "show_weekly_ave":"false",

        # Basic graph options
        "alpha_val":"0.75",
        "title_text": "Histogram",
        "range_in_title": "true",

        # Extended options
        "title_fontsize": "22",
        "title_color": "black",

        "show_grid": "true",
        "major_ticks": "",
        "minor_ticks": "",

        "color_cycle": "",
        "label_fontsize": "19",
        "label_color": "black",
        "legend_fontsize": "15",
        "legend_color": "black",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",

        "x_axis_color": "",
        "y_axis_color": "",
        "x_tick_color": "",
        "y_tick_color": "",
        "x_tick_fontsize": "14",
        "y_tick_fontsize": "14",

        "color_palette": "",
        "background_color": "",
        "axes_background_color": "",

        "x_tick_rotation": "0",
        "y_tick_format": "",
        "mpl_style": "",
        "use_only_mpl": "false"
    }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    # If extra is empty, load defaults
    if extra == {}:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra[key] if key in extra else default

    mpl_style = get_opt("mpl_style", "")
    use_only_mpl = (get_opt("use_only_mpl", "false").lower() == "true")

    # Histogram specific
    num_of_bins = int(get_opt('num_of_bins', "20"))
    show_raw = get_opt('show_raw', "false").lower()
    show_hourly_ave = get_opt('show_hourly_ave', "true").lower()
    show_daily_ave = get_opt('show_daily_ave', "true").lower()
    show_weekly_ave = get_opt('show_weekly_ave', "false").lower()

    # Common options
    show_grid = get_opt("show_grid", "true").lower() == "true"
    color_cycle = get_opt("color_cycle", "").lower()
    if ',' in color_cycle:
        color_cycle = [c.strip() for c in color_cycle.split(",") if c.strip()]
    alpha_val = float(get_opt("alpha_val", "0.75"))

    # Extended style options
    title_text = get_opt("title_text", "")
    title_color = get_opt("title_color", "black")
    label_color = get_opt("label_color", "black")
    legend_color = get_opt("legend_color", "black")
    x_axis_color = get_opt("x_axis_color", "")
    y_axis_color = get_opt("y_axis_color", "")
    x_tick_color = get_opt("x_tick_color", "")
    y_tick_color = get_opt("y_tick_color", "")
    x_tick_fontsize = get_opt("x_tick_fontsize", "14")
    y_tick_fontsize = get_opt("y_tick_fontsize", "14")
    color_palette = get_opt("color_palette", "")
    background_color = get_opt("background_color", "")
    axes_background_color = get_opt("axes_background_color", "")
    legend_position = get_opt("legend_position", "best")
    legend_border = get_opt("legend_border", "true").lower() == "true"
    legend_alpha = get_opt("legend_alpha", "1.0")
    x_tick_rotation = get_opt("x_tick_rotation", "0")
    y_tick_format = get_opt("y_tick_format", "")
    title_fontsize = get_opt("title_fontsize", "22")
    label_fontsize = get_opt("label_fontsize", "19")
    legend_fontsize = get_opt("legend_fontsize", "15")
    major_ticks = get_opt("major_ticks", "")
    minor_ticks = get_opt("minor_ticks", "")
    range_in_title = get_opt("range_in_title", "true").lower() == "true"
    grid_color = get_opt("grid_color", "tab:gray")
    grid_style = get_opt("grid_style", "--")
    grid_alpha = get_opt("grid_alpha", "0.5")

    if mpl_style and not use_only_mpl:
        plt.style.use(mpl_style)

    def make_hour_averages(date_list, value_list):
        dictionary_of_sets = {}
        for log_item_pos in range(len(date_list)):
            hour_group = date_list[log_item_pos].strftime("%Y:%m:%d:%H")
            dictionary_of_sets.setdefault(hour_group, []).append(value_list[log_item_pos])
        hourly_ave_values = [sum(vals)/len(vals) for vals in dictionary_of_sets.values()]
        return hourly_ave_values

    def make_day_averages(date_list, value_list):
        dictionary_of_sets = {}
        for log_item_pos in range(len(date_list)):
            day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
            dictionary_of_sets.setdefault(day_group, []).append(value_list[log_item_pos])
        daily_ave_values = [sum(vals)/len(vals) for vals in dictionary_of_sets.values()]
        return daily_ave_values

    def make_week_averages(date_list, value_list):
        dictionary_of_sets = {}
        # group by isocalendar (year, week)
        for log_item_pos in range(len(date_list)):
            year, week_num, day_of_week = date_list[log_item_pos].isocalendar()
            week_group = f"{year}:{week_num}"
            dictionary_of_sets.setdefault(week_group, []).append(value_list[log_item_pos])
        weekly_ave_values = [sum(vals)/len(vals) for vals in dictionary_of_sets.values()]
        return weekly_ave_values

    # Count total lines for labeling logic
    # We'll plot for each dataset: raw?, hourly?, daily?, weekly?
    lines_count = 0
    for dataset in list_of_datasets:
        # count how many hist lines we would create
        if show_raw == "true":
            lines_count += 1
        if show_hourly_ave == "true" and not use_only_mpl:
            lines_count += 1
        if show_daily_ave == "true" and not use_only_mpl:
            lines_count += 1
        if show_weekly_ave == "true" and not use_only_mpl:
            lines_count += 1

    # If only one line total, no labels are needed
    use_labels = (lines_count > 1)

    # Determine global earliest and latest date for range_in_title
    global_earliest = None
    global_latest = None
    for dataset in list_of_datasets:
        if dataset[0]:  # dataset[0] is date_list
            dlist = dataset[0]
            if dlist:
                earliest = dlist[0]
                latest = dlist[-1]
                if global_earliest is None or earliest < global_earliest:
                    global_earliest = earliest
                if global_latest is None or latest > global_latest:
                    global_latest = latest

    # Format the range if needed
    range_string = ""
    if range_in_title and global_earliest and global_latest:
        # Format: "From {H:MM d MMM 'YY} to {H:MM d MMM 'YY}"
        date_fmt = "%H:%M %d %b '%y"
        from_str = global_earliest.strftime(date_fmt)
        to_str = global_latest.strftime(date_fmt)
        range_string = f"From {from_str} to {to_str}"

    # If title_text is not empty and range_in_title is true, append range on new line
    # If title_text is empty and range_in_title is true, just set title to range_string
    final_title = title_text
    if range_in_title:
        if final_title.strip():
            final_title = final_title + "\n" + range_string
        else:
            final_title = range_string

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

    if background_color and not use_only_mpl:
        fig.patch.set_facecolor(background_color)
    if axes_background_color and not use_only_mpl:
        ax.set_facecolor(axes_background_color)

    if not use_only_mpl and color_cycle and color_cycle != "false":
        ax.set_prop_cycle(color=color_cycle)

    if not use_only_mpl and color_palette:
        if color_palette in plt.colormaps():
            cmap = cm.get_cmap(color_palette)
            generated_cycle = [cmap(i) for i in range(cmap.N // 10) if cmap.N > 0]
            if generated_cycle:
                ax.set_prop_cycle(color=generated_cycle)

    # Plot histograms for each dataset
    for dataset in list_of_datasets:
        date_list, value_list, key_list = dataset
        dataset_label = key_list[0] if key_list else ""

        # If only one line total and no labels needed, set label = "" else full label
        def maybe_label(base_label):
            return base_label if use_labels else None

        # Show hourly averages
        if show_hourly_ave == "true" and not use_only_mpl:
            hourly_ave_values = make_hour_averages(date_list, value_list)
            plt.hist(hourly_ave_values, num_of_bins, density=True, alpha=alpha_val,
                     label=maybe_label("Hourly Avg - " + dataset_label))

        # Show daily averages
        if show_daily_ave == "true" and not use_only_mpl:
            daily_ave_values = make_day_averages(date_list, value_list)
            plt.hist(daily_ave_values, num_of_bins, density=True, alpha=alpha_val,
                     label=maybe_label("Daily Avg - " + dataset_label))

        # Show weekly averages
        if show_weekly_ave == "true" and not use_only_mpl:
            weekly_ave_values = make_week_averages(date_list, value_list)
            plt.hist(weekly_ave_values, num_of_bins, density=True, alpha=alpha_val,
                     label=maybe_label("Weekly Avg - " + dataset_label))

        # Raw values
        if show_raw == "true":
            plt.hist(value_list, num_of_bins, density=True, alpha=alpha_val,
                     label=maybe_label("Raw - " + dataset_label))

    # Set title if not empty or if range_in_title is used
    if final_title and not use_only_mpl:
        plt.title(final_title, fontsize=int(title_fontsize), color=title_color if title_color else "black")

    # Set axis labels
    if label_fontsize and not use_only_mpl:
        # For histogram, x-axis is typically the measured variable
        # If there's at least one dataset, we can use its key as the label
        x_label = list_of_datasets[0][2][0] if list_of_datasets and list_of_datasets[0][2] else ""
        plt.xlabel(x_label, fontsize=int(label_fontsize), color=label_color if label_color else "black")
        plt.ylabel("Density", fontsize=int(label_fontsize), color=label_color if label_color else "black")

    # Show grid if requested
    if show_grid and not use_only_mpl:
        ax.grid(color=grid_color if grid_color else "tab:gray",
                linestyle=grid_style if grid_style else "--",
                alpha=float(grid_alpha) if grid_alpha else 0.5)

    # Set tick params
    if not use_only_mpl:
        if x_tick_color:
            ax.tick_params(axis='x', colors=x_tick_color)
        if x_tick_fontsize:
            ax.tick_params(axis='x', labelsize=int(x_tick_fontsize))
        if y_tick_color:
            ax.tick_params(axis='y', colors=y_tick_color)
        if y_tick_fontsize:
            ax.tick_params(axis='y', labelsize=int(y_tick_fontsize))

        if x_axis_color:
            ax.xaxis.label.set_color(x_axis_color)
        if y_axis_color:
            ax.yaxis.label.set_color(y_axis_color)

        # x_tick_rotation
        if x_tick_rotation and x_tick_rotation.isdigit():
            for tick in ax.get_xticklabels():
                tick.set_rotation(int(x_tick_rotation))

        # Format y-axis ticks if specified
        if y_tick_format:
            ax.yaxis.set_major_formatter(plticker.FormatStrFormatter(y_tick_format))

    # Set major/minor ticks if specified
    if major_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if minor_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)

    # If we used labels (more than one line)
    if use_labels and not use_only_mpl:
        legend = ax.legend(loc=legend_position if legend_position else "best",
                           fontsize=int(legend_fontsize) if legend_fontsize else 15,
                           frameon=legend_border, framealpha=float(legend_alpha) if legend_alpha else 1.0)
        if legend and legend_color:
            for text in legend.get_texts():
                text.set_color(legend_color)

    # Set y-axis and x-axis limits if provided
    if ymax and ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin and ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()
    print("Histogram graph created and saved to " + graph_path)
