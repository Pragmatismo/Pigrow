#!/usr/bin/env python3
"""Read capture metadata for the GUI timelapse datawalls (no image decoding).

The comparison always runs through the collection time, including when capture
has stopped. An automatic interval is a configured cron schedule, never a guess
from gaps between files. All labels and naive ISO inputs use the Pi's local time.
"""

import datetime as dt
from decimal import Decimal, ROUND_FLOOR
import json
import math
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}
CAPTURE_SCRIPTS = {"camcap.py", "libcam_cap.py", "picamcap.py", "picam2cap.py", "rpicap.py"}
CAPTURE_TIMESTAMP = re.compile(r"^cap_(\d+(?:\.\d+)?)$", re.IGNORECASE)
CRON_MACROS = {"@yearly": "0 0 1 1 *", "@annually": "0 0 1 1 *",
               "@monthly": "0 0 1 * *", "@weekly": "0 0 * * 0",
               "@daily": "0 0 * * *", "@midnight": "0 0 * * *",
               "@hourly": "0 * * * *"}


def _label(timestamp):
    return dt.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def _timestamp(value):
    if isinstance(value, dt.datetime):
        result = value.timestamp()
    else:
        try:
            result = float(value)
        except (TypeError, ValueError):
            result = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
    if not math.isfinite(result):
        raise ValueError("time must be a finite epoch value or ISO date/time")
    # Ensure values can also be represented in the local-time labels.
    _label(result)
    return result


def _normal_path(value, base=None):
    value = os.path.expandvars(os.path.expanduser(str(value)))
    if not os.path.isabs(value) and base is not None:
        value = os.path.join(str(base), value)
    return os.path.abspath(value)


def _capture_path(path, config_path, warnings):
    if path != "auto":
        return _normal_path(path)
    # The GUI invokes this module from the connected account's installation.
    # Anchor auto paths there rather than an inherited login-shell HOME or a
    # previous user's standard path left in dirlocs after moving an install.
    pigrow = Path(__file__).resolve().parents[3]
    default = str(pigrow / "caps")
    config = Path(config_path) if config_path is not None else pigrow / "config" / "dirlocs.txt"
    try:
        for line in config.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                if key.strip() == "caps_path" and value.strip():
                    configured = _normal_path(value.strip(), config.parent.parent)
                    if configured != default and re.fullmatch(r"/home/[^/]+/Pigrow/caps", configured):
                        warnings.append("Saved capture path {} is from another installation; using {}. "
                                        "Set capture_path explicitly to use that saved folder."
                                        .format(configured, default))
                        return default
                    return configured
    except FileNotFoundError:
        pass
    except OSError as exc:
        warnings.append("Could not read dirlocs: {}".format(exc))
    return default


def _scan(path, warnings):
    records = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if Path(entry.name).suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                try:
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    stat = entry.stat(follow_symlinks=False)
                    match = CAPTURE_TIMESTAMP.match(Path(entry.name).stem)
                    timestamp = float(match.group(1)) if match else stat.st_mtime
                    # Corrupt/out-of-range filename timestamps fall back to mtime.
                    try:
                        time_label = _label(timestamp)
                    except (OverflowError, OSError, ValueError):
                        timestamp = stat.st_mtime
                        time_label = _label(timestamp)
                    records.append({"path": os.path.join(path, entry.name),
                                    "timestamp": timestamp, "size": stat.st_size,
                                    "mtime": stat.st_mtime, "time_label": time_label})
                except OSError as exc:
                    warnings.append("Could not stat {}: {}".format(entry.name, exc))
    except OSError as exc:
        warnings.append("Could not read capture folder: {}".format(exc))
        return [], False
    records.sort(key=lambda record: (record["timestamp"], record["path"]))
    return records, True


def _cron_field(text, minimum, maximum, names=None):
    """Numeric cron lists/ranges/steps, with standard month/weekday names."""
    if names:
        for name, number in names.items():
            text = re.sub(name, str(number), text, flags=re.IGNORECASE)
    values = set()
    for part in text.split(","):
        pieces = part.split("/")
        if len(pieces) > 2:
            raise ValueError("invalid cron step")
        step = int(pieces[1]) if len(pieces) == 2 else 1
        if step <= 0:
            raise ValueError("invalid cron step")
        span = pieces[0]
        if span == "*":
            low, high = minimum, maximum
        elif "-" in span:
            low, high = map(int, span.split("-"))
        else:
            if len(pieces) == 2:
                raise ValueError("cron steps require a range or *")
            low = high = int(span)
        if low < minimum or high > maximum or low > high:
            raise ValueError("cron field outside valid range")
        values.update(range(low, high + 1, step))
    return values


class _CronSchedule:
    def __init__(self, fields):
        months = {name: i + 1 for i, name in enumerate(
            ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}
        weekdays = {name: i for i, name in enumerate(("sun", "mon", "tue", "wed", "thu", "fri", "sat"))}
        self.minutes = _cron_field(fields[0], 0, 59)
        self.hours = _cron_field(fields[1], 0, 23)
        self.days = _cron_field(fields[2], 1, 31)
        self.months = _cron_field(fields[3], 1, 12, months)
        self.weekdays = {value % 7 for value in _cron_field(fields[4], 0, 7, weekdays)}
        self.day_star = fields[2].startswith("*")
        self.weekday_star = fields[4].startswith("*")
        self.description = " ".join(fields)

    def _matches_date(self, date):
        dom = date.day in self.days
        dow = (date.weekday() + 1) % 7 in self.weekdays
        day_matches = dom and dow if self.day_star or self.weekday_star else dom or dow
        return date.month in self.months and day_matches

    def count(self, start, end):
        if start > end:
            return 0
        date = dt.datetime.fromtimestamp(start).date()
        last_date = dt.datetime.fromtimestamp(end).date()
        count = 0
        while date <= last_date:
            if self._matches_date(date):
                midnight = dt.datetime.combine(date, dt.time())
                # Count whole ordinary days at once, keeping large archives fast.
                next_midnight = midnight + dt.timedelta(days=1)
                day_start, day_end = midnight.timestamp(), next_midnight.timestamp()
                if start <= day_start and day_end <= end and day_end - day_start == 86400:
                    count += len(self.hours) * len(self.minutes)
                else:
                    for hour in self.hours:
                        for minute in self.minutes:
                            local = dt.datetime.combine(date, dt.time(hour, minute))
                            timestamp = local.timestamp()
                            # A nonexistent local time during a DST jump is not a slot.
                            if dt.datetime.fromtimestamp(timestamp) == local and start <= timestamp <= end:
                                count += 1
            date += dt.timedelta(days=1)
        return count

    def regular_interval(self):
        # Only advertise a fixed cadence for schedules that repeat evenly daily.
        if len(self.days) != 31 or len(self.months) != 12 or len(self.weekdays) != 7:
            return None
        minutes = sorted(hour * 60 + minute for hour in self.hours for minute in self.minutes)
        gaps = [right - left for left, right in zip(minutes, minutes[1:])]
        gaps.append(1440 + minutes[0] - minutes[-1])
        return gaps[0] * 60 if len(set(gaps)) == 1 else None


def _read_cron():
    try:
        result = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True,
                                timeout=10, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, "Could not read capture schedule: {}".format(exc)
    if result.returncode:
        return None, "No readable crontab; expected count is unknown."
    return result.stdout, None


def _find_schedule(path, cron_text, warnings):
    if cron_text is None:
        cron_text, error = _read_cron()
        if error:
            warnings.append(error)
            return None
    matches = []
    unsupported = False
    cron_timezone = None
    for raw in cron_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if re.match(r"CRON_TZ\s*=", line):
            cron_timezone = line.split("=", 1)[1].strip()
            continue
        if re.match(r"[A-Za-z_]\w*\s*=", line):
            continue
        if line.startswith("@"):
            pieces = line.split(None, 1)
            if len(pieces) != 2:
                continue
            schedule, command = CRON_MACROS.get(pieces[0]), pieces[1]
        else:
            pieces = line.split(None, 5)
            if len(pieces) != 6:
                continue
            schedule, command = " ".join(pieces[:5]), pieces[5]
        try:
            tokens = shlex.split(command, comments=True)
        except ValueError:
            continue
        script_indices = [index for index, token in enumerate(tokens)
                          if os.path.basename(token) in CAPTURE_SCRIPTS]
        if not script_indices:
            continue
        # A bare script or Python invocation is understood. Shell loops, wrappers,
        # sleeps and multiple commands may change the effective schedule.
        index = script_indices[0]
        prefix = tokens[:index]
        direct = not prefix or (len(prefix) <= 2 and re.match(r"^python[\d.]*$", os.path.basename(prefix[0]))
                                and all(token.startswith("-") for token in prefix[1:]))
        args = tokens[index + 1:]
        caps = [token.split("=", 1)[1] for token in args
                if token.startswith("caps=") or token.startswith("caps_path=")]
        destination = caps[-1] if caps else "~/Pigrow/caps"
        if "$" in os.path.expandvars(destination) or "`" in destination:
            unsupported = True
            continue
        destination = _normal_path(destination, os.path.expanduser("~"))
        if os.path.realpath(destination) != os.path.realpath(path):
            continue
        # Redirection tokens are harmless; shell control operators are not.
        if (not direct or len(script_indices) != 1 or cron_timezone is not None
                or any(token in {";", "&&", "||", "|", "&"} for token in tokens)
                or "%" in command):
            unsupported = True
            continue
        try:
            matches.append(_CronSchedule(schedule.split()) if schedule else None)
            unsupported = unsupported or matches[-1] is None
        except (ValueError, IndexError):
            unsupported = True
    if unsupported or len(matches) > 1:
        warnings.append("Capture cron jobs are unsupported or ambiguous; set interval explicitly for an expected count.")
        return None
    if not matches:
        warnings.append("No matching capture cron job; set interval explicitly for an expected count.")
        return None
    return matches[0]


def _daily_clock(value):
    value = str(value).strip().replace(":", "")
    if not re.match(r"^\d{4}$", value):
        raise ValueError("daily_time must be HHMM or HH:MM")
    hour, minute = int(value[:2]), int(value[2:])
    if hour > 23 or minute > 59:
        raise ValueError("daily_time must be a valid local time")
    return dt.time(hour, minute)


def _select(records, now, selection, daily_clock):
    """Newest target first. A missing hour/day keeps its own empty slot."""
    slots = []
    local_now = dt.datetime.fromtimestamp(now)
    # Convert before arithmetic: naive datetime subtraction clears ``fold`` at
    # the repeated autumn hour. Epoch arithmetic also skips the missing spring
    # hour and keeps each hourly capture window distinct.
    current_hour = local_now.replace(minute=0, second=0, microsecond=0).timestamp()
    available = [record for record in records if record["timestamp"] <= now]
    for index in range(5):
        target = None
        chosen = None
        if selection == "recent":
            if index < len(available):
                chosen = available[-1 - index]
            label = "Recent {}".format(index + 1)
        else:
            if selection == "hourly":
                target = current_hour - index * 3600
                # Disjoint windows allow images just before an hour mark to win
                # without reusing that capture for the adjacent target hour.
                period_start = target - 1800
                period_end = target + 1800
                label = dt.datetime.fromtimestamp(target).astimezone().strftime("%d %b %H:%M %Z")
            else:
                target_dt = dt.datetime.combine(local_now.date(), daily_clock)
                if target_dt.timestamp() > now:
                    target_dt -= dt.timedelta(days=1)
                target_dt -= dt.timedelta(days=index)
                day_start = dt.datetime.combine(target_dt.date(), dt.time())
                period_start = day_start.timestamp()
                period_end = (day_start + dt.timedelta(days=1)).timestamp()
                target = target_dt.timestamp()
                label = target_dt.strftime("%d %b %H:%M")
            candidates = [record for record in available
                          if period_start <= record["timestamp"] < period_end]
            if candidates:
                chosen = min(candidates, key=lambda record: (abs(record["timestamp"] - target), record["timestamp"]))
        slots.append({"key": "timelapse_{}".format(index + 1), "target": target,
                      "label": label, "path": chosen["path"] if chosen else None,
                      "timestamp": chosen["timestamp"] if chosen else None,
                      "time_label": chosen["time_label"] if chosen else None})
    return slots


def collect_info(path="auto", detail="fast", interval="auto", start="auto",
                 selection="recent", daily_time="1700", now=None,
                 config_path=None, cron_text=None):
    """Return a JSON-serializable report; ``now``/``cron_text`` allow repeatable use.

    ``start`` is ISO local time, offset-aware ISO time, or epoch seconds. With no
    explicit start the first observed capture anchors the comparison; this cannot
    detect captures missing before that file. Hour/day galleries keep empty slots
    for periods without captures rather than reusing an older image.
    """
    if detail not in {"fast", "detailed"}:
        raise ValueError("detail must be fast or detailed")
    if selection not in {"recent", "hourly", "daily"}:
        raise ValueError("selection must be recent, hourly or daily")
    daily_clock = _daily_clock(daily_time)
    now = _timestamp(time.time() if now is None else now)
    warnings = []
    path = _capture_path(path, config_path, warnings)
    records, readable = _scan(path, warnings)
    schedule = None
    if str(interval).lower() == "auto":
        schedule = _find_schedule(path, cron_text, warnings)
        interval_seconds = schedule.regular_interval() if schedule else None
        interval_source = "cron" if schedule else "unknown"
    else:
        interval_seconds = float(interval)
        if not math.isfinite(interval_seconds) or interval_seconds <= 0:
            raise ValueError("interval must be auto or a positive number of seconds")
        interval_source = "explicit"
    observed = [record for record in records if record["timestamp"] <= now]
    if len(observed) != len(records):
        warnings.append("Future-dated captures are excluded from the comparison and image selection.")
    first = observed[0] if observed else None
    last = observed[-1] if observed else None
    if str(start).lower() == "auto":
        window_start = first["timestamp"] if first else None
        if window_start is not None and schedule:
            window_start = math.floor(window_start / 60) * 60
        start_source = "first-observed" if first else "unknown"
        if first:
            warnings.append("Comparison starts at the first observed image; earlier missing images cannot be counted.")
    else:
        window_start = _timestamp(start)
        start_source = "explicit"
        if window_start > now:
            raise ValueError("start must not be later than the collection time")
    actual = sum(window_start <= record["timestamp"] <= now for record in records) if window_start is not None else 0
    expected = None
    if readable and window_start is not None:
        if schedule:
            expected = schedule.count(window_start, now)
        elif interval_seconds is not None:
            # Decimal text avoids losing an interval at fractional boundaries
            # (e.g. (1000.3 - 1000) / 0.1 is slightly below 3 as a float).
            elapsed = Decimal(str(now)) - Decimal(str(window_start))
            expected = int((elapsed / Decimal(str(interval_seconds))).to_integral_value(rounding=ROUND_FLOOR)) + 1
    missing = max(0, expected - actual) if expected is not None else None
    extra = max(0, actual - expected) if expected is not None else None
    if not readable:
        status = "error"
    elif not observed:
        status = "empty"
    elif expected is None:
        status = "unknown"
    elif missing:
        status = "behind"
    elif extra:
        status = "extra"
    else:
        status = "complete"
    summary = {"image_count": len(records), "total_bytes": sum(record["size"] for record in records),
               "first_timestamp": first["timestamp"] if first else None,
               "last_timestamp": last["timestamp"] if last else None,
               "first_label": first["time_label"] if first else None,
               "last_label": last["time_label"] if last else None,
               "latest_age_seconds": now - last["timestamp"] if last else None,
               "window_start": window_start, "window_end": now,
               "window_start_label": _label(window_start) if window_start is not None else None,
               "start_source": start_source, "actual_count": actual, "expected_count": expected,
               "missing_count": missing, "extra_count": extra,
               "completion_percent": float(Decimal(actual) * 100 / Decimal(expected)) if expected else None,
               "interval_seconds": interval_seconds, "interval_source": interval_source,
               "schedule_description": schedule.description if schedule else None,
               "selection": selection, "daily_time": daily_clock.strftime("%H:%M"),
               "status": status, "warnings": warnings}
    report = {"version": 1, "detail": detail, "path": path, "generated_at": now,
              "generated_label": _label(now), "timezone": time.tzname[time.localtime(now).tm_isdst],
              "summary": summary}
    if detail == "detailed":
        selections = _select(records, now, selection, daily_clock)
        by_path = {record["path"]: record for record in records}
        images = {"timelapse_latest": {key: last[key] for key in ("path", "size", "mtime")} if last else None}
        for slot in selections:
            chosen = by_path.get(slot["path"])
            images[slot["key"]] = {key: chosen[key] for key in ("path", "size", "mtime")} if chosen else None
        report.update({"points": observed, "latest": last,
                       "selections": selections, "datawall_images": images})
    return report


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    defaults = {"detail": "fast", "path": "auto", "interval": "auto", "start": "auto",
                "selection": "recent", "daily_time": "1700"}
    if "-flags" in argv:
        print("\n".join("{}={}".format(key, value) for key, value in defaults.items()))
        return 0
    if any(arg in {"-h", "--help", "-help"} for arg in argv):
        print(__doc__)
        print("Options (key=value): " + " ".join("{}={}".format(key, value) for key, value in defaults.items()))
        print("interval is seconds; start is ISO local time or epoch; daily_time is HHMM or HH:MM.")
        return 0
    try:
        for arg in argv:
            key, value = arg.split("=", 1)
            if key not in defaults:
                raise ValueError("unknown option: {}".format(key))
            defaults[key] = value
        report = collect_info(**defaults)
    except (ValueError, OverflowError, OSError) as exc:
        report = {"version": 1, "detail": defaults["detail"],
                  "summary": {"status": "error", "warnings": [str(exc)]}}
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
