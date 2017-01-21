#!/usr/bin/python
import os, sys

print(" ##  Pigrow Logs Downloader ")
try:
    user_name = str(os.getlogin())  #hash this line out if it causes problem, autograbs username
    logsdir = "/home/"+user_name+"/frompigrow/logs/"
    if not os.path.exists(logsdir):
        os.makedirs(logsdir)
except:
    print("Unsure what usename to use, setting log dir to ./")
    logsdir = "./"
    user_name = "pi"

target_address = "pi@192.168.1.10"
target_pass = "raspberry"
target_path = "/home/pi/Pigrow/logs/"

for argu in sys.argv[1:]:
    thearg = str(argu).split('=')[0]
    if  thearg == 'to' or thearg == 'logsdir':
        logsdir = str(argu).split('=')[1]
    elif thearg == 'ta':
        target_address = str(argu).split('=')[1]
    elif thearg == 'tp':
        target_pass = str(argu).split('=')[1]
    elif thearg == 'tl':
        target_path = str(argu).split('=')[1]

def download_logs(target_address, target_pass, target_path, logsdir):
    try:
        print("Grabbing logs, this may take a short while...")
        cmd = "rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass
        cmd +=" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_path+" "+logsdir
        os.system(cmd)
        print("local logs updated as " + logsdir)
    except exception as e:
        print("Files not grabbed!")
        raise

download_logs(target_address, target_pass, target_path, logsdir)
