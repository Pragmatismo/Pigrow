"""A bounded, labelled calendar of capture coverage and image appearance."""

from bisect import bisect_left
from collections import defaultdict
from itertools import groupby
from math import ceil
from statistics import median

from PIL import Image, ImageDraw

from timelapse_modules.analysis_common import (
    capture_datetime, date_from_filename, load_font, load_thumbnail,
    require_frames, save_image,
)

DESCRIPTION = (
    "Days across, midnight to midnight down (UTC). Blank areas reveal gaps; "
    "image strips reveal lighting and colour changes."
)

BACKGROUND = (247, 249, 252)
MISSING = (225, 231, 238)
MISSING_ALT = (234, 239, 244)
UNREADABLE = (242, 179, 168)
INK = (34, 49, 68)
MUTED = (87, 104, 124)
LEFT = 82
RIGHT = 26
TOP = 126
LABEL_HEIGHT = 116
PANEL_GAP = 34
FOOTER = 68
MAX_WIDTH = 2400
MAX_HEIGHT = 16000
MAX_PIXELS = 24_000_000


def find_vertical_position(hour, minute, img_height):
    return (hour * 60 + minute) * img_height / 1440


def find_vertical_position_from_datetime(dt_value, img_height):
    return _minute(dt_value) * img_height / 1440


def _minute(value):
    return (value.hour * 60 + value.minute + value.second / 60
            + value.microsecond / 60_000_000)


def get_image_windows(day_datetimes, full_day_minutes=1440, jitter_tolerance=1.5):
    """Centre strips on captures without painting through long missing periods.

    The typical positive interval sets strip duration, capped at one hour: an
    isolated photograph cannot establish coverage for a whole afternoon. Large
    gaps retain the missing-data background. Input must be chronological.
    """
    if not day_datetimes:
        return []
    intervals = [(right - left).total_seconds() / 60
                 for left, right in zip(day_datetimes, day_datetimes[1:])
                 if right > left]
    cadence = min(60.0, median(intervals)) if intervals else 30.0
    half = cadence / 2
    windows = [[max(0.0, _minute(value) - half),
                min(float(full_day_minutes), _minute(value) + half)]
               for value in day_datetimes]
    for previous, current in zip(windows, windows[1:]):
        gap = current[0] - previous[1]
        if 0 < gap <= jitter_tolerance:
            previous[1] = current[0] = (previous[1] + current[0]) / 2
    return [tuple(window) for window in windows]


def _layout(day_count):
    """Keep output dimensions independent of the number of input photographs."""
    body_height = 720 if day_count <= 120 else (480 if day_count <= 1500 else 360)
    widths = [max(120, (960 - LEFT - RIGHT) // day_count)] if day_count <= 7 else []
    widths += [120, 96, 72, 48, 32, 24, 16, 12]
    for column_width in widths:
        columns = min(day_count, (MAX_WIDTH - LEFT - RIGHT) // column_width)
        rows = ceil(day_count / columns)
        width = LEFT + columns * column_width + RIGHT
        height = TOP + rows * (LABEL_HEIGHT + body_height) + (rows - 1) * PANEL_GAP + FOOTER
        if height <= MAX_HEIGHT and width * height <= MAX_PIXELS:
            return column_width, columns, body_height, width, height
    raise ValueError(
        "Too many separate capture days for one readable day grid. "
        "Select a shorter date range and try again."
    )


def _render_rows(images, body_height):
    """Choose at most one photograph per output row, preserving visible gaps."""
    times = [_minute(value) for value, _ in images]
    windows = get_image_windows([value for value, _ in images])
    occupied = {}
    for index, minute in enumerate(times):
        row = min(body_height - 1, int(minute * body_height / 1440))
        old = occupied.get(row)
        midpoint = (row + .5) * 1440 / body_height
        if old is None or abs(times[old] - midpoint) > abs(minute - midpoint):
            occupied[row] = index
    rows = []
    for row in range(body_height):
        midpoint = (row + .5) * 1440 / body_height
        insertion = bisect_left(times, midpoint)
        candidates = [index for index in (insertion - 1, insertion)
                      if 0 <= index < len(times)]
        closest = min(candidates, key=lambda index: abs(times[index] - midpoint))
        if windows[closest][0] <= midpoint <= windows[closest][1]:
            rows.append(closest)
        else:
            rows.append(occupied.get(row))
    return rows


def _centered(draw, xy, text, font, fill=INK):
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text((int(xy[0] - (bounds[2] - bounds[0]) / 2), xy[1]),
              text, font=font, fill=fill)


def _short_count(count):
    # Exact totals remain in the heading; compact daily counts keep narrow
    # calendar columns legible even with hundreds of thousands of frames/day.
    for threshold, suffix in ((1_000_000_000, "b"), (1_000_000, "m"), (1_000, "k")):
        if count >= threshold:
            value = "{:.1f}".format(count / threshold).rstrip("0").rstrip(".")
            return value + suffix
    return str(count)


def _fitted_font(draw, text, size, max_width):
    font = load_font(size)
    while draw.textbbox((0, 0), text, font=font)[2] > max_width and size > 8:
        size -= 1
        font = load_font(size)
    return font


def _date_label(canvas, draw, day, count, x, width, y):
    font = load_font(15)
    count_text = _short_count(count)
    if width >= 72:
        _centered(draw, (x + width / 2, y + 18), day.strftime("%d %b"), font)
        _centered(draw, (x + width / 2, y + 41), str(day.year), load_font(13), MUTED)
        text = "{} frames".format(count_text)
        count_font = _fitted_font(draw, text, 11, width - 8)
        _centered(draw, (x + width / 2, y + 65), text, count_font, MUTED)
    else:
        label = Image.new("RGB", (110, max(12, width)), BACKGROUND)
        label_draw = ImageDraw.Draw(label)
        text = "{} / {}".format(day.isoformat(), count_text)
        label_font = _fitted_font(label_draw, text, min(11, width - 1), 106)
        label_draw.text((2, 0), text, font=label_font, fill=INK)
        rotated = label.rotate(90, expand=True)
        canvas.paste(rotated, (x + (width - rotated.width) // 2, y + 4))
        label.close()
        rotated.close()


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    day_images = defaultdict(list)
    undated = 0
    for path in frames:
        value = capture_datetime(path)
        if value is None:
            undated += 1
        else:
            day_images[value.date()].append((value, path))
    if not day_images:
        raise ValueError("No capture dates found in filenames. Use epoch or YYYYMMDDHHMMSS filename suffixes.")

    days = sorted(day_images)
    column_width, columns, body_height, width, height = _layout(len(days))
    canvas = Image.new("RGB", (width, height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((LEFT, 16), "Day grid", font=load_font(28), fill=INK)
    summary = "{:,} frames | {:,} capture days | {} to {} | UTC".format(
        len(frames), len(days), days[0].isoformat(), days[-1].isoformat())
    draw.text((LEFT, 54), summary, font=load_font(14), fill=MUTED)
    draw.text((LEFT, 80), "Each column is a full day (date / frame count). Grey = no capture; salmon = unreadable image.",
              font=load_font(13), fill=MUTED)
    unreadable = set()
    rendered = 0
    panel_count = ceil(len(days) / columns)
    for panel in range(panel_count):
        label_y = TOP + panel * (LABEL_HEIGHT + body_height + PANEL_GAP)
        plot_y = label_y + LABEL_HEIGHT
        panel_days = days[panel * columns:(panel + 1) * columns]
        panel_right = LEFT + len(panel_days) * column_width
        for column, day in enumerate(panel_days):
            x = LEFT + column * column_width
            images = sorted(day_images[day], key=lambda entry: entry[0])
            _date_label(canvas, draw, day, len(images), x, column_width, label_y)
            draw.rectangle((x, plot_y, x + column_width - 1, plot_y + body_height - 1), fill=MISSING)
            for tile_y in range(0, body_height, 12):
                for tile_x in range(0, column_width, 12):
                    if (tile_y // 12 + tile_x // 12) % 2:
                        draw.rectangle((x + tile_x, plot_y + tile_y,
                                        x + min(column_width - 1, tile_x + 11),
                                        plot_y + min(body_height - 1, tile_y + 11)), fill=MISSING_ALT)
            row_start = 0
            for index, group in groupby(_render_rows(images, body_height)):
                row_count = sum(1 for _ in group)
                if index is not None:
                    path = images[index][1]
                    try:
                        with load_thumbnail(path, (max(128, column_width), 360)) as thumbnail:
                            strip = thumbnail.resize((column_width, row_count), Image.Resampling.LANCZOS)
                            canvas.paste(strip, (x, plot_y + row_start))
                            strip.close()
                        rendered += 1
                    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError):
                        unreadable.add(str(path))
                        draw.rectangle((x, plot_y + row_start, x + column_width - 1,
                                        plot_y + row_start + row_count - 1), fill=UNREADABLE)
                row_start += row_count
            draw.line((x, plot_y, x, plot_y + body_height), fill=BACKGROUND)
        for hour in range(25):
            y = plot_y + round(hour * body_height / 24)
            label = "24:00" if hour == 24 else "{:02d}:00".format(hour)
            draw.text((16, y - 7), label, font=load_font(12), fill=MUTED)
            if hour % 3 == 0:
                draw.line((LEFT, y, panel_right, y), fill=(185, 197, 211), width=1)
        draw.rectangle((LEFT, plot_y, panel_right, plot_y + body_height), outline=(153, 169, 188))
    note = "Strips show typical capture intervals (maximum 1 hour); large gaps stay grey."
    draw.text((LEFT, height - FOOTER + 12), note, font=load_font(12), fill=MUTED)
    details = "Dense captures are sampled to image rows. {:,} undated files omitted; {:,} sampled images unreadable.".format(
        undated, len(unreadable))
    draw.text((LEFT, height - FOOTER + 34), details, font=load_font(12), fill=MUTED)
    if rendered == 0:
        canvas.close()
        raise ValueError("None of the dated images could be read. Check the image paths and file contents.")
    try:
        save_image(canvas, out_file)
    finally:
        canvas.close()
    return True
