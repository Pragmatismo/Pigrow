#!/usr/bin/python
import datetime, time
import os, sys
from subprocess import check_output
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

def gather_data(path="./"):
    print("Interorgating pi about it's status...")
    timenow = datetime.datetime.now()
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
    load_ave1,load_ave5,load_ave15 = os.getloadavg() # system load Averages for 1, 5 and 15 min;
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.split(":")[0]=="MemTotal":
                memtotal = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemAvailable":
                memavail = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemFree":
                memfree = line.split(":")[1].strip()
    return {'disk_total':total,
            'disk_used':used,
            'disk_free':free,
            'disk_percent':round(percent, 1),
            'timenow':timenow,
            'uptime_sec':uptime_seconds,
            'uptime_str':uptime_string.split('.')[0],
            'load_ave1':load_ave1,
            'load_ave5':load_ave5,
            'load_ave15':load_ave15,
            'memtotal':memtotal,
            'memfree':memfree,
            'memavail':memavail
            }



scripts_to_check = ['reddit_','checkDHT']

try:
    reddit_ear = map(int,check_output(["pidof",'atom']).split())
except:
    reddit_ear = False

if reddit_ear == False:
    print("Reddit Monitoring Script not running!")
else:
    if len(reddit_ear) > 1:
        print("There's more than one reddit monitoring script running!")
        for pid in reddit_ear:

            print pid

            #print os.getpgid(pid) # Return the process group id
            for line in open("/proc/"+ str(pid)  +"/status").readlines():
                if line.split(':')[0] == "State":
                    print line.split(':')[1].strip()

            #os.kill(pid, sig)
    else:
        print("Reddit Monitoring Script is running!")
        for line in open("/proc/"+ str(reddit_ear)  +"/status").readlines():
            if line.split(':')[0] == "State":
                reddit_ear_status = line.split(':')[1].strip()
        try:
            reddit_ear_path = open(os.path.join('/proc', str(pid), 'cmdline'), 'rb').read()
        except IOError:
            print("I think it died when we looked at it...")
        print reddit_ear_path
        print reddit_ear_status



#pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
#for pid in pids:
#    try:
#        print open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
#    except IOError: # proc has already terminated
#        continue




def get_pid(name):
    return map(int,check_output(["pidof",name]).split())

#try:
#    pid = get_pid('doggo')
#    print pid
#except:
#    print("No program of that name running.")

if __name__ == '__main__':
    print("################################################")
    print("######### SELF CHECKING INFO LOGGER ############")
    info = gather_data(path)
    for key, value in info.iteritems():
        print str(key) + " = " + str(value)
