"""File size in set order, with bounded rendering for long capture sets."""

import os

import numpy as np

from timelapse_modules.analysis_common import (
    frame_axis, new_figure, plot_series, require_frames, save_figure, style_axis,
)

DESCRIPTION = "File size by frame: find light/dark transitions and unusually small files."
MIB = 1024 ** 2


def collect_file_sizes(frames):
    """Retain positions of inaccessible files as gaps instead of shifting frames."""
    sizes = np.full(len(frames), np.nan, dtype=float)
    for index, path in enumerate(frames):
        try:
            sizes[index] = os.path.getsize(path)
        except (OSError, ValueError):
            continue
    return sizes, int(np.count_nonzero(~np.isfinite(sizes)))


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    sizes, missing = collect_file_sizes(frames)
    usable = sizes[np.isfinite(sizes)] / MIB
    if not usable.size:
        raise ValueError("No readable file sizes. Check that the image files still exist.")
    subtitle = ("{:,} frames | median {:.3f} MiB | range {:.3f}–{:.3f} MiB"
                .format(len(frames), np.median(usable), usable.min(), usable.max()))
    if missing:
        subtitle += " | {:,} inaccessible files shown as gaps".format(missing)
    if len(frames) > 6000:
        subtitle += " | Dense view: min–max ranges and mean per frame group"
    fig, axes = new_figure("File size by frame", subtitle)
    try:
        ax = axes[0]
        plot_series(ax, np.arange(1, len(frames) + 1), sizes / MIB)
        ax.axhline(np.median(usable), color="#a56821", linestyle="--", linewidth=1,
                   label="Median ({:.3f} MiB)".format(np.median(usable)))
        style_axis(ax, ylabel="File size (MiB; 1 MiB = 1,048,576 bytes)")
        frame_axis(ax, len(frames))
        ax.set_ylim(bottom=0)
        ax.legend(loc="best")
        save_figure(fig, out_file)
    finally:
        fig.clear()
    return True
