def read_graph_options():
    """
    Returns a dictionary of settings and their default values for use by the remote GUI.
    """
    return {
        "group_by": ["day", "week", "month"],
        # Additional bar styling options
        "title_text": "Min - Max Values",
        "show_time_period": "true",
        "show_grid": "false",
        "major_ticks": "",
        "minor_ticks": "1",
        "background_color": "",
        "axes_background_color": "",
        "title_fontsize": "22",
        "title_color": "black",
        "label_fontsize": "19",
        "label_color": "black",
        "legend_fontsize": "15",
        "legend_color": "black",
        "x_axis_color": "",
        "y_axis_color": "",
        "x_tick_color": "",
        "y_tick_color": "",
        "x_tick_fontsize": "14",
        "y_tick_fontsize": "14",
        "grid_color": "tab:gray",
        "grid_style": "--",
        "grid_alpha": "0.5",
        "x_tick_rotation": "0",
        "y_tick_format": "",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",
        "show_legend": "true",
        "bar_min_color": "blue",
        "bar_max_color": "red",
        "bar_width": "0.8",
        "bar_alpha": "0.75",
        "mpl_style": "",
        "use_only_mpl": "false",
        "keys": ""
    }

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    import matplotlib.dates as mdates
    import datetime

    if not extra:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra.get(key, default)

    # Extract main styling options
    title_text        = get_opt("title_text", "Min - Max Values")
    show_time_period  = get_opt("show_time_period","true").lower()=="true"
    show_grid         = get_opt("show_grid","false").lower()=="true"
    major_ticks       = get_opt("major_ticks","")
    minor_ticks       = get_opt("minor_ticks","1")

    mpl_style         = get_opt("mpl_style","")
    use_only_mpl      = get_opt("use_only_mpl","false").lower()=="true"
    background_color  = get_opt("background_color","")
    axes_background_color = get_opt("axes_background_color","")
    title_fontsize    = get_opt("title_fontsize","22")
    title_color       = get_opt("title_color","black")
    label_fontsize    = get_opt("label_fontsize","19")
    label_color       = get_opt("label_color","black")
    legend_fontsize   = get_opt("legend_fontsize","15")
    legend_color      = get_opt("legend_color","black")
    x_axis_color      = get_opt("x_axis_color","")
    y_axis_color      = get_opt("y_axis_color","")
    x_tick_color      = get_opt("x_tick_color","")
    y_tick_color      = get_opt("y_tick_color","")
    x_tick_fontsize   = get_opt("x_tick_fontsize","14")
    y_tick_fontsize   = get_opt("y_tick_fontsize","14")
    grid_color        = get_opt("grid_color","tab:gray")
    grid_style        = get_opt("grid_style","--")
    grid_alpha        = get_opt("grid_alpha","0.5")
    x_tick_rotation   = get_opt("x_tick_rotation","0")
    y_tick_format     = get_opt("y_tick_format","")
    legend_position   = get_opt("legend_position","best")
    legend_border     = get_opt("legend_border","true").lower()=="true"
    legend_alpha      = get_opt("legend_alpha","1.0")
    show_legend_opt   = get_opt("show_legend","true").lower()=="true"

    bar_min_color     = get_opt("bar_min_color","blue")
    bar_max_color     = get_opt("bar_max_color","red")
    bar_width         = float(get_opt("bar_width","0.8"))
    bar_alpha         = float(get_opt("bar_alpha","0.75"))

    # Key overwriting
    keys_override_str = get_opt("keys","")
    if keys_override_str.strip():
        custom_keys = [s.strip() for s in keys_override_str.split(",")]
    else:
        custom_keys = []

    # group_by logic: "day", "week", or "month"
    group_by_options = get_opt("group_by", ["day","week","month"])
    if isinstance(group_by_options, list):
        group_by = group_by_options[0]
    else:
        group_by = group_by_options.lower()

    if mpl_style and not use_only_mpl:
        plt.style.use(mpl_style)

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

    if background_color and not use_only_mpl:
        fig.patch.set_facecolor(background_color)
    if axes_background_color and not use_only_mpl:
        ax.set_facecolor(axes_background_color)

    def day_group_key(dt_val):
        return dt_val.strftime("%Y-%m-%d")

    def week_group_key(dt_val):
        y,w,_ = dt_val.isocalendar()
        return f"{y}-W{w}"

    def month_group_key(dt_val):
        return dt_val.strftime("%Y-%m")

    def make_dict_of_sets(date_list, value_list):
        """
        Create a dictionary grouping data by chosen group_by (day, week, month).
        Returns structure:
          { group_str: { 'values': [...], 'earliest': <datetime> } }
        """
        dictionary_of_sets = {}
        # choose group function
        if group_by=="day":
            group_func = day_group_key
        elif group_by=="week":
            group_func = week_group_key
        else:
            group_func = month_group_key

        for i, dt_val in enumerate(date_list):
            group_str = group_func(dt_val)
            if group_str not in dictionary_of_sets:
                dictionary_of_sets[group_str] = {
                    'values': [],
                    'earliest': dt_val
                }
            dictionary_of_sets[group_str]['values'].append(value_list[i])
            if dt_val < dictionary_of_sets[group_str]['earliest']:
                dictionary_of_sets[group_str]['earliest'] = dt_val
        return dictionary_of_sets

    def find_values_from_dict(dictionary_of_sets):
        """
        For each group, find the min and max values.
        Returns parallel lists: group_names, min_vals, max_vals, earliest_dates
        """
        group_names = []
        min_vals = []
        max_vals = []
        earliest_dates = []
        for g_str, data_dict in dictionary_of_sets.items():
            vals = data_dict['values']
            min_val = min(vals)
            max_val = max(vals)
            group_names.append(g_str)
            min_vals.append(min_val)
            max_vals.append(max_val)
            earliest_dates.append(data_dict['earliest'])
        return group_names, min_vals, max_vals, earliest_dates

    all_dates = []
    dataset_count = len(list_of_datasets)
    lines_count = 0  # Counting total bars (2 bars per dataset) for legend logic

    for i, ds in enumerate(list_of_datasets):
        date_list = ds[0]
        value_list = ds[1]
        key_list   = ds[2]

        if not date_list:
            continue

        # Overwrite dataset key if user specified
        if i < len(custom_keys):
            ds_label = custom_keys[i]
        else:
            ds_label = key_list[0] if key_list else ""

        dictionary_of_sets = make_dict_of_sets(date_list, value_list)
        group_names, day_min_vals, day_max_vals, earliest_dates = find_values_from_dict(dictionary_of_sets)

        all_dates.extend(earliest_dates)

        # Setup x positions and offsets if multiple datasets
        x_positions = list(range(len(group_names)))
        offset = (i - (dataset_count-1)/2)*bar_width*0.5 if dataset_count>1 else 0.0
        x_shifted = [x + offset for x in x_positions]

        # Legend labels. If multiple datasets, we label them "Min ds_label" / "Max ds_label"
        # If single dataset, label them "Min" / "Max {ds_label}" depending on ds_label presence
        if dataset_count>1:
            label_min = f"Min {ds_label}".strip() if ds_label else "Min"
            label_max = f"Max {ds_label}".strip() if ds_label else "Max"
        else:
            if ds_label.strip():
                label_min = f"Min {ds_label}"
                label_max = f"Max {ds_label}"
            else:
                label_min = "Min"
                label_max = "Max"

        # Draw the max bar first, then min bar on top => min bar is layered over max
        ax.bar(x_shifted, day_max_vals,
               width=bar_width/(1.2 if dataset_count>1 else 1.0),
               color=bar_max_color,
               alpha=bar_alpha,
               label=(label_max if (i==0 or dataset_count>1) else None),
               align="center")

        ax.bar(x_shifted, day_min_vals,
               width=bar_width/(1.2 if dataset_count>1 else 1.0),
               color=bar_min_color,
               alpha=bar_alpha,
               label=(label_min if (i==0 or dataset_count>1) else None),
               align="center")

        lines_count += 2  # We drew two bars per dataset

        # Set x ticks
        ax.set_xticks(range(len(group_names)))
        # x-axis tick labels
        if x_tick_rotation.isdigit():
            ax.set_xticklabels(group_names, rotation=int(x_tick_rotation))
        else:
            ax.set_xticklabels(group_names)

    # Decide if we show legend
    show_legend_final = (show_legend_opt and lines_count>2)

    # Ticks styling
    if major_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if minor_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)

    if show_grid and not use_only_mpl:
        ax.grid(color=grid_color if grid_color else "tab:gray",
                linestyle=grid_style if grid_style else "--",
                alpha=float(grid_alpha))

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

    # Build final title
    final_title = title_text
    if show_time_period and all_dates:
        earliest = min(all_dates)
        latest   = max(all_dates)
        date_fmt = "%b-%d %H:%M"
        final_title += f"\nTime Period; {earliest.strftime(date_fmt)} to {latest.strftime(date_fmt)}"

    ax.set_title(final_title, fontsize=int(title_fontsize), color=title_color)

    # If single dataset, label Y-axis with dataset name
    if len(list_of_datasets)==1 and list_of_datasets[0][2]:
        plt.ylabel(list_of_datasets[0][2][0], fontsize=int(label_fontsize), color=label_color)

    if ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    if show_legend_final:
        legend = ax.legend(loc=legend_position if legend_position else "best",
                           fontsize=int(legend_fontsize),
                           frameon=legend_border, framealpha=float(legend_alpha))
        if legend and legend_color:
            for text in legend.get_texts():
                text.set_color(legend_color)

    plt.tight_layout()
    plt.savefig(graph_path)
    print("High-Low graph created and saved to", graph_path)
    plt.close(fig)
