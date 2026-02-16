#!/usr/bin/python3
import os
import sys
import glob

HOME = os.path.expanduser("~")
LOG_DIR = os.path.join(HOME, "Pigrow", "logs")

def _last_nonblank_line(path, chunk_size=4096):
    """
    Efficiently read the last non-blank line from a text file.
    Returns the line (str) or an error string starting with 'Error:'.
    """
    if not os.path.isfile(path):
        return f"Error: file {path} not found."

    try:
        size = os.path.getsize(path)
    except OSError as e:
        return f"Error: cannot stat {path}: {e}"

    if size == 0:
        return f"Error: file {path} is empty."

    try:
        with open(path, "rb") as f:
            # Read from the end in chunks until we find a non-blank line
            offset = 0
            remainder = b""
            while True:
                read_size = min(chunk_size, size - offset)
                if read_size <= 0:
                    break
                offset += read_size
                f.seek(size - offset)
                data = f.read(read_size) + remainder
                # Split lines without dropping empty ones
                lines = data.splitlines()
                # If the data didn't start at file start, the first line may be partial;
                # carry it to the next iteration
                if size - offset > 0 and lines:
                    remainder = lines[0]
                    candidate_lines = lines[1:]
                else:
                    remainder = b""
                    candidate_lines = lines

                # Walk from end to find first non-blank
                for raw in reversed(candidate_lines):
                    try:
                        line = raw.decode("utf-8", errors="replace").strip()
                    except Exception:
                        line = raw.decode(errors="replace").strip()
                    if line != "":
                        return line

            # If we exhausted chunks, also consider any remainder (file very small)
            if remainder:
                line = remainder.decode("utf-8", errors="replace").strip()
                if line:
                    return line

            return f"Error: no non-blank lines in {path}."
    except Exception as e:
        return f"Error: failed reading {path}: {e}"

def show_info(logs=None):
    """
    If logs is None or empty, list all *.txt logs in LOG_DIR and show last non-blank line for each.
    If logs is a list of log filenames, show the last non-blank line for each.
    Output is a multi-line string: 'name: value' per line.
    """
    results = []

    if not logs:
        # Auto-discover .txt logs
        for full in sorted(glob.glob(os.path.join(LOG_DIR, "*.txt"))):
            name = os.path.basename(full)
            val = _last_nonblank_line(full)
            results.append(f"{name}: {val}")
        if not results:
            return f"Error: no .txt logs found in {LOG_DIR}."
        return "\n".join(results)

    # Use provided names (don’t allow paths—keep it within LOG_DIR)
    for name in logs:
        name = name.strip()
        if not name:
            continue
        full = os.path.join(LOG_DIR, name)
        val = _last_nonblank_line(full)
        results.append(f"{name}: {val}")

    if not results:
        return "Error: no logs specified."
    return "\n".join(results)

def _parse_args(argv):
    """
    Supported:
      -h / --help
      -flags                -> prints 'log='
      log=name1.txt,name2.txt
    """
    if not argv:
        return None

    logs = None
    for arg in argv:
        a = arg.strip()
        al = a.lower()
        if al in ("-h", "--help"):
            print("Last Log Line Info Module")
            print("")
            print("Usage:")
            print("  info_lastlog.py                  # show last line of all *.txt logs")
            print("  info_lastlog.py log=bme280.txt   # show last line of a specific log")
            print("  info_lastlog.py log=a.txt,b.txt  # show last lines for multiple logs")
            print("")
            print("Flags:")
            print("  -flags    -> prints 'log=' to indicate supported flag")
            sys.exit(0)
        elif al == "-flags":
            print("log=")
            sys.exit(0)
        elif "=" in a:
            key, val = a.split("=", 1)
            key = key.strip().lower()
            if key == "log":
                # Split comma-separated names
                logs = [v.strip() for v in val.split(",") if v.strip()]
    return logs

if __name__ == "__main__":
    logs = _parse_args(sys.argv[1:])
    # If _parse_args exited due to -h/-flags it won't reach here
    print(show_info(logs))
