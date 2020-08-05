#!/usr/bin/python
import os, sys
import datetime

homedir = os.getenv("HOME")
def load_locs(loc_locs):
    loc_dic = {}
    print("Loading location details")
    with open(loc_locs, "r") as f:
        for line in f:
            s_item = line.split("=")
            loc_dic[s_item[0]]=s_item[1].rstrip() #adds each setting to dictionary
    #Check for important options, but doe snothing at the moment...
    if 'loc_switchlog' in loc_dic:
        loc_switchlog = loc_dic['loc_switchlog']
    else:
        print("Switch log not set, run setup.py to configure your pigrow")
        loc_switchlog = homedir + '/Pigrow/logs/switch_log.txt'
        print('Trying default switch log,')
    if 'loc_settings' in loc_dic:
        loc_settings = loc_dic['loc_settings']
        print("Settings file present")
    else:
        print("Settings File not loaded, can't continue...")
        exit()
    if 'err_log' in loc_dic:
        err_log = loc_dic['err_log']
    else:
        err_log = "./err.log"
        print("No error log, outputting to current directory -but not because this code does nothing now")
    return loc_dic

def load_settings(loc_settings, err_log="./err.log"):
    pi_set = {}
    try:
        with open(loc_settings, "r") as f:
            for line in f:
                s_item = line.split("=")
                pi_set[s_item[0]]=s_item[1].rstrip() #adds each setting to dictionary
        return pi_set
    except:
        print("Settings not loaded, try running pi_setup")
        if not err_log == False:
            with open(err_log, "a") as f:
                line = 'pigrow_defs.py @' + str(datetime.datetime.now()) + '@ settings file error\n'
                f.write(line)
            print("Log writen:" + line)

def save_settings(pi_set, loc_settings, err_log="./err.log"):
    print("Saving Settings...")
    try:
        with open(loc_settings, "w") as f:
            for a,b in pi_set.items():
                try:
                    s_line = str(a) +"="+ str(b) +"\n"
                    f.write(s_line)
                    #print s_line
                except:
                    print("ERROR SETTINGS FILE ERROR SETTING NOT SAVED _ SERIOUS FAULT!")
            print(" - Settings saved to file - ")
    except:
        print("Settings not saved!")
        with open(err_log, "a") as ef:
            line = 'update_reddit.py @' + str(datetime.datetime.now()) + '@ settings file save error\n'
            ef.write(line)
        print("Log writen:" + line)

def read_setting(loc_settings, setting):
    settings = load_settings(loc_settings)
    for f_setting, f_value in settings.items():
        if setting == f_setting:
            print(" Found " + f_setting + " = " + f_value + " in " + loc_settings)
            return f_value
    print(f_setting + " not found in " + loc_settings)
    return ""

def change_setting(loc_settings, setting, value):
    settings = load_settings(loc_settings)
    found = False
    for f_setting, f_value in settings.items():
        if setting == f_setting:
            settings[setting] = value
            found = True
    if not found == True:
        settings[setting] = value
    print("Changed to - " + settings[setting])
    save_settings(settings, loc_settings)


def write_log(script, message, switch_log):
    line = script + "@" + str(datetime.datetime.now()) + "@" + message + '\n'
    with open(switch_log, "a") as f:
        f.write(line)
    print("Log writen:" + line)

def disk_full(path):
    st = os.statvfs(path)
    free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
        percent = ret = (float(used) / total) * 100
    except ZeroDivisionError:
        percent = 0
    return total, used, free, round(percent, 1)

def archive_grow(loc_dic, name, compress=False):
    responce =  "Request to archive grow as " + name
    responce += "  \nCurrent Status;  \n"
    log_path = loc_dic['log_path']
    graph_path = loc_dic['graph_path']
    caps_path = loc_dic['caps_path']
    responce += "Image Capture Dicrectory; " + str(len(os.listdir(caps_path))) + " files.  \n"
    responce += "Graph Dicrectory; " + str(len(os.listdir(graph_path))) + " files.  \n"
    responce += "Log Dicrectory; " + str(len(os.listdir(log_path))) + " files.  \n"
    d_total, d_used, d_free, d_percent = disk_full(loc_dic['path'])
    responce += "Current Filesystem has " + str(d_free) + " free space, " + str(d_percent) + "% remaining.  \n"
    archive_path = loc_dic['path'] + "archive/" + name

    dir_possible = str(archive_path)
    num = 0
    while os.path.exists(dir_possible) == True:
        num = num + 1
        dir_possible = dir_possible + "_"+str(num)+"_"
    archive_path = dir_possible

    responce += "Created, " + archive_path
    from shutil import copytree, move
    copytree(log_path, archive_path+"/logs/")
    responce += " and copied logs, "
    source_logs = os.listdir(log_path)
    for log in source_logs:
        if log in os.listdir(archive_path+"/logs/"):
            #responce += "log File, " + str(log) + " copied and cleared, "
            os.remove(log_path + log)
    if compress==False:
        cap_not_copy = 0
        cap_copy = 0
        os.mkdir(archive_path + "/caps/")
        for pic in os.listdir(caps_path):
            move(caps_path+pic, archive_path+"/caps/")
            if pic in os.listdir(archive_path+"/caps/"):
                #os.remove(caps_path + pic)
                cap_copy += 1
            else:
                cap_not_copy += 1
        if cap_not_copy > 0:
            responce += "Sorry, copied " +str(cap_copy)+" images but " + str(cap_not_copy) + " pictures didn't copy "
        else:
            responce += str(cap_copy) + "images copied, "
        if len(os.listdir(caps_path)) == 0:
            responce += 'no images to copy '
        os.mkdir(archive_path+"/graphs/")
        for graph in os.listdir(graph_path):
            move(graph_path+graph, archive_path+"/graphs/")
        responce += "and " + str(len(os.listdir(archive_path+"/graphs/"))) + " graphs. "
    else:
        responce += "ignoring graohs, and compressing caps folder into a timelapse video. "
        responce += " --well actually i'm just pretending to for now, sorry... "
        response += "  \n  \n I won't delete all your files tho either, so don't worry... (do a normal archive)"
    return responce

def set_condition(condition_name, trig_direction, cooldown="none"):
    trigger_conditions_path = homedir + "/Pigrow/logs/trigger_conditions.txt"    # trigger conditions file location
    # detrimne cooldown
    if cooldown.isdigit():
        cooldown_time = datetime.datetime.now() + datetime.timedelta(minutes=int(cooldown))
        #print("!pgd! - Setting cooldown to " + str(cooldown_time))
        cooldown = datetime.datetime.timestamp(cooldown_time)
    # read conditiosn file
    #print("!pgd! - writing conditions file")
    trig_con_found = False
    trig__con_tosave = ""
    if os.path.isfile(trigger_conditions_path):
        with open(trigger_conditions_path, 'r') as f:
            trigger_conditions = f.readlines()
        # check for and change if condition exists
        for line in trigger_conditions:
            line_split = line.split(",")
            if len(line_split) == 3:
                if line_split[0] == condition_name:
                    trig_con_found = True
                    line = line_split[0] + "," +  str(trig_direction) + "," + str(cooldown) + "\n"
                    #print("!pgd! - Recording - " + line)
            trig__con_tosave += line
    # if the condition doesn't exist add it
    if trig_con_found == False:
        trig__con_tosave += condition_name + "," + str(trig_direction) + "," + str(cooldown) + "\n"
    # save file
    with open(trigger_conditions_path, 'w') as f:
        f.write(trig__con_tosave)
    #print("!pgd! - written; ")
    #print(trig__con_tosave)
    #print("!pgd!------------")



if __name__ == '__main__':
    global loc_locs
    # test1.py executed as script
    # do something
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'

    for argu in sys.argv:
        thearg = str(argu).split('=')[0]
        if  thearg == 'locs':
            loc_locs = str(argu).split('=')[1]
    load_locs(loc_locs)
