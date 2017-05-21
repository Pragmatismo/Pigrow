#!/usr/bin/python
import os
import sys
import datetime
import numpy
from PIL import Image
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

def get_cam_config(target_ip, target_user, target_pass, cam_config_loc_on_pi):
        config_name = cam_config_loc_on_pi.split("/")[-1]
        localpath = tempfolder + config_name
        try:
            port = 22
            ssh_tran = paramiko.Transport((target_ip, port))
            print("  - connecting transport pipe... " + target_ip + " port:" + str(port))
            ssh_tran.connect(username=target_user, password=target_pass)
            sftp = paramiko.SFTPClient.from_transport(ssh_tran)
            print("looking for " + str(cam_config_loc_on_pi))
            sftp.get(cam_config_loc_on_pi, localpath)
            print("--config file collected from pi--")
            sftp.close()
            ssh_tran.close()
        except Exception as e:
            print("!!! There was an issue, " + str(e))
            return None
        return localpath

def take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, b_val, x_dim=800, y_dim=600, additonal_commands='', cam_capture_choice='uvccapture', output_file='/home/pi/test_cam_settings.jpg', ctrl_test_value=None, ctrl_text_string=None, cmd_str=''):
    found_login = False
    focus_val = "20"
    cam_output = '!!!--NO READING--!!!'
    try:
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        found_login = True

        print("taking test image...")
        if cam_capture_choice == "uvccapture":
            cam_cmd = "uvccapture " + additonal_commands   #additional commands (camera select)
            cam_cmd += " -S" + s_val #saturation
            cam_cmd += " -C" + c_val #contrast
            cam_cmd += " -G" + g_val #gain
            cam_cmd += " -B" + b_val #brightness
            cam_cmd += " -x"+str(x_dim)+" -y"+str(y_dim) + " "  #x and y dimensions of photo
            cam_cmd += "-v -t0 -o" + output_file                #verbose, no delay, output
        elif cam_capture_choice == "fswebcam":
            cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
            cam_cmd += " -D 2"      #the delay in seconds before taking photo
            cam_cmd += " -S 5"      #number of frames to skip before taking image
            # to list controls use fswebcam -d v4l2:/dev/video0 --list-controls
            cam_cmd += " --set brightness=" + b_val
            cam_cmd += " --set contrast=" + c_val
            cam_cmd += " --set Saturation=" + s_val
            cam_cmd += " --set gain=" + g_val
            ##For testing camera ctrl variables
            if not ctrl_text_string == None:
                cam_cmd += " --set " + ctrl_text_string + "=" + str(ctrl_test_value)
            #cam_cmd += ' --set "Focus, Auto"=False --set "Focus (absolute)"=' + focus_val
            cam_cmd += cmd_str
            cam_cmd += " --jpeg 90" #jpeg quality
            # cam_cmd += " --info HELLO INFO TEXT"
            cam_cmd += " " + output_file  #output filename'
        else:
            print("NOT IMPLIMENTED - SELECT CAM CHOICE OF UVC OR FSWEBCAM PLZ")

        print("---Doing: " + cam_cmd)
        stdin, stdout, stderr = ssh.exec_command(cam_cmd)
        cam_output = stderr.read().strip()
        print "Camera output; " + cam_output
        ssh.close()
    except Exception as e:
        print("Some form of problem; " + str(e))
        ssh.close()
    return found_login, cam_output, output_file

def take_unset_test_image(target_ip, target_user, target_pass, x_dim=800, y_dim=600, additonal_commands='', cam_capture_choice='uvccapture', output_file='/home/pi/test_defaults.jpg'):
    found_login = False
    cam_output = '!!!--NO READING--!!!'
    try:
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        found_login = True

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
        else:
            print("not yet implimented please select uv or fs webcam as you option")

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
    localpath = tempfolder + img_name
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
    return localpath

def get_test_pic_from_list(target_ip, target_user, target_pass, image_list):
    out_list = []
    try:
        port = 22
        ssh_tran = paramiko.Transport((target_ip, port))
        print("  - connecting transport pipe... " + target_ip + " port:" + str(port))
        ssh_tran.connect(username=target_user, password=target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
    except Exception as e:
        print("!!! There was an issue, " + str(e))
        return None
    for image_to_collect in image_list:
        print image_to_collect
        img_name = image_to_collect.split("/")[-1]
        localpath = tempfolder + img_name
        print localpath
        sftp.get(image_to_collect, localpath)
        print("--image " + str(image_to_collect) + " collected from pi--")
        out_list.append(localpath)
    sftp.close()
    ssh_tran.close()
    return out_list

def graph_image_collection(filelist, graph_folder):
    graph_path_tot = str(graph_folder + "combined_pixel_value.png")
    red_list = []
    gre_list = []
    blu_list = []
    tot_list = []
    counter = []
    count = 1
    #work out max value
    pil_c_photo = pil_c_photo = Image.open(filelist[0])
    x, y = pil_c_photo.size
    max_pixel = ((x * y) * 3) * 255
    #tot_list.append(max_pixel)
    #tot_list.append(0)
    #counter.append(1)
    #counter.append(2)


    for image in filelist:
        count = count + 1
        pil_c_photo = Image.open(image)
        numpy_pic = numpy.array(pil_c_photo)
        r_sum = numpy_pic[:,:,0].sum()
        g_sum = numpy_pic[:,:,1].sum()
        b_sum = numpy_pic[:,:,2].sum()
        tot_sum = r_sum + g_sum + b_sum
        red_list.append(r_sum)
        gre_list.append(g_sum)
        blu_list.append(b_sum)
        tot_list.append(tot_sum/max_pixel * 100)
        counter.append(count)
    print tot_list
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(dates, values, width=0.01, color='k', linewidth = 0)
    ax.plot(counter, tot_list, color='darkblue', lw=3)
    plt.title("Variation in sum of pixel values")
    plt.ylabel("percent of maximum pixel value")
    fig = plt.gcf()
    plt.savefig(graph_path_tot)
    print("Graph saved to " + str(graph_path_tot))
    return graph_path_tot


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
     ## image holder
        self.main_image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(1000, 1000), pos=(280, 10))
     ## setup details.
        wx.StaticText(self,  label='Cam options', pos=(50, 190))
        wx.StaticText(self,  label='Brightness;', pos=(10, 220))
        self.tb_b = wx.TextCtrl(self, pos=(120, 220), size=(75, 25))
        wx.StaticText(self,  label='Contrast;', pos=(10, 250))
        self.tb_c = wx.TextCtrl(self, pos=(120, 250), size=(75, 25))
        wx.StaticText(self,  label='Saturation;', pos=(10, 280))
        self.tb_s = wx.TextCtrl(self, pos=(120, 280), size=(75, 25))
        wx.StaticText(self,  label='Gain;', pos=(10, 310))
        self.tb_g = wx.TextCtrl(self, pos=(120, 310), size=(75, 25))
        wx.StaticText(self,  label='X;', pos=(10, 340))
        self.tb_x = wx.TextCtrl(self, pos=(120, 340), size=(75, 25))
        wx.StaticText(self,  label='Y;', pos=(10, 370))
        self.tb_y = wx.TextCtrl(self, pos=(120, 370), size=(75, 25))
     ## camera select
        cam_opts = ['uvccapture', 'fswebcam', 'picam-python', 'picam-cmdline']
        wx.StaticText(self,  label='capture with', pos=(15, 400))
        self.cam_combo = wx.ComboBox(self, choices = cam_opts, pos=(125,400), size=(125, 30))
        self.cam_combo.Bind(wx.EVT_COMBOBOX, self.cam_combo_go)
     ## fswebcam only controlls
        self.fs_label = wx.StaticText(self,  label='fswebcam setting to test', pos=(10, 435))
        self.list_fs_ctrls_btn = wx.Button(self, label='Show webcam controlls', pos=(25, 460))
        self.list_fs_ctrls_btn.Bind(wx.EVT_BUTTON, self.list_fs_ctrls_click)

        self.setting_string_label = wx.StaticText(self,  label='set;', pos=(10, 495))
        self.setting_string_tb = wx.TextCtrl(self, pos=(50, 495), size=(200, 25))
        self.setting_value_label = wx.StaticText(self,  label='value;', pos=(10, 525))
        self.setting_value_tb = wx.TextCtrl(self, pos=(60, 525), size=(100, 25))
        self.add_to_cmd_btn = wx.Button(self, label='Add to cmd string', pos=(5, 550))
        #self.list_fs_ctrls_btn = wx.Button(self, label='i dunno', pos=(175, 550))
        self.cmds_string_tb = wx.TextCtrl(self, pos=(10, 590), size=(200, 25))
        self.add_to_cmd_btn.Bind(wx.EVT_BUTTON, self.add_to_cmd_click)
        self.fs_label.Hide()



     ## uvc only contols
        #wx.StaticText(self,  label='Extra args;', pos=(10, 500))
        #self.tb_extra = wx.TextCtrl(self, pos=(10, 530), size=(200, 25))



     ## capture image buttons

        self.cap_cam_btn = wx.Button(self, label='Take useing settings', pos=(25, 700))
        self.cap_unset_btn = wx.Button(self, label='Take using no settings', pos=(25, 740))
        self.stability_batch_btn = wx.Button(self, label='take test batch', pos=(10, 780))
        self.graph_batch_btn = wx.Button(self, label='graph batch', pos=(150, 780))
        self.range_btn = wx.Button(self, label='take a range', pos=(25,820))
        range_opts = ['brightness', 'contrast', 'saturation', 'gain']
        self.range_combo = wx.ComboBox(self, choices = range_opts, pos=(140,820), size=(125, 30))
        self.cap_cam_btn.Bind(wx.EVT_BUTTON, self.capture_cam_image)
        self.cap_unset_btn.Bind(wx.EVT_BUTTON, self.capture_unset_cam_image)
        self.stability_batch_btn.Bind(wx.EVT_BUTTON, self.stability_batch_btn_click)
        self.graph_batch_btn.Bind(wx.EVT_BUTTON, self.graph_batch_click)
        self.range_btn.Bind(wx.EVT_BUTTON, self.range_btn_click)


     ## Important wx stuff
        self.SetSize((900, 900))
        self.SetTitle('Pigrow Control - Camera Config')
        self.Centre()
        self.Show(True)

    def add_to_cmd_click(self, e):
        test_str = self.setting_string_tb.GetValue()
        test_val = self.setting_value_tb.GetValue()
        cmd_str = self.cmds_string_tb.GetValue()
        cmd_str += ' --set "' + str(test_str) + '"=' + str(test_val)
        self.cmds_string_tb.SetValue(cmd_str)

    def list_fs_ctrls_click(self, e):
        print("this is supposed to fswebcam -d v4l2:/dev/video0 --list-controls on the pi")
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        try:
            ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
            print "Connected to " + target_ip
            found_login = True
            cam_cmd = "fswebcam -d v4l2:/dev/video0 --list-controls"
            print("---Doing: " + cam_cmd)
            stdin, stdout, stderr = ssh.exec_command(cam_cmd)
            cam_output = stderr.read().strip()
            print "Camera output; " + cam_output
            ssh.close()
        except Exception as e:
            print("Some form of problem; " + str(e))
            ssh.close()
        if not cam_output == None:
            msg_text = 'Camera located and interorgated; copy-paste a controll name from the following into the settings text box \n \n'
            msg_text += str(cam_output)
            wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)



    def cam_combo_go(self, e):
        if self.cam_combo.GetValue() == 'fswebcam':
            self.fs_label.Show()
            self.list_fs_ctrls_btn.Show()
            self.list_fs_ctrls_btn.Show()
            self.setting_string_label.Show()
            self.setting_string_tb.Show()
            self.setting_value_label.Show()
            self.setting_value_tb.Show()
        else:
            self.fs_label.Hide()
            self.list_fs_ctrls_btn.Hide()
            self.list_fs_ctrls_btn.Hide()
            self.setting_string_label.Hide()
            self.setting_string_tb.Hide()
            self.setting_value_label.Hide()
            self.setting_value_tb.Hide()

    def link_with_pi_btn_click(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        cam_config_loc_on_pi = '/home/pi/Pigrow/config/camera_settings.txt'
        log_on_test, boxname = get_box_name(target_ip, target_user, target_pass)
        if log_on_test == True:
            self.link_status_text.SetLabel("linked with - " + str(boxname))
            local_cam_settings_file = get_cam_config(target_ip, target_user, target_pass, cam_config_loc_on_pi)
            print local_cam_settings_file
            with open(local_cam_settings_file, "r") as f:
                for line in f:
                    s_item = line.split("=")
                    if s_item[0] == "s_val":
                        s_val = s_item[1].strip()
                    elif s_item[0] == "c_val":
                        c_val = s_item[1].strip()
                    elif s_item[0] == "g_val":
                        g_val = s_item[1].strip()
                    elif s_item[0] == "b_val":
                        b_val = s_item[1].strip()
                    elif s_item[0] == "x_dim":
                        x_dim = s_item[1].strip()
                    elif s_item[0] == "y_dim":
                        y_dim = s_item[1].strip()
                    elif s_item[0] == "additonal_commands":
                        additonal_commands = s_item[1].strip()
            print s_val, c_val, g_val, b_val, x_dim, y_dim, additonal_commands
            self.tb_s.SetValue(str(s_val))
            self.tb_c.SetValue(str(c_val))
            self.tb_g.SetValue(str(g_val))
            self.tb_b.SetValue(str(b_val))
            self.tb_x.SetValue(str(x_dim))
            self.tb_y.SetValue(str(y_dim))
            #self.tb_extra.SetValue(str(additonal_commands))
        else:
            print ("Failed to connect")

    def capture_cam_image(self, e):
        cam_capture_choice = self.cam_combo.GetValue()
        s_val = str(self.tb_s.GetValue())
        c_val = str(self.tb_c.GetValue())
        g_val = str(self.tb_g.GetValue())
        b_val = str(self.tb_b.GetValue())
        x_dim = str(self.tb_x.GetValue())
        y_dim = str(self.tb_y.GetValue())
        extra_args = '' # str(self.tb_extra.GetValue())
        print s_val, c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice
        if cam_capture_choice == 'fswebcam':
            ctrl_text_string = self.setting_string_tb.GetValue()
            ctrl_test_value = self.setting_value_tb.GetValue()
            cmd_str = self.cmds_string_tb.GetValue()
            print("+++++++++++++++++++++++++++=")
            print(ctrl_test_value)
            print(ctrl_text_string)
            print('===========')
            if not ctrl_test_value == '':
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice, ctrl_test_value=ctrl_test_value, ctrl_text_string=ctrl_text_string, cmd_str=cmd_str)
            else:
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice, cmd_str=cmd_str)
        else:
            found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice)
        photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
        self.main_image.SetBitmap(wx.BitmapFromImage(wx.Image(photo_location, wx.BITMAP_TYPE_ANY)))

    def capture_unset_cam_image(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        x_dim = self.tb_x.GetValue()
        y_dim = self.tb_y.GetValue()
        extra_args = self.tb_extra.GetValue()
        cam_capture_choice = self.cam_combo.GetValue()
        found_login, cam_output, output_file = take_unset_test_image(target_ip, target_user, target_pass, x_dim, y_dim, extra_args, cam_capture_choice)
        #print cam_output
        photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
        #print photo_location
        self.main_image.SetBitmap(wx.BitmapFromImage(wx.Image(photo_location, wx.BITMAP_TYPE_ANY)))

    def stability_batch_btn_click(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        s_val = self.tb_s.GetValue()
        c_val = self.tb_c.GetValue()
        g_val = self.tb_g.GetValue()
        b_val = self.tb_b.GetValue()
        x_dim = self.tb_x.GetValue()
        y_dim = self.tb_y.GetValue()
        extra_args = self.tb_extra.GetValue()
        cam_capture_choice = self.cam_combo.GetValue()
        photo_set = []
        for changing_range in range(0, 10):
            filename = 'range_bat_' + str(changing_range) + '.jpg'
            found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice, filename)
            photo_set.append(output_file)
        print photo_set
        batch_list = get_test_pic_from_list(target_ip, target_user, target_pass, photo_set)
        print batch_list

    def graph_batch_click(self, e):
        filelist = []
        for filefound in os.listdir(tempfolder):
            if filefound.endswith('jpg'):
                if filefound[0:10] == 'range_bat_':
                    filelist.append(str(tempfolder + filefound))
        filelist.sort(key=lambda f: int(filter(str.isdigit, f)))
        tot_graph = graph_image_collection(filelist, tempfolder)
        self.main_image.SetBitmap(wx.BitmapFromImage(wx.Image(tot_graph, wx.BITMAP_TYPE_ANY)))



        #photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)



    def range_btn_click(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        s_val = self.tb_s.GetValue()
        c_val = self.tb_c.GetValue()
        g_val = self.tb_g.GetValue()
        b_val = self.tb_b.GetValue()
        x_dim = self.tb_x.GetValue()
        y_dim = self.tb_y.GetValue()
        extra_args = self.tb_extra.GetValue()
        cam_capture_choice = self.cam_combo.GetValue()
        range_choice = self.range_combo.GetValue()
        range_start = 1
        range_end = 250
        range_jump = 10
        photo_set = []
        for changing_range in range(range_start, range_end, range_jump):
            if range_choice == 'brightness':
                filename = 'range_b_' + str(changing_range) + '.jpg'
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, g_val, str(changing_range), x_dim, y_dim, extra_args, cam_capture_choice, filename)
                photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
                photo_set.append(photo_location)
            elif range_choice == 'contrast':
                filename = 'range_c_' + str(changing_range) + '.jpg'
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, str(changing_range), g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice, filename)
                photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
                photo_set.append(photo_location)
            elif range_choice == 'saturation':
                filename = 'range_s_' + str(changing_range) + '.jpg'
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, str(changing_range), c_val, g_val, b_val, x_dim, y_dim, extra_args, cam_capture_choice, filename)
                photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
                photo_set.append(photo_location)
            elif range_choice == 'gain':
                filename = 'range_g_' + str(changing_range) + '.jpg'
                found_login, cam_output, output_file = take_test_image(target_ip, target_user, target_pass, s_val, c_val, str(changing_range), b_val, x_dim, y_dim, extra_args, cam_capture_choice, filename)
                photo_location = get_test_pic(target_ip, target_user, target_pass, output_file)
                photo_set.append(photo_location)

        self.main_image.SetBitmap(wx.BitmapFromImage(wx.Image(photo_location, wx.BITMAP_TYPE_ANY)))
        print photo_set




def main():
    app = wx.App()
    config_cam(None)
    app.MainLoop()


if __name__ == '__main__':
    tempfolder = "/home/pragmo/frompigrow/temp/"
    if not os.path.exists(tempfolder):
        os.makedirs(tempfolder)
    main()
