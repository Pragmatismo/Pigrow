#!/usr/bin/python
try:
    if not os.path.exists('/home/pi/Pigrow/caps/'):
        os.makedirs('/home/pi/Pigrow/caps/')
    if not os.path.exists('/home/pi/Pigrow/graphs/'):
        os.makedirs('/home/pi/Pigrow/graphs/')
    if not os.path.exists('/home/pi/Pigrow/logs/'):
        os.makedirs('/home/pi/Pigrow/logs/')
except:
    print("Couldn't make dirs, possinly not a pi...")

path = "/home/pragmo/pigitgrow/Pigrow/resources/"

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
        print("- Doesn't look like the ADafruit DHT driver is installed,")
        print("- Installing...")
        os.chdir(path)
        print("- Downloading Adafruit_Python_DHT from Github")
        os.system("git clone https://github.com/adafruit/Adafruit_Python_DHT.git")
        os.chdir( path + "Adafruit_Python_DHT/")
        print("- Updating your apt list and installing dependencies,")
        os.system("sudo apt-get update")
        os.system("sudo apt-get install build-essential python-dev python-openssl")
        print("- Dependencies installed, running --: sudo python setup.py install :--")
        os.system("sudo python setup.py install")
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
        raise
os.chdir(path)
print("")
print(" Installing dependencies for pigrow code...")
print(" - Using pip")
try:
    import praw, matplotlib, pexpect
    from crontab import CronTab
    print(" Required dependencies already installed.")
except:
    try:
        print(" Required dependencies not installed, attempting to install...")
        os.system("sudo pip install crontab praw matplotlib pexpect")
    except:
        print("Sorry, -- sudo pip install python-crontab praw matplotlib pexpect -- didn't work, try it manually.")
        print("")
        raise
print(" - Using apt-get")
print("")
try:
    os.system("sudo apt-get install sshpass uvccapture mpv")
except:
    print("Sorry, -- sudo apt-get install sshpass uvccapture mpv -- didn't work, try it manually..")
    raise
print("Install process complete, all dependencies installed.")
print("")
