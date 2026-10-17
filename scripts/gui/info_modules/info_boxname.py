#!/usr/bin/python3
from pathlib import Path

def show_info():
    """Read the configured name without matching comments or similar keys."""
    try:
        with (Path.home() / "Pigrow/config/pigrow_config.txt").open(
            encoding="utf-8"
        ) as config_file:
            for line in config_file:
                key, separator, value = line.partition("=")
                if separator and key.strip() == "box_name":
                    return value.strip()
    except OSError:
        pass
    return ""


if __name__ == '__main__':
    print(show_info())
