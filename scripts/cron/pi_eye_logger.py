import datetime
import os
import time

from pexpect import pxssh

print("----------------------------------")
print("------Data Logger Pi-Monitor------")
#print ("time on this computer is now: " + str(datetime.datetime.now()))
print("")

#user_name = "magimo"
path = "/Pigrow/"  # from user directory
try:
    # hash out when running from cron or whatever...
    user_name = str(os.getlogin())
except Exception:
    user_name = "pi"

loc_pi_list = "/home/" + user_name + path + "config/pi_list.txt"

pi_list = []
with open(loc_pi_list, "r") as f:
    pi_settings = f.read()
    pi_settings = pi_settings.split("\n")
    for line in pi_settings[0:-1]:
        line = line.split(">")
        hostname = (line[0].split("="))[1]
        username = (line[1].split("="))[1]
        password = (line[2].split("="))[1]
        pi_list.append([hostname, username, password])
        print hostname


def save_log(pi):
    print("")
    print "pitime   = " + str(pitime)
    print "comptime = " + str(datetime.datetime.now())[0:19]
    print "time differnce = " + str(datetime.datetime.now() - pitime)
    print("")
    print "pi's uptime = " + str(uptime)
    print "duration = " + str(pitime - uptime)[0:17]
    print "space_left = " + str(space_left)
    print("")

    log = "host=" + str(pi[0])
    log = log + ">pitime=" + str(pitime)
    log = log + ">comptime=" + str(datetime.datetime.now())[0:19]
    log = log + ">deviation=" + str(datetime.datetime.now() - pitime)
    log = log + ">duration=" + str(pitime - uptime)
    log = log + ">uptime=" + str(uptime)
    log = log + ">space_left=" + str(space_left)
    log = log + "\n"

    print log
    pi_log = "/home/" + user_name + path + \
        "logs/pieye_log_" + str(pi[0].split(".")[-1]) + ".txt"
    with open(pi_log, "a") as f:
        f.write(log)


def get_pi_times():
    global pitime
    global uptime
    global space_left
    global some_error
    # get uptime from pi
    try:
        s.sendline('uptime -s')
        s.prompt()
        frompi = s.before
        frompi = str(frompi)[11:30]
        uptime = datetime.datetime.strptime(frompi, '%Y-%m-%d %H:%M:%S')
        # print "LAST BOOT TIME (uptime) READ AS:" + str   (uptime)
    except Exception:
        print("error reading pi uptime")
        some_error = True
        raise
    # get current date time from pi
    try:
        s.sendline("date +%d:%b_%Y_%H:%M:%S")
        s.prompt()
        pitime = s.before
        pitime = str(pitime)[25:45]
        print pitime
        pitime = datetime.datetime.strptime(pitime, '%d:%b_%Y_%H:%M:%S')
        # print "CURRENT PI DATE TIME READ AS:" + str(pitime)
    except Exception:
        print("error reading pi date")
        some_error = True
    try:
        s.sendline('df -l --output=avail /')
        s.prompt()
        space_left = s.before
        print space_left
        space_left = space_left.split("\n")[2]
    except Exception:
        print("error reading pi disk fullness")
        some_error = True


def log_into_pi(pi):
    # load settings from file and log in to pi
    hostname = pi[0]
    username = pi[1]
    password = pi[2]
    # just keeps hammering away every fifteen secs until manages to connect,
    # no timeout yet
    connected = False
    global s
    counter_log = 0
    while connected == False and not counter_log >= 2:
        try:
            s = pxssh.pxssh()
            s.login(hostname, username, password)
            print("Connected to " + hostname + " ready to interrogate it...")
            connected = True
        except Exception:
            print("exception: ... will try again,")
            counter_log += 1
            time.sleep(10)
            print("trying again...")
            return('FAILED')
    try:
        get_pi_times()
        save_log(pi)
        s.logout()
    except Exception:
        print("Couldn't get proper log recordings but did manage to log in...")
        s.logout()
        raise


def connect_to_pi(pi):
    counter = 0
    some_error = True
    while some_error == True and not counter >= 9:
        if some_error == True:
            counter = counter + 1
            #print("Preparing to check up on; " + str(pi[0]))
            log_into_pi(pi)
            some_error = False  # this is so it loops until it gets good results then stops
        else:
            print("had enough goes now")
            pitime = 0
            uptime = "failed to respond"
            break


for pi in pi_list:
    connect_to_pi(pi)
