try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.ticker as plticker
    import matplotlib.cm as cm
    import datetime
except ImportError:
    print("Matplotlib not installed, can't create graphs on this device")


def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui.
    '''
    graph_module_settings_dict = {
        "auto_barwidth": "true",
        "bar_alpha": "1",
        "title_text": "",
        "show_time_period": "true",
        "bar_align": ["center", "edge"],
        "color_cycle": "",
        "bar_width": "0.0005",
        "show_grid": "false",

        # Additional style
        "major_ticks": "",
        "minor_ticks": "",
        "mpl_style": "",
        "use_only_mpl": "false",
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
        "color_palette": "",
        "show_legend": "true",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",
        "bar_edge_color": "",
        "bar_linewidth": "0"
    }
    return graph_module_settings_dict

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra={}):
    if not extra:
        extra = read_graph_options()

    def get_opt(key, default=None):
        return extra.get(key, default)

    # Extract main options
    title_text = get_opt("title_text","")
    show_time_period = get_opt("show_time_period","true").lower()=="true"
    color_cycle = get_opt("color_cycle","")
    if isinstance(color_cycle, str) and ',' in color_cycle:
        color_cycle = [c.strip() for c in color_cycle.split(",") if c.strip()]
    bar_width = float(get_opt("bar_width","0.0005"))
    bar_alpha = float(get_opt("bar_alpha","0.5"))
    show_grid = get_opt("show_grid","false").lower()=="true"
    major_ticks = get_opt("major_ticks","")
    minor_ticks = get_opt("minor_ticks","")

    mpl_style = get_opt("mpl_style","")
    use_only_mpl = get_opt("use_only_mpl","false").lower()=="true"
    background_color = get_opt("background_color","")
    axes_background_color = get_opt("axes_background_color","")
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
    grid_color = get_opt("grid_color","tab:gray")
    grid_style = get_opt("grid_style","--")
    grid_alpha = get_opt("grid_alpha","0.5")
    x_tick_rotation = get_opt("x_tick_rotation","0")
    y_tick_format = get_opt("y_tick_format","")
    color_palette = get_opt("color_palette","")
    legend_position = get_opt("legend_position","best")
    legend_border = get_opt("legend_border","true").lower()=="true"
    legend_alpha = get_opt("legend_alpha","1.0")
    bar_edge_color = get_opt("bar_edge_color","")
    bar_linewidth = float(get_opt("bar_linewidth","0"))
    bar_align = get_opt("bar_align","center")
    show_legend_opt = get_opt("show_legend","true").lower()=="true"
    auto_barwidth = get_opt("auto_barwidth","false").lower()=="true"

    if mpl_style and not use_only_mpl:
        plt.style.use(mpl_style)

    # Gather all dates to determine global earliest and latest
    all_dates = [d for ds in list_of_datasets for d in ds[0] if ds[0]]
    global_earliest = min(all_dates) if all_dates else None
    global_latest = max(all_dates) if all_dates else None

    lines_count = len([ds for ds in list_of_datasets if ds[0]])
    use_labels = (lines_count > 1)
    show_legend_final = (use_labels and show_legend_opt and not use_only_mpl)

    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12,
                                   float(size_v) if size_v else 7))

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

    # Compute auto_barwidth if enabled
    if auto_barwidth and all_dates:
        sorted_dates = sorted(all_dates)
        if len(sorted_dates) > 1:
            gaps = [(sorted_dates[i+1]-sorted_dates[i]).total_seconds() for i in range(len(sorted_dates)-1)]
            if gaps:
                min_gap_seconds = min(gaps)
                min_gap_days = min_gap_seconds/86400.0
                bar_width = min_gap_days * 0.8
            else:
                bar_width = 0.0005
        else:
            bar_width = 0.0005

    # Plot bars
    for ds in list_of_datasets:
        date_list, value_list, key_list = ds
        if not date_list:
            continue
        dataset_label = key_list[0] if key_list else ""
        ax.bar(date_list, value_list,
               label=(dataset_label if use_labels else None),
               width=bar_width, linewidth=bar_linewidth, alpha=bar_alpha,
               edgecolor=bar_edge_color if bar_edge_color else None,
               align=bar_align)

    # After plotting bars, check if bars are visible
    # If bars are too narrow:
    # 1. Get figure DPI and size in inches
    dpi = fig.dpi
    fig_width_in = fig.get_size_inches()[0]
    # horizontal pixels
    fig_width_px = dpi * fig_width_in

    # get current x limits
    xmin, xmax = ax.get_xlim()
    data_range = xmax - xmin
    if data_range > 0:
        data_per_pixel = data_range / fig_width_px
        # If bar_width < 2 * data_per_pixel, bars are likely too narrow
        if bar_width < 2 * data_per_pixel:
            # Append warning to title
            warning_text = "Too many data points to fit on the graph, reduce the amount of points or increase graph width."
            if title_text.strip():
                title_text += "\n" + warning_text
            else:
                title_text = warning_text

    # Customize axes
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

    final_title = title_text
    if show_time_period and global_earliest and global_latest:
        date_fmt = "%b-%d %H:%M"
        from_str = global_earliest.strftime(date_fmt)
        to_str = global_latest.strftime(date_fmt)
        time_period_str = f"Time Period; {from_str} to {to_str}"
        if final_title.strip():
            final_title += "\n" + time_period_str
        else:
            final_title = time_period_str

    if final_title and not use_only_mpl:
        ax.set_title(final_title, fontsize=int(title_fontsize), color=title_color)

    # If single dataset, label Y-axis with dataset name
    if len(list_of_datasets)==1 and list_of_datasets[0][2]:
        plt.ylabel(list_of_datasets[0][2][0], fontsize=int(label_fontsize), color=label_color)

    if ymax.isdigit():
        plt.ylim(top=int(ymax))
    if ymin.isdigit():
        plt.ylim(bottom=int(ymin))

    ax.xaxis_date()
    fig.autofmt_xdate()

    if show_legend_final:
        legend_position_v = legend_position if legend_position else "best"
        legend = ax.legend(loc=legend_position_v,
                           fontsize=int(legend_fontsize),
                           frameon=legend_border, framealpha=float(legend_alpha))
        if legend and legend_color:
            for text in legend.get_texts():
                text.set_color(legend_color)

    plt.tight_layout()
    plt.savefig(graph_path)
    plt.close(fig)
    print("Bar graph created and saved to", graph_path)
