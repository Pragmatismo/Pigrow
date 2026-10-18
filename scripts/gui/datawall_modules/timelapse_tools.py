"""Shared, GUI-independent rendering for timelapse datawall modules.

The remote info module owns scanning and image selection. These renderers only
consume its JSON and images downloaded by the datawall importer; they never
open capture folders or make network requests themselves.
"""

from datetime import datetime, timezone
import io
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps


WIDTH = 1200
PAD = 28
GAP = 16
BG = (238, 242, 246)
CARD = (255, 255, 255)
INK = (28, 43, 58)
MUTED = (91, 108, 124)
BLUE = (34, 104, 178)
GREEN = (28, 126, 95)
AMBER = (162, 100, 18)
RED = (174, 56, 56)
BORDER = (216, 224, 233)


def font(size):
    for filename in (
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(filename, size)
        except OSError:
            pass
    return ImageFont.load_default()


def number(value):
    """Return a finite numeric value, preserving missing metadata as unknown."""
    if value is None or isinstance(value, bool):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError, OverflowError):
        return None


def count(value):
    value = number(value)
    return "Unavailable" if value is None else format(int(value), ",")


def byte_size(value):
    value = number(value)
    if value is None:
        return "Unavailable"
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(value) < 1024 or unit == "TiB":
            return "{:.1f} {}".format(value, unit)
        value /= 1024


def duration(value):
    value = number(value)
    if value is None:
        return "Unavailable"
    value = max(0, int(value))
    if value < 60:
        return "{}s".format(value)
    if value < 3600:
        return "{}m {}s".format(value // 60, value % 60)
    if value < 86400:
        return "{}h {}m".format(value // 3600, value % 3600 // 60)
    return "{}d {}h".format(value // 86400, value % 86400 // 3600)


def time_label(value):
    value = number(value)
    if value is None:
        return "Unavailable"
    try:
        return datetime.fromtimestamp(value, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (OverflowError, OSError, ValueError):
        return "Unavailable"


def read_report(data):
    """The importer stores responses under the complete info command."""
    info = data.get("info") or {}
    for command, value in info.items():
        if str(command).strip().split(" ", 1)[0] != "timelapse":
            continue
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (ValueError, TypeError):
                return {"error": "Timelapse information could not be read: " + value[:400]}
        if isinstance(value, dict):
            return value
        return {"error": "Timelapse information has an unsupported format."}
    return {"error": "No timelapse information was imported. Import the datawall preset again."}


def text_lines(draw, text, face, width, limit=None):
    """Wrap paths and long words as well as ordinary text, with bounded output."""
    lines = []
    for paragraph in str(text).splitlines() or [""]:
        line = ""
        for word in paragraph.split():
            proposed = (line + " " + word).strip()
            if draw.textlength(proposed, font=face) <= width:
                line = proposed
                continue
            if line:
                lines.append(line)
                line = ""
            for char in word:
                if line and draw.textlength(line + char, font=face) > width:
                    lines.append(line)
                    line = ""
                line += char
        lines.append(line)
    if limit and len(lines) > limit:
        lines = lines[:limit]
        while lines[-1] and draw.textlength(lines[-1] + "...", font=face) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "..."
    return lines


def draw_text(draw, text, x, y, width, size=19, color=INK, limit=None):
    face = font(size)
    for line in text_lines(draw, text, face, width, limit):
        draw.text((x, y), line, font=face, fill=color)
        y += size + 8
    return y


def card(draw, box):
    draw.rounded_rectangle(box, radius=13, fill=CARD, outline=BORDER)


def summary_rows(report):
    summary = report.get("summary") or {}
    interval = number(summary.get("interval_seconds"))
    schedule = summary.get("schedule_description")
    if not schedule:
        schedule = "Every " + duration(interval) if interval is not None else "Schedule unavailable"
    start = summary.get("window_start_label") or time_label(summary.get("window_start"))
    source = summary.get("start_source") or summary.get("window_source")
    if source:
        start += " ({})".format(source)
    first = summary.get("first_label") or time_label(summary.get("first_timestamp"))
    last = summary.get("last_label") or time_label(summary.get("last_timestamp"))
    return [
        ("Capture folder", report.get("path") or "Unavailable"),
        ("Schedule", schedule),
        ("Counting from", start),
        ("First image", first),
        ("Latest image", last + "  |  Age: " + duration(summary.get("latest_age_seconds"))),
        ("Folder totals", "{} images  |  {}  |  Missing: {}  |  Extra: {}".format(
            count(summary.get("image_count")), byte_size(summary.get("total_bytes")),
            count(summary.get("missing_count")), count(summary.get("extra_count")))),
    ]


def draw_summary(base, data, report, detailed):
    draw = ImageDraw.Draw(base)
    summary = report.get("summary") or {}
    info = data.get("info") or {}
    y = PAD
    y = draw_text(draw, str(info.get("boxname") or "Pigrow") + " / Timelapse", PAD, y,
                  WIDTH - 2 * PAD, 32, limit=2)
    timestamp = report.get("generated_label") or info.get("datetime") or ""
    subtitle = ("Detailed capture report" if detailed else "Fast capture status")
    if timestamp:
        subtitle += "  |  " + str(timestamp)
    y = draw_text(draw, subtitle, PAD, y, WIDTH - 2 * PAD, 18, MUTED, limit=2) + 10

    status = str(summary.get("status") or "unknown").lower()
    status_text = {
        "complete": "On schedule", "behind": "Fewer captures than expected",
        "extra": "More captures than expected", "empty": "No capture images found",
        "unknown": "Expected count unavailable", "error": "Capture information unavailable",
    }.get(status, status.replace("_", " ").capitalize())
    if report.get("error"):
        status_text = "Capture information unavailable"
        status = "error"
    color = GREEN if status == "complete" else RED if status == "error" else AMBER
    y = draw_text(draw, status_text, PAD, y, WIDTH - 2 * PAD, 24, color, limit=2) + 12

    completion = number(summary.get("completion_percent"))
    stats = [
        ("CAPTURED IN WINDOW", count(summary.get("actual_count"))),
        ("EXPECTED IN WINDOW", count(summary.get("expected_count"))),
        ("COMPLETENESS", "Unavailable" if completion is None else "{:.1f}%".format(completion)),
    ]
    width = (WIDTH - 2 * PAD - 2 * GAP) // 3
    for index, (label, value) in enumerate(stats):
        x = PAD + index * (width + GAP)
        card(draw, (x, y, x + width, y + 110))
        draw_text(draw, label, x + 18, y + 14, width - 36, 15, MUTED)
        draw_text(draw, value, x + 18, y + 44, width - 36, 29, BLUE, limit=1)
    y += 110 + GAP

    row_sizes = []
    for label, value in summary_rows(report):
        wrapped = text_lines(draw, value, font(18), WIDTH - 240 - PAD * 2, 3)
        row_sizes.append((label, wrapped, max(34, len(wrapped) * 26 + 9)))
    card(draw, (PAD, y, WIDTH - PAD, y + sum(row[2] for row in row_sizes) + 24))
    y += 12
    for label, wrapped, height in row_sizes:
        draw_text(draw, label, PAD + 16, y, 205, 18, MUTED)
        draw_text(draw, "\n".join(wrapped), PAD + 224, y, WIDTH - PAD * 2 - 240, 18)
        y += height
    y += 12 + GAP

    warnings = summary.get("warnings") or []
    if isinstance(warnings, str):
        warnings = [warnings]
    else:
        warnings = list(warnings)
    if report.get("error"):
        warnings.insert(0, str(report["error"]))
    if detailed:
        image_errors = data.get("image_errors") or {}
        if image_errors:
            warnings.append("Some photographs could not be downloaded; their slots show placeholders.")
    for warning in warnings[:8]:
        y = draw_text(draw, "Note: " + str(warning), PAD + 4, y,
                      WIDTH - 2 * PAD - 8, 17, AMBER, limit=3) + 3
    return y


def photo_box(base, path, box, empty_text="No image for this period"):
    """Fit without cropping and tolerate missing, stale or corrupt downloads."""
    x, y, right, bottom = box
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=10, fill=(222, 229, 236), outline=BORDER)
    try:
        if not path or str(path).lower() == "none":
            raise OSError("No downloaded image")
        with Image.open(path) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((right - x - 2, bottom - y - 2), Image.Resampling.LANCZOS)
            base.paste(image, (x + (right - x - image.width) // 2,
                               y + (bottom - y - image.height) // 2))
        return True
    except (OSError, ValueError, TypeError, Image.DecompressionBombError):
        draw_text(draw, empty_text, x + 12, y + max(8, (bottom - y) // 2 - 28),
                  right - x - 24, 17, MUTED, limit=3)
        return False


def graph_image(report, width=WIDTH - 2 * PAD, height=340):
    """Use Agg directly so rendering never changes pyplot or GUI backends."""
    valid = []
    for point in report.get("points") or []:
        if not isinstance(point, dict):
            continue
        timestamp, size = number(point.get("timestamp")), number(point.get("size"))
        if timestamp is not None and size is not None and size >= 0:
            try:
                dt = datetime.fromtimestamp(timestamp, timezone.utc)
                valid.append((timestamp, dt, size))
            except (ValueError, OverflowError, OSError):
                pass
    if not valid:
        result = Image.new("RGB", (width, height), CARD)
        draw_text(ImageDraw.Draw(result), "No file size or capture time data available",
                  25, height // 2 - 15, width - 50, 21, MUTED)
        return result
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
        from matplotlib.figure import Figure

        valid.sort(key=lambda item: item[0])
        fig = Figure(figsize=(width / 100, height / 100), dpi=100, facecolor="white")
        canvas = FigureCanvasAgg(fig)
        size_ax, gap_ax = fig.subplots(1, 2)
        dates = [point[1] for point in valid]
        sizes = [point[2] / 1024 for point in valid]
        size_ax.plot(dates, sizes, color="#2268b2", linewidth=1.2, marker=".", markersize=3)
        size_ax.set_title("Image file size over time", loc="left", fontsize=11)
        size_ax.set_ylabel("File size (KiB)", fontsize=9)
        size_ax.set_ylim(bottom=0)

        if len(valid) > 1:
            intervals = [(valid[i][0] - valid[i - 1][0]) / 60 for i in range(1, len(valid))]
            gap_ax.plot(dates[1:], intervals, color="#1c7e5f", linewidth=1.2, marker=".", markersize=3)
        else:
            gap_ax.text(0.5, 0.5, "Need two captures to show intervals", ha="center", va="center",
                        transform=gap_ax.transAxes, fontsize=9)
        expected = number((report.get("summary") or {}).get("interval_seconds"))
        if expected is not None and expected > 0:
            gap_ax.axhline(expected / 60, color="#a26412", linestyle="--", label="Expected interval")
            gap_ax.legend(loc="upper left", fontsize=8)
        gap_ax.set_title("Time between captures", loc="left", fontsize=11)
        gap_ax.set_ylabel("Interval (minutes)", fontsize=9)
        gap_ax.set_ylim(bottom=0)

        for axis in (size_ax, gap_ax):
            locator = AutoDateLocator(minticks=3, maxticks=5, tz=timezone.utc)
            axis.xaxis.set_major_locator(locator)
            axis.xaxis.set_major_formatter(ConciseDateFormatter(locator, tz=timezone.utc))
            axis.set_xlabel("Capture time (UTC)", fontsize=9)
            axis.tick_params(labelsize=8)
            axis.grid(True, alpha=0.18)
            axis.spines[["top", "right"]].set_visible(False)
        fig.tight_layout(pad=1.8)
        buffer = io.BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)
        with Image.open(buffer) as graph:
            return graph.convert("RGB")
    except ImportError:
        result = Image.new("RGB", (width, height), CARD)
        draw_text(ImageDraw.Draw(result), "Install matplotlib to display capture history graphs",
                  25, height // 2 - 15, width - 50, 21, MUTED)
        return result


def draw_detail(base, data, report, y):
    draw = ImageDraw.Draw(base)
    images = data.get("images") or {}
    metadata = report.get("datawall_images") or {}
    latest = report.get("latest") or metadata.get("timelapse_latest") or {}
    if not latest:
        points = report.get("points") or []
        latest = points[-1] if points and isinstance(points[-1], dict) else {}

    y = draw_text(draw, "Latest capture", PAD, y + 8, WIDTH - 2 * PAD, 25) + 5
    latest_height = 570
    latest_path = images.get("timelapse_latest")
    available = photo_box(base, latest_path, (PAD, y, WIDTH - PAD, y + latest_height),
                          "Latest capture unavailable")
    y += latest_height + 9
    latest_label = latest.get("time_label") or time_label(latest.get("timestamp"))
    if latest.get("path"):
        latest_label += "  |  " + os.path.basename(str(latest["path"]))
    if not available and latest.get("path"):
        latest_label += "  |  Image could not be loaded"
    y = draw_text(draw, latest_label, PAD, y, WIDTH - 2 * PAD, 17, MUTED, limit=2) + 15

    summary = report.get("summary") or {}
    settings = data.get("settings") or {}
    mode = summary.get("selection") or settings.get("gallery_mode") or "recent"
    gallery_title = {
        "recent": "Five most recent captures",
        "hourly": "Closest to the hour / last five hours",
        "daily": "Closest to {} / last five days".format(
            summary.get("daily_time") or settings.get("daily_time") or "1700"),
    }.get(mode, "Selected captures")
    y = draw_text(draw, gallery_title, PAD, y, WIDTH - 2 * PAD, 24, limit=2) + 8
    selections = {item.get("key"): item for item in report.get("selections") or []
                  if isinstance(item, dict)}
    slot_w = (WIDTH - 2 * PAD - 4 * GAP) // 5
    gallery_top = y
    gallery_bottom = y
    for index in range(5):
        key = "timelapse_{}".format(index + 1)
        selection = selections.get(key) or {}
        x = PAD + index * (slot_w + GAP)
        photo_box(base, images.get(key), (x, y, x + slot_w, y + 145))
        label = selection.get("label") or "Image {}".format(index + 1)
        cy = draw_text(draw, label, x, y + 154, slot_w, 15, INK, limit=2)
        actual = selection.get("time_label")
        if actual:
            cy = draw_text(draw, actual, x, cy + 2, slot_w, 14, MUTED, limit=2)
        if selection.get("path") and not images.get(key):
            cy = draw_text(draw, "Download unavailable", x, cy + 2, slot_w, 14, AMBER, limit=2)
        gallery_bottom = max(gallery_bottom, cy)
    y = max(gallery_top + 205, gallery_bottom) + 20
    y = draw_text(draw, "Capture file history", PAD, y, WIDTH - 2 * PAD, 25) + 8
    graph = graph_image(report)
    base.paste(graph, (PAD, y))
    y += graph.height + 10
    return draw_text(draw, "Times on photographs use the Pigrow clock; graph times are UTC. "
                     "File sizes and timing can reveal gaps; they do not validate image content.",
                     PAD, y, WIDTH - 2 * PAD, 15, MUTED, limit=2)


def make_timelapse_datawall(data, opts=None, detailed=False):
    data = data if isinstance(data, dict) else {}
    options = dict(data.get("settings") or {})
    options.update(opts or {})
    report = read_report(data)
    base = Image.new("RGB", (WIDTH, 4600 if detailed else 2100), BG)
    y = draw_summary(base, data, report, detailed)
    if detailed:
        y = draw_detail(base, data, report, y)
    else:
        y = draw_text(ImageDraw.Draw(base), "Fast mode uses capture metadata only.",
                      PAD, y + 8, WIDTH - 2 * PAD, 16, MUTED)
    output = options.get("output") or ("./timelapse_detailed_datawall.png" if detailed
                                       else "./timelapse_fast_datawall.png")
    output = os.fspath(output)
    base.crop((0, 0, WIDTH, min(base.height, y + PAD))).save(output)
    return output
