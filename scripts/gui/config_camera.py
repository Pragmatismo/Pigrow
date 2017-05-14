#!/usr/bin/python
import os
import sys
import datetime
try:
    import wx
except:
    print(" You don't have WX installed, this draws the windows...")
    print("on ubunru;")
    print(" use the command ' sudo apt install python-wxgtk3.0 '")
    exit
try:
    import paramiko
except:
    print("  You don't have paramiko installed, this is what connects to the pi")
    print(" on ubuntu;")
    print(" use the command ' pip install paramiko ' to install.")
    exit
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print(" THIS IS A ALPHA-ALPHA STAGE SCRIPT - IT DOES ALMOST NOTHING AT THE MOMENT - UPDATES COMING SOON!")
##
###  THE FOLLOWIING NEED TO BE SET BY GUI BOXES
##
target_ip   = "192.168.1.6"
target_pass = "raspberry"
target_user = "pi"
target_config_path = "/home/pi/Pigrow/config/"
#target_crontab_path = "/var/spool/cron/crontabs/pi"
cap_type = "jpg"

def get_box_name(target_ip, target_user, target_pass):
    boxname = None
    found_login = False
    try:
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        found_login = True
        stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
        boxname = stdout.read().strip().split("=")[1]
        print "Pigrow Found; " + boxname
        ssh.close()
    except:
        print("dang - can't connect to pigrow or it's not a pigrow")
        ssh.close()
    return found_login, boxname

def take_unset_test_image(target_ip, target_user, target_pass):
    found_login = False
    cam_output = '!!!--NO READING--!!!'
    try:
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        found_login = True

        additonal_commands = ''                      #
        x_dim = 1200                                  #  This should come from GUI boxes
        y_dim = 1600                                  #     UPDATE COMING SOON
        output_file = "/home/pi/test_defaults.jpg"   #
        cam_capture_choice = "fswebcam"             #

        print("Using camera deafults to take image...")
        if cam_capture_choice == "uvccapture":
            cam_cmd = "uvccapture " + additonal_commands   #additional commands (camera select)
            cam_cmd += " -x"+str(x_dim)+" -y"+str(y_dim) + " "  #x and y dimensions of photo
            cam_cmd += "-v -t0 -o" + output_file                #verbose, no delay, output
        elif cam_capture_choice == "fswebcam":
            cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
            cam_cmd += " -D 2"      #the delay in seconds before taking photo
            cam_cmd += " -S 5"      #number of frames to skip before taking image
            cam_cmd += " --jpeg 90" #jpeg quality
            cam_cmd += " " + output_file  #output filename'

        print("---Doing: " + cam_cmd)
        stdin, stdout, stderr = ssh.exec_command(cam_cmd)
        cam_output = stderr.read().strip()
        print "Camera output; " + cam_output
        ssh.close()
    except Exception as e:
        print("Some form of problem; " + str(e))
        ssh.close()
    return found_login, cam_output, output_file

def get_test_pic(target_ip, target_user, target_pass, image_to_collect):
    img_name = image_to_collect.split("/")[-1]
    localpath = "/home/pragmo/pigitgrow/" + img_name
    try:
        port = 22
        ssh_tran = paramiko.Transport((target_ip, port))
        print("  - connecting transport pipe... " + target_ip + " port:" + str(port))
        ssh_tran.connect(username=target_user, password=target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        sftp.get(image_to_collect, localpath)
        print("--image collected from pi--")
        sftp.close()
        ssh_tran.close()
    except Exception as e:
        print("!!! There was an issue, " + str(e))
        return None
    print("SSH copy finished")
    return localpath


connected, box_name = get_box_name(target_ip, target_user, target_pass)
connected, camera_output, test_image = take_unset_test_image(target_ip, target_user, target_pass)
test_img_localpath = get_test_pic(target_ip, target_user, target_pass, test_image)
print("---------")
print("| " + str(box_name))
print("| " )
print("| " + str(test_img_localpath))
print("| ")
if "Processing captured image" in camera_output:
    print("| SUCCESSES!" )
else:
    print("| Seems to have failed...?")
