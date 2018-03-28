#!/usr/bin/python
import os
import sys
import datetime
try:
    import matplotlib.pyplot as plt
except:
    print("matplotlib is not installed, you won't be able to make graphs without it.")
    print("on ubuntu us the command;")
    print("   sudo apt install python-matplotlib")
    print(" on windows try;")
    print("   python -m pip install matplotlib")
try:
    import wx
except:
    print(" You don't have WX installed, this draws the windows...")
    print("on ubunru use the command;")
    print("   sudo apt install python-wxgtk3.0 ")
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

class pigrow_setup(wx.Frame):
    def __init__(self, *args, **kw):
        super(pigrow_setup, self).__init__(*args, **kw)
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
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi', pos=(10, 125), size=(175, 30))
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --', pos=(25, 160))
     ## Upload to pi button
        self.save_to_pi_btn = wx.Button(self, label='upload', pos=(190,125))
        self.save_to_pi_btn.Disable()
        #self.save_to_pi_btn.Bind(wx.EVT_BUTTON, self.save_to_pi_click)

     ## Important wx stuff
        self.SetSize((900, 900))
        self.SetTitle('Pigrow Control - Camera Config')
        self.Centre()
        self.Show(True)

    def link_with_pi_btn_click(self, e):
        #clear_temp_folder()
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        cam_config_loc_on_pi = '/home/pi/Pigrow/config/camera_settings.txt'
        log_on_test, boxname = get_box_name(target_ip, target_user, target_pass)
        if log_on_test == True and not boxname == None:
            self.link_status_text.SetLabel("linked with - " + str(boxname))
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
        if log_on_test == True and boxname == None:
            self.link_status_text.SetLabel("Found raspberry pi, but not pigrow")

def main():
    app = wx.App()
    pigrow_setup(None)
    app.MainLoop()


if __name__ == '__main__':
    tempfolder = "/home/pragmo/frompigrow/temp/"
    if not os.path.exists(tempfolder):
        os.makedirs(tempfolder)
    main()
