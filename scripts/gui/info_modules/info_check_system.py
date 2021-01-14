#!/usr/bin/python3
import os
homedir = os.getenv("HOME")

def show_info():
    #check pi for hdd/sd card space
    script_list = ["sensors/log_sensor_module.py", 'cron/camcap.py', 'cron/picamcap.py', 'cron/selflog.py', 'cron/selflog_adv.py', 'cron/donothing.py']
    msg = ""
    for script_base in script_list:
        script = homedir + "/Pigrow/scripts/" + script_base
        out =  os.popen('pidof ' + script + ' -x').read()
        list_of_pids = out.strip()
        msg += script # .split("/")[-1] + "\n"
        if not list_of_pids == "":
            list_of_pids = list_of_pids.split()
            if len(list_of_pids) > 1:
                msg += " has " + str(len(list_of_pids)) + " instances" + '\n'
            else:
                msg += '\n'
            for pid in list_of_pids:
                out =  os.popen('cat /proc/' + pid + '/status |grep State').read()
                status = out.replace("State:", "").strip()
                msg += "  -- pid " + pid + " : " + status
                # note arguments it was run with
                out =  os.popen('ps --no-headers ' + pid).read()
                args = out.split(script)[1].strip()
                msg += " with args " + args + "\n"
        else:
            cmd = 'ls -laru' + script + ' | cut -f6,7,8 -d" "'
            print(cmd)
            out =  os.popen(cmd).read()
            msg += "\n   None currently running. Last accessed " + out + "\n"





    return msg

if __name__ == '__main__':
    print(show_info())
