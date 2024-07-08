#!/usr/bin/env python3
import datetime, time
import os, sys
from subprocess import check_output
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'selflog.py'
path = homedir + '/Pigrow/'

for argu in sys.argv:
    if argu == '-h' or argu == '--help':
        print(" Pigrow Raspberry Pi Self-Logger")
        print(" ")
        print("Creates a log of several metrics that can be used to")
        print("monitor the pigrows health.")
        print("")
        print(" (minor update to add args coming soon)")
        sys.exit(0)
    if argu == '-flags':
        print("")
        sys.exit(0)

def gather_data(path="./"):
    print("Interorgating pi about it's status...")
    timenow = datetime.datetime.now()
    #check storage space
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    #check up time
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(datetime.timedelta(seconds = uptime_seconds))
    load_ave1,load_ave5,load_ave15 = os.getloadavg() # system load Averages for 1, 5 and 15 min;
    #check memory info
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.split(":")[0]=="MemTotal":
                memtotal = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemAvailable":
                memavail = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemFree":
                memfree = line.split(":")[1].strip()
    #check cpu temp with 'vcgencmd measure_temp'
    # different versions of raspberry pi os have it in differnt locations and cron needs the full path
    if os.path.isfile("/opt/vc/bin/vcgencmd"):
        vpath = '/usr/bin/vcgencmd'
    elif os.path.isfile("/opt/vc/bin/vcgencmd"):
        vpath = '/opt/vc/bin/vcgencmd'
    else:
        vpath = 'vcgencmd'
    cpu_temp = os.popen(vpath + ' measure_temp').read().strip()
    cpu_temp = cpu_temp.split('=')[1].replace("'C", "")
    #send back data in a dictionary
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
            'memavail':memavail,
            'cpu_temp':cpu_temp
            }

def check_script_running(script):
    try:
        script_test = map(int,check_output(["pidof",script,"-x"]).split())
    except:
        script_test = False
    if script_test == False:
        return {'num_running':'0','script_status':'none','script_path':'none'}
    else:
        if len(script_test) > 1:
            for pid in script_test:
                try:
                    script_test_path = open(os.path.join('/proc', str(pid), 'cmdline'), 'rb').read()
                except IOError:
                    return {'num_running':'0','script_status':'died','script_path':'none'}
                for line in open("/proc/"+ str(pid)  +"/status").readlines():
                    if line.split(':')[0] == "State":
                        script_test_status = line.split(':')[1].strip()
                return {'num_running':str(len(script_test)),'script_status':script_test_status,'script_path':script_test_path}
        else:
            for line in open("/proc/"+ str(script_test[0])  +"/status").readlines():
                if line.split(':')[0] == "State":
                    script_test_status = line.split(':')[1].strip()
            try:
                script_test_path = open(os.path.join('/proc', str(script_test[0]), 'cmdline'), 'rb').read()
            except IOError:
                return {'num_running':'0','script_status':'died','script_path':'none'}
            return {'num_running':'1','script_status':script_test_status,'script_path':script_test_path}

if __name__ == '__main__':
    scripts_to_check = ['reddit_settings_ear.py','checkDHT.py']# 'chromium-browse'] #this doesn't work :( works for 'atom' and 'bash' needs fix
    print("################################################")
    print("######### SELF CHECKING INFO LOGGER ############")
    info = gather_data(path)
    line = ''
    for key, value in info.items():
        line += str(key) + "=" + str(value) + ">"

    for script in scripts_to_check:
        script_status = check_script_running(script)
        #print("The script " + script + " has " + script_status['num_running'] + " instances running")
        for key, value in script_status.items():
           line += str(script + '_' + key) + "=" + str(value) + ">"
    line += '\n'
    print (line)

    log_location = homedir + '/Pigrow/logs/selflog.txt'
    try:
        with open(log_location, "a") as f:
            f.write(line)
    except:
        print["-LOG ERROR-"]
        err_log = homedir + "/Pigrow/logs/err_log.txt"
        pigrow_defs.write_log('selflog.py', 'writing self log failed', err_log)
