def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui.
    '''
    graph_module_settings_dict = {
        "group_by": ["days", "week", "dataset"],
        "color_cycle_fade": "false",
        "color_fade_channels": ["red", "green", "blue", "red+green", "red+blue", "green+blue"],
        "title_text": "",
        "range_in_title": "true",
        "color_cycle": "",
        "line_style": "-",
        "marker": "o",
        "show_legend": "true",
        "show_grid": "true",
        "major_ticks": "",
        "minor_ticks": "",
        "background_color": "",
        "axes_background_color": "",
        "x_axis_color": "",
        "y_axis_color": "",
        "x_tick_color": "",
        "y_tick_color": "",
        "x_tick_fontsize": "14",
        "y_tick_fontsize": "14",
        "line_width": "1.5",
        "line_alpha": "1.0",
        "color_palette": "",
        "grid_color": "tab:gray",
        "grid_style": "--",
        "grid_alpha": "0.5",
        "x_tick_rotation": "0",
        "y_tick_format": "",
        "label_color": "black",
        "title_color": "black",
        "title_fontsize": "22",
        "label_fontsize": "19",
        "legend_fontsize": "15",
        "legend_color": "black",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",
        "mpl_style": ""
        }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker
    import matplotlib.cm as cm
    import datetime

    if extra == {}:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra.get(key, default)

    # Extract settings
    title_text = get_opt("title_text", "")
    range_in_title = get_opt("range_in_title", "true").lower() == "true"
    color_cycle = get_opt("color_cycle", "")
    if isinstance(color_cycle, str) and ',' in color_cycle:
        color_cycle = [c.strip() for c in color_cycle.split(",") if c.strip()]
    line_style = get_opt("line_style", "-")
    marker = get_opt("marker", "o")
    line_flags = marker + line_style
    show_legend = get_opt("show_legend", "true").lower() == "true"
    show_grid = get_opt("show_grid", "true").lower() == "true"
    major_ticks = get_opt("major_ticks", "")
    minor_ticks = get_opt("minor_ticks", "")
    mpl_style = get_opt("mpl_style", "")
    background_color = get_opt("background_color", "")
    axes_background_color = get_opt("axes_background_color", "")
    x_axis_color = get_opt("x_axis_color", "")
    y_axis_color = get_opt("y_axis_color", "")
    x_tick_color = get_opt("x_tick_color", "")
    y_tick_color = get_opt("y_tick_color", "")
    x_tick_fontsize = get_opt("x_tick_fontsize", "14")
    y_tick_fontsize = get_opt("y_tick_fontsize", "14")
    line_width = get_opt("line_width", "1.5")
    line_alpha = get_opt("line_alpha", "1.0")
    color_palette = get_opt("color_palette", "")
    grid_color = get_opt("grid_color", "tab:gray")
    grid_style = get_opt("grid_style", "--")
    grid_alpha = get_opt("grid_alpha", "0.5")
    x_tick_rotation = get_opt("x_tick_rotation", "0")
    y_tick_format = get_opt("y_tick_format", "")
    label_color = get_opt("label_color", "black")
    title_color = get_opt("title_color", "black")
    title_fontsize = get_opt("title_fontsize", "22")
    label_fontsize = get_opt("label_fontsize", "19")
    legend_fontsize = get_opt("legend_fontsize", "15")
    legend_color = get_opt("legend_color", "black")
    legend_position = get_opt("legend_position", "best")
    legend_border = get_opt("legend_border", "true").lower() == "true"
    legend_alpha = get_opt("legend_alpha", "1.0")
    group_by_options = get_opt("group_by", ["days", "week", "dataset"])
    if isinstance(group_by_options, list):
        group_by = group_by_options[0]
    else:
        group_by = group_by_options.lower()

    color_cycle_fade = get_opt("color_cycle_fade", "false").lower() == "true"
    color_fade_channels = get_opt("color_fade_channels", ["red", "green", "blue", "red+green", "red+blue", "green+blue"])
    if isinstance(color_fade_channels, list):
        fade_channel = color_fade_channels[0]  # default to first if list
    else:
        fade_channel = color_fade_channels.lower()

    if mpl_style:
        plt.style.use(mpl_style)

    all_dates = []
    for ds in list_of_datasets:
        if ds[0]:
            all_dates.extend(ds[0])
    if not all_dates:
        print("No data to make a graph with...")
        return None
    global_earliest = min(all_dates)
    global_latest = max(all_dates)

    def group_by_day_or_week(date_val):
        if group_by == "days":
            return date_val.strftime("%Y:%m:%d")
        else:  # week
            y, w, d = date_val.isocalendar()
            return f"{y}:{w}"

    def shift_dates_for_dataset_mode(dates, earliest_of_first):
        # Shift all dates so earliest date matches earliest_of_first
        my_earliest = min(dates)
        delta = my_earliest - earliest_of_first
        shifted_dates = [d - delta for d in dates]
        return shifted_dates

    total_lines = []

    if group_by == "dataset" and len(list_of_datasets) > 0 and list_of_datasets[0][0]:
        earliest_of_first = min(list_of_datasets[0][0])
    else:
        earliest_of_first = None

    # Build lines
    for ds_i, ds in enumerate(list_of_datasets):
        date_list, value_list, key_list = ds
        if not date_list:
            continue

        if group_by in ["days", "week"]:
            dictionary_of_sets = {}
            for i in range(len(date_list)):
                d_val = date_list[i]
                v_val = value_list[i]
                group_key = group_by_day_or_week(d_val)
                dictionary_of_sets.setdefault(group_key, [[], []])
                dictionary_of_sets[group_key][0].append(v_val)
                dictionary_of_sets[group_key][1].append(d_val)

            ref_base = datetime.datetime(1980,1,1,0,0,0)
            for group_key, (vals, dts) in dictionary_of_sets.items():
                earliest_in_group = min(dts)
                shifted_dates = []
                for dd in dts:
                    delta = dd - earliest_in_group
                    shifted_dates.append(ref_base + delta)
                dataset_label = key_list[0] if key_list else ""
                total_lines.append((shifted_dates, vals, dataset_label))
        else:
            # group_by == "dataset"
            if ds_i == 0:
                shifted_dates = date_list
            else:
                shifted_dates = shift_dates_for_dataset_mode(date_list, earliest_of_first)
            dataset_label = key_list[0] if key_list else ""
            total_lines.append((shifted_dates, value_list, dataset_label))

    lines_count = len(total_lines)
    # Legend logic
    # If show_legend is true and lines_count > 1, show legend
    # If lines_count == 1 or show_legend is false, no legend
    show_legend_final = (show_legend and lines_count > 1)

    # If color_cycle_fade is true, generate a fade color cycle
    if color_cycle_fade and lines_count > 0:
        # Generate fade colors
        def get_fade_color(i, n, mode):
            # i from 0 to n-1, intensity = i/(n-1) if n>1 else 0
            if n > 1:
                intensity = i / (n - 1)
            else:
                intensity = 1.0

            # Each mode: start=white(1,1,1), end=some color combination
            R,G,B = 1.0,1.0,1.0
            # For single channels and combos we decided on logic:
            # red: final = (1,0,0)
            # green: final = (0,1,0)
            # blue: final = (0,0,1)
            # red+green: final = (1,1,0)
            # red+blue: final = (1,0,1)
            # green+blue: final=(0,1,1)
            if mode == "red":
                # from white to red: decrease G,B from 1 to 0
                G = 1.0 - intensity
                B = 1.0 - intensity
                # R stays 1.0
            elif mode == "green":
                # from white to green: decrease R,B
                R = 1.0 - intensity
                B = 1.0 - intensity
                # G stays 1.0
            elif mode == "blue":
                # from white to blue: decrease R,G
                R = 1.0 - intensity
                G = 1.0 - intensity
                # B stays 1.0
            elif mode == "red+green":
                # from white to yellow: final=(1,1,0)
                # only decrease B from 1.0 to 0.0
                B = 1.0 - intensity
                # R=1,G=1 fixed
            elif mode == "red+blue":
                # from white to magenta (1,0,1)
                # decrease G only
                G = 1.0 - intensity
            elif mode == "green+blue":
                # from white to cyan (0,1,1)
                # decrease R only
                R = 1.0 - intensity
            return (R,G,B)

        fade_mode = fade_channel
        generated_cycle = [get_fade_color(i, lines_count, fade_mode) for i in range(lines_count)]
        # We'll apply these colors line by line
    else:
        generated_cycle = None

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

    if background_color:
        fig.patch.set_facecolor(background_color)
    if axes_background_color:
        ax.set_facecolor(axes_background_color)

    if not color_cycle_fade and color_cycle and color_cycle != "false":
        ax.set_prop_cycle(color=color_cycle)

    if not color_cycle_fade and color_palette and color_palette in plt.colormaps():
        cmap = cm.get_cmap(color_palette)
        pal_cycle = [cmap(i) for i in range(cmap.N // 10) if cmap.N > 0]
        if pal_cycle:
            ax.set_prop_cycle(color=pal_cycle)

    # Plot lines with optional fade colors
    for i, (dates, vals, lbl) in enumerate(total_lines):
        chosen_label = lbl if lines_count > 1 and show_legend_final and lbl else None
        if generated_cycle:  # color_cycle_fade is True
            c = generated_cycle[i]
            ax.plot(dates, vals, line_style, marker=marker,
                    lw=float(line_width), alpha=float(line_alpha),
                    label=chosen_label, color=c)
        else:
            ax.plot(dates, vals, line_style, marker=marker,
                    lw=float(line_width), alpha=float(line_alpha),
                    label=chosen_label)

    # Legend
    if show_legend_final:
        legend = ax.legend(loc=legend_position if legend_position else "best",
                           fontsize=int(legend_fontsize) if legend_fontsize else 15,
                           frameon=legend_border, framealpha=float(legend_alpha))
        if legend and legend_color:
            for text in legend.get_texts():
                text.set_color(legend_color)

    # Grid, ticks, formatting
    if major_ticks:
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if minor_ticks:
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)

    if show_grid:
        ax.grid(color=grid_color if grid_color else "tab:gray",
                linestyle=grid_style if grid_style else "--",
                alpha=float(grid_alpha) if grid_alpha else 0.5)

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

    if x_tick_rotation.isdigit():
        for tick in ax.get_xticklabels():
            tick.set_rotation(int(x_tick_rotation))

    if y_tick_format:
        ax.yaxis.set_major_formatter(plticker.FormatStrFormatter(y_tick_format))

    # Construct title with range if needed
    range_string = ""
    if range_in_title and global_earliest and global_latest:
        date_fmt = "%H:%M %d %b '%y"
        from_str = global_earliest.strftime(date_fmt)
        to_str = global_latest.strftime(date_fmt)
        range_string = f"From {from_str} to {to_str}"

    if title_text.strip():
        if range_string:
            final_title = title_text + "\n" + range_string
        else:
            final_title = title_text
    else:
        final_title = range_string if range_in_title else ""

    if final_title:
        ax.set_title(final_title, fontsize=int(title_fontsize), color=title_color)

    # X-axis formatting for time
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    # Y-label from first dataset if available
    y_label = list_of_datasets[0][2][0] if list_of_datasets and list_of_datasets[0][2] else ""
    if label_fontsize:
        plt.ylabel(y_label, fontsize=int(label_fontsize), color=label_color)

    if ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close()
    print("Overlaid day/week/dataset graph with fade and legend options created and saved to " + graph_path)
