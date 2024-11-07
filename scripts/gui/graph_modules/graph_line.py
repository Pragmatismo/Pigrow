
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
def read_graph_options():
    '''
    Returns a dictionary of settings and their default values for use by the remote gui
    '''
    graph_module_settings_dict = {
        "title_text": "",
        "color_cycle": "false",
        "line_style": "-",
        "marker": "o",
        "show_grid": "true",
        "major_ticks": "",
        "minor_ticks": "",
        "title_fontsize": "12",
        "label_fontsize": "10",
        "legend_fontsize": "10",
        "line_width": "1.5",
        "line_alpha": "1.0",
        "color_palette": "",
        "grid_color": "gray",
        "grid_style": "--",
        "grid_alpha": "0.5",
        "background_color": "white",
        "axes_background_color": "white",
        "legend_position": "best",
        "legend_border": "true",
        "legend_alpha": "1.0",
        "x_tick_rotation": "0",
        "y_tick_format": "",
        "mpl_style": "",
        "use_only_mpl": "false"
    }

    print("AVAILABLE:", matplotlib.style.available)
    return graph_module_settings_dict


import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker


def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="",
               extra={}):
    print("Want's to create a line graph using the graph_line.py module...")

    # Load defaults if no settings supplied
    if extra == {}:
        extra = read_graph_options()

    # Extract and convert options from extra
    mpl_style = extra.get("mpl_style", "")
    use_only_mpl = extra.get("use_only_mpl", "false").lower() == "true"

    # Apply style if specified
    if mpl_style:
        plt.style.use(mpl_style)

    title_text = extra.get("title_text", "")
    color_cycle = extra.get("color_cycle", "false").lower()
    if ',' in color_cycle:
        color_cycle = [color.strip() for color in color_cycle.split(",")]
    line_style = extra.get("line_style", "-")
    marker = extra.get("marker", "o")
    line_flags = marker + line_style
    show_grid = extra.get("show_grid", "true").lower() == "true"
    major_ticks = extra.get("major_ticks", "")
    minor_ticks = extra.get("minor_ticks", "")
    title_fontsize = extra.get("title_fontsize", "12") or None
    label_fontsize = extra.get("label_fontsize", "10") or None
    legend_fontsize = extra.get("legend_fontsize", "10") or None
    line_width = float(extra.get("line_width", "1.5")) if extra.get("line_width", "1.5") else None
    line_alpha = float(extra.get("line_alpha", "1.0")) if extra.get("line_alpha", "1.0") else None
    color_palette = extra.get("color_palette", "").split(",") if extra.get("color_palette") else None
    grid_color = extra.get("grid_color", "gray")
    grid_style = extra.get("grid_style", "--")
    grid_alpha = float(extra.get("grid_alpha", "0.5")) if extra.get("grid_alpha", "0.5") else None
    background_color = extra.get("background_color", "white")
    axes_background_color = extra.get("axes_background_color", "white")
    legend_position = extra.get("legend_position", "best")
    legend_border = extra.get("legend_border", "true").lower() == "true"
    legend_alpha = float(extra.get("legend_alpha", "1.0")) if extra.get("legend_alpha", "1.0") else None
    x_tick_rotation = int(extra.get("x_tick_rotation", "0")) if extra.get("x_tick_rotation", "0") else None
    y_tick_format = extra.get("y_tick_format", "")

    if use_only_mpl:
        line_flags = ""
        color_cycle = ""
        line_flags = ""
        show_grid = ""
        major_ticks = ""
        minor_ticks = ""
        line_width = ""
        line_alpha = ""
        color_palette = ""
        grid_color = ""
        grid_style = ""
        grid_alpha = ""
        background_color = ""
        axes_background_color = ""
        legend_position = ""
        legend_border = ""
        legend_alpha = ""
        x_tick_rotation = ""
        y_tick_format = ""

    # Set up the figure and axes
    fig, ax = plt.subplots(figsize=(float(size_h) if size_h else 12, float(size_v) if size_v else 7))
    if background_color:
        fig.patch.set_facecolor(background_color)
    if axes_background_color:
        ax.set_facecolor(axes_background_color)

    # Set color cycle if provided
    if color_palette:
        ax.set_prop_cycle(color=color_palette)
    elif color_cycle and color_cycle != "false":
        ax.set_prop_cycle(color=color_cycle)

    # Create plot for each dataset
    for dataset in list_of_datasets:
        date_list, value_list, key_list = dataset
        if line_flags:
            ax.plot(date_list, value_list, line_flags, label=key_list[0], lw=line_width if line_width else 1.5,
                    alpha=line_alpha if line_alpha else 1.0)
        else:
            ax.plot(date_list, value_list, line_flags, label=key_list[0])

    # Organize the graphing area
    if major_ticks:
        loc = plticker.MultipleLocator(base=float(major_ticks))
        ax.yaxis.set_major_locator(loc)
    if minor_ticks:
        loc = plticker.MultipleLocator(base=float(minor_ticks))
        ax.yaxis.set_minor_locator(loc)
    if show_grid:
        ax.grid(color=grid_color, linestyle=grid_style, alpha=grid_alpha)

    # Set title and axis labels
    if title_text:
        plt.title(title_text, fontsize=int(title_fontsize) if title_fontsize else None)
    if list_of_datasets and label_fontsize:
        plt.ylabel(key_list[0], fontsize=int(label_fontsize))
    if x_tick_rotation:
        plt.xticks(rotation=int(x_tick_rotation))

    # Format y-axis ticks if specified
    if y_tick_format:
        ax.yaxis.set_major_formatter(plticker.FormatStrFormatter(y_tick_format))

    # Display legend if multiple datasets
    if len(list_of_datasets) > 1 and legend_position:
        ax.legend(loc=legend_position, fontsize=int(legend_fontsize) if legend_fontsize else None,
                  frameon=legend_border, framealpha=legend_alpha)

    # Set y-axis limits if provided
    if ymax:
        ax.set_ylim(top=int(ymax))
    if ymin:
        ax.set_ylim(bottom=int(ymin))

    # Format x-axis for dates and adjust layout
    ax.xaxis_date()
    fig.autofmt_xdate()

    # Save the graph to the specified path
    plt.savefig(graph_path)
    plt.close(fig)  # Close the figure to free memory
    print(f"Line graph created and saved to {graph_path}")
