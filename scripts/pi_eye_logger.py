from pexpect import pxssh
import time
import datetime
print("----------------------------------")
print("------Data Logger Pi-Monitor------")
#print ("time on this computer is now: " + str(datetime.datetime.now()))
print("")
loc_pi_settings = '/home/pi/Pigrow/config/pi_eye_settings.txt'
pi_log = '/home/pi/Pigrow/logs/pi_eye_log.txt'

some_error = False
#load settings from file and log in to pi
with open(loc_pi_settings, "r") as f:
    pi_settings = f.read()
    pi_settings = pi_settings.split("\n")
    hostname = (pi_settings[0].split("="))[1]
    username = (pi_settings[1].split("="))[1]
    password = (pi_settings[2].split("="))[1]

#just keeps hammering away every ten secs until manages to connect, no timeout yet
connected = False
while connected == False:
    try:
        s = pxssh.pxssh()
        s.login (hostname, username, password)
        print("Connected to " + hostname + " ready to interrogate it...")
        connected = True 
    except:
        print("exception: ... will try again,")
        time.sleep(10)
        print("trying again...")


def get_pi_times():
    global pitime
    global uptime
    global some_error
    #get uptime from pi
    try:
        s.sendline('uptime -s')
        s.prompt()
        frompi = s.before  
        frompi = str(frompi)[11:30]
        uptime = datetime.datetime.strptime(frompi, '%Y-%m-%d %H:%M:%S')
        #print "LAST BOOT TIME (uptime) READ AS:" + str   (uptime)
    except:
        print("uptime date error")
        some_error = True
    #get current date time from pi
    try:
        s.sendline("date +%d:%b_%Y_%H:%M:%S")
        s.prompt()
        pitime = s.before
        pitime = str(pitime)[25:45]
        pitime = datetime.datetime.strptime(pitime, '%d:%b_%Y_%H:%M:%S')
        #print "CURRENT PI DATE TIME READ AS:" + str(pitime)
    except:
        print("pi date error") 
        some_error = True
get_pi_times()
s.logout()

counter = 0
while some_error == True and counter != 9:
    if some_error ==  True:  
        print("Trying again...")
        counter = counter + 1
        get_pi_times()
    else:
        print("had enough goes now")
        pitime = 0
        uptime = "failed to respond" 
        break



print("")
print "pitime   = " + str(pitime)
print "comptime = " + str(datetime.datetime.now())[0:19]
print "time differnce = " + str(datetime.datetime.now() - pitime)
print("")
print "pi's uptime = " + str(uptime)
print "duration = " + str(pitime - uptime)[0:17]
print("")

log = "host="+hostname+">pitime="+str(pitime)+">comptime="+str(datetime.datetime.now())[0:19]+">deviation="+str(datetime.datetime.now() - pitime)+">duration="+str(pitime-uptime)+">uptime="+str(uptime)+"\n"

print log

with open(pi_log, "a") as f:
    f.write(log)


