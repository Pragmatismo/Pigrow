#!/usr/bin/python3
import os
import sys

def show_info(percent_only=False):
    """
    Retrieves disk usage for the root filesystem using 'df -l /'
    and returns either a detailed multi-line string or just the numeric percentage
    used if percent_only is True.
    """
    out = os.popen("df -l /").read()
    if len(out) > 1:
        # Split the output into tokens
        response_list = [item for item in out.split(" ") if item]

        hdd_total = response_list[-5]
        hdd_used = response_list[-4]
        hdd_available = response_list[-3]
        hdd_percent = response_list[-2]

        if percent_only:
            # Return only the numeric percentage, removing any trailing '%'
            return hdd_percent.rstrip('%')
        else:
            info = "Total     = " + hdd_total + " KB\n"
            info += "Available = " + hdd_available + " KB\n"
            info += "Used      = " + hdd_used + " KB (" + hdd_percent + ")\n"
            return info
    return "No disk usage info available"

if __name__ == '__main__':
    # Default setting
    percent_only = False

    # Process command-line arguments
    for arg in sys.argv[1:]:
        arg_lower = arg.lower()
        if arg_lower in ['-h', '--help']:
            print("Disk Usage Info Module")
            print("")
            print("Usage:")
            print("   [percent_only=true]   Output only the numeric percentage")
            print("")
            print("Example:")
            print("   ./info_diskusage.py percent_only=true")
            sys.exit(0)
        elif arg_lower == "-flags":
            print("percent_only=true")
            sys.exit(0)
        elif "=" in arg:
            key, val = arg.split("=", 1)
            key = key.lower().strip()
            val = val.lower().strip()
            if key == "percent_only":
                percent_only = (val == "true")

    # Output the disk usage info
    print(show_info(percent_only))
