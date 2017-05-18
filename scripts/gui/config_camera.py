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
    print("    pip install paramiko ")
    print(" on windows;")
    print("    python -m pip install paramiko")
    print(" if it fails update your pip with 'python -m pip install -U pip'")
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
        x_dim = 1600                                  #  This should come from GUI boxes
        y_dim = 1200                                  #     UPDATE COMING SOON
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


#connected, box_name = get_box_name(target_ip, target_user, target_pass)
#connected, camera_output, test_image = take_unset_test_image(target_ip, target_user, target_pass)
#test_img_localpath = get_test_pic(target_ip, target_user, target_pass, test_image)
#print("---------")
#print("| " + str(box_name))
#print("| " )
#print("| " + str(test_img_localpath))
#print("| ")
#if "Processing captured image" in camera_output:
#    print("| SUCCESSES!" )
#else:
#    print("| Seems to have failed...?")

class config_cam(wx.Frame):
    def __init__(self, *args, **kw):
        super(config_cam, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
     ## Pigrow to config and link button.
        wx.StaticText(self,  label='address', pos=(10, 20))
        self.tb_ip = wx.TextCtrl(self, pos=(125, 25), size=(150, 25))
        self.tb_ip.SetValue("192.168.1.")
        wx.StaticText(self,  label='Username', pos=(10, 60))
        self.tb_user = wx.TextCtrl(self, pos=(125, 60), size=(150, 25))
        self.tb_user.SetValue("pi")
        wx.StaticText(self,  label='Password', pos=(10, 95))
        self.tb_pass = wx.TextCtrl(self, pos=(125, 95), size=(150, 25))
        self.tb_pass.SetValue("raspberry")
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi', pos=(50, 125), size=(175, 30))
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --', pos=(25, 160))
     ## setup details.
        wx.StaticText(self,  label='Cam options', pos=(50, 200))
        wx.StaticText(self,  label='Brightness;', pos=(10, 230))
        self.tb_b = wx.TextCtrl(self, pos=(120, 230), size=(75, 25))
        wx.StaticText(self,  label='Contrast;', pos=(10, 260))
        self.tb_c = wx.TextCtrl(self, pos=(120, 260), size=(75, 25))
        wx.StaticText(self,  label='Saturation;', pos=(10, 290))
        self.tb_s = wx.TextCtrl(self, pos=(120, 290), size=(75, 25))
        wx.StaticText(self,  label='Gain;', pos=(10, 320))
        self.tb_g = wx.TextCtrl(self, pos=(120, 320), size=(75, 25))
        wx.StaticText(self,  label='X;', pos=(10, 350))
        self.tb_x = wx.TextCtrl(self, pos=(120, 350), size=(75, 25))
        wx.StaticText(self,  label='Y;', pos=(10, 380))
        self.tb_y = wx.TextCtrl(self, pos=(120, 380), size=(75, 25))
        wx.StaticText(self,  label='Extra args;', pos=(10, 410))
        self.tb_extra = wx.TextCtrl(self, pos=(120, 410), size=(75, 25))

     ## capture image buttons

        self.relay1_btn = wx.Button(self, label='Relay 1', pos=(100, 500))
        self.relay2_btn = wx.Button(self, label='Relay 2', pos=(100, 540))
        self.relay3_btn = wx.Button(self, label='Relay 3', pos=(100, 580))
        self.relay4_btn = wx.Button(self, label='Relay 4', pos=(100, 620))
        #self.relay1_btn.Bind(wx.EVT_BUTTON, self.relay1_btn_click)
        #self.relay2_btn.Bind(wx.EVT_BUTTON, self.relay2_btn_click)
        #self.relay3_btn.Bind(wx.EVT_BUTTON, self.relay3_btn_click)
        #self.relay4_btn.Bind(wx.EVT_BUTTON, self.relay4_btn_click)


     ## Important wx stuff
        self.SetSize((800, 600))
        self.SetTitle('Pigrow Control - Camera Config')
        self.Centre()
        self.Show(True)

    def link_with_pi_btn_click(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        log_on_test, boxname = get_box_name(target_ip, target_user, target_pass)
        if log_on_test == True:
            self.link_status_text.SetLabel("linked with - " + str(boxname))


def main():
    app = wx.App()
    config_cam(None)
    app.MainLoop()


if __name__ == '__main__':
    tempfolder = "~/frompigrow/temp/"
    if not os.path.exists(tempfolder):
        os.makedirs(tempfolder)
    main()
