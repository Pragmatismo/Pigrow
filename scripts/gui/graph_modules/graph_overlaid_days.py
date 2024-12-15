try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker
    import matplotlib.cm as cm
    import datetime
except ImportError:
    print("Matplotlib not installed, can't create graphs on this device.")

def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote GUI.
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
        "mpl_style": "",
        "keys": ""  # Option to overwrite dataset keys
    }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    # Load default settings if none supplied
    if not extra:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra.get(key, default)

    # Extract styling and logic options
    title_text        = get_opt("title_text", "")
    range_in_title    = get_opt("range_in_title", "true").lower() == "true"
    color_cycle       = get_opt("color_cycle", "")
    if isinstance(color_cycle, str) and ',' in color_cycle:
        color_cycle = [c.strip() for c in color_cycle.split(",") if c.strip()]
    line_style        = get_opt("line_style", "-")
    marker            = get_opt("marker", "o")
    show_legend       = get_opt("show_legend", "true").lower() == "true"
    show_grid         = get_opt("show_grid", "true").lower() == "true"
    major_ticks       = get_opt("major_ticks", "")
    minor_ticks       = get_opt("minor_ticks", "")
    mpl_style         = get_opt("mpl_style", "")
    background_color  = get_opt("background_color", "")
    axes_background_color = get_opt("axes_background_color", "")
    x_axis_color      = get_opt("x_axis_color", "")
    y_axis_color      = get_opt("y_axis_color", "")
    x_tick_color      = get_opt("x_tick_color", "")
    y_tick_color      = get_opt("y_tick_color", "")
    x_tick_fontsize   = get_opt("x_tick_fontsize","14")
    y_tick_fontsize   = get_opt("y_tick_fontsize","14")
    line_width        = get_opt("line_width","1.5")
    line_alpha        = get_opt("line_alpha","1.0")
    color_palette     = get_opt("color_palette","")
    grid_color        = get_opt("grid_color","tab:gray")
    grid_style        = get_opt("grid_style","--")
    grid_alpha        = get_opt("grid_alpha","0.5")
    x_tick_rotation   = get_opt("x_tick_rotation","0")
    y_tick_format     = get_opt("y_tick_format","")
    label_color       = get_opt("label_color","black")
    title_color       = get_opt("title_color","black")
    title_fontsize    = get_opt("title_fontsize","22")
    label_fontsize    = get_opt("label_fontsize","19")
    legend_fontsize   = get_opt("legend_fontsize","15")
    legend_color      = get_opt("legend_color","black")
    legend_position   = get_opt("legend_position","best")
    legend_border     = get_opt("legend_border","true").lower()=="true"
    legend_alpha      = get_opt("legend_alpha","1.0")

    group_by_options  = get_opt("group_by", ["days", "week", "dataset"])
    if isinstance(group_by_options, list):
        group_by = group_by_options[0]
    else:
        group_by = group_by_options.lower()

    color_cycle_fade  = get_opt("color_cycle_fade", "false").lower()=="true"
    color_fade_channels = get_opt("color_fade_channels", ["red","green","blue","red+green","red+blue","green+blue"])
    if isinstance(color_fade_channels,list):
        fade_channel = color_fade_channels[0]
    else:
        fade_channel = color_fade_channels.lower()

    # Overwrite keys logic
    keys_override_str = get_opt("keys","")
    if keys_override_str.strip():
        custom_keys = [s.strip() for s in keys_override_str.split(",")]
    else:
        custom_keys = []

    if mpl_style:
        plt.style.use(mpl_style)

    # Gather all dates to find global earliest and latest
    all_dates = []
    for ds in list_of_datasets:
        if ds[0]:
            all_dates.extend(ds[0])
    if not all_dates:
        print("No data to make a graph with.")
        return

    global_earliest = min(all_dates)
    global_latest   = max(all_dates)

    def group_key_func(date_val):
        """Return a group key (day or week) based on group_by."""
        if group_by=="days":
            return date_val.strftime("%Y:%m:%d")
        else:  # 'week'
            y,w,_ = date_val.isocalendar()
            return f"{y}:{w}"

    def build_ref_base(earliest_dt):
        """
        Construct a 'ref_base' that retains the hour, minute, second from earliest_dt,
        but fixes date to 1980-01-01.
        """
        return datetime.datetime(1980,1,1,
                                 earliest_dt.hour,
                                 earliest_dt.minute,
                                 earliest_dt.second,
                                 earliest_dt.microsecond)

    total_lines = []
    # If group_by=='dataset', find earliest date from the first dataset
    if group_by == "dataset" and list_of_datasets and list_of_datasets[0][0]:
        earliest_of_first = min(list_of_datasets[0][0])
        global_ref_base = build_ref_base(earliest_of_first)
    else:
        earliest_of_first = None
        global_ref_base   = None  # not used unless group_by=='dataset'

    for ds_i, ds in enumerate(list_of_datasets):
        date_list, value_list, key_list = ds
        if not date_list:
            continue

        # Possibly override the dataset key
        if ds_i < len(custom_keys):
            ds_label = custom_keys[ds_i]
        else:
            ds_label = key_list[0] if key_list else ""

        if group_by in ["days","week"]:
            dictionary_of_sets = {}
            for i, d_val in enumerate(date_list):
                v_val = value_list[i]
                g_key = group_key_func(d_val)
                if g_key not in dictionary_of_sets:
                    dictionary_of_sets[g_key] = {
                        'values': [],
                        'dates': [],
                        'earliest_real': d_val
                    }
                dictionary_of_sets[g_key]['values'].append(v_val)
                dictionary_of_sets[g_key]['dates'].append(d_val)
                if d_val < dictionary_of_sets[g_key]['earliest_real']:
                    dictionary_of_sets[g_key]['earliest_real'] = d_val

            for g_key, data_dict in dictionary_of_sets.items():
                vals = data_dict['values']
                dts  = data_dict['dates']
                earliest_in_group = min(dts)

                # Build the ref base preserving earliest_in_group's hour/min/sec
                ref_base = build_ref_base(earliest_in_group)
                shifted_dates = [ ref_base + (d - earliest_in_group) for d in dts ]

                original_earliest_dt = data_dict['earliest_real']
                total_lines.append((shifted_dates, vals, ds_label, original_earliest_dt))

        else:
            # group_by=='dataset'
            earliest_in_dataset = min(date_list)
            if ds_i==0:
                # Use global_ref_base from earliest_of_first
                if not global_ref_base:
                    global_ref_base = build_ref_base(earliest_in_dataset)
                shifted_dates = [ global_ref_base + (d - earliest_in_dataset) for d in date_list]
                original_earliest_dt = earliest_in_dataset
            else:
                # For subsequent datasets, shift relative to earliest_of_first
                # so they start at same hour:minute as the first dataset
                shifted_dates = [ global_ref_base + (d - earliest_of_first) for d in date_list]
                original_earliest_dt = min(date_list)

            total_lines.append((shifted_dates, value_list, ds_label, original_earliest_dt))

    lines_count = len(total_lines)
    show_legend_final = (show_legend and lines_count>1)

    # Possibly generate fade color cycle
    if color_cycle_fade and lines_count>0:
        def get_fade_color(i, n, mode):
            if n>1:
                intensity = i/(n-1)
            else:
                intensity = 1.0
            R,G,B = 1.0,1.0,1.0
            if mode=="red":
                G=1.0 - intensity
                B=1.0 - intensity
            elif mode=="green":
                R=1.0 - intensity
                B=1.0 - intensity
            elif mode=="blue":
                R=1.0 - intensity
                G=1.0 - intensity
            elif mode=="red+green":
                B=1.0 - intensity
            elif mode=="red+blue":
                G=1.0 - intensity
            elif mode=="green+blue":
                R=1.0 - intensity
            return (R,G,B)

        fade_mode = fade_channel
        generated_cycle = [get_fade_color(i, lines_count, fade_mode) for i in range(lines_count)]
    else:
        generated_cycle = None

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

    if background_color:
        fig.patch.set_facecolor(background_color)
    if axes_background_color:
        ax.set_facecolor(axes_background_color)

    if not color_cycle_fade and color_cycle and color_cycle!="false":
        ax.set_prop_cycle(color=color_cycle)
    elif not color_cycle_fade and color_palette and color_palette in plt.colormaps():
        cmap = cm.get_cmap(color_palette)
        pal_cycle = [cmap(i) for i in range(cmap.N // 10) if cmap.N>0]
        if pal_cycle:
            ax.set_prop_cycle(color=pal_cycle)

    # Plot lines
    for i, (dates, vals, ds_label, original_earliest) in enumerate(total_lines):
        date_str = original_earliest.strftime("%d-%b-%y") if original_earliest else "NoDate"

        if lines_count>1:
            legend_label = f"{ds_label} {date_str}".strip()
        else:
            legend_label = ds_label if ds_label.strip() else date_str

        final_label = legend_label if show_legend_final else None

        if generated_cycle:
            c = generated_cycle[i]
            ax.plot(dates, vals, line_style, marker=marker,
                    lw=float(line_width), alpha=float(line_alpha),
                    label=final_label, color=c)
        else:
            ax.plot(dates, vals, line_style, marker=marker,
                    lw=float(line_width), alpha=float(line_alpha),
                    label=final_label)

    # Legend
    if show_legend_final:
        legend = ax.legend(loc=legend_position if legend_position else "best",
                           fontsize=int(legend_fontsize),
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
        to_str   = global_latest.strftime(date_fmt)
        range_string = f"From {from_str} to {to_str}"

    if title_text.strip():
        final_title = title_text + ("\n"+range_string if range_string else "")
    else:
        final_title = range_string if range_in_title else ""

    if final_title:
        ax.set_title(final_title, fontsize=int(title_fontsize), color=title_color)

    # X-axis formatting
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    if list_of_datasets and list_of_datasets[0][2]:
        y_label = list_of_datasets[0][2][0]
        plt.ylabel(y_label, fontsize=int(label_fontsize), color=label_color)

    if ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close(fig)
    print("Enhanced overlay graph with preserved hour shift, real date legend, custom key overwriting saved to", graph_path)
