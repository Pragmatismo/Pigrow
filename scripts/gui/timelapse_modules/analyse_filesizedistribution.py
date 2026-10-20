"""A histogram to find a practical file-size cutoff for a capture set."""

import numpy as np

from timelapse_modules.analysis_common import new_figure, require_frames, save_figure, style_axis
from timelapse_modules.analyse_filesize import collect_file_sizes, MIB

DESCRIPTION = "File size histogram: compare dark/light groups and choose a cutoff in MiB."


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    sizes, missing = collect_file_sizes(frames)
    sizes = sizes[np.isfinite(sizes)] / MIB
    if not sizes.size:
        raise ValueError("No readable file sizes. Check that the image files still exist.")
    subtitle = ("{:,} readable files | median {:.3f} MiB | gaps between groups can suggest a light/dark cutoff"
                .format(sizes.size, np.median(sizes)))
    if missing:
        subtitle += " | {:,} inaccessible files skipped".format(missing)
    fig, axes = new_figure("File size distribution", subtitle)
    try:
        ax = axes[0]
        # At most 100 rectangles, independent of the number of captures.
        ax.hist(sizes, bins=min(100, max(1, int(np.sqrt(sizes.size)))), color="#2878b5",
                edgecolor="white", linewidth=0.5)
        ax.axvline(np.median(sizes), color="#a56821", linestyle="--", linewidth=1.5,
                   label="Median ({:.3f} MiB)".format(np.median(sizes)))
        style_axis(ax, xlabel="File size (MiB; 1 MiB = 1,048,576 bytes)", ylabel="Number of images")
        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xlim(left=max(0, ax.get_xlim()[0]))
        ax.set_ylim(bottom=0)
        ax.legend(loc="best")
        save_figure(fig, out_file)
    finally:
        fig.clear()
    return True
