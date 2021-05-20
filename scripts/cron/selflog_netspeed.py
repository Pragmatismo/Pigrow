#!/usr/bin/python3
import datetime
import os, sys
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
        print(" Pigrow Raspberry Pi Net Speed Self-Logger")
        print(" ")
        print("Creates a log of up and down net speed")
        print("")
        print("The log created can be graphed with the remote_gui")
        print("")
        sys.exit(0)
    if argu == '-flags':
        print("")
        sys.exit(0)
def speed_test():
    speed_info = os.popen('/usr/local/bin/speedtest-cli --csv').read()
    speed_info = speed_info.split(',')
    speed_data = {}
    speed_data['Server ID']    =speed_info[0].strip()
    speed_data['Sponsor']      =speed_info[1].strip()
    speed_data['Server_Name']  =speed_info[2].strip()
    speed_data['Distance']     =speed_info[4].strip()
    speed_data['Ping']         =speed_info[5].strip()
    speed_data['Download']     =speed_info[6].strip()
    speed_data['Upload']       =speed_info[7].strip()
    return speed_data

if __name__ == '__main__':
    scripts_to_check = ['reddit_settings_ear.py','checkDHT.py']# 'chromium-browse'] #this doesn't work :( works for 'atom' and 'bash' needs fix
    print(" ######################################")
    print("######### Net Speed  LOGGER ############")
    line = "timenow=" + str(datetime.datetime.now()) + ">"
    speed_data = speed_test()
    for key, value in sorted(speed_data.items()):
        line += str(key) + "=" + str(value) + ">"
    line = line[:-1] + "\n"
    # find the log and add a line to it
    if 'netspeed_log' in loc_dic:
        log_location = loc_dic['netspeed_log']
    else:
        log_location = homedir + '/Pigrow/logs/netspeed_log.txt'
    try:
        with open(log_location, "a") as f:
            f.write(line)
            print(" - log written - ", line)
            print("----")
    except:
        print["-LOG ERROR-"]
        pigrow_defs.write_log('selflog_netspeed.py', 'writing self log failed', loc_dic['err_log'])
