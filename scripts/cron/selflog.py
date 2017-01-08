#!/usr/bin/python
import datetime, time
import os, sys
sys.path.append('/home/pragmo/pigitgrow/Pigrow/scripts/')
import pigrow_defs
script = 'selflog.py'

#loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
loc_locs = '/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt'
loc_dic = pigrow_defs.load_locs(loc_locs)
path = loc_dic["path"]

##
## Raspberry Pi Self-Logger
##    This is designed to run independently or as a module called to gather current statistics
##

#   To be gathered;
#      Timenow  (timestamp)
#      Uptime   (duration since on)
#      Diskfull (total, space remaining, percentage)
#
#
#

def gather_data(path):
    print("Interorgating pi about it's status...")
    timenow = datetime.datetime.now()
    print timenow
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds = uptime_seconds))
    return {'total':total, 'used':used, 'free':free, 'percent':round(percent, 1), 'timenow':timenow, 'uptime_sec':uptime_seconds,'uptime_str':uptime_string.split('.')[0]}

info = gather_data(path)
print info
