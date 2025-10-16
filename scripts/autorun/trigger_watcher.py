#!/usr/bin/env python3
import time
import datetime
import os
import re
import sys
import argparse
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
try:
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler
except:
    err_log = homedir + "/Pigrow/logs/err_log.txt"
    err_msg = "Watchdog is not installed, trigger_log unable to run"
    pigrow_defs.write_log('trigger_log.py', err_msg, err_log)
    sys.exit()

trigger_events_path     = homedir + "/Pigrow/config/trigger_events.txt"
trigger_conditions_path = homedir + "/Pigrow/logs/trigger_conditions.txt"
trig_log                = homedir + "/Pigrow/logs/trig_log.txt"

parser = argparse.ArgumentParser(description="Watch Pigrow logs and fire triggers based on conditions.")
parser.add_argument('-v', '--verbose', type=int, choices=[0,1,2], default=2,
                    help='Set output verbosity level: 0=errors, 1=info, 2=debug')
parser.add_argument('-l', '--log', action='store_true',
                    help='Enable trigger logging to trig_log.txt')
args = parser.parse_args()

# Global settings
print_level = args.verbose
enable_logging = args.log

_TIME_RANGE_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$", re.ASCII)


def clear_conditions():
    try:
        os.remove(trigger_conditions_path)
    except FileNotFoundError:
        pass


class config_data:
    """
    Stores trigger specs as a list of dicts and the set of logs to watch.
    Legacy keys (always present):
      log_name, value_label, trigger_type, trigger_value,
      condition_name, trig_direction, trig_cooldown, cmd
    v2-only optional keys:
      enabled_window, device_link
    """

    def __init__(self):
        self.trigger_conditions = []  # list[dict]
        self.logs_to_check = []       # list[str]

    # ---------- file helpers ----------
    def read_file_lines(self, filepath: str):
        print_limit(f" - Loading {filepath}", 1)
        if not os.path.isfile(filepath):
            with open(filepath, "w") as _:
                pass
            print_limit(f" - {filepath} not found. Created blank.", 0)
            return []
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()

    # ---------- main loader ----------
    def load_trigger_events(self, trigger_file: str):
        lines = self.read_file_lines(self, trigger_file)
        triggers = []

        for raw in lines:
            line = raw.strip()
            if not line or "," not in line:
                continue
            try:
                if line.startswith("v2,"):
                    row = self._parse_v2_line(self, line)
                else:
                    row = self._parse_legacy_line(self, line)
            except Exception as e:
                print_limit(f" !! Failed to parse trigger line: {line} :: {e}", 0)
                continue

            if row:
                triggers.append(row)

        self.trigger_conditions = triggers

        # unique logs_to_check
        seen = set()
        logs = []
        for d in self.trigger_conditions:
            name = d["log_name"]
            if name not in seen:
                seen.add(name)
                logs.append(name)
        self.logs_to_check = logs
        print_limit(" - Checking logs; " + str(self.logs_to_check), 2)

    # ---------- parsing helpers ----------
    def _nth_comma_positions(line: str, n: int):
        pos, start = [], 0
        for _ in range(n):
            i = line.find(",", start)
            if i == -1:
                break
            pos.append(i)
            start = i + 1
        return pos

    def _parse_legacy_line(self, line: str) -> dict:
        """
        Legacy format (no version marker). 8 fields (7 commas).
        cmd is the tail and may contain commas.
        """
        commas = self._nth_comma_positions(line, 7)
        if len(commas) < 7:
            raise ValueError("legacy line has fewer than 7 commas")

        c = commas
        log_name       = line[:c[0]].strip()
        value_label    = line[c[0]+1:c[1]].strip()
        trigger_type   = line[c[1]+1:c[2]].strip()
        trigger_value  = line[c[2]+1:c[3]].strip()
        condition_name = line[c[3]+1:c[4]].strip()
        trig_direction = line[c[4]+1:c[5]].strip()
        trig_cooldown  = line[c[5]+1:c[6]].strip()
        cmd            = line[c[6]+1:].strip()

        return {
            "log_name": log_name,
            "value_label": value_label,
            "trigger_type": trigger_type,
            "trigger_value": trigger_value,
            "condition_name": condition_name,
            "trig_direction": trig_direction,
            "trig_cooldown": trig_cooldown,
            "cmd": cmd,
            # v2 fields absent
        }

    def _parse_v2_line(self, line: str) -> dict:
        """
        v2 format starts with 'v2,' and has exactly one guard field.
        Body fields after 'v2,' → 9 fields (8 commas):
          0 log_name
          1 value_label
          2 trigger_type
          3 trigger_value
          4 condition_name
          5 trig_direction
          6 trig_cooldown
          7 enable_guard     ('' | 'none' | 'HH:MM-HH:MM' | 'device:<type>:<name>:on|off')
          8 cmd              (tail; may contain commas)
        """
        body = line[3:]  # strip leading 'v2,'

        commas = self._nth_comma_positions(body, 8)
        if len(commas) < 8:
            raise ValueError("v2 line malformed: expected at least 8 commas after marker")

        c = commas
        log_name       = body[:c[0]].strip()
        value_label    = body[c[0]+1:c[1]].strip()
        trigger_type   = body[c[1]+1:c[2]].strip()
        trigger_value  = body[c[2]+1:c[3]].strip()
        condition_name = body[c[3]+1:c[4]].strip()
        trig_direction = body[c[4]+1:c[5]].strip()
        trig_cooldown  = body[c[5]+1:c[6]].strip()
        enable_guard   = body[c[6]+1:c[7]].strip()
        cmd            = body[c[7]+1:].strip()

        return {
            "log_name": log_name,
            "value_label": value_label,
            "trigger_type": trigger_type,
            "trigger_value": trigger_value,
            "condition_name": condition_name,
            "trig_direction": trig_direction,
            "trig_cooldown": trig_cooldown,
            "enable_guard": enable_guard,  # single guard field
            "cmd": cmd,
        }

def print_limit(text, level=1):
    if level <= print_level:
        print(text)
    if enable_logging and level <= print_level:
        pigrow_defs.write_log('trigger_watcher.py', text, trig_log)


def check_condition(condition_name, trig_direction):
    '''
    This reads the trigger_conditions file to determine if it should activate the trigger,
    it is stored as a seperate file rather than a list stored in memory so that it can be edited remotely
    for example it mighty be useful to turn something off until user intervention turns it on
    or for something to be controlled by a switch, button or remote interface -
    only creaing graphs while a screen is on for example ot having a control to give a short boost of heat.
    '''
    # read conditions file
    if not os.path.isfile(trigger_conditions_path):
        print_limit(" - Conditions file not fonnd, no conditions currently set",1 )
        return True
    else:
        with open(trigger_conditions_path, 'r') as f:
            trigger_conditions = f.readlines()
        # find trigger
        trigger_state = "none"
        for line in trigger_conditions:
            line_split = line.split(",")
            if len(line_split) == 3:
                if line_split[0] == condition_name:
                    trigger_state = line_split[1].strip().lower()
                    trigger_cooldown = line_split[2].strip()
        # check if condition is met
        if not trigger_state == "none":
            # convert timestamp to datetime
            if not trigger_cooldown == "none" and not trigger_cooldown == "":
                try:
                    trigger_datetime = datetime.datetime.fromtimestamp(float(trigger_cooldown))
                    if trigger_datetime > datetime.datetime.now():
                        print_limit(f"{condition_name}, {trig_direction} - still cooling down, wont fire again for " + str(trigger_datetime - datetime.datetime.now()), 1)
                        return False
                except:
                    print_limit(" !! Failed to convert cooldown to date, it should be a timestamp")
            # check if trigger state is already set
            if trigger_state == trig_direction:
                print_limit(f"{condition_name}, {trig_direction} - Not triggering because condition is already set...", 2)
                return False
            else:
                if not trigger_state == "pause":
                    print_limit(f"{condition_name}, {trig_direction} - Trigger is not paused and not already set.", 2)
                    return True
                else:
                    print_limit(f"{condition_name}, {trig_direction} - Trigger paused, not triggering.", 2)
                    return False
        else:
            return True


def get_last_line(log_path: str) -> str:
    """
    Robustly read the last line of a (possibly small) text file.
    Returns '' if the file is empty.
    """
    try:
        size = os.path.getsize(log_path)
    except OSError:
        return ""

    if size == 0:
        return ""

    # Try a simple tail: read a small chunk from the end and splitlines
    chunk = 1024
    with open(log_path, "rb") as f:
        if size <= chunk:
            data = f.read()
        else:
            f.seek(-chunk, os.SEEK_END)
            data = f.read()
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        text = data.decode(errors="replace")

    lines = text.splitlines()
    if lines:
        return lines[-1]
    return ""

def get_item_from_line(line, key):
    split_chr = ">"
    second_split_chr = "="

    if not line or split_chr not in line:
        return None

    for token in line.split(split_chr):
        if second_split_chr in token:
            k, v = token.split(second_split_chr, 1)
            if k.strip() == key:
                return v.strip()
    return None

def create_conditions_list(log_name):
    """
        Preserve existing consumer order while sourcing from dicts.
    """
    conditions = []
    for item in config_data.trigger_conditions:
        if item.get("log_name", "") == log_name:
            conditions.append([
                item.get("value_label", ""),
                item.get("trigger_type", ""),
                item.get("trigger_value", ""),
                item.get("condition_name", ""),
                item.get("trig_direction", ""),
                item.get("trig_cooldown", ""),
                item.get("cmd", ""),
                item.get("enable_guard", ""),
            ])
    return conditions



def check_trigger_value(trigger: str, line_value: str, value: str) -> bool:
    """
    Returns True if the trigger condition is met.
    """
    # Guard numeric cases
    def _to_float(s):
        return float(str(s).strip())

    try:
        if trigger == "above":
            if _to_float(value) < _to_float(line_value):
                print_limit(f" Value {line_value} larger than trigger value {value}", 1)
                return True

        elif trigger == "below":
            if _to_float(value) > _to_float(line_value):
                print_limit(f" Value {line_value} smaller than trigger value {value}", 1)
                return True

        elif trigger == "window":  # inside min:max
            if ":" in value:
                val_min, val_max = [p.strip() for p in value.split(":", 1)]
                if _to_float(line_value) > _to_float(val_min) and _to_float(line_value) < _to_float(val_max):
                    print_limit(f"Value greater than {val_min} and less than {val_max}", 1)
                    return True

        elif trigger == "frame":  # outside min:max
            if ":" in value:
                val_min, val_max = [p.strip() for p in value.split(":", 1)]
                outside = not (_to_float(line_value) > _to_float(val_min) and _to_float(line_value) < _to_float(val_max))
                if outside:
                    print_limit(f"Value less than {val_min} or greater than {val_max}", 1)
                    return True

        elif trigger == "all":
            print_limit(f"Trigger set to all", 1)
            return True

    except ValueError:
        print_limit(f" !! Non-numeric comparison: trigger={trigger} value='{value}' line_value='{line_value}'", 0)
        return False

    return False

def _parse_time_range(guard: str):
    m = _TIME_RANGE_RE.match(guard or "")
    if not m:
        return None
    h1, m1, h2, m2 = map(int, m.groups())
    if not (0 <= h1 < 24 and 0 <= h2 < 24 and 0 <= m1 < 60 and 0 <= m2 < 60):
        return None
    return h1 * 60 + m1, h2 * 60 + m2

def _now_minutes_local():
    t = datetime.datetime.now().time()
    return t.hour * 60 + t.minute

def _within_window(now_mins, start_mins, end_mins):
    if start_mins == end_mins:
        return False
    if start_mins < end_mins:
        return start_mins <= now_mins < end_mins
    return now_mins >= start_mins or now_mins < end_mins  # overnight

def guard_allows_firing(enable_guard: str) -> bool:
    g = (enable_guard or "").strip()
    if not g or g.lower() == "none":
        return True
    if g.lower().startswith("device:"):
        print_limit(f"link to device: {g} not yet supported.", 1)
        return False
    tr = _parse_time_range(g)
    if tr is None:
        print_limit(f" !! Unknown enable_guard format '{g}', blocking trigger.", 0)
        return False
    now_m = _now_minutes_local()
    ok = _within_window(now_m, tr[0], tr[1])
    if not ok:
        print_limit(f" - Outside time window {g}; not triggering.", 2)
    return ok

def check_value(log_path):

    date_text = "time"
    log_name = os.path.split(log_path)[1]
    print_limit(" - log changed - " + log_name, 1)

    # Check the conditions for this log
    # read log
    if log_name in config_data.logs_to_check:
        last_line = get_last_line(log_path)
        if not last_line:
            print_limit(" - Empty or unreadable log; skipping", 2)
            return

        line_date = get_item_from_line(last_line, "time")
        conditions = create_conditions_list(log_name)

        # check each trigger assocaiated wit this log
        for condition in conditions:
            val_label      = condition[0]
            trigger        = condition[1]
            value          = condition[2]
            condition_name = condition[3]
            trig_direction = condition[4]
            trig_cooldown  = condition[5]
            cmd            = condition[6]
            enable_guard   = condition[7]

            if not guard_allows_firing(enable_guard):
                continue

            if check_condition(condition_name, trig_direction) is True:
                line_value = get_item_from_line(last_line, val_label)

                if line_value is None or line_value == "":
                    print_limit(f" - No '{val_label}' in line; no action", 2)
                    continue

                if check_trigger_value(trigger, line_value, value):
                    print(f"Running Command; {cmd}")
                    os.system(cmd + " &")
                    pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)
                else:
                    print_limit(" - trigger value conditions not met, no action", 2)


def on_created(event):
    check_value(event.src_path)

def on_deleted(event):
    pass

def on_modified(event):
    check_value(event.src_path)

def on_moved(event):
    pass

def trig_change(event):
    if "trigger_events.txt" in event.src_path:
        print_limit(" - - - Trigger events file changed - - -", 2)
        config_data.load_trigger_events(config_data, trigger_events_path)

def observe_trig_file():
    print_limit(" - Enabling Trigger Events Config File Observation -", 2)
    path = homedir + "/Pigrow/config/"
    #trig_events_handler = PatternMatchingEventHandler(["*.txt"], None, True, False)
    trig_events_handler = PatternMatchingEventHandler(
            patterns = ["*.txt"],
            ignore_patterns = None,
            ignore_directories = True,
            case_sensitive = False
                              )
    trig_events_handler.on_created = trig_change
    trig_events_handler.on_modified = trig_change
    ####
    # are these not pointing to the wrong events handler? 
    trig_e_handler.on_deleted = on_deleted
    trig_e_handler.on_modified = on_modified
    ###
    trig_events_ob = Observer()
    trig_events_ob.schedule(trig_events_handler, path, recursive=True)
    trig_events_ob.start()


if __name__ == "__main__":
    # Set timed relays
    cmd = homedir + "/Pigrow/scripts/autorun/startup_set_relays.py"
    os.system(cmd)
    # empty the conditions file
    clear_conditions()
    # set path from locs file
    config_data.load_trigger_events(config_data, trigger_events_path)
    print_limit(" - Loaded trigger events;", 1)
    print_limit(config_data.trigger_conditions, 2)

    # Set up and run log file watcher
    path = homedir + "/Pigrow/logs/"
    patterns = ["*.txt"]
    #trig_e_handler = PatternMatchingEventHandler(patterns, None, True, False)
    trig_e_handler = PatternMatchingEventHandler(
            patterns = patterns,
            ignore_patterns = None,
            ignore_directories = True,
            case_sensitive = False
                              )
    trig_e_handler.on_created = on_created #,
    trig_e_handler.on_deleted = on_deleted
    trig_e_handler.on_modified = on_modified
    trig_e_handler.on_moved = on_moved
    trig_observer = Observer()
    trig_observer.schedule(trig_e_handler, path, recursive=True)
    trig_observer.start()
    # set up and run trigger config file watcher
    observe_trig_file()
    # loop forever waiting for file changes to happen.
    while True:
        time.sleep(1)
