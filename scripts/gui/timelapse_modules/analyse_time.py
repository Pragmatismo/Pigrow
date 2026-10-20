"""Capture time against the actual frame order used for the animation."""

import numpy as np

from timelapse_modules.analysis_common import (
    capture_datetime, date_from_filename, frame_axis, new_figure, plot_series,
    require_frames, save_figure, style_axis,
)

DESCRIPTION = "Capture time by frame: reveal timing changes, missing periods and out-of-order images."


def elapsed_capture_times(frames):
    dates = [capture_datetime(path) for path in frames]
    baseline = next((value for value in dates if value is not None), None)
    if baseline is None:
        raise ValueError("No capture timestamps found. Use filename suffixes such as _1700000000 or _20260102123000.")
    elapsed = np.array([(value - baseline).total_seconds() if value is not None else np.nan
                        for value in dates], dtype=float)
    return dates, baseline, elapsed


def time_unit(seconds):
    largest = float(np.max(np.abs(seconds[np.isfinite(seconds)]))) if len(seconds) else 0
    if largest >= 172800:
        return 86400.0, "days"
    if largest >= 7200:
        return 3600.0, "hours"
    if largest >= 120:
        return 60.0, "minutes"
    return 1.0, "seconds"


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    dates, baseline, elapsed = elapsed_capture_times(frames)
    missing = sum(value is None for value in dates)
    scale, unit = time_unit(elapsed)
    subtitle = "{:,} frames | elapsed from {} UTC | frame order retained".format(
        len(frames), baseline.strftime("%Y-%m-%d %H:%M:%S"))
    if missing:
        subtitle += " | {:,} unknown timestamps shown as gaps".format(missing)
    if len(frames) > 6000:
        subtitle += " | Dense view: min–max ranges and mean per frame group"
    fig, axes = new_figure("Capture time by frame", subtitle)
    try:
        ax = axes[0]
        plot_series(ax, np.arange(1, len(frames) + 1), elapsed / scale)
        style_axis(ax, ylabel="Elapsed capture time ({})".format(unit))
        frame_axis(ax, len(frames))
        save_figure(fig, out_file)
    finally:
        fig.clear()
    return True
