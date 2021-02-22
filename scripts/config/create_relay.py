#!/usr/bin/python3
import datetime, sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

##
## Command line arguments
##
new_name = ""
for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'name':
            new_name = theval
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("  Tool for generating new relay scripts")
        print("")
        print("  name=          - the name of the new relay")
        sys.exit()
    elif argu == '-flags':
        print("name=")
        sys.exit()
    else:
        print(" command line argument not understood; " + str(argu))


## Check new_name is valid
new_name = new_name.replace(" ", "")
cleaned_name = ""
for letter in new_name:
    if letter.isalnum():
        cleaned_name += letter

if cleaned_name == "":
    print(" A name for the new relay must be supplied")
    print(" use name=relay_name")
    sys.exit()

print(" Creating new relay switch - " + cleaned_name)

# load example scripts
on_relay_blank = homedir + "/Pigrow/resources/blank_switches/blank_on.py"
off_relay_blank = homedir + "/Pigrow/resources/blank_switches/blank_off.py"
on_name = cleaned_name + "_on.py"
off_name = cleaned_name + "_off.py"

print("   - using template " + on_relay_blank)
print("              and   " + off_relay_blank)

with open(on_relay_blank, "r") as f:
    on_blank = f.read()
with open(off_relay_blank, "r") as f:
    off_blank = f.read()

# make changes to the scripts
new_on = on_blank.replace("BLANK", cleaned_name)
new_off = off_blank.replace("BLANK", cleaned_name)

# save scripts
new_on_relay_path = homedir + '/Pigrow/scripts/switches/' + on_name
with open(new_on_relay_path, "w") as sp:
    sp.write(new_on)
chmod_cmd_on = "chmod +x " + new_on_relay_path
print( chmod_cmd_on)
out =  os.popen(chmod_cmd_on).read()
print(out)

new_off_relay_path = homedir + '/Pigrow/scripts/switches/' + off_name
with open(new_off_relay_path, "w") as sp:
    sp.write(new_off)
chmod_cmd_off = "chmod +x " + new_off_relay_path
out =  os.popen(chmod_cmd_off).read()


# show off that we've done it and demand praise.
print(on_name, " written to ", new_on_relay_path)
print(off_name, " written to ", new_off_relay_path)
