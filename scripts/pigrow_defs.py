import os, sys
import datetime

def load_locs(loc_locs):
    loc_dic = {}
    print("Loading location details")
    with open(loc_locs, "r") as f:
        for line in f:
            s_item = line.split("=")
            loc_dic[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
    #Check for important options,
    if 'loc_switchlog' in loc_dic:
        loc_switchlog = loc_dic['loc_switchlog']
    else:
        print("Switch log not set, run setup.py to configure your pigrow")
        loc_switchlog = '/home/pi/Pigrow/logs/switch_log.txt'
        print('Trying default switch log,')
    if 'loc_settings' in loc_dic:
        loc_settings = loc_dic['loc_settings']
        print("Settings file present")
    else:
        Print("Settings File not loaded, can't continue...")
        exit()
    if 'err_log' in loc_dic:
        err_log = loc_dic['err_log']
    else:
        err_log = "./err.log"
        print("No error log, outputting to current directory")
    return loc_dic

def load_settings(loc_settings, err_log="./err.log"):
    pi_set = {}
    try:
        with open(loc_settings, "r") as f:
            for line in f:
                s_item = line.split("=")
                pi_set[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
        return pi_set
    except:
        print("Settings not loaded, try running pi_setup")
        if not err_log == False:
            with open(err_log, "a") as f:
                line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ settings file error\n'
                f.write(line)
            print("Log writen:" + line)

def write_log(script, message, switch_log):
    line = script + "@" + str(datetime.datetime.now()) + "@" + message + '\n'
    with open(switch_log, "a") as f:
        f.write(line)
    print("Log writen:" + line)

if __name__ == '__main__':
    global loc_locs
    # test1.py executed as script
    # do something
    loc_locs = '/home/pi/Pigrow/config/dirlocs.txt'

    for argu in sys.argv:
        thearg = str(argu).split('=')[0]
        if  thearg == 'locs':
            loc_locs = str(argu).split('=')[1]
        elif  thearg == '-pragmo':
            loc_locs = "/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt"
    load_locs(loc_locs)
