#!/usr/bin/python3
import os
import sys
import fcntl
import errno

def get_lock(f):
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except IOError as e:
            # raise on unrelated IOErrors
            if e.errno != errno.EAGAIN:
                raise
            else:
                time.sleep(0.1)

def write_updated_tankstat(tank, vol, active):
    # read fresh in case edited since we started running
    # only change the lines we need to in case there's other info in the file
    c_ml = False
    c_a  = False
    homedir = os.getenv("HOME")
    t_stat_path = homedir + "/Pigrow/logs/tankstat_" + tank + ".txt"
    #
    if os.path.isfile(t_stat_path):
        with open(t_stat_path, "r+") as f:
            # Lock tank stat file
            get_lock(f)
            # read contents
            t_stat_txt = f.read()
            # create list of lines and edit current ml
            #     this preserves any other info that might be in the file
            t_stat_txt = t_stat_txt.splitlines()
            new_txt = []

            for line in t_stat_txt:
                if "current_ml=" in line:
                    if not vol == "":
                        line = "current_ml=" + str(vol)
                    c_ml = True
                elif "active=" in line:
                    if active.lower()=="true":
                        line = "active=true"
                    elif active.lower()=="false":
                        line = "active=false"
                    c_a = True
                new_txt.append(line)

            # add if not alraedy included
            if c_ml == False:
                new_txt.append("current_ml=" + str(vol))
            if c_a == False:
                if active.lower()=="true":
                    new_txt.append("active=true")
                elif active.lower()=="false":
                    new_txt.append("active=false")

            # create text str for file from list
            tankstat = ""
            for line in new_txt:
                if not line.strip() == "":
                    tankstat += line.strip() + "\n"
            # write new text
            f.seek(0)
            f.write(tankstat)
            f.truncate()
            # unlock file
            fcntl.flock(f, fcntl.LOCK_UN)
    else:
        print(" No tankstate file found, creating a new one for", tank)
        tankstat = ""
        # vol
        if not vol == "":
            tankstat += "current_ml=" + str(vol) + " "
        # active
        if active.lower()=="true":
            tankstat += "active=true"
        elif active.lower()=="false":
            tankstat += "active=false"
        # write file
        # (no need for lock, there isn't a file yet)
        with open(t_stat_path, "w") as f:
            f.write(tankstat)

    print(" Written;")
    print(tankstat)


if __name__ == '__main__':

    tank = ""
    vol = ""
    active = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            thevalue = str(argu).split('=')[1]
            if thearg == 'tank':
                tank = thevalue
            if thearg == "vol" or thearg == "ml":
                vol = float(thevalue)
            if thearg == 'active':
                active = thevalue

        elif 'help' in argu or argu == '-h':
            print(" Set the tankstat file to a supplied water level")
            print("")
            print(" This script is designed to be triggered by a float switch")
            print(" or similar, can be used for any purpose.")
            print("")
            print(" - Initial version, should only be used for refilling when pump")
            print("   not activated, or on empty to disable pumps.")
            print("")
            print(" --- This version does not yet kill currently running pumps ---")
            print(" ")
            print(" ")
            print(" tank=tank name")
            print(" active=[true,false]   - optional set to enable tank")
            print("")
            print(" vol=NUM  -  remaining tank vol ml")
            print("  ml=NUM   (same as above)")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("tank=TANK NAME")
            print("vol=NUM")
            print("active=[true,false]")
            sys.exit(0)

    if not tank=="":
        if not active == "" or not vol == "":
            write_updated_tankstat(tank, vol, active)
        else:
            print("Needs to have either a vol= or active= supplied.")
    else:
        print(" Need's to have tank=TANKNAME ")
