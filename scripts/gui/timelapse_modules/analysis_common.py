"""Shared, headless rendering helpers for Image Set Analyse modules.

Frame numbers always refer to the supplied set order. Epoch timestamps are UTC;
compact date suffixes are taken literally, without consulting file modification
times (which change when images are downloaded).
"""

import math
import os
from pathlib import Path
import re
import tempfile
import textwrap
from datetime import datetime, timezone

import numpy as np
from PIL import Image, ImageFont, ImageOps


def require_frames(frames):
    frames = list(frames)
    if not frames:
        raise ValueError("There are no images in the selected frame range.")
    return frames


def capture_datetime(path):
    """Read a capture suffix, preferring 14-digit calendar dates over epochs."""
    suffix = Path(path).stem.rsplit("_", 1)[-1]
    if re.fullmatch(r"\d{14}", suffix):
        try:
            return datetime.strptime(suffix, "%Y%m%d%H%M%S")
        except ValueError:
            return None
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", suffix):
        return None
    try:
        timestamp = float(suffix)
        if not math.isfinite(timestamp):
            return None
        return datetime.fromtimestamp(timestamp, timezone.utc).replace(tzinfo=None)
    except (ValueError, OverflowError, OSError):
        return None


def date_from_filename(path):
    return os.path.basename(path), capture_datetime(path) or "undetermined"


def load_thumbnail(path, size=(128, 128)):
    """Return an owned RGB thumbnail; never keep the source file open.

    JPEG draft decoding reduces peak memory before orientation and conversion.
    Pillow's decompression-bomb protection remains enabled for other formats.
    """
    with Image.open(path) as source:
        source.draft("RGB", size)
        source.thumbnail(size, Image.Resampling.LANCZOS)
        oriented = ImageOps.exif_transpose(source)
        try:
            return oriented.convert("RGB")
        finally:
            if oriented is not source:
                oriented.close()


def load_font(size):
    for name in ("DejaVuSans.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow before scalable default fonts.
        return ImageFont.load_default()


def _atomic_png(out_file, writer):
    """Replace the output only after a complete render, including on disk errors."""
    destination = os.path.abspath(out_file)
    handle, temporary = tempfile.mkstemp(prefix=".analysis-", suffix=".png",
                                          dir=os.path.dirname(destination))
    os.close(handle)
    try:
        writer(temporary)
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_image(image, out_file):
    _atomic_png(out_file, lambda path: image.save(path, format="PNG"))


def new_figure(title, subtitle="", rows=1):
    # Direct Agg canvases avoid GUI backends in delayedresult worker threads.
    # No pyplot state or process-global backend changes are needed.
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    caption = "\n".join(textwrap.wrap(subtitle, width=145))
    height = 6.5 if rows == 1 else 3.5 * rows + 2
    figure = Figure(figsize=(16, height), dpi=100, facecolor="#f5f7fa")
    FigureCanvasAgg(figure)
    axes = list(figure.subplots(rows, 1, squeeze=False)[:, 0])
    figure.suptitle(title, x=0.07, y=0.975, ha="left", fontsize=20,
                   fontfamily="DejaVu Sans", fontweight="bold", color="#1b293a")
    if caption:
        figure.text(0.07, 0.925, caption, ha="left", va="top", fontsize=10,
                    fontfamily="DejaVu Sans", color="#435269", linespacing=1.5)
    # Keep the complete title, caption, tick labels, and legend on the canvas.
    caption_height = max(1, len(caption.splitlines())) * 0.25
    top = 1 - (1.0 + caption_height) / height
    figure.subplots_adjust(left=0.085, right=0.975, bottom=0.105,
                            top=top, hspace=0.42)
    for axis in axes:
        style_axis(axis)
    return figure, axes


def style_axis(ax, xlabel="Frame number (set order)", ylabel=""):
    ax.set_facecolor("white")
    ax.set_xlabel(xlabel, fontsize=11, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=11, labelpad=10)
    ax.tick_params(axis="both", labelsize=10, colors="#435269")
    ax.grid(axis="y", color="#dde3eb", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#acb7c6")


def frame_axis(ax, count):
    from matplotlib.ticker import MaxNLocator, StrMethodFormatter
    ax.set_xlim(0.5, max(1, count) + 0.5)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10, integer=True, min_n_ticks=1))
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))


def plot_series(ax, x, y, color="#2878b5", label=None):
    """Plot dense series with bounded artists, preserving extrema and gaps.

    Each dense bin covers consecutive input frames. Vertical ranges retain short
    spikes; the mean line stops whenever a bin contains missing values.
    """
    x, y = np.asarray(x), np.asarray(y, dtype=float)
    if len(y) <= 6000:
        return ax.plot(x, y, color=color, label=label, linewidth=1.3,
                       marker="o" if len(y) <= 80 else None, markersize=3)
    count = min(1600, len(y))
    edges = np.linspace(0, len(y), count + 1, dtype=int)
    centers, low, high, means, mixed_x, mixed_y = [], [], [], [], [], []
    for start, end in zip(edges[:-1], edges[1:]):
        values = y[start:end]
        valid = np.isfinite(values)
        center = (float(x[start]) + float(x[end - 1])) / 2
        centers.append(center)
        if not valid.any():
            low.append(np.nan)
            high.append(np.nan)
            means.append(np.nan)
            continue
        finite = values[valid]
        low.append(float(finite.min()))
        high.append(float(finite.max()))
        mean = float(finite.mean())
        means.append(mean if valid.all() else np.nan)
        if not valid.all():
            mixed_x.append(center)
            mixed_y.append(mean)
    ax.vlines(centers, low, high, colors=color, alpha=0.4, linewidth=0.8)
    if mixed_x:
        ax.scatter(mixed_x, mixed_y, color=color, s=3)
    return ax.plot(centers, means, color=color, label=label, linewidth=1.2)


def save_figure(figure, out_file):
    try:
        _atomic_png(out_file, lambda path: figure.savefig(path, format="png", dpi=100))
    finally:
        figure.clear()
