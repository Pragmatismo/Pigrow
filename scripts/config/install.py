#!/usr/bin/python
import os
import socket
import time


def is_connected():
    site = "www.reddit.com"
    try:
        host = socket.gethostbyname(site)
        s = socket.create_connection((host, 80), 2)
        return True
    except Exception: pass
    return False


while is_connected() == False:
    time.sleep(10)

print("Found reddit, internet is up")

try:
    if not os.path.exists('/home/pi/Pigrow/caps/'):
        os.makedirs('/home/pi/Pigrow/caps/')
    if not os.path.exists('/home/pi/Pigrow/graphs/'):
        os.makedirs('/home/pi/Pigrow/graphs/')
    if not os.path.exists('/home/pi/Pigrow/logs/'):
        os.makedirs('/home/pi/Pigrow/logs/')
except Exception: print("Couldn't make dirs, possinly not a pi...")

path = "/home/pi/Pigrow/resources/"

print("Checking Dependencies...")
print("  - DHT Sensor;")
print(" This is for reading the Temp and Humid sensor, it's supplied by")
print("    https://en.wikipedia.org/wiki/Adafruit_Industries")
print("")
print("   https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated")
print("")
try:
    import Adafruit_DHT
    print("- Adafruit DHT driver is installed and working")
    print("- ")
except Exception: try:
        print("- Doesn't look like the ADafruit DHT driver is installed,")
        print("- Installing...")
        os.chdir(path)
        print("- Downloading Adafruit_Python_DHT from Github")
        os.system("git clone https://github.com/adafruit/Adafruit_Python_DHT.git")
        ada_path = path + "Adafruit_Python_DHT/"
        os.chdir(ada_path)
        print("- Updating your apt list and installing dependencies,")
        os.system("sudo apt-get update --yes")
        os.system(
            "sudo apt-get install --yes build-essential python-dev python-openssl")
        print("- Dependencies installed, running --: sudo python setup.py install :--")
        os.system("sudo python " + ada_path + "setup.py install")
        print("- Done! ")
        try:
            import Adafruit_DHT
            print("Adafruit_DHT Installed and working.")
        except Exception: print("...but it doens't seem to have worked...")
            print(" Try running this script again, if not then")
            print(" follow the manual install instructions above")
            print(" and then try this script again...")
            print("")
    except Exception:        print(
            "Install failed, use the install instructions linked above to do it manually.")
        # raise
os.chdir(path)
print("")
print(" Installing dependencies for pigrow code...")
print(" - Using pip")
try:
    import praw
    import pexpect
    # from crontab import CronTab #python-crontab #using apt
    print(" Required dependencies already installed.")
except Exception:    try:
        print(" Required dependencies not installed, attempting to install...")
        os.system("sudo pip install praw pexpect")
    except Exception:        print("Sorry, -- sudo pip install praw pexpect -- didn't work, try it manually.")
        print("")
        # raise
print(" - Using apt-get")
print("")
try:
    os.system(
        "sudo apt-get --yes install python-matplotlib sshpass uvccapture mpv python-crontab")
except Exception:    print("Sorry, -- sudo apt-get --yes install python-matplotlib sshpass uvccapture mpv python-crontab-- didn't work, try it manually..")
    # raise
print("")
print("Install process complete, all dependencies installed (or failed...)")
print("")
