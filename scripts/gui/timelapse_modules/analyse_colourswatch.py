"""A bounded, labelled strip showing full-frame color changes in set order."""

import numpy as np
from PIL import Image, ImageDraw

from timelapse_modules.analysis_common import (
    load_font, load_thumbnail, require_frames, save_image,
)


WIDTH, HEIGHT = 1600, 680
LEFT, RIGHT = 90, 1530
TOP, STRIP_HEIGHT = 142, 340
AVERAGE_TOP, AVERAGE_HEIGHT = 510, 42
MISSING = (212, 217, 224)
ERROR_COLOR = (197, 42, 132)
_IMAGE_ERRORS = (OSError, ValueError, SyntaxError, Image.DecompressionBombError)


def analyse_set(ani_frame_list, out_file):
    frames = require_frames(ani_frame_list)
    bins = min(len(frames), RIGHT - LEFT)
    sums = np.zeros((bins, STRIP_HEIGHT, 3), dtype=np.float32)
    counts = np.zeros(bins, dtype=np.int64)
    failures = np.zeros(bins, dtype=np.int64)
    for index, image_path in enumerate(frames):
        column = min(bins - 1, index * bins // len(frames))
        try:
            with load_thumbnail(image_path, (128, 384)) as image:
                # Average across the FULL frame width, retaining vertical detail.
                with image.resize((1, STRIP_HEIGHT), Image.Resampling.BOX) as profile:
                    sums[column] += np.asarray(profile, dtype=np.float32)[:, 0]
        except _IMAGE_ERRORS:
            failures[column] += 1
        else:
            counts[column] += 1
        if (index + 1) % 500 == 0:
            print("Swatch: {:,} / {:,} images".format(index + 1, len(frames)))
    failed = int(failures.sum())
    if failed == len(frames):
        raise ValueError("None of the selected images could be read. Check that the files exist and are valid images.")

    values = np.full((STRIP_HEIGHT, bins, 3), MISSING, dtype=np.uint8)
    valid = counts > 0
    values[:, valid] = np.clip(sums[valid] / counts[valid, None, None], 0, 255).astype(np.uint8).transpose(1, 0, 2)
    result = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(result)
    title_font, font, small = load_font(30), load_font(18), load_font(16)
    draw.text((LEFT, 25), "Color swatch through the image set", font=title_font, fill="#203045")
    draw.text((LEFT, 72), "{:,} frames in set order · full image width squeezed into each strip; vertical detail retained".format(len(frames)), font=font, fill="#526273")
    grouping = ("Each strip represents one frame." if bins == len(frames) else
                "{:,} strips average consecutive groups of {:,}–{:,} frames; all frames are processed.".format(
                    bins, len(frames) // bins, (len(frames) + bins - 1) // bins))
    draw.text((LEFT, 101), grouping, font=small, fill="#526273")
    with Image.fromarray(values) as strip:
        with strip.resize((RIGHT - LEFT, STRIP_HEIGHT), Image.Resampling.NEAREST) as scaled:
            result.paste(scaled, (LEFT, TOP))
    average = np.rint(values.astype(np.float32).mean(axis=0)).astype(np.uint8)[None, :, :]
    with Image.fromarray(average) as strip:
        with strip.resize((RIGHT - LEFT, AVERAGE_HEIGHT), Image.Resampling.NEAREST) as scaled:
            result.paste(scaled, (LEFT, AVERAGE_TOP))
    draw.rectangle((LEFT - 1, TOP - 1, RIGHT, TOP + STRIP_HEIGHT), outline="#9daab8")
    draw.rectangle((LEFT - 1, AVERAGE_TOP - 1, RIGHT, AVERAGE_TOP + AVERAGE_HEIGHT), outline="#9daab8")
    draw.text((LEFT, 487), "Mean color", font=small, fill="#526273")
    if bins <= 80:
        for index in range(1, bins):
            xpos = LEFT + index * (RIGHT - LEFT) // bins
            draw.line((xpos, TOP, xpos, TOP + STRIP_HEIGHT), fill=(255, 255, 255), width=1)
    for index in np.flatnonzero(failures):
        x1 = LEFT + int(index) * (RIGHT - LEFT) // bins
        x2 = LEFT + (int(index) + 1) * (RIGHT - LEFT) // bins - 1
        draw.rectangle((x1, TOP + STRIP_HEIGHT - 7, max(x1, x2), TOP + STRIP_HEIGHT - 1), fill=ERROR_COLOR)
    tick_frames = sorted(set(int(round(value)) for value in np.linspace(1, len(frames), min(6, len(frames)))))
    for number in tick_frames:
        xpos = LEFT + (number - 0.5) * (RIGHT - LEFT) / len(frames)
        draw.line((int(xpos), AVERAGE_TOP + AVERAGE_HEIGHT, int(xpos), AVERAGE_TOP + AVERAGE_HEIGHT + 7), fill="#536477")
        label = format(number, ",")
        box = draw.textbbox((0, 0), label, font=small)
        label_width = box[2] - box[0]
        draw.text((min(RIGHT - label_width, max(LEFT, xpos - label_width / 2)), 565), label, font=small, fill="#35465a")
    draw.text((LEFT, 594), "Frame number (set order)", font=font, fill="#35465a")
    note = ("{:,} unreadable images: magenta marks affected strips; grey strips have no readable image.".format(failed)
            if failed else "Color transitions reveal lighting, subject and camera changes. Click the preview to inspect the full image.")
    draw.text((LEFT, 635), note, font=small, fill="#8b225e" if failed else "#526273")
    save_image(result, out_file)
    return True
