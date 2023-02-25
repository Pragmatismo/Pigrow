#!/usr/bin/python3
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta

def show_info():
    # Run the 'grep' command to search for lines in the syslog that contain the words "CRON" and "CMD"
    result = subprocess.run(['grep', '-E', 'CRON.*CMD', '/var/log/syslog'], stdout=subprocess.PIPE)
    # Decode the output of the command as a UTF-8 string
    output = result.stdout.decode('utf-8')
    # Split the output into individual lines
    lines = output.split('\n')

    # Create a dictionary to store information about each unique cron cmd script
    cron_cmds = defaultdict(list)

    # get time syslog starts
    line = lines[0]
    parts = line.split()
    syslog_start_time = parts[0] + ' ' + parts[1] + ' ' + parts[2]
    syslog_start_time = datetime.strptime(syslog_start_time + ' ' + str(datetime.now().year), '%b %d %H:%M:%S %Y')

    # Iterate over each line in the syslog that contains a CRON CMD entry
    for line in lines:
        if 'CRON' in line and 'CMD' in line:
            # Extract the cron cmd script and the time it was called from the syslog line

            parts = line.split()
            cron_cmd = " ".join(parts[7:])
            cron_time = parts[0] + ' ' + parts[1] + ' ' + parts[2]
            cron_time = datetime.strptime(cron_time + ' ' + str(datetime.now().year), '%b %d %H:%M:%S %Y')

            # Append the time the script was called to the list of times for this script
            cron_cmds[cron_cmd].append(cron_time)

    # Create a string to store the output
    output_str = 'syslog start time: ' + str(syslog_start_time) + '\n\n'

    # Iterate over each unique cron cmd script and calculate the requested information
    for cron_cmd, cron_times in cron_cmds.items():
        # Calculate the number of times the script has been called
        num_calls = len(cron_times)

        # Calculate the time since the script was last called
        last_call_time = cron_times[-1]
        time_since_last_call = datetime.now() - last_call_time

        # Calculate the time difference between the last five times the script was called
        time_diffs = []
        for i in range(-1, -6, -1):
            try:
                if len(cron_times) >= abs(i):
                    time_diff = cron_times[i] - cron_times[i-1]
                    time_diffs.append(str(time_diff))
            except:
                pass

        # Create a string with the calculated information and add it to the output
        output_str += "Cron CMD script " + str(cron_cmd) + " has been called " + str(num_calls) + " times.\n"
        output_str += "Last call was at " + str(last_call_time) + ", which was " + str(time_since_last_call) + " ago.\n"
        output_str += "Time difference between last 5 calls: " + ", ".join(time_diffs) + "\n\n"

    return output_str


if __name__ == '__main__':
    print(show_info())
