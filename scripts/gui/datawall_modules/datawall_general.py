#!/usr/bin/env python3
"""
Datawall+ (dwtools integrated)
- Uses dwtools.make_image_box() to render the "recent" image (timestamp + age) in the FULL top-left column.
- Fixes undefined vars (e.g., right_x) and removes any stray typos like card_G.
- Keeps the cleaner card UI and graceful fallbacks everywhere else.

Drop-in
-------
from datawall_plus import read_datawall_options, make_datawall

Requires dwtools.py in the same folder:
from dwtools import make_image_box
"""
from __future__ import annotations

import os
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
from dwtools import make_image_box, InfoModuleVisuals

# --------------------------
# THEME & LAYOUT
# --------------------------
DW_WIDTH = 1024
BG_COLOR = (242, 243, 239)         # light canvas
FG_COLOR = (28, 28, 30)            # near-black
MUTED = (98, 104, 110)
ACCENT = (34, 139, 230)            # blue accent
OK = (32, 178, 170)                # teal OK
WARN = (255, 165, 0)               # amber warn
BAD = (220, 53, 69)                # red bad
NEUTRAL = (160, 164, 168)
CARD_BG = (255, 255, 255)
BORDER = (225, 228, 232)
SHADOW = (0, 0, 0, 60)
RADIUS = 16
PADDING = 20
GUTTER = 16
LINE_SPACING = 6

TITLE_SIZE = 40
SUBTITLE_SIZE = 24
TEXT_SIZE = 18
SMALL_SIZE = 14

MAX_LOG_LINES = 10

# --------------------------
# OPTIONS & PRESET REQUESTS
# --------------------------
def read_datawall_options():
    module_settings_dict = {"font_size": "18"}
    preset_req = {
        "info_read": [
            "boxname",
            "datetime",
            "check_lamp",
            "power_warnings",
            "diskusage percent_only=true",
            "switch_position",
            "switch_log  duration=day7",
            "error_log",
        ],
        "graphs": [("temp", "weeksagemoss")],
        "logs": [("temphumid", "sibothmon")],
        "pictures": [("recent", "recent")],
    }
    return module_settings_dict, preset_req

# --------------------------
# FONT LOADER
# --------------------------
FONT_CANDIDATES = [
    "Antonio-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

# --------------------------
# DRAW HELPERS
# --------------------------
def rounded_rectangle(draw: ImageDraw.ImageDraw, xy: Tuple[int,int,int,int], fill, outline=None, width=1, radius=RADIUS):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def drop_shadow(base: Image.Image, rect: Tuple[int,int,int,int], blur=8, spread=2):
    from PIL import ImageFilter
    x1, y1, x2, y2 = rect
    w, h = base.size
    shadow = Image.new("RGBA", (w, h), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    for i in range(spread):
        sd.rounded_rectangle([x1-i, y1-i, x2+i, y2+i], radius=RADIUS+i, fill=SHADOW)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(shadow)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int,int]:
    bbox = draw.textbbox((0,0), text, font=font)
    return bbox[2]-bbox[0], bbox[3]-bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    words = text.split(" ") if text else []
    if not words:
        return []
    lines, line = [], ""
    for word in words:
        test = (line + " " + word) if line else word
        if text_size(draw, test, font)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def wrap_ellipsis(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int, max_lines: int) -> List[str]:
    if not text:
        return []
    raw = wrap_text(draw, text, font, max_width)
    if len(raw) <= max_lines:
        return raw
    clipped = raw[:max_lines]
    last = clipped[-1]
    while text_size(draw, last + "…", font)[0] > max_width and len(last) > 0:
        last = last[:-1]
    clipped[-1] = last + "…"
    return clipped


def grid_positions(x: int, y: int, w: int, item_w: int, h: int, item_h: int, gap: int):
    cx, cy = x, y
    while cy + item_h <= y + h:
        if cx + item_w <= x + w:
            yield (cx, cy)
            cx += item_w + gap
        else:
            cx = x
            cy += item_h + gap


def safe_float(x: Any, default=0.0) -> float:
    try:
        if isinstance(x, str) and x.strip().endswith('%'):
            return float(x.strip().strip('%'))
        return float(x)
    except Exception:
        return default


def draw_progress_bar(draw: ImageDraw.ImageDraw, xy: Tuple[int,int,int,int], pct: float):
    x1,y1,x2,y2 = xy
    rounded_rectangle(draw, xy, fill=(255,255,255), outline=BORDER, width=1, radius=12)
    width = x2 - x1
    filled = int(width * max(0,min(pct,100))/100)
    color = OK if pct < 75 else (WARN if pct < 90 else BAD)
    rounded_rectangle(draw, (x1, y1, x1+filled, y2), fill=color, radius=12)
    if pct >= 98:
        step = 10
        for i in range(x1, x1+filled, step):
            draw.line((i, y1, i+6, y2), fill=(255,255,255), width=2)

# --------------------------
# MAIN ENTRY
# --------------------------

def make_datawall(data: Dict[str, Any], opts: Optional[Dict[str, Any]] = None) -> str:
    opts = opts or {}

    try:
        RESAMPLE = Image.Resampling.LANCZOS
    except AttributeError:
        RESAMPLE = Image.LANCZOS

    # fonts
    title_font = load_font(TITLE_SIZE)
    subtitle_font = load_font(SUBTITLE_SIZE)
    text_font = load_font(int(opts.get("font_size", TEXT_SIZE)))
    small_font = load_font(SMALL_SIZE)

    # unpack data safely
    info = data.get("info", {}) or {}
    images = data.get("images", {}) or {}
    graphs = data.get("graphs", {}) or {}
    log_data = data.get("data", {}) or {}

    boxname = str(info.get("boxname", "Datawall"))
    dt_text = str(info.get("datetime", ""))
    check_lamp = str(info.get("check_lamp", ""))
    power_warn = str(info.get("power_warnings", ""))
    diskusage_raw = info.get("diskusage percent_only=true", "")
    switch_pos = str(info.get("switch_position", ""))
    switch_log = str(info.get("switch_log  duration=day7", ""))
    error_log = str(info.get("error_log", ""))

    recent_image_path = images.get("recent")
    graph_image_path = graphs.get("temp")

    dataset_list = log_data.get("temphumid") or []

    # canvas
    W = DW_WIDTH
    H = 2200
    base = Image.new("RGBA", (W, H), BG_COLOR + (255,))
    d = ImageDraw.Draw(base)

    y = PADDING

    # HEADER
    tw, th = text_size(d, boxname, title_font)
    d.text(((W - tw)//2, y), boxname, font=title_font, fill=FG_COLOR)
    y += th + 8
    if dt_text:
        sw, sh = text_size(d, dt_text, subtitle_font)
        d.text(((W - sw)//2, y), dt_text, font=subtitle_font, fill=MUTED)
        y += sh
    y += PADDING

    # --------------------------
    # ROW 1 — LEFT: recent image uses FULL left column area (no inner padding)
    #          RIGHT: info card (matched height to left for a tidy row)
    # --------------------------
    col_w = (W - (PADDING*2) - GUTTER) // 2
    left_x = PADDING
    right_x = left_x + col_w + GUTTER

    # Left: build stamped image
    stamped = make_image_box(recent_image_path, text="bottom_left", age=True)
    sw, sh = stamped.size
    new_h = int(sh * (col_w / sw)) if sw else 0
    if new_h <= 0:
        new_h = 220
    stamped = stamped.resize((col_w, new_h), resample=RESAMPLE)

    left_rect = (left_x, y, left_x + col_w, y + new_h)
    drop_shadow(base, left_rect)
    rounded_rectangle(d, left_rect, fill=CARD_BG, outline=BORDER)
    base.paste(stamped, (left_x, y))

    # Right: info card, match left height
    info_card_h = max(220, new_h)
    right_rect = (right_x, y, right_x + col_w, y + info_card_h)
    drop_shadow(base, right_rect)
    rounded_rectangle(d, right_rect, fill=CARD_BG, outline=BORDER)

    info_x = right_x + PADDING
    info_y = y + PADDING
    info_w = col_w - 2*PADDING

    items = [
        ("Check Lamp", check_lamp),
        ("Power", power_warn),
        ("Disk", None),  # custom bar
    ]

    for label, val in items:
        dw_, dh_ = text_size(d, label + ":", text_font)
        d.text((info_x, info_y), label + ":", font=text_font, fill=FG_COLOR)
        if label == "Disk":
            pct = safe_float(diskusage_raw, 0.0)
            bar_h = max(18, SMALL_SIZE+6)
            bar_rect = (info_x + dw_ + 8, info_y + (dh_-bar_h)//2, info_x + dw_ + 8 + 180, info_y + (dh_-bar_h)//2 + bar_h)
            draw_progress_bar(d, bar_rect, pct)
            pct_txt = f"{pct:.0f}%"
            pw, ph = text_size(d, pct_txt, small_font)
            d.text((bar_rect[0] + (bar_rect[2]-bar_rect[0]-pw)//2, bar_rect[1] + (bar_rect[3]-bar_rect[1]-ph)//2), pct_txt, font=small_font, fill=(0,0,0))
        else:
            val = (val or "").strip() or "—"
            lines = wrap_ellipsis(d, val, text_font, max_width=info_w - dw_ - 12, max_lines=2)
            d.text((info_x + dw_ + 8, info_y), "\n".join(lines), font=text_font, fill=MUTED)
        info_y += dh_ + 10

    y = y + max(new_h, info_card_h) + PADDING

    # --------------------------
    # ROW 2 — LEFT: High/Low + Switch chips  |  RIGHT: Graph (or sparkline fallback)
    # --------------------------
    left_top = y

    # LEFT CONTENT
    left_rect2 = (left_x, left_top, left_x + col_w, left_top)  # end y set later
    content_y = left_top + PADDING

    # High/Low block
    hl_title = "High/Low"
    d.text((left_x + PADDING, content_y), hl_title, font=text_font, fill=FG_COLOR)
    content_y += text_size(d, hl_title, text_font)[1] + 6

    hl_lines: List[str] = []
    if dataset_list:
        for ds in dataset_list:
            key = str(ds.get("key", "—"))
            tuples = ds.get("trimmed_data", []) or []
            values = [v for _, v in tuples if isinstance(v, (int, float))]
            if values:
                hi, lo = max(values), min(values)
                hl_lines += [f"{key}", f"High: {hi}", f"Low: {lo}"]
            else:
                hl_lines += [f"{key}", "High: —", "Low: —"]
            hl_lines.append("")
    else:
        hl_lines = ["No dataset found"]

    for line in hl_lines:
        d.text((left_x + PADDING, content_y), line, font=small_font if line and not line.endswith(':') and not line.startswith('High') and not line.startswith('Low') else text_font, fill=MUTED)
        content_y += text_size(d, line if line else " ", text_font)[1] + 2

    content_y += 6

    # Switch positions
    # d.text((left_x + PADDING, content_y), "Switch Positions", font=text_font, fill=FG_COLOR)
    # content_y += text_size(d, "Switch Positions", text_font)[1] + 8
    #
    # switches: List[Tuple[str, str]] = []
    # for raw in (switch_pos or "").splitlines():
    #     parts = raw.split(" is ")
    #     if len(parts) == 2:
    #         name, status = parts[0].strip(), parts[1].strip().lower()
    #         if name:
    #             switches.append((name, status))
    #
    # chip_w, chip_h = 110, 44
    # grid_h = 4*chip_h + 3*8
    # area_x, area_y = left_x + PADDING, content_y
    #
    # # Lay out chips by index mapping over generated positions
    # idx = 0
    # for gx, gy in grid_positions(area_x, area_y, col_w - 2*PADDING, chip_w, grid_h, chip_h, gap=8):
    #     if idx >= len(switches):
    #         break
    #     name, status = switches[idx]
    #     idx += 1
    #     color = OK if status == 'on' else (BAD if status == 'off' else NEUTRAL)
    #     rounded_rectangle(d, (gx, gy, gx+chip_w, gy+chip_h), fill=(247,248,250), outline=BORDER, radius=12)
    #     dot_r = 7
    #     d.ellipse((gx+10-dot_r, gy+chip_h//2-dot_r, gx+10+dot_r, gy+chip_h//2+dot_r), fill=color)
    #     label = f"{name} · {status.upper()}" if status else name
    #     d.text((gx+24, gy + (chip_h - text_size(d, label, small_font)[1])//2), label, font=small_font, fill=FG_COLOR)
    #
    # left_end_y = max(area_y + grid_h, content_y + 4) + PADDING
    # left_rect2 = (left_x, left_top, left_x + col_w, left_end_y)
    # drop_shadow(base, left_rect2)
    # rounded_rectangle(d, left_rect2, fill=None, outline=BORDER)



    # After drawing the High/Low section:
    content_y += PADDING  # pad, item1, pad

    # Build the switch positions image (choose column count; or make it configurable via opts)
    switch_cols = int(opts.get("switch_cols", 4))
    sp_img = InfoModuleVisuals.switch_positions_image(switch_pos, columns=switch_cols)

    # Scale to fill available width while maintaining aspect ratio
    avail_w = col_w - 2 * PADDING
    try:
        RESAMPLE = Image.Resampling.LANCZOS
    except AttributeError:
        RESAMPLE = Image.LANCZOS

    iw, ih = sp_img.size
    if iw == 0:
        iw = 1
    new_h = int(ih * (avail_w / iw))
    sp_img = sp_img.resize((avail_w, new_h), resample=RESAMPLE)

    # Paste into the left card
    base.paste(sp_img, (left_x + PADDING, content_y))
    content_y += new_h

    # Bottom pad
    content_y += PADDING

    # Now finalize the left card frame/height
    left_end_y = content_y
    left_rect2 = (left_x, left_top, left_x + col_w, left_end_y)
    drop_shadow(base, left_rect2)
    rounded_rectangle(d, left_rect2, fill=None, outline=BORDER)



    # RIGHT CONTENT (graph or fallback)
    right_top = y
    gx0, gy0 = right_x + PADDING, right_top + PADDING
    d.text((gx0, gy0), "Graph", font=text_font, fill=FG_COLOR)
    gy0 += text_size(d, "Graph", text_font)[1] + 8

    # Try to load external graph image to a neat box
    def load_image_letterbox(path: Optional[str], target_w: int, target_h: int) -> Optional[Image.Image]:
        if not path or not os.path.isfile(path):
            return None
        try:
            img = Image.open(path).convert("RGB")
            ow, oh = img.size
            ratio = min(target_w/ow, target_h/oh)
            nw, nh = int(ow*ratio), int(oh*ratio)
            resized = img.resize((nw, nh), resample=RESAMPLE)
            canvas = Image.new("RGB", (target_w, target_h), (247,248,250))
            canvas.paste(resized, ((target_w-nw)//2, (target_h-nh)//2))
            return canvas
        except Exception:
            return None

    area_w, area_h = col_w - 2*PADDING, 220
    graph_img = load_image_letterbox(graph_image_path, area_w, area_h)

    if graph_img is not None:
        base.paste(graph_img, (gx0, gy0))
        gy0 += area_h
    else:
        # simple sparkline fallback
        rounded_rectangle(d, (gx0, gy0, gx0+area_w, gy0+area_h), fill=(247,248,250), outline=BORDER, radius=12)
        series = None
        for ds in dataset_list:
            tuples = ds.get("trimmed_data", []) or []
            vals = [v for _, v in tuples if isinstance(v, (int,float))]
            if len(vals) >= 2:
                series = vals
                break
        if series:
            mn, mx = min(series), max(series)
            rng = (mx - mn) or 1.0
            px1, py1, px2, py2 = gx0+16, gy0+16, gx0+area_w-16, gy0+area_h-16
            d.line((px1, py2, px2, py2), fill=BORDER, width=1)
            for i in range(len(series)-1):
                t1 = i/(len(series)-1)
                t2 = (i+1)/(len(series)-1)
                x1 = int(px1 + t1*(px2-px1))
                x2 = int(px1 + t2*(px2-px1))
                y1 = int(py2 - ((series[i]-mn)/rng)*(py2-py1))
                y2 = int(py2 - ((series[i+1]-mn)/rng)*(py2-py1))
                d.line((x1, y1, x2, y2), fill=ACCENT, width=2)
        else:
            msg = "No graph data"
            mw, mh = text_size(d, msg, text_font)
            d.text((gx0 + (area_w-mw)//2, gy0 + (area_h-mh)//2), msg, font=text_font, fill=NEUTRAL)
        gy0 += area_h

    right_end_y = gy0 + PADDING
    right_rect2 = (right_x, right_top, right_x + col_w, right_end_y)
    drop_shadow(base, right_rect2)
    rounded_rectangle(d, right_rect2, fill=None, outline=BORDER)

    y = max(left_end_y, right_end_y) + PADDING

    # --------------------------
    # ROW 3 — Logs
    # --------------------------
    half_w = (W - (PADDING*2) - GUTTER) // 2

    def draw_log_card(x: int, top: int, title: str, body: str) -> int:
        cx, cy = x + PADDING, top + PADDING
        d.text((cx, cy), title, font=text_font, fill=FG_COLOR)
        cy += text_size(d, title, text_font)[1] + 8
        lines = wrap_ellipsis(d, body, small_font, max_width=half_w - 2*PADDING, max_lines=MAX_LOG_LINES)
        if not lines:
            lines = ["—"]
        for ln in lines:
            d.text((cx, cy), ln, font=small_font, fill=MUTED)
            cy += text_size(d, ln, small_font)[1] + 2
        cy += PADDING
        rect = (x, top, x + half_w, cy)
        drop_shadow(base, rect)
        rounded_rectangle(d, rect, fill=None, outline=BORDER)
        return cy

    y1 = draw_log_card(PADDING, y, "Switch Log", switch_log)
    y2 = draw_log_card(PADDING + half_w + GUTTER, y, "Error Log", error_log)

    y = max(y1, y2) + PADDING

    # crop & save
    out_h = min(H, y)
    final = base.crop((0, 0, W, out_h))
    output_path = opts.get("output", "./test_datawall.png")
    try:
        final.convert("RGB").save(output_path)
    except Exception as e:
        print("Error saving datawall image:", e)
        return ""
    return output_path

if __name__ == "__main__":
    sample = {
        "info": {
            "boxname": "Pigrow — Moss Corner",
            "datetime": "2025-09-05 14:12",
            "check_lamp": "Lamp OK (12h cycle)",
            "power_warnings": "Battery low overnight <11.8V",
            "diskusage percent_only=true": "83",
            "switch_position": "grow_lights is on\nfogger is off\ncam_night is on",
            "switch_log  duration=day7": "[12:01] grow_lights -> ON\n[22:10] grow_lights -> OFF …",
            "error_log": "(none)",
        },
        "images": {},
        "graphs": {},
        "data": {
            "temphumid": [
                {"key": "tempC", "trimmed_data": [(0, 18.2), (1, 19.1), (2, 20.0), (3, 19.4)]},
                {"key": "humid%", "trimmed_data": [(0, 68), (1, 71), (2, 69), (3, 72)]},
            ]
        },
    }
    print(make_datawall(sample))

