#!/usr/bin/env python3
"""
Datawall utilities — dwtools.py (v2)

Exports:
- make_image_box(path_or_image, text="bottom_left", age=True) -> PIL.Image
- InfoModuleVisuals.switch_positions_image(switch_text: str, columns: int = 3) -> PIL.Image

Notes
-----
- `make_image_box` stamps capture time parsed from filenames like `cap_1746734401.jpg`, formats as
  "13:40 20 May 2005", and optionally appends a softer "Taken X ago" string. Supports corner pills
  (on-image) or above/below bands.
- `InfoModuleVisuals.switch_positions_image` builds a grid of big state circles with labels beneath.
  • Status `on` → green circle with "ON"
  • Status `off` → red circle with "OFF"
  • Anything else → blue circle with red "ERROR"
  Layout uses the requested number of columns; rows are added as needed. If no switches are present,
  returns a neutral grey block saying "No Switches in Config".

Both utilities are robust against missing/odd inputs and have sensible visual defaults.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from typing import Optional, Tuple, Union, List

from PIL import Image, ImageDraw, ImageFont

__all__ = ["make_image_box", "InfoModuleVisuals"]

# ---------- SHARED FONT STACK ----------
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "Antonio-Regular.ttf",
]


def _load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    if not text:
        return (0, 0)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

# ============================================================================
# 1) IMAGE BOX UTILITY
# ============================================================================
PAD = 12
PILL_BG = (0, 0, 0, 140)   # translucent black
TEXT_MAIN = (255, 255, 255, 255)
TEXT_SECONDARY = (230, 230, 230, 255)
BAND_BG = (245, 246, 248)
BAND_TEXT = (40, 44, 52)

TITLE_SIZE = 28     # timestamp
SUBTITLE_SIZE = 18  # age


def _parse_ts_from_name(path: str) -> Optional[int]:
    name = os.path.basename(path)
    stem, _dot, _ext = name.partition(".")
    matches = re.findall(r"(\d{9,13})", stem)
    if not matches:
        return None
    ts = int(matches[-1])
    if ts > 10_000_000_000:  # milliseconds
        ts //= 1000
    return ts


def _format_dt_local(ts: int) -> str:
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%H:%M %d %b %Y")


def _format_age(ts: int, now: Optional[datetime] = None) -> str:
    if now is None:
        now = datetime.now()
    then = datetime.fromtimestamp(ts)
    delta = now - then
    seconds = max(0, int(delta.total_seconds()))
    if seconds < 60:
        return "Taken 1 min ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"Taken {minutes} min ago"
    hours = minutes // 60
    rem_min = minutes % 60
    if hours < 24:
        if rem_min:
            return f"Taken {hours} hour and {rem_min} min ago" if hours == 1 else f"Taken {hours} hours and {rem_min} min ago"
        return f"Taken {hours} hour ago" if hours == 1 else f"Taken {hours} hours ago"
    days = hours // 24
    if days < 7:
        return f"Taken {days} day ago" if days == 1 else f"Taken {days} days ago"
    weeks = days // 7
    return f"Taken {weeks} week ago" if weeks == 1 else f"Taken {weeks} weeks ago"


def make_image_box(
    path_or_image: Union[str, Image.Image],
    text: str = "bottom_left",
    age: bool = True,
) -> Image.Image:
    """Load an image and stamp capture time text."""
    if isinstance(path_or_image, Image.Image):
        img = path_or_image.convert("RGB")
        src_path = None
    else:
        src_path = str(path_or_image) if path_or_image is not None else None
        try:
            img = Image.open(src_path).convert("RGB")
        except Exception:
            w, h = 640, 360
            img = Image.new("RGB", (w, h), (235, 238, 242))
            dph = ImageDraw.Draw(img)
            msg = "Image not found" if not src_path else f"Missing: {os.path.basename(src_path)}"
            font = _load_font(20)
            tw, th = _text_size(dph, msg, font)
            dph.text(((w - tw)//2, (h - th)//2), msg, font=font, fill=(120, 126, 134))
            src_path = None

    W, H = img.size
    rgba = img.convert("RGBA")
    draw = ImageDraw.Draw(rgba)

    ts = _parse_ts_from_name(src_path) if src_path else None
    if ts is None:
        main = "Unknown capture time"
        secondary = None
    else:
        main = _format_dt_local(ts)
        secondary = _format_age(ts) if age else None

    title_font = _load_font(TITLE_SIZE)
    sub_font = _load_font(SUBTITLE_SIZE)

    title_w, title_h = _text_size(draw, main, title_font)
    sub_w, sub_h = (0, 0)
    if secondary:
        sub_w, sub_h = _text_size(draw, secondary, sub_font)

    def paste_pill(x: int, y: int) -> None:
        pad_x, pad_y = PAD, PAD
        pill_w = max(title_w, sub_w) + pad_x*2
        pill_h = title_h + (sub_h + 4 if secondary else 0) + pad_y*2
        pill = Image.new("RGBA", (pill_w, pill_h), (0,0,0,0))
        pd = ImageDraw.Draw(pill)
        pd.rounded_rectangle((0,0,pill_w, pill_h), radius=12, fill=PILL_BG)
        pd.text((pad_x, pad_y), main, font=title_font, fill=TEXT_MAIN)
        if secondary:
            pd.text((pad_x, pad_y + title_h + 4), secondary, font=sub_font, fill=TEXT_SECONDARY)
        rgba.alpha_composite(pill, (x, y))

    pos = (text or "").lower().strip()

    if pos in {"top_left", "top_right", "bottom_left", "bottom_right"}:
        pill_w = max(title_w, sub_w) + PAD*2
        pill_h = title_h + (sub_h + 4 if secondary else 0) + PAD*2
        if pos == "top_left":
            px, py = PAD, PAD
        elif pos == "top_right":
            px, py = W - pill_w - PAD, PAD
        elif pos == "bottom_left":
            px, py = PAD, H - pill_h - PAD
        else:
            px, py = W - pill_w - PAD, H - pill_h - PAD
        paste_pill(px, py)
        return rgba.convert("RGB")

    # Above/below bands
    label_h = title_h + (sub_h + 4 if secondary else 0) + PAD*2
    band = Image.new("RGBA", (W, label_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle((0, 0, W, label_h), fill=BAND_BG)
    total_h = title_h + (sub_h + 4 if secondary else 0)
    y0 = (label_h - total_h)//2
    tx = (W - title_w)//2
    bd.text((tx, y0), main, font=title_font, fill=BAND_TEXT)
    if secondary:
        sx = (W - sub_w)//2
        bd.text((sx, y0 + title_h + 4), secondary, font=sub_font, fill=(90, 95, 102))

    out = Image.new("RGBA", (W, H + label_h), (255,255,255,0))
    if pos == "above":
        out.alpha_composite(band, (0, 0))
        out.alpha_composite(rgba, (0, label_h))
    else:  # below or anything else
        out.alpha_composite(rgba, (0, 0))
        out.alpha_composite(band, (0, H))

    return out.convert("RGB")

# ============================================================================
# 2) INFO MODULE VISUALS (Switch Positions)
# ============================================================================
class InfoModuleVisuals:
    """Visual components for info modules.

    Currently: switch positions grid → returns a PIL.Image you can paste in your datawall.
    """

    # Colors
    OK = (0, 180, 120)
    OFF = (220, 68, 68)
    ERR_BG = (50, 115, 245)
    ERR_TXT = (200, 32, 32)
    OUTLINE = (30, 30, 30)
    BG = (255, 255, 255)
    PLACEHOLDER_BG = (232, 235, 238)
    PLACEHOLDER_TXT = (105, 112, 120)

    PAD_X = 18
    PAD_Y = 16

    TITLE_FONT_SIZE = 18  # for labels under circles

    @staticmethod
    def _parse_switches(switch_text: str) -> List[Tuple[str, str]]:
        switches: List[Tuple[str, str]] = []
        if not switch_text:
            return switches
        for line in switch_text.splitlines():
            parts = line.split(" is ")
            if len(parts) == 2:
                name = parts[0].strip()
                status = parts[1].strip().lower()
                if name:
                    switches.append((name, status))
        return switches

    @classmethod
    def switch_positions_image(cls, switch_text: str, columns: int = 3) -> Image.Image:
        """Build a grid of big state circles with labels and return a PIL.Image.

        Args:
            switch_text: text from the `switch_position` info module
            columns: number of columns to use in the grid (>=1)
        """
        columns = max(1, int(columns or 1))
        switches = cls._parse_switches(switch_text)

        if not switches:
            w, h = 640, 200
            img = Image.new("RGB", (w, h), cls.PLACEHOLDER_BG)
            d = ImageDraw.Draw(img)
            font = _load_font(20)
            msg = "No Switches in Config"
            tw, th = _text_size(d, msg, font)
            d.text(((w - tw)//2, (h - th)//2), msg, font=font, fill=cls.PLACEHOLDER_TXT)
            return img

        # Decide intrinsic canvas size. We'll scale in the datawall to available width.
        # Use a base cell width/height; circle diameter adapts to cell width.
        cell_w = 150
        base_pad = 14
        label_font = _load_font(cls.TITLE_FONT_SIZE)

        # compute rows
        n = len(switches)
        rows = (n + columns - 1) // columns

        # Estimate label height (2 lines max if very long names)
        test_draw = ImageDraw.Draw(Image.new("RGB", (1, 1), (255, 255, 255)))
        lh = _text_size(test_draw, "Ag", label_font)[1]
        # row gap slightly larger than inner pad
        row_gap = int(base_pad * 1.1)

        # circle diameter fits within cell with margins
        circle_d = min(110, cell_w - 2*base_pad)
        # cell height = circle + pad + label + extra gap below label
        cell_h = circle_d + base_pad + lh + row_gap

        # total canvas size
        W = columns * cell_w + (columns - 1) * base_pad + cls.PAD_X * 2
        H = rows * cell_h + (rows - 1) * row_gap + cls.PAD_Y * 2

        img = Image.new("RGB", (W, H), cls.BG)
        d = ImageDraw.Draw(img)

        def status_colors(status: str):
            if status == "on":
                return cls.OK, "ON", (255, 255, 255)
            if status == "off":
                return cls.OFF, "OFF", (255, 255, 255)
            # error/unknown
            return cls.ERR_BG, "ERROR", cls.ERR_TXT

        for idx, (name, status) in enumerate(switches):
            r = idx // columns
            c = idx % columns
            x0 = cls.PAD_X + c * (cell_w + base_pad)
            y0 = cls.PAD_Y + r * (cell_h + row_gap)

            # circle box
            cx = x0 + (cell_w - circle_d) // 2
            cy = y0
            circle_box = (cx, cy, cx + circle_d, cy + circle_d)

            fill, status_text, status_color = status_colors(status)
            d.ellipse(circle_box, fill=fill, outline=cls.OUTLINE, width=2)

            # status text centered in circle
            stat_font = _load_font(22)
            sw, sh = _text_size(d, status_text, stat_font)
            d.text((cx + (circle_d - sw)//2, cy + (circle_d - sh)//2), status_text, font=stat_font, fill=status_color)

            # label under circle, centered; wrap to 2 lines if long
            name_max_w = cell_w - 8
            # naive two-line wrap
            words = name.split()
            lines: List[str] = []
            cur = ""
            for w_ in words:
                test = (cur + " " + w_) if cur else w_
                if _text_size(d, test, label_font)[0] <= name_max_w:
                    cur = test
                else:
                    if cur:
                        lines.append(cur)
                    cur = w_
            if cur:
                lines.append(cur)
            if len(lines) > 2:
                lines = lines[:2]
                # add ellipsis to 2nd line if needed
                while _text_size(d, lines[-1] + "…", label_font)[0] > name_max_w and len(lines[-1]) > 0:
                    lines[-1] = lines[-1][:-1]
                lines[-1] += "…"

            ty = cy + circle_d + base_pad
            for li, line in enumerate(lines or [name]):
                lw, lh_ = _text_size(d, line, label_font)
                d.text((x0 + (cell_w - lw)//2, ty), line, font=label_font, fill=(35, 38, 42))
                ty += lh_

        return img
