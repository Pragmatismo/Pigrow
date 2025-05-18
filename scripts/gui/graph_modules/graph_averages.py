try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import matplotlib.ticker as plticker
    import matplotlib.cm as cm
    import datetime
    import math
except ImportError:
    print("Matplotlib not installed, can't create graphs on this device")


def read_graph_options():
    """
    Returns a dictionary of settings and their default values for use by the remote GUI.
    """
    return {
        "title_text": "",
        "range_in_title": "true",
        "show_raw": "false",
        "show_hourly": "true",
        "show_daily": "true",
        "show_weekly": "false",
        "show_monthly": "false",
        "show_average": "false",
        "show_median": "false",
        "show_stddev": "false",
        "show_rolling": "true",
        # Rolling average options
        "rolling_unit": ["hour", "day", "week", "month", "points"],
        "points_window": "50",    # used if rolling_unit='points'
        "rolling_window": "1",   # used if rolling_unit is time-based

        # Styling options
        "show_legend": "true",
        "color_cycle": "",
        "line_style": "-",
        "marker": "o",
        "major_ticks": "",
        "minor_ticks": "",
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
        "line_width": "1.5",
        "line_alpha": "1.0",
        "color_palette": "",
        "show_grid": "true",
        "grid_color": "tab:gray",
        "grid_style": "--",
        "grid_alpha": "0.5",
        "background_color": "",
        "axes_background_color": "",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",
        "x_tick_rotation": "0",
        "y_tick_format": "",
        "mpl_style": "",
        "use_only_mpl": "false",
    }


def make_graph(data_sets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    if not extra:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra.get(key, default)

    # Extract main options
    title_text = get_opt("title_text", "")
    range_in_title = get_opt("range_in_title", "true").lower() == "true"
    show_raw = get_opt("show_raw", "true").lower()
    show_rolling = get_opt("show_rolling", "true").lower()
    show_daily = get_opt("show_daily", "true").lower()
    show_average = get_opt("show_average", "true").lower()
    show_hourly = get_opt("show_hourly", "false").lower()
    show_weekly = get_opt("show_weekly", "false").lower()
    show_monthly = get_opt("show_monthly", "false").lower()
    show_median = get_opt("show_median", "false").lower()
    show_stddev = get_opt("show_stddev", "false").lower()
    show_legend_opt = get_opt("show_legend", "true").lower() == "true"

    rolling_unit_opt = get_opt("rolling_unit", ["points","hour","day","week","month"])
    rolling_unit = rolling_unit_opt[0] if isinstance(rolling_unit_opt, list) else rolling_unit_opt.lower()
    points_window = int(get_opt("points_window", "50"))
    rolling_window = int(get_opt("rolling_window", "24"))

    # Styling options
    mpl_style = get_opt("mpl_style", "")
    use_only_mpl = get_opt("use_only_mpl","false").lower()=="true"
    color_cycle = get_opt("color_cycle", "")
    if isinstance(color_cycle, str) and ',' in color_cycle:
        color_cycle = [c.strip() for c in color_cycle.split(",") if c.strip()]
    line_style = get_opt("line_style","-")
    marker = get_opt("marker","o")
    major_ticks = get_opt("major_ticks","")
    minor_ticks = get_opt("minor_ticks","")
    title_fontsize = get_opt("title_fontsize","22")
    title_color = get_opt("title_color","black")
    label_fontsize = get_opt("label_fontsize","19")
    label_color = get_opt("label_color","black")
    legend_fontsize = get_opt("legend_fontsize","15")
    legend_color = get_opt("legend_color","black")
    x_axis_color = get_opt("x_axis_color","")
    y_axis_color = get_opt("y_axis_color","")
    x_tick_color = get_opt("x_tick_color","")
    y_tick_color = get_opt("y_tick_color","")
    x_tick_fontsize = get_opt("x_tick_fontsize","14")
    y_tick_fontsize = get_opt("y_tick_fontsize","14")
    line_width = get_opt("line_width","1.5")
    line_alpha = get_opt("line_alpha","1.0")
    color_palette = get_opt("color_palette","")
    show_grid = get_opt("show_grid","true").lower()=="true"
    grid_color = get_opt("grid_color","tab:gray")
    grid_style = get_opt("grid_style","--")
    grid_alpha = get_opt("grid_alpha","0.5")
    background_color = get_opt("background_color","")
    axes_background_color = get_opt("axes_background_color","")
    legend_position = get_opt("legend_position","best")
    legend_border = get_opt("legend_border","true").lower()=="true"
    legend_alpha = get_opt("legend_alpha","1.0")
    x_tick_rotation = get_opt("x_tick_rotation","0")
    y_tick_format = get_opt("y_tick_format","")

    if mpl_style and not use_only_mpl:
        plt.style.use(mpl_style)

    # Helper functions
    def group_and_average(date_list, value_list, freq):
        dictionary = {}
        for i, d in enumerate(date_list):
            if freq=="hour":
                key = d.strftime("%Y-%m-%d:%H")
            elif freq=="day":
                key = d.strftime("%Y-%m-%d")
            elif freq=="week":
                y,w,_ = d.isocalendar()
                key = f"{y}-W{w}"
            elif freq=="month":
                key = d.strftime("%Y-%m")
            else:
                key = d.strftime("%Y-%m-%d")
            dictionary.setdefault(key,[]).append((d,value_list[i]))
        if not dictionary:
            return [],[]
        intervals = []
        for _, pairs in dictionary.items():
            dates = [p[0] for p in pairs]
            vals = [p[1] for p in pairs]
            avg = sum(vals)/len(vals)
            start_d = min(dates)
            end_d = max(dates)
            intervals.append((start_d, end_d, avg))
        intervals.sort(key=lambda x:x[0])
        final_dates = []
        final_vals = []
        for (sd,ed,av) in intervals:
            final_dates.append(sd)
            final_vals.append(av)
            final_dates.append(ed)
            final_vals.append(av)
        return final_dates, final_vals

    def rolling_average_by_points(date_list, value_list, window_size):
        result_dates = []
        result_vals = []
        for i in range(window_size-1, len(date_list)):
            subset = value_list[i-window_size+1:i+1]
            avg_val = sum(subset)/len(subset)
            result_dates.append(date_list[i])
            result_vals.append(avg_val)
        return result_dates, result_vals

    def rolling_average_by_time(date_list, value_list, unit, window):
        if unit=="hour":
            delta = datetime.timedelta(hours=window)
        elif unit=="day":
            delta = datetime.timedelta(days=window)
        elif unit=="week":
            delta = datetime.timedelta(weeks=window)
        elif unit=="month":
            delta = datetime.timedelta(days=30*window)
        else:
            delta = datetime.timedelta(days=window)

        result_dates = []
        result_vals = []
        start_idx = 0
        for i, current_time in enumerate(date_list):
            while start_idx < i and date_list[start_idx] < current_time - delta:
                start_idx += 1
            subset = value_list[start_idx:i+1]
            if len(subset)<2:
                continue
            avg_val = sum(subset)/len(subset)
            result_dates.append(current_time)
            result_vals.append(avg_val)
        return result_dates, result_vals

    # Gather all dates to determine global earliest and latest
    all_dates = [d for ds in data_sets for d in ds[0] if ds[0]]
    if not all_dates:
        print("No data to graph.")
        return
    global_earliest = min(all_dates)
    global_latest = max(all_dates)

    # Count lines before plotting
    lines_count = 0
    for ds in data_sets:
        date_list, value_list, _ = ds
        if not date_list:
            continue
        # raw
        if show_raw=="true":
            lines_count += 1
        # rolling
        if show_rolling=="true":
            if rolling_unit=="points":
                if len(value_list)>=points_window:
                    lines_count += 1
            else:
                lines_count += 1
        # daily
        if show_daily=="true":
            lines_count += 1
        # hourly
        if show_hourly=="true":
            lines_count += 1
        # weekly
        if show_weekly=="true":
            lines_count += 1
        # monthly
        if show_monthly=="true":
            lines_count += 1
        # average
        if show_average=="true":
            lines_count += 1
        # median
        if show_median=="true":
            lines_count += 1
        # stddev
        if show_stddev=="true":
            lines_count += 1
            if show_average!="true":
                lines_count += 1

    use_labels = (lines_count > 1)
    show_legend_final = (use_labels and show_legend_opt and not use_only_mpl)

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

    if not use_only_mpl and mpl_style:
        plt.style.use(mpl_style)

    if background_color and not use_only_mpl:
        fig.patch.set_facecolor(background_color)
    if axes_background_color and not use_only_mpl:
        ax.set_facecolor(axes_background_color)

    if not use_only_mpl and color_cycle and color_cycle != "false":
        ax.set_prop_cycle(color=color_cycle)

    if not use_only_mpl and color_palette and color_palette in plt.colormaps():
        cmap = cm.get_cmap(color_palette)
        pal_cycle = [cmap(i) for i in range(cmap.N // 10) if cmap.N > 0]
        if pal_cycle:
            ax.set_prop_cycle(color=pal_cycle)

    for ds in data_sets:
        date_list, value_list, key_list = ds
        if not date_list:
            continue
        dataset_label = key_list[0] if key_list else ""

        if value_list:
            total_avg = sum(value_list)/len(value_list)
            sorted_vals = sorted(value_list)
            mid = len(sorted_vals)//2
            median_val = (sorted_vals[mid] if len(sorted_vals)%2==1
                          else (sorted_vals[mid-1]+sorted_vals[mid])/2.0)
            variance = sum((x - total_avg)**2 for x in value_list)/len(value_list)
            std_dev = math.sqrt(variance)
        else:
            total_avg = 0
            median_val = 0
            std_dev = 0

        # raw
        if show_raw=="true":
            ax.plot(date_list, value_list, line_style, marker=marker,
                    lw=float(line_width), alpha=float(line_alpha),
                    label=("Raw - "+dataset_label if use_labels else None))

        # rolling
        if show_rolling=="true":
            if rolling_unit=="points":
                if len(value_list)>=points_window:
                    rd, rv = rolling_average_by_points(date_list, value_list, points_window)
                    if rv:
                        ax.plot(rd, rv, line_style, marker=marker,
                                lw=float(line_width), alpha=float(line_alpha),
                                label=(f"Rolling({points_window}pts) - "+dataset_label if use_labels else None))
            else:
                rd, rv = rolling_average_by_time(date_list, value_list, rolling_unit, rolling_window)
                if rv:
                    ax.plot(rd, rv, line_style, marker=marker,
                            lw=float(line_width), alpha=float(line_alpha),
                            label=(f"Rolling({rolling_window} {rolling_unit}) - "+dataset_label if use_labels else None))

        # daily
        if show_daily=="true":
            dd, dv = group_and_average(date_list, value_list, "day")
            if dv:
                ax.plot(dd, dv, line_style, marker=marker,
                        lw=float(line_width), alpha=float(line_alpha),
                        label=("Daily Avg - "+dataset_label if use_labels else None))

        # hourly
        if show_hourly=="true":
            hd, hv = group_and_average(date_list, value_list, "hour")
            if hv:
                ax.plot(hd, hv, line_style, marker=marker,
                        lw=float(line_width), alpha=float(line_alpha),
                        label=("Hourly Avg - "+dataset_label if use_labels else None))

        # weekly
        if show_weekly=="true":
            wd, wv = group_and_average(date_list, value_list, "week")
            if wv:
                ax.plot(wd, wv, line_style, marker=marker,
                        lw=float(line_width), alpha=float(line_alpha),
                        label=("Weekly Avg - "+dataset_label if use_labels else None))

        # monthly
        if show_monthly=="true":
            md, mv = group_and_average(date_list, value_list, "month")
            if mv:
                ax.plot(md, mv, line_style, marker=marker,
                        lw=float(line_width), alpha=float(line_alpha),
                        label=("Monthly Avg - "+dataset_label if use_labels else None))

        # average
        if show_average=="true":
            ax.axhline(y=total_avg, lw=float(line_width),
                       alpha=float(line_alpha), linestyle='--', color='gray',
                       label=("Overall Avg - "+dataset_label if use_labels else None))

        # median
        if show_median=="true":
            ax.axhline(y=median_val, color='magenta', lw=float(line_width),
                       alpha=float(line_alpha), linestyle=':',
                       label=("Median - "+dataset_label if use_labels else None))

        # stddev
        if show_stddev=="true":
            # If show_average not true, show mean line now
            if show_average!="true":
                ax.axhline(y=total_avg, lw=float(line_width),
                           alpha=float(line_alpha), linestyle='--', color='gray',
                           label=("Mean - "+dataset_label if use_labels else None))
            if date_list:
                ax.fill_between(date_list,
                                [total_avg-std_dev]*len(date_list),
                                [total_avg+std_dev]*len(date_list),
                                color='gray', alpha=0.2,
                                label=("±1 StdDev - "+dataset_label if use_labels else None))

    # Title and range
    range_string = ""
    if range_in_title and global_earliest and global_latest:
        date_fmt = "%H:%M %d %b '%y"
        from_str = global_earliest.strftime(date_fmt)
        to_str = global_latest.strftime(date_fmt)
        range_string = f"From {from_str} to {to_str}"

    if title_text.strip():
        final_title = title_text + ("\n" + range_string if range_string else "")
    else:
        final_title = range_string if range_in_title else ""

    if final_title and not use_only_mpl:
        ax.set_title(final_title, fontsize=int(title_fontsize), color=title_color)

    # Y-label from first dataset
    if data_sets and data_sets[0][2]:
        plt.ylabel(data_sets[0][2][0], fontsize=int(label_fontsize), color=label_color)

    # Grid and ticks
    if major_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if minor_ticks and not use_only_mpl:
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)

    if show_grid and not use_only_mpl:
        ax.grid(color=grid_color if grid_color else "tab:gray",
                linestyle=grid_style if grid_style else "--",
                alpha=float(grid_alpha) if grid_alpha else 0.5)

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

        if x_tick_rotation.isdigit():
            for tick in ax.get_xticklabels():
                tick.set_rotation(int(x_tick_rotation))

        if y_tick_format:
            ax.yaxis.set_major_formatter(plticker.FormatStrFormatter(y_tick_format))

    # Set y/x limits
    if ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    ax.xaxis_date()
    fig.autofmt_xdate()

    if show_legend_final:
        legend_position_v = legend_position if legend_position else "best"
        legend = ax.legend(loc=legend_position_v,
                           fontsize=int(legend_fontsize) if legend_fontsize else 15,
                           frameon=legend_border, framealpha=float(legend_alpha) if legend_alpha else 1.0)
        if legend and legend_color:
            for text in legend.get_texts():
                text.set_color(legend_color)

    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close(fig)
    print("Enhanced averages graph with median, stddev, and optional legend created and saved to", graph_path)
