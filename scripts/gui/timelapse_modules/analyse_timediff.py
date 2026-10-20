"""Adjacent capture intervals, preserving timing errors and unknown timestamps."""

import numpy as np

from timelapse_modules.analysis_common import (
    capture_datetime, date_from_filename, frame_axis, new_figure, plot_series,
    require_frames, save_figure, style_axis,
)
from timelapse_modules.analyse_time import time_unit

DESCRIPTION = "Time between adjacent frames: spot gaps, duplicate timestamps and clock changes."


def capture_intervals(frames):
    dates = [capture_datetime(path) for path in frames]
    intervals = np.full(len(frames), np.nan, dtype=float)
    for index in range(1, len(dates)):
        if dates[index - 1] is not None and dates[index] is not None:
            intervals[index] = (dates[index] - dates[index - 1]).total_seconds()
    return dates, intervals


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    dates, intervals = capture_intervals(frames)
    valid = intervals[np.isfinite(intervals)]
    if not valid.size:
        if len(frames) == 1 and dates[0] is not None:
            subtitle = "1 frame | At least two adjacent timestamped frames are needed to measure an interval."
        else:
            raise ValueError("No adjacent frames have usable capture timestamps; intervals cannot be measured.")
    else:
        positive = valid[valid > 0]
        typical = float(np.median(positive)) if positive.size else None
        subtitle = "{:,} frames | {:,} measured intervals".format(len(frames), valid.size)
        if typical is not None:
            subtitle += " | median positive interval {:g} s | {:,} gaps >1.5× median".format(
                typical, int(np.count_nonzero(valid > 1.5 * typical)))
        subtitle += " | {:,} duplicates | {:,} backwards".format(
            int(np.count_nonzero(valid == 0)), int(np.count_nonzero(valid < 0)))
        unknown = int(np.count_nonzero(~np.isfinite(intervals[1:])))
        if unknown:
            subtitle += " | {:,} unknown intervals shown as gaps".format(unknown)
    scale, unit = time_unit(valid)
    if len(frames) > 6000:
        subtitle += " | Dense view: min–max ranges and mean per frame group"
    fig, axes = new_figure("Time between frames", subtitle)
    try:
        ax = axes[0]
        style_axis(ax, ylabel="Interval since previous frame ({})".format(unit))
        frame_axis(ax, len(frames))
        if valid.size:
            plot_series(ax, np.arange(1, len(frames) + 1), intervals / scale)
            ax.axhline(0, color="#77818a", linewidth=0.8)
            positive = valid[valid > 0]
            if positive.size:
                typical = float(np.median(positive))
                ax.axhline(typical / scale, color="#a56821", linewidth=1, linestyle="--",
                           label="Median positive interval ({:g} s)".format(typical))
            anomalies = np.isfinite(intervals) & (intervals <= 0)
            if np.any(anomalies):
                # Bound anomaly marker count too; the series still retains all extrema.
                positions = np.flatnonzero(anomalies)
                positions = positions[::max(1, int(np.ceil(len(positions) / 1000)))]
                ax.scatter(positions + 1, intervals[positions] / scale, s=22, color="#b33434",
                           zorder=4, label="Duplicate / backwards timestamp")
            ax.legend(loc="best")
        else:
            ax.text(0.5, 0.5, "One frame: no interval yet", transform=ax.transAxes,
                    ha="center", va="center", color="#52606d")
        save_figure(fig, out_file)
    finally:
        fig.clear()
    return True
