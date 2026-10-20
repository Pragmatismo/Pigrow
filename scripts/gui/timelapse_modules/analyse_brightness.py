"""Reveal light/dark periods and near-black/near-white pixels in an image set."""

import numpy as np

from timelapse_modules.analysis_common import (
    frame_axis, new_figure, plot_series, require_frames, save_figure, style_axis,
)
from timelapse_modules.analyse_colorgraph import collect_statistics


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    _, _, _, luminance, failed = collect_statistics(frames)
    subtitle = ("{:,} frames in set order · thumbnail estimates · brightness uses weighted RGB "
                "(21% red, 72% green, 7% blue)").format(len(frames))
    if failed:
        subtitle += "\n{:,} unreadable images left as gaps.".format(failed)
    fig, axes = new_figure("Brightness and exposure", subtitle, rows=2)
    x = np.arange(1, len(frames) + 1)
    plot_series(axes[0], x, luminance[:, 0], color="#b47b18", label="Mean brightness")
    style_axis(axes[0], ylabel="Brightness (%)")
    axes[0].set_ylim(-2, 102)
    axes[0].legend(loc="upper right", fontsize=9)
    plot_series(axes[1], x, luminance[:, 1], color="#344354", label="Near black (luminance ≤ 5/255)")
    plot_series(axes[1], x, luminance[:, 2], color="#bf651f", label="Near white (luminance ≥ 250/255)")
    style_axis(axes[1], ylabel="Pixels near limits (%)")
    axes[1].set_ylim(-2, 102)
    axes[1].legend(loc="upper right", fontsize=9)
    for ax in axes:
        frame_axis(ax, len(frames))
    save_figure(fig, out_file)
    return True
