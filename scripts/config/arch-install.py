#!/usr/bin/python
import time
import socket
import os

homedir = os.getenv("HOME")

## UVCCAPTURE IS NOT RESOLVED
def is_connected():
    site = "www.reddit.com"
    try:
        host = socket.gethostbyname(site)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

while is_connected() == False:
    time.sleep(10)

print("Found reddit, internet is up")

try:
    if not os.path.exists(homedir + '/Pigrow/caps/'):
        os.makedirs(homedir + '/Pigrow/caps/')
    if not os.path.exists(homedir + '/Pigrow/graphs/'):
        os.makedirs(homedir + '/Pigrow/graphs/')
    if not os.path.exists(homedir + '/Pigrow/logs/'):
        os.makedirs(homedir + '/Pigrow/logs/')
except:
    print("Couldn't make dirs, possinly not a pi...")

path = homedir + "/Pigrow/resources/"

print("checking and installing pip for python2.7")
os.system("sudo pacman -S python2-pip pkgfile libv4l")



print("Checking Dependencies...")
print("  - DHT Sensor;")
print(" This is for reading the Temp and Humid sensor, it's supplied by")
print("    https://en.wikipedia.org/wiki/Adafruit_Industries")
print("")
print( "   https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated")
print("")
try:
    import Adafruit_DHT
    print("- Adafruit DHT driver is installed and working")
    print("- ")
    except:
    try:
        print("- Doesn't look like the Adafruit DHT driver is installed,")
        print("- Installing...")
        os.chdir(path)
        print("- Downloading Adafruit_Python_DHT from Github")
        os.system("git clone https://github.com/adafruit/Adafruit_Python_DHT.git")
        ada_path = path + "Adafruit_Python_DHT/"
        os.chdir(ada_path)
        print("- Updating your apt list and installing dependencies,")
        print("- Dependencies installed, running --: sudo python setup.py install --force-pi :--")
        os.system("sudo python2 " + ada_path + "setup.py install --force-pi")
        print("- Done! ")
        try:
            import Adafruit_DHT

            print("Adafruit_DHT Installed and working.")
        except:
            print("...but it doens't seem to have worked...")
            print(" Try running this script again, if not then")
            print(" follow the manual install instructions above")
            print(" and then try this script again...")
            print("")
    except:
        print("Install failed, use the install instructions linked above to do it manually.")
        # raise
os.chdir(path)
os.chdir(path)
print("")
print(" Installing dependencies for pigrow code...")
print(" - Using pip")
try:
    import praw, pexpect, python, crontab
    #from crontab import CronTab #python-crontab #using apt
    print(" Required dependencies already installed.")
except:
    try:
        print(" Required dependencies not installed, attempting to install...")
        os.system("sudo pip2 install praw pexpect python-crontab crontab pyopenssl"
                  "")
    except:
        print("Sorry, -- sudo pip2 install praw pexpect python-crontab crontab-- didn't work, try it manually.")
        print("")
        #raise
print(" - Using pacman")
print("")
try:
    os.system("sudo pacman -S python-matplotlib sshpass uvccapture mpv python-dev")
except:
    print("Sorry, -- sudo apt-get --yes install python-matplotlib sshpass mpv python-crontab-- didn't work, try it manually..")
    #raise
print("")
print("Install process complete, all dependencies installed (or failed...)")
print("")
