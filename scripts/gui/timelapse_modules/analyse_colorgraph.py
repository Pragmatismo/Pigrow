"""Compare RGB levels in set order, with bounded thumbnail decoding and rendering."""

import numpy as np
from PIL import Image

from timelapse_modules.analysis_common import (
    frame_axis, load_thumbnail, new_figure, plot_series, require_frames,
    save_figure, style_axis,
)


_IMAGE_ERRORS = (OSError, ValueError, SyntaxError, Image.DecompressionBombError)


def image_statistics(image_path):
    """Return RGB and luminance estimates from a small RGB thumbnail.

    Percentiles describe pixels within one image, rather than uncertainty in the
    mean. Closing the thumbnail releases its pixels before the next image opens.
    """
    with load_thumbnail(image_path, (128, 128)) as image:
        pixels = np.asarray(image, dtype=np.float32).reshape(-1, 3)
        rgb_mean = pixels.mean(axis=0) / 2.55
        rgb_low, rgb_high = np.percentile(pixels, (10, 90), axis=0) / 2.55
        luminance = pixels @ np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)
        brightness = float(luminance.mean() / 2.55)
        dark = float(np.count_nonzero(luminance <= 5) * 100 / len(luminance))
        bright = float(np.count_nonzero(luminance >= 250) * 100 / len(luminance))
    return rgb_mean, rgb_low, rgb_high, brightness, dark, bright


def collect_statistics(frames, progress_interval=500):
    """Keep failed images in their original positions as NaN values."""
    means = np.full((len(frames), 3), np.nan, dtype=np.float32)
    lows = means.copy()
    highs = means.copy()
    luminance = means.copy()  # mean luminance, dark pixels, bright pixels
    failed = 0
    for index, image_path in enumerate(frames):
        try:
            mean, low, high, brightness, dark, bright = image_statistics(image_path)
        except _IMAGE_ERRORS:
            failed += 1
        else:
            means[index], lows[index], highs[index] = mean, low, high
            luminance[index] = brightness, dark, bright
        if progress_interval and (index + 1) % progress_interval == 0:
            print("Analysed {:,} / {:,} images".format(index + 1, len(frames)))
    if failed == len(frames):
        raise ValueError("None of the selected images could be read. Check that the files exist and are valid images.")
    return means, lows, highs, luminance, failed


def color_intensity_ranges(image_path):
    """Legacy helper: count dominant-color pixels in twenty 5% strength bins.

    Signed subtraction avoids treating a weak channel as dominant by uint8
    wraparound. Strength is relative to the full 0..255 range.
    """
    with load_thumbnail(image_path, (128, 128)) as image:
        pixels = np.asarray(image, dtype=np.int16).reshape(-1, 3)
        counts = []
        for channel in range(3):
            other = np.max(pixels[:, [index for index in range(3) if index != channel]], axis=1)
            difference = (pixels[:, channel] - other) / 2.55
            positive = difference[difference > 0]
            counts.append(np.histogram(positive, bins=np.linspace(0, 100, 21))[0])
    return tuple(counts)


def process_image(image_path):
    """Compatibility wrapper for callers of the old per-image helper."""
    return color_intensity_ranges(image_path)


def _pixel_band(ax, low, high, color, max_bins=1200):
    """Draw a bounded envelope without losing narrow peaks in large sets."""
    count = len(low)
    if count <= max_bins:
        x = np.arange(1, count + 1)
    else:
        edges = np.linspace(0, count, max_bins + 1, dtype=int)
        reduced_low = np.full(max_bins, np.nan)
        reduced_high = np.full(max_bins, np.nan)
        for index, (start, end) in enumerate(zip(edges[:-1], edges[1:])):
            # A failed image leaves a visible break, even inside a dense group.
            if np.isfinite(low[start:end]).all():
                reduced_low[index] = low[start:end].min()
                reduced_high[index] = high[start:end].max()
        x = (edges[:-1] + edges[1:] + 1) / 2
        low, high = reduced_low, reduced_high
    if count == 1:
        ax.vlines(1, low[0], high[0], color=color, alpha=0.25, linewidth=12, label="10–90% of pixels")
    else:
        ax.fill_between(x, low, high, color=color, alpha=0.18, linewidth=0, label="10–90% of pixels")


def analyse_set(ani_frame_list, out_file, progress_interval=500):
    frames = require_frames(ani_frame_list)
    means, lows, highs, _, failed = collect_statistics(frames, progress_interval)
    subtitle = ("{:,} frames in set order · RGB brightness estimated from thumbnails · "
                "bands show the 10th–90th pixel percentiles").format(len(frames))
    if failed:
        subtitle += "\n{:,} unreadable images left as gaps.".format(failed)
    if len(frames) > 1200:
        subtitle += "\nDense curves retain extremes; bands show the outer pixel range per group."
    fig, axes = new_figure("Color levels through the image set", subtitle, rows=3)
    x = np.arange(1, len(frames) + 1)
    for channel, (ax, name, color) in enumerate(zip(axes, ("Red", "Green", "Blue"), ("#c43c39", "#29884b", "#2878b5"))):
        _pixel_band(ax, lows[:, channel], highs[:, channel], color)
        plot_series(ax, x, means[:, channel], color=color, label="Mean intensity")
        style_axis(ax, ylabel=name + " intensity (%)")
        frame_axis(ax, len(frames))
        ax.set_ylim(-2, 102)
        ax.legend(loc="upper right", fontsize=9)
    save_figure(fig, out_file)
    return True
