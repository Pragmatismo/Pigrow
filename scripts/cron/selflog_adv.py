#!/usr/bin/python
import datetime, time
import os, sys
import psutil
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'adv_selflog.py'
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
loc_dic = pigrow_defs.load_locs(loc_locs)
path = loc_dic["path"]

##
## Raspberry Advanced Pi Self-Logger
##    This grabs a whole load of info and sticks it in a log file
##

for argu in sys.argv:
    if argu == '-h' or argu == '--help':
        print(" Pigrow Raspberry Pi Advanced Self-Logger")
        print(" ")
        print("Creates a log of loads of metrics that can be used to")
        print("monitor the pigrows health.")
        print("")
        print("The log created can be graphed with the remote_gui")
        print("")
        sys.exit(0)
    if argu == '-flags':
        print("")
        sys.exit(0)

def psutil_info():
    ps_util_info = {}
    ps_util_info['timenow'] = datetime.datetime.now()
    ps_util_info['cpu_temp'] = psutil.sensors_temperatures(fahrenheit=False)['bcm2835_thermal'][0][1]
    ps_util_info['cpu_ctx_switches']    = psutil.cpu_stats()[0]
    ps_util_info['cpu_interrupts']     = psutil.cpu_stats()[1]
    ps_util_info['cpu_soft_interrupts'] = psutil.cpu_stats()[2]
    ps_util_info['cpu_frequency']     = psutil.cpu_freq(percpu=False)[0]
    ps_util_info['min_cpu_frequency'] = psutil.cpu_freq(percpu=False)[1]
    ps_util_info['max_cpu_frequency'] = psutil.cpu_freq(percpu=False)[2]
    ps_util_info['load_ave1']  = psutil.getloadavg()[0]
    ps_util_info['load_ave5']  = psutil.getloadavg()[1]
    ps_util_info['load_ave15'] = psutil.getloadavg()[2]
    ps_util_info['vmem_total']     = psutil.virtual_memory()[0]
    ps_util_info['vmem_available'] = psutil.virtual_memory()[1]
    ps_util_info['vmem_pcent']     = psutil.virtual_memory()[2]
    ps_util_info['vmem_used']      = psutil.virtual_memory()[3]
    ps_util_info['vmem_free']      = psutil.virtual_memory()[4]
    ps_util_info['vmem_active']    = psutil.virtual_memory()[5]
    ps_util_info['swap_pcent'] = psutil.swap_memory()[3]
    ps_util_info['swap_in']    = psutil.swap_memory()[4]
    ps_util_info['swap_out']   = psutil.swap_memory()[5]
    ps_util_info['disk_used']        = psutil.disk_usage("/home/")[1]
    ps_util_info['disk_free']        = psutil.disk_usage("/home/")[2]
    ps_util_info['disk_usage_pcent'] = psutil.disk_usage("/home/")[3]
    # Disk In-Out
    ps_util_info['read_count']         = psutil.disk_io_counters(perdisk=False, nowrap=True)[0]
    ps_util_info['write_count']        = psutil.disk_io_counters(perdisk=False, nowrap=True)[1]
    ps_util_info['read_bytes']         = psutil.disk_io_counters(perdisk=False, nowrap=True)[2]
    ps_util_info['write_bytes']        = psutil.disk_io_counters(perdisk=False, nowrap=True)[3]
    ps_util_info['read_time']          = psutil.disk_io_counters(perdisk=False, nowrap=True)[4]
    ps_util_info['write_time']         = psutil.disk_io_counters(perdisk=False, nowrap=True)[5]
    ps_util_info['read_merged_count']  = psutil.disk_io_counters(perdisk=False, nowrap=True)[6]
    ps_util_info['write_merged_count'] = psutil.disk_io_counters(perdisk=False, nowrap=True)[7]
    ps_util_info['busy_time']          = psutil.disk_io_counters(perdisk=False, nowrap=True)[8]
    # Net In-Out
    ps_util_info['bytes_sent']   = psutil.net_io_counters(pernic=False, nowrap=True)[0]
    ps_util_info['bytes_recv']   = psutil.net_io_counters(pernic=False, nowrap=True)[1]
    ps_util_info['packets_sent'] = psutil.net_io_counters(pernic=False, nowrap=True)[2]
    ps_util_info['packets_recv'] = psutil.net_io_counters(pernic=False, nowrap=True)[3]
    ps_util_info['errin']        = psutil.net_io_counters(pernic=False, nowrap=True)[4]
    ps_util_info['errout']       = psutil.net_io_counters(pernic=False, nowrap=True)[5]
    ps_util_info['dropin']       = psutil.net_io_counters(pernic=False, nowrap=True)[6]
    ps_util_info['dropout']      = psutil.net_io_counters(pernic=False, nowrap=True)[7]
    return ps_util_info

def check_scripts(script):
    # Check stats of running process
    pid = os.popen('pidof ' + script + ' -x').read()
    scripts_data = {}
    if not pid == "":
        p = psutil.Process(int(pid))
        with p.oneshot():
            name = p.name()
            # status = p.status()
            key = script.split('.')[0] + "_"
            scripts_data[key + 'cpu_time_user']   = p.cpu_times()[0]
            scripts_data[key + 'cpu_time_system'] = p.cpu_times()[1]
            scripts_data[key + 'create_time'] = p.create_time()
            scripts_data[key + 'rss']    = p.memory_info()[0]
            scripts_data[key + 'vms']    = p.memory_info()[1]
            scripts_data[key + 'shared'] = p.memory_info()[2]
            scripts_data[key + 'text']   = p.memory_info()[3]
            scripts_data[key + 'lib']    = p.memory_info()[4]
            scripts_data[key + 'data']   = p.memory_info()[5]
            scripts_data[key + 'dirty']  = p.memory_info()[6]
            scripts_data[key + 'read_count']  = p.io_counters()[0]
            scripts_data[key + 'write_count'] = p.io_counters()[1]
            scripts_data[key + 'read_bytes']  = p.io_counters()[2]
            scripts_data[key + 'write_bytes'] = p.io_counters()[3]
            scripts_data[key + 'read_chars']  = p.io_counters()[4]
            scripts_data[key + 'write_chars'] = p.io_counters()[5]
    return scripts_data

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return {'uptime_seconds':uptime_seconds}

def count_processes():
    user = 'pi'
    ps_all_info = os.popen('ps -A --no-headers').read()
    ps_sshd = os.popen('ps -C sshd --no-headers').read()
    ps_for_user = os.popen('ps -U ' + user + ' --no-headers').read()
    ps_for_root = os.popen('ps -U root --no-headers').read()
    ps_all_users = os.popen('ps aux --no-header -w').read()
    ps_all_threads = os.popen('ps -AL --no-headers').read()
    ps_all_info = len(ps_all_info.splitlines())
    ps_sshd = len(ps_sshd.splitlines())
    ps_for_user = len(ps_for_user.splitlines())
    ps_for_root = len(ps_for_root.splitlines())
    ps_all_users = len(ps_all_users.splitlines())
    ps_all_threads = len(ps_all_threads.splitlines())
    return {'ps_all_info':ps_all_info,
            'ps_sshd':ps_sshd,
            'ps_for_user':ps_for_user,
            'ps_for_root':ps_for_root,
            'ps_all_users':ps_all_users,
            'ps_all_threads':ps_all_threads
            }

def gather_data():
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.split(":")[0]=="MemTotal":
                memtotal = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemAvailable":
                memavail = line.split(":")[1].strip()
            elif line.split(":")[0]=="MemFree":
                memfree = line.split(":")[1].strip()
    #send back data in a dictionary
    return {'memtotal':memtotal,
            'memfree':memfree,
            'memavail':memavail,
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

if __name__ == '__main__':
    scripts_to_check = ['reddit_settings_ear.py','checkDHT.py']# 'chromium-browse'] #this doesn't work :( works for 'atom' and 'bash' needs fix
    print("####################################################")
    print("######### ADV SELF CHECKING INFO LOGGER ############")
    info = gather_data()
    #print('Found ' + str(len(info)) + ' graphable metrics')
    info.update(count_processes())
    #print('Found ' + str(len(info)) + ' graphable metrics')
    info.update(get_uptime())
    #print('Found ' + str(len(info)) + ' graphable metrics')
    info.update(psutil_info())
    #print('Found ' + str(len(info)) + ' graphable metrics')
    scripts_to_check = ['reddit_settings_ear.py','checkDHT.py']
    for script in scripts_to_check:
        info.update(check_scripts(script))
    #print('Increased to ' + str(len(info)) + ' with active script info')

    #
    # Make the dictionary into a line of text for the log
    #
    line = ''
    for key, value in info.items():
        line += str(key) + "=" + str(value) + ">"
        #print(key, " = ", value)
    for script in scripts_to_check:
        script_status = check_script_running(script)
        for key, value in script_status.items():
           line += str(script + '_' + key) + "=" + str(value) + ">"
    line += '\n'
    # find the log and add a line to it
    if 'adv_self_log' in loc_dic:
        log_location = loc_dic['adv_self_log']
    else:
        log_location = homedir + '/Pigrow/logs/adv_selflog.txt'
    try:
        with open(log_location, "a") as f:
            f.write(line)
            #print(" - log written - ", line)
    except:
        print["-LOG ERROR-"]
        pigrow_defs.write_log('adv_selflog.py', 'writing self log failed', loc_dic['err_log'])
