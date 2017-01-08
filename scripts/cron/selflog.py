#!/usr/bin/python
import datetime, time
import os, sys
from subprocess import check_output
sys.path.append('/home/pi/Pigrow/scripts/')
import pigrow_defs
script = 'selflog.py'

loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'
#loc_locs = '/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt'
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

def check_script_running(script):
    try:
        script_test = map(int,check_output(["pidof",script,"-x"]).split())
    except:
        script_test = False
    if script_test == False:
        #print(script + " not running!")
        return {'num_running':'0','script_status':'none','script_path':'none'}
    else:
        if len(script_test) > 1:
            #print("There's more than one " + script + " running!")
            for pid in script_test:
                #print "---"
                #print pid
                try:
                    script_test_path = open(os.path.join('/proc', str(pid), 'cmdline'), 'rb').read()
                    #print script_test_path
                except IOError:
                    #print("I think it died when we looked at it...")
                    return {'num_running':'0','script_status':'died','script_path':'none'}
                #print os.getpgid(pid) # Return the process group id
                for line in open("/proc/"+ str(pid)  +"/status").readlines():
                    if line.split(':')[0] == "State":
                        script_test_status = line.split(':')[1].strip()
                return {'num_running':str(len(script_test)),'script_status':script_test_status,'script_path':script_test_path}
                #os.kill(pid, sig)
        else:
            #print(script + " is running!")
            for line in open("/proc/"+ str(script_test[0])  +"/status").readlines():
                if line.split(':')[0] == "State":
                    script_test_status = line.split(':')[1].strip()
            try:
                script_test_path = open(os.path.join('/proc', str(script_test[0]), 'cmdline'), 'rb').read()
            except IOError:
                #print("I think it died when we looked at it...")
                return {'num_running':'0','script_status':'died','script_path':'none'}
            #print script_test_path
            #print script_test_status
            return {'num_running':'1','script_status':script_test_status,'script_path':script_test_path}




#pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
#for pid in pids:
#    try:
#        print open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
#    except IOError: # proc has already terminated
#        continue




#def get_pid(name):
#    return map(int,check_output(["pidof",name]).split())

#try:
#    pid = get_pid('doggo')
#    print pid
#except:
#    print("No program of that name running.")

if __name__ == '__main__':
    scripts_to_check = ['reddit_settings_ear_2.py','checkDHT.py']# 'chromium-browse'] #this doesn't work :( works for 'atom' and 'bash' needs fix
    print("################################################")
    print("######### SELF CHECKING INFO LOGGER ############")
    info = gather_data(path)
    line = ''
    for key, value in info.iteritems():
        line += str(key) + "=" + str(value) + ">"
    for script in scripts_to_check:
        script_status = check_script_running(script)
        #print("The script " + script + " has " + script_status['num_running'] + " instances running")
        for key, value in script_status.iteritems():
           line += str(script + '_' + key) + "=" + str(value) + ">"
    line += '\n'
    print line
    try:
        with open(loc_dic['self_log'], "a") as f:
            f.write(line)
    except:
        print["-LOG ERROR-"]
        pigrow_defs.write_log('checkDHT.py', 'writing dht log failed', loc_dic['err_log'])
