#!/usr/bin/python3

#
#   WORK IN PROGRESS
#
# Classes already created;
# -app pannels
#    pi_link_pnl        - top-left connection box with ip, username, pass
#    view_pnl           - allows you to select which options to view
#
# -main pannels
#    system_info_pnl    - for setting up the raspberry pi system and pigrow install
#    system_ctrl_pnl        - buttons for system_info_pnl
#
#    config_info_pnl    -shows info on current pigorow config
#    config_ctrl_pnl    -  buttons for above
#
#    cron_list_pnl      - shows the 3 cron type lists on the right of the window
#    cron_info_pnl          - buttons for cron_list_pnl
#    cron_job_dialog        - dialogue box for edit cron job
#
#    localfiles_info_pnl  - shows local files for spesific pigrow
#    localfiles_ctrl_pnl  - buttons for above
#       + uoload & download dialog box
#
#    graphing_info_pn
#    graphing_ctrl_pannel
#
#
# - Useful functions and stored variables
#
#            I NEED TO MAKE A NEAT PLACE FOR SHARED VARIABLES
#               THIS WILL HAPPEN SOON
#
#  Set the status bar
#    MainApp.status.write_bar("Status bar normal text")       # normal background with black text
#    MainApp.status.write_warning("Status bar warning text")  # red back with black text
#
#
#
###                Run a command on the pigrow
##     MainApp.localfiles_ctrl_pannel.run_on_pi(self, command)
#          Runs a command on the pigrow and returns output and error
####     out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
#
###                download a file to the local folder system
##    MainApp.localfiles_ctrl_pannel.download_file_to_folder(remote_file, local_name)
#          remote file is the full path to the file to be downloaded
#          local_name is the folder and filename within the pigrows local folder
####     MainApp.localfiles_ctrl_pannel.download_file_to_folder("/home/" + pi_link_pnl.target_user + "/Pigrow/graphs/graph.png", "graphs/graph.png"
#
###                 upload a file to the raspberry pi
##    MainApp.localfiles_ctrl_pannel.upload_file_to_folder(local_path, remote_path):
#           local_path and remote_path should be full and explicit paths
####     MainApp.localfiles_ctrl_pannel.upload_file_to_folder(localfiles_info_pnl.local_path + "temp/temp.txt", "/home/" + pi_link_pnl.target_user + "/Pigrow/temp/temp.txt")
#
###                 save text to a file on the pi
##   MainApp.localfiles_ctrl_pannel.save_text_to_file_on_pi(file_location, text)
#
#
###      Useful Variables - Path info
##
##  temp_local = os.path.join(localfiles_info_pnl.local_path, "/temp/")
##  remote_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/"
##
##  box_name = MainApp.config_ctrl_pannel.config_dict["box_name"]
##  box_name = pi_link_pnl.boxname
#
#  SETTINGS FOR THE GUI TO USE
#    # Called as gui_set
    #     fot example use
    #             window_width = gui_set.width_of_window
    #     to return the size of the gui's window
 # gui_set.width_of_window
 # gui_set.height_of_window

#
##
###

print("")
print(" Pigrow Remote Control Utility")
print("     Set-up and manage your Pigrow remotely ")
print("             --work in progress--  ")
print("     Works best on Linux, especially Ubuntu")
print("     ")
print("  More information at www.reddit.com/r/Pigrow")
print("")
print("  Work in progress, please report any errors or problems ")
print("  Code shared under a GNU General Public License v3.0")
print("")

import os
import sys
import shutil
import platform
import time
import datetime
import numpy as np
from stat import S_ISDIR
try:
    import image_combine
except:
    print("Importing image_combine.py failed, you won't be able to combine images")
    print("in the camera config tab or when making datawalls locally.")
try:
    import wx
    import wx.adv
    import wx.lib.scrolledpanel as scrolled
    from wx.lib.masked import NumCtrl
    #print (wx.__version__)
    #import wx.lib.scrolledpanel
except:
    print(" You don't have WX Python installed, this makes the gui")
    print(" google 'installing wx python' for your operating system")
    print("")
    print("    easiest should be using pip to install the wxpython package")
    print("            pip3 install wxpython")
    print("")
    print("on ubuntu try the commands;")
    #print("     sudo apt-get install python3-setuptools")
    #print("     sudo easy_install3 pip")
    print("     pip3 install wxpython")
    print(" or")
    print("   sudo apt install python-wxgtk3.0 ")
    print("")
    print(" Note: wx must be installed for python3")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon
    from matplotlib.ticker import StrMethodFormatter
except:
    print(" -------")
    print("  You don't have matploylib installed, this is used to create graphs")
    print("  You can ignore this wrning and still use most the functionality of the program")
    print("  if you want  to use graphs then make sure you have matploylib installed for python 3")
    print("  the command ")
    print("      pip install matplotlib")
    print("  should work on most systems, if not then google your os name + 'install matplotlib'")
    print(" -----")
    sys.exit()

try:
    import paramiko
except:
    print("  You don't have paramiko installed, this is what connects to the pi")
    print(" google 'installing paramiko python' for your operating system")
    print(" on ubuntu;")
    print(" use the command ' pip install paramiko ' to install.")
    print("")
    print(" if you don't have pip installed you can install using")
    print("     sudo apt-get install python3-setuptools")
    print("     sudo easy_install3 pip")
    print("         ")
    sys.exit(1)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#
#
## Dialog Boxes for Generaic USE
#
#

class scroll_text_dialog(wx.Dialog):
    def __init__(self, parent,  text_to_show, title, cancel=True, readonly=True):
        wx.Dialog.__init__(self, parent, title=(title))
        scroll_text_dialog.text = None
        if readonly == True:
            self.text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE | wx.TE_READONLY)
        else:
            self.text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnsizer = wx.BoxSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.Bind(wx.EVT_BUTTON, self.ok_click)
        btnsizer.Add(btn, 0, wx.ALL, 5)
        btnsizer.Add((5,-1), 0, wx.ALL, 5)
        if cancel==True:
            cancel_btn = wx.Button(self, wx.ID_CANCEL)
            btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(sizer)
    def ok_click(self, e):
        scroll_text_dialog.text = self.text.GetValue()
        self.Destroy()

class show_image_dialog(wx.Dialog):
    def __init__(self, parent,  image_to_show, title):
        wx.Dialog.__init__(self, parent, title=(title))
        # limit size to screen
        width, height = wx.GetDisplaySize()
        im_width, im_height = image_to_show.GetSize()
        print(" W: ", width, im_width )
        print(" H: ", height, im_height)
        if im_height > height:
            im_height = height
        if im_width > width:
            im_width = width
        # create scroll panel
        display_panel = scrolled.ScrolledPanel(self, size=(im_width, im_height), style = wx.HSCROLL|wx.VSCROLL)
        display_panel.SetupScrolling()
        pic = wx.StaticBitmap(display_panel, -1, image_to_show)
        # panel sizer
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(pic) #, wx.ID_ANY, wx.EXPAND)
        display_panel.SetSizer(panel_sizer)
        # main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(display_panel)
        self.SetSizerAndFit(sizer)


def scale_pic(pic, target_size):
    pic_height = pic.GetHeight()
    pic_width = pic.GetWidth()
    # scale the image, preserving the aspect ratio
    if pic_width > pic_height:
        sizeratio = (pic_width / target_size)
        new_height = (pic_height / sizeratio)
        scale_pic = pic.Scale(target_size, new_height, wx.IMAGE_QUALITY_HIGH)
        #print(pic_width, pic_height, sizeratio, target_size, new_height, scale_pic.GetWidth(), scale_pic.GetHeight())
    else:
        sizeratio = (pic_height / target_size)
        new_width = (pic_width / sizeratio)
        scale_pic = pic.Scale(new_width, target_size, wx.IMAGE_QUALITY_HIGH)
        #print(pic_width, pic_height, sizeratio, new_width, target_size, scale_pic.GetWidth(), scale_pic.GetHeight())
    return scale_pic

def is_a_valid_and_free_gpio(gpio_pin):
    '''
    This checks if a GPIO pin is valid and currently not linked
    to anything in the config file.
    takes an str or int of the gpio number.
    returns - True or False
    '''
    if not str(gpio_pin).isdigit():
        return False
    gpio_pin = int(gpio_pin)
    if gpio_pin < 2:
        return False
    if gpio_pin > 27:
        return False
    #add check here to see if pin is already used in config file
    return True

def get_module_options(module_prefix, m_folder="graph_modules"):
    list_of_modules = []
    modules_folder = os.path.join(os.getcwd(), m_folder)
    module_options = os.listdir(modules_folder)
    for file in module_options:
        if module_prefix in file:
            file = file.split(module_prefix)[1]
            if ".py" in file:
                file = file.split(".py")[0]
                list_of_modules.append(file)
    return list_of_modules
#
#
## Place for persistent stuff
class shared_data:
    def __init__(self):
        # Connection settings
        shared_data.ssh_port = 22
        #
        ## settings
        #
        shared_data.always_show_config_changes = False  # if true always show the 'upload to pigrow?' dialog box
        #
        ## paths
        #
        # gui system paths
        shared_data.cwd = os.getcwd()
        shared_data.ui_img_path = os.path.join(shared_data.cwd, "ui_images")
        shared_data.graph_modules_path = os.path.join(shared_data.cwd, "graph_modules")
        shared_data.sensor_modules_path = os.path.join(shared_data.cwd, "sensor_modules")
        sys.path.append(shared_data.graph_modules_path)
        sys.path.append(shared_data.sensor_modules_path)
        shared_data.graph_presets_path = os.path.join(shared_data.cwd, "graph_presets")
        shared_data.datawall_presets_path = os.path.join(shared_data.cwd, "datawall_presets")
        #
        ## Temporarily Stored data
        #
        # graphing logs
        shared_data.log_to_load = None
        shared_data.list_of_datasets = [] # [[date, value, key], [set2_date, set2_value, set2_key], etc]
        #      [shared_data.first_date_set, shared_data.first_value_set, shared_data.first_keys_set]
        shared_data.first_value_set = []
        shared_data.first_date_set = []
        shared_data.first_keys_set = []
        shared_data.first_valueset_name = ""
        # camconf info
        shared_data.most_recent_camconf_image = ""
        shared_data.camcomf_compare_image  = ""

        #
        ## Icon images
        #
        no_log_img_path = os.path.join(shared_data.ui_img_path, "log_loaded_none.png")
        yes_log_img_path = os.path.join(shared_data.ui_img_path, "log_loaded_true.png")
        warn_log_img_path = os.path.join(shared_data.ui_img_path, "log_loaded_none.png")
        shared_data.no_log_image = wx.Image(no_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        shared_data.yes_log_image = wx.Image(yes_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        shared_data.warn_log_image = wx.Image(warn_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #
        ## Fonts
        #
        shared_data.title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.item_title_font = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.info_font = wx.Font(14, wx.MODERN, wx.ITALIC, wx.NORMAL)
        shared_data.large_info_font = wx.Font(16, wx.MODERN, wx.ITALIC, wx.NORMAL)

    class settings_dialog(wx.Dialog):
        '''
        Dialog box for changing the gui settings
        #
        dbox = shared_data.settings_dialog(None)
        dbox.ShowModal()
        dbox.Destroy()
        #
        '''
        def __init__(self, parent):
            wx.Dialog.__init__(self, parent, title="Remote Gui Settings")
            # SSH Settings
            self.sshport_l = wx.StaticText(self, label='SSH Port')
            self.ssh_port_tc = wx.TextCtrl(self, -1, str(shared_data.ssh_port))
            # Buttons
            btn = wx.Button(self, wx.ID_OK)
            cancel_btn = wx.Button(self, wx.ID_CANCEL)
            btn.Bind(wx.EVT_BUTTON, self.ok_click)
            # Sizers
            sshport_sizer = wx.BoxSizer(wx.HORIZONTAL)
            sshport_sizer.Add(self.sshport_l, 0, wx.ALL, 5)
            sshport_sizer.Add(self.ssh_port_tc, 0, wx.ALL, 5)
            btnsizer = wx.BoxSizer(wx.HORIZONTAL)
            btnsizer.Add(btn, 0, wx.ALL, 5)
            btnsizer.Add((5,-1), 0, wx.ALL, 5)
            btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(sshport_sizer, 0, wx.EXPAND|wx.ALL, 5)
            main_sizer.Add(btnsizer, 0, wx.ALL, 5)
            self.SetSizerAndFit(main_sizer)
        def ok_click(self, e):
            shared_data.ssh_port = int(self.ssh_port_tc.GetValue())
            self.Destroy()

#
#
## System Pannel
#
#
class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.tab_label = wx.StaticText(self,  label='System Config Menu')
        self.pigrow_side_label = wx.StaticText(self,  label='Pigrow Software')
        self.system_side_label = wx.StaticText(self,  label='System')
        self.i2c_side_label = wx.StaticText(self,  label='I2C')
        self.onewire_side_label = wx.StaticText(self,  label='1Wire')
        self.picam_label = wx.StaticText(self,  label='Picam')
        self.tab_label.SetFont(shared_data.sub_title_font)
        self.pigrow_side_label.SetFont(shared_data.sub_title_font)
        self.system_side_label.SetFont(shared_data.sub_title_font)
        self.i2c_side_label.SetFont(shared_data.sub_title_font)
        self.onewire_side_label.SetFont(shared_data.sub_title_font)
        self.picam_label.SetFont(shared_data.sub_title_font)
        # Start drawing the UI elements
        # tab info
        self.read_system_btn = wx.Button(self, label='Read System Info')
        self.read_system_btn.Bind(wx.EVT_BUTTON, self.read_system_click)
        # pigrow software install and upgrade buttons
        self.install_pigrow_btn = wx.Button(self, label='pigrow install')
        self.install_pigrow_btn.Bind(wx.EVT_BUTTON, self.install_click)
        self.update_pigrow_btn = wx.Button(self, label='update pigrow')
        self.update_pigrow_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_click)
        # pi power control
        self.reboot_pigrow_btn = wx.Button(self, label='reboot pi')
        self.reboot_pigrow_btn.Bind(wx.EVT_BUTTON, self.reboot_pigrow_click)
        self.shutdown_pi_btn = wx.Button(self, label='shutdown pi')
        self.shutdown_pi_btn.Bind(wx.EVT_BUTTON, self.shutdown_pi_click)
        # pi gpio overlay controlls
        self.find_i2c_btn = wx.Button(self, label='i2c check')
        self.find_i2c_btn.Bind(wx.EVT_BUTTON, self.find_i2c_devices)
        self.i2c_baudrate_btn = wx.Button(self, label='baudrate')
        self.i2c_baudrate_btn.Bind(wx.EVT_BUTTON, self.set_baudrate)
        self.i2c_baudrate_btn.Disable()
        self.find_1wire_btn = wx.Button(self, label='1 wire check')
        self.find_1wire_btn.Bind(wx.EVT_BUTTON, self.find_1wire_devices)
        self.add_1wire_btn = wx.Button(self, label='Add 1w')
        self.add_1wire_btn.Bind(wx.EVT_BUTTON, self.add_1wire)
        self.edit_1wire_btn = wx.Button(self, label='change')
        self.edit_1wire_btn.Bind(wx.EVT_BUTTON, self.edit_1wire)
        self.remove_1wire_btn = wx.Button(self, label='remove')
        self.remove_1wire_btn.Bind(wx.EVT_BUTTON, self.remove_1wire)
        self.add_1wire_btn.Disable()
        self.edit_1wire_btn.Disable()
        self.remove_1wire_btn.Disable()
        # run command on pi button
        self.run_cmd_on_pi_btn = wx.Button(self, label='Run Command On Pi')
        self.run_cmd_on_pi_btn.Bind(wx.EVT_BUTTON, self.run_cmd_on_pi_click)
        self.edit_boot_config_btn = wx.Button(self, label='Edit /boot/config.txt')
        self.edit_boot_config_btn.Bind(wx.EVT_BUTTON, self.edit_boot_config_click)
        # Enable / Disable Camera
        self.enable_cam_btn = wx.Button(self, label='Enable')
        self.enable_cam_btn.Bind(wx.EVT_BUTTON, self.enable_cam_click)
        self.disable_cam_btn = wx.Button(self, label='Disable')
        self.disable_cam_btn.Bind(wx.EVT_BUTTON, self.disable_cam_click)
        # gui settings
        self.gui_settings_btn = wx.Button(self, label='GUI Settings')
        self.gui_settings_btn.Bind(wx.EVT_BUTTON, self.gui_settings_click)

        # Sizers
        power_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_sizer.Add(self.reboot_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        power_sizer.Add(self.shutdown_pi_btn, 0, wx.ALL|wx.EXPAND, 3)
        i2c_sizer = wx.BoxSizer(wx.HORIZONTAL)
        i2c_sizer.Add(self.find_i2c_btn, 0, wx.ALL|wx.EXPAND, 3)
        i2c_sizer.Add(self.i2c_baudrate_btn, 0, wx.ALL|wx.EXPAND, 3)
        onewire_sizer = wx.BoxSizer(wx.HORIZONTAL)
        onewire_sizer.Add(self.find_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)
        onewire_sizer.Add(self.add_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)
        one_wire_con_sizer = wx.BoxSizer(wx.HORIZONTAL)
        one_wire_con_sizer.Add(self.edit_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)
        one_wire_con_sizer.Add(self.remove_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)
        picam_sizer = wx.BoxSizer(wx.HORIZONTAL)
        picam_sizer.Add(self.picam_label, 0, wx.ALL|wx.EXPAND, 3)
        picam_sizer.Add(self.enable_cam_btn, 0, wx.ALL|wx.EXPAND, 3)
        picam_sizer.Add(self.disable_cam_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.tab_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.read_system_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.pigrow_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.install_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.system_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.run_cmd_on_pi_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.edit_boot_config_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(power_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.i2c_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(i2c_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.onewire_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(onewire_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(one_wire_con_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(picam_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.gui_settings_btn, 0, wx.ALL, 3)
        self.SetSizer(main_sizer)

    def gui_settings_click(self, e):
        dbox = shared_data.settings_dialog(None)
        dbox.ShowModal()
        dbox.Destroy()

    def enable_cam_click(self, e):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo raspi-config nonint do_camera 0")
        msg = "Raspberry Pi needs to be restarted for changes to take effect, do that now?"
        dbox = wx.MessageDialog(self, msg, "Reboot Pi?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo reboot now")
            MainApp.pi_link_pnl.link_with_pi_btn_click("e")

    def disable_cam_click(self, e):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo raspi-config nonint do_camera 1")
        print("Picam module disabled.")

    # 1Wire - ds18b20
    def find_ds18b20_devices(self):
        temp_sensor_list = []
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /sys/bus/w1/devices")
        w1_bus_folders = out.splitlines()
        for folder in w1_bus_folders:
            if folder[0:3] == "28-":
                temp_sensor_list.append(folder)
        return temp_sensor_list

    def find_dtoverlay_1w_pins(self):
        ''' This checks on the raspi's /boot/config.txt and lists the gpio
            numbers used with dtoverlay=w1-gpio then returns a list containing
            [gpio_num, line comment]
            and a text block of error messages
            all #ed lines are ignored
        '''
        print("finding w1 overlays in config file")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        config_txt_lines = out.splitlines()
        line_enabled = None
        line_gpio_num = ""
        line_comment = ""
        gpio_pins = []
        err_msg = ""
        for line in config_txt_lines:
            comment = None
            command = None
            gpio_pin = None
            if not line.strip()[0:1] == "#":
                if "dtoverlay=w1-gpio" in line:
                    if "#" in line:
                        hash_pos = line.find("#")
                        command = line[:hash_pos]
                        comment = line[hash_pos:]
                    else:
                        command = line
                    if "gpiopin=" in command:
                        gpio_pin = command.split("gpiopin=")[1].strip()
                        if not gpio_pin.isdigit():
                            gpio_pin = 'error'
                            err_msg += "!!! Error reading pi's /boot/config.txt could't determine gpio number -" + command + "\n"
                    else:
                        gpio_pin = "default (4)"
                    gpio_pins.append([gpio_pin, comment])
                # look to see if gpio pin is changed later in the file...
                elif "dtparam" in line and "gpiopin" in line:
                    if "dtparam=gpiopin=" in line:
                        if "#" in line:
                            hash_pos = line.find("#")
                            command = line[:hash_pos]
                            comment = line[hash_pos:]
                        else:
                            command = line
                        #split the comment section and extract the gpio number
                        gpio_pin = command.split("dtparam=gpiopin=")[1]
                        if not gpio_pin.isdigit():
                            gpio_pin = None
                            err_msg += "!!! Error reading pi's /boot/config.txt could't determine gpio number -" + command + "\n"
                        if not len(gpio_pins) == 0:
                            err_msg += "!!! GPIO pin changed using dtparam=gpiopin= from " + str(gpio_pins[-1][0]) + " to " + str(gpio_pin)
                            err_msg += "\n    - (this makes it confusing so automatic editing is now disabled)"
                            gpio_pins[-1] = (gpio_pin, gpio_pins[-1][1])
                    else:
                        err_msg += "!!! dtparam gpiopin included in line but we couldn't understand it, "
                        err_msg += " - if the config file lines works then please msg me with them and what the end result is when using it -" + line + "\n"
        if len(gpio_pins) > 0 and err_msg == "":
            self.edit_1wire_btn.Enable()
            self.remove_1wire_btn.Enable()
        return gpio_pins, err_msg

    def find_1wire_devices(self, e):
        module_text = ""
        therm_module_text = ""
        other_modules = ""
        onewire_config_file = ""
        # Check running modules for w1 and therm overlay
        print("looking to see if 1wire overlay is turned on")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("lsmod")
        oneW_modules = ""
        for line in out.splitlines():
            if line[0:4] == "wire":
                oneW_modules = line.split(" ")[-1].split(",")
        if not oneW_modules == "":
            if "w1_gpio" in oneW_modules:
                module_text = "1wire module enabled\n"
            if "w1_therm" in oneW_modules:
                therm_module_text = "1wire thermometer module enabled\n"
                temp_sensor_list = self.find_ds18b20_devices()
                if len(temp_sensor_list) > 0:
                    therm_module_text += "Found " + str(len(temp_sensor_list)) + " temp sensors;\n"
                for item in temp_sensor_list:
                    therm_module_text += "  - " + str(item) + "\n"
            else:
                therm_module_text = "1wire thermometer module NOT enabled\n"
            other_modules = "other one wire modules loaded"
            for module in oneW_modules:
                if not module == "w1_gpio" and not module == "w1_therm":
                    other_modules += ", " + module
            if other_modules == "other one wire modules loaded":
                other_modules = ""
            else:
                other_modules += "\n"
        else:
            module_text = "1wire module NOT enabled\n"
        # Check config file for 1wire overlay
        #             /boot/config.txt file should include 'dtoverlay=w1-gpio'
        onewire_pin_list, onewire_err_text = self.find_dtoverlay_1w_pins()
        enabled_onewire_overlays_text = "Enabled Overlay on GPIO; "
        if len(onewire_pin_list) > 0:
            for item in onewire_pin_list:
                if not item[0] == None:
                    enabled_onewire_overlays_text += item[0]
                    if not item[1] == "" and not item[1] == None:
                        enabled_onewire_overlays_text += " (" + item[1] + "), "
                    else:
                        enabled_onewire_overlays_text += ", "
            onewire_config_file_text = "Found 1wire overlay in /boot/config.txt\n" + enabled_onewire_overlays_text[:-2]
        else:
            onewire_config_file_text = "1wire overlay not found in /boot/config.txt"
            self.edit_1wire_btn.Disable()
            self.remove_1wire_btn.Disable()
        onewire_config_file_text += "\n" + onewire_err_text
        # turn on add new one wire overlay button
        self.add_1wire_btn.Enable()
        # assemble final message and print to screen
        final_1wire_text = module_text + therm_module_text + other_modules + onewire_config_file_text
        MainApp.system_info_pannel.sys_1wire_info.SetLabel(final_1wire_text)
        MainApp.window_self.Layout()
        print(" - " + module_text + therm_module_text + other_modules + onewire_config_file_text)

    def add_1wire(self, e):
        msg = "The Device Tree Overlay is a core system component of the raspberry pi "
        msg += "when adding a One Wire device make sure you select the correct pin.\n"
        msg += "You may have as many one wire overlays in place as you want, "
        msg += "but make sure you remove unsused overlays before using the pin for something else.\n\n"
        msg += 'What gpio pin is the 1wire connected to?'
        generic = '4'
        onewire_dbox = wx.TextEntryDialog(self, msg, "1wire GPIO pin select", generic)
        if onewire_dbox.ShowModal() == wx.ID_OK:
            pin_number = onewire_dbox.GetValue()
            if is_a_valid_and_free_gpio(pin_number) == False:
                err_msg = "Error: Pin must be a number between 2 and 27 which isn't currently assigned to another device"
                d = wx.MessageDialog(self, err_msg, "Error", wx.OK | wx.ICON_ERROR)
                answer = d.ShowModal()
                d.Destroy()
                return "cancelled"
        else:
            return "cancelled"
        onewire_dbox.Destroy()
        gpio_pin = "gpiopin=" + str(pin_number)
        dt_cmd = "dtoverlay=w1-gpio," + gpio_pin
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        config_text = out + "\n" + dt_cmd
        self.update_boot_config(config_text)
        self.find_1wire_devices("e")

    def edit_1wire(self, e):
        edit_1wire_dbox = one_wire_change_pin_dbox(None)
        edit_1wire_dbox.ShowModal()
        self.find_1wire_devices("e")

    def remove_1wire(self, e):
        remove_1wire_dbox = remove_onewire_dbox(None)
        remove_1wire_dbox.ShowModal()
        self.find_1wire_devices("e")

    def update_boot_config(self, config_text):
        question_text = "Are you sure you want to change the pi's /boot/config.txt file?"
        dbox = wx.MessageDialog(self, question_text, "update pigrow /boot/config.txt?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            sftp = ssh.open_sftp()
            folder = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/temp/"
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir " + folder)
            f = sftp.open(folder + 'boot_config.txt', 'w')
            f.write(config_text)
            f.close()
            copy_cmd = "sudo cp --no-preserve=mode,ownership " + folder + "boot_config.txt /boot/config.txt"
            #copy_cmd = "sudo mv /home/" + pi_link_pnl.target_user + "/Pigrow/temp/boot_config.txt /boot/config.txt"
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(copy_cmd)
            print(out, error)
            print("Pi's /boot/config.txt file changed")
    # I2C
    def i2c_check(self):
        # checking for i2c folder in /dev/
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/*i2c*")
        if "/dev/i2c-1" in out:
            i2c_text = ("found i2c bus 1")
            i2c_bus_number = 1
        elif "/dev/i2c-0" in out:
            i2c_bus_number = 0
            i2c_text = ("found i2c bus 0")
        elif "/dev/i2c-" in out:
            i2c_bus_number = int(out.split("/dev/i2c-")[1])
            print("i2c not found on most likely busses, but maybe it's on")
            print (i2c_bus_number)
            print(("trying using bus " + str(i2c_bus_number)))
        else:
            MainApp.system_info_pannel.sys_i2c_info.SetLabel("i2c bus not found")
            return "i2c not found"
        # if i2c bus found perform aditional checks, updates the textbox and returns the bus number
        # check if baurdrate is changed in Config
        self.i2c_baudrate_btn.Enable()
        i2c_baudrate = self.check_i2c_baudrate(i2c_bus_number)
        i2c_text += " baudrate " + str(i2c_baudrate)
        #
        #  also might be worth looking at  sudo cat /sys/module/i2c_bcm2708/parameters/baudrate though it reads 0 when inset I think
        #
        #
        # change text
        MainApp.system_info_pannel.sys_i2c_info.SetLabel(i2c_text)
        # return
        return i2c_bus_number

    def set_baudrate(self, e):
        new_i2c_baudrate = "30000"
        # ask the user what baudrate they want to set
        baud_dbox = wx.TextEntryDialog(self, 'Set i2c baudrate in /boot/config.txt to', 'Change i2c baudrate', new_i2c_baudrate)
        if baud_dbox.ShowModal() == wx.ID_OK:
            new_i2c_baudrate = baud_dbox.GetValue()
        else:
            return "cancelled"
        baud_dbox.Destroy()
        #
        print("changing the i2c baudrate")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        raspberry_config = out.splitlines()
        # put it together again chaning settings line
        config_text = ""
        changed = False
        for line in raspberry_config:
            if "dtparam=i2c_baudrate=" in line:
                line = "dtparam=i2c_baudrate=" + new_i2c_baudrate
                print ("i2c set baudrate changing /boot/config.txt line to " + line)
                changed = True
            config_text = config_text + line + "\n"
        if changed == False:
            print("/boot/config.txt did not have 'dtparam=12c_baudrate=' so adding it")
            config_text = config_text + "dtparam=i2c_baudrate=" + new_i2c_baudrate + "\n"
        self.update_boot_config(config_text)

    def check_i2c_baudrate(self, i2c_bus_number):
        # ask pi to read the pi's boot congif file for i2c baudrate info
        #print("looking at /boot/config.txt file for baudrate setting;")
        # dtparam=i2c_baudrate
        #out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt | grep i2c" + str(i2c_bus_number) + "_baudrate=") #if it wants to know bus num
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt | grep i2c_baudrate=")
        out = out.replace("dtparam=i2c_baudrate=", "")
        out = out.strip()
        if out == "" or out == None:
            #print("Baudrate not changed in /boot/config.txt")
            return "default"
        #else:
            #print("Baudrate changed to;" + str(out))
        return out

    def find_i2c_devices(self, e):
        # this has to be run by a button press because it might
        # in some situations confuse i2c sensors so best
        # not to call it needlessly
        # returns a list of i2c addresses which may be useful at some point
        #                                 when doing live readings or some such
        #                                 but isn't currently used
        ##
        # calsl i2c_check to locate the active i2c bus
        i2c_bus_number = self.i2c_check()
        if not i2c_bus_number == "i2c not found":
            print (i2c_bus_number)
            # check i2c bus with i2cdetect and list found i2c devices
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/usr/sbin/i2cdetect -y " + str(i2c_bus_number))
            print((out, error))
            i2c_devices_found = out.splitlines()
            # trimming text and sorting into a list
            i2c_addresses = []
            for line in i2c_devices_found[1:]:
                line = line[3:].replace("--", "").strip()
                if not line == "":
                    if not len(line) > 2: #only lines with 1 item in
                        i2c_addresses.append(line)
                    else: #lines with more than one item
                        for item in line.split("  "):
                            i2c_addresses.append(item)
            # changing text on screen
            i2c_text = MainApp.system_info_pannel.sys_i2c_info.GetLabel().split("\n")[0]
            if len(i2c_addresses) > 0:
                i2c_text += "\nfound " + str(len(i2c_addresses)) + " devices at; " + str(i2c_addresses)
            else:
                i2c_text += "\nNo devices found"
            MainApp.system_info_pannel.sys_i2c_info.SetLabel(i2c_text)
            # returning a list of i2c device addresses
            MainApp.window_self.Layout()
            return i2c_addresses

    # power controls
    def reboot_pigrow_click(self, e):
        dbox = wx.MessageDialog(self, "Are you sure you want to reboot the pigrow?", "reboot pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo reboot now")
            MainApp.pi_link_pnl.link_with_pi_btn_click("e")
            print((out, error))

    def shutdown_pi_click(self, e):
        dbox = wx.MessageDialog(self, "Are you sure you want to shutdown the pi?", "Shutdown Pi?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo shutdown now")
            MainApp.pi_link_pnl.link_with_pi_btn_click("e")
            print((out, error))
    # system checks
    def check_pi_diskspace(self):
        #check pi for hdd/sd card space
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("df -l /")
        if len(out) > 1:
            responce_list = []
            for item in out.split(" "):
                if len(item) > 0:
                    responce_list.append(item)
            hdd_total = responce_list[-5]
            hdd_percent = responce_list[-2]
            hdd_available = responce_list[-3]
            hdd_used = responce_list[-4]
            return hdd_total, hdd_percent, hdd_available, hdd_used
        else:
            return "Error", "Error", "Error", "Error"

    def check_pi_os(self):
        # check what os the pi is running
        os_name = "undetermined"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /etc/os-release")
        for line in out.split("\n"):
            if "PRETTY_NAME=" in line:
                os_name = line.split('"')[1]
        return os_name

    def check_for_pigrow_folder(self, hdd_used="unknown"):
        #check if pigrow folder exits and read size
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("du -s ~/Pigrow/")
        if not "No such file or directory" in error:
            pigrow_size = out.split("\t")[0]
            try:
                folder_pcent = float(pigrow_size) / float(hdd_used) * 100
                folder_pcent = format(folder_pcent, '.2f')
            except: #mostly like due to not being a number
                folder_pcent = "undetermined"
        else: #i.e. when no such file or directory is the error
            pigrow_size = "not found"
            folder_pcent = "not found"
        return pigrow_size, folder_pcent

    def check_git(self):
        update_needed = False
        #
        # read git update info
        #
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ remote -v update")
        if len(error) > 1:
            git_text = error.split("\n")
            count = 0
            for line in git_text:
                if "origin/master" in line:
                    master_branch = line
                    count = count + 1
            if count > 1:
                print("ERROR ERROR TWO MASTER BRANCHES WTF?")
            elif count == 0:
                #print("No Pigrow install detected")
                install_needed = True
            elif count == 1:
                if "[up to date]" in master_branch:
                    #print("master branch is upto date")
                    update_needed = False
                else:
                    #print("Master branch requires updating")
                    update_needed = True
        #
        # Read git status
        #
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ status --untracked-files no")
        if "Your branch and 'origin/master' have diverged" in out:
            update_needed = 'diverged'
        elif "Your branch is" in out:
            git_line = out.split("\n")[1]
            git_update = git_line.split(" ")[3]
            if git_update == 'behind':
                update_needed = True
                git_num = git_line.split(" ")[6]
            elif git_update == 'ahead':
                update_needed = 'ahead'
            #elif git_update == 'up-to-date':
            #    print("says its up to date")
        else:
            update_needed = 'error'

        # determine what sort of update is required
        if update_needed == True:
            MainApp.system_info_pannel.sys_pigrow_update.SetLabel("update required, " + str(git_num) + " updates behind")
            update_type = "clean"
        elif update_needed == False:
            MainApp.system_info_pannel.sys_pigrow_update.SetLabel("master branch is upto date")
            update_type = "none"
        elif update_needed == 'ahead':
            MainApp.system_info_pannel.sys_pigrow_update.SetLabel("Caution Required!\nYou modified your Pigrow code")
            update_type = "merge"
        elif update_needed == 'diverged':
            MainApp.system_info_pannel.sys_pigrow_update.SetLabel("Caution Required!\nYou modified your Pigrow code")
            update_type = "merge"
        elif update_needed == 'error':
            if install_needed == True:
                MainApp.system_info_pannel.sys_pigrow_update.SetLabel("Pigrow folder not found.")
                update_type = "error"
        else:
            MainApp.system_info_pannel.sys_pigrow_update.SetLabel("Some confusion with git, sorry.")
            update_type = "error"
        return update_type

    def check_video_power(self):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd display_power")
        out = out.strip().strip("display_power=")
        if out == "0":
            message = "Video power off"
        else:
            tv_out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("tvservice -s")
            message = "Video power on\n" + tv_out.strip()
        return message

    def check_video_items(self):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd get_lcd_info")
        msg = out.strip().strip("")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd dispmanx_list")
        msg += "\n  Dispmanx Items;\n" +  out.strip().strip("")
        return msg

    def check_pi_power_warning(self):
        #check for low power WARNING
        # this only works on certain versions of the pi
        # it checks the power led value
        # it's normally turned off as a LOW POWER warning
        display_message = "LED1: "
        if not "pi 3" in MainApp.system_info_pannel.sys_pi_revision.GetLabel().lower():
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /sys/class/leds/led1/brightness")
            out = out.strip()
            if out == "255":
                display_message = display_message + "No Warning"
            elif out == "" or out == None:
                display_message = display_message + "Not Supported"
            else:
                display_message = display_message + "Low power warning! (" + str(out).strip() + ")"
        else:
            display_message = display_message + "feature disabled on pi 3"
        #
        # New improved low power warning
        #
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd get_throttled")
        out = out.strip().strip("throttled=")
        display_message = display_message + "\nvcgencmd: " # + out
        if out == "0x0":
            display_message = display_message + " No Warning"
        #
        out_int = int(out, 16)
        #display_message += "\nint-" + str(out_int)
        bit_nums = [[0, "Under_Voltage detected"],
                    [1, "Arm frequency capped"],
                    [2, "Currently throttled"],
                    [3, "Soft temperature limit active"],
                    [16, "Under-voltage has occurred"],
                    [17, "Arm frequency capping has occurred"],
                    [18, "Throttling has occurred"],
                    [19, "Soft temperature limit has occurred"]]
        for x in range(0, len(bit_nums)):
            bit_num  = bit_nums[x][0]
            bit_text = bit_nums[x][1]
            if (out_int & ( 1 << bit_num )):
                display_message += "\n  - " + bit_text
                #display_message += "\n(bit-" + str(bit_num) + ") " + bit_text

        #
        MainApp.system_info_pannel.sys_power_status.SetLabel(display_message)

    def check_pi_version(self):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /proc/device-tree/model")
        return out.strip()

    def find_network_name(self):
        # Read the currently connected network name
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/sbin/iwgetid")
        try:
            network_name = out.split('"')[1]
            return network_name
        except Exception as e:
            print(("fiddle and fidgets! find network name didn't work - " + str(e)))
            return "unable to read"

    def find_added_wifi(self):
        # read /etc/wpa_supplicant/wpa_supplicant.conf for listed wifi networks
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo cat /etc/wpa_supplicant/wpa_supplicant.conf")
        out = out.splitlines()
        in_a_list = False
        network_items = []
        network_list = []
        for line in out:
            if "}" in line:
                in_a_list = False
                # list finished sort into fields
                ssid = ""
                psk = ""
                key_mgmt = ""
                other = ""
                for x in network_items:
                    if "ssid=" in x:
                        ssid = x[5:]
                    elif "psk=" in x:
                        psk = x[4:]
                        psk = "(password hidden)"
                    elif "key_mgmt=" in x:
                        key_mgmt = x[9:]
                    else:
                        other = other + ", "
                network_list.append([ssid, key_mgmt, psk, other])
                network_items = []
            if in_a_list == True:
                network_items.append(line.strip())
            if "network" in line:
                in_a_list = True
        network_text = ""
        for item in network_list:
            for thing in item:
                network_text += thing + " "
            network_text += "\n"
        return network_text

    def find_connected_webcams(self):
        # picam info
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd get_camera")
        if "detected=" in out:
            out = out.split('detected=')[1].strip()
            if out == "0":
                # If no cam detected check if camera module is enabled
                get_cam, get_error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo raspi-config nonint get_camera")
                if get_cam.strip() == "1":
                    picam_text = "Picam Module Not Enabled\n"
                elif get_cam.strip() == "0":
                    picam_text = 'Picam Enabled, None detected\n'
                else:
                    print(out, error)
                    picam_text = "Unable to determine if picam module is enabled"
            elif out == "1":
                picam_text = "1 Picam\n"
            elif out == "2":
                picam_text = "Dual Picams\n"
            else:
                picam_text = 'Multipul Picams'
        else:
            picam_text = " Command line output did not match expected format, possibly because vcgencmd is not installed"
            picam_text += " or possibly because your language is set to something other than english, if so please let me know."
        print(picam_text)
        # web camera info
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/video*")
        if "No such file or directory" in error:
            cam_text = "No webcams"
        else:
            camera_list = out.strip().split(" ")
            try:
                if len(camera_list) == 1:
                    out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("udevadm info --query=all /dev/video0 |grep ID_MODEL=")
                    cam_name = out.split("=")[1].strip()
                    cam_text = cam_name
                elif len(camera_list) > 1:
                    for cam in camera_list:
                        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("udevadm info --query=all " + cam + " |grep ID_MODEL=")
                        if not "=" in out:
                            cam_name = "unknown device"
                        else:
                            cam_name = out.split("=")[1].strip()
                            cam_text = cam_name + "\n       on " + cam + "\n"
            except:
                print("Failed to identify video source")
                cam_text = "Error reading webcams"
        cam_text = picam_text + cam_text
        return cam_text

    def get_pi_time_diff(self):
        # just asks the pi the data at the same time grabs local datetime
        # returns to the user as strings
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("date")
        local_time = datetime.datetime.now()
        local_time_text = local_time.strftime("%a %d %b %X") + " " + str(time.tzname[0]) + " " + local_time.strftime("%Y")
        pi_time = out.strip()
        return local_time_text, pi_time
    # buttons
    def read_system_click(self, e):
        ### pi system interrogation
        # disk space
        hdd_total, hdd_percent, hdd_available, hdd_used = self.check_pi_diskspace()
        MainApp.system_info_pannel.sys_hdd_total.SetLabel(str(hdd_total) + " KB")
        MainApp.system_info_pannel.sys_hdd_remain.SetLabel(str(hdd_available) + " KB")
        MainApp.system_info_pannel.sys_hdd_used.SetLabel(str(hdd_used) + " KB (" + str(hdd_percent) + ")")
        # installed OS
        os_name = self.check_pi_os()
        MainApp.system_info_pannel.sys_os_name.SetLabel(os_name)
        # check if pigrow folder exits and read size
        pigrow_size, folder_pcent = self.check_for_pigrow_folder(hdd_used)
        if pigrow_size == "not found":
            MainApp.system_info_pannel.sys_pigrow_folder.SetLabel("Pigrow folder now found")
        else:
            MainApp.system_info_pannel.sys_pigrow_folder.SetLabel(str(pigrow_size) + " KB (" +str(folder_pcent) + "% of used)")
        # check if git upate needed
        self.check_git() #ugly and deals with UI itself, needs upgrade and clean but git is a headfuck so like oneday...
        # pi board revision
        pi_version = self.check_pi_version()
        MainApp.system_info_pannel.sys_pi_revision.SetLabel(pi_version)
        # check for low power warning
        self.check_pi_power_warning()
        # check video power
        MainApp.system_info_pannel.sys_video_power_info.SetLabel(self.check_video_power())
        MainApp.system_info_pannel.sys_video_info.SetLabel(self.check_video_items())
        # WIFI
        network_name = self.find_network_name()
        MainApp.system_info_pannel.sys_network_name.SetLabel(network_name)
        network_text = self.find_added_wifi()
        MainApp.system_info_pannel.wifi_list.SetLabel(network_text)
        # camera info
        camera_names = self.find_connected_webcams()
        MainApp.system_info_pannel.sys_camera_info.SetLabel(camera_names)
        # datetimes and difference
        local_time, pi_time = self.get_pi_time_diff()
        MainApp.system_info_pannel.sys_pi_date.SetLabel(pi_time)
        MainApp.system_info_pannel.sys_pc_date.SetLabel(str(local_time))
        # GPIO info pannel
        self.i2c_check()
        # Tidy the gui up...
        MainApp.window_self.Layout()

    def install_click(self, e):
        install_dbox = install_dialog(None, title='Install Pigrow to Raspberry Pi')
        install_dbox.ShowModal()

    def update_pigrow_click(self, e):
        update_dbox = upgrade_pigrow_dialog(None, title='Update Pigrow to Raspberry Pi')
        update_dbox.ShowModal()

    def run_cmd_on_pi_click(self, e):
        msg = 'Input command to run on pi\n\n This will run the command and wait for it to finish before\ngiving results and resuming the gui'
        generic = 'ls ~/Pigrow/'
        run_cmd_dbox = wx.TextEntryDialog(self, msg, "Run command on pi", generic)
        if run_cmd_dbox.ShowModal() == wx.ID_OK:
            cmd_to_run = run_cmd_dbox.GetValue()
        else:
            return "cancelled"
        run_cmd_dbox.Destroy()
        # run command on the pi
        print("Running command; " + str(cmd_to_run))
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd_to_run)
        print(out, error)
        # tell user about it with a dialog boxes
        dbox = scroll_text_dialog(None, str(out) + str(error), "Output of " + str(cmd_to_run), False)
        dbox.ShowModal()
        dbox.Destroy()

    def edit_boot_config_click(self ,e):
        boot_conf = edit_boot_config_dialog(None)
        boot_conf.ShowModal()

class edit_boot_config_dialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(edit_boot_config_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 600))
        self.SetTitle("Edit /boot/config.txt")
    def InitUI(self):
        self.boot_config_original, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        header_text = "This file is an integral part of the the Raspbery Pi's system\n"
        header_text += " settings loaded here take effect right at the start of the boot procediure\n"
        header_text += " so even minor errors can cause serious problems."
        header_text += "\n Please read the offical documentation carefully; https://www.raspberrypi.org/documentation/configuration/config-txt/ "
        header = wx.StaticText(self, label=header_text)
        self.config_text = wx.TextCtrl(self, -1, self.boot_config_original, size=(800,600), style=wx.TE_MULTILINE)
        post_text = "Changes made won't take effect until you reboot your pi"
        post_text += "\n \nWarning : Mistakes editing this file may cause your Pi to fail to boot"
        post = wx.StaticText(self, label=post_text)
        #
        ok_btn = wx.Button(self, label='OK', size=(175, 30))
        ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)

        # sizers
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.AddStretchSpacer(1)
        btnsizer.Add(ok_btn, 0, wx.ALL, 5)
        btnsizer.AddStretchSpacer(1)
        btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
        btnsizer.AddStretchSpacer(1)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(self.config_text, 0, wx.EXPAND|wx.ALL, 3)
        main_sizer.Add(post, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizerAndFit(main_sizer)

    def ok_click(self, e):
        config_text = self.config_text.GetValue()
        if not config_text == self.boot_config_original:
            system_ctrl_pnl.update_boot_config(None, config_text)
        self.Destroy()

class one_wire_change_pin_dbox(wx.Dialog):
    '''
    This opens a dialog box whixh allows you to change the gpio pin associated with
    the one wire devices, it only works with lines that include a ,gpiopin= entry and
    should not be called when there are complications in the file such as dtparam=gpiopin=
    being used to change the pin number on a subsiquent line.
    This is designed to work only with lines added by us or the offical raspi_conf tools,
    the button for it should be disabled if any complications are in the files
    '''
    def __init__(self, *args, **kw):
        super(one_wire_change_pin_dbox, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 350))
        self.SetTitle("Change 1Wire Overlay Pin")
    def InitUI(self):

        # draw the pannel and text
        pnl = wx.Panel(self)

        title = wx.StaticText(self,  label='Change 1wire Pin')
        title.SetFont(shared_data.title_font)
        sub_text = wx.StaticText(self,  label="Editing the /boot/config.txt file's \ndtoverlay=w1-gpio,gpiopin= lines")
        sub_text.SetFont(shared_data.sub_title_font)
        # add drop down box with list of 1wire overlay gpio pins
        #
        tochange_gpiopin_l = wx.StaticText(self, label='current 1wire gpio pin -')
        pin_list_with_comment, error_msg = system_ctrl_pnl.find_dtoverlay_1w_pins(MainApp.system_ctrl_pannel)
        if not error_msg == "":
            print("!!! /boot/config.txt file too complex for automatic editing, sorry")
            self.Destroy()
        pin_list = []
        for item in pin_list_with_comment:
            pin_list.append(item[0])
        self.tochange_gpiopin_cb = wx.ComboBox(self, choices = pin_list, size=(110, 25))
        if len(pin_list) > 0:
            self.tochange_gpiopin_cb.SetValue(pin_list[0])
        #
        new_gpiopin_l = wx.StaticText(self, label='Change to GPIO pin -')
        self.new_gpiopin_tc = wx.TextCtrl(self, size=(110, 25)) # new number
        self.new_gpiopin_tc.Bind(wx.EVT_TEXT, self.make_config_line)
        line_l = wx.StaticText(self, label="/boot/config/txt line")
        self.line_t = wx.StaticText(self, label="")
        # ok and cancel Buttons
        self.ok_btn = wx.Button(self, label='OK', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # sizers
        old_gpio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        old_gpio_sizer.Add(tochange_gpiopin_l, 0, wx.ALL, 2)
        old_gpio_sizer.Add(self.tochange_gpiopin_cb, 0, wx.ALL, 2)
        new_gpio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        new_gpio_sizer.Add(new_gpiopin_l, 0, wx.ALL, 2)
        new_gpio_sizer.Add(self.new_gpiopin_tc, 0, wx.ALL, 2)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(old_gpio_sizer, 0, wx.ALL, 3)
        main_sizer.Add(new_gpio_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(line_l, 0, wx.ALL, 3)
        main_sizer.Add(self.line_t, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def make_config_line(self, e):
        gpiopin = self.new_gpiopin_tc.GetValue()
        # check pin valid and disable ok button if not, maybe paint box red
        self.line_t.SetLabel("dtoverlay=w1-gpio,gpiopin=" + gpiopin + "\n")
        if is_a_valid_and_free_gpio(gpiopin):
            self.line_t.SetBackgroundColour((250,250,250))
            self.ok_btn.Enable()
        else:
            self.line_t.SetBackgroundColour((230, 100, 100))
            self.ok_btn.Disable()

    def ok_click(self, e):
        new_line = self.line_t.GetLabel()
        old_pin =  self.tochange_gpiopin_cb.GetValue()
        old_line = "dtoverlay=w1-gpio,gpiopin=" + old_pin
        if old_pin == "default (4)":
            old_line = "dtoverlay=w1-gpio"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        config_lines = out.splitlines()
        config_text = ""
        for line in config_lines:
            if old_line in line:
                print("--Changing " + line + " to " + new_line)
                line = new_line
            config_text = config_text + line + "\n"
        system_ctrl_pnl.update_boot_config(MainApp.system_ctrl_pannel, config_text)
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class remove_onewire_dbox(wx.Dialog):
    '''lists the gpio pins mentioned in the 1wire config section of
       the /boot/config.txt file and gives you the option to remove one line
       this only works with neat and tidy config files
    '''
    def __init__(self, *args, **kw):
        super(remove_onewire_dbox, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 350))
        self.SetTitle("Remove 1Wire Overlay Pin")
    def InitUI(self):

        # draw the pannel and text
        pnl = wx.Panel(self)
        title = wx.StaticText(self,  label='Remove 1wire Pin')
        title.SetFont(shared_data.title_font)
        sub_text = wx.StaticText(self,  label="Editing the /boot/config.txt file and removing \n the selected dtoverlay=w1-gpio,gpiopin= line")
        sub_text.SetFont(shared_data.sub_title_font)
        # Select Pin
        tochange_gpiopin_l = wx.StaticText(self, label='1wire gpio pin to remove from config')
        pin_list_with_comment, error_msg = system_ctrl_pnl.find_dtoverlay_1w_pins(MainApp.system_ctrl_pannel)
        if not error_msg == "":
            print("!!! /boot/config.txt file too complex for automatic editing, sorry")
            self.Destroy()
        pin_list = []
        for item in pin_list_with_comment:
            pin_list.append(item[0])
        self.tochange_gpiopin_cb = wx.ComboBox(self, choices = pin_list, size=(110, 25))
        if len(pin_list) > 0:
            self.tochange_gpiopin_cb.SetValue(pin_list[0])
        # ok and cancel Buttons
        self.ok_btn = wx.Button(self, label='OK', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # Sizers
        old_gpio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        old_gpio_sizer.Add(tochange_gpiopin_l, 0, wx.ALL, 2)
        old_gpio_sizer.Add(self.tochange_gpiopin_cb, 0, wx.ALL, 2)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(old_gpio_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def ok_click(self, e):
        old_line = "dtoverlay=w1-gpio,gpiopin=" + self.tochange_gpiopin_cb.GetValue()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        config_lines = out.splitlines()
        config_text = ""
        for line in config_lines:
            if not old_line in line:
                config_text = config_text + line + "\n"
            else:
                print(" -- Removing " + line)
        system_ctrl_pnl.update_boot_config(MainApp.system_ctrl_pannel, config_text)
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class system_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        # Tab Title
        title_l = wx.StaticText(self,  label='System Control Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Configure the raspberry pi on which the pigrow code runs', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)
        #
        ## placing the information boxes
        #
        # base system info (Top - Left) Sizer Pannel
        # System
        system_l = wx.StaticText(self,  label='System', size=(25,25))
        system_l.SetFont(shared_data.item_title_font)
        pi_rev_l = wx.StaticText(self,  label='Hardware -')
        self.sys_pi_revision = wx.StaticText(self,  label='--')
        self.sys_pi_revision.SetFont(shared_data.info_font)
        os_name_l = wx.StaticText(self,  label='OS installed -')
        self.sys_os_name = wx.StaticText(self,  label='--')
        self.sys_os_name.SetFont(shared_data.info_font)
        # Pigrow update status
        pigrow_l = wx.StaticText(self,  label='Pigrow', size=(25,25))
        pigrow_l.SetFont(shared_data.item_title_font)
        update_status_l = wx.StaticText(self,  label='Update Status -')
        self.sys_pigrow_update = wx.StaticText(self,  label='--')
        self.sys_pigrow_update.SetFont(shared_data.info_font)
        # SDcard details
        storage_space_l = wx.StaticText(self,  label='Storage Space', size=(25,25))
        storage_space_l.SetFont(shared_data.item_title_font)
        total_hdd_l = wx.StaticText(self,  label='               Total  -')
        self.sys_hdd_total = wx.StaticText(self,  label='--')
        self.sys_hdd_total.SetFont(shared_data.info_font)
        free_hdd_l = wx.StaticText(self,  label='                Free  -')
        self.sys_hdd_remain = wx.StaticText(self,  label='--')
        self.sys_hdd_remain.SetFont(shared_data.info_font)
        used_hdd_l = wx.StaticText(self,  label='                 Used  -')
        self.sys_hdd_used = wx.StaticText(self,  label='--')
        self.sys_hdd_used.SetFont(shared_data.info_font)
        pigrow_folder_hdd_l = wx.StaticText(self,  label='Pigrow folder  -')
        self.sys_pigrow_folder = wx.StaticText(self,  label='--')
        self.sys_pigrow_folder.SetFont(shared_data.info_font)
        #power level warning details
        power_l = wx.StaticText(self,  label='Power', size=(25,25))
        power_l.SetFont(shared_data.item_title_font)
        power_status_l = wx.StaticText(self,  label='Power Warning -')
        self.sys_power_status = wx.StaticText(self,  label='--')
        self.sys_power_status.SetFont(shared_data.info_font)
        # Pi datetime vs local pc datetime
        time_l = wx.StaticText(self,  label='Date and Time', size=(25,25))
        time_l.SetFont(shared_data.item_title_font)
        pi_time_l = wx.StaticText(self,  label='Time on Pi -', style=wx.ALIGN_RIGHT)
        self.sys_pi_date = wx.StaticText(self,  label='--')
        self.sys_pi_date.SetFont(shared_data.info_font)
        local_time_l = wx.StaticText(self,  label='Time on local pc -', style=wx.ALIGN_RIGHT)
        self.sys_pc_date = wx.StaticText(self,  label='--')
        self.sys_pc_date.SetFont(shared_data.info_font)
        #
        ## peripheral hardware (top-right)
        #
        #camera details
        camera_title_l = wx.StaticText(self,  label='Camera', size=(25,25))
        camera_title_l.SetFont(shared_data.item_title_font)
        camera_l = wx.StaticText(self,  label=' - ')
        self.sys_camera_info = wx.StaticText(self,  label='--')
        self.sys_camera_info.SetFont(shared_data.info_font)
        # GPIO set up details
        gpio_overlay_l = wx.StaticText(self,  label='GPIO Overlays', size=(25,25))
        gpio_overlay_l.SetFont(shared_data.item_title_font)
        i2c_l = wx.StaticText(self,  label='I2C -', size=(-1,25))
        self.sys_i2c_info = wx.StaticText(self,  label='--')
        self.sys_i2c_info.SetFont(shared_data.info_font)
        uart_l = wx.StaticText(self,  label='UART -', size=(-1,25))
        self.sys_uart_info = wx.StaticText(self,  label='- (not implimented) -', size=(300,25))
        self.sys_uart_info.SetFont(shared_data.info_font)
        onewire_l = wx.StaticText(self,  label='1 Wire -', size=(-1,25))
        self.sys_1wire_info = wx.StaticText(self,  label='- click to scan -', size=(300,-1))
        self.sys_1wire_info.SetFont(shared_data.info_font)
        # Video info
        video_l = wx.StaticText(self,  label='Video', size=(25,25))
        video_l.SetFont(shared_data.item_title_font)
        video_power_l = wx.StaticText(self,  label='Power -', size=(-1,25))
        self.sys_video_power_info = wx.StaticText(self,  label='--', size=(300,-1))
        self.sys_video_power_info.SetFont(shared_data.info_font)
        video_res_l = wx.StaticText(self,  label='Resolution -', size=(-1,25))
        self.sys_video_info = wx.StaticText(self,  label='--', size=(300,-1))
        self.sys_video_info.SetFont(shared_data.info_font)
        #dispmanx_l = wx.StaticText(self,  label='Dispmanx -', size=(-1,25))
        #self.dispmanx_info = wx.StaticText(self,  label='--', size=(300,-1))
        #self.dispmanx_info.SetFont(shared_data.info_font)

        # network pannel - lower half
        #wifi deatils
        network_l = wx.StaticText(self,  label='Network', size=(90,30))
        network_l.SetFont(shared_data.item_title_font)
        current_network_l = wx.StaticText(self,  label='Connected to -')
        self.sys_network_name = wx.StaticText(self,  label='-network name-')
        self.sys_network_name.SetFont(shared_data.info_font)
        saved_wifi_l = wx.StaticText(self,  label='Saved Wifi Networks')
        saved_wifi_l.SetFont(shared_data.item_title_font)
        self.wifi_list = wx.StaticText(self,  label='--')
        found_wifi_l = wx.StaticText(self,  label='Found Wifi Networks')
        found_wifi_l.SetFont(shared_data.item_title_font)
        self.scan_wifi_btn = wx.Button(self, label='Scan', size=(75, 25))
        self.scan_wifi_btn.Bind(wx.EVT_BUTTON, self.scan_wifi_btn_click)
        self.available_wifi_list = wx.StaticText(self,  label='-')

        #
        # Sizers
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        # base system info (Top - Left) Sizer Pannel
        # system
        hardware_version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hardware_version_sizer.Add(pi_rev_l, 0, wx.ALL, 3)
        hardware_version_sizer.Add(self.sys_pi_revision, 0, wx.ALL|wx.EXPAND, 3)
        os_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        os_name_sizer.Add(os_name_l, 0, wx.ALL, 3)
        os_name_sizer.Add(self.sys_os_name, 0, wx.ALL|wx.EXPAND, 3)
        # pigrow update status
        update_status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        update_status_sizer.Add(update_status_l, 0, wx.ALL, 3)
        update_status_sizer.Add(self.sys_pigrow_update, 0, wx.ALL|wx.EXPAND, 3)
        # sd card
        sd_size_sizer = wx.FlexGridSizer(4, 2, 0, 5)
        sd_size_sizer.AddMany( [(total_hdd_l, 0, wx.ALIGN_RIGHT),
            (self.sys_hdd_total, 0),
            (free_hdd_l, 0, wx.ALIGN_RIGHT),
            (self.sys_hdd_remain, 0),
            (used_hdd_l, 0, wx.ALIGN_RIGHT),
            (self.sys_hdd_used, 0),
            (pigrow_folder_hdd_l, 0, wx.ALIGN_RIGHT),
            (self.sys_pigrow_folder, 0)])
        # power
        power_status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_status_sizer.Add(power_status_l, 0, wx.ALL, 3)
        power_status_sizer.Add(self.sys_power_status, 0, wx.ALL|wx.EXPAND, 3)
        # time
        time_sizer = wx.FlexGridSizer(2, 2, 0, 5)
        time_sizer.AddMany( [(pi_time_l, 0, wx.ALIGN_RIGHT),
            (self.sys_pi_date, 0),
            (local_time_l, 0, wx.ALIGN_RIGHT),
            (self.sys_pc_date, 0)])
        # base system sizer - top-left
        base_system_info_sizer = wx.BoxSizer(wx.VERTICAL)
        base_system_info_sizer.Add(system_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(hardware_version_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(os_name_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(pigrow_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(update_status_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(storage_space_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(sd_size_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(power_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(power_status_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(time_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(time_sizer, 0, wx.LEFT, 3)
        # peripheral hardware (top-right)
        cam_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cam_name_sizer.Add(camera_l, 0, wx.ALL, 3)
        cam_name_sizer.Add(self.sys_camera_info, 0, wx.ALL|wx.EXPAND, 3)
        overlays_sizer = wx.FlexGridSizer(3, 2, 3, 5)
        overlays_sizer.AddMany( [(i2c_l, 0, wx.ALIGN_RIGHT),
            (self.sys_i2c_info, 0),
            (uart_l, 0, wx.ALIGN_RIGHT),
            (self.sys_uart_info, 0),
            (onewire_l, 0, wx.ALIGN_RIGHT),
            (self.sys_1wire_info, 0)])
        video_power_sizer = wx.BoxSizer(wx.HORIZONTAL)
        video_power_sizer.Add(video_power_l, 0, wx.ALL, 3)
        video_power_sizer.Add(self.sys_video_power_info, 0, wx.ALL|wx.EXPAND, 3)
        video_res_sizer = wx.BoxSizer(wx.HORIZONTAL)
        video_res_sizer.Add(video_res_l, 0, wx.ALL, 3)
        video_res_sizer.Add(self.sys_video_info, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer = wx.BoxSizer(wx.VERTICAL)
        peripheral_device_sizer.Add(camera_title_l, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer.Add(cam_name_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        peripheral_device_sizer.Add(gpio_overlay_l, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer.Add(overlays_sizer, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer.Add(video_l, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer.Add(video_power_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        peripheral_device_sizer.Add(video_res_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        # Top panel area
        panel_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_area_sizer.Add(base_system_info_sizer, 0, wx.ALL, 0)
        panel_area_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(5, -1), style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        panel_area_sizer.Add(peripheral_device_sizer, 0, wx.ALL|wx.EXPAND, 0)
        # wifi area sizers
        current_network_sizer = wx.BoxSizer(wx.HORIZONTAL)
        current_network_sizer.Add(current_network_l, 0, wx.LEFT, 3)
        current_network_sizer.Add(self.sys_network_name, 0, wx.LEFT, 30)
        wifi_area_sizer = wx.BoxSizer(wx.VERTICAL)
        wifi_area_sizer.Add(network_l, 0, wx.ALL, 0)
        saved_wifi_sizer = wx.BoxSizer(wx.VERTICAL)
        saved_wifi_sizer.Add(saved_wifi_l, 0, wx.ALL, 5)
        saved_wifi_sizer.Add(self.wifi_list, 0, wx.LEFT, 30)
        found_wifi_label_and_button = wx.BoxSizer(wx.HORIZONTAL)
        found_wifi_label_and_button.Add(found_wifi_l, 0, wx.ALL, 5)
        found_wifi_label_and_button.Add(self.scan_wifi_btn, 0, wx.ALL, 5)
        found_wifi_sizer = wx.BoxSizer(wx.VERTICAL)
        found_wifi_sizer.Add(found_wifi_label_and_button, 0, wx.ALL, 5)
        found_wifi_sizer.Add(self.available_wifi_list, 0, wx.LEFT, 30)
        wifi_panels_sizer = wx.BoxSizer(wx.HORIZONTAL)
        wifi_panels_sizer.AddStretchSpacer(1)
        wifi_panels_sizer.Add(saved_wifi_sizer, 0, wx.ALL, 20)
        wifi_panels_sizer.AddStretchSpacer(1)
        wifi_panels_sizer.Add(found_wifi_sizer, 0, wx.ALL, 20)
        wifi_panels_sizer.AddStretchSpacer(1)
        wifi_area_sizer.Add(current_network_sizer, 0, wx.LEFT, 30)
        wifi_area_sizer.Add(wifi_panels_sizer, 0, wx.ALL, 0)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(panel_area_sizer, 0, wx.ALL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(wifi_area_sizer, 0, wx.ALL, 7)
        self.SetSizer(main_sizer)

    def scan_wifi_btn_click(self, e):
        print("Pi is scanning for wifi...")
        MainApp.status.write_bar("Pi is scanning for wifi...")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo iwlist scan |grep ESSID")
        out = out.splitlines()
        list_of_network_text = ""
        for line in out:
            if "ESSID:" in line:
                line = line.split("ESSID:")[1]
                list_of_network_text += line + "\n"
        self.available_wifi_list.SetLabel(list_of_network_text)
        MainApp.status.write_bar("Ready...")
        MainApp.window_self.Layout()

class upgrade_pigrow_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(upgrade_pigrow_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 675))
        self.SetTitle("Upgrade Pigrow")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        title = wx.StaticText(self,  label='Upgrade Pigrow')
        sub_title = wx.StaticText(self,  label='Use GIT to update the Pigrow to the newest version.')
        title.SetFont(shared_data.title_font)
        sub_title.SetFont(shared_data.sub_title_font)
        # see which files are changed locally
        local_l = wx.StaticText(self,  label='Local;')
        local_l.SetFont(shared_data.sub_title_font)
        local_changes_tc = wx.TextCtrl(self, -1, "--", size=(500,200), style=wx.TE_MULTILINE)
        changes = self.read_git_dif()
        local_changes_tc.SetLabel(str(changes))
        # see which files are changed remotely
        repo_l = wx.StaticText(self,  label='Repo;')
        repo_l.SetFont(shared_data.sub_title_font)
        remote_changes_tc = wx.TextCtrl(self, -1, "--", size=(500,200), style=wx.TE_MULTILINE)
        repo_changes, num_repo_changed_files = self.read_repo_changes()
        remote_changes_tc.SetValue(repo_changes)
        # upgrade type
        pigrow_status = wx.StaticText(self,  label='Pigrow Status;')
        pigrow_status.SetFont(shared_data.sub_title_font)
        upgrade_type = self.determine_upgrade_type(repo_changes)
        upgrade_type_tb = wx.StaticText(self,  label=upgrade_type)
        if upgrade_type == "behind":
            upgrade_type_tb.SetForegroundColour((255,75,75))
        elif upgrade_type == "up-to-date":
            upgrade_type_tb.SetForegroundColour((25,150,25))
        upgrade_type_tb.SetFont(shared_data.info_font)
        # upgrade and cancel buttons
        self.upgrade_btn = wx.Button(self, label='Upgrade', size=(175, 30))
        self.upgrade_btn.Bind(wx.EVT_BUTTON, self.upgrade_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        #Sizers
        upgrade_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        upgrade_type_sizer.Add(pigrow_status, 0, wx.ALL, 4)
        upgrade_type_sizer.Add(upgrade_type_tb, 0, wx.ALL, 4)
        local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_sizer.Add(local_l, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        local_sizer.Add(local_changes_tc, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        remote_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remote_sizer.Add(repo_l, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        remote_sizer.Add(remote_changes_tc, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upgrade_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(upgrade_type_sizer, 0, wx.TOP, 15)
        main_sizer.Add(remote_sizer, 0, wx.TOP, 25)
        main_sizer.Add(local_sizer, 0, wx.TOP, 10)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL, 3)
        self.SetSizer(main_sizer)

    # git diff --name-only HEAD@{0} HEAD@{1}               # shows the most recent changes, filenames
    # git log --pretty=oneline --name-status HEAD^..HEAD   # shows update log changes since last update

    def determine_upgrade_type(self, num_repo_changed_files):
        # looks at available info and offers best upgrade options
        update_needed = "not determined"
        if len(num_repo_changed_files) > 0:
            upgrade_needed = True
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ status --untracked-files no")
        if "have diverged" in out:
            update_needed = 'diverged'
        for line in out.splitlines():
            if "Your branch is" in line:
                if 'behind' in line:
                    update_needed = 'behind'
                    git_num = line.split(" ")[6]
                elif 'ahead' in line:
                    update_needed = 'ahead'
                elif "up-to-date" in line:
                    update_needed = 'up-to-date'
        return update_needed

    def read_repo_changes(self):
        # lists changes made to the remote (githubed) version since our last update.
        repo_changes = "getting to it soon..."
        # grabbing info from github but not updating anything yet
        print("fetching repo info from git")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ fetch -v")
        print((out, error))
        print("compairing us with them")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ diff origin/master master --stat")
        print((out, error))
        # parse into usable data
        changed_files, num_files_changed, num_insertions, num_deletions = self.parse_git_diff_info(out)
        display_text = str(num_files_changed) + " Files changed"
        for item in changed_files:
            display_text += "\n   " + str(item)
        return display_text, changed_files

    def read_git_dif(self):
        # could use "diff --name-only" instead of --stat
        # checks for changes we've made locally to our git folder
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git -C ~/Pigrow/ diff --stat")
        # parse into useable data
        changed_files, num_files_changed, num_insertions, num_deletions = self.parse_git_diff_info(out)
        display_text = str(num_files_changed) + " Files changed;"
        for item in changed_files:
            display_text += "\n     " + str(item)
        return display_text

    def parse_git_diff_info(self, git_diff_text):
        # convert output from "git diff --stat"  into list and numbers
        # create blank variables
        changed_files = []
        num_files_changed = "0"
        num_insertions = "0"
        num_deletions = "0"
        display_text = ""
        # split 'git diff --stat' output into useful pieces
        git_diff_text = git_diff_text.splitlines()
        if len(git_diff_text) > 1:
            git_local_details = str(git_diff_text[-1:])
            git_changes = git_diff_text[:-1]
            for item in git_changes:
                item = item.split("|")[0]
                changed_files.append(item)
            # fix final line into numbers we can use..
            if " file" in git_local_details:
                num_files_changed = git_local_details.split(" file")[0]
                num_files_changed = num_files_changed.split("' ")[1]
            if "insertions" in git_local_details:
                num_insertions = git_local_details.split("changed, ")[1]
                num_insertions = num_insertions.split(" insertions")[0]
            try:
                if "deletions" in git_local_details:
                    num_deletions = git_local_details.split("(+), ")[1]
                    num_deletions = num_deletions.split(" deletions")[0]
            except:
                print(" !!!  Could not read the git repo's deletetions info, it's not important though")
            display_text = str(num_files_changed) + " Files changed locally,"
        return changed_files, num_files_changed, num_insertions, num_deletions


    def cancel_click(self, e):
        self.Destroy()

    def upgrade_click(self, e):
        # we could also use "git checkout ." before "git pull" if we want to ignore any changes we've made
        # set do_upgrade flag to true, changes to false if git makes it confusing
        do_upgrade = True
        # check to determine best git merge stratergy
        update_type = MainApp.system_ctrl_pannel.check_git()
        if update_type == "clean":
            git_command = "git -C ~/Pigrow/ pull"
        elif update_type == "merge":
            print("WARNING WARNING _ THIS CODE IS VERY MUCH IN THE TESTING PHASE")
            print("if you're doing odd things it's very likely to mess up!")
            #this can cause odd confusions which requires use of 'git rebase'
            #reokace command line question with dialog box
            #question = raw_input("merge using default, ours or theirs?")
            question = "theirs"
            if question == "ours":
                git_command = "git -C ~/Pigrow/ pull --strategy=ours" #if we've changed a file it ignores the remote updated one
            elif question == "theirs":
                #often needs to commit or stash changes before working
                git_command = "git -C ~/Pigrow/ pull -s recursive -X theirs" #removes any changes made locally and replaces file with remote updated one
            elif question == "default":
                git_command = "git -C ~/Pigrow/ pull"
            else:
                print("not an option, calling the whole thing off...")
                do_upgrade = False
        #runs the git pull command using the selected stratergy
        if do_upgrade == True:
            dbox = wx.MessageDialog(self, "Are you sure you want to upgrade this pigrow?", "update pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            #if user said ok then upload file to pi
            if (answer == wx.ID_OK):
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(git_command)
                responce = out.strip()
                print (responce)
                if len(error) > 0:
                    print(('error:' + str(error)))
                    MainApp.system_info_pannel.sys_pigrow_update.SetLabel("--UPDATE ERROR--\n" + error)
                else:
                    MainApp.system_info_pannel.sys_pigrow_update.SetLabel("--UPDATED--")
                self.Destroy()

class install_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(install_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 800))
        self.SetTitle("Install Pigrow")
    def InitUI(self):
        pnl = wx.Panel(self)
        # Header
        header_title = wx.StaticText(self,  label='Install Pigrow')
        header_sub = wx.StaticText(self,  label='Tool for installing pigrow code and dependencies')
        header_title.SetFont(shared_data.title_font)
        header_sub.SetFont(shared_data.sub_title_font)
        # Installed components
        # Core
        label_core = wx.StaticText(self,  label='Core components;')
        label_core.SetFont(shared_data.sub_title_font)
        self.pigrow_base_check = wx.CheckBox(self,  label='Pigrow base')
        self.pigrow_dirlocs_check = wx.CheckBox(self,  label='Locations File')
        self.config_wiz_check = wx.CheckBox(self,  label='Set-up Wizard')
        self.cron_check = wx.CheckBox(self,  label='python crontab')
        # sensors
        label_sensors = wx.StaticText(self,  label='Sensors;')
        label_sensors.SetFont(shared_data.sub_title_font)
        self.adaDHT_check = wx.CheckBox(self,  label='Adafruit_DHT (old py2)')
        self.ada1115_check = wx.CheckBox(self,  label='Adafruit ADS1115')
        # Camera
        label_camera = wx.StaticText(self,  label='Camera;')
        label_camera.SetFont(shared_data.sub_title_font)
        self.uvccapture_check = wx.CheckBox(self,  label='uvccapture')
        # Visualisation
        label_visualisation = wx.StaticText(self,  label='Visualisation;')
        label_visualisation.SetFont(shared_data.sub_title_font)
        self.matplotlib_check = wx.CheckBox(self,  label='Matplotlib py2')
        self.matplotlib3_check = wx.CheckBox(self,  label='Matplotlib py3')
        self.mpv_check = wx.CheckBox(self,  label='mpv')
        # Networking
        label_networking = wx.StaticText(self,  label='Networking;')
        label_networking.SetFont(shared_data.sub_title_font)
        self.praw_check = wx.CheckBox(self,  label='praw')
        self.sshpass_check = wx.CheckBox(self,  label='sshpass')
        self.pexpect_check = wx.CheckBox(self,  label='pexpect')
        #status text
        self.currently_doing_l = wx.StaticText(self,  label="Currently:")
        self.currently_doing = wx.StaticText(self,  label='...')
        self.progress = wx.StaticText(self,  label='...')
        # right hand side - module list
        self.module_list_l = wx.StaticText(self,  label="Install Modules:")
        self.install_module_list = wx.ListCtrl(self, size=(-1,200), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.install_module_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_install_module_opt)
        self.install_module_list.InsertColumn(0, 'Install')
        self.install_module_list.InsertColumn(1, 'Module')
        self.discover_folder_modules()

        #ok and cancel buttons
        self.start_btn = wx.Button(self, label='Start', size=(175, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        # sizers
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer.Add(header_title, 0, wx.ALL, 3)
        header_sizer.Add(header_sub, 0, wx.ALL, 3)
        # left hand side - hardcoded install tools
        base_sizer = wx.BoxSizer(wx.VERTICAL)
        base_sizer.Add(label_core, 0, wx.EXPAND|wx.ALL, 3)
        base_sizer.Add(self.pigrow_base_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.pigrow_dirlocs_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.config_wiz_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.cron_check, 0, wx.EXPAND|wx.LEFT, 30)
        sensor_sizer = wx.BoxSizer(wx.VERTICAL)
        sensor_sizer.Add(label_sensors, 0, wx.EXPAND|wx.ALL, 3)
        sensor_sizer.Add(self.adaDHT_check, 0, wx.EXPAND|wx.LEFT, 30)
        sensor_sizer.Add(self.ada1115_check, 0, wx.EXPAND|wx.LEFT, 30)
        camera_sizer = wx.BoxSizer(wx.VERTICAL)
        camera_sizer.Add(label_camera, 0, wx.EXPAND|wx.ALL, 3)
        camera_sizer.Add(self.uvccapture_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer = wx.BoxSizer(wx.VERTICAL)
        visualisation_sizer.Add(label_visualisation, 0, wx.EXPAND|wx.ALL, 3)
        visualisation_sizer.Add(self.matplotlib_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer.Add(self.matplotlib3_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer.Add(self.mpv_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer = wx.BoxSizer(wx.VERTICAL)
        networking_sizer.Add(label_networking, 0, wx.EXPAND|wx.ALL, 3)
        networking_sizer.Add(self.praw_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.sshpass_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.pexpect_check, 0, wx.EXPAND|wx.LEFT, 30)
        # right hand side - folder modules
        folder_modules_sizer = wx.BoxSizer(wx.VERTICAL)
        folder_modules_sizer.Add(self.module_list_l, 0, wx.EXPAND, 30)
        folder_modules_sizer.Add(self.install_module_list, 0, wx.EXPAND, 30)

        status_text_sizer = wx.BoxSizer(wx.VERTICAL)
        status_text_sizer.Add(self.currently_doing_l, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.currently_doing, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.progress, 0, wx.EXPAND|wx.ALL, 3)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.start_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)

        left_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        left_bar_sizer.Add(base_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(sensor_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(camera_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(visualisation_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(networking_sizer, 0, wx.ALL|wx.EXPAND, 2)
        right_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        right_bar_sizer.Add(folder_modules_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options = wx.BoxSizer(wx.HORIZONTAL)
        middle_options.AddStretchSpacer(1)
        middle_options.Add(left_bar_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options.AddStretchSpacer(1)
        middle_options.Add(right_bar_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options.AddStretchSpacer(1)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(middle_options, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(status_text_sizer, 0, wx.ALL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(main_sizer)





        #run initial checks
        wx.GetApp().Yield() #update screen to show changes

        self.check_for_pigrow_base()
        self.check_dirlocs()
        self.check_config()
        self.check_python_dependencies()
        self.check_python3_dependencies()
        wx.GetApp().Yield() #update screen to show changes
        self.check_program_dependencies()
        self.check_module_dependencies()

    def discover_folder_modules(self):
        # Read sensor modules folder and list install presets
        install_modules_files = os.listdir(shared_data.sensor_modules_path)
        label_text = ""
        self.install_module_list.DeleteAllItems()
        index = 0
        for file in install_modules_files:
            if "_install.txt" in file:
                module = file.split("_install")[0]
                self.install_module_list.InsertItem(index, "False")
                self.install_module_list.SetItem(index, 1, module)
                index = index + 1

    def onDoubleClick_install_module_opt(self, e):
        index =  e.GetIndex()
        to_install = self.install_module_list.GetItem(index, 0).GetText()
        module_name = self.install_module_list.GetItem(index, 1).GetText()
        if to_install == "True":
            self.install_module_list.SetItem(index, 0, "False")
        else:
            self.install_module_list.SetItem(index, 0, "True")

    def check_dirlocs(self):
        print(" Checking for existence and validity of dirlocs.txt")
        dirlocs_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/dirlocs.txt"
        locs_file, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + dirlocs_path)
        if not 'No such file or directory' in locs_file:
            locs_file = locs_file.splitlines()
            for line in locs_file:
                if line[0:5] == "path=":
                    listed_path = line.split("path=")[1]
                    if not listed_path == "/home/" + pi_link_pnl.target_user + "/Pigrow/":
                        print("!!! Error in dirlocs, path does not match current path")
                    else:
                        print("   valid path found in dirlocs.txt", line)
                        self.pigrow_dirlocs_check.SetForegroundColour((75,200,75))
                        return True
        self.pigrow_dirlocs_check.SetForegroundColour((200,75,75))
        self.pigrow_dirlocs_check.SetValue(True)
        return False

    def check_for_pigrow_base(self):
        print("Checking for pigrow code on raspberry pi")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        print(out, error)
        if not len(out.splitlines()) < 1:
            self.pigrow_base_check.SetForegroundColour((75,200,75))
        else:
            self.pigrow_base_check.SetForegroundColour((255,75,75))
            self.pigrow_base_check.SetValue(True)

    def check_config(self):
        print("Checking config file contains box name")
        if not pi_link_pnl.get_box_name() == None:
            self.config_wiz_check.SetForegroundColour((75,200,75))
        else:
            self.config_wiz_check.SetForegroundColour((255,75,75))
            self.config_wiz_check.SetValue(True)

    def config_wizard(self):
        # set box name
        msg = "Select a name for your pigrow."
        msg += "\n\n This will be used to identify your pigrow and to name the local folder in which\n "
        msg += "files from or associated with the pigrow will be stored. \n\n "
        msg += "Ideally choose a simple and descriptive name, like Veg, Flowering, Bedroom, or Greenhouse"
        pi_link_pnl.boxname = "blank"
        MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("e")
        valid_name = False
        while valid_name == False:
            name_box_dbox = wx.TextEntryDialog(self, msg, "Name your Pigrow")
            if name_box_dbox.ShowModal() == wx.ID_OK:
                box_name = name_box_dbox.GetValue()
                if not box_name == "":
                    MainApp.config_ctrl_pannel.config_dict["box_name"] = box_name
                    pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
                    MainApp.pi_link_pnl.link_status_text.SetLabel("linked with - " + box_name)
                    MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")
                    valid_name = True
                else:
                    w_msg = "You must select a name for your pigrow"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
            else:
                print ("User decided not to set the box name")
                valid_name = True
        ## Selflog
        self.add_selflog()
        ## Sensors, Relay devices and triggers
        msg = "Configure Sensors, Relay Devices and Triggers\n\n"
        msg += "To control devices you need to add relay devices and sensors, "
        #msg += "The relays are used to control the power to your devices, they turn on the lights, heater and etc."
        msg += "\n\n options to configure relays and sensors during install will be added here soon, for now add and configure them in the pigrow config tab and sensor tab."
        dbox = wx.MessageDialog(self, msg, "Relay Devices", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("wants to config relays and sensors but that feature isn't written yet")

    def set_control_sensor_to_dht22(self):
        #
        #
        # THIS IS NO LONGER USED - remove when modular sensor system adoption is complete.
        #
        #
        # gpio pin
        msg = "Set DHT22 GPIO pin\n\n"
        msg += "Input the GPIO number of which you connected the DHT22 data pin to."
        valid_gpio = False
        while valid_gpio == False:
            dht22_gpio_dbox = wx.TextEntryDialog(self, msg, "DHT22 GPIO")
            if dht22_gpio_dbox.ShowModal() == wx.ID_OK:
                DHT22_GPIO = dht22_gpio_dbox.GetValue()
                if not DHT22_GPIO== "" and DHT22_GPIO.isdigit() == True:
                    MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"] = DHT22_GPIO
                    valid_gpio = True
                else:
                    w_msg = "You must select a valid GPIO number"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
                    if not (answer == wx.ID_OK):
                        print("User cancelled dht22 set up")
                        return "cancelled"
        # log frequency
        msg = "Set log frequency\n\n"
        msg += "Select how frequently to log the dht22 temp and humid data, this also determines how"
        msg += "frequently it will check temperature and humidity values to decide when to turn on and"
        msg += "turn off devices.\n\n"
        msg += "A value between 60 seconds and 1800 seconds (half an hour) is ideal."
        valid_freq = False
        while valid_freq == False:
            dht22_freq_dbox = wx.TextEntryDialog(self, msg, "DHT22 Logging Frequency")
            if dht22_freq_dbox.ShowModal() == wx.ID_OK:
                DHT22_freq = dht22_freq_dbox.GetValue()
                if not DHT22_freq== "" and DHT22_freq.isdigit() == True:
                    MainApp.config_ctrl_pannel.gpio_dict["log_frequency"] = DHT22_freq
                    valid_freq = True
                else:
                    w_msg = "You must input a time in seconds for how often you want to read the control sensor."
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
                    if not (answer == wx.ID_OK):
                        print("User cancelled dht22 set up")
                        return "cancelled"
        # test dht22 and ask user if they want to add to cron
        args = "gpio=" + DHT22_GPIO + " sensor=dht22"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/build_test/test_dht.py " + args)
        out = out.strip()
        if "temp" in out:
            out = out.split(" ")
            temp = out[0].split("=")[1]
            humid = out[1].split("=")[1]
        elif "failed" in out:
            temp = "failed"
            humid = "failed"
        else:
            temp = "error"
            humid = "error"
        msg = "Control sensor set to dht22 on GPIO pin " + DHT22_GPIO + " reading every " + DHT22_freq + " seconds.\n\n"
        msg += " Sensor readings\n            Temp: " + temp + "\n            Humid: " + humid + "\n\n"
        msg += "You can change these settings and configure switching behaviour in the config dht dialog box found in the Pigrow Setup tab.\n\n"
        cron_dht_exists, cron_dht_enabled, cron_dht_index = self.check_for_control_script(scriptname="checkDHT.py")
        if cron_dht_exists == False:
            msg += "To enable the sensor's logging and device switching the script checkDHT.py must be running on the pigrow, this is called at "
            msg += "start-up by Cron the pi's task scheduling tool."
            msg += "\n\n, Press ok to add checkDHT.py to crons startup list, or cancel to skip this step."
        else:
            msg += "checkDHT.py is already in the start up cron list, possibly from a prior install. "
            if cron_dht_enabled == False:
                msg += " But is currently disabled."
            msg +=  "\n\n Press ok to remove all instances of checkDHT.py from the cron startup list and add it again, "
            msg += "or press cancel to skip this step."
        dbox = wx.MessageDialog(self, msg, "Control Sensor Config", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("Cleaning cron of old checkdht22.py calls...")
            while cron_dht_exists:
                print("Removing " + str(cron_dht_index))
                cron_list_pnl.startup_cron.DeleteItem(cron_dht_index)
                cron_dht_exists, cron_dht_enabled, cron_dht_index = self.check_for_control_script(scriptname="checkDHT.py")
            print("Adding a new checkDHT.py script to cron")
            checkDHT_path = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/scripts/autorun/checkDHT.py"
            cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', "True", checkDHT_path, "", "")
            MainApp.cron_info_pannel.update_cron_click("e")
        # save settings
        MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

    def set_temp_and_humid_ranges(self):
        # Low Temp
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "The control sensor is used to turn on and off climate control devices, at the moment \n"
        msg += "the only option is simple switching which uses threashold values to determine if devices should\n"
        msg += "be turned on or off, but again other options will be added as the pigrow continues to grow.\n"
        msg += "\n All Temperatures are in C, I'll add the option of using american units soon."
        msg += "\n\n Set the low temp, if it falls below this temperature the heater will turn on. "
        valid_temp = False
        while valid_temp == False:
            lowtemp_dbox = wx.TextEntryDialog(self, msg, "Set Low Temp in degrees C", "15")
            if lowtemp_dbox.ShowModal() == wx.ID_OK:
                lowtemp = lowtemp_dbox.GetValue()
                if lowtemp.isdigit():
                    print("Valid Low Temp of - ", lowtemp)
                    valid_temp = True
                else:
                    w_msg = "You must select a temperature in C"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # Low Temp
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "All Temperatures are in C, I'll add the option of using american units soon."
        msg += "\n\n Set the High temp, if it rises above this temperature the cooling system will engage.\n\n"
        msg += "This is generally an extra fan which sucks air out the top of your growspace but can \n"
        msg += "also be an air chiller, an inlet letting colder outside air in or similar."
        valid_temp = False
        while valid_temp == False:
            hightemp_dbox = wx.TextEntryDialog(self, msg, "Set High Temp in degrees C", "25")
            if hightemp_dbox.ShowModal() == wx.ID_OK:
                hightemp = hightemp_dbox.GetValue()
                if hightemp.isdigit():
                    print("Valid High Temp of - ", hightemp)
                    valid_temp = True
                else:
                    w_msg = "You must select a temperature in C"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # low humidity
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "Relative Humidity is measured as a percentage\n\n"
        msg += "Set the Low Humidity threashold, if the humidity falls bellow this point it will\n"
        msg += "turn on the humidifier until the humidity rises above this point again. \n"
        valid_humid = False
        while valid_humid == False:
            lowhum_dbox = wx.TextEntryDialog(self, msg, "Set Low Humidity", "35")
            if lowhum_dbox.ShowModal() == wx.ID_OK:
                lowhum = lowhum_dbox.GetValue()
                lowhum = lowhum.replace("%", "")
                if lowhum.isdigit():
                    print("Valid Low Humidity of - ", lowhum)
                    valid_humid = True
                else:
                    w_msg = "You must input a number for the low humidity value"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # high humidity
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "Relative Humidity is measured as a percentage\n\n"
        msg += "Set the High Humidity threashold, if the humidity rises above this point it will\n"
        msg += "turn on the dehumidifier until the humidity falls below this point again. \n"
        valid_humid = False
        while valid_humid == False:
            highhum_dbox = wx.TextEntryDialog(self, msg, "Set High Humidity", "70")
            if highhum_dbox.ShowModal() == wx.ID_OK:
                highhum = highhum_dbox.GetValue()
                highhum = highhum.replace("%", "")
                if highhum.isdigit():
                    print("Valid High Humidity of - ", highhum)
                    valid_humid = True
                else:
                    w_msg = "You must input a number for the high humidity value"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        print("Completed threashold set-up, saving to pi")
        MainApp.config_ctrl_pannel.config_dict["heater_templow"] = lowtemp
        MainApp.config_ctrl_pannel.config_dict["heater_temphigh"] = hightemp
        MainApp.config_ctrl_pannel.config_dict["humid_low"] = lowhum
        MainApp.config_ctrl_pannel.config_dict["humid_high"] = highhum
        MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

    def check_for_control_script(self, scriptname):
        last_index = cron_list_pnl.startup_cron.GetItemCount()
        script_has_cronjob_already = False
        script_enabled = False
        script_startupcron_index = None
        if not last_index == 0:
            for index in range(0, last_index):
                name = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
                if scriptname in name:
                    script_enabled = cron_list_pnl.startup_cron.GetItem(index, 1).GetText()
                    script_startupcron_index = index
                    script_has_cronjob_already = True
        return script_has_cronjob_already, script_enabled, script_startupcron_index

    def add_selflog(self):
        msg = "Enable Selflog\n\n"
        msg += "The selflog is a simple python script which is called periodically by cron to log various system \n"
        msg += "conditions including the Raspberry Pi's cpu temperature, it's available memory and disk space."
        msg += "\n\n"
        msg += "These logs can be downloaded and graphed using presets found in the local graphing tools."
        cron_selflog_exists, cron_selflog_enabled, cron_selflog_index = self.check_for_selflog_script()
        if cron_selflog_exists == False:
            msg += "\n\n, Press ok to add selflog.py to cron repeating every fifteen min, or cancel to skip this step."
        else:
            msg += "\n\nselflog.py is already in cron's repeating list, possibly from a prior install. "
            if cron_selflog_enabled == False:
                msg += " But is currently disabled."
            msg +=  "\n\n Press ok to remove all instances of selflog.py from the cron repeating list and add it again, "
            msg += "or press cancel to skip this step."
        dbox = wx.MessageDialog(self, msg, "Self Log Config", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("Cleaning cron of old selflog.py calls...")
            while cron_selflog_exists:
                print("Removing " + str(cron_selflog_index))
                cron_list_pnl.repeat_cron.DeleteItem(cron_selflog_index)
                cron_selflog_exists, cron_selflog_enabled, cron_selflog_index = self.check_for_selflog_script()
            print("Adding a new selflog.py script to cron")
            selflog_path = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/scripts/cron/selflog.py"
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', "True", "*/15 * * * *", selflog_path, "", "")
            MainApp.cron_info_pannel.update_cron_click("e")

    def check_for_selflog_script(self):
        last_index = cron_list_pnl.repeat_cron.GetItemCount()
        has_cron_got_selflog_already = False
        selflog_enabled = False
        selflog_index = None
        if not last_index == 0:
            for index in range(0, last_index):
                name = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                if "selflog.py" in name:
                    selflog_enabled = cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()
                    selflog_index = index
                    has_cron_got_selflog_already = True
        return has_cron_got_selflog_already, selflog_enabled, selflog_index

    def install_pigrow(self):
        print(" Cloning git repo onto pi")
        # download pigrow scripts from git
        self.currently_doing.SetLabel("using git to clone (download) pigrow code")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
        print(out, error)
        self.progress_install_bar()

        # create empty folders
        self.currently_doing.SetLabel("creating empty folders")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/caps/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/graphs/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/logs/")
        self.progress_install_bar()

    def create_dirlocs_from_template(self):
        print("Creting dirlocs.txt from template")
        self.currently_doing.SetLabel("Creating dirlocs from template")
        # grab template from pi and swap wildcards for username
        dirlocs_template, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat ~/Pigrow/config/templates/dirlocs_temp.txt")
        dirlocs_text = dirlocs_template.replace("**", str("/home/" + pi_link_pnl.target_user))
        # Create a local version of dirloc.txt to upload onto pi
        if localfiles_info_pnl.local_path == "":
            localfiles_info_pnl.local_path = os.path.join(MainApp.localfiles_path, str(pi_link_pnl.boxname))
        local_temp_path = os.path.join(localfiles_info_pnl.local_path, "temp")
        local_temp_dirlocs_path =  os.path.join(local_temp_path, "dirlocs.txt")
        #print(local_temp_path)
        #print(local_temp_dirlocs_path)
        if not os.path.isdir(local_temp_path):
            os.makedirs(local_temp_path)
        with open(local_temp_dirlocs_path, "w") as temp_local:
            temp_local.write(dirlocs_text)
        MainApp.localfiles_ctrl_pannel.upload_file_to_folder(local_temp_dirlocs_path, "/home/" + pi_link_pnl.target_user + "/Pigrow/config/dirlocs.txt")
        self.progress_install_bar()
        print(" - uploaded new dirlocs to pigrow config folder")

    def update_pip(self):
        # update pip the python package manager
        print(" - updating pip2")
        self.currently_doing.SetLabel("Updating PIP2 the python2 install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        print(" - install running command; sudo pip2 install -U pip")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip2 install -U pip")
        print (out)

    def install_pip2_package(self, pip2_package):
        pip2_command = "sudo pip2 install " + pip2_package
        self.currently_doing.SetLabel("Using pip2 to install " + pip2_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip2_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(pip2_command)
        print("   -- Finished " + pip2_package + " install attempt;")
        print (out, error)

    def update_pip2_package(self, pip2_package):
        # this is not yet used
        pip2_command = "sudo pip2 install -U"
        self.currently_doing.SetLabel("Upgrading pip2 package " + pip2_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip2_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(pip2_command)
        print("   -- Finished " + pip2_package + " upgrade attempt;")
        print (out, error)

    def update_pip3(self):
        # update pip the python package manager
        print(" - updating pip3")
        self.currently_doing.SetLabel("Updating PIP3 the python3 install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        print(" - install running command; sudo pip3 install -U pip")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install -U pip")
        print (out)

    def install_pip3_package(self, pip3_package):
        pip3_command = "sudo pip3 install " + pip3_package
        self.currently_doing.SetLabel("Using pip3 to install " + pip3_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip3_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(pip3_command)
        print("   -- Finished " + pip3_package + " install attempt;")
        print (out, error)

    def update_pip3_package(self, pip3_package):
        # this is not yet used
        pip3_command = "sudo pip3 install -U"
        self.currently_doing.SetLabel("Upgrading pip3 package " + pip3_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip3_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(pip3_command)
        print("   -- Finished " + pip3_package + " upgrade attempt;")
        print (out, error)

    #def install_praw(self):
        # praw is the module for connecting to reddit
        self.currently_doing.SetLabel("Using pip3 to install praw")
        self.progress.SetLabel("###########~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install praw")
        print (out)

    #def install_matplotlib3(self):
        # Matplotlib makes the graphs for us
        self.currently_doing.SetLabel("Using pip3 to install matplotlib")
        self.progress.SetLabel("###############~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install matplotlib")
        print (out)

    #def install_pexpect(self):
        # pexpect is the tool used to connect to other pigrows if using pigrow log
        self.currently_doing.SetLabel("using pip to install pexpect")
        self.progress.SetLabel("#############~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install pexpect")
        print (out)

    #def install_adafruit_DHT(self):
        print("starting adafruit install")
        self.progress.SetLabel("###############~~~~~~~~~~~~~~")
        self.currently_doing.SetLabel("Using pip to install adafruit_DHT module")
        wx.GetApp().Yield()
        adafruit_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install Adafruit_DHT")
        print (adafruit_install)

    #def install_adafruit_ads1115(self):
        print("starting adafruit install")
        self.progress.SetLabel("################~~~~~~~~~~~~~")
        self.currently_doing.SetLabel("Using pip3 to install adafruit's ADS1x15 driver")
        wx.GetApp().Yield()
        print(" - installing RPI-GPIO module")
        GPIO_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install RPI.GPIO")
        print (GPIO_install)
        print("-----")
        print(error)
        print(" - installing adafruit blinka module")
        blinka_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install adafruit-blinka")
        print (blinka_install)
        print("-----")
        print(error)
        print(" - installing adafruit ads1x15 module")
        ads1115_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install adafruit-circuitpython-ads1x15")
        print (ads1115_install)
        print("-----")
        print(error)

    def update_apt(self):
        print(" - updating apt")
        self.currently_doing.SetLabel("updating apt the system package manager on the raspberry pi")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get update --yes")
        print (out, error)

    #def install_uvccaptre(self):
        self.currently_doing.SetLabel("Using apt to install uvccaptre")
        self.progress.SetLabel("####################~~~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install uvccapture")
        print (out, error)

    #def install_mpv(self):
        self.currently_doing.SetLabel("Using apt to install mpv")
        self.progress.SetLabel("#####################~~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install mpv")
        print (out, error)

    #def install_python_matplotlib(self):
        self.currently_doing.SetLabel("Using apt to install python-matplotlib")
        self.progress.SetLabel("######################~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install python-matplotlib")
        print (out, error)

    #def install_sshpass(self):
        self.currently_doing.SetLabel("Using apt to install sshpass")
        self.progress.SetLabel("#######################~~~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install sshpass")
        print (out, error)

    #def install_python_crontab(self):
        self.currently_doing.SetLabel("Using apt to install python-crontab")
        self.progress.SetLabel("########################~~~~~~~")
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install python-crontab")
        print (out, error)

    def install_apt_package(self, apt_package):
        apt_command= "sudo apt-get --yes install " + apt_package
        self.currently_doing.SetLabel("Using apt to install " + apt_package)
        wx.GetApp().Yield()
        print(" - install running command; " + apt_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(apt_command)
        print("   -- Finished " + apt_package + " install attempt;")
        print (out, error)

    def install_wget_package(self, package_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_file_name = os.path.split(package_name)[1]
        install_p = sensor_module_folder + install_file_name
        self.currently_doing.SetLabel("Using wget to download " + package_name)
        command = "wget " + package_name + " -O " + install_p
        print(" - install running command; " + command)
        wx.GetApp().Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(command)
        print("   -- Finished " + package_name + " install attempt;")
        print(out, error)

    def check_module_dependencies(self):
        print(" Testing dependencies from install module files")
        for module_index in range(0, self.install_module_list.GetItemCount()):
            module_name = self.install_module_list.GetItem(module_index, 1).GetText()
            module_name = module_name + "_install.txt"
            install_module_path = os.path.join(shared_data.sensor_modules_path, module_name)
            with open(install_module_path, "r") as install_text:
                install_module_file = install_text.read().splitlines()
            install_method = ""
            package_name = ""
            import_name = ""
            for line in install_module_file:
                if "install_method=" in line:
                    install_method = line.split("=")[1]
                elif "package_name=" in line:
                    package_name =  line.split("=")[1]
                elif "import=" in line:
                    import_name =  line.split("=")[1]
            is_installed = False
            if not install_method == "" and not package_name == "":
                if install_method == "pip2":
                    if "True" in self.test_py_module(package_name):
                        is_installed = True
                elif install_method == 'pip3':
                    if not import_name == "":
                        if "True" in self.test_py3_module(import_name):
                            is_installed = True
                    else:
                        if "True" in self.test_py3_module(package_name):
                            is_installed = True
                elif install_method == "apt":
                    is_installed = self.test_apt_package(package_name)
                elif install_method == "wget":
                    is_installed = self.test_wget_file(package_name)

            if is_installed == True:
                self.install_module_list.SetItemTextColour(module_index, wx.Colour(90,180,90))
                print(" -- " + package_name + " is already installed")
            else:
                self.install_module_list.SetItemTextColour(module_index, wx.RED)
                print(" -- " + package_name + " is not installed")


    def test_apt_package(self, package_name):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("apt-cache policy " + package_name + " |grep Installed")
        if "Installed" in out:
            if not "(none)" in out:
                return True
            else:
                return False
        else:
            return False

    def test_wget_file(self, package_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_file_name = os.path.split(package_name)[1]
        install_p = sensor_module_folder + install_file_name
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls " + install_p)
        if install_p == out.strip():
            return True
        else:
            return False

    def check_program_dependencies(self):
        program_dependencies = ["sshpass", "uvccapture", "mpv"]
        working_programs = []
        nonworking_programs = []
        for program in program_dependencies:
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("apt-cache policy "+program+" |grep Installed")
            if "Installed" in out:
                if not "(none)" in out:
                    working_programs.append(program)
                else:
                    nonworking_programs.append(program)
            else:
                nonworking_programs.append(program)
        #colour ui
        if "uvccapture" in working_programs:
            self.uvccapture_check.SetForegroundColour((75,200,75))
        else:
            self.uvccapture_check.SetForegroundColour((255,75,75))
            self.uvccapture_check.SetValue(True)
        if "mpv" in working_programs:
            self.mpv_check.SetForegroundColour((75,200,75))
        else:
            self.mpv_check.SetForegroundColour((255,75,75))
            self.mpv_check.SetValue(True)
        if "sshpass" in working_programs:
            self.sshpass_check.SetForegroundColour((75,200,75))
        else:
            self.sshpass_check.SetForegroundColour((255,75,75))
            self.sshpass_check.SetValue(True)

    def check_python3_dependencies(self):
        # Dependencies for ADS1115
        ads1115_working = True
        if "True" in self.test_py3_module("board"):
            print("Adafruit board module installed")
        else:
            ads1115_working = False
            print("Adafruit board module is NOT installed - this is required for the ads1115")
        if "True" in self.test_py3_module("busio"):
            print("Adafruit busio module installed")
        else:
            ads1115_working = False
            print("Adafruit board module is NOT installed - this is required for the ads1115")
        if "True" in self.test_py3_module("adafruit_ads1x15"):
            print("Adafruit ADS1x15 module installed")
        else:
            ads1115_working = False
            print("Adafruit ads1x15 module is NOT installed - this is required for the ads1115")
        if ads1115_working == True:
            self.ada1115_check.SetForegroundColour((75,200,75))
        else:
            self.ada1115_check.SetForegroundColour((255,75,75))
            self.ada1115_check.SetValue(True)
        # Praw - the reddit bot module
        if "True" in self.test_py3_module("praw"):
            self.praw_check.SetForegroundColour((75,200,75))
        else:
            self.praw_check.SetForegroundColour((255,75,75))
            self.praw_check.SetValue(True)
        # matplotlib
        if "True" in self.test_py3_module("matplotlib"):
            self.matplotlib3_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib3_check.SetForegroundColour((255,75,75))
            self.matplotlib3_check.SetValue(True)

    def check_python_dependencies(self):
        python_dependencies = ["matplotlib", "Adafruit_DHT", "pexpect", "crontab"]
        working_modules = []
        nonworking_modules = []
        for module in python_dependencies:
            #print module
            out = self.test_py_module(module)
            if "True" in out:
                working_modules.append(module)
            else:
                nonworking_modules.append(module)
        MainApp.status.write_bar("")
        # colour UI
        if "matplotlib" in working_modules:
            self.matplotlib_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib_check.SetForegroundColour((255,75,75))
            self.matplotlib_check.SetValue(True)
        wx.GetApp().Yield()
        if "Adafruit_DHT" in working_modules:
            self.adaDHT_check.SetForegroundColour((75,200,75))
        else:
            self.adaDHT_check.SetForegroundColour((255,75,75))
            self.adaDHT_check.SetValue(True)
        if "crontab" in working_modules:
            self.cron_check.SetForegroundColour((75,200,75))
        else:
            self.cron_check.SetForegroundColour((255,75,75))
            self.cron_check.SetValue(True)
        if "pexpect" in working_modules:
            self.pexpect_check.SetForegroundColour((75,200,75))
        else:
            self.pexpect_check.SetForegroundColour((255,75,75))
            self.pexpect_check.SetValue(True)

    def progress_install_bar(self):
        current_label = self.progress.GetLabel()
        extra_hashes = "#" * self.hash_per_item
        pos = current_label.find("~")
        hashes = current_label[:pos]
        tilda = current_label[pos:]
        if len(tilda) > self.hash_per_item:
            tilda = tilda[:-self.hash_per_item]
        else:
            tilda = ""
        hashes = hashes + extra_hashes
        print (current_label, extra_hashes, pos, hashes, tilda)
        self.progress.SetLabel(hashes + tilda)
        #self.currently_doing.SetLabel("-")
        wx.GetApp().Yield()

    def start_click(self, e):
        print("(Upgraded) Install process started;")
        self.progress.SetLabel("#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()


        # hardcoded controlls -
        #                     -  Remove this when these are added to generated list control
        # installed using pip2
        pip2_package_list = []
        if self.pexpect_check.GetValue() == True:
            pip2_package_list.append('pexpect')
        if self.adaDHT_check.GetValue() == True:
            pip2_package_list.append('Adafruit_DHT')

        # installed using pip3
        pip3_package_list = []
        if self.ada1115_check.GetValue() == True:
            #self.install_adafruit_ads1115()
            #pip3_package_list.append('RPI.GPIO')
            #pip3_package_list.append('adafruit-blinka')
            pip3_package_list.append('adafruit-circuitpython-ads1x15')
        if self.praw_check.GetValue() == True:
            #self.install_praw()
            pip3_package_list.append('praw')
        if self.matplotlib3_check.GetValue() == True:
            #self.install_matplotlib3()
            pip3_package_list.append('matplotlib')

        # Dependencies installed using apt
        apt_package_list = []
        if self.uvccapture_check.GetValue() == True:
            #self.install_uvccaptre()
            apt_package_list.append('uvccapture')
        if self.mpv_check.GetValue() == True:
            #self.install_mpv()
            apt_package_list.append('mpv')
        if self.sshpass_check.GetValue() == True:
            #self.install_sshpass()
            apt_package_list.append('sshpass')
        if self.matplotlib_check.GetValue() == True:
            #self.install_python_matplotlib()
            apt_package_list.append('python-matplotlib')
        if self.cron_check.GetValue() == True:
            #self.install_python_crontab()
            apt_package_list.append('python-crontab')
        # Add modular sensors to list from table
        wget_package_list = []
        for module_index in range(0, self.install_module_list.GetItemCount()):
            if self.install_module_list.GetItem(module_index, 0).GetText() == "True":
                module_name = self.install_module_list.GetItem(module_index, 1).GetText()
                module_name = module_name + "_install.txt"
                install_module_path = os.path.join(shared_data.sensor_modules_path, module_name)
                with open(install_module_path, "r") as install_text:
                    install_module_file = install_text.read().splitlines()
                for line in install_module_file:
                    if "install_method=" in line:
                        install_method = line.split("=")[1]
                    if "package_name=" in line:
                        package_name =  line.split("=")[1]
                if not install_method == "" and not package_name == "":
                    if install_method == "pip2":
                        pip2_package_list.append(package_name)
                    elif install_method == 'pip3':
                        pip3_package_list.append(package_name)
                    elif install_method == "apt":
                        apt_package_list.append(package_name)
                    elif install_method == "wget":
                        wget_package_list.append(package_name)


        # counting items for progress bar
        item_count = len(pip3_package_list) + len(pip3_package_list) + len(apt_package_list) + len(wget_package_list)
        if self.pigrow_base_check.GetValue() == True:
            item_count += 1
        if self.pigrow_dirlocs_check.GetValue() == True:
            item_count += 1
        if self.config_wiz_check.GetValue() == True:
            item_count += 1
        total_spaces =  30
        if item_count == 0:
            item_count = 1
        self.hash_per_item = int(total_spaces / item_count)

        # Base installed via Git Clone
        if self.pigrow_base_check.GetValue() == True:
            self.install_pigrow()
            self.progress_install_bar()
        # make dirlocs with pi's username
        if self.pigrow_dirlocs_check.GetValue() == True:
            self.create_dirlocs_from_template()
            self.progress_install_bar()
        # Install packages
        # Cycle through list install all pip2 packages
        if len(pip2_package_list) > 0:
            self.update_pip()
            for pip2_package in pip2_package_list:
                self.install_pip2_package(pip2_package)
                self.progress_install_bar()
        # cycle through and install all pip3 packages
        if len(pip3_package_list) > 0:
            self.update_pip3()
            for pip3_package in pip3_package_list:
                self.install_pip3_package(pip3_package)
                self.progress_install_bar()
        # cycle through all and install all apt packages
        if len(apt_package_list) > 0:
            self.update_apt()
            for apt_package in apt_package_list:
                self.install_apt_package(apt_package)
                self.progress_install_bar()
        # download all files using wget
        for wget_package in wget_package_list:
            self.install_wget_package(wget_package)
            self.progress_install_bar()
        # run the setup wizard
        if self.config_wiz_check.GetValue() == True:
            self.currently_doing.SetLabel(" Config Wizard")
            self.progress.SetLabel("##############################~")
            wx.GetApp().Yield()
            self.config_wizard()

        # Announce finished
        print("(Upgraded) Install process finished;")
        self.progress.SetLabel("####### INSTALL COMPLETE ######")
        self.currently_doing.SetLabel(" -- ")
        self.start_btn.Disable()
        self.cancel_btn.SetLabel("OK")
        wx.GetApp().Yield()


    def cancel_click(self, e):
        self.Destroy()

    def test_py_module(self, module):
        msg = "  - Testing; " + module
        MainApp.status.write_bar(msg)
        print(msg)
        module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python -c " + module_question)
        return out

    def test_py3_module(self, module):
        module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python3 -c " + module_question)
        return out


#
#
#
### pigrow Config pannel
#
#
class config_ctrl_pnl(wx.Panel):
    #this controlls the data displayed on config_info_pnl
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        self.config_l = wx.StaticText(self,  label='Pigrow Config')
        self.relay_l = wx.StaticText(self,  label='Relay')
        self.dht_l = wx.StaticText(self,  label='DHT Sensor')
        self.name_box_btn = wx.Button(self, label='change box name')
        self.name_box_btn.Bind(wx.EVT_BUTTON, self.name_box_click)
        self.config_lamp_btn = wx.Button(self, label='config lamp')
        self.config_lamp_btn.Bind(wx.EVT_BUTTON, self.config_lamp_click)
        self.config_water_btn = wx.Button(self, label='config watering')
        self.config_water_btn.Bind(wx.EVT_BUTTON, self.config_water_click)
        self.config_dht_btn = wx.Button(self, label='config dht')
        self.config_dht_btn.Bind(wx.EVT_BUTTON, self.config_dht_click)
        self.new_gpio_btn = wx.Button(self, label='Add new relay device')
        self.new_gpio_btn.Bind(wx.EVT_BUTTON, self.add_new_device_relay)
        self.update_config_btn = wx.Button(self, label='read config from pigrow')
        self.update_config_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_setup_pannel_information_click)
        self.update_settings_btn = wx.Button(self, label='update pigrow settings')
        self.update_settings_btn.Bind(wx.EVT_BUTTON, self.update_setting_file_on_pi_click)
        #sizers
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.config_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_config_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_settings_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.name_box_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.dht_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.config_dht_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.relay_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.config_lamp_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.config_water_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.new_gpio_btn , 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)




    def name_box_click(self, e):
        box_name = config_info_pnl.boxname_text.GetValue()
        if not box_name == MainApp.config_ctrl_pannel.config_dict["box_name"]:
            MainApp.config_ctrl_pannel.config_dict["box_name"] = box_name
            pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
            MainApp.pi_link_pnl.link_status_text.SetLabel("linked with - " + box_name)
            self.update_setting_file_on_pi_click("e")
        else:
            print("no change")

    def update_pigrow_setup_pannel_information_click(self, e):
        print("reading pigrow and updating local config info")
        # clear dictionaries and tables
        self.dirlocs_dict = {}
        self.config_dict = {}
        self.gpio_dict = {}
        self.gpio_on_dict = {}
        MainApp.config_info_pannel.gpio_table.DeleteAllItems()
        # define file locations
        pigrow_config_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/"
        pigrow_dirlocs = pigrow_config_folder + "dirlocs.txt"
        #read pigrow locations file
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_dirlocs)
        dirlocs = out.splitlines()
        if len(dirlocs) > 1:
            for item in dirlocs:
                try:
                    item = item.split("=")
                    #self.dirlocs_dict = {item[0]:item[1]}
                    self.dirlocs_dict[item[0]] = item[1]
                except:
                    print(("!!error reading value from dirlocs; " + str(item)))
        else:
            print("Error; dirlocs contains no information")
            dbox = wx.MessageDialog(self, "The dirlocs file contains no information, do you want to create a new one?", "Create new dirlocs?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                print("creating new dirlocs")
                install_dialog.create_dirlocs_from_template(self)


        #We've now created self.dirlocs_dict with key:value for every setting:value in dirlocs
        #now we grab some of the important ones from the dictionary
        #folder location info (having this in a file on the pi makes it easier if doing things odd ways)
        location_msg = ""
        location_problems = []
        try:
            pigrow_path = self.dirlocs_dict['path']
        #    location_msg += pigrow_path + "\n"
        except:
            location_msg += ("No path locaion info in pigrow dirlocs\n")
            pigrow_path = ""
            location_problems.append("path")
        try:
            pigrow_logs_path = self.dirlocs_dict['log_path']
        #    location_msg += pigrow_logs_path + "\n"
        except:
            location_msg += ("No logs locaion info in pigrow dirlocs\n")
            pigrow_logs_path = ""
            location_problems.append("log_path")
        try:
            pigrow_graph_path = self.dirlocs_dict['graph_path']
        #    location_msg += pigrow_graph_path + "\n"
        except:
            location_msg += ("No graph locaion info in pigrow dirlocs\n")
            pigrow_graph_path = ""
            location_problems.append("graph_path")
        try:
            pigrow_caps_path = self.dirlocs_dict['caps_path']
        #    location_msg += pigrow_caps_path + "\n"
        except:
            location_msg += ("No caps locaion info in pigrow dirlocs\n")
            pigrow_caps_path = ""
            location_problems.append("caps_path")

         #settings file locations
        try:
            pigrow_settings_path = self.dirlocs_dict['loc_settings']
        except:
            location_msg += ("No pigrow config file locaion info in pigrow dirlocs\n")
            pigrow_settings_path = ""
            location_problems.append("loc_settings")
        try:
            pigrow_cam_settings_path = self.dirlocs_dict['camera_settings']
        except:
            location_msg +=("no camera settings file locaion info in pigrow dirlocs (optional)\n")
            pigrow_cam_settings_path = ""

         # log file locations
        try:
            pigrow_err_log_path = self.dirlocs_dict['err_log']
        except:
            location_msg += ("No err log locaion info in pigrow dirlocs\n")
            pigrow_err_log_path = ""
            location_problems.append("err_log")
        try:
            pigrow_self_log_path = self.dirlocs_dict['self_log']
        except:
            location_msg += ("No self_log locaion info in pigrow dirlocs (optional)\n")
            pigrow_self_log_path = ""
        try:
            pigrow_switchlog_path = self.dirlocs_dict['loc_switchlog']
        except:
            location_msg += "No switchlog locaion info in pigrow dirlocs (optional)\n"
            pigrow_switchlog_path = ""
        #check to see if there were problems and tell the user.
        if len(location_problems) == 0:
            location_msg += ("All vital locations present")
        else:
            location_msg += "Important location information missing! " + str(location_problems) + " not found"
        #display on screen
        config_info_pnl.location_text.SetLabel(location_msg)
        #
        #read pigrow config file
        #
        if not pigrow_settings_path == "":
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_settings_path)
            pigrow_settings = out.splitlines()
        else:
            pigrow_settings = []
        #go through the setting file and put them in the correct dictionary
        if len(pigrow_settings) > 1:
            for item in pigrow_settings:
                try:
                    equals_pos = item.find("=")
                    setting_value  = item[equals_pos + 1:]
                    setting_name = item[:equals_pos]
                    print(setting_name, setting_value)

                    line_split = setting_name.split("_")
                    if line_split[0] == 'gpio' and not setting_value == "":
                        if len(line_split) == 2:
                            self.gpio_dict[line_split[1]] = setting_value
                        elif len(line_split) == 3:
                            self.gpio_on_dict[str(line_split[1])] = setting_value
                    else:
                        if not setting_value == "":
                            self.config_dict[setting_name] = setting_value
                except:
                    print(("!!error reading value from config file; " + str(item)))
        # we've now created self.config_dict with a list of all the items in the config file
        #   and self.gpio_dict and self.gpio_on_dict with gpio numbers and low/high pin direction info


        #unpack non-gpio information from config file
        config_problems = []
        config_msg = ''
        lamp_msg = ''
        dht_msg = ''
        #lamp timeing
        if "lamp" in self.gpio_dict:
            if "time_lamp_on" in self.config_dict:
                lamp_on_hour = int(self.config_dict["time_lamp_on"].split(":")[0])
                lamp_on_min = int(self.config_dict["time_lamp_on"].split(":")[1])

            else:
                lamp_msg += "lamp on time not set "
                config_problems.append('lamp')
            if "time_lamp_off" in self.config_dict:
                lamp_off_hour = int(self.config_dict["time_lamp_off"].split(":")[0])
                lamp_off_min = int(self.config_dict["time_lamp_off"].split(":")[1])
            else:
                lamp_msg += "lamp off time not set\n"
                config_problems.append('lamp')
            #convert to datetime objects and add a day to the off time so that it's
            #   working out the time on gap correctly (i.e. avoid reporting negative time)
            if not 'lamp' in config_problems:
                on_time = datetime.time(int(lamp_on_hour),int(lamp_on_min))
                off_time = datetime.time(int(lamp_off_hour), int(lamp_off_min))
                aday = datetime.timedelta(days=1)
                if on_time > off_time:
                    dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + aday))
                else:
                    dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))
                length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))
                lamp_msg += "Lamp turning on at " + str(on_time)[:-3] + " and off at " + str(off_time)[:-3]
                lamp_msg += " (" + str(length_lamp_on)[:-3] + " on, "  +str(aday - length_lamp_on)[:-3] + " off)\n"

            # checking lamp timings in cron
            on_cron = self.get_cron_time("lamp_on.py")
            off_cron = self.get_cron_time("lamp_off.py")
            if on_cron != "not found" and off_cron != "not found":
                if on_cron != "runs more than once" and off_cron != "runs more than once":
                    on_cron = datetime.time(int(on_cron.split(" ")[1]), int(on_cron.split(" ")[0]))
                    off_cron = datetime.time(int(off_cron.split(" ")[1]), int(off_cron.split(" ")[0]))
                    if on_cron == on_time and off_cron == off_time:
                        lamp_msg += "Lamp synced with cron"
                    else:
                        lamp_msg += "Warning - lamp not synced with cron."
                else:
                    lamp_msg += "Warning - lamp switching more than once a day"
            else:
                lamp_msg += "Warning - cron switching not configured"
                #on_cron_converted = []
        else:
            lamp_msg += "no lamp linked to gpio, ignoring lamp timing settings"
     #heater on and off temps
        if "heater" in self.gpio_dict:
            dht_msg += "heater enabled, "
        else:
            dht_msg += "no heater gpio, "
        # low
        if "heater_templow" in self.config_dict:
            self.heater_templow =  self.config_dict["heater_templow"]
            dht_msg += "Temp low; " + str(self.heater_templow) + " "
        else:
            dht_msg += "\nheater low temp not set\n"
            config_problems.append('heater_templow')
            self.heater_templow = None
        # high
        if "heater_temphigh" in self.config_dict:
            self.heater_temphigh = self.config_dict["heater_temphigh"]
            dht_msg += "temp high: " + str(self.heater_temphigh) + " (Centigrade)\n"
        else:
            dht_msg += "\nheater high temp not set\n"
            config_problems.append('heater_temphigh')
            self.heater_temphigh = None
        #
        # read humid info
        if "humid" in self.gpio_dict or "dehumid" in self.gpio_dict:
            dht_msg += "de/humid linked, "
        else:
            dht_msg += "de/humid NOT linked, "
        # low
        if "humid_low" in self.config_dict:
            self.humid_low = self.config_dict["humid_low"]
            dht_msg += "humidity low; " + str(self.humid_low)
        else:
            dht_msg += "\nHumid low not set\n"
            config_problems.append('humid_low')
            self.humid_low = None
        # high
        if "humid_high" in self.config_dict:
            self.humid_high = self.config_dict["humid_high"]
            dht_msg += " humidity high: " + str(self.humid_high) + "\n"
        else:
            dht_msg += "humid high not set\n"
            config_problems.append('humid_high')
            self.humid_high = None
        #
        #add gpio message to the message text
        config_msg += "We have " + str(len(self.gpio_dict)) + " devices linked to the GPIO\n"
        if "dht22sensor" in self.gpio_dict:
            dht_msg += "DHT Sensor on pin " + str(self.gpio_dict['dht22sensor'] + "\n")
            if "log_frequency" in self.config_dict:
                self.log_frequency = self.config_dict["log_frequency"]
                dht_msg += "Logging dht every " + str(self.log_frequency) + " seconds. \n"
            else:
                self.log_frequency = ""
                dht_msg += "DHT Logging frequency not set\n"
                config_problems.append('dht_log_frequency')
            #check to see if log location is set in dirlocs.txt
            try:
                dht_msg += "logging to; " + self.dirlocs_dict['loc_dht_log'] + "\n"
            except:
                dht_msg += "No DHT log locaion in pigrow dirlocs\n"
                config_problems.append('dht_log_location')
        else:
            dht_msg += "DHT Sensor not linked\n"

        #read cron info to see if dht script is running
        last_index = cron_list_pnl.startup_cron.GetItemCount()
        self.check_dht_running = "not found"
        extra_args = ""
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
                 if "checkDHT.py" in name:
                     self.check_dht_running = cron_list_pnl.startup_cron.GetItem(index, 1).GetText()
                     extra_args = cron_list_pnl.startup_cron.GetItem(index, 4).GetText().lower()
                     self.checkdht_cronindex = index
        # write more to dht script messages
        if self.check_dht_running == "True":
            dht_msg += "script check_DHT.py is currently running\n"
        elif self.check_dht_running == "not found":
            dht_msg += "script check_DHT not set to run on startup, add to cron and restart pigrow\n"
        elif self.check_dht_running == "False":
            dht_msg += "script check_DHT.py should be running but isn't - check error logs\n"
        else:
            dht_msg += "error reading cron info\n"
        #extra args used to select options modes, if to ignore heater, etc.
        dht_msg += "extra args = " + extra_args + "\n"
        dht_msg += ""
         #heater
        if "use_heat=true" in extra_args:
            dht_msg += "heater enabled, "
            self.use_heat = True
        elif "use_heat=false" in extra_args:
            dht_msg += "heater disabled, "
            self.use_heat = False
        else:
            dht_msg += "heater enabled, "
            self.use_heat = True
         #humid
        if "use_humid=true" in extra_args:
            dht_msg += "humidifier enabled, "
            self.use_humid = True
        elif "use_humid=false" in extra_args:
            dht_msg += "humidifier disabled, "
            self.use_humid = False
        else:
            dht_msg += "humidifier enabled, "
            self.use_humid = True
         #dehumid
        if "use_dehumid=true" in extra_args:
            dht_msg += "dehumidifier enabled, "
            self.use_dehumid = True
        elif "use_dehumid=false" in extra_args:
            dht_msg += "dehumidifier disabled, "
            self.use_dehumid = False
        else:
            dht_msg += "dehumidifier enabled, "
            self.use_dehumid = True
         #who controls fans
        if "use_fan=heat" in extra_args:
            dht_msg += "fan switched by heater "
            self.fans_owner = "heater"
        elif "use_fan=hum" in extra_args:
            dht_msg += "fan switched by humidifer "
            self.fans_owner = "humid"
        elif "use_fan=dehum" in extra_args:
            dht_msg += "fan switched by dehumidifer "
            self.fans_owner = "dehumid"
        elif "use_fan=hum" in extra_args:
            dht_msg += "dht control of fan disabled "
            self.fans_owner = "manual"
        else:
            dht_msg += "fan swtiched by heater"
            self.fans_owner = "heater"

        #checks to see if gpio devices with on directions are also linked to a gpio pin and counts them
        relay_list_text = "Device - Pin - Switch direction for power on - current device state"
        for key in self.gpio_on_dict:
            if key in self.gpio_dict:
                info = ''
                self.add_to_GPIO_list(str(key), self.gpio_dict[key], self.gpio_on_dict[key], info=info)
        #listing config problems at end of config messsage
        if len(config_problems) > 0:
            config_msg += "found " + str(len(config_problems)) + " config problems; "
        for item in config_problems:
            config_msg += item + ", "

        #putting the info on the screen
        config_info_pnl.boxname_text.SetValue(pi_link_pnl.boxname)
        config_info_pnl.config_text.SetLabel(config_msg)
        config_info_pnl.lamp_text.SetLabel(lamp_msg)
        config_info_pnl.dht_text.SetLabel(dht_msg)

    def get_cron_time(self, script):
        last_index = cron_list_pnl.timed_cron.GetItemCount()
        script_timestring = "not found"
        count = 0
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
                 if script in name:
                     script_timestring = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
                     count = count + 1
            if count > 1:
                return "runs more than once"
        return script_timestring

    def config_lamp_click(self, e):
        lamp_dbox = config_lamp_dialog(None, title='Config Lamp')
        lamp_dbox.ShowModal()

    def config_water_click(self, e):
        self.water_dbox = config_water_dialog(None, title='Config Watering')
        self.water_dbox.ShowModal()

    def config_dht_click(self, e):
        dht_dbox = edit_dht_dialog(None, title='Config DHT')
        dht_dbox.ShowModal()

    def add_new_device_relay(self, e):
        #define as blank
        config_ctrl_pnl.device_toedit = ""
        config_ctrl_pnl.gpio_toedit = ""
        config_ctrl_pnl.wiring_toedit = ""
        #create dialogue box
        gpio_dbox = edit_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        device = config_ctrl_pnl.device_new
        gpio = config_ctrl_pnl.gpio_new
        wiring = config_ctrl_pnl.wiring_new
        if not device == "":
            #update config file
            print((device, gpio, wiring))
            config_ctrl_pnl.add_to_GPIO_list(MainApp.config_ctrl_pannel, device, gpio, wiring, currently='UNLINKED')
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

        else:
            print ("cancelled")

    def check_device_status(self, gpio_pin, on_power_state):
        #Checks if a device is on or off by reading the pin and compairing to the relay wiring direction
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("echo " + str(gpio_pin) + " > /sys/class/gpio/export")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /sys/class/gpio/gpio" + str(gpio_pin) + "/value")
        gpio_status = out.strip()
        gpio_err = out.strip()
        if gpio_status == "1":
            if on_power_state == 'low':
                device_status = "OFF"
            elif on_power_state == 'high':
                device_status = 'ON'
            else:
                device_status = "settings error"
        elif gpio_status == '0':
            if on_power_state == 'low':
                device_status = "ON"
            elif on_power_state == 'high':
                device_status = 'OFF'
            else:
                device_status = "setting error"
        else:
            device_status = "read error -" + gpio_status + "-"
        return device_status

    def add_to_GPIO_list(self, device, gpio, wiring, currently='', info=''):
        #config_ctrl_pnl.add_to_GPIO_list(self, device, gpio, wiring, currently='', info='')
        if currently == '':
            currently = self.check_device_status(gpio, wiring)
        config_info_pnl.gpio_table.InsertItem(0, str(device))
        config_info_pnl.gpio_table.SetItem(0, 1, str(gpio))
        config_info_pnl.gpio_table.SetItem(0, 2, str(wiring))
        config_info_pnl.gpio_table.SetItem(0, 3, str(currently))
        config_info_pnl.gpio_table.SetItem(0, 4, str(info))

    def update_setting_file_on_pi_click(self, e, ask="yes"):
        #create updated settings file
        #
        #creating GPIO config block
        item_count = config_info_pnl.gpio_table.GetItemCount()
        # add dht22 sesnsor if present;
        if "dht22sensor" in self.gpio_dict:
            gpio_config_block = "\ngpio_dht22sensor=" + self.gpio_dict["dht22sensor"]
        else:
            gpio_config_block = ""
        # list all devices with gpio and wiring directions
        for count in range(0, item_count):
            device = config_info_pnl.gpio_table.GetItem(count, 0).GetText()
            gpio = config_info_pnl.gpio_table.GetItem(count, 1).GetText()
            wiring = config_info_pnl.gpio_table.GetItem(count, 2).GetText()
            if not str("gpio_" + device) in self.config_dict: #check for doubles, so can update by writing to config_dict
                gpio_config_block += "\ngpio_" + device + "=" + gpio
            if not str("gpio_" + device + "_on") in self.config_dict:
                gpio_config_block += "\ngpio_" + device + "_on=" + wiring
        # list all non-gpio settings
        other_settings = ""
        for key, value in list(self.config_dict.items()):
            other_settings += "\n" + key + "=" + value
        config_text = other_settings[1:]
        config_text += gpio_config_block
        # show user and ask user if they relly want to update
        if ask == "yes":
            dbox = wx.MessageDialog(self, config_text, "upload to pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            #if user said ok then upload file to pi
            if (answer == wx.ID_OK):
                update = True
            else:
                update = False
        else:
            update = True
        if update == True or shared_data.always_show_config_changes == True:
            pigrow_config_file_location = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/config/pigrow_config.txt"
            MainApp.localfiles_ctrl_pannel.save_text_to_file_on_pi(pigrow_config_file_location, config_text)
            self.update_pigrow_setup_pannel_information_click("e")
            MainApp.sensors_ctrl_pannel.make_tables_click("e")


class config_info_pnl(scrolled.ScrolledPanel):
    #  This displays the config info
    # controlled by the config_ctrl_pnl
    def __init__( self, parent ):
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.HSCROLL|wx.VSCROLL)
        font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        # Tab Title
        title_l = wx.StaticText(self,  label='Pigrow Setup', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Tools to set up the climate control functions of the Pigrow', size=(550,40))
        page_sub_title.SetFont(shared_data.sub_title_font)
        # info boxes
        self.name_l = wx.StaticText(self,  label='Box Name;', size=(100,25))
        self.name_l.SetFont(font)
        config_info_pnl.boxname_text = wx.TextCtrl(self)
        self.dirlocs_l = wx.StaticText(self,  label='dirlocs.txt location information;', size=(100,25))
        self.dirlocs_l.SetFont(font)
        config_info_pnl.location_text = wx.StaticText(self,  label='locations')
        self.conf_l = wx.StaticText(self,  label='pigrow_config.txt settings information;', size=(100,25))
        self.conf_l.SetFont(font)
        config_info_pnl.config_text = wx.StaticText(self,  label='config')
        self.lamp_l = wx.StaticText(self,  label='Lamp;', size=(100,25))
        self.lamp_l.SetFont(font)
        config_info_pnl.lamp_text = wx.StaticText(self,  label='lamp')
        self.dht_l = wx.StaticText(self,  label='DHT Sensor;      (Obsolete - Only used with checkDHT)', size=(100,25))
        self.dht_l.SetFont(font)
        config_info_pnl.dht_text = wx.StaticText(self,  label='dht')
        self.relay_l = wx.StaticText(self,  label='Relay GPIO link;', size=(100,25))
        self.relay_l.SetFont(font)
        config_info_pnl.gpio_table = self.GPIO_list(self, 1)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_GPIO)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_KEY_DOWN, self.del_gpio_item)
        gpio_pin_image = wx.Image('pi_zero.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        gpio_diagram = wx.StaticBitmap(self, -1, gpio_pin_image, (gpio_pin_image.GetWidth(), gpio_pin_image.GetHeight()))
        info_sizer = wx.BoxSizer(wx.VERTICAL)
        info_sizer.Add(self.name_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.boxname_text, 0, wx.LEFT|wx.EXPAND, 30)
        info_sizer.AddStretchSpacer(1)
        info_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        info_sizer.Add(self.dirlocs_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.location_text, 0, wx.LEFT|wx.EXPAND, 30)
        info_sizer.AddStretchSpacer(1)
        info_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        info_sizer.Add(self.conf_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.config_text, 0, wx.LEFT|wx.EXPAND, 30)
        info_sizer.AddStretchSpacer(1)
        info_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        info_sizer.Add(self.lamp_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.lamp_text, 0, wx.LEFT|wx.EXPAND, 30)
        info_sizer.AddStretchSpacer(1)
        info_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        info_sizer.Add(self.dht_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.dht_text, 0, wx.LEFT|wx.EXPAND, 30)
        info_sizer.AddStretchSpacer(1)
        info_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        info_sizer.Add(self.relay_l, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.Add(config_info_pnl.gpio_table, 0, wx.ALL|wx.EXPAND, 3)
        info_sizer.AddStretchSpacer(1)
        info_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_panel_sizer.Add(info_sizer, 0, wx.ALL|wx.EXPAND, 3)
        info_panel_sizer.Add(gpio_diagram, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(info_panel_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)
        self.SetupScrolling()

    def del_gpio_item(self, e):
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
                mbox = wx.MessageDialog(None, "Delete selected device?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
                sure = mbox.ShowModal()
                if sure == wx.ID_YES:
                    config_info_pnl.gpio_table.DeleteItem(config_info_pnl.gpio_table.GetFocusedItem())
                    MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

    class GPIO_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,635), size=(570,160)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Device')
            self.InsertColumn(1, 'GPIO')
            self.InsertColumn(2, 'wiring')
            self.InsertColumn(3, 'Currently')
            self.InsertColumn(4, 'info')
            self.SetColumnWidth(0, 150)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 100)
            self.SetColumnWidth(4, -1)

    def onDoubleClick_GPIO(self, e):
        index =  e.GetIndex()
        config_info_pnl.index = index
        #get info for dialogue box
        device = config_info_pnl.gpio_table.GetItem(index, 0).GetText()
        gpio = config_info_pnl.gpio_table.GetItem(index, 1).GetText()
        wiring = config_info_pnl.gpio_table.GetItem(index, 2).GetText()
        currently = config_info_pnl.gpio_table.GetItem(index, 3).GetText()
        #set data for dialogue box to read
        config_ctrl_pnl.device_toedit = device
        config_ctrl_pnl.gpio_toedit = gpio
        config_ctrl_pnl.wiring_toedit = wiring
        config_ctrl_pnl.currently_toedit = currently
        #create dialogue box
        gpio_dbox = doubleclick_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        # read data from dbox
        new_device = config_ctrl_pnl.device_new
        new_gpio = config_ctrl_pnl.gpio_new
        new_wiring = config_ctrl_pnl.wiring_new
        new_currently = config_ctrl_pnl.currently_new
        # if changes happened mark the ui
        #
        if not new_currently == "":
            config_info_pnl.gpio_table.SetItem(index, 0, str(new_device))
            config_info_pnl.gpio_table.SetItem(index, 1, str(new_gpio))
            config_info_pnl.gpio_table.SetItem(index, 2, str(new_wiring))
            config_info_pnl.gpio_table.SetItem(index, 3, str(new_currently))
        if not device == new_device or not gpio == new_gpio or not wiring == new_wiring:
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

class config_lamp_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing the lamp timing settings
    def __init__(self, *args, **kw):
        super(config_lamp_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 600))
        self.SetTitle("Config Lamp")
    def InitUI(self):
        # get settings
        on_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[0])
        on_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[1])
        off_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[0])
        off_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[1])
        # draw the pannel and text
        # title
        pnl = wx.Panel(self)
        title_l = wx.StaticText(self,  label='Lamp Config')
        title_l.SetFont(shared_data.title_font)
        # Timing Dials
        #   hour on - first line
        on_label = wx.StaticText(self,  label='on time')
        self.on_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(on_hour))
        self.on_hour_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        on_colon = wx.StaticText(self,  label=':')
        self.on_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(on_min))
        self.on_min_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        #   length on on period - second line
        duration_label = wx.StaticText(self,  label='Lamp on for ')
        self.on_period_h_spin = wx.SpinCtrl(self, min=0, max=23, value="")
        self.on_period_h_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        duration_mid = wx.StaticText(self,  label='hours and ')
        self.on_period_m_spin = wx.SpinCtrl(self, min=0, max=59, value="")
        self.on_period_m_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        duration_min = wx.StaticText(self,  label='min')
        #   off time - third line (worked out by above or manual input)
        off_label = wx.StaticText(self,  label='off time')
        self.off_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(off_hour))
        self.off_hour_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        off_mid = wx.StaticText(self,  label=':')
        self.off_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(off_min))
        self.off_min_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        #
        # cron timing of switches
        # labels
        cron_label = wx.StaticText(self,  label='Cron Timing of Switches;')
        blank = wx.StaticText(self,  label=' ')
        current_label = wx.StaticText(self,  label='Current')
        new_label = wx.StaticText(self,  label='New')
        cron_on_label = wx.StaticText(self,  label=" on;")
        cron_off_label = wx.StaticText(self,  label="off;")
        # cron strings
        lamp_on_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_on.py").strip()
        lamp_off_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_off.py").strip()
        self.cron_lamp_on = wx.StaticText(self,  label=lamp_on_string)
        self.cron_lamp_off = wx.StaticText(self,  label=lamp_off_string)
        new_on_string = (str(on_min) + " " + str(on_hour) + " * * *")
        new_off_string = (str(off_min) + " " + str(off_hour) + " * * *")
        self.new_on_string_text = wx.StaticText(self,  label=new_on_string,)
        self.new_off_string_text = wx.StaticText(self,  label=new_off_string)
        #
        # set lamp period values
        on_period_hour, on_period_min = self.calc_light_period(on_hour, on_min, off_hour, off_min)
        self.on_period_h_spin.SetValue(on_period_hour)
        self.on_period_m_spin.SetValue(on_period_min)
        #ok and cancel buttons
        self.ok_btn = wx.Button(self, label='Ok', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        # Sizers
        # timing
        on_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        on_time_sizer.Add(on_label, 0, wx.ALL, 5)
        on_time_sizer.Add(self.on_hour_spin, 0, wx.ALL, 5)
        on_time_sizer.Add(on_colon, 0, wx.ALL, 5)
        on_time_sizer.Add(self.on_min_spin, 0, wx.ALL, 5)
        on_duration_sizer = wx.BoxSizer(wx.HORIZONTAL)
        on_duration_sizer.Add(duration_label, 0, wx.ALL, 5)
        on_duration_sizer.Add(self.on_period_h_spin, 0, wx.ALL, 5)
        on_duration_sizer.Add(duration_mid, 0, wx.ALL, 5)
        on_duration_sizer.Add(self.on_period_m_spin, 0, wx.ALL, 5)
        on_duration_sizer.Add(duration_min, 0, wx.ALL, 5)
        off_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        off_time_sizer.Add(off_label, 0, wx.ALL, 5)
        off_time_sizer.Add(self.off_hour_spin, 0, wx.ALL, 5)
        off_time_sizer.Add(off_mid, 0, wx.ALL, 5)
        off_time_sizer.Add(self.off_min_spin, 0, wx.ALL, 5)
        #cron
        cron_info_sizer = wx.GridSizer(3, 3, 0, 0)
        cron_info_sizer.AddMany( [(blank, 0, wx.EXPAND),
            (current_label, 0, wx.EXPAND),
            (new_label, 0, wx.EXPAND),
            (cron_on_label, 0, wx.EXPAND),
            (self.cron_lamp_on, 0, wx.EXPAND),
            (self.new_on_string_text, 0, wx.EXPAND),
            (cron_off_label, 0, wx.EXPAND),
            (self.cron_lamp_off, 0, wx.EXPAND),
            (self.new_off_string_text, 0, wx.EXPAND)])
        # buttons
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0, wx.ALL, 5)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)
        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(on_time_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(on_duration_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(off_time_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(cron_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(cron_info_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer , 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)


    def on_spun(self, e):
        # make light hour and min into time delta
        light_period_h = self.on_period_h_spin.GetValue()
        light_period_m = self.on_period_m_spin.GetValue()
        time_period = datetime.timedelta(hours=light_period_h, minutes=light_period_m)
        # make on hour and min into datetime
        on_hour = self.on_hour_spin.GetValue()
        on_min = self.on_min_spin.GetValue()
        on_time = datetime.time(int(on_hour),int(on_min))
        date_on = datetime.datetime.combine(datetime.date.today(), on_time)
        # new off time
        new_off_time = date_on + time_period
        self.off_hour_spin.SetValue(new_off_time.hour)
        self.off_min_spin.SetValue(new_off_time.minute)
        self.new_on_string_text.SetLabel(str(on_min) + " " + str(on_hour) + " * * *")
        self.new_off_string_text.SetLabel(str(new_off_time.minute) + " " + str(new_off_time.hour) + " * * *")

    def off_spun(self, e):
        # make on hour and min into datetime
        on_hour = self.on_hour_spin.GetValue()
        on_min = self.on_min_spin.GetValue()
        off_hour = self.off_hour_spin.GetValue()
        off_min = self.off_min_spin.GetValue()
        hours, mins = self.calc_light_period(on_hour, on_min, off_hour, off_min)
        self.on_period_h_spin.SetValue(hours)
        self.on_period_m_spin.SetValue(mins)
        self.new_on_string_text.SetLabel(str(on_min) + " " + str(on_hour) + " * * *")
        self.new_off_string_text.SetLabel(str(off_min) + " " + str(off_hour) + " * * *")

    def calc_light_period(self, on_hour, on_min, off_hour, off_min):
        # make datetime objects
        on_time = datetime.time(int(on_hour),int(on_min))
        date_on = datetime.datetime.combine(datetime.date.today(), on_time)
        off_time = datetime.time(int(off_hour),int(off_min))
        # determine on/off cycle order and account for daily on/off cycle being inverted
        #                        i.e. lamp turning on at 7am and off at 6am gives 23 hours of light
        if on_time > off_time:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time) + datetime.timedelta(days=1)))
        else:
            dateoff = ((datetime.datetime.combine(datetime.date.today(), off_time)))
        # determine lamp period
        length_lamp_on = (dateoff - datetime.datetime.combine(datetime.date.today(), on_time))
        length_on_in_min = length_lamp_on.seconds / 60
        hours = length_on_in_min / 60 #because it's an int it ignores the remainder thus giving only whole hours (hacky?)
        mins = length_on_in_min - (hours * 60)
        return hours, mins


    def ok_click(self, e):
        # check for changes to cron
        if self.cron_lamp_on.GetLabel() == "not found" or self.cron_lamp_off.GetLabel() == "not found":
            mbox = wx.MessageDialog(None, "Add new job to cron?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                if self.cron_lamp_on.GetLabel() == "not found":
                    cron_task = "/home/pi/Pigrow/scripts/switches/" + "lamp_on.py"
                    MainApp.cron_info_pannel.add_to_onetime_list("new", "True", self.new_on_string_text.GetLabel(), cron_task)
                if self.cron_lamp_off.GetLabel() == "not found":
                    cron_task = "/home/pi/Pigrow/scripts/switches/" + "lamp_off.py"
                    MainApp.cron_info_pannel.add_to_onetime_list("new", "True", self.new_off_string_text.GetLabel(), cron_task)
                    MainApp.cron_info_pannel.update_cron_click("e")
        elif not self.new_on_string_text.GetLabel() == self.cron_lamp_on.GetLabel() or not self.new_off_string_text.GetLabel() == self.cron_lamp_off.GetLabel():
            print((":" + self.new_on_string_text.GetLabel() + ":"))
            print((":" + self.cron_lamp_on.GetLabel() + ":"))
            mbox = wx.MessageDialog(None, "Update cron timing?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            result_on = 'done'  # these are for cases when only one is changed
            result_off = 'done' # if it attempts to update cron and fails it'll change to an error message
            if sure == wx.ID_YES:
                if not self.new_on_string_text.GetLabel() == self.cron_lamp_on.GetLabel():
                    result_on = self.change_cron_trigger("lamp_on.py", self.new_on_string_text.GetLabel())
                if not self.new_off_string_text.GetLabel() == self.cron_lamp_off.GetLabel():
                    result_off = self.change_cron_trigger("lamp_off.py", self.new_off_string_text.GetLabel())
                if result_on != "done" or result_off != "done":
                    wx.MessageBox('Cron update error, edit lamp switches in the cron pannel', 'Info', wx.OK | wx.ICON_INFORMATION)
                else:
                    MainApp.cron_info_pannel.update_cron_click("e")
        # check for changes to settings file
        time_lamp_on = str(self.on_hour_spin.GetValue()) + ":" + str(self.on_min_spin.GetValue())
        time_lamp_off = str(self.off_hour_spin.GetValue()) + ":" + str(self.off_min_spin.GetValue())
        if not MainApp.config_ctrl_pannel.config_dict["time_lamp_on"] == time_lamp_on or not MainApp.config_ctrl_pannel.config_dict["time_lamp_off"] == time_lamp_off:
            MainApp.config_ctrl_pannel.config_dict["time_lamp_on"] = time_lamp_on
            MainApp.config_ctrl_pannel.config_dict["time_lamp_off"] = time_lamp_off
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")
        self.Destroy()

    def change_cron_trigger(self, script, new_time):
        last_index = cron_list_pnl.timed_cron.GetItemCount()
        script_timestring = "not found"
        count = 0
        if not last_index == 0:
            for index in range(0, last_index):
                 name = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
                 if script in name:
                     script_index = index
                     count = count + 1
            if count > 1:
                return "runs more than once"
        cron_list_pnl.timed_cron.SetStringItem(script_index, 2, new_time)
        return "done"

    def cancel_click(self, e):
        print("Cancelled")
        self.Destroy()

class config_water_dialog(wx.Dialog):
    # list of timed watering jobs
    class timed_watering_list(wx.ListCtrl):
        def __init__(self, parent, id, size=(600,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Line') #remove this if not needed
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Timing Mode')
            self.InsertColumn(3, 'Time')
            self.InsertColumn(4, 'Duration')
            #self.SetColumnWidth(0, 50)
            #self.SetColumnWidth(1, 50)
            #self.SetColumnWidth(2, 100)
            #self.SetColumnWidth(3, 150)

        def add_to_timed_water_list(self, line, enabled, timing_type, time, duration):
            self.InsertItem(0, str(line))
            self.SetItem(0, 1, str(enabled))
            self.SetItem(0, 2, str(timing_type))
            self.SetItem(0, 3, str(time))
            self.SetItem(0, 4, str(duration))

        def check_for_duration(self, job_extra):
            if 'duration=' in job_extra:
                duration = job_extra.split('duration=')[1].split(' ')[0]
            elif 's=' in job_extra:
                duration = job_extra.split('s=')[1].split(' ')[0]
            elif 'd=' in job_extra:
                duration = job_extra.split('d=')[1].split(' ')[0]
            else:
                duration = 'not set'
            return duration

        def fill_watering_job_list(self):
            print("Looing for watering jobs in cron tables")
            self.DeleteAllItems()  # clear out existing data so it's not doubled
            # add repeating jobs
            repeat_cron_list_count = cron_list_pnl.repeat_cron.GetItemCount()
            water_time = "not found"
            for index in range(0, repeat_cron_list_count):
                job_name  = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                if "timed_water.py" in job_name:
                    line_num = cron_list_pnl.repeat_cron.GetItem(index, 0).GetText()
                    enabled = cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()
                    job_extra = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                    water_time = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
                    # convert cron timing string into human readable text
                    freq_num, freq_text = cron_list_pnl.repeating_cron_list.parse_cron_string(self, water_time)
                    water_time = str(freq_num) + " " + freq_text
                    duration = self.check_for_duration(job_extra)
                    self.add_to_timed_water_list(line_num, enabled, 'repeating', water_time, duration)
            # add timed jobs
            onetime_cron_list_count = cron_list_pnl.timed_cron.GetItemCount()
            for index in range(0, onetime_cron_list_count):
                job_name  = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
                if "timed_water.py" in job_name:
                    line_num = cron_list_pnl.timed_cron.GetItem(index, 0).GetText()
                    enabled = cron_list_pnl.timed_cron.GetItem(index, 1).GetText()
                    job_extra = cron_list_pnl.timed_cron.GetItem(index, 4).GetText()
                    water_time = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
                    duration = self.check_for_duration(job_extra)
                    self.add_to_timed_water_list(line_num, enabled, 'exact time', water_time, duration)
            # add start up jobs
            startup_cron_list_count = cron_list_pnl.startup_cron.GetItemCount()
            for index in range(0, startup_cron_list_count):
                job_name  = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
                if "timed_water.py" in job_name:
                    line_num = cron_list_pnl.startup_cron.GetItem(index, 0).GetText()
                    enabled = cron_list_pnl.startup_cron.GetItem(index, 1).GetText()
                    job_extra = cron_list_pnl.startup_cron.GetItem(index, 4).GetText()
                    duration = self.check_for_duration(job_extra)
                    self.add_to_timed_water_list(line_num, enabled, 'startup', 'EVERY REBOOT', duration)



    #Dialog box for creating or editing the watering related settings
    def __init__(self, *args, **kw):
        super(config_water_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((650, 700))
        self.SetTitle("Config Water")
    def InitUI(self):

        # draw the pannel and text
        pnl = wx.Panel(self)
        title_l = wx.StaticText(self,  label='Watering Config')
        title_l.SetFont(shared_data.title_font)
        # gpio info
        self.gpio_loc_box_l = wx.StaticText(self,  label='GPIO Pin')
        self.gpio_loc_box = wx.TextCtrl(self, size=(70,30))
        self.gpio_direction_box_l = wx.StaticText(self,  label='Switch direction')
        directs = ['low', 'high']
        self.gpio_direction_box = wx.ComboBox(self, choices=directs,size=(100,30))
        # control options
        self.control_choices_l = wx.StaticText(self,  label='Control Using')
        control_choices = ['any', 'timed', 'sensor']
        self.control_choices_box = wx.ComboBox(self, choices=control_choices,size=(100,30))
        self.control_choices_box.Bind(wx.EVT_TEXT, self.control_choice_box_go)
        # # #
        # Shown when 'any' is selected
        msg = 'Manual control selected.\n\n '
        msg += 'Configure cron jobs manually using\n'
        msg += '     .../switches/timed_water.py\n'
        msg += '\n'
        msg += 'Other sensor and logic driven scripts coming soon'
        self.any_l = wx.StaticText(self,  label=msg)
        # Shown when timed is selected
        self.timed_l = wx.StaticText(self,  label='Water controlled by a timed_water.py cron job')
        # add new cron watering job
        # Water Duration
        self.water_duration_l = wx.StaticText(self,  label='Watering duration in seconds')
        self.water_duration = wx.TextCtrl(self, value="", style=wx.TE_PROCESS_ENTER)
        self.water_duration.Bind(wx.EVT_TEXT, self.water_duration_text_change)
        self.total_water_volume_l = wx.StaticText(self,  label='Total water to be pumped;')
        self.total_water_volume_unit = wx.StaticText(self,  label='litres')
        self.total_water_volume_value = wx.TextCtrl(self,  value='', style=wx.TE_PROCESS_ENTER)
        self.total_water_volume_value.Bind(wx.EVT_TEXT, self.water_volume_text_change)
        self.add_new_timed_watering_btn = wx.Button(self, label=' \nAdd new\nWatering Job\n ')
        self.add_new_timed_watering_btn.Bind(wx.EVT_BUTTON, self.add_new_timed_watering_click)
        self.manual_run_watering_btn = wx.Button(self, label=' \nRun Pump\nTimed\n ')
        self.manual_run_watering_btn.Bind(wx.EVT_BUTTON, self.manual_run_watering_click)
        # timing method
        self.timing_choices_l = wx.StaticText(self,  label='Timing')
        timing_choices = ['exact time', 'repeating']
        self.timing_choices_box = wx.ComboBox(self, choices=timing_choices,size=(100,30))
        self.timing_choices_box.Bind(wx.EVT_TEXT, self.timing_choice_box_go)
        # timing repeating
        self.repeat_time = wx.TextCtrl(self, size=(80, 25))
        rep_time_choices = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_time_box = wx.ComboBox(self, choices=rep_time_choices,size=(100,30))
        self.rep_time_key = wx.StaticText(self,  label='Min          :  Hour        :  Day       :  Month    :  Day Of Week')
        #timing exact
        self.min_time = wx.TextCtrl(self, size=(50, 25))
        self.hour_time = wx.TextCtrl(self, size=(50, 25))
        self.day_time = wx.TextCtrl(self, size=(50, 25))
        self.month_time = wx.TextCtrl(self, size=(50, 25))
        self.dow_time = wx.TextCtrl(self, size=(50, 25))
        # timed job list
        self.watering_jobs_cron_list = self.timed_watering_list(self, 1)


        # Shown when sensor is selected
        msg = 'Unfortunately this is not yet implemented,\nan update will be coming soon'
        self.sensor_l = wx.StaticText(self,  label=msg)
        # # #
        # flow rate Calibration tool
        msg = 'Flow Rate calibration;'
        self.flow_rate_l = wx.StaticText(self,  label=msg)
        self.calibrate_flow_rate_btn = wx.Button(self, label=' \nCalibrate\nFlow Rate\n ')
        self.calibrate_flow_rate_btn.Bind(wx.EVT_BUTTON, self.calibrate_flow_rate_click)
        self.flow_rate_per_min_value = wx.StaticText(self,  label='')
        self.flow_rate_per_min_l = wx.StaticText(self,  label=' Litres Per Min')
        # quick flow rate and volume calulator


        # ok / cancel buttons
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 450), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(250, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)
        # set info in boxes
        self.find_and_show_watering_relay()

        # Sizers
        gpio_loc_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gpio_loc_box_sizer.Add(self.gpio_loc_box_l, 0, wx.LEFT, 5)
        gpio_loc_box_sizer.Add(self.gpio_loc_box, 0, wx.LEFT, 5)
        gpio_dir_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gpio_dir_box_sizer.Add(self.gpio_direction_box_l, 0, wx.LEFT, 5)
        gpio_dir_box_sizer.Add(self.gpio_direction_box, 0, wx.LEFT, 5)
        gpio_sizer = wx.BoxSizer(wx.VERTICAL)
        gpio_sizer.Add(gpio_loc_box_sizer, 0, wx.ALL|wx.EXPAND, 3)
        gpio_sizer.Add(gpio_dir_box_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #
        control_choice_sizer = wx.BoxSizer(wx.HORIZONTAL)
        control_choice_sizer.Add(self.control_choices_l, 0, wx.ALL, 5)
        control_choice_sizer.Add(self.control_choices_box, 0, wx.ALL, 5)
        # Options only shown depending on control choice
        # shown only when 'any' is selected
        any_sizer = wx.BoxSizer(wx.VERTICAL)
        any_sizer.Add(self.any_l, 0, wx.ALL, 5)
        # shown only when 'timed' is selected
        timing_mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_mode_sizer.Add(self.timing_choices_l, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.timing_choices_box, 0, wx.ALL, 5)
        timing_mode_sizer.AddStretchSpacer(1)
        timing_mode_sizer.Add(self.repeat_time, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.rep_time_box, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.min_time, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.hour_time, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.day_time, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.month_time, 0, wx.ALL, 5)
        timing_mode_sizer.Add(self.dow_time, 0, wx.ALL, 5)

        water_duration_sizer = wx.BoxSizer(wx.HORIZONTAL)
        water_duration_sizer.Add(self.water_duration_l, 0, wx.ALL, 2)
        water_duration_sizer.Add(self.water_duration, 0, wx.ALL, 2)
        total_volume_sizer = wx.BoxSizer(wx.HORIZONTAL)
        total_volume_sizer.Add(self.total_water_volume_l, 0, wx.ALL, 2)
        total_volume_sizer.Add(self.total_water_volume_value, 0, wx.ALL, 2)
        total_volume_sizer.Add(self.total_water_volume_unit, 0, wx.ALL, 2)
        water_duration_and_total_sizer = wx.BoxSizer(wx.VERTICAL)
        water_duration_and_total_sizer.Add(water_duration_sizer, 0, wx.LEFT, 30)
        water_duration_and_total_sizer.Add(total_volume_sizer, 0, wx.LEFT, 30)
        #water_duration_and_total_sizer.Add(timing_mode_sizer, 0, wx.ALL, 5)
        #water_duration_and_total_sizer.Add(self.rep_time_key, 0, wx.LEFT, 175)
        add_new_job_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_new_job_sizer.Add(self.add_new_timed_watering_btn, 0, wx.LEFT, 20)
        add_new_job_sizer.Add(water_duration_and_total_sizer, 0, wx.ALL, 5)
        add_new_job_sizer.Add(self.manual_run_watering_btn, 0, wx.LEFT, 10)
        timed_sizer = wx.BoxSizer(wx.VERTICAL)
        timed_sizer.Add(self.timed_l, 0, wx.ALL, 5)
        timed_sizer.Add(add_new_job_sizer, 0, wx.ALL, 5)
        timed_sizer.Add(timing_mode_sizer, 0, wx.ALL, 5)
        timed_sizer.Add(self.rep_time_key, 0, wx.LEFT, 175)
        timed_sizer.Add(self.watering_jobs_cron_list, 0, wx.ALL, 5)


        # shown only when 'sensor' is selected
        sensor_sizer = wx.BoxSizer(wx.VERTICAL)
        sensor_sizer.Add(self.sensor_l, 0, wx.ALL, 5)
        #
        # flow rate Calibration tool
        flow_per_sec_sizer = wx.BoxSizer(wx.HORIZONTAL)
        flow_per_sec_sizer.Add(self.flow_rate_per_min_value, 0, wx.ALL, 5)
        flow_per_sec_sizer.Add(self.flow_rate_per_min_l, 0, wx.ALL, 5)
        calibrate_flow_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calibrate_flow_rate_sizer.Add(self.calibrate_flow_rate_btn, 0, wx.ALL, 5)
        calibrate_flow_rate_sizer.Add(flow_per_sec_sizer, 0, wx.ALL, 5)
        flow_rate_sizer = wx.BoxSizer(wx.VERTICAL)
        flow_rate_sizer.Add(self.flow_rate_l, 0, wx.ALL, 5)
        flow_rate_sizer.Add(calibrate_flow_rate_sizer, 0, wx.ALL, 5)

        #
        top_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_bar_sizer.Add(gpio_sizer, 0, wx.ALL, 5)
        top_bar_sizer.AddStretchSpacer(1)
        top_bar_sizer.Add(flow_rate_sizer, 0, wx.ALL, 5)

        #
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0, wx.ALL, 5)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(top_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        # shown only when selected
        main_sizer.Add(control_choice_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(timed_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(sensor_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(any_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer , 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

        self.watering_jobs_cron_list.fill_watering_job_list()

    def water_duration_text_change(self, e):
        flow_rate = self.flow_rate_per_min_value.GetLabel()
        time_to_run = self.water_duration.GetValue()
        try:
            water_volume = round((float(flow_rate)/60) * float(time_to_run), 4)
        except:
            water_volume = ''
        self.total_water_volume_value.ChangeValue(str(water_volume))
        self.Layout()

    def water_volume_text_change(self, e):
        flow_rate = self.flow_rate_per_min_value.GetLabel()
        volume = self.total_water_volume_value.GetValue()
        try:
            time_to_run = round(float(volume) / (float(flow_rate)/60), 4)
        except:
            time_to_run = ""
        self.water_duration.ChangeValue(str(time_to_run))
        self.Layout()


    def calibrate_flow_rate_click(self, e):
        calibrate_water_dbox = calibrate_water_flow_rate_dialog(None)
        calibrate_water_dbox.ShowModal()
        if not self.flow_rate_per_min_value.GetLabel() == "":
            self.total_water_volume_value.Enable(True)
        self.Layout()

    def add_new_timed_watering_click(self, e):
        print("this is not implemented yet but will be soon...")
        task_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/timed_water.py"
        # Watering Duration
        duration = self.water_duration.GetValue()
        if not duration.isdigit():
            msg = "You must set a watering duration or volume"
            msg += "\n\n The watering duration must be a whole number of seconds\n without any decimal points or commas"
            wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
            return None
        # Watering Timing
        timing_choice = self.timing_choices_box.GetValue()
        if not timing_choice == 'exact time' and not timing_choice == 'repeating':
            msg = "You must select a timing method and time"
            wx.MessageBox(msg, 'Error', wx.OK | wx.ICON_ERROR)
            return None
        if timing_choice == 'exact time':
            timing_min = self.min_time.GetValue()
            timing_hour = self.hour_time.GetValue()
            timing_day = self.day_time.GetValue()
            timing_month = self.month_time.GetValue()
            timing_dow = self.dow_time.GetValue()
            time_text = cron_info_pnl.make_onetime_cron_timestring(None, timing_min, timing_hour, timing_day, timing_month, timing_dow)
            cron_info_pnl.add_to_onetime_list(None, 'new', True, time_text, task_path, 'duration=' + duration, '')
        elif timing_choice == 'repeating':
            repeat_num = self.repeat_time.GetValue()
            repeat_text = self.rep_time_box.GetValue()
            time_text = repeat_num + " " + repeat_text
            timing_string = cron_info_pnl.make_repeating_cron_timestring(None, repeat_num, repeat_text)
            cron_info_pnl.add_to_repeat_list(None, 'new', True, timing_string, task_path, 'duration=' + duration, '')
        # add to the list table
        self.timed_watering_list.add_to_timed_water_list(self.watering_jobs_cron_list, 'new', 'true', timing_choice, time_text, duration)
        cron_info_pnl.update_cron_click(MainApp.cron_info_pannel, 'e')

    def manual_run_watering_click(self, e):
        duration = self.water_duration.GetValue()
        try:
            print(duration)
            duration = round(float(duration), 0)
            duration = str(duration).split('.')[0]
        except:
            print("Watering duration needs to be a number")
            return None
        cmd = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/timed_water.py duration=" + duration
        msg = "Run the water for " + duration + " seconds?\n\nYou will not be able to cancel this once it starts."
        dbox = wx.MessageDialog(self, msg, "Manual Watering Event", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        if (answer == wx.ID_OK):
            print(" Running - " + cmd)
            MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)

    def hide_hideable_ui(self):
        self.timed_l.Hide()
        self.water_duration_l.Hide()
        self.water_duration.Hide()
        self.total_water_volume_l.Hide()
        self.total_water_volume_value.Hide()
        self.sensor_l.Hide()
        self.any_l.Hide()
        self.timing_choices_l.Hide()
        self.timing_choices_box.Hide()
        self.repeat_time.Hide()
        self.rep_time_box.Hide()
        self.min_time.Hide()
        self.hour_time.Hide()
        self.day_time.Hide()
        self.month_time.Hide()
        self.dow_time.Hide()
        self.rep_time_key.Hide()
        self.total_water_volume_unit.Hide()
        self.add_new_timed_watering_btn.Hide()
        self.manual_run_watering_btn.Hide()
        self.watering_jobs_cron_list.Hide()
        self.Layout()

    def control_choice_box_go(self, e):
        self.hide_hideable_ui()
        control_choice = self.control_choices_box.GetValue()
        if control_choice == 'timed':
            self.timed_l.Show()
            self.water_duration_l.Show()
            self.water_duration.Show()
            self.total_water_volume_l.Show()
            self.total_water_volume_value.Show()
            self.timing_choices_l.Show()
            self.timing_choices_box.Show()
            self.total_water_volume_unit.Show()
            self.add_new_timed_watering_btn.Show()
            self.manual_run_watering_btn.Show()
            self.watering_jobs_cron_list.Show()
        if control_choice == 'sensor':
            self.sensor_l.Show()
        if control_choice == 'any':
            self.any_l.Show()
        self.Layout()

    def timing_choice_box_go(self, e):
        timing_choice = self.timing_choices_box.GetValue()
        if timing_choice == 'repeating':
            self.min_time.Hide()
            self.hour_time.Hide()
            self.day_time.Hide()
            self.month_time.Hide()
            self.dow_time.Hide()
            self.rep_time_key.Hide()
            self.repeat_time.Show()
            self.rep_time_box.Show()
        elif timing_choice == 'exact time':
            self.min_time.Show()
            self.hour_time.Show()
            self.day_time.Show()
            self.month_time.Show()
            self.dow_time.Show()
            self.rep_time_key.Show()
            self.repeat_time.Hide()
            self.rep_time_box.Hide()
        self.Layout()

    def find_and_show_watering_relay(self):
        # all relay config settings are stored in gpio_dict and gpio_on_dict
        # other settings in the config_dict
        print(MainApp.config_ctrl_pannel.gpio_on_dict)
        print("Looking for watering device in config")
        # gpio address
        if "water" in MainApp.config_ctrl_pannel.gpio_dict:
            self.gpio_loc_box.SetValue(MainApp.config_ctrl_pannel.gpio_dict["water"])
        else:
            print("Watering Device not found in pigrow's settings file")
            self.gpio_loc_box.SetValue("none")

        # direction
        if "water" in MainApp.config_ctrl_pannel.gpio_on_dict:
            print("Found watering relays switch direction; ")
            self.gpio_direction_box.SetValue(MainApp.config_ctrl_pannel.gpio_on_dict["water"])
        else:
            print("Watering devices switch direction not found in pigrow's settings file")
            self.gpio_direction_box.SetValue('none')
        # control
        if 'water_control' in MainApp.config_ctrl_pannel.config_dict:
            print("Found watering control option; ")
            self.control_choices_box.SetValue(MainApp.config_ctrl_pannel.config_dict["water_control"])
        else:
            print("Watering devices control option not found in pigrow's config file")
            self.control_choices_box.SetValue('none')
        # flow rate
        if 'water_flow_rate' in MainApp.config_ctrl_pannel.config_dict:
            #print("Found water flow rate; ")
            self.flow_rate_per_min_value.SetLabel(MainApp.config_ctrl_pannel.config_dict["water_flow_rate"])
            self.total_water_volume_value.Enable(True)
        else:
            print("Water flow rate option not found in pigrow's config file")
            self.flow_rate_per_min_value.SetLabel("")
            self.total_water_volume_value.Enable(False)


    def ok_click(self, e):
        # Check for changes to settings file
        settings_changed = False
        new_gpio = self.gpio_loc_box.GetValue().strip()
        new_switch_direction = self.gpio_direction_box.GetValue().strip()
        new_control_option = self.control_choices_box.GetValue()
        new_flow_rate = self.flow_rate_per_min_value.GetLabel()
        # gpio pin
        if 'water' in MainApp.config_ctrl_pannel.gpio_dict:
            current_gpio = MainApp.config_ctrl_pannel.gpio_dict["water"]
        else:
            current_gpio = "none"
        if not current_gpio == new_gpio:
            settings_changed = True
        # switch direction
        if 'water' in MainApp.config_ctrl_pannel.gpio_on_dict:
            current_switch_direction = MainApp.config_ctrl_pannel.gpio_on_dict["water"]
        else:
            current_switch_direction = 'none'
        if not current_switch_direction == new_switch_direction:
            settings_changed = True
        # water control
        if 'water_control' in MainApp.config_ctrl_pannel.config_dict:
            current_control_option = MainApp.config_ctrl_pannel.config_dict["water_control"]
        else:
            current_control_option = 'none'
        if not current_control_option == new_control_option:
            settings_changed = True
        # water flow rate
        if 'water_flow_rate' in MainApp.config_ctrl_pannel.config_dict:
            current_flow_rate = MainApp.config_ctrl_pannel.config_dict["water_flow_rate"]
        else:
            current_flow_rate = 'none'
        if not current_flow_rate == new_flow_rate:
            settings_changed = True

        # Update settings file
        if settings_changed == True:
            # Add to the config_dict so it get's written to the pi then loading into the relay table
            MainApp.config_ctrl_pannel.config_dict["gpio_water"] = new_gpio
            MainApp.config_ctrl_pannel.config_dict["gpio_water_on"] = new_switch_direction
            MainApp.config_ctrl_pannel.config_dict["water_control"] = new_control_option
            if not new_flow_rate == "none" or not new_flow_rate == "":
                MainApp.config_ctrl_pannel.config_dict["water_flow_rate"] = new_flow_rate
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")



        #
        self.Destroy()

    def cancel_click(self, e):
        print("Changing watering configuration has ben cancelled")
        self.Destroy()

class calibrate_water_flow_rate_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(calibrate_water_flow_rate_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((450, 300))
        self.SetTitle("Calibrate Water Flow Rate")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        title_l = wx.StaticText(self,  label='Calibrate Water Flow Rate')
        title_l.SetFont(shared_data.title_font)
        msg = 'Time how long it takes to fill a measured\ncontainer to determine the flow rate of\nyour pump.'
        sub_title_l = wx.StaticText(self,  label=msg)
        sub_title_l.SetFont(shared_data.sub_title_font)
        # container size input
        self.container_size_l = wx.StaticText(self,  label='Container Size')
        self.container_size_box = wx.TextCtrl(self, size=(70,30))
        # Running Time
        self.running_time_l = wx.StaticText(self,  label='Time Elapsed; ')
        self.running_time_value = wx.StaticText(self,  label='--')
        # ok / cancel buttons
        self.go_btn = wx.Button(self, label='Start', pos=(15, 450), size=(175, 30))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(250, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)

        flow_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        flow_rate_sizer.Add(self.container_size_l, 0, wx.ALL, 5)
        flow_rate_sizer.Add(self.container_size_box, 0, wx.ALL, 5)
        running_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        running_time_sizer.Add(self.running_time_l, 0, wx.ALL, 5)
        running_time_sizer.Add(self.running_time_value, 0, wx.ALL, 5)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.go_btn, 0, wx.ALL, 5)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(sub_title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(flow_rate_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(running_time_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer , 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

        # Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

    def update(self, event):
        self.time_count = self.time_count + 1
        self.running_time_value.SetLabel(str(self.time_count))

    def turn_on(self, water_gpio_pin, water_gpio_direction):
        if water_gpio_direction == 'low':
            on_cmd = 'generic_low.py'
        elif water_gpio_direction == 'high':
            on_cmd = 'generic_high.py'
        cmd = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/" + on_cmd + " gpio=" + water_gpio_pin
        print(" Running - " + cmd)
        MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)

    def turn_off(self, water_gpio_pin, water_gpio_direction):
        if water_gpio_direction == 'high':
            on_cmd = 'generic_low.py'
        elif water_gpio_direction == 'low':
            on_cmd = 'generic_high.py'
        cmd = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/" + on_cmd + " gpio=" + water_gpio_pin
        print(" Running - " + cmd)
        MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)

    def go_click(self, e):
        button_label = self.go_btn.GetLabel()
        water_gpio_pin = MainApp.config_ctrl_pannel.water_dbox.gpio_loc_box.GetValue()
        water_gpio_direction = MainApp.config_ctrl_pannel.water_dbox.gpio_direction_box.GetValue()
        if button_label == "Start":
            self.time_count = 0
            self.timer.Start(1000)
            self.go_btn.SetLabel("Stop")
            print(" Setting GPIO " + water_gpio_pin + " to " + water_gpio_direction + " ( - ON - )")
            self.turn_on(water_gpio_pin, water_gpio_direction)
        else:
            self.timer.Stop()
            self.go_btn.SetLabel("Start")
            print(" Setting GPIO " + water_gpio_pin + " to the opposite of " + water_gpio_direction + " ( - OFF - )")
            self.turn_off(water_gpio_pin, water_gpio_direction)
            total_time = int(self.running_time_value.GetLabel())
            container_size = int(self.container_size_box.GetValue())
            flowrate = round(container_size / total_time, 4)
            print(" Total Time - " + str(total_time) + " seconds to fill a " + str(container_size) + " litre container")
            print(" Flowrate of " + str(flowrate) + " litres per second, or " + str(flowrate * 60) + ' litres per min')
            msg = "Set the flow rate to " + str(flowrate*60) + " litres per minute"
            mbox = wx.MessageDialog(None, msg, "Set flow rate?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                MainApp.config_ctrl_pannel.water_dbox.flow_rate_per_min_value.SetLabel(str(flowrate*60))
                self.Destroy()

    def OnClose(self, e):
        if not self.go_btn.GetLabel() == "Start":
            water_gpio_pin = MainApp.config_ctrl_pannel.water_dbox.gpio_loc_box.GetValue()
            water_gpio_direction = MainApp.config_ctrl_pannel.water_dbox.gpio_direction_box.GetValue()
            self.turn_off(water_gpio_pin, water_gpio_direction)
            self.timer.Stop()
        self.Destroy()

class doubleclick_gpio_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(doubleclick_gpio_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((450, 300))
        self.SetTitle("GPIO config")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Edit Device Config', pos=(20, 10))
        self.msgtext = wx.StaticText(self,  label='', pos=(10, 40))
        self.update_box_text()
        # buttons
        okButton = wx.Button(self, label='Ok', pos=(25, 150))
        edit_Button = wx.Button(self, label='Edit', pos=(150, 150))
        switch_Button = wx.Button(self, label='Switch', pos=(275, 150))
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        edit_Button.Bind(wx.EVT_BUTTON, self.OnEdit)
        switch_Button.Bind(wx.EVT_BUTTON, self.OnSwitch)

    def update_box_text(self):
        msg = config_ctrl_pnl.device_toedit
        msg += "\n GPIO pin; " + config_ctrl_pnl.gpio_toedit
        msg += "\n Wiring direction; " + config_ctrl_pnl.wiring_toedit
        msg += "\n Currently: " + config_ctrl_pnl.currently_toedit
        self.msgtext.SetLabel(msg)

    def OnClose(self, e):
        self.Destroy()

    def OnEdit(self, e):
        # show edit_gpio_dialog box
        gpio_dbox = edit_gpio_dialog(None, title='Device GPIO link')
        gpio_dbox.ShowModal()
        # catch any changes made if ok was pressed, if cancel all == ''
        if not config_ctrl_pnl.currently_new == "":
            config_ctrl_pnl.device_toedit =  config_ctrl_pnl.device_new
            config_ctrl_pnl.gpio_toedit =  config_ctrl_pnl.gpio_new
            config_ctrl_pnl.wiring_toedit =  config_ctrl_pnl.wiring_new
            config_ctrl_pnl.currently_toedit =  config_ctrl_pnl.currently_new
        self.Destroy()


    def OnSwitch(self, e):
        device = config_ctrl_pnl.device_toedit
        currently = config_ctrl_pnl.currently_toedit
        self.switch_device(device, currently)
        if not currently == config_ctrl_pnl.currently_new:
            # if changes happened mark the ui
            config_info_pnl.gpio_table.SetStringItem(config_info_pnl.index, 3, str(config_ctrl_pnl.currently_new))

    def switch_device(self, device, currently):
        switch_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/"
        if currently == "ON":
            switch_command = switch_path + device + "_off.py"
            future_state = "OFF"
        elif currently == "OFF":
            switch_command = switch_path + device + "_on.py"
            future_state = "ON"
        else:
            switch_command = "ERROR"
        #if error show error message
        if not switch_command == "ERROR":
            #make dialogue box to ask if should switch the device
            d = wx.MessageDialog(
                self, "Are you sure you want to switch " + device + " to the " +
                future_state + " poisition?\n\n\n " +
                "Note: automated control scripts might " +
                "\n      switch this " + currently + " again " +
                "\n      if thier trigger conditions are met. "
                , "Switch " + device + " " + future_state + "?"
                , wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = d.ShowModal()
            d.Destroy()
            #if user said ok then switch device
            if (answer == wx.ID_OK):
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(switch_command)
                print (out)   # shows box with switch info from pigrow
                if not error == "": print (error)
                config_ctrl_pnl.currently_toedit = future_state #for if toggling within the dialog box
                self.update_box_text()
                config_ctrl_pnl.currently_new = future_state
                config_ctrl_pnl.device_new = device
                config_ctrl_pnl.gpio_new = config_ctrl_pnl.gpio_toedit
                config_ctrl_pnl.wiring_new = config_ctrl_pnl.wiring_toedit
        else:
            d = wx.MessageDialog(self, "Error, current state not determined\n You must upload the settings to the pigrow before switching the device", "Error", wx.OK | wx.ICON_ERROR)
            answer = d.ShowModal()
            d.Destroy()
            return "ERROR"

class edit_gpio_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(edit_gpio_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((850, 380))
        self.SetTitle("Device GPIO config")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # these need to be set by whoever calls the dialog box before it's created
        device = config_ctrl_pnl.device_toedit
        gpio = config_ctrl_pnl.gpio_toedit
        wiring = config_ctrl_pnl.wiring_toedit

        # draw the pannel
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Device GPIO Config', pos=(20, 10))
        #background image
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # devices combo box
        switch_list = self.list_switch_scripts()
        unlinked_devices = self.list_unused_devices(switch_list)
        wx.StaticText(self,  label='Device;', pos=(20, 50))
        self.devices_combo = wx.ComboBox(self, choices = unlinked_devices, pos=(90,50), size=(175, 25))
        self.devices_combo.SetValue(device)
        # gpio text box
        wx.StaticText(self,  label='GPIO', pos=(10, 100))
        self.gpio_tc = wx.TextCtrl(self, pos=(56, 98), size=(40, 25))
        self.gpio_tc.SetValue(gpio)
        self.gpio_tc.Bind(wx.EVT_CHAR, self.onChar) #limit to valid gpio numbers
        # wiring direction combo box
        wiring_choices = ['low', 'high']
        wx.StaticText(self,  label='Wiring side;', pos=(100, 100))
        self.wiring_combo = wx.ComboBox(self, choices = wiring_choices, pos=(200,98), size=(110, 25))
        self.wiring_combo.SetValue(wiring)
        #Buttom Row of Buttons
        okButton = wx.Button(self, label='Ok', pos=(200, 250))
        closeButton = wx.Button(self, label='Cancel', pos=(300, 250))
        okButton.Bind(wx.EVT_BUTTON, self.set_new_gpio_link)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./relaydialogue.png")
        dc.DrawBitmap(bmp, 0, 0)

    def onChar(self, event):
        #this inhibits any non-numeric keys
        key = event.GetKeyCode()
        try: character = chr(key)
        except ValueError: character = "" # arrow keys will throw this error
        acceptable_characters = "1234567890"
        if character in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127: # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del
            event.Skip()
            return
        else:
            return False

    def list_switch_scripts(self):
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/scripts/switches/")
        switches = out.split("\n")
        switch_list = []
        for item in switches:
            if item[-6:] == "_on.py":
                switch_list.append(item.split("_")[0])
            elif item.split('_')[0] == "timed":
                switch_list.append(item.split("_")[1].split(".")[0])
        return switch_list

    def list_unused_devices(self, switch_list):
        item_count = config_info_pnl.gpio_table.GetItemCount()
        used_devices = []
        for num in range(0, item_count):
            device = config_info_pnl.gpio_table.GetItem(num, 0).GetText()
            used_devices.append(device)
        unused_devices = []
        for item in switch_list:
            if not item in used_devices:
                unused_devices.append(item)
        return unused_devices

    def list_used_gpio(self):
        item_count = config_info_pnl.gpio_table.GetItemCount()
        used_gpio = []
        for num in range(0, item_count):
            gpio = config_info_pnl.gpio_table.GetItem(num, 1).GetText()
            used_gpio.append(gpio)
        return used_gpio

    def list_unused_gpio(self, used_gpio):
        valid_gpio = ['2', '3', '4', '17', '27', '22', '10', '9', '11', '5',
                      '6', '13', '19', '26', '14', '15', '18', '23', '24',
                      '25', '8', '7', '12', '16', '20', '21']
        unused_gpio = []
        for item in valid_gpio:
            if not item in used_gpio:
                unused_gpio.append(item)
        return unused_gpio

    def set_new_gpio_link(self, e):
        #get data from combo boxes.
        unused_gpio = self.list_unused_gpio(self.list_used_gpio())
        config_ctrl_pnl.device_new = self.devices_combo.GetValue()
        config_ctrl_pnl.gpio_new = self.gpio_tc.GetValue()
        config_ctrl_pnl.wiring_new = self.wiring_combo.GetValue()
        #check to see if info is valid and closes if it is
        should_close = True
        # check if device is set
        if config_ctrl_pnl.device_new == "":
            wx.MessageBox('Select a device to link from the list', 'Error', wx.OK | wx.ICON_INFORMATION)
            should_close = False
        #check if gpio number is valid
        if not config_ctrl_pnl.gpio_new == config_ctrl_pnl.gpio_toedit or config_ctrl_pnl.gpio_toedit == "":
            if not config_ctrl_pnl.gpio_new in unused_gpio and should_close == True:
                wx.MessageBox('Select a valid and unused gpio pin', 'Error', wx.OK | wx.ICON_INFORMATION)
                config_ctrl_pnl.gpio_new = self.gpio_tc.SetValue("")
                should_close = False
        # check if wiring direction is set to a valid setting
        if not config_ctrl_pnl.wiring_new == "low" and should_close == True:
            if not config_ctrl_pnl.wiring_new == "high":
                wx.MessageBox("No wiring direction set, \nIf you don't know guess and change it if the device turns on when it should be off", 'Error', wx.OK | wx.ICON_INFORMATION)
                should_close = False
        # if box should be closed then close it
        if should_close == True:
            #checks to see if changes have been made and updates ui if so
            if not config_ctrl_pnl.device_new == config_ctrl_pnl.device_toedit:
                config_ctrl_pnl.currently_new = 'unlinked'
            else:
                if not config_ctrl_pnl.gpio_new == config_ctrl_pnl.gpio_toedit:
                    config_ctrl_pnl.currently_new = 'unlinked'
                else:
                    if not config_ctrl_pnl.wiring_new == config_ctrl_pnl.wiring_toedit:
                        config_ctrl_pnl.currently_new = 'unlinked'
                    else:
                        config_ctrl_pnl.currently_new = config_ctrl_pnl.currently_toedit
            self.Destroy()

    def OnClose(self, e):
        config_ctrl_pnl.device_new = ''
        config_ctrl_pnl.gpio_new = ''
        config_ctrl_pnl.wiring_new = ''
        config_ctrl_pnl.currently_new = ''
        self.Destroy()

class edit_dht_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(edit_dht_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 600))
        self.SetTitle("Dht config")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        ## top text
        warning = "This is only used for the \ncheckDHT.py method\n which is now replaced by\n the modular sensor system.\n"
        warning += "Use that instead"
        warning_l = wx.StaticText(self,  label=warning, pos=(350, 100))
        warning_l.SetForegroundColour((180,80,70))
        wx.StaticText(self,  label='Sensor Config;', pos=(20, 10))
        # editable info text
        self.sensor_combo = wx.ComboBox(self, pos=(10,35), choices=['dht22', 'dht11', 'am2302'])
        self.sensor_combo.SetValue("dht22")
        wx.StaticText(self,  label=' on GPIO pin ', pos=(120, 40))
        self.gpio_text = wx.TextCtrl(self, value="", pos=(230, 35))
        # gpio pin
        if "dht22sensor" in MainApp.config_ctrl_pannel.gpio_dict:
            self.sensor_pin = MainApp.config_ctrl_pannel.gpio_dict['dht22sensor']
        else:
            self.sensor_pin = ""
        self.gpio_text.SetValue(self.sensor_pin)
        # read buttons
        self.read_dht_btn = wx.Button(self, label='read sensor', pos=(5, 70), size=(150, 60))
        self.read_dht_btn.Bind(wx.EVT_BUTTON, self.read_dht_click)
        ## temp and humid live reading
        wx.StaticText(self,  label='Temp;', pos=(165, 75))
        wx.StaticText(self,  label='Humid;', pos=(165, 100))
        self.temp_text = wx.StaticText(self,  label='', pos=(230, 75))
        self.humid_text = wx.StaticText(self,  label='', pos=(230, 100))
        ##
        if MainApp.config_ctrl_pannel.check_dht_running == "True":
            check_msg = "Active"
        elif MainApp.config_ctrl_pannel.check_dht_running == "not found":
            check_msg = "not set"
        elif MainApp.config_ctrl_pannel.check_dht_running == "False":
            check_msg = "Error"
       # device control
        wx.StaticText(self,  label='Device Control - checkDHT.py : ' + check_msg, pos=(10, 140))
        wx.StaticText(self,  label='DHT controlled switching of device relays', pos=(5, 155))
        self.heater_checkbox = wx.CheckBox(self, label='Heater', pos = (10,180))
        self.humid_checkbox = wx.CheckBox(self, label='Humid', pos = (110,180))
        self.dehumid_checkbox = wx.CheckBox(self, label='Dehumid', pos = (210,180))
        self.heater_checkbox.SetValue(MainApp.config_ctrl_pannel.use_heat)
        self.humid_checkbox.SetValue(MainApp.config_ctrl_pannel.use_humid)
        self.dehumid_checkbox.SetValue(MainApp.config_ctrl_pannel.use_dehumid)
        wx.StaticText(self,  label='fans controlled by ', pos=(10, 210))
        self.fans_combo = wx.ComboBox(self, pos=(170,205), choices=['manual', 'heater', 'humid', 'dehumid'])
        self.fans_combo.SetValue(MainApp.config_ctrl_pannel.fans_owner)
        #
        # logging info
        wx.StaticText(self,  label='logging every ', pos=(10, 360))
        self.log_rate_text = wx.TextCtrl(self, value="", pos=(130, 355))
        wx.StaticText(self,  label='seconds', pos=(230, 360))
        # logging frequency
        self.log_frequency = MainApp.config_ctrl_pannel.log_frequency
        self.log_rate_text.SetValue(self.log_frequency)
        # log location
        wx.StaticText(self,  label='to; ', pos=(10, 390))
        self.log_loc_text = wx.TextCtrl(self, value="", pos=(30, 385), size=(350, 25))
        if "loc_dht_log" in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_location = MainApp.config_ctrl_pannel.dirlocs_dict['loc_dht_log']
            print (log_location)
            print ("log location")
        else:
            log_location = "none set"
        self.log_loc_text.SetValue(log_location)
        # if checkdht not set to run then greyout unused commands
        if check_msg == "not set":
            self.heater_checkbox.Enable(False)
            self.humid_checkbox.Enable(False)
            self.dehumid_checkbox.Enable(False)
            self.fans_combo.Enable(False)
            self.log_rate_text.Enable(False)
            self.log_loc_text.Enable(False)


        # temp and humidity brackets
        temp_low = MainApp.config_ctrl_pannel.heater_templow
        temp_high = MainApp.config_ctrl_pannel.heater_temphigh
        humid_low = MainApp.config_ctrl_pannel.humid_low
        humid_high = MainApp.config_ctrl_pannel.humid_high
        wx.StaticText(self,  label='Temp', pos=(55, 235))
        wx.StaticText(self,  label='Humid', pos=(250, 235))
        wx.StaticText(self,  label='high -', pos=(5, 260))
        wx.StaticText(self,  label='high -', pos=(200, 260))
        wx.StaticText(self,  label='low -', pos=(5, 295))
        wx.StaticText(self,  label='low -', pos=(200, 295))
        self.high_temp_text = wx.TextCtrl(self, value=temp_high, pos=(50, 255))
        self.low_temp_text = wx.TextCtrl(self, value=temp_low, pos=(50, 290))
        self.high_humid_text = wx.TextCtrl(self, value=humid_high, pos=(250, 255))
        self.low_humid_text = wx.TextCtrl(self, value=humid_low, pos=(250, 290))
        #buttons
        # need to add - check if software installed if not change read dht to install dht and if config changes made change to confirm changes or something
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 450), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)


    def read_dht_click(self, e):
        self.sensor_pin = self.gpio_text.GetValue()
        self.sensor = self.sensor_combo.GetValue()
        args = "gpio=" + self.sensor_pin + " sensor=" + self.sensor
        print (args)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/build_test/test_dht.py " + args)
        out = out.strip()
        if "temp" in out:
            out = out.split(" ")
            temp = out[0].split("=")[1]
            humid = out[1].split("=")[1]
            self.temp_text.SetLabel(temp)
            self.humid_text.SetLabel(humid)
        elif "failed" in out:
            self.temp_text.SetLabel("failed")
            self.humid_text.SetLabel("failed")
        else:
            self.temp_text.SetLabel("error")
            self.humid_text.SetLabel("error")

    def ok_click(self, e):
        #check for changes
        changes_made = ""
        # loking for changes to config options for settings file
        if not self.gpio_text.GetValue() == MainApp.config_ctrl_pannel.gpio_dict['dht22sensor']:
            changes_made += "Dht gpio; " + self.gpio_text.GetValue() + " "
        if not self.log_rate_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['log_frequency']:
            changes_made += "log rate; " + self.log_rate_text.GetValue() + " "
        if not self.high_temp_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['heater_temphigh']:
            changes_made += "temp high; " + self.high_temp_text.GetValue() + " "
        if not self.low_temp_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['heater_templow']:
            changes_made += "temp low; " + self.low_temp_text.GetValue() + " "
        if not self.high_humid_text.GetValue() == MainApp.config_ctrl_pannel.config_dict["humid_high"]:
            changes_made += "humid high; " + self.high_humid_text.GetValue() + " "
        if not self.low_humid_text.GetValue() == MainApp.config_ctrl_pannel.config_dict['humid_low']:
            changes_made += "humid low; " + self.low_humid_text.GetValue() + " "
        # looking for changes to cron options for checkDHT.py
        extra_args = ""
        if not changes_made == "":
            changes_made += "\n"
        if not self.heater_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_heat:
            changes_made += " Heater enabled;" + str(self.heater_checkbox.GetValue())
        if self.heater_checkbox.GetValue() == False:
            extra_args += " use_heat=false"
        if not self.humid_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_humid:
            changes_made += " Humid enabled:" + str(self.humid_checkbox.GetValue())
        if self.humid_checkbox.GetValue() == False:
            extra_args += " use_humid=false"
        if not self.dehumid_checkbox.GetValue() == MainApp.config_ctrl_pannel.use_dehumid:
            changes_made += " Dehumid enabled;" + str(self.dehumid_checkbox.GetValue())
        if self.dehumid_checkbox.GetValue() == False:
            extra_args += " use_dehumid=false"
        if not self.fans_combo.GetValue() == MainApp.config_ctrl_pannel.fans_owner:
            changes_made += " Fans set by;" + self.fans_combo.GetValue()
        if self.fans_combo.GetValue() == "manual":
            extra_args += " usefan=none"
        elif self.fans_combo.GetValue() == "humid":
            extra_args += " usefan=hum"
        elif self.fans_combo.GetValue() == "dehumid":
            extra_args += " usefan=dehum"
        if len(extra_args) > 1:
            extra_args = extra_args[1:]
            print(("extra args = " + extra_args))
            index = MainApp.config_ctrl_pannel.checkdht_cronindex
            cron_list_pnl.startup_cron.SetStringItem(index, 4, str(extra_args))
            changes_made += "\n -- Update Cron to save changes --"


        #
        # changing settings ready for updating config file
        #
        if not changes_made == "":
            #setting dht22 in config dictionary
            if not self.gpio_text.GetValue() == "":
                MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"] = self.gpio_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"]
            print("ignoring self.sensor_combo box because code not written for pigrow base code")
            # logging rate in config dictionary
            if not self.log_rate_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["log_frequency"] = self.log_rate_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["log_frequency"]
            # temp and humid min max values
            if not self.high_temp_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["heater_temphigh"] = self.high_temp_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["heater_temphigh"]
            if not self.low_temp_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["heater_templow"] = self.low_temp_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["heater_templow"]
            if not self.high_humid_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["humid_high"] = self.high_humid_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["humid_high"]
            if not self.low_humid_text.GetValue() == "":
                MainApp.config_ctrl_pannel.config_dict["humid_low"] = self.low_humid_text.GetValue()
            else:
                del MainApp.config_ctrl_pannel.config_dict["humid_low"]
            #
            # edit dht message text
            MainApp.config_info_pannel.dht_text.SetLabel("changes have been made update pigrow config to use them\n" + changes_made)
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")
        self.Destroy()

    def cancel_click(self, e):
        print("Cancelled")
        self.Destroy()

#
#
##Cron tab
#
#
class cron_info_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        wx.StaticText(self,  label='Cron Config Menu', pos=(25, 10))
        self.read_cron_btn = wx.Button(self, label='Read Crontab', pos=(10, 40), size=(175, 30))
        self.read_cron_btn.Bind(wx.EVT_BUTTON, self.read_cron_click)
        self.new_cron_btn = wx.Button(self, label='New cron job', pos=(10, 80), size=(175, 30))
        self.new_cron_btn.Bind(wx.EVT_BUTTON, self.new_cron_click)
        self.update_cron_btn = wx.Button(self, label='Update Cron', pos=(10, 120), size=(175, 30))
        self.update_cron_btn.Bind(wx.EVT_BUTTON, self.update_cron_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.read_cron_btn, 0, wx.ALL, 5)
        main_sizer.Add(self.new_cron_btn, 0, wx.ALL, 5)
        main_sizer.Add(self.update_cron_btn, 0, wx.ALL, 5)
        self.SetSizer(main_sizer)



    def update_cron_click(self, e):
        #make a text file of all the cron jobs
        cron_text = ''
        startup_num = cron_list_pnl.startup_cron.GetItemCount()
        for num in range(0, startup_num):
            cron_line = ''
            if cron_list_pnl.startup_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            script_cmd = cron_list_pnl.startup_cron.GetItemText(num, 3) # cron task
            script_cmd += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 4) # cron_extra_args
            script_cmd += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 5) # cron_comment
            cron_line += '@reboot ' + script_cmd
            cron_text += cron_line + '\n'
            # ask if unrunning scripts should be started
            is_running = self.test_if_script_running(cron_list_pnl.startup_cron.GetItemText(num, 3))
            enabled = cron_list_pnl.startup_cron.GetItemText(num, 1)
            print (enabled)
            if is_running == False and enabled == 'True':
                dbox = wx.MessageDialog(self, "Would you like to start running script " + str(script_cmd), "Run on Pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                dbox.Destroy()
                if (answer == wx.ID_OK):
                    print(("Running " +str(script_cmd)))
                    ssh.exec_command(script_cmd + " &") # don't ask for output and it's non-blocking
                                                        # this is absolutely vital!
        # add repating jobs to cron list
        repeat_num = cron_list_pnl.repeat_cron.GetItemCount()
        for num in range(0, repeat_num):
            cron_line = ''
            if cron_list_pnl.repeat_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.repeat_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        onetime_num = cron_list_pnl.timed_cron.GetItemCount()
        for num in range(0, onetime_num):
            cron_line = ''
            if cron_list_pnl.timed_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.timed_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        # ask the user if they're sure
        msg_text = "Update cron to; \n\n" + cron_text
        mbox = wx.MessageDialog(None, msg_text, "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if sure == wx.ID_YES:
            print ("Updating remote cron")
            # save cron text onto pigrow as text file then import into cron
            sftp = ssh.open_sftp()
            try:
                tempfolder = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp'
                sftp.mkdir(tempfolder)
            except IOError:
                pass
            f = sftp.open(tempfolder + '/remotecron.txt', 'w')
            f.write(cron_text)
            f.close()
            responce, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab " + tempfolder + '/remotecron.txt')
        else:
            print("Updating cron cancelled")
        mbox.Destroy()
        #refresh cron list
        self.read_cron_click("event")

    def read_cron_click(self, event):
        #reads pi's crontab then puts jobs in correct table
        print("Reading cron information from pi")
        cron_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab -l")
        cron_text = cron_text.split('\n')
        #select instance of list to use
        startup_list_instance = cron_list_pnl.startup_cron
        repeat_list_instance = cron_list_pnl.repeat_cron
        onetime_list_instance = cron_list_pnl.timed_cron
        #clear lists of prior data
        startup_list_instance.DeleteAllItems()
        repeat_list_instance.DeleteAllItems()
        onetime_list_instance.DeleteAllItems()
        #sort cron info into lists
        line_number = 0

        for cron_line in cron_text:
            line_number = line_number + 1
            real_job = True
            if len(cron_line) > 5:
                cron_line.strip()
                #determine if enabled or disabled with hash
                if cron_line[0] == '#':
                    job_enabled = False
                    cron_line = cron_line[1:].strip(' ')
                else:
                    job_enabled = True
                # sort for job type, split into timing string and cmd sting
                if cron_line.find('@reboot') > -1:
                    cron_jobtype = 'reboot'
                    timing_string = '@reboot'
                    cmd_string = cron_line[8:]
                else:
                    split_cron = cron_line.split(' ')
                    timing_string = ''
                    for star in split_cron[0:5]:
                        if not star.find('*') > -1 and not star.isdigit():
                            real_job = False
                        timing_string += star + ' '
                    cmd_string = ''

                    for cmd in split_cron[5:]:
                        cmd_string += cmd + ' '
                    if timing_string.find('/') > -1:
                        cron_jobtype = 'repeating'
                    else:
                        cron_jobtype = 'one time'
                # split cmd_string into cmd_string and comment
                cron_comment_pos = cmd_string.find('#')
                if cron_comment_pos > -1:
                    cron_comment = cmd_string[cron_comment_pos:].strip(' ')
                    cmd_string = cmd_string[:cron_comment_pos].strip(' ')
                else:
                    cron_comment = ''
                # split cmd_string into task and extra args
                cron_task = cmd_string.split(' ')[0]
                cron_extra_args = ''
                for arg in cmd_string.split(' ')[1:]:
                    cron_extra_args += arg + ' '
                if real_job == True and not cmd_string == '':
                    #print job_enabled, timing_string, cron_jobtype, cron_task, cron_extra_args, cron_comment
                    if cron_jobtype == 'reboot':
                        self.add_to_startup_list(line_number, job_enabled, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'one time':
                        self.add_to_onetime_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'repeating':
                        self.add_to_repeat_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
        print("cron information read and updated into tables.")

    def test_if_script_running(self, script):
        print(" --- Note: cron tab start-up scripts table currently only tests if a script is active and ignores name= arguments ")
        #cron_info_pnl.test_if_script_running(MainApp.cron_info_pannel, script)
        script_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("pidof -x " + str(script))
        if script_text == '':
            return False
        else:
            #print 'pid of = ' + str(script_text)
            return True

    def add_to_startup_list(self, line_number, job_enabled, cron_task, cron_extra_args='', cron_comment=''):
        is_running = self.test_if_script_running(cron_task)
        cron_list_pnl.startup_cron.InsertItem(0, str(line_number))
        cron_list_pnl.startup_cron.SetItem(0, 1, str(job_enabled))
        cron_list_pnl.startup_cron.SetItem(0, 2, str(is_running))   #tests if script it currently running on pi
        cron_list_pnl.startup_cron.SetItem(0, 3, cron_task)
        cron_list_pnl.startup_cron.SetItem(0, 4, cron_extra_args)
        cron_list_pnl.startup_cron.SetItem(0, 5, cron_comment)

    def add_to_repeat_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.repeat_cron.InsertItem(0, str(line_number))
        cron_list_pnl.repeat_cron.SetItem(0, 1, str(job_enabled))
        cron_list_pnl.repeat_cron.SetItem(0, 2, timing_string)
        cron_list_pnl.repeat_cron.SetItem(0, 3, cron_task)
        cron_list_pnl.repeat_cron.SetItem(0, 4, cron_extra_args)
        cron_list_pnl.repeat_cron.SetItem(0, 5, cron_comment)

    def add_to_onetime_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.timed_cron.InsertItem(0, str(line_number))
        cron_list_pnl.timed_cron.SetItem(0, 1, str(job_enabled))
        cron_list_pnl.timed_cron.SetItem(0, 2, timing_string)
        cron_list_pnl.timed_cron.SetItem(0, 3, cron_task)
        cron_list_pnl.timed_cron.SetItem(0, 4, cron_extra_args)
        cron_list_pnl.timed_cron.SetItem(0, 5, cron_comment)

    def make_repeating_cron_timestring(self, repeat, repeat_num):
        #assembles timing sting for cron
        # min (0 - 59) | hour (0 - 23) | day of month (1-31) | month (1 - 12) | day of week (0 - 6) (Sunday=0)
        if repeat == 'min':
            if int(repeat_num) in range(0,59):
                cron_time_string = '*/' + str(repeat_num)
            else:
                print("Cron string min wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string = '*'
        if repeat == 'hour':
            if int(repeat_num) in range(0,23):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron string hour wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'day':
            if int(repeat_num) in range(1,31):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron string day wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'month':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting month wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'dow':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron string dow wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        return cron_time_string

    def make_onetime_cron_timestring(self, job_min, job_hour, job_day, job_month, job_dow):
        # timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        if job_min.isdigit():
            timing_string = str(job_min)
        else:
            timing_string = '*'
        if job_hour.isdigit():
            timing_string += ' ' + str(job_hour)
        else:
            timing_string += ' *'
        if job_day.isdigit():
            timing_string += ' ' + str(job_day)
        else:
            timing_string += ' *'
        if job_month.isdigit():
            timing_string += ' ' + str(job_month)
        else:
            timing_string += ' *'
        if job_dow.isdigit():
            timing_string += ' ' + str(job_dow)
        else:
            timing_string += ' *'
        return timing_string

    def new_cron_click(self, e):
        #define blank fields and defaults for dialogue box to read
        cron_info_pnl.cron_path_toedit = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/cron/"
        cron_info_pnl.cron_task_toedit = 'input cron task here'
        cron_info_pnl.cron_args_toedit = ''
        cron_info_pnl.cron_comment_toedit = ''
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '30'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = ''
        cron_info_pnl.cron_month_toedit = ''
        cron_info_pnl.cron_dow_toedit = ''
        cron_info_pnl.cron_enabled_toedit = True
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = self.make_onetime_cron_timestring(job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None or not job_script == '':
            cron_task = job_path + job_script
            if cron_jobtype == 'startup':
                self.add_to_startup_list('new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                self.add_to_onetime_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                self.add_to_repeat_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

class cron_list_pnl(wx.Panel):
    #
    #  This displays the three different cron type lists on the big-pannel
    #  double click to edit one of the jobs (not yet written)
    #  ohter control buttons found on the cron control pannel
    #

    #none of these resize or anything at the moment
    #consider putting into a sizer or autosizing with math
    #--to screen size tho not to size of cronlist that'd be super messy...
    class startup_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,10), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Active')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 55)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 75)
            self.SetColumnWidth(3, 400)
            self.SetColumnWidth(4, 300)
            self.SetColumnWidth(5, 100)

    class repeating_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,245), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'every')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 55)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 400)
            self.SetColumnWidth(4, 300)
            self.SetColumnWidth(5, 100)

        def parse_cron_string(self, cron_rep_string):
            try:
                cron_stars = cron_rep_string.split(' ')
                if '/' in cron_stars[0]:
                    cron_rep = 'min'
                    cron_num = cron_stars[0].split('/')[-1]
                elif '/' in cron_stars[1]:
                    cron_rep = 'hour'
                    cron_num = cron_stars[1].split('/')[-1]
                elif '/' in cron_stars[2]:
                    cron_rep = 'day'
                    cron_num = cron_stars[2].split('/')[-1]
                elif '/' in cron_stars[3]:
                    cron_rep = 'month'
                    cron_num = cron_stars[3].split('/')[-1]
                elif '/' in cron_stars[4]:
                    cron_rep = 'dow'
                    cron_num = cron_stars[4].split('/')[-1]
                else:
                    cron_rep = ""
                    cron_num = "fail"
                return cron_num, cron_rep
            except:
                return "", ""

    class other_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,530)):
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Time')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 55)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 400)
            self.SetColumnWidth(4, 300)
            self.SetColumnWidth(5, 100)

    def __init__( self, parent ):
        wx.Panel.__init__(self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL)
        # Tab Title
        title_l = wx.StaticText(self,  label='Cron Tab Control', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Use cron on the pigrow to time events and trigger devices', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)
        # Info boxes
        cron_start_up_l = wx.StaticText(self,  label='Cron start up;')
        cron_list_pnl.startup_cron = self.startup_cron_list(self, 1)
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_startup)
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.startup_got_focus)
        cron_repeat_l = wx.StaticText(self,  label='Repeating Jobs;')
        cron_list_pnl.repeat_cron = self.repeating_cron_list(self, 1)
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.repeat_got_focus)
        cron_timed_l = wx.StaticText(self,  label='One time triggers;')
        cron_list_pnl.timed_cron = self.other_cron_list(self, 1)
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.timed_got_focus)
        # sizers
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(cron_start_up_l, 0, wx.ALL, 3)
        main_sizer.Add(cron_list_pnl.startup_cron, 1, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(cron_repeat_l, 0, wx.ALL, 3)
        main_sizer.Add(cron_list_pnl.repeat_cron, 1, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(cron_timed_l, 0, wx.ALL, 3)
        main_sizer.Add(cron_list_pnl.timed_cron, 1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def startup_got_focus(self, e):
        timed_focus = cron_list_pnl.timed_cron.GetFocusedItem()
        cron_list_pnl.timed_cron.Select(timed_focus, on=0)
        repeat_focus = cron_list_pnl.repeat_cron.GetFocusedItem()
        cron_list_pnl.repeat_cron.Select(repeat_focus, on=0)

    def repeat_got_focus(self, e):
        startup_focus = cron_list_pnl.startup_cron.GetFocusedItem()
        cron_list_pnl.startup_cron.Select(startup_focus, on=0)
        timed_focus = cron_list_pnl.timed_cron.GetFocusedItem()
        cron_list_pnl.timed_cron.Select(timed_focus, on=0)

    def timed_got_focus(self, e):
        startup_focus = cron_list_pnl.startup_cron.GetFocusedItem()
        cron_list_pnl.startup_cron.Select(startup_focus, on=0)
        repeat_focus = cron_list_pnl.repeat_cron.GetFocusedItem()
        cron_list_pnl.repeat_cron.Select(repeat_focus, on=0)


    def del_item(self, e):
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
                mbox = wx.MessageDialog(None, "Delete selected cron job?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
                sure = mbox.ShowModal()
                if sure == wx.ID_YES:
                    if cron_list_pnl.startup_cron.GetSelectedItemCount() == 1:
                        print(cron_list_pnl.startup_cron.DeleteItem(cron_list_pnl.startup_cron.GetFocusedItem()))
                    if cron_list_pnl.repeat_cron.GetSelectedItemCount() == 1:
                        print(cron_list_pnl.repeat_cron.DeleteItem(cron_list_pnl.repeat_cron.GetFocusedItem()))
                    if cron_list_pnl.timed_cron.GetSelectedItemCount() == 1:
                        print(cron_list_pnl.timed_cron.DeleteItem(cron_list_pnl.timed_cron.GetFocusedItem()))



    def onDoubleClick_timed(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
        cron_stars = timing_string.split(' ')
        cron_min = cron_stars[0]
        cron_hour = cron_stars[1]
        cron_day = cron_stars[2]
        cron_month = cron_stars[3]
        cron_dow = cron_stars[4]

        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'one time'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = cron_min
        cron_info_pnl.cron_hour_toedit = cron_hour
        cron_info_pnl.cron_day_toedit = cron_day
        cron_info_pnl.cron_month_toedit = cron_month
        cron_info_pnl.cron_dow_toedit = cron_dow
        if str(cron_list_pnl.timed_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = cron_info_pnl.make_onetime_cron_timestring(MainApp.cron_info_pannel, job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.timed_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_repeat(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
        cron_num, cron_rep = cron_list_pnl.repeating_cron_list.parse_cron_string(self, timing_string)
        #
        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = cron_rep
        cron_info_pnl.cron_everynum_toedit = cron_num
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = '*'
        cron_info_pnl.cron_month_toedit = '*'
        cron_info_pnl.cron_dow_toedit = '*'
        if str(cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.repeat_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_startup(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'startup'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = '*'
        cron_info_pnl.cron_month_toedit = '*'
        cron_info_pnl.cron_dow_toedit = '*'
        if str(cron_list_pnl.startup_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.startup_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

class cron_job_dialog(wx.Dialog):
    #Dialog box for creating or editing cron scripts
    #   takes ten variables from cron_info_pnl
    #   which need to be set before it's called
    #   then it creates ten outgonig variables to
    #   be grabbed after it closes to be stored in
    #   whatever table they belong in
    #    - cat_script displays text of currently selected script
    #            this is useful for sh scripts with no -h option.
    #    - get_cronable_scripts(script_path) takes path and
    #            returns a list of py or sh scripts in that folder.
    #    - get_help_text(script_to_ask) which takes script location and
    #            returns the helpfile text from the -h output of the script.
    def __init__(self, *args, **kw):
        super(cron_job_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((850, 400))
        self.SetTitle("Cron Job Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #these need to be set before the dialog is created
        cron_path = cron_info_pnl.cron_path_toedit
        cron_task = cron_info_pnl.cron_task_toedit
        cron_args = cron_info_pnl.cron_args_toedit
        cron_comment = cron_info_pnl.cron_comment_toedit
        cron_type = cron_info_pnl.cron_type_toedit
        cron_everystr = cron_info_pnl.cron_everystr_toedit
        cron_everynum = cron_info_pnl.cron_everynum_toedit
        cron_enabled = cron_info_pnl.cron_enabled_toedit
        cron_min = cron_info_pnl.cron_min_toedit
        cron_hour = cron_info_pnl.cron_hour_toedit
        cron_day = cron_info_pnl.cron_day_toedit
        cron_month = cron_info_pnl.cron_month_toedit
        cron_dow = cron_info_pnl.cron_dow_toedit
        #draw the pannel
         ## universal controls
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Cron job editor', pos=(20, 10))
        cron_type_opts = ['startup', 'repeating', 'one time']
        wx.StaticText(self,  label='timing method;', pos=(165, 10))
        self.cron_type_combo = wx.ComboBox(self, choices = cron_type_opts, pos=(260,10), size=(125, 25))
        self.cron_type_combo.Bind(wx.EVT_COMBOBOX, self.cron_type_combo_go)
        wx.StaticText(self,  label='path;', pos=(10, 50))
        script_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts"
        cron_path_opts = [script_path + "/cron/", script_path + "/autorun/", script_path + "/switches/", script_path + "/sensors/", script_path + "/visualisation/"]
        self.cron_path_combo = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER, choices = cron_path_opts, pos=(100,45), size=(525, 30))
        self.cron_path_combo.Bind(wx.EVT_TEXT_ENTER, self.cron_path_combo_go)
        self.cron_path_combo.Bind(wx.EVT_COMBOBOX, self.cron_path_combo_go)
        show_cat_butt = wx.Button(self, label='view script', pos=(625, 75))
        show_cat_butt.Bind(wx.EVT_BUTTON, self.cat_script)
        wx.StaticText(self,  label='Extra args;', pos=(10, 110))
        self.cron_args_tc = wx.TextCtrl(self, pos=(100, 110), size=(525, 25))
        show_help_butt = wx.Button(self, label='show help', pos=(625, 110))
        show_help_butt.Bind(wx.EVT_BUTTON, self.show_help)
        wx.StaticText(self,  label='comment;', pos=(10, 140))
        self.cron_comment_tc = wx.TextCtrl(self, pos=(100, 140), size=(525, 25))
        self.cron_enabled_cb = wx.CheckBox(self,  label='Enabled', pos=(400, 190))
        ### set universal controls data...
        self.cron_type_combo.SetValue(cron_type)
        self.cron_path_combo.SetValue(cron_path)
        self.cron_args_tc.SetValue(cron_args)
        self.cron_comment_tc.SetValue(cron_comment)
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb = wx.ComboBox(self, choices = cron_script_opts, pos=(25,80), size=(600, 25))
        self.cron_script_cb.SetValue(cron_task)
        self.cron_enabled_cb.SetValue(cron_enabled)
        # draw and hide optional option controlls
        ## for repeating cron jobs
        self.cron_rep_every = wx.StaticText(self,  label='Every ', pos=(60, 190))
        self.cron_every_num_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25))  #box for number, name num only range set by repeat_opt
        self.cron_every_num_tc.Bind(wx.EVT_CHAR, self.onChar)
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.cron_repeat_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, pos=(170,190), size=(100, 30))
        self.cron_rep_every.Hide()
        self.cron_every_num_tc.Hide()
        self.cron_repeat_opts_cb.Hide()
        self.cron_repeat_opts_cb.SetValue(cron_everystr)
        self.cron_every_num_tc.SetValue(cron_everynum)
        ## for one time cron jobs
        self.cron_switch = wx.StaticText(self,  label='Time; ', pos=(60, 190))
        self.cron_switch2 = wx.StaticText(self,  label='[min : hour : day : month : day of the week]', pos=(110, 220))
        self.cron_timed_min_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25)) #limit to 0-23
        self.cron_timed_min_tc.SetValue(cron_min)
        self.cron_timed_min_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_hour_tc = wx.TextCtrl(self, pos=(160, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_hour_tc.SetValue(cron_hour)
        self.cron_timed_hour_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_day_tc = wx.TextCtrl(self, pos=(205, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_day_tc.SetValue(cron_day)
        self.cron_timed_day_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_month_tc = wx.TextCtrl(self, pos=(250, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_month_tc.SetValue(cron_month)
        self.cron_timed_month_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_dow_tc = wx.TextCtrl(self, pos=(295, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_dow_tc.SetValue(cron_dow)
        self.cron_timed_dow_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_switch.Hide()
        self.cron_switch2.Hide()
        self.cron_timed_min_tc.Hide()
        self.cron_timed_hour_tc.Hide()
        self.cron_timed_day_tc.Hide()
        self.cron_timed_month_tc.Hide()
        self.cron_timed_dow_tc.Hide()
        self.set_control_visi() #set's the visibility of optional controls
        #Buttom Row of Buttons
        okButton = wx.Button(self, label='Ok', pos=(200, 250))
        closeButton = wx.Button(self, label='Cancel', pos=(300, 250))
        okButton.Bind(wx.EVT_BUTTON, self.do_upload)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def onChar(self, event):
        #this inhibits any non-numeric keys
        key = event.GetKeyCode()
        try: character = chr(key)
        except ValueError: character = "" # arrow keys will throw this error
        acceptable_characters = "1234567890"
        if character in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127: # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del
            event.Skip()
            return
        else:
            return False

    def cat_script(self, e):
        target_ip = pi_link_pnl.target_ip
        target_user = pi_link_pnl.target_user
        target_pass = pi_link_pnl.target_pass
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        script_to_ask = script_path + script_name

        try:
            script_text, error_text = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + str(script_to_ask))
            print("Connected to " + target_ip)
            print("running; cat " + str(script_to_ask))
            if not error_text == '':
                msg_text =  "Error reading script " + script_to_ask + " \n\n"
                msg_text += str(error_text)
            else:
                msg_text = script_to_ask + '\n\n'
                msg_text += str(script_text)
            dbox = show_script_cat(None, msg_text, script_to_ask)
            dbox.ShowModal()
            dbox.Destroy()
        except Exception as e:
            print("oh bother, this seems wrong... " + str(e))

    def get_cronable_scripts(self, script_path):
        #this reads the files in the path provided
        #then creates a list of all .py and .sh scripts in that folder
        cron_opts = []
        try:
            print("reading " + str(script_path))
            out, error_text = MainApp.localfiles_ctrl_pannel.run_on_pi("ls " + str(script_path))
            cron_dir_list = out.split('\n')
            for filename in cron_dir_list:
                if filename.endswith("py") or filename.endswith('sh'):
                    cron_opts.append(filename)
        except Exception as e:
            print(("aggghhhhh cap'ain something ain't right! " + str(e)))
        return cron_opts
    def cron_path_combo_go(self, e):
        cron_path = self.cron_path_combo.GetValue()
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb.Clear()
        for x in cron_script_opts:
            self.cron_script_cb.Append(x)
    def cron_type_combo_go(self, e):
        self.set_control_visi()
    def set_control_visi(self):
        #checks which type of cron job is set in combobox and shows or hides
        #which ever UI elemetns are required - doesn't lose or change the data.
        cron_type = self.cron_type_combo.GetValue()
        if cron_type == 'one time':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Show()
            self.cron_switch2.Show()
            self.cron_timed_min_tc.Show()
            self.cron_timed_hour_tc.Show()
            self.cron_timed_day_tc.Show()
            self.cron_timed_month_tc.Show()
            self.cron_timed_dow_tc.Show()
        elif cron_type == 'repeating':
            self.cron_rep_every.Show()
            self.cron_every_num_tc.Show()
            self.cron_repeat_opts_cb.Show()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
        elif cron_type == 'startup':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
    def get_help_text(self, script_to_ask):
        #open an ssh pipe and runs the script with a -h argument
        #
        #WARNING
        #       If the script doesn't support -h args then it'll just run it
        #       this can cause switches to throw, photos to be taken or etc
        if script_to_ask.endswith('sh'):
            return ("Sorry, .sh files don't support help arguments, try viewing it instead.")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(str(script_to_ask) + " -h")
        return out
    def show_help(self, e):
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        helpfile = self.get_help_text(str(script_path + script_name))
        msg_text =  script_name + ' \n \n'
        msg_text += str(helpfile)
        dbox = show_script_cat(None, helpfile, script_name + " help info")
        dbox.ShowModal()
        dbox.Destroy()
    def do_upload(self, e):
        #get data from boxes
        #   these are the exit variables, they're only set when ok is pushed
        #   this is to stop any dirty old data mixing in with the correct stuff
        self.job_type = self.cron_type_combo.GetValue()
        self.job_path = self.cron_path_combo.GetValue()
        self.job_script = self.cron_script_cb.GetValue()
        self.job_args = self.cron_args_tc.GetValue()
        self.job_comment = self.cron_comment_tc.GetValue()
        self.job_enabled = self.cron_enabled_cb.GetValue()
        self.job_repeat = self.cron_repeat_opts_cb.GetValue()
        self.job_repnum = self.cron_every_num_tc.GetValue()
        self.job_min = self.cron_timed_min_tc.GetValue()
        self.job_hour = self.cron_timed_hour_tc.GetValue()
        self.job_day = self.cron_timed_day_tc.GetValue()
        self.job_month = self.cron_timed_month_tc.GetValue()
        self.job_dow = self.cron_timed_dow_tc.GetValue()
        self.Destroy()
    def OnClose(self, e):
        #set all post-creation flags to zero
        #   this is so that it doesn't ever somehow confuse old dirty data
        #   with new correct data, stuff comes in one side and leaves the other.
        self.job_type = None
        self.job_path = None
        self.job_script = None
        self.job_args = None
        self.job_comment = None
        self.job_enabled = None
        self.job_repeat = None
        self.job_repnum = None
        self.job_min = None
        self.job_hour = None
        self.job_day = None
        self.job_month = None
        self.job_dow = None
        self.Destroy()

class show_script_cat(wx.Dialog):
    def __init__(self, parent,  text_to_show, script_title):
        wx.Dialog.__init__(self, parent, title=("Script " + script_title))
        text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer = wx.BoxSizer(wx.VERTICAL )
        btnsizer = wx.BoxSizer()
        btn = wx.Button(self, wx.ID_OK)
        btnsizer.Add(btn, 0, wx.ALL, 5)
        btnsizer.Add((5,-1), 0, wx.ALL, 5)
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.Add(btn, 0, wx.ALL, 5)
        sizer.Add(text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALL, 5)
        self.SetSizerAndFit(sizer)

#
#
#
## Local Files tab
#
#
#
class localfiles_info_pnl(scrolled.ScrolledPanel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.HSCROLL|wx.VSCROLL)
        #set blank variables
        localfiles_info_pnl.local_path = ""
        # top title
        page_title =  wx.StaticText(self,  label='Local Files', size=(300,40))
        page_sub_title =  wx.StaticText(self,  label='Files downloaded from the pi and stored locally', size=(550,30))
        page_title.SetFont(shared_data.title_font)
        page_sub_title.SetFont(shared_data.sub_title_font)
        # placing the information boxes
        local_path_l =  wx.StaticText(self,  label='Local Path -', size=(135, 25))
        local_path_l.SetFont(shared_data.item_title_font)
        localfiles_info_pnl.local_path_txt = wx.StaticText(self,  label='local path')
        #local photo storage info
        photo_l = wx.StaticText(self,  label='Photos', size=(75,25))
        photo_l.SetFont(shared_data.item_title_font)
        caps_folder_l = wx.StaticText(self,  label='Caps Folder;')
        localfiles_info_pnl.caps_folder = 'caps'
        localfiles_info_pnl.folder_text = wx.StaticText(self,  label=localfiles_info_pnl.caps_folder)
        localfiles_info_pnl.set_caps_folder_btn = wx.Button(self, label='...')
        localfiles_info_pnl.set_caps_folder_btn.Bind(wx.EVT_BUTTON, self.set_caps_folder_click)
        localfiles_info_pnl.photo_text = wx.StaticText(self,  label='photo text')
        localfiles_info_pnl.first_photo_title = wx.StaticText(self,  label='first image')
        blank_img = wx.Bitmap(255, 255)
        localfiles_info_pnl.photo_folder_first_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        localfiles_info_pnl.photo_folder_first_pic.Bind(wx.EVT_BUTTON, self.first_img_click)
        localfiles_info_pnl.last_photo_title = wx.StaticText(self,  label='last image')
        localfiles_info_pnl.photo_folder_last_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        localfiles_info_pnl.photo_folder_last_pic.Bind(wx.EVT_BUTTON, self.last_img_click)
        #file list boxes
        config_l = wx.StaticText(self,  label='Config', size=(75,25))
        config_l.SetFont(shared_data.item_title_font)
        localfiles_info_pnl.config_files = self.config_file_list(self, 1)
        localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        logs_l = wx.StaticText(self,  label='Logs', size=(75,25))
        logs_l.SetFont(shared_data.item_title_font)
        localfiles_info_pnl.logs_files = self.logs_file_list(self, 1)
        localfiles_info_pnl.logs_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_logs)
        #localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
    #    localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        #cron info text
        cron_l = wx.StaticText(self,  label='Cron', size=(75,25))
        cron_l.SetFont(shared_data.item_title_font)
        localfiles_info_pnl.cron_info = wx.StaticText(self,  label='cron info')

        #Sizers
        # full row sizers
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 3)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 3)
        local_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_path_sizer.Add(local_path_l, 0, wx.ALL, 3)
        local_path_sizer.Add(localfiles_info_pnl.local_path_txt, 1, wx.ALL|wx.EXPAND, 3)
        # camera bar sizers
        photos_sizer = wx.BoxSizer(wx.VERTICAL)
        photos_sizer.Add(photo_l, 0, wx.ALL, 3)
        caps_folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        caps_folder_sizer.Add(caps_folder_l, 0, wx.ALL, 3)
        caps_folder_sizer.Add(localfiles_info_pnl.folder_text, 0, wx.ALL|wx.EXPAND, 3)
        caps_folder_sizer.Add(localfiles_info_pnl.set_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 3)
        photos_sizer.Add(caps_folder_sizer, 0, wx.ALL, 3)
    #    photos_sizer.AddStretchSpacer(1)
        photos_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        photos_sizer.Add(localfiles_info_pnl.photo_text, 0, wx.ALL|wx.EXPAND, 3)
    #    photos_sizer.AddStretchSpacer(1)
        photos_sizer.Add(localfiles_info_pnl.first_photo_title, 0, wx.ALL|wx.EXPAND, 2)
        photos_sizer.Add(localfiles_info_pnl.photo_folder_first_pic, 1, wx.ALL|wx.EXPAND, 3)
    #    photos_sizer.AddStretchSpacer(1)
        photos_sizer.Add(localfiles_info_pnl.last_photo_title, 0, wx.ALL|wx.EXPAND, 2)
        photos_sizer.Add(localfiles_info_pnl.photo_folder_last_pic, 1, wx.ALL|wx.EXPAND, 3)
    #    photos_sizer.AddStretchSpacer(1)
        # tables bar sizer
        tables_sizer = wx.BoxSizer(wx.VERTICAL)
        tables_sizer.Add(config_l, 0, wx.ALL, 3)
        tables_sizer.Add(localfiles_info_pnl.config_files, 1, wx.ALL|wx.EXPAND, 3)
        #tables_sizer.AddStretchSpacer(1)
        tables_sizer.Add(logs_l, 0, wx.ALL, 3)
        tables_sizer.Add(localfiles_info_pnl.logs_files, 1, wx.ALL|wx.EXPAND, 3)
        #tables_sizer.AddStretchSpacer(1)
        tables_sizer.Add(cron_l, 0, wx.ALL, 3)
        tables_sizer.Add(localfiles_info_pnl.cron_info, 1, wx.ALL|wx.EXPAND, 3)
    #    tables_sizer.AddStretchSpacer(1)

        main_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_area_sizer.Add(tables_sizer, 0, wx.ALL, 3)
        main_area_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        main_area_sizer.Add(photos_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(local_path_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(main_area_sizer, 0, wx.ALL|wx.EXPAND, 3)
        # panel set up
        self.SetSizer(main_sizer)
        self.SetupScrolling()

    def set_caps_folder_click(self, e):
        msg = "Input the name of the directory to download images from,\n\nThe folder will be located in the root of the Pigrow folder and have the same name in the frompigrow folder locally"
        msg += "\n\nThis will not affect where images are saved by the capture scripts."
        new_caps_path_dialog = wx.TextEntryDialog(self, msg, "Image Capture Folder", "caps")
        if new_caps_path_dialog.ShowModal() == wx.ID_OK:
            new_caps_folder = new_caps_path_dialog.GetValue()

        localfiles_info_pnl.folder_text.SetLabel(new_caps_folder)
        localfiles_info_pnl.caps_folder = new_caps_folder
        MainApp.localfiles_ctrl_pannel.update_local_filelist_click("e")



    def first_img_click(self, e):
        first = wx.Image(self.first_image_path, wx.BITMAP_TYPE_ANY)
        first = first.ConvertToBitmap()
        dbox = show_image_dialog(None, first, "First image")
        dbox.ShowModal()
        dbox.Destroy()

    def last_img_click(self, e):
        last = wx.Image(self.final_image_path, wx.BITMAP_TYPE_ANY)
        last = last.ConvertToBitmap()
        dbox = show_image_dialog(None, last, "Most recent image")
        dbox.ShowModal()
        dbox.Destroy()

    class config_file_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(25, 250), size=(550,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.SetColumnWidth(0, 190)
            self.SetColumnWidth(1, 150)
            self.SetColumnWidth(2, 110)
            self.SetColumnWidth(3, 100)

    class logs_file_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(25, 500), size=(550,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.SetColumnWidth(0, 190)
            self.SetColumnWidth(1, 150)
            self.SetColumnWidth(2, 110)
            self.SetColumnWidth(3, 100)

    def draw_photo_folder_images(self, first_pic, last_pic):
        # load and display first image
        try:
            first = wx.Image(first_pic, wx.BITMAP_TYPE_ANY)
            first = scale_pic(first, 300)
            first = first.ConvertToBitmap()
            localfiles_info_pnl.photo_folder_first_pic.SetBitmap(first)
        except:
            print("!! First image in local caps folder didn't work.")
        # load and display last image
        try:
            last = wx.Image(last_pic, wx.BITMAP_TYPE_ANY)
            last = scale_pic(last, 300)
            last = last.ConvertToBitmap()
            localfiles_info_pnl.photo_folder_last_pic.SetBitmap(last)
        except:
            print("!! Last image in local caps folder didn't work.")

    def add_to_config_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.config_files.InsertItem(0, str(name))
        localfiles_info_pnl.config_files.SetItem(0, 1, str(mod_date))
        localfiles_info_pnl.config_files.SetItem(0, 2, str(age))
        localfiles_info_pnl.config_files.SetItem(0, 3, str(update_status))

    def add_to_logs_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.logs_files.InsertItem(0, str(name))
        localfiles_info_pnl.logs_files.SetItem(0, 1, str(mod_date))
        localfiles_info_pnl.logs_files.SetItem(0, 2, str(age))
        localfiles_info_pnl.logs_files.SetItem(0, 3, str(update_status))

    def onDoubleClick_config(self, e):
        index =  e.GetIndex()
        filename = localfiles_info_pnl.config_files.GetItem(index, 0).GetText()
        file_path = os.path.join(localfiles_info_pnl.local_path, "config", filename)
        with open(file_path, "r") as config_file:
            config_file_text = config_file.read()
        dbox = scroll_text_dialog(None, config_file_text, "Editing " + filename, True, False)
        dbox.ShowModal()
        if scroll_text_dialog.text == None:
            #print("User aborted")
            return None
        else:
            if not scroll_text_dialog.text == config_file_text:
                #print(scroll_text_dialog.text)
                question_text = "Save changes to config file?"
                dbox = wx.MessageDialog(self, question_text, "Save Changes?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                if (answer == wx.ID_OK):
                    with open(file_path, "w") as config_file:
                        config_file.write(scroll_text_dialog.text)
                    print(" Config file " + filename + " changes saved")
            else:
                #print("Config file unchanged")
                return None

    def onDoubleClick_logs(self, e):
        print("sry nothing happens - this will be added soon")

class localfiles_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        tab_label = wx.StaticText(self,  label='Local file and backup options',)
        self.update_local_filelist_btn = wx.Button(self, label='Refresh Filelist Info')
        self.update_local_filelist_btn.Bind(wx.EVT_BUTTON, self.update_local_filelist_click)
        self.download_btn = wx.Button(self, label='Download files')
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)
        self.upload_btn = wx.Button(self, label='Restore to pi')
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)
        self.clear_downed_btn = wx.Button(self, label='clear downloaded\n photos from pigrow')
        self.clear_downed_btn.Bind(wx.EVT_BUTTON, self.clear_downed_click)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(tab_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_local_filelist_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.download_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.clear_downed_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.upload_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def clear_downed_click(self, e):
        # looks at local files an remote files removing any from the pigrows
        # that are already stored in the local caps folder for that pigrow
        print("clearing already downloaded images off pigrow")
        caps_path = os.path.join(localfiles_info_pnl.local_path, localfiles_info_pnl.caps_folder)
        caps_files = os.listdir(caps_path)
        print("---------")
        print(caps_path)
        print(len(caps_files))
        print("-----")
        caps_files.sort()
        print(str(len(caps_files)) + " files locally \n")
        #read pi's caps folder
        try:
            pi_caps_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/" + localfiles_info_pnl.caps_folder
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls " + pi_caps_path)
            remote_caps = out.splitlines()
            print(len(remote_caps))
            print("-------------------")
        except Exception as e:
            print(("-- reading remote caps folder failed; " + str(e)))
            remote_caps = []
        count = 0
        for the_remote_file in remote_caps:
            if the_remote_file in caps_files:
                the_remote_file = pi_caps_path + "/" + the_remote_file
                MainApp.status.write_bar("clearing - " + the_remote_file)
                MainApp.localfiles_ctrl_pannel.run_on_pi("rm " + the_remote_file, False)
                wx.GetApp().Yield()
                count = count + 1
            MainApp.status.write_bar("Cleared " + str(count) + " files from the pigrow")
        # when done refreh the file info
        self.update_local_filelist_click("e")

    def run_on_pi(self, command, write_status=True):
        #Runs a command on the pigrow and returns output and error
        #  out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        if write_status == True:
            MainApp.status.write_blue_bar("Running; " + command)
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            out = stdout.read()
            error = stderr.read()
            out = out.decode()
            error = error.decode()
            if write_status == True:
                MainApp.status.write_bar("ready...")
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            if write_status == True:
                MainApp.status.write_warning("FAILED: Check your connection")
            return "", error
        return out, error

    def update_local_filelist_click(self, e):
        print("looking for local files.")
        # clear lists
        localfiles_info_pnl.config_files.DeleteAllItems()
        localfiles_info_pnl.logs_files.DeleteAllItems()
        # create local folder path
        localfiles_info_pnl.local_path = os.path.join(MainApp.localfiles_path, str(pi_link_pnl.boxname))
        localfiles_info_pnl.local_path_txt.SetLabel(localfiles_info_pnl.local_path)
        # check for data and sort into on screen lists
        if not os.path.isdir(localfiles_info_pnl.local_path):
            localfiles_info_pnl.local_path_txt.SetLabel(localfiles_info_pnl.local_path)
        else:
            local_files = os.listdir(localfiles_info_pnl.local_path)
            #set caps folder
            localfiles_info_pnl.folder_text.SetLabel(localfiles_info_pnl.caps_folder)
            #define empty lists
            folder_list = []
            #read all the folders in the pigrows local folder
            for item in local_files:
                item_path = os.path.join(localfiles_info_pnl.local_path, item)
                if os.path.isdir(item_path) == True:
                    folder_files = os.listdir(item_path)
                    counter = 0
                    for thing in folder_files:
                        counter = counter + 1
                    folder_list.append([item, counter])
                    #add local config files to list and generate info
                    if item == "config":
                        config_list = []
                        config_files = os.listdir(item_path)
                        for thing in config_files:
                            if thing.endswith("txt"):
                                thing_path = os.path.join(item_path, thing)
                                modified = os.path.getmtime(thing_path)
                                #config_list.append([thing, modified])
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_config_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    if item == "logs":
                        logs_list = []
                        logs_files = os.listdir(item_path)
                        for thing in logs_files:
                            if thing.endswith("txt"):
                                thing_path = os.path.join(item_path, thing)
                                modified = os.path.getmtime(thing_path)
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_logs_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    #read caps info and make report
                    if item == localfiles_info_pnl.caps_folder:
                        caps_files = os.listdir(item_path)
                        #print("---------")
                        #print(str(item_path))
                        #print(caps_files)
                        #print("-----------")
                        caps_files.sort()
                        caps_message = str(len(caps_files)) + " files locally \n"
                        #read pi's caps folder
                        try:
                            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/" + localfiles_info_pnl.caps_folder)
                            remote_caps = out.splitlines()
                        except Exception as e:
                            print(("-- reading remote caps folder failed; " + str(e)))
                            remote_caps = []
                        if len(remote_caps) > 1:
                            for file in remote_caps:
                                if ".jpg" in file:
                                    first_r_img_file = file
                                    break
                            for file in reversed(remote_caps):
                                if ".jpg" in file:
                                    last_r_img_file = file
                                    break
                        # local caps files
                        if len(caps_files) > 1:
                            for file in caps_files:
                                if ".jpg" in file:
                                    first_img_file = file
                                    break
                            for file in reversed(caps_files):
                                if ".jpg" in file:
                                    last_img_file = file
                                    break
                            #lable first and last image with name
                            localfiles_info_pnl.first_photo_title.SetLabel(first_img_file)
                            localfiles_info_pnl.last_photo_title.SetLabel(last_img_file)
                            #determine date range of images

                            first_date, first_dt = self.filename_to_date(first_img_file)
                            last_date, last_dt = self.filename_to_date(last_img_file)
                            if not last_dt == None and not first_dt == None:
                                caps_message += "  " + str(first_date) + " - " + str(last_date)
                                length_of_local = last_dt - first_dt
                                caps_message += '\n     ' + str(length_of_local)
                            #draw first and last imagess to the screen
                            localfiles_info_pnl.first_image_path = os.path.join(item_path, first_img_file)
                            localfiles_info_pnl.final_image_path = os.path.join(item_path, last_img_file)
                            localfiles_info_pnl.draw_photo_folder_images(MainApp.localfiles_info_pannel, localfiles_info_pnl.first_image_path, localfiles_info_pnl.final_image_path)
                        caps_message += "\n" + str(len(remote_caps)) + " files on Pigrow \n"
                        # remote image files
                        if len(remote_caps) > 1:
                            try:
                                first_remote, first_r_dt = self.filename_to_date(first_r_img_file)
                            except:
                                first_remote = "error"
                                first_r_dt = None
                            try:
                                last_remote, last_r_dt = self.filename_to_date(last_r_img_file)
                            except:
                                last_remote = "error"
                                last_r_dt = None
                            caps_message += "  " + str(first_remote) + " - " + str(last_remote)
                            if not last_r_dt == None:
                                if not first_r_dt == None:
                                    length_of_remote = last_r_dt - first_r_dt
                                    caps_message += '\n     ' + str(length_of_remote)
                        else:
                            caps_message += " "

                        #update the caps info pannel with caps message
                        localfiles_info_pnl.photo_text.SetLabel(caps_message)
                        MainApp.window_self.Layout()


            # check to see if crontab is saved locally
            localfiles_ctrl_pnl.cron_backup_file = os.path.join(localfiles_info_pnl.local_path, "crontab_backup.txt")
            if os.path.isfile(localfiles_ctrl_pnl.cron_backup_file) == True:
                #checks time of local crontab_backup and determines age
                modified = os.path.getmtime(localfiles_ctrl_pnl.cron_backup_file)
                modified = datetime.datetime.fromtimestamp(modified)
                file_age = datetime.datetime.now() - modified
                modified = modified.strftime("%Y-%m-%d %H:%M")
                file_age = str(file_age).split(".")[0]
                #checks to see if local and remote files are the same
                remote_cron_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab -l")
                #read local file
                with open(localfiles_ctrl_pnl.cron_backup_file, "r") as local_cron:
                    local_cron_text = local_cron.read()
                #compare the two files
                if remote_cron_text == local_cron_text:
                    updated = True
                else:
                    updated = False
                cron_msg = "local cron file last updated\n    " + modified + "\n    " + file_age + " ago,\n  \n\n identical to pi version: " + str(updated)
                localfiles_info_pnl.cron_info.SetLabel(cron_msg)
            else:
                localfiles_info_pnl.cron_info.SetLabel("no local cron file")
                ## output
        print("local file info discovered..")

    def filename_to_date(self, filename):
        #
        # DOUBLE! this is also in timelapse tab so pick one and use that one only!
        #
        if "_" in filename:
            try:
                date = float(filename.split(".")[0].split("_")[-1])
                file_datetime = datetime.datetime.fromtimestamp(date)
                text_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(date))
                return text_date, file_datetime
            except:
                print("!! tried to parse from a unix datetime but failed " + str(filename))
                return None, None
        elif "-" in filename:
            try:
                date = filename.split("-")[1]
                # 10-2018 05 05 20 12 12-03
                file_datetime = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                text_date = file_datetime.strftime('%Y-%m-%d %H:%M')
                return text_date, file_datetime
            except:
                print("!! Tried to parse filename as Motion date but failed " + str(filename))
                return None, None
        else:
            return None, None

    def download_click(self, e):
        #show download dialog boxes
        file_dbox = file_download_dialog(None, title='Download dialog box')
        file_dbox.ShowModal()
        self.update_local_filelist_click("e")

    def upload_click(self, e):
        upload_dbox = upload_dialog(None, title='Upload dialog box')
        upload_dbox.ShowModal()
        self.update_local_filelist_click("e")

    def download_file_to_folder(self, remote_file, local_name):
        #
        # this downloads a single file into the pi's local folder
        # localfiles_ctrl_pnl.download_file_to_folder(remote_file, local_name)
        #
        local_base_path = localfiles_info_pnl.local_path_txt.GetLabel()
        if local_name[0] == "/":
            local_name = local_name[1:]
        #print (" -- local base path -- " + local_base_path)
        local_path = os.path.join(local_base_path, local_name)
        #print (" -- local path -- " + local_path)
        without_filename = os.path.split(local_path)[0]
        #print (" -- without_filename -- " + str(without_filename))
        if not os.path.isdir(without_filename):
            os.makedirs(without_filename)
            #print("made folder " + str(without_filename))
        port = shared_data.ssh_port
        print("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        print("    to  download " + remote_file + " to " + local_path)
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        self.sftp.get(remote_file, local_path)
        self.sftp.close()
        ssh_tran.close()
        print(("    file copied to " + str(local_path)))
        return local_path

    def upload_file_to_folder(self, local_path, remote_path):
        # Copies a folder from the local machine onto the pigrow
        # local_path and remote_path should be full and explicit paths
        port = shared_data.ssh_port
        print(("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port)))
        print(("    to  upload " + local_path + " to " + remote_path))
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        self.sftp.put(local_path, remote_path)
        self.sftp.close()
        ssh_tran.close()
        print((" file copied to " + str(remote_path)))

    def save_text_to_file_on_pi(self, file_location, text):
        sftp = ssh.open_sftp()
        f = sftp.open(file_location, 'w')
        f.write(text)
        f.close()

class file_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(file_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 400))
        self.SetTitle("Download files from Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #draw the pannel
        wx.StaticText(self,  label='Select elements to download to local storage', pos=(30, 5))
        self.cb_conf = wx.CheckBox(self, label='Config',pos = (80,30))
        self.cb_logs = wx.CheckBox(self, label='Logs',pos = (80,55))
        self.cb_cron = wx.CheckBox(self, label='Crontab',pos = (80,80))
        self.cb_pics = wx.CheckBox(self, label='Photos',pos = (80,105))
        self.cb_graph = wx.CheckBox(self, label='Graphs',pos = (80,130))
        #right side
        self.cb_all = wx.CheckBox(self, label='Back up\nWhole Pigrow Folder',pos = (270,75))
        #progress bar
        wx.StaticText(self,  label='saving to; '+ localfiles_info_pnl.local_path, pos=(15, 155))
        self.current_file_txt = wx.StaticText(self,  label='--', pos=(30, 190))
        self.current_dest_txt = wx.StaticText(self,  label='--', pos=(30, 215))
        #buttons
        self.start_download_btn = wx.Button(self, label='Download files', pos=(40, 240), size=(175, 50))
        self.start_download_btn.Bind(wx.EVT_BUTTON, self.start_download_click)
        self.close_btn = wx.Button(self, label='Close', pos=(250, 240), size=(175, 50))
        self.close_btn.Bind(wx.EVT_BUTTON, self.OnClose)
         ## universal controls
        pnl = wx.Panel(self)

    def start_download_click(self, e):
        #make folder if it doesn't exist
        if not os.path.isdir(localfiles_info_pnl.local_path):
            os.makedirs(localfiles_info_pnl.local_path)
        #make empty lists
        files_to_download = []
        # downloading cron file and saving it as a local backup
        if self.cb_cron.GetValue() == True:
            print("including crontab file")
            cron_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab -l")
            if not os.path.isdir(localfiles_info_pnl.local_path):
                os.makedirs(localfiles_info_pnl.local_path)
            localfiles_ctrl_pnl.cron_backup_file = os.path.join(localfiles_info_pnl.local_path, "crontab_backup.txt")
            with open(localfiles_ctrl_pnl.cron_backup_file, "w") as file_to_save:
                file_to_save.write(cron_text)
        ## Downloading files from the pi
        # connecting the sftp pipe
        port = shared_data.ssh_port
        if not len(pi_link_pnl.target_ip.split(".")) == 4:
            import socket
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((pi_link_pnl.target_ip, port))
            ssh_tran = paramiko.Transport(sock=sock)
        else:
            ssh_tran = paramiko.Transport(pi_link_pnl.target_ip, port)

        print(("#sb#  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port)))
        MainApp.status.write_bar("connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        # creating a list of files to be download from the pigrow
        if self.cb_all.GetValue() == False:
        # make list using selected components to be downloaded, list contains two elemnts [remote file, local destination]
            # list config files for download
            if self.cb_conf.GetValue() == True:
                #local_config = localfiles_info_pnl.local_path + "config/"
                local_config = os.path.join(localfiles_info_pnl.local_path, "config/")
                if not os.path.isdir(local_config):
                    os.makedirs(local_config)
                target_config_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                remote_config = self.sftp.listdir(target_config_files)
                for item in remote_config:
                    files_to_download.append([target_config_files + item, local_config + item])
            # List logs files  for download
            if self.cb_logs.GetValue() == True:
                #local_logs = localfiles_info_pnl.local_path + "logs/"
                local_logs = os.path.join(localfiles_info_pnl.local_path, "logs")
                if not os.path.isdir(local_logs):
                    os.makedirs(local_logs)
                target_logs_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                remote_logs = self.sftp.listdir(target_logs_files)
                for item in remote_logs:
                    local_log_item = os.path.join(local_logs, item)
                    files_to_download.append([target_logs_files + item, local_log_item])
            # list caps files for download
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                #local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                local_pics = os.path.join(localfiles_info_pnl.local_path, caps_folder)
                if not os.path.isdir(local_pics):
                    os.makedirs(local_pics)
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                try:
                    remote_caps = self.sftp.listdir(target_caps_files)
                except IOError as e:
                    if "No such file" in str(e):
                        remote_caps = []
                    else:
                        print(("Error downloadig files - " + str(e)))
                for item in remote_caps:
                    if item not in listofcaps_local:
                        item_path = os.path.join(local_pics, item)
                        files_to_download.append([target_caps_files + item, item_path])
            # list graphs for download
            if self.cb_graph.GetValue() == True:
                target_graph_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                #local_graphs = localfiles_info_pnl.local_path + "graphs/"
                local_graphs = os.path.join(localfiles_info_pnl.local_path, "graphs")
                if not os.path.isdir(local_graphs):
                    os.makedirs(local_graphs)
                try:
                    remote_graphs = self.sftp.listdir(target_graph_files)
                except IOError as e:
                    if "No such file" in str(e):
                        remote_graphs = []
                    else:
                        print(("Error downloadig files - " + str(e)))
                for item in remote_graphs:
                    location_local_graph = os.path.join(local_graphs, item)
                    files_to_download.append([target_graph_files + item, location_local_graph])
        else:
            # this is when the backup checkbox is ticked
            folder_name = "/Pigrow" #start with / but don't end with one.
            target_folder = "/home/" + str(pi_link_pnl.target_user) + folder_name
            #local_folder = localfiles_info_pnl.local_path + "backup"
            local_folder = os.path.join(localfiles_info_pnl.local_path, "backup")
            if not os.path.isdir(local_folder):
                os.makedirs(local_folder)
            folders, files = self.sort_folder_for_folders(target_folder)
            while len(folders) > 0:
                if not ".git" in folders[0]:
                    new_folders, new_files = self.sort_folder_for_folders(folders[0])
                    files = files + new_files
                    folders = folders + new_folders
                    new_folder = local_folder + "/" + folders[0].split(folder_name + "/")[1]
                    print (new_folder)
                    if not os.path.isdir(new_folder):
                        os.makedirs(new_folder)
                folders = folders[1:]

            for item in files:
                filename = item[len(target_folder):]
                files_to_download.append([item, local_folder + filename])
            #
            print("downloading entire pigrow folder")
        # Work though the list of files to download
        print("downloading; " + str(len(files_to_download)))
        for remote_file in files_to_download:
            #grabs all files in the list and overwrites them if they already exist locally.
            self.current_file_txt.SetLabel("from; " + remote_file[0])
            self.current_dest_txt.SetLabel("to; " + remote_file[1])
            wx.GetApp().Yield() #update screen to show changes
            try:
                self.sftp.get(remote_file[0], remote_file[1])
            except:
                print(" - couldn't download " + remote_file[0] + " probably a folder or something.")
        self.current_file_txt.SetLabel("Done")
        self.current_dest_txt.SetLabel("Downloaded " + str(len(files_to_download)) + " files")
        #disconnect the sftp pipe
        self.sftp.close()
        ssh_tran.close()
        MainApp.status.write_bar("closed transport pipe")

    def sort_folder_for_folders(self, target_folder):
        folders = []
        files = []
        for f in self.sftp.listdir_attr(target_folder):
            if S_ISDIR(f.st_mode):
                folders.append(str(target_folder + '/' + f.filename))
            else:
                files.append(str(target_folder + '/' + f.filename))
        return folders, files

    def OnClose(self, e):
        #closes the dialogue box
        self.Destroy()

class upload_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(upload_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 455))
        self.SetTitle("upload files to Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #draw the pannel
        wx.StaticText(self,  label='Select elements to upload from local storage to pi\n\n   ** Warning this will overwrite current pigrow files \n                          which may result in loss of data **', pos=(30, 5))
        self.cb_conf = wx.CheckBox(self, label='Config',pos = (80,90))
        self.cb_logs = wx.CheckBox(self, label='Logs',pos = (80,115))
        self.cb_cron = wx.CheckBox(self, label='Crontab',pos = (80,140))
        self.cb_pics = wx.CheckBox(self, label='Photos',pos = (80,165))
        self.cb_graph = wx.CheckBox(self, label='Graphs',pos = (80,190))
        #right side
        self.cb_all = wx.CheckBox(self, label='Restore Back up\nof whole Pigrow Folder',pos = (270,130))
        #progress bar
        wx.StaticText(self,  label='uploading from; '+ localfiles_info_pnl.local_path, pos=(15, 215))
        self.current_file_txt = wx.StaticText(self,  label='--', pos=(30, 245))
        self.current_dest_txt = wx.StaticText(self,  label='--', pos=(30, 270))
        #buttons
        self.start_upload_btn = wx.Button(self, label='Upload files', pos=(40, 300), size=(175, 50))
        self.start_upload_btn.Bind(wx.EVT_BUTTON, self.start_upload_click)
        self.close_btn = wx.Button(self, label='Close', pos=(300, 300), size=(175, 50))
        self.close_btn.Bind(wx.EVT_BUTTON, self.OnClose)
         ## universal controls
        pnl = wx.Panel(self)

    def start_upload_click(self, e):
        files_to_upload  = []
        ## connecting the sftp pipe
        port = shared_data.ssh_port
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        print(("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port)))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        ## uploading to the pi
        # creating a list of files to be uploaded
        if self.cb_all.GetValue() == False:
            # uploading and installing cron file
            temp_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/temp/"
            cron_temp = temp_folder + "cron.txt"
            if self.cb_cron.GetValue() == True:
                print("including crontab file")
                #upload cronfile to temp folder
                try:
                    sftp.put(localfiles_ctrl_pnl.cron_backup_file, cron_temp)
                except IOError:
                    sftp.mkdir(temp_folder)
                    sftp.put(localfiles_ctrl_pnl.cron_backup_file, cron_temp)
                self.current_file_txt.SetLabel("from; " + localfiles_ctrl_pnl.cron_backup_file)
                self.current_dest_txt.SetLabel("to; " + cron_temp)
                wx.GetApp().Yield()
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("crontab " + cron_temp)
        # make list using selected components to be uploaded, list contains two elemnts [local file, remote destination]
            if self.cb_conf.GetValue() == True:
                #local_config = localfiles_info_pnl.local_path + "config/"
                local_config = os.path.join(localfiles_info_pnl.local_path, "config")
                target_config = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                local_config_files = os.listdir(local_config)
                for item in local_config_files:
                    local_item_path = os.path.join(local_config, item)
                    files_to_upload.append([local_item_path, target_config + item])
            #do the same for the logs folder
            if self.cb_logs.GetValue() == True:
                #local_logs = localfiles_info_pnl.local_path + "logs/"
                local_logs = os.path.join(localfiles_info_pnl.local_path, "logs")
                target_logs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                target_logs_files = os.listdir(local_logs)
                for item in target_logs_files:
                    local_item_path = os.path.join(local_logs, item)
                    files_to_upload.append([local_item_path, target_logs + item])
            #and the graphs folder
            if self.cb_graph.GetValue() == True:
                #local_graphs = localfiles_info_pnl.local_path + "graphs/"
                local_graphs = os.path.join(localfiles_info_pnl.local_path, "graphs")
                target_graphs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                local_graph_files = os.listdir(local_graphs)
                for item in local_graph_files:
                    local_item_path = os.path.join(local_graphs, item)
                    files_to_upload.append([local_item_path, target_graphs + item])
            ## for photos only upload photos that don't already exost on pi
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                #local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                local_pics = os.path.join(localfiles_info_pnl.local_path, caps_folder)
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                remote_caps = sftp.listdir(target_caps_files)
                for item in listofcaps_local:
                    if item not in remote_caps:
                        local_pic_path = os.path.join(local_pics, item)
                        files_to_upload.append([local_pic_path, target_caps_files + item])
        else:
            # make list of all ~/Pigrow/ files using os.walk
            #    - this is for complete backups ignoring the file system.
            print("restoring entire pigrow folder (not yet implimented)")
        for upload_file in files_to_upload:
            #grabs all files in the list and overwrites them if they already exist locally.
            self.current_file_txt.SetLabel("from; " + upload_file[0])
            self.current_dest_txt.SetLabel("to; " + upload_file[1])
            wx.GetApp().Yield()
            sftp.put(upload_file[0], upload_file[1])
        self.current_file_txt.SetLabel("Done")
        self.current_dest_txt.SetLabel("--")
        #disconnect the sftp pipe
        sftp.close()
        ssh_tran.close()


    def OnClose(self, e):
        #closes the dialogue box
        self.Destroy()

#
#
#
## Graphing Tab
#
#
#

class graphing_info_pnl(scrolled.ScrolledPanel):
    #
    #  This displays the graphing info
    # controlled by the graphing_ctrl_pnl
    #
    def __init__( self, parent ):
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.HSCROLL|wx.VSCROLL )

        ## Draw UI elements
        self.graph_txt = wx.StaticText(self,  label='Graphs;', size=(80, 30))
        self.graphs_clear_btn = wx.Button(self, label='clear', size=(55,27))
        self.graphs_clear_btn.Bind(wx.EVT_BUTTON, MainApp.graphing_ctrl_pannel.clear_graph_area)
        self.graph_txt.SetFont(shared_data.sub_title_font)
        # for local graphing
        self.data_extraction_l = wx.StaticText(self,  label='Data Extraction Options')
        self.data_extraction_l.SetFont(shared_data.sub_title_font)
        self.show_hide_date_extract_btn = wx.Button(self, label='hide')
        self.show_hide_date_extract_btn.Bind(wx.EVT_BUTTON, self.show_hide_date_extract_click)
        self.save_data_extract_btn = wx.Button(self, label='Save')
        self.save_data_extract_btn.Bind(wx.EVT_BUTTON, MainApp.graphing_ctrl_pannel.save_data_extract_click)
        self.example_line_l = wx.StaticText(self,  label='Example Line -')
        self.example_line = wx.StaticText(self,  label='')
        # this bit copied from timelapse make overlay dialogs
        # split line character
        self.split_character_l = wx.StaticText(self,  label='Split Character')
        self.split_character_tc = wx.TextCtrl(self, size=(90, 25))
        self.split_character_tc.Bind(wx.EVT_TEXT, self.split_line_text)
        # row of date related options
        self.date_pos_l = wx.StaticText(self,  label='Date Position')
        self.date_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.date_pos_cb.Bind(wx.EVT_TEXT, self.date_pos_go)
        self.date_pos_cb.Disable()
        self.date_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.date_pos_split_tc.Bind(wx.EVT_TEXT, self.date_pos_split_text)
        self.date_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.date_pos_split_cb.Bind(wx.EVT_TEXT, self.date_pos_split_select)
        self.date_pos_ex = wx.StaticText(self,  label='')
        # row of value related options
        self.value_pos_l = wx.StaticText(self,  label='Value Position')
        self.value_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.value_pos_cb.Bind(wx.EVT_TEXT, self.value_pos_go)
        self.value_pos_cb.Disable()
        self.value_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.value_pos_split_tc.Bind(wx.EVT_TEXT, self.value_pos_split_text)
        self.value_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.value_pos_split_cb.Bind(wx.EVT_TEXT, self.value_pos_split_go)
        self.value_pos_ex = wx.StaticText(self,  label='')
        self.rem_from_val_l = wx.StaticText(self,  label='Remove from Value -')
        self.rem_from_val_tc = wx.TextCtrl(self, size=(150, 25))
        # row of key related options
        self.key_pos_l = wx.StaticText(self,  label='Key Position')
        self.key_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.key_pos_cb.Bind(wx.EVT_TEXT, self.key_pos_go)
        self.key_pos_cb.Disable()
        self.key_manual_l = wx.StaticText(self,  label='Label -')
        self.key_manual_tc = wx.TextCtrl(self, size=(150, 25))
        self.key_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.key_pos_split_tc.Bind(wx.EVT_TEXT, self.key_pos_split_text)
        self.key_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.key_pos_split_cb.Bind(wx.EVT_TEXT, self.key_pos_split_go)
        self.key_pos_ex = wx.StaticText(self,  label='')
        self.key_matches_l = wx.StaticText(self,  label='Limit to Key Containing -')
        self.key_matches_tc = wx.TextCtrl(self, size=(150, 25))
        # data extract sizer grid
        split_chr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        split_chr_sizer.Add(self.split_character_l, 0,  wx.ALL, 3)
        split_chr_sizer.Add(self.split_character_tc, 0,  wx.ALL, 3)
        data_extract_pos_sizer = wx.GridSizer(3, 5, 0, 0)
        data_extract_pos_sizer.AddMany( [(self.date_pos_l, 0, wx.EXPAND),
            (self.date_pos_cb, 0, wx.EXPAND),
            (self.date_pos_split_tc, 0, wx.EXPAND),
            (self.date_pos_split_cb, 0, wx.EXPAND),
            (self.date_pos_ex, 0, wx.EXPAND),
            (self.value_pos_l, 0, wx.EXPAND),
            (self.value_pos_cb, 0, wx.EXPAND),
            (self.value_pos_split_tc, 0, wx.EXPAND),
            (self.value_pos_split_cb, 0, wx.EXPAND),
            (self.value_pos_ex, 0, wx.EXPAND),
            (self.key_pos_l, 0, wx.EXPAND),
            (self.key_pos_cb, 0, wx.EXPAND),
            (self.key_pos_split_tc, 0, wx.EXPAND),
            (self.key_pos_split_cb, 0, wx.EXPAND),
            (self.key_pos_ex, 0, wx.EXPAND) ])
        key_match_sizer = wx.BoxSizer(wx.HORIZONTAL)
        key_match_sizer.Add(self.key_matches_l, 0, wx.ALL, 3)
        key_match_sizer.Add(self.key_matches_tc, 0, wx.ALL, 3)
        key_match_sizer.Add(self.rem_from_val_l, 0, wx.ALL, 3)
        key_match_sizer.Add(self.rem_from_val_tc, 0, wx.ALL, 3)
        data_extract_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        data_extract_label_sizer.Add(self.key_manual_l, 0 , wx.ALL, 3)
        data_extract_label_sizer.Add(self.key_manual_tc, 0 , wx.ALL, 3)
        fields_extract_sizer = wx.BoxSizer(wx.VERTICAL)
        #fields_extract_sizer.Add(self.top_l, 0 , wx.ALL, 3)
        #fields_extract_sizer.Add(data_extract_example_line_sizer, 0 , wx.ALL, 3)
        fields_extract_sizer.Add(split_chr_sizer, 0 , wx.ALL, 3)
        fields_extract_sizer.Add(data_extract_pos_sizer, 0 , wx.ALIGN_CENTER_HORIZONTAL, 3)
        fields_extract_sizer.Add(data_extract_label_sizer, 0, wx.ALL, 3)
        fields_extract_sizer.Add(key_match_sizer, 0, wx.ALL, 3)
        # data trimming
        # time and date controlls
        self.data_controls = wx.StaticText(self,  label='Settings;')
        self.data_controls.SetFont(shared_data.sub_title_font)
        self.start_date_l = wx.StaticText(self,  label='Start at -')
        self.start_time_picer = wx.adv.TimePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.start_date_picer = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.end_date_l = wx.StaticText(self,  label='Finish at -')
        self.end_time_picer = wx.adv.TimePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.end_date_picer = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.limit_date_to_last_l = wx.StaticText(self,  label='Limit date to ')
        limit_choices = ["none", "hour", "day", "week", "month", "year", "1st log", "custom"]
        self.limit_date_to_last_cb = wx.ComboBox(self, size=(90, 25),choices = limit_choices)
        self.limit_date_to_last_cb.Bind(wx.EVT_TEXT, self.limit_date_to_last_go)

        graph_options_sizer = wx.BoxSizer(wx.VERTICAL)
        graph_options_sizer.Add(self.data_controls, 0, wx.ALL|wx.EXPAND, 4)

        # high-low values
        self.danger_low_l = wx.StaticText(self,  label='Danger Low -')
        self.danger_low_tc = wx.TextCtrl(self, size=(60, 25))
        self.low_l = wx.StaticText(self,  label='Low -')
        self.low_tc = wx.TextCtrl(self, size=(60, 25))
        self.high_l = wx.StaticText(self,  label='High -')
        self.high_tc = wx.TextCtrl(self, size=(60, 25))
        self.danger_high_l = wx.StaticText(self,  label='Danger High -')
        self.danger_high_tc = wx.TextCtrl(self, size=(60, 25))
        high_low_sizer = wx.BoxSizer(wx.HORIZONTAL)
        high_low_sizer.Add(self.danger_low_l, 0, wx.ALL, 3)
        high_low_sizer.Add(self.danger_low_tc, 0, wx.ALL, 3)
        high_low_sizer.Add(self.low_l, 0, wx.ALL, 3)
        high_low_sizer.Add(self.low_tc, 0, wx.ALL, 3)
        high_low_sizer.Add(self.high_l, 0, wx.ALL, 3)
        high_low_sizer.Add(self.high_tc, 0, wx.ALL, 3)
        high_low_sizer.Add(self.danger_high_l, 0, wx.ALL, 3)
        high_low_sizer.Add(self.danger_high_tc, 0, wx.ALL, 3)
        # graph axis limits
        self.axis_y_min_l = wx.StaticText(self,  label='Y axis minimum')
        self.axis_y_min_cb = wx.TextCtrl(self, size=(60, 25))
        self.axis_y_max_l = wx.StaticText(self,  label='Y axis maximum')
        self.axis_y_max_cb = wx.TextCtrl(self, size=(60, 25))
        self.size_h_l = wx.StaticText(self,  label='Width')
        self.size_h_cb = wx.TextCtrl(self, size=(60, 25), value="12")
        self.size_v_l = wx.StaticText(self,  label='Height')
        self.size_v_cb = wx.TextCtrl(self, size=(60, 25), value="7")
        axis_limits_sizer = wx.BoxSizer(wx.HORIZONTAL)
        axis_limits_sizer.Add(self.axis_y_min_l, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.axis_y_min_cb, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.axis_y_max_l, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.axis_y_max_cb, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.size_h_l, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.size_h_cb, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.size_v_l, 0, wx.ALL, 3)
        axis_limits_sizer.Add(self.size_v_cb, 0, wx.ALL, 3)

        # Sizers
        # local graphing
        example_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        example_line_sizer.Add(self.example_line_l, 0, wx.ALL, 0)
        example_line_sizer.Add(self.example_line, 0, wx.ALL, 0)
        de_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        de_label_sizer.Add(self.data_extraction_l, 0, wx.ALL, 0)
        de_label_sizer.Add(self.show_hide_date_extract_btn, 0, wx.ALL, 0)
        de_label_sizer.Add(self.save_data_extract_btn, 0, wx.ALL, 0)
        time_and_date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_and_date_sizer.Add(self.limit_date_to_last_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.limit_date_to_last_cb, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.start_date_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.start_time_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.start_date_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_date_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_time_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_date_picer, 0, wx.ALL, 2)
        data_extract_sizer = wx.BoxSizer(wx.VERTICAL)
        data_extract_sizer.Add(de_label_sizer, 0, wx.ALL, 5)
        data_extract_sizer.Add(example_line_sizer, 0, wx.ALL, 5)
        data_extract_sizer.Add(fields_extract_sizer, 0, wx.ALL, 3)
        data_extract_sizer.Add(time_and_date_sizer, 0, wx.ALL, 0)

        #
        self.graph_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graph_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.graph_l_sizer.Add(self.graph_txt, 0, wx.ALL|wx.EXPAND, 3)
        self.graph_l_sizer.Add(self.graphs_clear_btn, 0, wx.ALL|wx.EXPAND, 3)
        #self.graph_sizer.Add(wx.StaticText(self,  label='problem'), 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer =  wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(data_extract_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(graph_options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(high_low_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(axis_limits_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_l_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_sizer, 0, wx.ALL, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()
        self.hide_data_extract()
        self.hide_graph_settings()

    def show_hide_date_extract_click(self, e):
        if self.show_hide_date_extract_btn.GetLabel() == "show":
            self.show_data_extract()
            self.show_hide_date_extract_btn.SetLabel("hide")
        else:
            self.hide_data_extract()
            self.data_extraction_l.Show()
            self.show_hide_date_extract_btn.Show()
            self.show_hide_date_extract_btn.SetLabel("show")
        self.Layout()

    def hide_data_extract(self):
        self.data_extraction_l.Hide()
        self.show_hide_date_extract_btn.Hide()
        self.save_data_extract_btn.Hide()
        self.example_line_l.Hide()
        self.example_line.Hide()
        self.split_character_l.Hide()
        self.split_character_tc.Hide()
        self.date_pos_l.Hide()
        self.date_pos_cb.Hide()
        self.date_pos_split_tc.Hide()
        self.date_pos_split_cb.Hide()
        self.date_pos_ex.Hide()
        self.value_pos_l.Hide()
        self.value_pos_cb.Hide()
        self.value_pos_split_tc.Hide()
        self.value_pos_split_cb.Hide()
        self.value_pos_ex.Hide()
        self.key_pos_l.Hide()
        self.key_pos_cb.Hide()
        self.key_manual_l.Hide()
        self.key_manual_tc.Hide()
        self.key_pos_split_tc.Hide()
        self.key_pos_split_cb.Hide()
        self.key_pos_ex.Hide()
        self.key_matches_l.Hide()
        self.key_matches_tc.Hide()
        self.rem_from_val_l.Hide()
        self.rem_from_val_tc.Hide()
        self.start_date_l.Hide()
        self.start_time_picer.Hide()
        self.start_date_picer.Hide()
        self.end_date_l.Hide()
        self.end_time_picer.Hide()
        self.end_date_picer.Hide()
        self.limit_date_to_last_l.Hide()
        self.limit_date_to_last_cb.Hide()
        self.Layout()

    def hide_graph_settings(self):
        # settings
        self.danger_low_l.Hide()
        self.danger_low_tc.Hide()
        self.low_l.Hide()
        self.low_tc.Hide()
        self.high_l.Hide()
        self.high_tc.Hide()
        self.danger_high_l.Hide()
        self.danger_high_tc.Hide()
        self.data_controls.Hide()
        self.data_controls.Hide()
        self.axis_y_min_l.Hide()
        self.axis_y_min_cb.Hide()
        self.axis_y_max_l.Hide()
        self.axis_y_max_cb.Hide()
        self.size_h_l.Hide()
        self.size_h_cb.Hide()
        self.size_v_l.Hide()
        self.size_v_cb.Hide()
        self.Layout()

    def show_data_extract(self):
        self.data_extraction_l.Show()
        self.show_hide_date_extract_btn.Show()
        self.save_data_extract_btn.Show()
        self.example_line_l.Show()
        self.example_line.Show()
        self.split_character_l.Show()
        self.split_character_tc.Show()
        self.date_pos_l.Show()
        self.date_pos_cb.Show()
        self.date_pos_split_tc.Show()
        self.date_pos_split_cb.Show()
        self.date_pos_ex.Show()
        self.value_pos_l.Show()
        self.value_pos_cb.Show()
        self.value_pos_split_tc.Show()
        self.value_pos_split_cb.Show()
        self.value_pos_ex.Show()
        self.key_pos_l.Show()
        self.key_pos_cb.Show()
        self.key_manual_l.Show()
        self.key_manual_tc.Show()
        self.key_pos_split_tc.Show()
        self.key_pos_split_cb.Show()
        self.key_pos_ex.Show()
        val_pos = self.value_pos_cb.GetValue()
        if not val_pos == "match text":
            self.key_matches_l.Show()
            self.key_matches_tc.Show()
        self.rem_from_val_l.Show()
        self.rem_from_val_tc.Show()
        # date line special tools
        self.limit_date_to_last_l.Show()
        self.limit_date_to_last_cb.Show()
        if not self.limit_date_to_last_cb.GetValue() == 'none':
            self.start_date_l.Show()
            self.start_time_picer.Show()
            self.start_date_picer.Show()
            self.end_date_l.Show()
            self.end_time_picer.Show()
            self.end_date_picer.Show()
        self.Layout()

    def show_graph_settings(self):
        # setting
        self.danger_low_l.Show()
        self.danger_low_tc.Show()
        self.low_l.Show()
        self.low_tc.Show()
        self.high_l.Show()
        self.high_tc.Show()
        self.danger_high_l.Show()
        self.danger_high_tc.Show()
        self.data_controls.Show()
        self.data_controls.Show()
        self.axis_y_min_l.Show()
        self.axis_y_min_cb.Show()
        self.axis_y_max_l.Show()
        self.axis_y_max_cb.Show()
        self.size_h_l.Show()
        self.size_h_cb.Show()
        self.size_v_l.Show()
        self.size_v_cb.Show()
        self.Layout()

    def clear_and_reset_fields(self):
        self.date_pos_ex.SetLabel("")
        self.value_pos_ex.SetLabel("")
        self.key_pos_ex.SetLabel("")
        self.date_pos_cb.SetValue("")
        self.value_pos_cb.SetValue("")
        self.key_pos_cb.SetValue("None")
        self.date_pos_cb.Disable()
        self.value_pos_cb.Disable()
        self.key_pos_cb.Disable()
        self.date_pos_cb.Clear()
        self.value_pos_cb.Clear()
        self.key_pos_cb.Clear()
        self.key_pos_cb.Append("None")
        self.key_pos_cb.Append("Manual")
        #
        self.date_pos_split_cb.Disable()
        self.date_pos_split_cb.SetValue("")
        self.date_pos_split_cb.Clear()
        self.value_pos_split_cb.Disable()
        self.value_pos_split_cb.SetValue("")
        self.value_pos_split_cb.Clear()
        self.key_pos_split_cb.Disable()
        self.key_pos_split_cb.SetValue("")
        self.key_pos_split_cb.Clear()
        self.date_pos_split_tc.Disable()
        self.value_pos_split_tc.Disable()
        self.key_pos_split_tc.Disable()
        self.date_pos_split_tc.SetValue("")
        self.value_pos_split_tc.SetValue("")
        self.key_pos_split_tc.SetValue("")
        self.key_pos_ex.SetLabel("")

        self.axis_y_min_cb.SetValue("")
        self.axis_y_max_cb.SetValue("")
        #self.size_h_cb.SetValue("15")
        #self.size_v_cb.SetValue("10")

    def split_line_text(self, e):
        self.clear_and_reset_fields()
        split_character = self.split_character_tc.GetValue()
        if not split_character == "":
            line = self.example_line.GetLabel()
            if split_character in line:
                self.split_line = line.split(split_character)
                self.date_pos_cb.Enable()
                self.value_pos_cb.Enable()
                self.key_pos_cb.Enable()
                self.value_pos_cb.Append("match text")
                for x in range(0, len(self.split_line)):
                    self.date_pos_cb.Append(str(x))
                    self.value_pos_cb.Append(str(x))
                    self.key_pos_cb.Append(str(x))
            else:
                return None
            # check each entry to see if it's a date format we understand
            found = None
            #self.date_pos_split_tc.SetValue("")
            for item in range(0, len(self.split_line)):
                try:
                    test_date = datetime.datetime.strptime(self.split_line[item], '%Y-%m-%d %H:%M:%S.%f')
                    self.date_pos_cb.SetValue(str(item))
                    self.date_pos_ex.SetLabel(self.split_line[item])
                    self.date_pos_ex.SetForegroundColour((75,200,75))
                    found = str(item)
                except:
                    split_chr_choices = MainApp.graphing_ctrl_pannel.get_split_chr(self.split_line[item])
                    if len(split_chr_choices) == 1:
                        item_split_again = self.split_line[item].split(split_chr_choices[0])
                        for position_in_split_again_item in range(0, len(item_split_again)):
                            try:
                                date_to_test = item_split_again[position_in_split_again_item]
                                test_date = datetime.datetime.strptime(date_to_test, '%Y-%m-%d %H:%M:%S.%f')
                                self.date_pos_cb.SetValue(str(item))
                                self.date_pos_split_tc.SetValue(split_chr_choices[0])
                                found = str(item)
                            except:
                                pass
                # after sorting through each item in the line react to results and try to guess value if possible
            if found == None:
                print("local graphing tab - Could not auto detect date")
            else:
                if len(self.split_line) == 2:
                    if not self.value_pos_cb.GetValue() == "match text":
                        if found == "0":
                            self.value_pos_cb.SetValue("1")
                            self.value_pos_ex.SetLabel(self.split_line[1])
                        elif found == "1":
                            self.value_pos_cb.SetValue("0")
                            self.value_pos_ex.SetLabel(self.split_line[0])

    def key_pos_go(self, e):
        val_pos = self.value_pos_cb.GetValue()
        if not val_pos == "match text":
            key_pos = self.key_pos_cb.GetValue()
            if not key_pos == "" and not key_pos == "None" and not key_pos == "Manual" and not key_pos == None:
                self.key_pos_ex.SetLabel(self.split_line[int(key_pos)])
                self.key_pos_split_tc.Enable()
                self.key_pos_split_tc.Show()
                self.key_pos_split_cb.Show()
                self.key_manual_l.Show()
                self.key_manual_tc.Show()
                self.key_matches_l.Show()
                self.key_matches_tc.Show()
                #self.SetSizer(main_sizer)
            elif key_pos == "Manual":
                self.key_pos_split_tc.Hide()
                self.key_pos_split_cb.Hide()
                self.key_pos_split_cb.SetValue("")
                self.key_manual_l.Show()
                self.key_manual_tc.Show()
                self.key_matches_l.Hide()
                self.key_matches_tc.Hide()
                self.key_pos_ex.SetLabel("")
                #self.SetSizer(main_sizer)
            elif key_pos == "None" or key_pos == "" or key_pos == None:
            #    self.key_pos_ex.SetLabel("")
                self.key_pos_split_tc.Hide()
                self.key_pos_split_cb.SetValue("")
                self.key_pos_split_cb.Hide()
                self.key_manual_l.Show()
                self.key_manual_tc.Show()
                self.key_matches_l.Show()
                self.key_matches_tc.Hide()
                self.key_pos_ex.SetLabel("")
        else:
            # Find the value to display as an example when match text is selected
            line = self.example_line.GetLabel()
            split_character = self.split_character_tc.GetValue()
            value_split = self.value_pos_split_tc.GetValue()
            value_split_pos = self.value_pos_split_cb.GetSelection()
            key_text = self.key_pos_cb.GetValue()
            if ".txt" in shared_data.first_valueset_name:
                self.key_manual_tc.SetValue(key_text + " " + shared_data.first_valueset_name.split('.txt')[0])
            else:
                self.key_manual_tc.SetValue(key_text + " " + shared_data.first_valueset_name)
            #THIS TEXT HER
            if value_split_pos == 0:
                t_value_pos = 1
                t_key_pos = 0
            else:
                t_value_pos = 0
                t_key_pos = 1
            value = ""
            if split_character in line:
                line_items = line.split(split_character)
                for item in line_items:
                    if value_split in item:
                        item_items = item.split(value_split)
                        if item_items[t_key_pos] == key_text:
                            value = item_items[t_value_pos]
            self.key_pos_ex.SetLabel(value)
            self.key_pos_split_tc.Hide()
            self.key_pos_split_cb.Hide()
        self.Layout()

    def key_pos_split_text(self, e):
        self.key_pos_split_cb.Clear()
        val_pos_ex = self.key_pos_ex.GetLabel()
        split_symbol = self.key_pos_split_tc.GetValue()
        if not split_symbol == "":
            if split_symbol in val_pos_ex:
                key_split = val_pos_ex.split(split_symbol)
                for x in key_split:
                    self.key_pos_split_cb.Append(x)
                self.key_pos_split_cb.Enable()
            else:
                self.key_pos_split_cb.Disable()
                self.key_pos_split_cb.SetValue("")
                self.key_pos_go("e")
        else:
            self.key_pos_split_cb.Disable()
            self.key_pos_split_cb.SetValue("")
            self.key_pos_go("e")

    def key_pos_split_go(self, e):
        key_pos = self.key_pos_cb.GetValue()
        if key_pos == "None" or key_pos == "Manual":
            self.key_pos_ex.SetLabel("")
        else:
            key_pos_split = self.key_pos_split_cb.GetValue()
            self.key_pos_ex.SetLabel(key_pos_split)

    def value_pos_go(self, e):
        '''
        Triggers when the combobox for selecting which position in the
        split line the value to display is found.
           - The value might then be split again if needed using value_pos_split_tc
        '''
        val_pos = self.value_pos_cb.GetValue()
        if not val_pos == "" and not val_pos == "match text":
            self.value_pos_ex.SetLabel(self.split_line[int(val_pos)])
            self.value_pos_split_tc.Enable()
            self.key_pos_split_cb.Show()
            self.key_pos_split_tc.Show()
            self.key_matches_l.Show()
            self.key_matches_tc.Show()
            self.make_btn_enable()
            MainApp.window_self.Layout()
        # special case for matching text
        if val_pos == "match text":
            key_matches = self.key_matches_tc.Show()
            self.value_pos_split_tc.Enable()
            self.key_pos_split_cb.Hide()
            self.key_pos_split_tc.Hide()
            self.key_matches_l.Hide()
            self.key_matches_tc.Hide()
            self.make_btn_enable()
            MainApp.window_self.Layout()
            self.key_pos_cb.Clear()
            self.key_pos_cb.SetValue("")
        if val_pos == "":
            self.value_pos_split_tc.Disable()

    def value_pos_split_text(self, e):
        '''
        Triggers when the text in the textctrl for splitting the
        value (which should be already split from the log line)
        is changed either by user or machine.
        '''
        self.value_pos_split_cb.Clear() # blank combo box to the right of it
        val_pos = self.value_pos_cb.GetValue()
        split_symbol = self.value_pos_split_tc.GetValue()
        if not split_symbol == "" and not val_pos == "match text":
            # Show the two sides of the selected field or blank it if split character is wrong
            val_pos_ex = self.value_pos_ex.GetLabel()
            if split_symbol in val_pos_ex:
                value_split = val_pos_ex.split(split_symbol)
                for x in value_split:
                    self.value_pos_split_cb.Append(x)
                self.value_pos_split_cb.Enable()
            else:
                self.value_pos_split_cb.Disable()
                self.value_pos_split_cb.SetValue("")
                self.value_pos_go("e")

        if val_pos == "match text":
            # set box to 'first' and 'last' to determine which side of the split-text to use as the key
            self.value_pos_split_cb.Append('left')
            self.value_pos_split_cb.Append('right')
            MainApp.graphing_info_pannel.value_pos_split_cb.SetSelection(0)
            MainApp.graphing_info_pannel.value_pos_split_go("e")
            self.value_pos_split_cb.Enable()
        if split_symbol == "":
            self.value_pos_split_cb.Disable()
            self.value_pos_split_cb.SetValue("")
            self.value_pos_go("e")

    def use_match_text_key(self):
        self.key_pos_cb.Clear()
        #get list of keys
        example_line = self.example_line.GetLabel()
        split_chr = self.split_character_tc.GetValue()
        split_symbol_2 = self.value_pos_split_tc.GetValue()
        split_pos_2 = self.value_pos_split_cb.GetSelection()
        list_of_keys = []
        if split_chr in example_line:
            example_line = example_line.split(split_chr)
            for item in example_line:
                if split_symbol_2 in item:
                    item = item.split(split_symbol_2)[split_pos_2]
                    list_of_keys.append(item)
        self.key_pos_cb.Enable()
        self.key_pos_cb.Append(list_of_keys)
        if len(list_of_keys) > 1:
            self.key_pos_cb.SetValue(list_of_keys[1])
        else:
            self.key_pos_cb.SetValue(list_of_keys[0])

    def value_pos_split_go(self, e):
        '''
        displays the text as an example if value has been split again
        after being split from the original log entry line.
        '''
        val_pos = self.value_pos_cb.GetValue()
        value_pos_split = self.value_pos_split_cb.GetValue()
        self.value_pos_ex.SetLabel(value_pos_split)
        #
        if val_pos == "match text":
            self.use_match_text_key()
        else:
            self.make_btn_enable()

    def date_pos_go(self, e):
        date_pos = self.date_pos_cb.GetValue()
        if date_pos.isdigit():
            date_pos = int(date_pos)
            if not date_pos > len(self.split_line):
                ex_date = self.split_line[date_pos]
                self.date_pos_ex.SetLabel(ex_date)
                try:
                    test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S.%f')
                    self.date_pos_ex.SetForegroundColour((75,200,75))
                    self.date_good = True
                except:
                    self.date_pos_ex.SetForegroundColour((220,75,75))
                    self.date_pos_split_tc.Enable()
                    self.date_good = False
        else:
            self.date_good = False
        self.make_btn_enable()

    def date_pos_split_text(self, e):
        self.date_pos_split_cb.Enable()
        date_pos_ex = self.date_pos_ex.GetLabel()
        split_symbol = self.date_pos_split_tc.GetValue()
        if not split_symbol == "":
            if split_symbol in date_pos_ex:
                date_split = date_pos_ex.split(split_symbol)
                self.date_pos_split_cb.Clear()
                for x in date_split:
                    self.date_pos_split_cb.Append(x)
                if len(date_split) == 2:
                    try:
                        test_date = datetime.datetime.strptime(date_split[0], '%Y-%m-%d %H:%M:%S.%f')
                        self.date_pos_split_cb.SetValue(date_split[0])
                        if self.value_pos_split_tc.GetValue() == "":
                            self.value_pos_cb.SetValue("match text")
                            self.value_pos_split_tc.SetValue(split_symbol)
                    except:
                        try:
                            test_date = datetime.datetime.strptime(date_split[1], '%Y-%m-%d %H:%M:%S.%f')
                            self.date_pos_split_cb.SetValue(date_split[1])
                            if self.value_pos_split_tc.GetValue() == "":
                                self.value_pos_cb.SetValue("match text")
                                self.value_pos_split_tc.SetValue(split_symbol)
                        except:
                            print(" - local graphing pnl can't auto determine date - " + str(date_split))
            else:
                self.date_pos_split_cb.Disable()
                self.date_pos_split_cb.SetValue("")
                self.date_pos_go("e")
        else:
            self.date_pos_split_cb.Disable()
            self.date_pos_split_cb.SetValue("")
            self.date_pos_go("e")

    def date_pos_split_select(self, e):
        date_pos = self.date_pos_split_cb.GetValue()
        self.date_pos_ex.SetLabel(date_pos)
        try:
            test_date = datetime.datetime.strptime(date_pos, '%Y-%m-%d %H:%M:%S.%f')
            self.date_pos_ex.SetForegroundColour((75,200,75))
            self.date_good = True
        except:
            self.date_pos_ex.SetForegroundColour((220,75,75))
            self.date_good = False
        self.make_btn_enable()

    def make_btn_enable(self):
        val_ex = self.value_pos_ex.GetLabel()
        val_good = False
        rem_from_val = self.rem_from_val_tc.GetValue()
        #print("value example:", val_ex, "  rem_from_val:", rem_from_val)
        if not rem_from_val == "":
            val_ex = val_ex.replace(rem_from_val, "")
        #print("val_ex after replace:",val_ex)
        if val_ex.isdigit():
            val_good = True
        else:
            try:
                test = float(val_ex)
                val_good = True
            except:
                val_good = False
        # if valid turn on graphing buttons
        if self.date_good and val_good == True:
            #print("Local Graphing - valid data")
            MainApp.graphing_ctrl_pannel.enable_value_graphs()
        else:
            #print("local graphing - not got valid data")
            MainApp.graphing_ctrl_pannel.disable_value_graphs()

    def hide_date_extract_boxes(self):
        self.start_date_l.Hide()
        self.end_date_l.Hide()
        self.start_time_picer.Hide()
        self.start_date_picer.Hide()
        self.end_time_picer.Hide()
        self.end_date_picer.Hide()

    def show_date_extract_boxes(self):
        self.start_date_l.Show()
        self.end_date_l.Show()
        self.start_time_picer.Show()
        self.start_date_picer.Show()
        self.end_time_picer.Show()
        self.end_date_picer.Show()

    def limit_date_to_last_go(self, e):
        limit_setting = self.limit_date_to_last_cb.GetValue()
        if limit_setting == "none":
            self.hide_date_extract_boxes()
            return None
        self.show_date_extract_boxes()
        if limit_setting == "custom":
            MainApp.graphing_ctrl_pannel.set_dates_to_log()
            return None
        # widen range of datebox so it accepts the values
        current_datetime = datetime.datetime.now()
        is_set, range_start, range_end = MainApp.graphing_info_pannel.end_date_picer.GetRange()
        self.end_date_picer.SetRange(range_start, current_datetime)
        self.start_date_picer.SetRange(range_start, current_datetime)
        # set
        print("Limiting date to ", limit_setting)
        if limit_setting == "1st log":
            if len(shared_data.list_of_datasets) > 0:
                if len(shared_data.list_of_datasets[0][0]) > 0:
                    new_start_date = shared_data.list_of_datasets[0][0][0]
                    new_end_date = shared_data.list_of_datasets[0][0][-1]
                    self.start_time_picer.SetValue(new_start_date)
                    self.start_date_picer.SetValue(new_start_date)
                    self.end_time_picer.SetValue(new_end_date)
                    self.end_date_picer.SetValue(new_end_date)
            return None
        # set related to current time
        elif limit_setting == "hour":
            limit = datetime.timedelta(hours=1)
        elif limit_setting == "day":
            limit = datetime.timedelta(days=1)
        elif limit_setting == "week":
            limit = datetime.timedelta(weeks=1)
        elif limit_setting == "month":
            limit = datetime.timedelta(weeks=4)
        elif limit_setting == "year":
            limit = datetime.timedelta(weeks=52)
        new_start_datetime = current_datetime - limit
        self.start_time_picer.SetValue(new_start_datetime)
        self.start_date_picer.SetValue(new_start_datetime)
        self.end_time_picer.SetValue(datetime.datetime(year = 3000, month = 1, day = 1, hour = 23, minute = 59, second = 59))
        self.end_date_picer.SetValue(current_datetime)

    def read_log_date_and_value(self, numbers_only = False, limit_by_date = True, date_only = False):
        # cancel if no date value set
        if self.date_pos_cb.GetValue() == "":
            print(" -- Attempted to read log without date position set")
            if date_only == False:
                return [], [], []
            else:
                return []
        # read date limits
        if limit_by_date == True:
            # This checks the date limit selection and resets limit_by_date to false if required
            date_limit_to = MainApp.graphing_info_pannel.limit_date_to_last_cb.GetValue()
            if date_limit_to == 'none':
                limit_by_date = False
        if limit_by_date == True:
            # if the date is being used check the boxes for information
            first_time = MainApp.graphing_info_pannel.start_time_picer.GetValue()
            first_date = MainApp.graphing_info_pannel.start_date_picer.GetValue()
            first_datetime = datetime.datetime(year = first_date.year, month = first_date.month + 1, day = first_date.day, hour = first_time.hour, minute = first_time.minute, second = first_time.second)
            last_time = MainApp.graphing_info_pannel.end_time_picer.GetValue()
            last_date = MainApp.graphing_info_pannel.end_date_picer.GetValue()
            last_datetime = datetime.datetime(year = last_date.year, month = last_date.month + 1, day = last_date.day, hour = last_time.hour, minute = last_time.minute, second = last_time.second)
            #print(first_datetime, last_datetime)
        # notify user what we're doing
        msg = " - Reading Log " + str(shared_data.log_to_load)
        if date_only == True:
            msg += " - Dates Only"
        if limit_by_date == True:
            msg += " - Limiting by Date"
        if numbers_only == True:
            msg += " - Numbers only"
        print(msg)
        MainApp.status.write_bar(msg)
        shared_data.first_valueset_name = os.path.split(shared_data.log_to_load)[1]
        # get line splitting info from ui boxes
        split_chr = self.split_character_tc.GetValue()
        date_pos = int(self.date_pos_cb.GetValue())
        date_split = self.date_pos_split_tc.GetValue()
        date_split_pos = self.date_pos_split_cb.GetSelection()
        if not date_only == True:
            value_pos = int(self.value_pos_cb.GetValue())
            value_split = self.value_pos_split_tc.GetValue()
            value_split_pos = self.value_pos_split_cb.GetSelection()
            # key position or label
            key_pos = self.key_pos_cb.GetValue()
            key_split = self.key_pos_split_tc.GetValue()
            key_pos_split = int(self.key_pos_split_cb.GetSelection())

            #if key_pos == 'Manual':
            key_manual = self.key_manual_tc.GetValue()
            key_pos = ""
                #
            if key_pos.isdigit():
                    key_pos = int(key_pos)
            if self.key_matches_tc.IsEnabled() == True:
                key_matches = self.key_matches_tc.GetValue()
            else:
                key_matches = ""
        #
        ##
        ### loading log from file
        ##
        #
        print("  -- Reading log from file")
        with open(shared_data.log_to_load) as f:
            log_to_parse = f.read()
        log_to_parse = log_to_parse.splitlines()
        if len(log_to_parse) == 0:
            print(" --- Log file is empty")

        #
        ##
        ### read log into lists
        ##
        #
        # define lists to fill
        date_list = []
        value_list = []
        key_list = []
        # cycle through each line and fill the lists
        for line in log_to_parse:
            line_items = line.split(split_chr)
            # get date for this log entry
            date = line_items[date_pos]
            if not date_split == "":
                date = date.split(date_split)[date_split_pos]
            if "." in date:
                date = date.split(".")[0]
            # Check date is valid and ignore if not
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if limit_by_date == True:
                    if date > last_datetime or date < first_datetime:
                        date = ""
            except:
                #raise
                print("date not valid -" + str(date))
                date = ""

            # get value for this log entry
            if not date_only == True:
                value = line_items[value_pos]
                if not value_split == "":
                    value = line_items[value_pos]
                    value = value.split(value_split)[value_split_pos]
                # remove from value
                rem_from_val = self.rem_from_val_tc.GetValue()
                if not rem_from_val == "":
                    value = value.replace(rem_from_val, "")
                # perform checks for numbers only when selected
                if numbers_only == True:
                    try:
                        value = float(value)
                    except:
                        print('value not valid -' + str(value))
                        value = ""

                # get key for this log entry
                if not key_pos == "":
                    key = line_items[key_pos]
                    if not key_split == "":
                        key = key.split(key_split)[key_pos_split]
                    # if key matching is selected
                    if not key_matches == "":
                        if not key_matches in key:
                            key = False
                # if manual key is selected
                elif not key_manual == "":
                    key = key_manual
                elif key_pos == "" and key_manual == "":
                    key = ""

                # add to lists
                if not date == "" and not value == "" and not key == False:
                    date_list.append(date)
                    value_list.append(value)
                    key_list.append(key)
            else:
                if not date == "":
                    date_list.append(date)
        # end of loop - return appropriate lists
        if len(date_list) == 0:
            dmsg = "No valid log entries were found, check settings and try again"
            wx.MessageBox(dmsg, 'No data', wx.OK | wx.ICON_INFORMATION)
        if date_only == False:
            shared_data.first_value_set = value_list
            shared_data.first_date_set = date_list
            shared_data.first_keys_set = key_list
            return date_list, value_list, key_list
        else:
            return date_list

    def read_log_with_text_match(self, numbers_only = False, limit_by_date = True):
        # cancel if no date value set
        if self.date_pos_cb.GetValue() == "":
            print(" -- Attempted to read log without date position set")
            if date_only == False:
                return [], [], []
        # read date limits
        if limit_by_date == True:
            # This checks the date limit selection and resets limit_by_date to false if required
            date_limit_to = MainApp.graphing_info_pannel.limit_date_to_last_cb.GetValue()
            if date_limit_to == 'none':
                limit_by_date = False
        if limit_by_date == True:
            first_time = MainApp.graphing_info_pannel.start_time_picer.GetValue()
            first_date = MainApp.graphing_info_pannel.start_date_picer.GetValue()
            first_datetime = datetime.datetime(year = first_date.year, month = first_date.month + 1, day = first_date.day, hour = first_time.hour, minute = first_time.minute, second = first_time.second)
            last_time = MainApp.graphing_info_pannel.end_time_picer.GetValue()
            last_date = MainApp.graphing_info_pannel.end_date_picer.GetValue()
            last_datetime = datetime.datetime(year = last_date.year, month = last_date.month + 1, day = last_date.day, hour = last_time.hour, minute = last_time.minute, second = last_time.second)
            #print(first_datetime, last_datetime)
        # notify user what we're doing
        msg = " - Reading Log " + str(shared_data.log_to_load)
        if limit_by_date == True:
            msg += " - Limiting by Date"
        if numbers_only == True:
            msg += " - Numbers only"
        print(msg)
        MainApp.status.write_bar(msg)
        shared_data.first_valueset_name = os.path.split(shared_data.log_to_load)[1]
        # get line splitting info from ui boxes
        split_chr = self.split_character_tc.GetValue()
        date_pos = int(self.date_pos_cb.GetValue())
        date_split = self.date_pos_split_tc.GetValue()
        date_split_pos = self.date_pos_split_cb.GetSelection()
        value_split = self.value_pos_split_tc.GetValue()
        value_split_pos = self.value_pos_split_cb.GetSelection()
        rem_from_val = self.rem_from_val_tc.GetValue()
        if value_split_pos == 0:
            t_value_pos = 1
            t_key_pos = 0
        else:
            t_value_pos = 0
            t_key_pos = 1
        key_text = self.key_pos_cb.GetValue()
        #
        ##
        ### loading log from file
        ##
        #
        print("  -- Reading log from file")
        with open(shared_data.log_to_load) as f:
            log_to_parse = f.read()
        log_to_parse = log_to_parse.splitlines()
        if len(log_to_parse) == 0:
            print(" --- Log file is empty")
        ##
        ### read log into lists
        ##
        #
        # define lists to fill
        date_list = []
        value_list = []
        key_list = []
        # cycle through each line and fill the lists
        for line in log_to_parse:
            date = ""
            value = ""
            key = ""
            if split_chr in line:
                line_items = line.split(split_chr)
                for item in line_items:
                    # date - by positional argument only at the moment
                    date = line_items[date_pos]
                    if not date_split == "":
                        date = date.split(date_split)[date_split_pos]
                    if "." in date:
                        date = date.split(".")[0]
                    # Check date is valid and ignore if not
                    try:
                        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                        if limit_by_date == True:
                            if date > last_datetime or date < first_datetime:
                                date = ""
                    except:
                        #raise
                        print("date not valid -" + str(date))
                        date = ""
                    #value
                    if value_split in item:
                        item_items = item.split(value_split)
                        if item_items[t_key_pos] == key_text:
                            value = item_items[t_value_pos]
                            key = item_items[t_key_pos]
                            # remove from value
                            if not rem_from_val == "":
                                value = value.replace(rem_from_val, "")
                            # check it's a number and convert type to float
                            try:
                                value = float(value)
                            except:
                                print(" - Value not a valid number; " + str(value))
                                value = ""
            # set key to manual
            if not self.key_manual_tc.GetValue() == "":
                key = self.key_manual_tc.GetValue()
            # add to lists
            if not date == "" and not value == "" and not key == False:
                date_list.append(date)
                value_list.append(value)
                key_list.append(key)
        # end of loop - return appropriate lists
        if len(date_list) == 0:
            dmsg = "No valid log entries were found, check settings and try again"
            wx.MessageBox(dmsg, 'No data', wx.OK | wx.ICON_INFORMATION)
        #shared_data.first_value_set = value_list
        #shared_data.first_date_set = date_list
        #shared_data.first_keys_set = key_list
        return date_list, value_list, key_list

    def show_local_graph(self, graph_path):
        MainApp.graphing_info_pannel.graph_sizer.Add(wx.StaticBitmap(MainApp.graphing_info_pannel, -1, wx.Image(graph_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        win_width = self.GetSize()[0]
        win_height = self.GetSize()[1]
        w_space_left = win_width - 285
        size = wx.Size(win_width, win_height)
        self.SetMinSize(size)
        MainApp.window_self.Layout()
        self.SetupScrolling()


class graphing_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # Start drawing the UI elements
        #graphing engine selection
        make_graph_l = wx.StaticText(self,  label='Make graphs on;')
        graph_opts = ['Pigrow', 'local']
        self.graph_cb = wx.ComboBox(self, choices = graph_opts)
        self.graph_cb.Bind(wx.EVT_TEXT, self.graph_engine_combo_go)
        #
        ##
        ### options shown when graphing on the pigrow
        ##
        #
        self.pigraph_text = wx.StaticText(self,  label='Graphing directly on the pigrow\n saves having to download logs')
        # select graphing script

        # manual
        self.script_text = wx.StaticText(self,  label='Graphing Script;')
        self.select_script_cb = wx.ComboBox(self, choices = ['BLANK'])
        self.select_script_cb.Bind(wx.EVT_COMBOBOX, self.select_script_combo_go)
        self.opts_cb = wx.ComboBox(self, choices=['BLANK'])
        self.opts_cb.Bind(wx.EVT_COMBOBOX, self.opt_combo_go)
        # list box for of graphing options
        self.get_opts_tb = wx.CheckBox(self, label='Get Options')
        self.get_opts_tb.Bind(wx.EVT_CHECKBOX, self.get_opts_click)
        # various ui elements for differing options value sets - text, list
        self.opts_text = wx.TextCtrl(self)
        command_line_opts_value_list = ['BLANK']
        self.command_line_opts_value_list_cb = wx.ComboBox(self, choices = command_line_opts_value_list)
        # button to add arg to string
        self.add_arg_btn = wx.Button(self, label='Add to command line')
        self.add_arg_btn.Bind(wx.EVT_BUTTON, self.add_arg_click)
        # extra arguments string
        self.extra_args_label = wx.StaticText(self,  label='Commandline Flags;')
        self.extra_args = wx.TextCtrl(self)
        # remote buttons
        self.make_graph_btn = wx.Button(self, label='Make Graph')
        self.make_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_click)
        self.download_graph = wx.CheckBox(self, label='download')
        self.download_graph.SetValue(True)
        #
        ##
        ### for local graph construction
        ##
        #
        # current log files info
        self.num_of_logs_loaded = wx.StaticText(self,  label='0', size=(20, 25))
        self.num_of_logs_loaded.SetFont(shared_data.large_info_font)
        self.valset_1_loaded  = wx.StaticBitmap(self, -1, shared_data.no_log_image)
        self.valset_1_len_l = wx.StaticText(self,  label=' Datapoints : ')
        self.valset_1_len = wx.StaticText(self,  label='0')
        self.valset_1_name = wx.StaticText(self,  label='-')
        self.download_log_cb = wx.CheckBox(self,  label='download ')
        self.set_log_btn = wx.Button(self, label='Add', size=(90,-1))
        self.set_log_btn.Bind(wx.EVT_BUTTON, self.set_log_click)
        self.clear_log_btn = wx.Button(self, label='Clear', size=(50,-1))
        self.clear_log_btn.Bind(wx.EVT_BUTTON, self.clear_log_click)
        #presets
        self.data_title_text = wx.StaticText(self,  label='Data Source')
        self.data_title_text.SetFont(shared_data.sub_title_font)
        self.preset_text = wx.StaticText(self,  label='Preset')
        self.graph_presets_cb = wx.ComboBox(self, choices=['BLANK'])
        self.graph_presets_cb.Bind(wx.EVT_COMBOBOX, self.graph_preset_cb_go)
        self.graph_preset_all = wx.CheckBox(self, label='all')
        self.graph_preset_all.Bind(wx.EVT_CHECKBOX, self.preset_all_click)
        # open log
        self.select_log_btn = wx.Button(self, label='Select Log File')
        self.select_log_btn.Bind(wx.EVT_BUTTON, self.select_log_click)
        # load data using a sucker modules
        self.module_sucker_text = wx.StaticText(self,  label='Data Sucker Modules')
        self.module_sucker_cb = wx.ComboBox(self, choices=get_module_options("sucker_", "graph_modules"))
        self.module_sucker_go_btn = wx.Button(self, label='Go')
        self.module_sucker_go_btn.Bind(wx.EVT_BUTTON, self.suck_from_imported_module)
        # graph section
        self.graph_title_text = wx.StaticText(self,  label='Graphs', size=(40,30))
        self.graph_title_text.SetFont(shared_data.sub_title_font)
        # make_graph_from_imported_module
        self.refresh_module_graph_btn = wx.Button(self, label='R', size=(40,30))
        self.refresh_module_graph_btn.Bind(wx.EVT_BUTTON, self.refresh_module_graph_go)
        self.module_graph_choice = wx.ComboBox(self,  size=(150, 30), choices = get_module_options("graph_","graph_modules"))
        self.module_graph_choice.Bind(wx.EVT_COMBOBOX, self.module_graph_choice_go)

        self.module_graph_btn = wx.Button(self, label='Make', size=(60,25))
        self.module_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_from_imported_module)
        self.animate_module = wx.Button(self, label='Animate')
        self.animate_module.Bind(wx.EVT_BUTTON, self.animate_module_click)
        self.animate_show_time_period_l = wx.StaticText(self,  label='Hours to Show')
        self.animate_show_time_period_tc = wx.TextCtrl(self, value="24")
        self.animate_roll_speed_l = wx.StaticText(self,  label='Roll Speed Min')
        self.animate_roll_speed_tc = wx.TextCtrl(self, value="15")
        # imported module options
        self.graph_module_settings = wx.CheckBox(self, label='settings')
        self.graph_module_settings.Bind(wx.EVT_CHECKBOX, self.graph_module_settings_click)
        self.module_options_list_ctrl = wx.ListCtrl(self, size=(-1,100), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.module_options_list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_gm_opt)
        self.module_options_list_ctrl.InsertColumn(0, 'Option')
        self.module_options_list_ctrl.InsertColumn(1, 'Value')
        # datawall module
        self.datawall_title_text = wx.StaticText(self,  label='Datawall', size=(80,30))
        self.datawall_title_text.SetFont(shared_data.sub_title_font)
        self.datawall_preset_l = wx.StaticText(self,  label='preset')
        self.dw_preset_list_cb = wx.ComboBox(self,  size=(150, 30), choices = [])
        self.datawall_module_l = wx.StaticText(self,  label='module')
        self.dw_module_list_cb = wx.ComboBox(self,  size=(150, 30), choices = get_module_options("datawall_", "graph_modules"))
        self.module_dw_btn = wx.Button(self, label='Make', size=(60,25))
        self.module_dw_btn.Bind(wx.EVT_BUTTON, self.make_datawall_from_module)

        # graphs
        self.local_simple_line = wx.Button(self, label='Simple Line Graph')
        self.local_simple_line.Bind(wx.EVT_BUTTON, self.local_simple_line_go)
        self.local_color_line = wx.Button(self, label='Color Line Graph')
        self.local_color_line.Bind(wx.EVT_BUTTON, self.local_color_line_go)
        self.local_simple_bar = wx.Button(self, label='Simple Bar Graph')
        self.local_simple_bar.Bind(wx.EVT_BUTTON, self.local_simple_bar_go)
        self.local_box_plot = wx.Button(self, label='Hourly Box Plot Graph')
        self.local_box_plot.Bind(wx.EVT_BUTTON, self.local_box_plot_go)
        self.over_threasholds_by_hour = wx.Button(self, label='Threashold by hour')
        self.over_threasholds_by_hour.Bind(wx.EVT_BUTTON, self.over_threasholds_by_hour_go)
        self.threasholds_pie = wx.Button(self, label='Threashold Pie')
        self.threasholds_pie.Bind(wx.EVT_BUTTON, self.threasholds_pie_go)
        self.dividied_daily = wx.Button(self, label='Divided Daily')
        self.dividied_daily.Bind(wx.EVT_BUTTON, self.divided_daily_go)
        self.local_simple_line.Disable()
        self.local_color_line.Disable()
        self.local_simple_bar.Disable()
        self.local_box_plot.Disable()
        self.over_threasholds_by_hour.Disable()
        self.threasholds_pie.Disable()
        self.dividied_daily.Disable()
        self.value_diff_graph = wx.Button(self, label='Value Diff Graph')
        self.value_diff_graph.Bind(wx.EVT_BUTTON, self.value_diff_graph_go)
        self.log_time_diff_graph = wx.Button(self, label='Time Diff Graph')
        self.log_time_diff_graph.Bind(wx.EVT_BUTTON, self.log_time_diff_graph_go)
        self.switch_log_graph = wx.Button(self, label='Switch Log Graph')
        self.switch_log_graph.Bind(wx.EVT_BUTTON, self.switch_log_graph_go)

        # Sizers
        # options used when graphing locally
        valset_1_len_sizer = wx.BoxSizer(wx.HORIZONTAL)
        valset_1_len_sizer.Add(self.valset_1_len_l, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_len_sizer.Add(self.valset_1_len, 0, wx.ALL|wx.EXPAND, 3)

        valset_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        valset_name_sizer.Add(self.valset_1_name, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_text_sizer = wx.BoxSizer(wx.VERTICAL)
        valset_1_text_sizer.Add(valset_1_len_sizer, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_text_sizer.Add(valset_name_sizer, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        valset_1_sizer.Add(self.num_of_logs_loaded, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        valset_1_sizer.Add(self.valset_1_loaded, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_sizer.Add(valset_1_text_sizer, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_sizer.Add(self.set_log_btn, 0, wx.ALL|wx.EXPAND, 3)
        valset_1_sizer.Add(self.clear_log_btn, 0, wx.ALL|wx.EXPAND, 3)
        # data import sizers
        graph_preset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        graph_preset_sizer.Add(self.graph_presets_cb, 0, wx.ALL|wx.EXPAND, 3)
        graph_preset_sizer.Add(self.graph_preset_all, 0, wx.ALL|wx.EXPAND, 3)
        module_sucker_sizer = wx.BoxSizer(wx.HORIZONTAL)
        module_sucker_sizer.Add(self.module_sucker_cb, 0, wx.ALL|wx.EXPAND, 3)
        module_sucker_sizer.Add(self.module_sucker_go_btn, 0, wx.ALL|wx.EXPAND, 3)
        # graph sizers
        module_graph_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        module_graph_sizer.Add(self.refresh_module_graph_btn, 0, wx.ALL, 3)
        module_graph_sizer.Add(self.module_graph_choice, 0, wx.ALL|wx.EXPAND, 3)
        module_graph_sizer.Add(self.module_graph_btn, 0, wx.ALL, 3)
        module_animate_settings_sizer = wx.FlexGridSizer(2, 2, 0, 5)
        module_animate_settings_sizer.AddMany( [(self.animate_show_time_period_l, 0, wx.ALIGN_RIGHT),
            (self.animate_show_time_period_tc, 0),
            (self.animate_roll_speed_l, 0, wx.ALIGN_RIGHT),
            (self.animate_roll_speed_tc, 0)])
        module_animate_main_sizer = wx.BoxSizer(wx.VERTICAL)
        module_animate_main_sizer.Add(self.animate_module, 0, wx.ALL|wx.EXPAND, 3)
        module_animate_main_sizer.Add(module_animate_settings_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        # datawall
        datawall_preset_list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        datawall_preset_list_sizer.Add(self.datawall_preset_l, 0, wx.ALL, 3)
        datawall_preset_list_sizer.Add(self.dw_preset_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        datawall_module_list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        datawall_module_list_sizer.Add(self.datawall_module_l, 0, wx.ALL, 3)
        datawall_module_list_sizer.Add(self.dw_module_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        datawall_sizer = wx.BoxSizer(wx.VERTICAL)
        datawall_sizer.Add(self.datawall_title_text, 0, wx.ALL, 3)
        datawall_sizer.Add(datawall_preset_list_sizer, 0, wx.ALL, 3)
        datawall_sizer.Add(datawall_module_list_sizer, 0, wx.ALL, 3)
        datawall_sizer.Add(self.module_dw_btn, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        # local opts size
        local_opts_sizer = wx.BoxSizer(wx.VERTICAL)
        local_opts_sizer.Add(valset_1_sizer, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(self.download_log_cb, 0, wx.RIGHT|wx.ALIGN_RIGHT, 30)
        local_opts_sizer.Add(self.data_title_text, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(self.preset_text, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(graph_preset_sizer, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(self.select_log_btn, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.module_sucker_text, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(module_sucker_sizer, 0, wx.ALL, 3)
        local_opts_sizer.AddStretchSpacer(1)
        local_opts_sizer.Add(self.graph_title_text, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(module_graph_sizer, 0, wx.ALL, 3)
        local_opts_sizer.Add(module_animate_main_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        local_opts_sizer.Add(self.graph_module_settings, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.module_options_list_ctrl, 0, wx.ALL|wx.EXPAND, 3)
        local_opts_sizer.Add(datawall_sizer, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_simple_line, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_color_line, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_simple_bar, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_box_plot, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.over_threasholds_by_hour, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.threasholds_pie, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.dividied_daily, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.value_diff_graph, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.log_time_diff_graph, 0, wx.ALL, 3)
        local_opts_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(5, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        local_opts_sizer.Add(self.switch_log_graph, 0, wx.ALL, 3)
        # sizers used for graphing on pigrow
        make_graph_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        make_graph_sizer.Add(self.make_graph_btn, 0, wx.ALL|wx.EXPAND, 3)
        make_graph_sizer.Add(self.download_graph, 0, wx.ALL|wx.EXPAND, 3)
        # main sizer
        self.line1 = wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL)
        self.line2 = wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL)
        self.line4 = wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(make_graph_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.line1, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.pigraph_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.line2, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.script_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.select_script_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.get_opts_tb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.line3, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.opts_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.command_line_opts_value_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.opts_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.add_arg_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.extra_args_label, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.extra_args, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.line4, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(make_graph_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(local_opts_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(self.main_sizer)

        # hideing all pigrow graphing UI elements until graph on pigrow is selected
        self.hide_make_on_pi_ui_elements()
        self.hide_make_local_ui_elements()
        # making blank lists for compare graphs to use
        shared_data.first_value_set = []
        shared_data.first_date_set = []

    def hide_make_on_pi_ui_elements(self):
        self.pigraph_text.Hide()
        self.script_text.Hide()
        self.select_script_cb.Hide()
        self.get_opts_tb.Hide()
        self.extra_args_label.Hide()
        self.extra_args.Hide()
        self.make_graph_btn.Hide()
        self.download_graph.Hide()
        self.line1.Hide()
        self.line2.Hide()
        self.line3.Hide()
        self.line4.Hide()
        self.blank_options_ui_elements()

    def show_make_on_pi_ui_elements(self):
        self.pigraph_text.Show()
        self.script_text.Show()
        self.select_script_cb.Show()
        self.get_opts_tb.Show()
        self.extra_args_label.Show()
        self.extra_args.Show()
        self.make_graph_btn.Show()
        self.download_graph.Show()
        self.line1.Show()
        self.line2.Show()
        self.line3.Show()
        self.line4.Show()

    def hide_make_local_ui_elements(self):
        self.select_log_btn.Hide()
        self.preset_text.Hide()
        self.graph_presets_cb.Hide()
        self.graph_preset_all.Hide()
        # graphs
        self.local_simple_line.Hide()
        self.local_color_line.Hide()
        self.local_simple_bar.Hide()
        self.local_box_plot.Hide()
        self.over_threasholds_by_hour.Hide()
        self.threasholds_pie.Hide()
        self.dividied_daily.Hide()
        self.log_time_diff_graph.Hide()
        self.value_diff_graph.Hide()
        self.switch_log_graph.Hide()
        #
        self.module_graph_choice.Hide()
        self.module_graph_btn.Hide()
        self.animate_module.Hide()
        self.animate_show_time_period_l.Hide()
        self.animate_show_time_period_tc.Hide()
        self.animate_roll_speed_l.Hide()
        self.animate_roll_speed_tc.Hide()
        self.graph_module_settings.Hide()
        self.module_options_list_ctrl.Hide()
        self.refresh_module_graph_btn.Hide()
        # datawall
        self.datawall_title_text.Hide()
        self.datawall_preset_l.Hide()
        self.dw_preset_list_cb.Hide()
        self.datawall_module_l.Hide()
        self.dw_module_list_cb.Hide()
        self.module_dw_btn.Hide()
        #
        self.data_title_text.Hide()
        self.graph_title_text.Hide()
        self.valset_1_loaded.Hide()
        self.num_of_logs_loaded.Hide()
        self.valset_1_name.Hide()
        self.download_log_cb.Hide()
        self.valset_1_len_l.Hide()
        self.valset_1_len.Hide()
        self.module_sucker_text.Hide()
        self.module_sucker_cb.Hide()
        self.module_sucker_go_btn.Hide()
        self.set_log_btn.Hide()
        self.clear_log_btn.Hide()

        try:
            MainApp.graphing_info_pannel.hide_data_extract()
            MainApp.graphing_info_pannel.hide_graph_settings()
        except:
            pass

    def show_make_local_ui_elements(self):
        self.select_log_btn.Show()
        self.preset_text.Show()
        self.graph_presets_cb.Show()
        self.graph_preset_all.Show()
        self.local_simple_line.Show()
        self.local_color_line.Show()
        self.local_simple_bar.Show()
        self.local_box_plot.Show()
        self.over_threasholds_by_hour.Show()
        self.threasholds_pie.Show()
        self.dividied_daily.Show()
        self.log_time_diff_graph.Show()
        self.value_diff_graph.Show()
        self.switch_log_graph.Show()
        self.module_graph_choice.Show()
        self.module_graph_btn.Show()
        self.animate_module.Show()
        self.animate_show_time_period_l.Show()
        self.animate_show_time_period_tc.Show()
        self.animate_roll_speed_l.Show()
        self.animate_roll_speed_tc.Show()
        self.graph_module_settings.Show()
        self.module_options_list_ctrl.Show()
        self.refresh_module_graph_btn.Show()
        # datawall
        self.datawall_title_text.Show()
        self.datawall_preset_l.Show()
        self.dw_preset_list_cb.Show()
        self.datawall_module_l.Show()
        self.dw_module_list_cb.Show()
        self.module_dw_btn.Show()
        #
        self.data_title_text.Show()
        self.graph_title_text.Show()
        self.valset_1_loaded.Show()
        self.num_of_logs_loaded.Show()
        self.valset_1_name.Show()
        self.download_log_cb.Show()
        self.valset_1_len_l.Show()
        self.valset_1_len.Show()
        self.module_sucker_text.Show()
        self.module_sucker_cb.Show()
        self.module_sucker_go_btn.Show()
        self.set_log_btn.Show()
        self.clear_log_btn.Show()

    def enable_value_graphs(self):
        self.local_simple_line.Enable()
        self.local_color_line.Enable()
        self.local_simple_bar.Enable()
        self.local_box_plot.Enable()
        self.over_threasholds_by_hour.Enable()
        self.threasholds_pie.Enable()
        self.dividied_daily.Enable()
        self.value_diff_graph.Enable()

    def disable_value_graphs(self):
        self.local_simple_line.Disable()
        self.local_color_line.Disable()
        self.local_simple_bar.Disable()
        self.local_box_plot.Disable()
        self.over_threasholds_by_hour.Disable()
        self.threasholds_pie.Disable()
        self.dividied_daily.Disable()
        self.value_diff_graph.Disable()

    def redownload_log(self):
        current_log = shared_data.log_to_load
        pi_logs, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/logs/")
        log_name = os.path.split(current_log)[1]
        if log_name in pi_logs:
            remote_file = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/" + log_name
            MainApp.localfiles_ctrl_pannel.download_file_to_folder(remote_file, "logs/" + log_name)
        else:
            print(" - Log file not found on pigrow")

    def graph_engine_combo_go(self, e):
        # combo box selects if you want to make graphs on pi or locally
        # then shows the relevent UI elements for that option.
        graph_mode = self.graph_cb.GetValue()
        if graph_mode == 'Pigrow':
            # select ui elements
            self.hide_make_local_ui_elements()
            self.show_make_on_pi_ui_elements()
            # Find graphing scripts and list them in combo box
            select_script_opts = self.get_graphing_scripts()
            for x in select_script_opts:
                self.select_script_cb.Append(x)
        elif graph_mode == 'local':
            self.hide_make_on_pi_ui_elements()
            self.show_make_local_ui_elements()
            self.discover_graph_presets()
            self.discover_datawall_preset_list()
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

    def read_example_line_from_file(self, dont_set_ui=False):
        print(" -- Reading log to get example line")
        with open(shared_data.log_to_load) as f:
            log_to_graph = f.read()
        log_to_graph = log_to_graph.splitlines()
        if len(log_to_graph) == 0:
            print(" --- Log file is empty")
        MainApp.graphing_info_pannel.example_line.SetLabel(log_to_graph[0])
        if not dont_set_ui == True:
            MainApp.graphing_info_pannel.clear_and_reset_fields()
            split_chr_choices = self.get_split_chr(log_to_graph[0])
            if len(split_chr_choices) == 1:
                MainApp.graphing_info_pannel.split_character_tc.SetValue(split_chr_choices[0])
            else:
                MainApp.graphing_info_pannel.split_character_tc.SetValue(">")

    # Make locally controlls
    def select_log_click(self, e):
        wildcard = "TXT and LOG files (*.txt;*.log)|*.txt;*.log"
        openFileDialog = wx.FileDialog(self, "Select log file", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        log_path = os.path.join(localfiles_info_pnl.local_path, "logs")
        openFileDialog.SetDirectory(log_path)
        openFileDialog.SetMessage("Select log file to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("Cancelled")
            return None
        log_path = openFileDialog.GetPath()
        print(" - Using ", log_path, " to make a graph locally" )
        MainApp.graphing_info_pannel.show_data_extract()
        MainApp.graphing_info_pannel.show_graph_settings()
        MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue('none')
        # write path to shared data
        shared_data.log_to_load = log_path
        shared_data.first_valueset_name = os.path.split(log_path)[1]
        # Open log file
        self.read_example_line_from_file()

    def set_dates_to_log(self):
        '''
        This is used when selecting 'custom' from the limit date by dropdown box.
        '''
        date_list = MainApp.graphing_info_pannel.read_log_date_and_value(limit_by_date = False,  date_only = True)
        first_date = date_list[0]
        last_date = date_list[-1]
        MainApp.graphing_info_pannel.start_date_picer.SetRange(first_date, last_date)
        MainApp.graphing_info_pannel.start_date_picer.SetValue(first_date)
        MainApp.graphing_info_pannel.start_time_picer.SetValue(first_date)
        MainApp.graphing_info_pannel.end_date_picer.SetRange(first_date, last_date)
        MainApp.graphing_info_pannel.end_time_picer.SetValue(last_date)
        MainApp.graphing_info_pannel.end_date_picer.SetValue(last_date)

    def get_split_chr(self, line):
        non_split_characters = ["-", ":", ".", ",", " ", "_"]
        non_split_characters += ["a","b","c","d","e","f","g","h","i", "j", "k", "l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        split_chr_choices = []
        for chr in line:
            if not chr.isdigit() and not chr.lower() in non_split_characters:
                if not chr in split_chr_choices:
                    split_chr_choices.append(chr)
        return split_chr_choices

    def clear_log_click(self, e):
        shared_data.list_of_datasets = []
        shared_data.first_valueset_name = ""
        self.valset_1_name.SetLabel("-")
        self.disable_value_graphs()
        self.valset_1_loaded.SetBitmap(shared_data.no_log_image)
        self.num_of_logs_loaded.SetLabel("0")
        self.valset_1_len.SetLabel("0")

    def set_log_click(self, e):
        #
        if self.download_log_cb.GetValue() == True:
            self.redownload_log()
        #print("number of datasets", len(shared_data.list_of_datasets))
        val_method = MainApp.graphing_info_pannel.value_pos_cb.GetValue()
        if val_method == 'match text':
            print(" -- using text matching to gather data")
            date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_with_text_match(numbers_only=True)
        else:
            date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        #
        if len(date_list) == len(value_list) and len(date_list) == len(key_list) and len(date_list) > 0:
            self.enable_value_graphs()
            shared_data.list_of_datasets.append([date_list, value_list, key_list])
            self.valset_1_loaded.SetBitmap(shared_data.yes_log_image)
            self.valset_1_len.SetLabel(str(len(date_list)))
            self.valset_1_name.SetLabel(shared_data.first_valueset_name)
            self.num_of_logs_loaded.SetLabel(str(len(shared_data.list_of_datasets)))
            MainApp.graphing_info_pannel.show_hide_date_extract_btn.SetLabel("hide")
            MainApp.graphing_info_pannel.show_hide_date_extract_click("e")
            MainApp.window_self.Layout()
        else:
            print(" - problem with the lists returned from trying to load log.... ")
            if len(date_list) == 0:
                #shared_data.list_of_datasets = shared_data.list_of_datasets[:-1]
                if len(shared_data.list_of_datasets) == 0:
                    self.valset_1_loaded.SetBitmap(shared_data.no_log_image)
                else:
                    self.valset_1_loaded.SetBitmap(shared_data.yes_log_image)
            else:
                self.num_of_logs_loaded.SetLabel(str(len(shared_data.list_of_datasets)))
                self.valset_1_len.SetLabel(str(len(date_list)) + " " + str(len(value_list)) + " " + str(len(key_list)))
                self.valset_1_loaded.SetBitmap(shared_data.warn_log_image)


    # graph presets

    def discover_graph_presets(self, e=""):
        show_all = self.graph_preset_all.GetValue()

        graph_presets = os.listdir(shared_data.graph_presets_path)
        self.graph_presets_cb.Clear()
        graph_preset_list = []
        for file in graph_presets:
            if show_all == False:
                current_preset_path = os.path.join(shared_data.graph_presets_path, file)
                log_path = self.get_log_path_from_preset(current_preset_path)
                if not log_path == None:
                    if os.path.isfile(log_path) == True:
                        graph_preset_list.append(file)
            else:
                graph_preset_list.append(file)
        graph_preset_list.sort()
        self.graph_presets_cb.Append(graph_preset_list)

    def get_log_path_from_preset(self, graph_preset_path):
        local_logs_path = os.path.join(localfiles_info_pnl.local_path, "logs")
        with open(graph_preset_path) as f:
            graph_presets = f.read()
        graph_presets = graph_presets.splitlines()
        for line in graph_presets:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos + 1:]
                if key == "log_path":
                    log_path = os.path.join(local_logs_path, value)
                    return log_path
        return None

    def preset_all_click(self, e):
        self.discover_graph_presets()

    def save_data_extract_click(self, e=""):
        # log location
        log_path = shared_data.log_to_load
        file_text = "log_path=" + log_path + "\n"
        # grab settings from ui
        split_chr = MainApp.graphing_info_pannel.split_character_tc.GetValue()
        if not split_chr == "":
            file_text += "split_chr=" + split_chr +"\n"
        # date
        date_pos = MainApp.graphing_info_pannel.date_pos_cb.GetValue()
        if not date_pos == "":
            file_text += "date_pos=" + date_pos + "\n"
        date_split = MainApp.graphing_info_pannel.date_pos_split_tc.GetValue()
        if not date_split == "":
            file_text += "date_split=" + date_split + "\n"
        date_split_pos = MainApp.graphing_info_pannel.date_pos_split_cb.GetSelection()
        if not date_split_pos == "":
            file_text += "date_split_pos=" + str(date_split_pos) + "\n"
        # value
        value_pos = MainApp.graphing_info_pannel.value_pos_cb.GetValue()
        if not value_pos == "":
            file_text += "value_pos=" + value_pos + "\n"
        value_split = MainApp.graphing_info_pannel.value_pos_split_tc.GetValue()
        if not value_split == "":
            file_text += "value_split=" + value_split + "\n"
        value_split_pos = MainApp.graphing_info_pannel.value_pos_split_cb.GetSelection()
        if not value_split_pos == "":
            file_text += "value_split_pos=" + str(value_split_pos) + "\n"
        value_rem = MainApp.graphing_info_pannel.rem_from_val_tc.GetValue()
        if not value_rem == "":
            file_text += "value_rem=" + value_rem + "\n"
        # key
        key_pos = MainApp.graphing_info_pannel.key_pos_cb.GetValue()
        if not key_pos == "":
            file_text += "key_pos=" + key_pos + "\n"
        key_split = MainApp.graphing_info_pannel.key_pos_split_tc.GetValue()
        if not key_split == "":
            file_text += "key_split=" + key_split + "\n"
        key_split_pos = MainApp.graphing_info_pannel.key_pos_split_cb.GetValue()
        if not key_split_pos == "":
            file_text += "key_split_pos=" + key_split_pos + "\n"
        key_match = MainApp.graphing_info_pannel.key_matches_tc.GetValue()
        if not key_match == "":
            file_text += "key_match=" + key_match + "\n"
        key_manual = MainApp.graphing_info_pannel.key_manual_tc.GetValue()
        if not key_manual == "":
            file_text += "key_manual=" + key_manual + "\n"
        # date
        limit_date = MainApp.graphing_info_pannel.limit_date_to_last_cb.GetValue()
        if not limit_date == "":
            file_text += "limit_date=" + limit_date + "\n"
        if limit_date == "custom":
            first_time = MainApp.graphing_info_pannel.start_time_picer.GetValue()
            first_date = MainApp.graphing_info_pannel.start_date_picer.GetValue()
            first_datetime = str(datetime.datetime(year = first_date.year, month = first_date.month + 1, day = first_date.day, hour = first_time.hour, minute = first_time.minute, second = first_time.second))
            if "." in first_datetime:
                first_datetime = first_datetime.split(".")[0]
            last_time = MainApp.graphing_info_pannel.end_time_picer.GetValue()
            last_date = MainApp.graphing_info_pannel.end_date_picer.GetValue()
            last_datetime = str(datetime.datetime(year = last_date.year, month = last_date.month + 1, day = last_date.day, hour = last_time.hour, minute = last_time.minute, second = last_time.second))
            if "." in last_datetime:
                last_datetime = last_datetime.split(".")[0]
            file_text += "start_time=" + first_datetime + "\n"
            file_text += "end_time=" + last_datetime + "\n"
        print(file_text)
        # ask name
        msg = "Name of preset"
        filename_dbox = wx.TextEntryDialog(self, msg, "Name Preset", "")
        if filename_dbox.ShowModal() == wx.ID_OK:
            new_preset_name = filename_dbox.GetValue()
            new_preset_name = new_preset_name.strip().replace(" ", "_")
            if not (".txt") in new_preset_name.lower():
                new_preset_name += ".txt"
            # check if it already exists and confirm overwrite
            graph_preset_path = os.path.join(shared_data.graph_presets_path, new_preset_name)
            if os.path.isfile(graph_preset_path):
                dbox = wx.MessageDialog(self, "Preset of that name already exists, overwrite it?", "Overwrite?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                dbox.Destroy()
                if not (answer == wx.ID_OK):
                    return "cancelled"
            # save to graph presets
            with open(graph_preset_path, "w") as f:
                f.write(file_text)


    def graph_preset_cb_go(self ,e):
        # blank settings from prior use
        limit_setting = MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue('none')
        # load presets
        graph_option = self.graph_presets_cb.GetValue()
        MainApp.graphing_info_pannel.show_data_extract()
        MainApp.graphing_info_pannel.show_graph_settings()
        print("Want's to use preset from " + graph_option)
        graph_preset_path = os.path.join(shared_data.graph_presets_path, graph_option)
        with open(graph_preset_path) as f:
            graph_presets = f.read()
        graph_presets = graph_presets.splitlines()
        #
        #
        ###  The dictionary below should be removed as it's now obsolete
        #
        #
        preset_settings = {}
        log_preset_setting_list = []
        for line in graph_presets:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos + 1:]
                preset_settings[key]=value
                text_string = key + ":" + value
                log_preset_setting_list.append(text_string)
        #
        # set and load log
        if "log_path" in preset_settings:
            local_logs_path = os.path.join(localfiles_info_pnl.local_path, "logs")
            log_path = os.path.join(local_logs_path, preset_settings["log_path"])
            shared_data.first_valueset_name = graph_option
            shared_data.log_to_load = log_path
            self.read_example_line_from_file(dont_set_ui=True)
        else:
            print("Log path not found in presets file")
        # set the UI boxes based on settings from preset file
        self.set_data_extraction_settings_from_text(log_preset_setting_list)

    # datawall

    def discover_datawall_preset_list(self, e=""):
        dw_presets = os.listdir(shared_data.datawall_presets_path)
        self.dw_preset_list_cb.Clear()
        dw_presets.sort()
        self.dw_preset_list_cb.Append(dw_presets)


    def get_graph_size_from_ui(self):
        try:
            size_h = int(MainApp.graphing_info_pannel.size_h_cb.GetValue())
        except:
            size_h = 10
        try:
            size_v = int(MainApp.graphing_info_pannel.size_v_cb.GetValue())
        except:
            raise
            size_v = 10
        if size_v > 655:
            size_v = 655
            MainApp.graphing_info_pannel.size_v_cb.SetValue("655")
        if size_h > 655:
            size_h = 655
            MainApp.graphing_info_pannel.size_h_cb.SetValue("655")
        return size_h, size_v

    def module_graph_choice_go(self, e):
        self.graph_module_settings_click("e")

    def refresh_module_graph_go(self, e):
        #
        self.module_graph_choice.Clear()
        module_list = get_module_options("graph_", "graph_modules")
        self.module_graph_choice.Append(module_list)
        #
        self.module_sucker_cb.Clear()
        module_list = get_module_options("sucker_", "graph_modules")
        self.module_sucker_cb.Append(module_list)

    def graph_module_settings_click(self, e):
        self.module_options_list_ctrl.DeleteAllItems()
        if self.graph_module_settings.GetValue() == True:
            print("Reading options from module...")
            module_name = self.module_graph_choice.GetValue()
            module_name = "graph_" + module_name
            if module_name in sys.modules:
                del sys.modules[module_name]
            exec("from " + module_name + " import read_graph_options", globals())
            gm_options_dict = read_graph_options()
            index = 0
            for key, value in gm_options_dict.items():
                self.module_options_list_ctrl.InsertItem(index, key)
                self.module_options_list_ctrl.SetItem(index, 1, value)
                index = index + 1

    def onDoubleClick_gm_opt(self, e):
        index =  e.GetIndex()
        #get info for dialogue box
        key = self.module_options_list_ctrl.GetItem(index, 0).GetText()
        val = self.module_options_list_ctrl.GetItem(index, 1).GetText()
        msg_text = " Select the new value for " + key
        setval_dbox = wx.TextEntryDialog(self, msg_text, 'Set Graph Module Option', val)
        if setval_dbox.ShowModal() == wx.ID_OK:
            newval = setval_dbox.GetValue()
            self.module_options_list_ctrl.SetItem(index, 1, newval)
        setval_dbox.Destroy()

    def make_gm_extra_settings_dict(self):
        '''
        Reads the graph module settings table and returns a list of settings
        '''
        #
        if not self.graph_module_settings.GetValue() == True:
            return {}
        gm_options_dict = {}
        for index in range(0, self.module_options_list_ctrl.GetItemCount()):
            key = self.module_options_list_ctrl.GetItem(index, 0).GetText()
            val = self.module_options_list_ctrl.GetItem(index, 1).GetText()
            gm_options_dict[key]=val
        return gm_options_dict
        #

    def make_graph_from_imported_module(self, e, file_name=""):
        print("Want's to create a graph using a external module...  ")
        # read data from log
        count_list = ""
        for x in shared_data.list_of_datasets:
            count_list += " " + str(len(x[0]))
        if len(shared_data.list_of_datasets) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a graph from a module using  " + str(len(count_list)) + " values")
        # read graph settings from ui boxes
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        dangercold = MainApp.graphing_info_pannel.danger_low_tc.GetValue()
        toocold = MainApp.graphing_info_pannel.low_tc.GetValue()
        toohot = MainApp.graphing_info_pannel.high_tc.GetValue()
        dangerhot = MainApp.graphing_info_pannel.danger_high_tc.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        module_name = self.module_graph_choice.GetValue()
        # create name for graph based on the module name
        if file_name == "":
            file_name = module_name + "_graph.png"
        graph_path = os.path.join(localfiles_info_pnl.local_path, file_name)
        # set module_name to have it's full value
        module_name = "graph_" + module_name
        # unload the old module to bring in any changes to the script since it was loaded
        if module_name in sys.modules:
            del sys.modules[module_name]
        # import the make_graph function as a module
        exec("from " + module_name + " import make_graph", globals())
        # creaty the graph using the imported module
        extra = self.make_gm_extra_settings_dict()  #this is temporary testing
        make_graph(shared_data.list_of_datasets, graph_path, ymax, ymin, size_h, size_v, dangerhot, toohot, toocold, dangercold, extra)
        # Tell the user and show the graph
        print("module_graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        MainApp.status.write_bar("ready...")

    def animate_module_click(self, e):
        MainApp.status.write_bar(" Creating an animation...")
        # read graph settings from ui boxes
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        dangercold = MainApp.graphing_info_pannel.danger_low_tc.GetValue()
        toocold = MainApp.graphing_info_pannel.low_tc.GetValue()
        toohot = MainApp.graphing_info_pannel.high_tc.GetValue()
        dangerhot = MainApp.graphing_info_pannel.danger_high_tc.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        module_name = self.module_graph_choice.GetValue()
        # set module_name to have it's full value
        full_module_name = "graph_" + module_name
        # unload the old module to bring in any changes to the script since it was loaded
        if full_module_name in sys.modules:
            del sys.modules[full_module_name]
        # import the make_graph function as a module
        exec("from " + full_module_name + " import make_graph", globals())
        #
        ## Check user really intended to do this
        #
        # get name, set folder
        def_graph_base_name = "ani_" + module_name
        ani_name_dbox = wx.TextEntryDialog(self, 'Choose a name for your animation', 'Name Animated Graph', def_graph_base_name)
        if ani_name_dbox.ShowModal() == wx.ID_OK:
            graph_base_name = ani_name_dbox.GetValue()
        else:
            return "cancelled"
        ani_name_dbox.Destroy()
        graph_folder_path = os.path.join(localfiles_info_pnl.local_path, graph_base_name)
        if not os.path.isdir(graph_folder_path):
            os.makedirs(graph_folder_path)
        #
        ## The Animation business...
        #
        # set start conditions
        roll_speed = int(self.animate_roll_speed_tc.GetValue())
        roll_speed_td = datetime.timedelta(minutes=roll_speed)
        roll_speed_in_seconds = roll_speed * 60
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        start_of_frame = date_list[0]
        # determine how many frames to make
        show_time_period = int(self.animate_show_time_period_tc.GetValue())
        if show_time_period == 0:
            print(" --------- special mode activated --------- ")
            special_mode = True
            print(" ------------------++++-------------------- ")
        else:
            special_mode = False
            print(" ________normal mode___________ ")
        show_time_period = datetime.timedelta(hours=show_time_period)
        end_of_frame = date_list[0] + show_time_period
        time_range_of_whole_set = (date_list[-1] - show_time_period) - date_list[0]
        time_range_of_whole_set = time_range_of_whole_set.total_seconds()
        amount_of_frames = int(round(time_range_of_whole_set / roll_speed_in_seconds, 0))
        print("amount of frames ", amount_of_frames)
        # find min max values so we can stabalise the graph output
        if ymin == "" or ymax == "":
            ymin = value_list[0]
            ymax = value_list[0]
            for x in value_list:
                if x > ymax:
                    ymax = x
                if x < ymin:
                    ymin = x
        #
        ## Cycle through each frame making the graphs for it
        #
        for frame_num in range(0, amount_of_frames):
            MainApp.status.write_bar(" Creating frame " + str(frame_num) + " of " + str(amount_of_frames))
            if special_mode == False:
                # create datasets for each frame using rolling start and end dates
                list_of_trimmed_data_sets = []
                start_of_frame = start_of_frame + roll_speed_td
                end_of_frame = end_of_frame + roll_speed_td
                for data_set in shared_data.list_of_datasets:
                    trimmed_date_list  = []
                    trimmed_value_list = []
                    trimmed_key_list   = []
                    date_list   = data_set[0]
                    value_list  = data_set[1]
                    key_list    = data_set[2]
                    for x in range(len(date_list)):
                        if date_list[x] > start_of_frame and date_list[x] < end_of_frame:
                            trimmed_date_list.append(date_list[x])
                            trimmed_value_list.append(value_list[x])
                            trimmed_key_list.append(key_list[x])
                    data_lists = [trimmed_date_list, trimmed_value_list, trimmed_key_list]
                    list_of_trimmed_data_sets.append(data_lists)
            else:
                print(" - Using special mode")
                # wrap up single log entries and send them to the grapher
                start_of_frame = start_of_frame + roll_speed_td
                current_log_position = 0
                found_next = False
                while found_next == False:
                    if date_list[current_log_position] >= start_of_frame:
                        found_next = True
                    else:
                        current_log_position = current_log_position + 1
                    if current_log_position > len(date_list):
                        current_log_position = len(date_list)
                        found_next = True
                trimmed_date_list  = [date_list[current_log_position]]
                trimmed_value_list = [value_list[current_log_position]]
                trimmed_key_list   = [key_list[current_log_position]]
                list_of_trimmed_data_sets = [[trimmed_date_list, trimmed_value_list, trimmed_key_list]]

            #
            # Create Frame's File Name
            rolling_last_datetime = str(datetime.datetime.timestamp(trimmed_date_list[-1])).split(".")[0]
            current_graph_name = graph_base_name + "_" + str(rolling_last_datetime) + ".png"
            current_graph_filepath = os.path.join(graph_folder_path, current_graph_name)
            #
            extra = self.make_gm_extra_settings_dict()
            print(" - Creating " + current_graph_filepath)
            make_graph(list_of_trimmed_data_sets, current_graph_filepath, ymax, ymin, size_h, size_v, dangerhot, toohot, toocold, dangercold, extra)


        # Tell the user and show the graph
        MainApp.graphing_info_pannel.show_local_graph(current_graph_filepath)
        MainApp.status.write_bar("ready...")

    def suck_from_imported_module(self, e):
        module_name = self.module_sucker_cb.GetValue()
        # import sucker function from module
        module_name = "sucker_" + module_name
        if module_name in sys.modules:
            del sys.modules[module_name]
        exec("from " + module_name + " import run_sucker", globals())
        # run the function and set the data to the logs
        values, dates, keys = run_sucker()
        print(" - Sucker added ", len(values), len(dates), len(keys), " data points.")
        shared_data.first_valueset_name = module_name
        shared_data.list_of_datasets.append([dates, values, keys])
        self.enable_value_graphs()
        if len(dates) == len(values) and len(dates) == len(keys) and len(dates) > 0:
            self.valset_1_loaded.SetBitmap(shared_data.yes_log_image)
            self.num_of_logs_loaded.SetLabel(str(len(shared_data.list_of_datasets)))
            self.valset_1_len.SetLabel(str(len(dates)))
            self.valset_1_name.SetLabel(module_name)
            MainApp.window_self.Layout()
        else:
            print(" - These lists either aren't the same length or are all empty, that could be a problem for the graph modules.... ")
            self.valset_1_loaded.SetBitmap(shared_data.warn_log_image)

    # make graphs
    def local_simple_line_go(self, e):
        print("Want's to create a simple line graph...  ")
        # read data from log
        date_list = shared_data.list_of_datasets[0][0]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a simple line graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # start making the graph
        fig = plt.gcf()
        fig.canvas.set_window_title('Simple Line Graph')
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        ax.set_prop_cycle(color=['black', 'blue', 'red', 'green'])
        for x in shared_data.list_of_datasets:
            date_list = x[0]
            value_list = x[1]
            key_list = x[2]
            ax.plot(date_list, value_list, label=key_list[0], lw=1)
        ax.xaxis_date()

        fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "line_graph.png")
        plt.savefig(graph_path)
        print("line graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def local_color_line_go(self, e):
        # read graph settings from ui boxes
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        dangercold = float(MainApp.graphing_info_pannel.danger_low_tc.GetValue())
        toocold = float(MainApp.graphing_info_pannel.low_tc.GetValue())
        toohot = float(MainApp.graphing_info_pannel.high_tc.GetValue())
        dangerhot = float(MainApp.graphing_info_pannel.danger_high_tc.GetValue())
        size_h, size_v = self.get_graph_size_from_ui()
        # read data from the log
        print("Want's to create a color line graph...")
        value_list = shared_data.first_value_set
        date_list = shared_data.first_date_set
        key_list = shared_data.first_keys_set
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a colour line graph from " + str(len(date_list)) + " values")
        # define graph space
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        # make the graph
        ax.plot(date_list, value_list, color='black', lw=2)
        # colour hot and cold porions of the graph
        value_list = np.array(value_list)
        if not dangercold == None:
            ax.fill_between(date_list, value_list, 0,where=value_list < dangercold, alpha=0.6, color='darkblue')
        if not toocold == None:
            ax.fill_between(date_list, value_list, 0,where=value_list < toocold, alpha=0.6, color='blue')
        if not toohot == None:
            ax.fill_between(date_list, value_list, 0,where=value_list > toohot, alpha=0.6, color='red')
        if not dangerhot == None:
            ax.fill_between(date_list, value_list, 0,where=value_list > dangerhot, alpha=0.6, color='darkred')
        # add titles and axis labels
        fig = plt.gcf()
        fig.canvas.set_window_title('Simple Line Graph')
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        # Y temp axis
        plt.ylabel(key_list[0])
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        # X date axis
        ax.xaxis_date()
        # i should write some code here to only show the parts of the date that are needed
        #ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%d-%b %H:%M'))
        fig.autofmt_xdate()
        # show or save graph
        #plt.show()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "line_graph.png")
        plt.savefig(graph_path)
        print("line graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def local_simple_bar_go(self, e):
        print("Want's to create a simple bar graph...  ")
        # read log
        date_list = shared_data.list_of_datasets[0][0]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a simple bar graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # define the graph space
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        for x in shared_data.list_of_datasets:
            date_list = x[0]
            value_list = x[1]
            key_list = x[2]
            ax.bar(date_list, value_list,width=0.01, linewidth = 1, alpha=0.5, label=key_list[0])
        if len(shared_data.list_of_datasets) > 1:
            ax.legend()
        else:
            plt.ylabel(key_list[0])
        ax.xaxis_date()
        fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "bar_graph.png")
        plt.savefig(graph_path)
        print("bar graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def over_threasholds_by_hour_go(self, e):
        # read log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a threasholds by hour graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        dangercold = float(MainApp.graphing_info_pannel.danger_low_tc.GetValue())
        toocold = float(MainApp.graphing_info_pannel.low_tc.GetValue())
        toohot = float(MainApp.graphing_info_pannel.high_tc.GetValue())
        dangerhot = float(MainApp.graphing_info_pannel.danger_high_tc.GetValue())
        size_h, size_v = self.get_graph_size_from_ui()
        # start making graph
        print("Making EpiphanyHermit's warningd by hour graph...")
        # Colors for the danger temps
        dangercoldColor = 'xkcd:purplish blue'
        toocoldColor = 'xkcd:light blue'
        toohotColor = 'xkcd:orange'
        dangerhotColor = 'xkcd:red'
        # Group the data by hour
        dangerhotArray = [0]*24
        toohotArray = [0]*24
        toocoldArray = [0]*24
        dangercoldArray = [0]*24
        for i in range(len(date_list)):
            h = int(date_list[i].strftime('%H'))
            if value_list[i] >= dangerhot:
                dangerhotArray[h] += 1
            elif value_list[i] >= toohot:
                toohotArray[h] += 1
            elif value_list[i] <= dangercold:
                dangercoldArray[h] += 1
            elif value_list[i] <= toocold:
                toocoldArray[h] += 1
        ind = np.arange(24)  # the x locations for the groups
        width = 0.25  # the width of the bars
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        rects1 = ax.bar(ind - width/2, dangercoldArray, width, yerr=None, color=dangercoldColor, label='DC')
        rects2 = ax.bar(ind - width/4, toocoldArray, width, yerr=None, color=toocoldColor, label='TC')
        rects3 = ax.bar(ind + width/4, toohotArray, width, yerr=None, color=toohotColor, label='TH')
        rects4 = ax.bar(ind + width/2, dangerhotArray, width, yerr=None, color=dangerhotColor, label='DH')
        # Add some text for labels, title and custom x-axis tick labels, etc.
        fig.suptitle('Dangerous Values by Hour', fontsize=14, fontweight='bold')
        ax.set_ylabel('Counts')
        ax.set_title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10)
        ax.set_xticks(ind)
        labels = ('00:00', '01:00', '02:00', '03:00', '04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00')
        ax.set_xticklabels(labels,rotation=45)
        ax.legend()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "minmax_hour_plot.png")
        print("danger values graph created and saved to " + graph_path)
        plt.savefig(graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def threasholds_pie_go(self, e):
        # read the log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a threasholds pie from " + str(len(date_list)) + " values")
        # read settings from ui
        dangercold = float(MainApp.graphing_info_pannel.danger_low_tc.GetValue())
        toocold = float(MainApp.graphing_info_pannel.low_tc.GetValue())
        toohot = float(MainApp.graphing_info_pannel.high_tc.GetValue())
        dangerhot = float(MainApp.graphing_info_pannel.danger_high_tc.GetValue())
        # start making graph
        print("Making EpiphanyHermit's pie...")
        sliceColors = ['xkcd:red',
                       'xkcd:orange',
                       'xkcd:light green',
                       'xkcd:light blue',
                       'xkcd:purplish blue']

        tempThresholds = [('%.2f°' % dangerhot).replace(".00°","°")
            , ('%.2f°' % toohot).replace(".00°","°")
            , ('{:.2f}° < > {:.2f}°'.format(toohot,toocold)).replace(".00°","°")
            , ('%.2f°' % toocold).replace(".00°","°")
            , ('%.2f°' % dangercold).replace(".00°","°")]

        # Group the data by classification
        tempCount = [0,0,0,0,0]
        for i in range(len(date_list)):
            if value_list[i] >= dangerhot:
                tempCount[0] += 1
            elif value_list[i] >= toohot:
                tempCount[1] += 1
            elif value_list[i] <= dangercold:
                tempCount[4] += 1
            elif value_list[i] <= toocold:
                tempCount[3] += 1
            else:
                tempCount[2] += 1

        # The slices will be ordered and plotted counter-clockwise.
        temps = list()
        colors = list()
        for i in range(5):
            if tempCount[i] == 0:
                continue
            temps.append(tempCount[i])
            colors.append(sliceColors[i])

        plt.pie(temps, colors=colors, autopct='%1.1f%%', pctdistance=1.16)

        #draw a circle at the center of the pie
        centre_circle = plt.Circle((0,0), 0.75, color='black', fc='white',linewidth=0)
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        fig.suptitle('Value Groups', fontsize=14, fontweight='bold')
        plt.title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10, y=1.07)

        # Set aspect ratio to be equal so that pie is drawn as a circle.
        plt.axis('equal')

        # legend
        custom_lines = [Line2D([0], [0], color=sliceColors[0], lw=2),
                        Line2D([0], [0], color=sliceColors[1], lw=2),
                        Line2D([0], [0], color=sliceColors[2], lw=2),
                        Line2D([0], [0], color=sliceColors[3], lw=2),
                        Line2D([0], [0], color=sliceColors[4], lw=2)]

        fig.legend(custom_lines, [tempThresholds[0]
                , tempThresholds[1]
                , tempThresholds[2]
                , tempThresholds[3]
                , tempThresholds[4]]
                , bbox_to_anchor=(.97,.97)
                , loc="upper right")

        fig.subplots_adjust(right=0.85, top=0.83)
        graph_path = os.path.join(localfiles_info_pnl.local_path, "threashold_pie.png")
        print("pie created and saved to " + graph_path)
        plt.savefig(graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def local_box_plot_go(self, e):
        # reading the log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a local box plot from " + str(len(date_list)) + " values")
        # reading settings from ui
        dangercold = float(MainApp.graphing_info_pannel.danger_low_tc.GetValue())
        toocold = float(MainApp.graphing_info_pannel.low_tc.GetValue())
        toohot = float(MainApp.graphing_info_pannel.high_tc.GetValue())
        dangerhot = float(MainApp.graphing_info_pannel.danger_high_tc.GetValue())
        # start making graph
        print("Making EpiphanyHermit's competition winning box plot...")
        # Start and End colors for the gradient
        startColor = (118,205,38)
        endColor = (38,118,204)
        dangercoldColor = 'xkcd:purplish blue'
        toocoldColor = 'xkcd:light blue'
        toohotColor = 'xkcd:orange'
        dangerhotColor = 'xkcd:red'

        # Group the data by hour
        hours = [[] for i in range(24)]
        for i in range(len(date_list)):
            h = int(date_list[i].strftime('%H'))
            hours[h].append(value_list[i])

        # give the graph a rectangular formatr
        fig, ax1 = plt.subplots(figsize=(10, 6))
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.15)
        fig.suptitle('Median Value by Hour', fontsize=14, fontweight='bold')

        bp = ax1.boxplot(hours,whis=0,widths=1,showfliers=False,showcaps=False,medianprops=dict(linestyle=''),boxprops=dict(linestyle=''))
        ax1.set_axisbelow(True)
        ax1.set_title(min(date_list).strftime("%B %d, %Y") + ' - ' + max(date_list).strftime("%B %d, %Y"), fontsize=10)

        # x-axis
        labels = [item.get_text() for item in ax1.get_xticklabels()]
        for i in range(24):
            labels[i] = str(i).zfill(2) + ':00'
        ax1.set_xticklabels(labels,rotation=45,fontsize=8)
        ax1.set_xlim(0, 25)
        ax1.set_xlabel('Hour of the Day')

        # y-axis
        fmt = StrMethodFormatter('{x:,g}°')
        ax1.yaxis.set_major_formatter(fmt)
        ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
        #ax1.set_ylabel('Value')

        # legend
        custom_lines = [Line2D([0], [0], color=dangerhotColor, lw=2),
                        Line2D([0], [0], color=toohotColor, lw=2),
                        Line2D([0], [0], color=toocoldColor, lw=2),
                        Line2D([0], [0], color=dangercoldColor, lw=2)]

        plt.legend(custom_lines, [('%.2f°' % dangerhot).replace(".00°","°")
                , ('%.2f°' % toohot).replace(".00°","°")
                , ('%.2f°' % toocold).replace(".00°","°")
                , ('%.2f°' % dangercold).replace(".00°","°")]
                , bbox_to_anchor=(1.02,1)
                , loc="upper left")

        plt.subplots_adjust(right=0.85)

        # given a defined start and stop, calculate 24 shade gradient
        boxColors = [[] for i in range(24)]
        for i in range(24):
            for j in range(3):
                newColor = 0
                step = abs(startColor[j] - endColor[j]) / 24
                if startColor[j] > endColor[j]:
                    newColor = (startColor[j] - (i * step)) / 255
                else:
                    newColor = (startColor[j] + (i * step)) / 255
                boxColors[i].append(newColor)

        # Apply box specific info: color, median, warning
        minEdge = 100
        maxEdge = 0
        medians = list(range(24))
        for i in range(24):
            box = bp['boxes'][i]
            boxX = []
            boxY = []
            for j in range(5):
                boxX.append(box.get_xdata()[j])
                boxY.append(box.get_ydata()[j])
            boxCoords = np.column_stack([boxX, boxY])

            # Find min & max box edges to set y-axis limits
            if minEdge > min(boxY):
                minEdge = min(boxY)
            if maxEdge < max(boxY):
                maxEdge = max(boxY)

            # Alert user to dangerous temps
            warning = 'none'
            if min(hours[i]) <= toocold and min(hours[i]) > dangercold:
                warning = toocoldColor
            if min(hours[i]) <= dangercold:
                warning = dangercoldColor
            if max(hours[i]) >= toohot and max(hours[i]) < dangerhot:
                warning = toohotColor
            if max(hours[i]) >= dangerhot:
                warning = dangerhotColor

            # Color the box and set the edge color, if applicable
            boxPolygon = Polygon(boxCoords, facecolor=boxColors[i],edgecolor=warning)
            ax1.add_patch(boxPolygon)

            # add median data
            med = bp['medians'][i]
            medians[i] = med.get_ydata()[0]

        top = maxEdge + 1
        bottom = minEdge - 1
        ax1.set_ylim(bottom, top)

        # Add the medians just above the hour marks
        pos = np.arange(24) + 1
        upperLabels = [str(np.round(s, 2)) for s in medians]
        weights = ['bold', 'semibold']
        k = -1
        for tick, label in zip(range(24), ax1.get_xticklabels()):
            w = tick % 2
            k = k + 1
            ax1.text(pos[tick],bottom + (bottom*0.02),upperLabels[tick],horizontalalignment='center',size='x-small',weight=weights[w],color=boxColors[k])
        graph_path = os.path.join(localfiles_info_pnl.local_path, "box_plot.png")
        print("Box plot created and saved to " + graph_path)
        plt.savefig(graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def log_time_diff_graph_go(self, e):
        print("Want's to create a simple line graph...  ")
        # read data from log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) < 2:
            return None
        MainApp.status.write_bar("-- Creating a time diff graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # create list of time diffs
        counter = 0
        counter_list = []
        timediff_list = []
        time_of_prev_item = date_list[0]
        for current_items_time in date_list[1:]:
            time_diff = current_items_time - time_of_prev_item
            counter = counter + 1
            counter_list.append(counter)
            timediff_list.append(time_diff.total_seconds())
            time_of_prev_item = current_items_time
        # start making the graph
        fig = plt.gcf()
        fig.canvas.set_window_title('Time Diff Graph')
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        plt.title("Time difference between log entries\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        plt.ylabel("Time difference in seconds")
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        ax.plot(counter_list, timediff_list, color='black', lw=1)
        #ax.xaxis_date()
        #fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "time_diff_graph.png")
        plt.savefig(graph_path)
        print("time diff graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def value_diff_graph_go(self, e):
        print("Want's to create a value differnce graph...  ")
        # read data from log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) < 2:
            return None
        MainApp.status.write_bar("-- Creating a value diff graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # create list of Value diffs
        #counter = 0
        #counter_list = []
        value_dif_list = []
        prior_value = value_list[0]
        for current_value in value_list[1:]:
            value_diff = prior_value - current_value
            #counter = counter + 1
            #counter_list.append(counter)
            value_dif_list.append(value_diff)
            prior_value = current_value
        # start making the graph
        fig = plt.gcf()
        fig.canvas.set_window_title('Value Diff Graph')
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        plt.title("Value difference between log entries\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        plt.ylabel("Value difference")
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        ax.plot(date_list[1:], value_dif_list, color='black', lw=1)
        ax.xaxis_date()
        fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "value_diff_graph.png")
        plt.savefig(graph_path)
        print("Value diff graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        fig.clf()
        MainApp.status.write_bar("ready...")

    def divided_daily_go(self, e):
        # read log
        date_list   = shared_data.list_of_datasets[0][0]
        value_list  = shared_data.list_of_datasets[0][1]
        key_list    = shared_data.list_of_datasets[0][2]
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        MainApp.status.write_bar("-- Creating a daily values graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # start making graph
        print("Making divided daily graph...")
        dictionary_of_sets = {}
        for log_item_pos in range(0, len(date_list)):
            day_group = date_list[log_item_pos].strftime("%Y:%m:%d")
            log_time = date_list[log_item_pos]
            log_time = log_time.replace(year=1980, month=1, day=1)
            if day_group in dictionary_of_sets:
                # Read existing lists of dates and values
                values_to_graph = dictionary_of_sets[day_group][0]
                dates_to_graph = dictionary_of_sets[day_group][1]
                # add current value and date to lists
                values_to_graph.append(value_list[log_item_pos])
                dates_to_graph.append(log_time)
            else:
                # create new date and value lists if the day_group doesn't exists yet
                values_to_graph = [value_list[log_item_pos]]
                dates_to_graph = [log_time]
            # put the lists of values and dates into the dictionary of sets under the daygroup key
            dictionary_of_sets[day_group]=[values_to_graph, dates_to_graph]
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        for key, value in dictionary_of_sets.items():
            days_date_list = value[1]
            days_value_list = value[0]
            ax.plot(days_date_list, days_value_list, lw=1, label=key)
        ax.legend()
        plt.title("Daily Values\nTime Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        fig.autofmt_xdate()
        plt.ylabel(key_list[0]) # + " in " + key_unit)
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        graph_path = os.path.join(localfiles_info_pnl.local_path, "divided_days.png")
        plt.savefig(graph_path)
        print("divided days created and saved to " + graph_path)
        fig.clf()
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        MainApp.status.write_bar("ready...")

    # switch log
    def parse_switch_log_for_relays(self, add_data_to_square = True):
        MainApp.status.write_bar(" -- Reading switch log")
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value()
        if len(date_list) == 0:
            print("No data to make a graph with...")
            return None
        dates_to_graph = []
        values_to_graph = []
        dictionary_of_sets = {}
        power_on_markers = []
        for item in range(0, len(date_list)):
            if "_on.py" in key_list[item]:
                device_name = key_list[item].split("_on.py")[0]
                if device_name in dictionary_of_sets:
                    values_to_graph = dictionary_of_sets[device_name][0]
                    dates_to_graph = dictionary_of_sets[device_name][1]
                    #adding extra data to square the graph
                    if add_data_to_square == True:
                        values_to_graph.append(0)
                        time_minus_a_second = date_list[item] + datetime.timedelta(0,-1)
                        dates_to_graph.append(time_minus_a_second)
                    # adding new data point
                    values_to_graph.append(1)
                    dates_to_graph.append(date_list[item])
                    # putting data back into dictionary
                    dictionary_of_sets[device_name]=[values_to_graph, dates_to_graph]
                else:
                    values_to_graph = [1]
                    dates_to_graph = [date_list[item]]
                    dictionary_of_sets[device_name]=[values_to_graph, dates_to_graph]

            elif "_off.py" in key_list[item]:
                device_name = key_list[item].split("_off.py")[0]
                if device_name in dictionary_of_sets:
                    values_to_graph = dictionary_of_sets[device_name][0]
                    dates_to_graph = dictionary_of_sets[device_name][1]
                    #adding extra data to square the graph
                    if add_data_to_square == True:
                        values_to_graph.append(1)
                        time_minus_a_second = date_list[item] + datetime.timedelta(0,-1)
                        dates_to_graph.append(time_minus_a_second)
                    # adding new data point
                    values_to_graph.append(0)
                    dates_to_graph.append(date_list[item])
                    data = [values_to_graph, dates_to_graph]
                    dictionary_of_sets[device_name]=data
                else:
                    values_to_graph = [0]
                    dates_to_graph = [date_list[item]]
                    data = [values_to_graph, dates_to_graph]
                    dictionary_of_sets[device_name] = data
                    #    device_name = key_list[item].split("_off.py")[0]
                    #        values_to_graph = dictionary_of_sets[device_name].append(0)
                    #        dictionary_of_sets[device_name]=values_to_graph
            elif "water.py" in key_list[item]:
                device_name = key_list[item].split(".py")[0]
                if "watered for " in value_list[item]:
                    water_duration = value_list[item].split("watered for ")[1]
                if " seconds." in water_duration:
                    water_duration = water_duration.split(" seconds.")[0]
                water_duration = int(water_duration)
                print("water duration ", water_duration)
                # if it already exists grab the list and add to it
                if device_name in dictionary_of_sets:
                    values_to_graph = dictionary_of_sets[device_name][0]
                    dates_to_graph = dictionary_of_sets[device_name][1]
                    #adding extra data to square the graph
                    if add_data_to_square == True:
                        values_to_graph.append(0)
                        time_minus_a_second = date_list[item] + datetime.timedelta(0,-1)
                        dates_to_graph.append(time_minus_a_second)
                    # adding new data point for start of watering
                    values_to_graph.append(1)
                    dates_to_graph.append(date_list[item])
                    # adding new data point for end of watering
                    values_to_graph.append(1)
                    time_plus_duration = date_list[item] + datetime.timedelta(0,water_duration)
                    dates_to_graph.append(time_plus_duration)
                    # adding final square
                    values_to_graph.append(0)
                    time_plus_duration_and_a_second = date_list[item] + datetime.timedelta(0,water_duration+1)
                    dates_to_graph.append(time_plus_duration_and_a_second)
                    # put everything back in the dictionary ready for the next log entry
                    data = [values_to_graph, dates_to_graph]
                    dictionary_of_sets[device_name]=data
                else:
                    # adding new data point for start of watering
                    values_to_graph.append(1)
                    dates_to_graph.append(date_list[item])
                    # adding new data point for end of watering
                    values_to_graph.append(1)
                    time_plus_duration = date_list[item] + datetime.timedelta(0,water_duration)
                    dates_to_graph.append(time_plus_duration)
                    # adding final square
                    values_to_graph.append(0)
                    time_plus_duration_and_a_second = date_list[item] + datetime.timedelta(0,water_duration+1)
                    dates_to_graph.append(time_plus_duration_and_a_second)
                    # put everything back in the dictionary ready for the next log entry
                    data = [values_to_graph, dates_to_graph]
                    dictionary_of_sets[device_name] = data
            # get list of start up times."
            elif "chechDHT.py" in key_list[item]:
                if "Script initialised, performing lamp state check" in value_list[item]:
                    print("Found turn on at " + str(date_list[item]))
                    power_on_markers.append(date_list[item])
            else:
                item = None
        MainApp.status.write_bar("ready...")
        return dictionary_of_sets, power_on_markers

    #
    def set_data_extraction_settings_from_text(self, settings_list):
        for setting in settings_list:
            if ":" in setting:
                split_pos = setting.find(":")
                set_key = setting[:split_pos].strip()
                set_val = setting[split_pos + 1:].strip()
                ##

                if set_key == "split_chr":
                    MainApp.graphing_info_pannel.split_character_tc.SetValue(set_val)
                # date
                elif set_key == "date_pos":
                    MainApp.graphing_info_pannel.date_pos_cb.SetValue(set_val)
                elif set_key == "date_split":
                    MainApp.graphing_info_pannel.date_pos_split_tc.SetValue(set_val)
                elif set_key == "date_split_pos":
                    MainApp.graphing_info_pannel.date_pos_split_cb.SetSelection(int(set_val))
                # value
                elif set_key == "value_rem":
                    MainApp.graphing_info_pannel.rem_from_val_tc.SetValue(set_val)
                elif set_key == "value_pos":
                    MainApp.graphing_info_pannel.value_pos_cb.SetValue(set_val)
                elif set_key == "value_split":
                    MainApp.graphing_info_pannel.value_pos_split_tc.SetValue(set_val)
                elif set_key == "value_split_pos":
                    MainApp.graphing_info_pannel.value_pos_split_cb.SetSelection(int(set_val))
                    MainApp.graphing_info_pannel.value_pos_split_go("e")
                # key
                elif set_key == "key_pos":
                    MainApp.graphing_info_pannel.key_pos_cb.SetValue(set_val)
                elif set_key == "key_split":
                    MainApp.graphing_info_pannel.key_pos_split_tc.SetValue(set_val)
                elif set_key == "key_split_pos":
                    MainApp.graphing_info_pannel.key_pos_split_cb.SetSelection(int(set_val))
                    MainApp.graphing_info_pannel.key_pos_split_go("e")
                elif set_key == "key_match":
                    MainApp.graphing_info_pannel.key_matches_tc.SetValue(set_val)
                elif set_key == "key_manual":
                    MainApp.graphing_info_pannel.key_manual_tc.SetValue(set_val)
                # Date settings
                elif set_key == "limit_date":
                    MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue(set_val)
                elif set_key == "start_time":
                    start_time = datetime.datetime.strptime(set_val, '%Y-%m-%d %H:%M:%S')
                    if not MainApp.graphing_info_pannel.limit_date_to_last_cb.GetValue() == "custom":
                        MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue("custom")
                    MainApp.graphing_info_pannel.start_time_picer.SetValue(start_time)
                    MainApp.graphing_info_pannel.start_date_picer.SetValue(start_time)
                elif set_key == "end_time":
                    end_time = datetime.datetime.strptime(set_val, '%Y-%m-%d %H:%M:%S')
                    if not MainApp.graphing_info_pannel.limit_date_to_last_cb.GetValue() == "custom":
                        MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue("custom")
                    MainApp.graphing_info_pannel.end_time_picer.SetValue(end_time)
                    MainApp.graphing_info_pannel.end_date_picer.SetValue(end_time)

    def set_graph_settings_from_text(self, settings_list):
        '''
        Set the graph settings from a list of text strings
           key:value
        '''
        self.graph_module_settings.SetValue(True)
        self.graph_module_settings_click("e")
        setting_control_dict = self.make_gm_extra_settings_dict()
        for setting in settings_list:
            if ":" in setting:
                split_pos = setting.find(":")
                set_key = setting[:split_pos].strip()
                set_val = setting[split_pos + 1:].strip()
                # Axis limits and Size
                if set_key == "y_min":
                    MainApp.graphing_info_pannel.axis_y_min_cb.SetValue(set_val)
                elif set_key == "y_max":
                    MainApp.graphing_info_pannel.axis_y_max_cb.SetValue(set_val)
                elif set_key == "size_h":
                    MainApp.graphing_info_pannel.size_h_cb.SetValue(set_val)
                elif set_key == "size_v":
                    MainApp.graphing_info_pannel.size_v_cb.SetValue(set_val)
                elif set_key in setting_control_dict:
                    setting_control_dict[set_key]=set_val
        # write settings list back to ui
        self.module_options_list_ctrl.DeleteAllItems()
        index = 0
        for key, value in setting_control_dict.items():
            self.module_options_list_ctrl.InsertItem(index, key)
            self.module_options_list_ctrl.SetItem(index, 1, value)
            index = index + 1


                            #    print(" --- Want's to set graph setting " + set_key + " to " + set_val + " but not doing that yet... Sorry")


                                # setting
                                # if "value_range_source" in preset_settings:
                                #     value_range_source = preset_settings["value_range_source"]
                                # if value_range_source == "config":
                                #     if "low" in preset_settings:
                                #         low_loc = preset_settings["low"]
                                #         if not low_loc == "":
                                #             if low_loc in MainApp.config_ctrl_pannel.config_dict:
                                #                 low_value = MainApp.config_ctrl_pannel.config_dict[low_loc]
                                #                 MainApp.graphing_info_pannel.low_tc.SetValue(low_value)
                                #                 danger_low = ((float(low_value) / 100) * 80)
                                #                 MainApp.graphing_info_pannel.danger_low_tc.SetValue(str(danger_low))
                                #     if "high" in preset_settings:
                                #         high_loc = preset_settings["high"]
                                #         if not high_loc == "":
                                #             if high_loc in MainApp.config_ctrl_pannel.config_dict:
                                #                 high_value = MainApp.config_ctrl_pannel.config_dict[high_loc]
                                #                 MainApp.graphing_info_pannel.high_tc.SetValue(high_value)
                                #                 danger_high = ((float(high_value) / 100) * 120)
                                #                 MainApp.graphing_info_pannel.danger_high_tc.SetValue(str(danger_high))
                                # else:
                                #     MainApp.graphing_info_pannel.low_tc.SetValue(preset_settings["low"])
                                #     MainApp.graphing_info_pannel.danger_low_tc.SetValue(preset_settings["danger_low"])
                                #     MainApp.graphing_info_pannel.high_tc.SetValue(preset_settings["high"])
                                #     MainApp.graphing_info_pannel.danger_high_tc.SetValue(preset_settings["danger_high"])


                                ##

    def load_current_dw_log(self, dw_log_settings, dw_log_presets):
        print(" -- loading log")
        # open preset
        for preset in dw_log_presets:
            self.graph_presets_cb.SetValue(preset.strip())
            self.graph_preset_cb_go("e")
            # do settings
            self.set_data_extraction_settings_from_text(dw_log_settings)
            # load log
            self.set_log_click("e")

    def make_current_dw_graph(self, dw_current_graphs, dw_graphs_settings, made_graph_list):
        for x in dw_current_graphs:
            self.module_graph_choice.SetValue(x)
            # do settings
            self.set_graph_settings_from_text(dw_graphs_settings)
            #make graph
            graph_num = str(len(made_graph_list) + 1)
            graph_name = "datawall_graph_" + graph_num + ".png"
            graph_path = os.path.join(localfiles_info_pnl.local_path, graph_name)
            self.make_graph_from_imported_module("e", file_name=graph_name)
            made_graph_list.append(graph_path)

    def make_datawall_from_module(self, e=""):
        # test
        dw_preset_choice = self.dw_preset_list_cb.GetValue()
        datawall_preset_path = os.path.join(shared_data.datawall_presets_path, dw_preset_choice)
        with open(datawall_preset_path) as f:
            datawall_presets = f.read()
        print (" - - - - -")
        print (datawall_presets)
        print (" - - - - -")
        datawall_presets = datawall_presets.splitlines()
        graph_count = 0
        current_graph = ""
        dw_log_settings = []
        dw_log_presets  = []
        dw_current_graphs   = []
        dw_graphs_settings  = []
        made_graph_list  = []
        for line in datawall_presets:
            line = line.strip()
            if line == "load_log":
                print( " Datawall - Loading " + str(dw_log_presets))
                self.load_current_dw_log(dw_log_settings, dw_log_presets)
                dw_log_settings = []
                dw_log_presets  = []
            if line == "make_graph":
                print( " Datawall - Making Graph " + current_graph)
                self.make_current_dw_graph(dw_current_graphs, dw_graphs_settings, made_graph_list)
                dw_current_graphs   = []
                dw_graphs_settings  = []
            # options settings
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos].strip()
                value = line[equals_pos + 1:].strip()
                if key == "graph_name":
                    print( " Datawall - Starting graph - " + value)
                    current_graph = value
                    dw_log_settings = []
                    dw_log_presets  = []
                    dw_current_graphs   = []
                    dw_graphs_settings  = []
                    # blank prior settings and logs
                    self.clear_log_click("e")
                elif "_" in key:
                    equals_pos = key.find("_")
                    key_type = key[:equals_pos].strip()
                    key_job  = key[equals_pos + 1:].strip()
                    # handling loading of logs
                    if key_type == "log":
                        if key_job == "preset":
                            preset_name = value.split(",")
                            for x in preset_name:
                                dw_log_presets.append(x)
                        if key_job == "setting":
                            dw_log_settings.append(value)
                    # handling making of graphs
                    if key_type == "graph":
                        if key_job == "module":
                            module_name = value.split(",")
                            for x in module_name:
                                dw_current_graphs.append(x)
                        if key_job == "setting":
                            dw_graphs_settings.append(value)
        #
        print(" Created Graphs - ", made_graph_list)
        #
        module_name = self.dw_module_list_cb.GetValue()
        if module_name == "" or module_name == "none":
            print(" - No datawall selected, finishing.")
            return "done without making datawall"
        module_name = "datawall_" + module_name
        # unload the old module to bring in any changes to the script since it was loaded
        if module_name in sys.modules:
            del sys.modules[module_name]
        # import the make_graph function as a module
        exec("from " + module_name + " import make_datawall", globals())
        base_filename = module_name+".png"
        datawall_path = os.path.join(localfiles_info_pnl.local_path, base_filename)
        make_datawall(made_graph_list, datawall_path, shared_data.list_of_datasets)
        MainApp.graphing_info_pannel.show_local_graph(datawall_path)


    def switch_log_graph_go(self, e):

        # date limits
        print("User wants to graph the switch log, i'm still working on that though....")
        # example switch log lines
        # lamp_on.py@2018-05-05 06:00:02.022281@lamp turned on
        # lamp_off.py@2018-05-05 23:00:02.647168@lamp turned off
        MainApp.status.write_bar("-- Creating a graph of the switch log")
        dictionary_of_sets, power_on_markers = self.parse_switch_log_for_relays()
        size_h, size_v = self.get_graph_size_from_ui()
        # graph
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        for key, value in dictionary_of_sets.items():
            date_list = value[1]
            value_list = value[0]
            ax.plot(date_list, value_list, lw=1, label=key)
        for x in power_on_markers:
            plt.axvline(x, color='#d62728')
        ax.legend()
        fig = plt.gcf()
        fig.canvas.set_window_title('Switch Log Graph')
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        ax.xaxis_date()
        fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "switch_log_graph.png")
        plt.savefig(graph_path)
        print("line graph created and saved to " + graph_path)
        fig.clf()
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        MainApp.status.write_bar("ready...")

    def switch_log_relay_weekly(self, e):
        dictionary_of_sets, power_on_markers = self.parse_switch_log_for_relays()
        size_h, size_v = self.get_graph_size_from_ui()
        # graph
        for key, value in dictionary_of_sets.items():
            date_list = dictionary_of_sets[1]
            value_list = value[0]


        fig, ax = plt.subplots(figsize=(size_h, size_v))
        #
        ax.plot(date_list, value_list, lw=2, label=key)
        #
        ax.legend()
        fig = plt.gcf()
        fig.canvas.set_window_title('Switch Log Graph')
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        ax.xaxis_date()
        fig.autofmt_xdate()
        graph_path = os.path.join(localfiles_info_pnl.local_path, "switch_log_graph.png")
        plt.savefig(graph_path)
        print("line graph created and saved to " + graph_path)
        fig.clf()
        MainApp.graphing_info_pannel.show_local_graph(graph_path)







    # Make on Pi controlls
    def get_opts_click(self, e):
        #turns on UI elements for automatically found script options
        #then asks get_script_options to ask the script on the pi to list flags
        if self.get_opts_tb.IsChecked():
            print("fetching scripts options, warning script must know how to respond to -flags argument")
            self.opts_cb.Show()
            self.add_arg_btn.Show()
            wx.GetApp().Yield()
            if not self.select_script_cb.GetValue() == "":
                self.get_script_options()
        else:
            self.blank_options_ui_elements()
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

    def get_script_options(self):
        #runs the script on the raspberry pi and adds all detected flags to
        #the command line options combo box (self.opts_cb)
        #also a dictionary of all the commands and their defaults or options (self.options_dict)
        scriptpath = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation/" + self.select_script_cb.GetValue()
        print(("Fetching options for; " + scriptpath))
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(scriptpath + " -flags")
        flags = out.splitlines()
        self.opts_cb.Clear()
        self.options_dict={}
        try:
            for opt in flags:
                if "=" in opt:
                    optpair = opt.split("=")
                    optkey = optpair[0]
                    optval = optpair[1]
                    self.opts_cb.Append(optkey)
                    self.options_dict[optkey]=optval

        except:
            self.blank_options_ui_elements()
        if self.opts_cb.GetCount() < 1:
            self.blank_options_ui_elements()
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

    def blank_options_ui_elements(self):
        #hides UI elements for auto-discovered command line arguments.
        self.opts_cb.Hide()
        self.opts_cb.SetValue("")
        self.opts_text.Hide()
        self.opts_text.SetValue("")
        self.command_line_opts_value_list_cb.Hide()
        self.command_line_opts_value_list_cb.SetValue("")
        self.add_arg_btn.Hide()

    def opt_combo_go(self, e):
        #selects which UI elements to show for command line option values and defaults
        #attempts to parse command line string into list or text
        self.opts_text.Hide()
        option = self.opts_cb.GetValue()
        value_text = str(self.options_dict[option])
        if "[" in value_text and "]" in value_text:
            value_text = value_text.split("[")[1]
            value_text = value_text.split("]")[0]
            value_text = value_text.split(",")
            self.opts_text.Hide()
            self.opts_text.SetValue("")
            self.command_line_opts_value_list_cb.Clear()
            self.command_line_opts_value_list_cb.SetValue("")
            self.command_line_opts_value_list_cb.Show()
            for item in value_text:
                self.command_line_opts_value_list_cb.Append(item)
        else:
            self.command_line_opts_value_list_cb.Hide()
            self.command_line_opts_value_list_cb.SetValue("")
            self.command_line_opts_value_list_cb.Clear()
            self.opts_text.Show()
            self.opts_text.SetValue(value_text)
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

    def add_arg_click(self, e):
        #reads the user selected option from the two text boxes then
        #adds it to the end of the existing command line arguments text
        argkey = self.opts_cb.GetValue()
        if not self.command_line_opts_value_list_cb.GetCount() > 0:
            argval = self.opts_text.GetValue()
        else:
            argval = self.command_line_opts_value_list_cb.GetValue()
        argval = argval.replace(" ", "_")
        argstring = argkey + "=" + argval
        existing_args = self.extra_args.GetValue()
        self.extra_args.SetValue(existing_args + " " + argstring)

    def get_graphing_scripts(self):
        # checks the pigrows visualisation folder for graphing scripts and adds to list
        print("getting graphing scripts")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation")
        vis_list = out.split("\n")
        graph_opts = []
        for filename in vis_list:
            if filename.endswith("py") or filename.endswith('sh'):
                graph_opts.append(filename)
        return graph_opts

    def make_graph_click(self, e):
        # currently asks the pi to make the graph using the options supplied
        # will be upgraded to run graphing modules locally at some point if that options selected instead
        script_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/visualisation/" + self.select_script_cb.GetValue()
        script_command = script_path + " " + self.extra_args.GetValue()
        print("#sb# Running; " + script_command)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(script_command)
        msg = str(out) + " " + str(error)
        dmsg = "Script Output;\n"# + msg.replace("...", ",")
        for line in msg.splitlines():  #this is a hacky way of removing nonsence
            pos = line.find("...")     #from the output which breaks the dialog box
            if pos > 0:                    #stops line at an ... which avoids displaying
                line = line[:pos]      #bad log info as this is often gibberish
            dmsg += line + "\n"        #which would otherwise disrupt the messagebox
        wx.MessageBox(dmsg, 'Script Output', wx.OK | wx.ICON_INFORMATION)
        print (dmsg)
        ## attempt to find path of graph on pi
        path_possible = dmsg.replace("\n", " ").strip().split(" ")
        self.clear_graph_area()
        for possible in path_possible:
            if ".png" in possible:
                local_name = possible.split("/Pigrow/")[1]
                if self.download_graph.GetValue() == True:
                    img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, possible, local_name)
                    MainApp.graphing_info_pannel.graph_sizer.Add(wx.StaticText(MainApp.graphing_info_pannel,  label=possible), 0, wx.ALL, 2)
                    MainApp.graphing_info_pannel.graph_sizer.Add(wx.StaticBitmap(MainApp.graphing_info_pannel, -1, wx.Image(img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        MainApp.graphing_info_pannel.graph_sizer.Layout()
        MainApp.graphing_info_pannel.main_sizer.Layout()
        MainApp.camconf_info_pannel.SetSizer(MainApp.graphing_info_pannel.main_sizer)
        MainApp.graphing_info_pannel.SetupScrolling()
        MainApp.window_self.Layout()

    def clear_graph_area(self, e=""):
        # usage = MainApp.graphing_info_pannel.clear_graph_area()
        children = MainApp.graphing_info_pannel.graph_sizer.GetChildren()
        for child in children:
            item = child.GetWindow()
            item.Destroy()

    def select_script_combo_go(self, e):
        #this is the same as pressing the button to enable asking the script
        #to send a list of -flags.
        self.opts_cb.SetValue("")
        self.opts_text.SetValue("")
        self.command_line_opts_value_list_cb.SetValue("")
        self.get_opts_click("fake event")
        #graphing_script = self.select_script_cb.GetValue()
        #print graphing_script



#
#
#
## Camera Config Tab
#
#
#
class camconf_info_pnl(scrolled.ScrolledPanel):
    #
    def __init__( self, parent ):
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.HSCROLL|wx.VSCROLL )
        ## Draw UI elements
        # placing the information boxes
        # top row
        ccf_label = wx.StaticText(self,  label='Camera Config file', size=(150,30))
        #self.camconf_path_tc = wx.TextCtrl(self, value="", size=(400, 30))
        self.camconf_path_tc = wx.ComboBox(self, choices = [], size=(400, 30))
        self.camconf_path_tc.Bind(wx.EVT_COMBOBOX, MainApp.camconf_ctrl_pannel.read_cam_config_click)
        # Top bar info
        # basic settings - left col
        b_label = wx.StaticText(self,  label='Brightness;')
        self.tb_b = wx.TextCtrl(self, size=(75, 25))
        c_label = wx.StaticText(self,  label='Contrast;')
        self.tb_c = wx.TextCtrl(self, size=(75, 25))
        s_label = wx.StaticText(self,  label='Saturation;')
        self.tb_s = wx.TextCtrl(self, size=(75, 25))
        g_label = wx.StaticText(self,  label='Gain;')
        self.tb_g = wx.TextCtrl(self, size=(75, 25))
        # size settings - 2nd col
        is_label = wx.StaticText(self,  label='Image Size;')
        x_label = wx.StaticText(self,  label='X;')
        self.tb_x = wx.TextCtrl(self, size=(75, 25))
        y_label = wx.StaticText(self,  label='Y;')
        self.tb_y = wx.TextCtrl(self, size=(75, 25))
        # camera capture unique options - 3rd col
        ## generic (legacy support remove when possible)
        self.extra_cmds_generic_label = wx.StaticText(self, label='extra args string;')
        self.cmds_string_tb = wx.TextCtrl(self, size=(265, 90), style=wx.TE_MULTILINE)
        self.cmds_string_tb.Hide() #here for legacy only
        self.extra_cmds_generic_label.Hide() #here for legacy only
        #####
        ## fswebcam only controlls
        self.list_fs_ctrls_btn = wx.Button(self, label='Show webcam controlls')
        self.list_fs_ctrls_btn.Bind(wx.EVT_BUTTON, self.list_fs_ctrls_click)
        # line 2 - setting key
        self.setting_string_label = wx.StaticText(self,  label='set;')
        self.setting_string_tb = wx.TextCtrl(self, size=(200,25))
        # line 3  - setting value
        self.setting_value_label = wx.StaticText(self,  label='value;')
        self.setting_value_tb = wx.TextCtrl(self, size=(100, 25))
        self.add_to_cmd_btn = wx.Button(self, label='Add to cmd...')
        self.add_to_cmd_btn.Bind(wx.EVT_BUTTON, self.add_to_cmd_click)
        #
        self.extra_cmds_fs_label = wx.StaticText(self,  label='extra commands for fs;')
        self.extra_cmds_string_fs_tb = wx.TextCtrl(self, size=(250,40), style=wx.TE_MULTILINE)
        ## uvccaptre only controlls
        self.extra_cmds_uvc_label = wx.StaticText(self,  label='extra commands for uvc;')
        self.extra_cmds_string_uvc_tb = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        #####
        ## picamcap only controls
        self.picam_options_list_ctrl = wx.ListCtrl(self, size=(575,150), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.picam_options_list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_picam_opt)
        self.picam_options_list_ctrl.InsertColumn(0, 'Option')
        self.picam_options_list_ctrl.InsertColumn(1, 'Value')
        self.picam_options_list_ctrl.InsertColumn(2, 'Choices')
        self.picam_options_list_ctrl.SetColumnWidth(0, 175)
        self.picam_options_list_ctrl.SetColumnWidth(1, 100)
        self.picam_options_list_ctrl.SetColumnWidth(2, 300)
        self.fill_picam_opts_with_defaults()


        #####
        ##sizers
        # top line cam conf file on pi (this will hopefully be moved somewhere better)
        cam_conf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cam_conf_sizer.Add(ccf_label, 0, wx.ALL, 5)
        cam_conf_sizer.Add(self.camconf_path_tc , 0, wx.ALL, 5)
        # camera controlls
        b_sizer = wx.BoxSizer(wx.HORIZONTAL)
        b_sizer.Add(b_label, 0, wx.RIGHT, 5)
        b_sizer.Add(self.tb_b, 0, wx.RIGHT, 5)
        c_sizer = wx.BoxSizer(wx.HORIZONTAL)
        c_sizer.Add(c_label, 0, wx.RIGHT, 5)
        c_sizer.Add(self.tb_c, 0, wx.RIGHT, 5)
        s_sizer = wx.BoxSizer(wx.HORIZONTAL)
        s_sizer.Add(s_label, 0, wx.RIGHT, 5)
        s_sizer.Add(self.tb_s, 0, wx.RIGHT, 5)
        g_sizer = wx.BoxSizer(wx.HORIZONTAL)
        g_sizer.Add(g_label, 0, wx.RIGHT, 5)
        g_sizer.Add(self.tb_g, 0, wx.RIGHT, 5)
        basic_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        basic_settings_sizer.Add(b_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        basic_settings_sizer.Add(c_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        basic_settings_sizer.Add(s_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        basic_settings_sizer.Add(g_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        # image sizer
        x_sizer = wx.BoxSizer(wx.HORIZONTAL)
        x_sizer.Add(x_label, 0, wx.ALL, 5)
        x_sizer.Add(self.tb_x, 0, wx.ALL, 5)
        y_sizer = wx.BoxSizer(wx.HORIZONTAL)
        y_sizer.Add(y_label, 0, wx.ALL, 5)
        y_sizer.Add(self.tb_y, 0, wx.ALL, 5)
        image_size_sizer = wx.BoxSizer(wx.VERTICAL)
        image_size_sizer.Add(is_label, 0, wx.ALL, 1)
        image_size_sizer.Add(x_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        image_size_sizer.Add(y_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 0)
        # camera option spesific settings
        #fswebcam sizer - only shown when fswebcam is selected
        fs_set_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fs_set_sizer.Add(self.setting_string_label, 0, wx.RIGHT, 5)
        fs_set_sizer.Add(self.setting_string_tb, 0, wx.RIGHT, 5)
        fs_value_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fs_value_sizer.Add(self.setting_value_label, 0, wx.RIGHT, 5)
        fs_value_sizer.Add(self.setting_value_tb, 0, wx.RIGHT, 5)
        fs_value_sizer.Add(self.add_to_cmd_btn, 0, wx.RIGHT, 5)
        fswebcam_args_sizer = wx.BoxSizer(wx.VERTICAL)
        fswebcam_args_sizer.Add(self.extra_cmds_fs_label, 0, wx.RIGHT, 5)
        fswebcam_args_sizer.Add(self.extra_cmds_string_fs_tb, 1, wx.RIGHT|wx.EXPAND, 1)
        fswebcam_opts_sizer = wx.BoxSizer(wx.VERTICAL)
        fswebcam_opts_sizer.Add(self.list_fs_ctrls_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 1)
        fswebcam_opts_sizer.Add(fs_set_sizer, 0, wx.ALL, 1)
        fswebcam_opts_sizer.Add(fs_value_sizer, 0, wx.ALL|wx.EXPAND, 1)
        #uvc sizer - only shown when uvc us Selected
        self.uvc_opts_sizer = wx.BoxSizer(wx.VERTICAL)
        self.uvc_opts_sizer.Add(self.extra_cmds_uvc_label, 0, wx.RIGHT, 5)
        self.uvc_opts_sizer.Add(self.extra_cmds_string_uvc_tb, 1, wx.RIGHT|wx.EXPAND, 5)
        # picamcap sizer - only shown when picamcap is selected
        picamcap_opts_sizer = wx.BoxSizer(wx.VERTICAL)
        picamcap_opts_sizer.Add(self.picam_options_list_ctrl, 0, wx.ALL|wx.EXPAND, 1)

        # NEED TO BE ADDED - generic extra args for legacy + extra args for other camera opts
        #2nd row Pannels sizers
        panels_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panels_sizer.Add(basic_settings_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(image_size_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(fswebcam_opts_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(fswebcam_args_sizer, 0, wx.ALL|wx.EXPAND, 5)
        panels_sizer.Add(self.uvc_opts_sizer, 0, wx.ALL|wx.EXPAND, 5)
        panels_sizer.Add(picamcap_opts_sizer, 0, wx.ALL|wx.EXPAND, 5)
        # picture display AREA
        self.picture_sizer = wx.BoxSizer(wx.VERTICAL)
        # MAIN sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(cam_conf_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(panels_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.picture_sizer, 0, wx.ALL, 0)
        # hide all unique controlls until option selected in combobox
        self.hide_fswebcam_control()
        self.hide_uvc_control()
        self.hide_picamcap_control()
        # set sizers and scrolling
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def seek_cam_configs(self):
        conf_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls " + str(conf_folder))
        config_list = out.splitlines()
        cam_config_list = []
        self.camconf_path_tc.Clear()
        for file in config_list:
            file_name = conf_folder + file.strip()
            grep_cmd = "grep cam_num= " + file_name
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(grep_cmd)
            if not out.strip() == "":
                self.camconf_path_tc.Append(file_name)


    def put_picam_settings_in_listbox(self, settings_list):
        self.picam_options_list_ctrl.DeleteAllItems()
        for index in range(0, len(settings_list)):
            self.picam_options_list_ctrl.InsertItem(index, settings_list[index][0])
            self.picam_options_list_ctrl.SetItem(index, 1, settings_list[index][1])
            self.picam_options_list_ctrl.SetItem(index, 2, settings_list[index][2])


    def fill_picam_opts_with_defaults(self):
        # ["digital_gain", "", ""]
        settings_list = [["sharpness", "", "-100 to 100"],
                         ["zoom", "", "0 to ?"],
                         ["drc_strength", "", 'off, low, medium, high'],
                         ["exposure_compensation", "", "-25 to 25" ],
                         ["exposure_mode", "", "'off' 'auto' 'night' 'nightpreview' 'backlight' 'spotlight' 'sports' 'snow' 'beach' 'verylong' 'fixedfps' 'antishake' 'fireworks'"],
                         ["exposure_speed", "", "0 (auto), shutter speed in microseconds"],
                         ["hflip", "", "True"],
                         ["vflip", "", "True"],
                         ["rotation", "", "0, 90, 180, 270"],
                         ["meter_mode", "", "average, spot, backlit, matrix"],
                         ["image_denoise", "", "True"],
                         ["image_effect", "", "see https://www.reddit.com/r/Pigrow/wiki/info_camera"],
                         ["image_effect_params", "", ""],
                         ["awb_mode", "", "'off' 'auto' 'sunlight' 'cloudy' 'shade' 'tungsten' 'fluorescent' 'incandescent' 'flash' 'horizon'"]]
        self.put_picam_settings_in_listbox(settings_list)


    def onDoubleClick_picam_opt(self, e):
        # fetch option info from table
        index =  e.GetIndex()
        setting = self.picam_options_list_ctrl.GetItem(index, 0).GetText()
        current_value = self.picam_options_list_ctrl.GetItem(index, 1).GetText()
        opts = self.picam_options_list_ctrl.GetItem(index, 2).GetText()
        # ask user for setting with a dialog box
        msg = "Select value for " + setting
        msg += "\n\n" + opts
        picam_setting_dialog = wx.TextEntryDialog(self, msg, "Picam Setting", current_value)
        if picam_setting_dialog.ShowModal() == wx.ID_OK:
            new_setting = picam_setting_dialog.GetValue()
            self.picam_options_list_ctrl.SetItem(index, 1, new_setting)

    def hide_uvc_control(self):
        self.extra_cmds_uvc_label.Hide()
        self.extra_cmds_string_uvc_tb.Hide()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def show_uvc_control(self):
        self.extra_cmds_uvc_label.Show()
        self.extra_cmds_string_uvc_tb.Show()
        self.hide_fswebcam_control()
        self.hide_picamcap_control()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def hide_fswebcam_control(self):
        self.list_fs_ctrls_btn.Hide()
        self.list_fs_ctrls_btn.Hide()
        self.setting_string_label.Hide()
        self.setting_string_tb.Hide()
        self.setting_value_label.Hide()
        self.setting_value_tb.Hide()
        self.add_to_cmd_btn.Hide()
        self.extra_cmds_fs_label.Hide()
        self.extra_cmds_string_fs_tb.Hide()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def show_fswebcam_control(self):
        self.list_fs_ctrls_btn.Show()
        self.list_fs_ctrls_btn.Show()
        self.setting_string_label.Show()
        self.setting_string_tb.Show()
        self.setting_value_label.Show()
        self.setting_value_tb.Show()
        self.add_to_cmd_btn.Show()
        self.extra_cmds_fs_label.Show()
        self.extra_cmds_string_fs_tb.Show()
        # hide other Controlls
        self.hide_uvc_control()
        self.hide_picamcap_control()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def hide_picamcap_control(self):
        self.picam_options_list_ctrl.Hide()

    def show_picamcap_control(self):
        self.picam_options_list_ctrl.Show()
        # hide other Controlls
        self.hide_uvc_control()
        self.hide_fswebcam_control()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()


    def list_fs_ctrls_click(self, e):
        print("runing cmd: fswebcam -d v4l2:/dev/video0 --list-controls (on the pi)")
        cam_choice = MainApp.camconf_ctrl_pannel.cam_cb.GetValue()
        cam_cmd = "fswebcam -d v4l2:" + cam_choice + " --list-controls"
        MainApp.status.write_bar("---Doing: " + cam_cmd)
        cam_output, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cam_cmd)
        print ("Camera output; " + cam_output + " \n    and error;" + error)
        if not cam_output == "":
            msg_text = 'Camera located and interorgated; copy-paste a controll name from the following into the settings text box \n \n'
            msg_text += str(cam_output)
            dbox = scroll_text_dialog(None, msg_text, "Camera Options", False)
            dbox.ShowModal()
            dbox.Destroy()
        if "command not found" in error or "command not found" in cam_output:
            print("!!! fswebcam not installed !!!")
            wx.MessageBox('fswebcam is not install on this pi', 'Camera Config', wx.OK | wx.ICON_INFORMATION)



    def add_to_cmd_click(self, e):
        test_str = self.setting_string_tb.GetValue().strip()
        test_val = self.setting_value_tb.GetValue().strip()
        cmd_str = self.extra_cmds_string_fs_tb.GetValue()
        if test_str in cmd_str:
            cmd_str = self.modify_cmd_str(cmd_str, test_str, test_val)
        else:
            cmd_str += ' --set "' + str(test_str) + '"="' + str(test_val) + '"'
        self.extra_cmds_string_fs_tb.SetValue(cmd_str)
        self.setting_string_tb.SetValue('')
        self.setting_value_tb.SetValue('')

    def modify_cmd_str(self, cmd_str, new_key, new_value):
        cmds = cmd_str.split("--set ")
        command_string = []
        for cmd in cmds:
            if "=" in cmd:
                print(cmd)
                set_key = cmd.split('"')[1]
                if set_key == new_key:
                    cmd = '"' + new_key + '"=' + new_value
                    print(cmd)
                command_string.append(cmd)
        # pur it back togerher into a string
        new_cmd_string = ""
        for cmd in command_string:
            new_cmd_string += "--set " + cmd + " "
        return new_cmd_string.strip()

class camconf_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # read / save cam config button
        self.read_cam_config_btn = wx.Button(self, label='read config')
        self.read_cam_config_btn.Bind(wx.EVT_BUTTON, self.read_cam_config_click)
        self.save_cam_config_btn = wx.Button(self, label='save to pi')
        self.save_cam_config_btn.Bind(wx.EVT_BUTTON, self.save_cam_config_click)
        #camera options
        self.cam_select_l = wx.StaticText(self,  label='Camera selection;')
        self.list_cams_btn = wx.Button(self, label='find', size=(30, 30))
        self.list_cams_btn.Bind(wx.EVT_BUTTON, self.list_cams_click)
        cam_opts = [""]
        self.cam_cb = wx.ComboBox(self, choices = cam_opts, size=(225, 30))
        #
        self.cap_tool_l = wx.StaticText(self,  label='Capture tool;')
        webcam_opts = ['uvccapture', 'fswebcam', 'picamcap']
        self.webcam_cb = wx.ComboBox(self, choices = webcam_opts, size=(265, 30))
        self.webcam_cb.Bind(wx.EVT_COMBOBOX, self.webcam_combo_go)

        # Buttons
        self.take_unset_btn = wx.Button(self, label='Take using\ncam default')
        self.take_unset_btn.Bind(wx.EVT_BUTTON, self.take_unset_click)
        self.take_set_btn = wx.Button(self, label='Take using\nlocal settings')
        self.take_set_btn.Bind(wx.EVT_BUTTON, self.take_set_click)
        self.take_s_set_btn = wx.Button(self, label='Take using\nsaved settings')
        self.take_s_set_btn.Bind(wx.EVT_BUTTON, self.take_saved_set_click)
        # Take Range altering a single setting
        range_opts = ['brightness', 'contrast', 'saturation', 'gain', 'user']
        self.range_combo = wx.ComboBox(self, choices = range_opts)
        # start point, end point, increment every x - text control, label, default settings
        self.range_start_tc = wx.TextCtrl(self)
        self.range_end_tc = wx.TextCtrl(self)
        self.range_every_tc = wx.TextCtrl(self)
        self.range_start_l = wx.StaticText(self,  label='start;')
        self.range_end_l = wx.StaticText(self,  label='end;')
        self.range_every_l = wx.StaticText(self,  label='every;')
        self.range_start_tc.SetValue("0")
        self.range_end_tc.SetValue("255")
        self.range_every_tc.SetValue("20")
        # take range button
        self.take_range_btn = wx.Button(self, label='Take\nrange', size=(50,-1))
        self.take_range_btn.Bind(wx.EVT_BUTTON, self.range_btn_click)
        # compare
        self.onscreen_compare_l = wx.StaticText(self,  label='Compare Images;')
        self.set_as_compare_btn = wx.Button(self, label='Set as compare image')
        self.set_as_compare_btn.Bind(wx.EVT_BUTTON, self.set_as_compare_click)
        self.use_compare = wx.CheckBox(self, label='Enable')
        compare_opts = image_combine.config.styles
        self.compare_style_cb = wx.ComboBox(self, choices = compare_opts, value=compare_opts[0], size=(265, 30))
        # show noise - image set analasis
        self.anal_tools_l = wx.StaticText(self,  label='Analasis Tools;')
        self.cap_stack_btn = wx.Button(self, label='Capture Stack')
        self.cap_stack_btn.Bind(wx.EVT_BUTTON, self.cap_stack_click)
        self.capture_stack_count = wx.TextCtrl(self, value="5")
        self.use_range_combine = wx.CheckBox(self, label='Combine Range')
        combine_opts = image_combine.config.combine_styles
        self.set_style_cb = wx.ComboBox(self, choices = combine_opts, value=combine_opts[0], size=(265, 30))


        # Sizers
        load_save_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        load_save_btn_sizer.Add(self.read_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        load_save_btn_sizer.Add(self.save_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        find_select_cam_sizer = wx.BoxSizer(wx.HORIZONTAL)
        find_select_cam_sizer.Add(self.list_cams_btn, 0, wx.ALL, 0)
        find_select_cam_sizer.Add(self.cam_cb, 0, wx.ALL|wx.EXPAND, 0)
        take_single_photo_btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        take_single_photo_btns_sizer.Add(self.take_unset_btn, 0, wx.ALL, 0)
        take_single_photo_btns_sizer.Add(self.take_s_set_btn, 0, wx.ALL, 0)
        range_options_btn_sizer = wx.GridSizer(3, 2, 0, 0)
        range_options_btn_sizer.AddMany( [(self.range_start_l, 0, wx.EXPAND),
            (self.range_start_tc, 0, wx.EXPAND),
            (self.range_end_l, 0, wx.EXPAND),
            (self.range_end_tc, 0, wx.EXPAND),
            (self.range_every_l, 0, wx.EXPAND),
            (self.range_every_tc, 0, wx.EXPAND) ])
        range_options_sizer = wx.BoxSizer(wx.VERTICAL)
        range_options_sizer.Add(self.range_combo, 0, wx.ALL|wx.EXPAND, 0)
        range_options_sizer.Add(range_options_btn_sizer, 0, wx.ALL|wx.EXPAND, 0)
        range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        range_sizer.Add(self.take_range_btn, 0, wx.ALL|wx.EXPAND, 0)
        range_sizer.Add(range_options_sizer, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer = wx.BoxSizer(wx.VERTICAL)
        compare_sizer.Add(self.onscreen_compare_l, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.set_as_compare_btn, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.use_compare, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.compare_style_cb, 0, wx.ALL|wx.EXPAND, 0)
        stack_cap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stack_cap_sizer.Add(self.cap_stack_btn, 0, wx.ALL|wx.EXPAND, 0)
        stack_cap_sizer.Add(self.capture_stack_count, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer = wx.BoxSizer(wx.VERTICAL)
        anal_sizer.Add(self.anal_tools_l, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer.Add(stack_cap_sizer, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer.Add(self.set_style_cb, 0, wx.ALL|wx.EXPAND, 0)

        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(load_save_btn_sizer, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.cam_select_l, 0, wx.ALL, 0)
        main_sizer.Add(find_select_cam_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.cap_tool_l, 0, wx.ALL, 0)
        main_sizer.Add(self.webcam_cb, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.take_set_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(take_single_photo_btns_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(range_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.use_range_combine, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(compare_sizer, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(anal_sizer, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)


    def read_cam_config_click(self, e):
        # if camera config file path blank set from dirlocs dictonary
        if MainApp.camconf_info_pannel.camconf_path_tc.GetValue() == "":
            try:
                MainApp.camconf_info_pannel.camconf_path_tc.SetValue(MainApp.config_ctrl_pannel.dirlocs_dict['camera_settings'])
            except:
                #raise
                MainApp.camconf_info_pannel.camconf_path_tc.SetValue("/home/" + pi_link_pnl.target_user + "/Pigrow/config/camera_settings.txt")
                print("Camera config location not set in dirlocs, using default location.")
        # read the settings files for camera config settings
        the_cam_settings_path = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + the_cam_settings_path)
        if out == "":
            print("Unable to read settings file -" + the_cam_settings_path)
            return None
        cam_settings = out.splitlines()
        self.camera_settings_dict = {}
        for line in cam_settings:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos+1:]
                self.camera_settings_dict[key] = value

        # putting dictionary info into ui display
        # camera choice
        if "cam_num" in self.camera_settings_dict:
            self.cam_cb.SetValue(self.camera_settings_dict['cam_num'])
        if "cam_opt" in self.camera_settings_dict:
            self.webcam_cb.SetValue(self.camera_settings_dict['cam_opt'])
            #
            if self.camera_settings_dict['cam_opt'] == 'fswebcam':
                MainApp.camconf_info_pannel.show_fswebcam_control()
            elif self.camera_settings_dict['cam_opt'] == 'uvccapture':
                MainApp.camconf_info_pannel.show_uvc_control()
            elif self.camera_settings_dict['cam_opt'] == 'picamcap':
                MainApp.camconf_info_pannel.show_picamcap_control()
            else:
                print("!!! Unknown camera capture option - " + str(self.camera_settings_dict['cam_opt']))
        # basic values
        if "b_val" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_b.SetValue(self.camera_settings_dict['b_val'])
        if "c_val" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_c.SetValue(self.camera_settings_dict['c_val'])
        if "s_val" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_s.SetValue(self.camera_settings_dict['s_val'])
        if "g_val" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_g.SetValue(self.camera_settings_dict['g_val'])
        # pos
        if "x_dim" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_x.SetValue(self.camera_settings_dict['x_dim'])
        if "y_dim" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.tb_y.SetValue(self.camera_settings_dict['y_dim'])
        # extra commands
        if "additonal_commands" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.cmds_string_tb.SetValue(self.camera_settings_dict['additonal_commands'])
        #
        if "fsw_extra" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.SetValue(self.camera_settings_dict['fsw_extra'])
        if "cam_uvc_extra" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.extra_cmds_string_uvc_tb.SetValue(self.camera_settings_dict['cam_uvc_extra'])
        self.write_picam_sets_into_listbox(self.camera_settings_dict)

    def write_picam_sets_into_listbox(self, camera_settings_dict):
        # get list of settings
        picam_settings = []
        for x in range(0, MainApp.camconf_info_pannel.picam_options_list_ctrl.GetItemCount()):
            picam_settings.append(MainApp.camconf_info_pannel.picam_options_list_ctrl.GetItem(x, 0).GetText())
        # check to see if setting is in settings dict and change if it is
        for x in range(0, len(picam_settings)):
            if picam_settings[x] in camera_settings_dict:
                MainApp.camconf_info_pannel.picam_options_list_ctrl.SetItem(x, 1, camera_settings_dict[picam_settings[x]])


    def make_picam_conf_textblock(self):
        text_block = ""
        for x in range(0, MainApp.camconf_info_pannel.picam_options_list_ctrl.GetItemCount()):
            option = MainApp.camconf_info_pannel.picam_options_list_ctrl.GetItem(x, 0).GetText()
            value =  MainApp.camconf_info_pannel.picam_options_list_ctrl.GetItem(x, 1).GetText()
            if not value == "":
                text_block += option + "=" + value + "\n"
        return text_block

    def save_cam_config_click(self, e):
        # Construct camera config file
        config_text = "cam_num=" + str(self.cam_cb.GetValue()) + "\n"
        config_text += "cam_opt=" + str(self.webcam_cb.GetValue()) + "\n"
        config_text += "b_val=" + str(MainApp.camconf_info_pannel.tb_b.GetValue()) + "\n"
        config_text += "s_val=" + str(MainApp.camconf_info_pannel.tb_s.GetValue()) + "\n"
        config_text += "c_val=" + str(MainApp.camconf_info_pannel.tb_c.GetValue()) + "\n"
        config_text += "g_val=" + str(MainApp.camconf_info_pannel.tb_g.GetValue()) + "\n"
        config_text += "x_dim=" + str(MainApp.camconf_info_pannel.tb_x.GetValue()) + "\n"
        config_text += "y_dim=" + str(MainApp.camconf_info_pannel.tb_y.GetValue()) + "\n"
        if not str(MainApp.camconf_info_pannel.cmds_string_tb.GetValue()) == "":
            config_text += "additonal_commands=" + str(MainApp.camconf_info_pannel.cmds_string_tb.GetValue()) + "\n"
        if not str(MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.GetValue()) == "":
            config_text += "fsw_extra=" + str(MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.GetValue()) + "\n"
        # config_text += "uvc_extra=" + str("")
        picam_conf_text = self.make_picam_conf_textblock()
        if not picam_conf_text == "":
            config_text += picam_conf_text

        # Ask if user really wants to update
        camera_settings_path = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        remote_path = os.path.dirname(camera_settings_path)
        config_file_name = os.path.basename(camera_settings_path)
        filename_dbox = wx.TextEntryDialog(self, 'Upload config file with name, \n\n(Change when using more than one camera)', 'Upload config to Pi?', config_file_name)
        if filename_dbox.ShowModal() == wx.ID_OK:
            cam_config_file_name = filename_dbox.GetValue()
        else:
            return "cancelled"
        filename_dbox.Destroy()
        local_base_path = localfiles_info_pnl.local_path_txt.GetLabel()
        temp_local = os.path.join(local_base_path, 'temp/')
        if not os.path.isdir(temp_local):
            os.makedirs(temp_local)
        local_cam_settings_file = os.path.join(temp_local, cam_config_file_name)
        with open(local_cam_settings_file, "w") as f:
            f.write(config_text)
        remote_path = MainApp.config_ctrl_pannel.dirlocs_dict['path'] + "/config/"
        remote_conf_path = os.path.join(remote_path, cam_config_file_name)
        MainApp.localfiles_ctrl_pannel.upload_file_to_folder(local_cam_settings_file, remote_conf_path)


    def list_cams_click(self, e):
        # find picams
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("vcgencmd get_camera")
        if "detected=" in out:
            out = out.split('detected=')[1].strip()
            if out == "0":
                print(' - No Picam detected')
                picam_list = []
            elif out == "1":
                print(' - 1 Picam Detected')
                picam_list = ['picam 0']
            elif out == "2":
                print(' - Dual Picams Detected')
                picam_list = ['picam 0', 'picam 1']
            else:
                print(' - Multipul Picams detected - only using first two: ' + out)
                picam_list = ['picam 0', 'picam 1']
        # find webcams
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/video*")
        cam_list = out.strip().split("\n")
        # add cams to list box
        self.cam_cb.Clear()
        cam_list = picam_list + cam_list
        for cam in cam_list:
            self.cam_cb.Append(cam)

    def clear_picture_area(self):
        children = MainApp.camconf_info_pannel.picture_sizer.GetChildren()
        for child in children:
            item = child.GetWindow()
            item.Destroy()

    def get_camopt_spesific_additional_cmds(self):
        cam_opt = self.webcam_cb.GetValue()
        if cam_opt == "fswebcam":
            cam_additional = MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.GetValue()
        elif cam_opt == "uvccapture":
            print(" !!! uvcapture doesn't yet use additional commands fix ASAP")
            cam_additional = "link to text control for uvc opts here please" # .GetValue()
        else:
            print("!!!! YOU FORGOT TO SET UP OPTIONS HANDLING FOR THIS CAMERA CAPTURE TOOL")
            cam_additional = ""
        return cam_additional

    def install_fswebcam(self):
        print("user asked to install fswebcam on the pi")
        dbox = wx.MessageDialog(self, "fswebcam isn't installed on the pigrow, would you like to install it?", "install fswebcam?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("installing fswebcam on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt install fswebcam --force-yes -y")
            print(out, error)

    def show_image_onscreen(self, img_path, text_label, no_clear=False):
        # clear the picture area
        if not no_clear == True:
            self.clear_picture_area()
        # check if compare is enabled
        if self.use_compare.GetValue():
            if shared_data.camcomf_compare_image == "":
                print(" - No compare image, using this one")
                shared_data.most_recent_camconf_image = img_path
                self.set_as_compare_click("e")
                img_to_show = img_path
            else:
                print("COMPARING!!!!!")
                style = self.compare_style_cb.GetValue()
                img_to_show = image_combine.combine([shared_data.camcomf_compare_image, img_path], style)
        else:
            img_to_show = img_path


        # Display image in the picture sizer
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticText(MainApp.camconf_info_pannel,  label=text_label), 0, wx.ALL, 2)
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticBitmap(MainApp.camconf_info_pannel, -1, wx.Image(img_to_show, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        shared_data.most_recent_camconf_image = img_path
        MainApp.camconf_info_pannel.SetSizer(MainApp.camconf_info_pannel.main_sizer)
        MainApp.camconf_info_pannel.SetupScrolling()

    def set_as_compare_click(self, e):
        file_to_set = shared_data.most_recent_camconf_image
        print(" - Setting " + file_to_set + " as compare image.")
        without_filename = os.path.split(file_to_set)[0]
        filetype = os.path.split(file_to_set)[1].split(".")[1]
        compare_path = os.path.join(without_filename, "compare_image." + filetype)
        shutil.copy(file_to_set, compare_path)
        shared_data.camcomf_compare_image = compare_path

    def cap_stack_click(self, e):
        # THIS IS HERE FOR TESTING - REMOVE WHEN DONE
        module_name = "image_combine"
        if module_name in sys.modules:
            del sys.modules[module_name]
        import image_combine
        #
        pic_amount = int(self.capture_stack_count.GetValue())
        # take photos and add path to a list
        # read current settings
        cam_set = self.cam_cb.GetValue()
        cam_opt = self.webcam_cb.GetValue()
        cam_b = MainApp.camconf_info_pannel.tb_b.GetValue()
        cam_c = MainApp.camconf_info_pannel.tb_c.GetValue()
        cam_s = MainApp.camconf_info_pannel.tb_s.GetValue()
        cam_g = MainApp.camconf_info_pannel.tb_g.GetValue()
        cam_x = MainApp.camconf_info_pannel.tb_x.GetValue()
        cam_y = MainApp.camconf_info_pannel.tb_y.GetValue()
        opts_test_str = MainApp.camconf_info_pannel.setting_string_tb.GetValue()
        cam_additional = self.get_camopt_spesific_additional_cmds()
        #
        filename_list = []
        for x in range(0, pic_amount):
            filename = "test_noise_" + str(x) + ".jpg"
            info, remote_img_path = self.take_test_image(cam_s, cam_c, cam_g, cam_b, cam_x, cam_y, cam_set, cam_opt, filename, None, None, cam_additional)
            filename_list.append(remote_img_path)
        # download photos to local temp folder
        local_filenames = []
        for photo_path in filename_list:
            picture_name = photo_path.split("/")[-1]
            local_temp_img_path = os.path.join("temp", picture_name)
            print("  - Downloading " + picture_name)
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, photo_path, local_temp_img_path)
            local_base_path = localfiles_info_pnl.local_path_txt.GetLabel()
            local_path = os.path.join(local_base_path, local_temp_img_path)
            local_filenames.append(local_path)

        # combine image to show noise and movement
        style = self.set_style_cb.GetValue()
        output_path = os.path.join(local_base_path, "temp/combined.jpg")
        img_to_show = image_combine.multi_combine(local_filenames, style, output_path)
        # img_to_show = image_combine.combine_diff(local_filenames)
        #img_to_show.save(output_path)
        # display image on the screen
        self.show_image_onscreen(img_to_show, "Combined difference of " + str(pic_amount) + " images.")


    def take_saved_set_click(self, e):
        settings_file = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        outpath = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/'
        # check if picam or webcam and take with appropriate script
        camera = self.cam_cb.GetValue()
        if 'picam' in camera:
            print("Taking photo using picamcap.py")
            cmd = '/home/' + pi_link_pnl.target_user + '/Pigrow/scripts/cron/picamcap.py caps=' + outpath + ' set=' + settings_file
        else:
            print("Taking photo using camcap.py")
            cmd = '/home/' + pi_link_pnl.target_user + '/Pigrow/scripts/cron/camcap.py caps=' + outpath + ' set=' + settings_file
        # take photo
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        output = out + error
        print (out, error)
        path = output.split("Saving image to:")[1].split("\n")[0].strip()
        # download photo
        local_temp_img_path = os.path.join("temp", "test_settings.jpg")
        img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, path, local_temp_img_path)
        # display on screen
        label = "Taken with settings stored on the Pigrow"
        self.show_image_onscreen(img_path, label)


    def take_set_click(self, e, filename="test_settings.jpg"):
        # take using the settings currently displayed on the screen
        cam_set = self.cam_cb.GetValue()
        cam_opt = self.webcam_cb.GetValue()
        cam_b = MainApp.camconf_info_pannel.tb_b.GetValue()
        cam_c = MainApp.camconf_info_pannel.tb_c.GetValue()
        cam_s = MainApp.camconf_info_pannel.tb_s.GetValue()
        cam_g = MainApp.camconf_info_pannel.tb_g.GetValue()
        cam_x = MainApp.camconf_info_pannel.tb_x.GetValue()
        cam_y = MainApp.camconf_info_pannel.tb_y.GetValue()
        cam_additional = self.get_camopt_spesific_additional_cmds()
        # determine output file name
        outfile = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/test_settings.jpg'
        # take the image
        info, remote_img_path = self.take_test_image(cam_s, cam_c, cam_g, cam_b, cam_x, cam_y, cam_set, cam_opt, outfile, None, None, cam_additional)
        # download and display on screen
        if info == "command not found":
            print("Camera capture program not installed on pigrow! going to try installing i guess...")
            if cam_opt == "fswebcam":
                self.install_fswebcam()
        else:
            local_temp_img_path = os.path.join("temp", filename)
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, remote_img_path, local_temp_img_path)
            # display on screen
            label = "Image taken using local settings"
            self.show_image_onscreen(img_path, label)

    def range_btn_click(self, e):
        '''
        Takes a range of images allowing the user to compare settings more easily.
        '''
        # load settings from ui
        cam_set = self.cam_cb.GetValue()
        cam_opt = self.webcam_cb.GetValue()
        cam_b = MainApp.camconf_info_pannel.tb_b.GetValue()
        cam_c = MainApp.camconf_info_pannel.tb_c.GetValue()
        cam_s = MainApp.camconf_info_pannel.tb_s.GetValue()
        cam_g = MainApp.camconf_info_pannel.tb_g.GetValue()
        cam_x = MainApp.camconf_info_pannel.tb_x.GetValue()
        cam_y = MainApp.camconf_info_pannel.tb_y.GetValue()
        opts_test_str = MainApp.camconf_info_pannel.setting_string_tb.GetValue()
        cam_additional = self.get_camopt_spesific_additional_cmds()
        range_opt = self.range_combo.GetValue()
        range_start = self.range_start_tc.GetValue()
        range_end =self.range_end_tc.GetValue()
        range_every = self.range_every_tc.GetValue()
        if range_opt == "" or range_start == "" or range_end == "" or range_every == "":
            print(" - Need to select range options before creating a range.")
            return None
        range_photo_set = []
        outfolder= '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/'
        local_base_path = localfiles_info_pnl.local_path_txt.GetLabel()
        #cycle through the selected range taking a photo at each point and adding the remote path to range_photo_set
        for changing_range in range(int(range_start), int(range_end) + int(range_every), int(range_every)):
            outfile = outfolder + 'range_' + str(changing_range) + '.jpg'
            if range_opt == 'brightness':
                info, remote_img_path = self.take_test_image(cam_s, cam_c, cam_g, str(changing_range), cam_x, cam_y, cam_set, cam_opt, outfile, None, None, cam_additional)
            elif range_opt == 'contrast':
                info, remote_img_path = self.take_test_image(cam_s, str(changing_range), cam_g , cam_b, cam_x, cam_y, cam_set, cam_opt, outfile, None, None, cam_additional)
            elif range_opt == 'saturation':
                info, remote_img_path = self.take_test_image(str(changing_range), cam_c, cam_g, cam_b, cam_x, cam_y, cam_set, cam_opt, outfile, None, None, cam_additional)
            elif range_opt == 'gain':
                info, remote_img_path = self.take_test_image(cam_s, cam_c, str(changing_range), cam_b, cam_x, cam_y, cam_set, cam_opt, outfile, None, None, cam_additional)
            elif range_opt == 'user':
                info, remote_img_path = self.take_test_image(cam_s, cam_c, cam_g, cam_b, cam_x, cam_y, cam_set, cam_opt, outfile, ctrl_test_value=str(changing_range), ctrl_text_string='"' + opts_test_str + '"', cmd_str=cam_additional)
            range_photo_set.append(remote_img_path)
        # download all the images in the range_photo_set
        self.clear_picture_area()
        local_images = []
        for photo_path in range_photo_set:
            picture_name = photo_path.split("/")[-1]
            local_temp_img_path = os.path.join("temp", picture_name)
            print("  - Downloading " + picture_name)
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, photo_path, local_temp_img_path)
            local_path = os.path.join(local_base_path, local_temp_img_path)
            local_images.append(local_path)
            if not self.use_range_combine.GetValue() == True:
                self.show_image_onscreen(img_path, picture_name, no_clear=True)
        if self.use_range_combine.GetValue() == True:
            style = self.set_style_cb.GetValue()
            output_path = os.path.join(local_base_path, "temp/combined.jpg")
            img_to_show = image_combine.multi_combine(local_images, style, output_path)
            self.show_image_onscreen(img_to_show, "Combined Image")


    def create_temp_picamcap_settings(self, temp_picamcap_settings_path, s_val, c_val, g_val, b_val, x_dim, y_dim, cam_opt, cam_num):
        print(" Creating temporary settings file for picamcap.py config")
        temp_conf = "s_val=" + str(s_val)
        temp_conf += "\nc_val=" + str(c_val)
        temp_conf += "\ng_val=" + str(g_val)
        temp_conf += "\nb_val=" + str(b_val)
        temp_conf += "\nx_dim=" + str(x_dim)
        temp_conf += "\ny_dim=" + str(y_dim)
        temp_conf += "\ncam_opt=" + str(cam_opt)
        temp_conf += "\ncam_num=" + str(cam_num)
        picam_conf_text = self.make_picam_conf_textblock()
        if not picam_conf_text == "":
            temp_conf += "\n" + picam_conf_text
        local_temp_path = os.path.join(localfiles_info_pnl.local_path, "temp")
        local_temp_piccamset_path =  os.path.join(local_temp_path, "temp_picam_sets.txt")
        if not os.path.isdir(local_temp_path):
            os.makedirs(local_temp_path)
        with open(local_temp_piccamset_path, "w") as temp_local:
            temp_local.write(temp_conf)
        MainApp.localfiles_ctrl_pannel.upload_file_to_folder(local_temp_piccamset_path, temp_picamcap_settings_path)


    def take_test_image(self, s_val, c_val, g_val, b_val, x_dim=800, y_dim=600,
                        cam_select='/dev/video0', cam_capture_choice='uvccapture', output_file='~/test_cam_settings.jpg',
                        ctrl_test_value=None, ctrl_text_string=None, cmd_str=''):
        cam_output = '!!!--NO READING--!!!'
        print(" Preparing to take test image...")
        # uvccapture
        if cam_capture_choice == "uvccapture":
            additional_commands = " -d" + cam_select
            cam_cmd = "uvccapture " + additional_commands   #additional commands (camera select)
            cam_cmd += " -S" + s_val #saturation
            cam_cmd += " -C" + c_val #contrast
            cam_cmd += " -G" + g_val #gain
            cam_cmd += " -B" + b_val #brightness
            cam_cmd += " -x"+str(x_dim)+" -y"+str(y_dim) + " "  #x and y dimensions of photo
            cam_cmd += "-v -t0 -o" + output_file                #verbose, no delay, output
        # fswebcam
        elif cam_capture_choice == "fswebcam":
            cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
            cam_cmd += " -d v4l2:" + cam_select
            cam_cmd += " -D 2"      #the delay in seconds before taking photo
            cam_cmd += " -S 5"      #number of frames to skip before taking image
            # to list controls use fswebcam -d v4l2:/dev/video0 --list-controls
            if not b_val == '':
                cam_cmd += " --set brightness=" + b_val
            if not c_val == '':
                cam_cmd += " --set contrast=" + c_val
            if not s_val == '':
                cam_cmd += " --set Saturation=" + s_val
            if not g_val == '':
                cam_cmd += " --set gain=" + g_val
            ##For testing camera ctrl variables
            if not ctrl_text_string == None:
                cam_cmd += " --set \"" + ctrl_text_string + "\"=" + str(ctrl_test_value)
            cam_cmd += " " + cmd_str
            cam_cmd += " --jpeg 90" #jpeg quality
            # cam_cmd += ' --info "HELLO INFO TEXT"'
            cam_cmd += " " + output_file  #output filename'
        elif cam_capture_choice == "picamcap":
            temp_picamcap_settings_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/temp/temp_picamcap_sets.txt"
            self.create_temp_picamcap_settings(temp_picamcap_settings_path, s_val, c_val, g_val, b_val, x_dim, y_dim, cam_capture_choice, cam_select)
            picamcap_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/cron/picamcap.py"
            cam_cmd = picamcap_path + " set=" + temp_picamcap_settings_path + " filename=" + output_file
        else:
            print(" Unknown capture option, please select uvcwebcam, fdwebcam, or picamcap")
        print("~~~~~~~~~~~~~~~~~~~~")
        print ("Taking photo using; " + cam_cmd)
        cam_output, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cam_cmd)
        if "command not found" in error:
            cam_output = "command not found"
        print ("Camera output; " + cam_output + " " + error)
        print("~~~~~~~~~~~~~~~~~~~~")
        return cam_output, output_file

    def take_unset_click(self, e):
        info, remote_img_path = self.take_unset_test_image()
        local_temp_img_path = os.path.join("temp", "test_defaults.jpg")
        img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, remote_img_path, local_temp_img_path)
        label="Picture taken using camera default"
        self.show_image_onscreen(img_path, label)

    def take_unset_test_image(self, x_dim=10000, y_dim=10000, additonal_commands='', cam_capture_choice='uvccapture', output_file=None):
        cam_select = self.cam_cb.GetValue()
        MainApp.status.write_bar("Using camera deafults to take image...")
        if output_file == None:
            output_file = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/test_defaults.jpg'
        cam_capture_choice = self.webcam_cb.GetValue()
        if cam_capture_choice == "uvccapture":
            cam_cmd = "uvccapture " + additonal_commands   #additional commands (camera select)
            cam_cmd += " -x"+str(x_dim)+" -y"+str(y_dim) + " "  #x and y dimensions of photo
            cam_cmd += "-v -t0 -o" + output_file                #verbose, no delay, output
        elif cam_capture_choice == "fswebcam":
            cam_cmd  = "fswebcam -r " + str(x_dim) + "x" + str(y_dim)
            if not cam_select == "":
                cam_cmd += " --device=" + cam_select
            cam_cmd += " -D 2"      #the delay in seconds before taking photo
            cam_cmd += " -S 5"      #number of frames to skip before taking image
            cam_cmd += " --jpeg 90" #jpeg quality
            cam_cmd += " " + output_file  #output filename'
        elif cam_capture_choice == "picamcap":
            cam_cmd = "raspistill -o " + output_file
        else:
            print("Unknown capture option - please select uvc, fswebcam, or picamcap as your option")

        print("---Doing: " + cam_cmd)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cam_cmd)
        MainApp.status.write_bar("Camera output; " + out)
        return out, output_file

    def webcam_combo_go(self, e):
        MainApp.camconf_info_pannel.hide_uvc_control()
        MainApp.camconf_info_pannel.hide_fswebcam_control()
        MainApp.camconf_info_pannel.hide_picamcap_control()
        if self.webcam_cb.GetValue() == 'fswebcam':
            MainApp.camconf_info_pannel.show_fswebcam_control()
        elif self.webcam_cb.GetValue() == 'uvccapture':
            MainApp.camconf_info_pannel.show_uvc_control()
        elif self.webcam_cb.GetValue() == 'picamcap':
            MainApp.camconf_info_pannel.show_picamcap_control()


#
#
#
##  Timelapse Maker Control Panel
#
#
#

class timelapse_info_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # Tab Title
        title_l = wx.StaticText(self,  label='Timelapse Control Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Making timelapse videos using files downloaded from the pigrow', size=(700,30))
        page_sub_title.SetFont(shared_data.sub_title_font)
        # placing the information boxes
        blank_img = wx.Bitmap(400, 400)
        self.first_img_l = wx.StaticText(self,  label='-first image- (date)')
        self.first_image = wx.BitmapButton(self, -1, blank_img, size=(400, 400))
        self.first_image.Bind(wx.EVT_BUTTON, self.first_image_click)
        first_prev_btn = wx.Button(self, label='<')
        first_prev_btn.Bind(wx.EVT_BUTTON, self.first_prev_click)
        self.first_frame_no = wx.TextCtrl(self, size=(75, 25), style=wx.TE_CENTRE)
        self.first_frame_no.Bind(wx.EVT_TEXT, self.first_frame_change)
        first_next_btn = wx.Button(self, label='>')
        first_next_btn.Bind(wx.EVT_BUTTON, self.first_next_click)
        self.last_img_l = wx.StaticText(self,  label='-last image- (date)')
        self.last_image = wx.BitmapButton(self, -1, blank_img, size=(400, 400))
        self.last_image.Bind(wx.EVT_BUTTON, self.last_image_click)
        last_prev_btn = wx.Button(self, label='<')
        last_prev_btn.Bind(wx.EVT_BUTTON, self.last_prev_click)
        self.last_frame_no = wx.TextCtrl(self, size=(75, 25), style=wx.TE_CENTRE)
        self.last_frame_no.Bind(wx.EVT_TEXT, self.last_frame_change)
        last_next_btn = wx.Button(self, label='>')
        last_next_btn.Bind(wx.EVT_BUTTON, self.last_next_click)
        # information area - left GridSizer
        # File Info
        file_info_l = wx.StaticText(self,  label='File Info')
        self.images_found_l = wx.StaticText(self,  label='Images found')
        self.images_found_info = wx.StaticText(self,  label='-images found-')
        self.spare_l = wx.StaticText(self,  label='spare')
        self.spare_info = wx.StaticText(self,  label='-spare-')
        # Animation info
        ani_info_l = wx.StaticText(self,  label='Animation Info')
        self.ani_frame_count_l = wx.StaticText(self,  label='Frame Count')
        self.ani_frame_count_info = wx.StaticText(self,  label='-frame count-')
        self.ani_length_l = wx.StaticText(self,  label='Length ')
        self.ani_length_info = wx.StaticText(self,  label='--')
        # graph area - right side
        graph_opts = ['-', 'Filesize', 'Time difference']
        graph_l = wx.StaticText(self,  label='Graph;', pos=(165, 10))
        self.graph_combo = wx.ComboBox(self, choices = graph_opts, pos=(260,10), size=(125, 25))
        self.graph_combo.Bind(wx.EVT_COMBOBOX, self.graph_combo_go)
        graph_refresh_button = wx.Button(self, label='refresh')
        graph_refresh_button.Bind(wx.EVT_BUTTON, self.graph_refresh)
        self.size_graph = wx.BitmapButton(self, -1, blank_img, size=(400, 400))
        self.size_graph.Bind(wx.EVT_BUTTON, self.graph_clicked)
        # sizers
        # image area
        first_img_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        first_img_buttons_sizer.Add(first_prev_btn, 0, wx.ALL, 2)
        first_img_buttons_sizer.Add(self.first_frame_no, 0, wx.ALL, 2)
        first_img_buttons_sizer.Add(first_next_btn, 0, wx.ALL, 2)
        first_img_sizer = wx.BoxSizer(wx.VERTICAL)
        first_img_sizer.Add(self.first_img_l, 0, wx.ALL, 2)
        first_img_sizer.Add(self.first_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        first_img_sizer.Add(first_img_buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        last_img_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        last_img_buttons_sizer.Add(last_prev_btn, 0, wx.ALL, 2)
        last_img_buttons_sizer.Add(self.last_frame_no, 0, wx.ALL, 2)
        last_img_buttons_sizer.Add(last_next_btn, 0, wx.ALL, 2)
        last_img_sizer = wx.BoxSizer(wx.VERTICAL)
        last_img_sizer.Add(self.last_img_l, 0, wx.ALL, 2)
        last_img_sizer.Add(self.last_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        last_img_sizer.Add(last_img_buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        img_panels_sizer = wx.BoxSizer(wx.HORIZONTAL)
        img_panels_sizer.Add(first_img_sizer, 0, wx.ALL, 5)
        img_panels_sizer.Add(last_img_sizer, 0, wx.ALL, 5)
        # info area - left panel grid sizers
        info_panel_sizer = wx.GridSizer(3, 2, 0, 0)
        info_panel_sizer.AddMany([(self.images_found_l, 0, wx.EXPAND),
            (self.images_found_info, 0, wx.EXPAND),
            (self.spare_l, 0, wx.EXPAND),
            (self.spare_info, 0, wx.EXPAND)])
        ani_panel_sizer = wx.GridSizer(3, 2, 0, 0)
        ani_panel_sizer.AddMany([(self.ani_frame_count_l, 0, wx.EXPAND),
            (self.ani_frame_count_info, 0, wx.EXPAND),
            (self.ani_length_l, 0, wx.EXPAND),
            (self.ani_length_info, 0, wx.EXPAND),])
        text_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        text_panel_sizer.AddStretchSpacer(1)
        text_panel_sizer.Add(file_info_l, 0, wx.ALL, 3)
        text_panel_sizer.Add(info_panel_sizer, 0, wx.ALL, 3)
        text_panel_sizer.AddStretchSpacer(1)
        text_panel_sizer.Add(ani_info_l, 0, wx.ALL, 3)
        text_panel_sizer.Add(ani_panel_sizer, 0, wx.ALL, 3)
        graph_opts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        graph_opts_sizer.Add(graph_l, 0, wx.ALL, 3)
        graph_opts_sizer.Add(self.graph_combo, 0, wx.ALL, 3)
        graph_opts_sizer.Add(graph_refresh_button, 0, wx.ALL, 3)
        graph_sizer = wx.BoxSizer(wx.VERTICAL)
        graph_sizer.Add(graph_opts_sizer, 0, wx.ALL, 3)
        graph_sizer.Add(self.size_graph, 0, wx.ALL, 3)
        lower_half_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_half_sizer.AddStretchSpacer(1)
        lower_half_sizer.Add(text_panel_sizer, 0, wx.ALL, 3)
        lower_half_sizer.AddStretchSpacer(1)
        lower_half_sizer.Add(graph_sizer, 0, wx.ALL, 3)
        lower_half_sizer.AddStretchSpacer(1)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(img_panels_sizer, 0, wx.ALL, 3)
        main_sizer.Add(lower_half_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def first_image_click(self, e):
        first = self.first_ani_pic.ConvertToBitmap()
        dbox = show_image_dialog(None, first, "First image")
        dbox.ShowModal()
        dbox.Destroy()

    def last_image_click(self, e):
        last = self.last_ani_pic.ConvertToBitmap()
        dbox = show_image_dialog(None, last, "Last image")
        dbox.ShowModal()
        dbox.Destroy()

    def graph_clicked(self, e):
        bitmap = self.size_graph.Bitmap
        dbox = show_image_dialog(None, bitmap, "Graph")
        dbox.ShowModal()
        dbox.Destroy()

    def set_first_image(self, filename):
        try:
            self.first_ani_pic = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            first = scale_pic(self.first_ani_pic, 400)
            first = first.ConvertToBitmap()
            MainApp.timelapse_info_pannel.first_image.SetBitmap(first)
            filename = filename.split("/")[-1]
            filename_date = MainApp.timelapse_ctrl_pannel.date_from_fn(filename)
            if not filename_date == None:
                MainApp.timelapse_info_pannel.first_img_l.SetLabel(filename + " (" + str(filename_date) + ")")
            else:
                MainApp.timelapse_info_pannel.first_img_l.SetLabel(filename)
        except:
            print("!! first frame in local caps folder didn't work for timelapse tab.")

    def set_last_image(self, filename):
        try:
            self.last_ani_pic = wx.Image(filename, wx.BITMAP_TYPE_ANY)
            last = scale_pic(self.last_ani_pic, 400)
            last = last.ConvertToBitmap()
            MainApp.timelapse_info_pannel.last_image.SetBitmap(last)
            filename = filename.split("/")[-1]
            filename_date = MainApp.timelapse_ctrl_pannel.date_from_fn(filename)
            if not filename_date == None:
                MainApp.timelapse_info_pannel.last_img_l.SetLabel(filename + " (" + str(filename_date) + ")")
            else:
                MainApp.timelapse_info_pannel.last_img_l.SetLabel(filename)
        except:
            print("!! Last frame in local caps folder didn't work for timelapse tab.")
            raise

    def first_frame_change(self, e):
        frame_no_text = MainApp.timelapse_info_pannel.first_frame_no.GetValue()
        if not frame_no_text.isdigit():
            return None
        frame_number = int(frame_no_text)
        if frame_number < 1:
            frame_number = 1
            MainApp.timelapse_info_pannel.first_frame_no.ChangeValue(str(frame_number))
        max_frame = int(MainApp.timelapse_info_pannel.last_frame_no.GetValue())
        if frame_number > max_frame:
            frame_number = max_frame
            MainApp.timelapse_info_pannel.first_frame_no.ChangeValue(str(frame_number))
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_first_image(filename)
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def last_frame_change(self, e):
        frame_no_text = MainApp.timelapse_info_pannel.last_frame_no.GetValue()
        if not frame_no_text.isdigit():
            return None
        frame_number = int(frame_no_text)
        if frame_number < int(MainApp.timelapse_info_pannel.first_frame_no.GetValue()):
            frame_number = int(MainApp.timelapse_info_pannel.first_frame_no.GetValue())
            MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(frame_number))
        max_frame = len(MainApp.timelapse_ctrl_pannel.cap_file_paths)
        if frame_number > max_frame:
            frame_number = max_frame
            MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(frame_number))
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_last_image(filename)
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def first_prev_click(self, e):
        frame_number = int(self.first_frame_no.GetValue()) -1
        if frame_number < 1:
            return None #just to break the loop
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_first_image(filename)
        MainApp.timelapse_info_pannel.first_frame_no.ChangeValue(str(frame_number))
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def first_next_click(self, e):
        frame_number = int(self.first_frame_no.GetValue()) +1
        if frame_number > int(self.last_frame_no.GetValue()):
            return None #just to break the loop
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_first_image(filename)
        MainApp.timelapse_info_pannel.first_frame_no.ChangeValue(str(frame_number))
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def last_prev_click(self, e):
        frame_number = int(self.last_frame_no.GetValue()) -1
        if frame_number < int(MainApp.timelapse_info_pannel.first_frame_no.GetValue()):
            return None #just to break the loop
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_last_image(filename)
        MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(frame_number))
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def last_next_click(self, e):
        frame_number = int(self.last_frame_no.GetValue()) +1
        if frame_number > len(MainApp.timelapse_ctrl_pannel.cap_file_paths):
            return None #just to break the loop
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[frame_number - 1]
        self.set_last_image(filename)
        MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(frame_number))
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def set_frame_count(self):
        frame_count = len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list)
        # set length_of_local
        fps = int(MainApp.timelapse_ctrl_pannel.fps_tc.GetValue())
        length_in_sec = frame_count / fps
        length = datetime.timedelta(seconds=length_in_sec)
        length = str(length).split(".")[0]
        self.ani_frame_count_info.SetLabel(str(frame_count))
        self.ani_length_info.SetLabel(length)

    def graph_combo_go(self, e):
        graph_to_show = self.graph_combo.GetValue()
        if graph_to_show == "Filesize":
            #print("Making filesize graph...")
            MainApp.status.write_bar("Creating filesize graph")
            image_to_show = self.make_filesize_graph()
        elif graph_to_show  == "Time difference":
            MainApp.status.write_bar("Creating time difference graph")
            image_to_show = self.make_time_dif_graph()
        else:
            #print("No graph")
            image_to_show = wx.Bitmap(400, 400)
        self.size_graph.SetBitmap(image_to_show)
        MainApp.status.write_bar("--")

    def graph_refresh(self, e):
        self.graph_combo_go(None)

    def make_time_dif_graph(self):
        counter = 0
        counter_list = []
        timediff_list = []
        time_of_prev_file = MainApp.timelapse_ctrl_pannel.date_from_fn(MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0])
        for file in MainApp.timelapse_ctrl_pannel.trimmed_frame_list[1:]:
            time_of_file =  MainApp.timelapse_ctrl_pannel.date_from_fn(file)
            time_diff = time_of_prev_file - time_of_file
            counter = counter + 1
            counter_list.append(counter)
            timediff_list.append(time_diff.total_seconds())
            time_of_prev_file = time_of_file
        # make graph
        plt.figure(1, figsize=(12, 10))
        ax = plt.subplot()
        ax.bar(counter_list, timediff_list, color='green')
        #ax.plot(counter, filesize)
        plt.title("Time difference between images")
        plt.xlabel("File number")
        plt.ylabel("Time differeence")
        graph_path = os.path.join(localfiles_info_pnl.local_path, "temp", "timediff_graph.png")
        print("-------------------", graph_path)
        plt.savefig(graph_path)
        plt.close()
        return wx.Bitmap(graph_path)

    def make_filesize_graph(self):
        counter = 0
        counter_list = []
        filesize_list = []
        for file in MainApp.timelapse_ctrl_pannel.trimmed_frame_list:
            filesize = os.path.getsize(file)
            counter = counter + 1
            counter_list.append(counter)
            filesize_list.append(filesize)
            #print(counter, filesize)
        #print("Found ", len(counter_list), " filesizes")
        plt.figure(1, figsize=(12, 10))
        ax = plt.subplot()
        ax.bar(counter_list, filesize_list, color='green')
        #ax.plot(counter, filesize)
        plt.title("filesize")
        plt.xlabel("file number")
        plt.ylabel("filesize")
        graph_path = os.path.join(localfiles_info_pnl.local_path, "temp", "filesize_graph.png")
        print("-------------------", graph_path)
        plt.savefig(graph_path)
        plt.close()
        return wx.Bitmap(graph_path)

class timelapse_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(150,-1), style=wx.TAB_TRAVERSAL)
        # Capture controlls
        #quick_capture_l = wx.StaticText(self,  label='Quick Capture',size=(100,25))
        #quick_capture_l.SetFont(shared_data.sub_title_font)
        #capture_start_btn = wx.Button(self, label='Start capture')
        #capture_start_btn.Bind(wx.EVT_BUTTON, self.start_capture_click)
        # path options
        path_l = wx.StaticText(self,  label='Image Path',size=(100,25))
        path_l.SetFont(shared_data.sub_title_font)
        open_caps_folder_btn = wx.Button(self, label='Open Caps Folder')
        open_caps_folder_btn.Bind(wx.EVT_BUTTON, self.open_caps_folder_click)
        select_set_btn = wx.Button(self, label='Select\nCaps Set')
        select_set_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_set_click)
        select_folder_btn = wx.Button(self, label='Select\nCaps Folder')
        select_folder_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_folder_click)
        # frame slect - range, limit to start / end dates, etc
        frame_select_l = wx.StaticText(self,  label='Frames',size=(100,25))
        frame_select_l.SetFont(shared_data.sub_title_font)
        range_l = wx.StaticText(self,  label='Use Every')
        self.range_tc = wx.TextCtrl(self, value="1")
        range_options = ['Strict', 'Average', 'Rolling Average', 'Largest']
        self.range_combo = wx.ComboBox(self, choices = range_options, size=(100,25), value='Average')
        limit_to_l = wx.StaticText(self,  label='Last')
        self.limit_to_num = wx.TextCtrl(self, value="", size=(50,25))
        limit_options = ['all', 'hours', 'days', 'weeks','months']
        self.limit_combo = wx.ComboBox(self, choices = limit_options, size=(100,25), value='all')
        size_min_l = wx.StaticText(self,  label='Min File Size')
        self.size_min_limit = wx.TextCtrl(self, value="", size=(100,25))
        calculate_frames_btn = wx.Button(self, label='Calculate Frames')
        calculate_frames_btn.Bind(wx.EVT_BUTTON, self.calculate_frames_click)
        # make overlay set
        make_log_overlay_set_btn = wx.Button(self, label='Overlay Log Info')
        make_log_overlay_set_btn.Bind(wx.EVT_BUTTON, self.make_log_overlay_set)
        make_image_overlay_set_btn = wx.Button(self, label='Overlay Image Set')
        make_image_overlay_set_btn.Bind(wx.EVT_BUTTON, self.make_image_overlay_set)
        # credits frames
        credits_l = wx.StaticText(self,  label='Credits')
        credits_opts = ['none', 'freeze_2']
        self.credits_cb = wx.ComboBox(self, choices = credits_opts, size=(150, 30))

        # audio
        audio_l = wx.StaticText(self,  label='Audio',size=(100,25))
        #audio_l.SetFont(shared_data.sub_title_font)
        self.audio_file_tc = wx.TextCtrl(self)
        set_audio_btn = wx.Button(self, label='...', size=(27,27))
        set_audio_btn.Bind(wx.EVT_BUTTON, self.set_audio_click)
        # Render controlls
        render_l = wx.StaticText(self,  label='Render',size=(100,25))
        render_l.SetFont(shared_data.sub_title_font)
        fps_l = wx.StaticText(self,  label='FPS')
        self.fps_tc = wx.TextCtrl(self, value="25", size=(50,25))
        # outfile
        outfile_l = wx.StaticText(self,  label='Outfile')
        self.out_file_tc = wx.TextCtrl(self)
        set_outfile_btn = wx.Button(self, label='...', size=(27,27))
        set_outfile_btn.Bind(wx.EVT_BUTTON, self.set_outfile_click)
        # buttons
        make_timelapse_btn = wx.Button(self, label='Make Timelapse')
        make_timelapse_btn.Bind(wx.EVT_BUTTON, self.make_timelapse_click)
        play_timelapse_btn = wx.Button(self, label='Play')
        play_timelapse_btn.Bind(wx.EVT_BUTTON, self.play_timelapse_click)
        # Sizers
        #capture_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        #capture_bar_sizer.Add(quick_capture_l, 0, wx.ALL|wx.EXPAND, 3)
        #capture_bar_sizer.Add(capture_start_btn, 0, wx.ALL|wx.EXPAND, 3)
        credits_sizer = wx.BoxSizer(wx.HORIZONTAL)
        credits_sizer.Add(credits_l, 1, wx.ALL, 1)
        credits_sizer.Add(self.credits_cb, 0, wx.ALL|wx.EXPAND, 0)
        audio_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        audio_name_sizer.Add(audio_l, 0, wx.ALL|wx.EXPAND, 3)
        audio_name_sizer.Add(self.audio_file_tc, 1, wx.ALL|wx.EXPAND, 1)
        audio_name_sizer.Add(set_audio_btn, 0, wx.ALL, 0)
        file_bar_select_butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_bar_select_butt_sizer.Add(select_set_btn, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_select_butt_sizer.Add(select_folder_btn, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        file_bar_sizer.Add(path_l, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer.Add(open_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer.Add(file_bar_select_butt_sizer, 0, wx.ALL|wx.EXPAND, 3)
        file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_name_sizer.Add(outfile_l, 0, wx.ALL, 1)
        file_name_sizer.Add(self.out_file_tc, 1, wx.ALL|wx.EXPAND, 1)
        file_name_sizer.Add(set_outfile_btn, 0, wx.ALL, 0)
        fps_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fps_sizer.Add(fps_l, 0, wx.ALL, 1)
        fps_sizer.Add(self.fps_tc, 0, wx.ALL, 1)
        frame_range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frame_range_sizer.Add(range_l, 0, wx.ALL, 1)
        frame_range_sizer.Add(self.range_tc, 0, wx.ALL, 1)
        frame_date_limit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        frame_date_limit_sizer.Add(limit_to_l, 0, wx.ALL, 1)
        frame_date_limit_sizer.Add(self.limit_to_num, 0, wx.ALL, 1)
        frame_date_limit_sizer.Add(self.limit_combo, 0, wx.ALL, 1)
        size_min_limit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        size_min_limit_sizer.Add(size_min_l, 0, wx.ALL, 1)
        size_min_limit_sizer.Add(self.size_min_limit, 0, wx.ALL, 1)
        frame_select_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_select_sizer.Add(frame_select_l, 0, wx.ALL, 1)
        frame_select_sizer.Add(frame_range_sizer, 0, wx.ALL, 1)
        frame_select_sizer.Add(self.range_combo, 0, wx.ALL|wx.ALIGN_RIGHT, 1)
        frame_select_sizer.Add(frame_date_limit_sizer, 0, wx.ALL, 1)
        frame_select_sizer.Add(size_min_limit_sizer, 0, wx.ALL, 1)
        frame_select_sizer.Add(calculate_frames_btn, 0, wx.ALL|wx.ALIGN_RIGHT, 1)
        make_overlay_set_sizer = wx.BoxSizer(wx.VERTICAL)
        make_overlay_set_sizer.Add(make_log_overlay_set_btn, 0, wx.ALL, 3)
        make_overlay_set_sizer.Add(make_image_overlay_set_btn, 0, wx.ALL, 3)
        render_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        render_buttons_sizer.Add(make_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_buttons_sizer.Add(play_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        render_bar_sizer.Add(render_l, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(fps_sizer, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(file_name_sizer, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(render_buttons_sizer, 0, wx.ALL|wx.EXPAND, 3)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        #main_sizer.AddStretchSpacer(1)
        #main_sizer.Add(capture_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(file_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(frame_select_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(make_overlay_set_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(credits_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(audio_name_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(render_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        #create blank lists
        self.trimmed_frame_list = []
        self.cap_file_paths = []

    def start_capture_click(self, e):
        print("Quick Capture feature not yet enabled")

    def make_log_overlay_set(self, e):
        make_log_overlay_dbox = make_log_overlay_dialog(None)
        make_log_overlay_dbox.ShowModal()

    def make_image_overlay_set(self, e):
        make_image_overlay_dbox = make_combined_image_set_dialog(None)
        make_image_overlay_dbox.ShowModal()

    def make_timelapse_click(self, e):
        ofps  = self.fps_tc.GetValue()
        outfile= self.out_file_tc.GetValue()
        #  credits style
        freeze_num = 0
        credit_style = self.credits_cb.GetValue()
        if "_" in credit_style:
            credit_style, setting_num = credit_style.split("_")
        # write text file of frame to use
        temp_folder = os.path.join(localfiles_info_pnl.local_path, "temp")
        if not os.path.isdir(temp_folder):
            os.makedirs(temp_folder)
        listfile = os.path.join(temp_folder, "frame_list.txt")
        frame_list_text_file = open(listfile, "w")
        for file in self.trimmed_frame_list:
            frame_list_text_file.write(file + "\n")
        if credit_style == "freeze":
            freeze_num = int(ofps) * int(setting_num)
            for x in range(0, int(freeze_num)):
                frame_list_text_file.write(self.trimmed_frame_list[-1] + "\n")
        frame_list_text_file.close()
        extra_commands = ""
        if not self.audio_file_tc.GetValue() == "":
            frame_count = len(self.trimmed_frame_list) + freeze_num
            extra_commands += " --audiofile=\"" + str(self.audio_file_tc.GetValue()) + "\" --frames=" + str(frame_count)
        print (" ##  making you a timelapse video...")
        cmd = "mpv mf://@"+listfile+" --mf-fps="+str(ofps)
        cmd += " -o "+outfile+" " + extra_commands
        print(" Running - " + cmd)
        os.system(cmd)
        print(" --- "+ outfile +" Done ---")

    def select_new_caps_set_click(self, e):
        new_cap_path = self.select_folder()
        # find file info and call open caps folder
        cap_dir = os.path.split(new_cap_path)
        cap_set  = cap_dir[1].split("_")[0]  # Used to select set if more than one are present
        cap_type = cap_dir[1].split('.')[1]
        cap_dir = cap_dir[0]
        print(" Selected " + cap_dir + " with capset; " + cap_set + " filetype; " + cap_type)
        self.open_caps_folder(cap_dir, cap_type, cap_set)

    def select_new_caps_folder_click(self, e):
        new_cap_path = self.select_folder()
        # find file info and call open caps folder
        cap_dir = os.path.split(new_cap_path)
        cap_type = cap_dir[1].split('.')[1]
        cap_dir = cap_dir[0]
        print(" Selected " + cap_dir + " filetype; " + cap_type)
        self.open_caps_folder(cap_dir, cap_type, cap_set=None)

    def select_folder(self):
        wildcard = "JPG and PNG files (*.jpg;*.png)|*.jpg;*.png|GIF files (*.gif)|*.gif"
        openFileDialog = wx.FileDialog(self, "Select caps folder", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()
        return new_cap_path

    def set_outfile_click(self, e):
        outfile = self.select_outfile()
        self.out_file_tc.SetValue(outfile)

    def set_audio_click(self, e):
        outfile = self.select_audiofile()
        self.audio_file_tc.SetValue(outfile)

    def select_audiofile(self):
        wildcard = "MP3 files (*.mp3)|*.mp3|WAV files (*.wav)|*.wav"
        default_path = os.path.join(localfiles_info_pnl.local_path, "")
        openFileDialog = wx.FileDialog(self, "Select audio file", "", default_path, wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an audio file to play over your video")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        outfile = openFileDialog.GetPath()
        return outfile

    def select_outfile(self):
        wildcard = "MP4 files (*.mp4)|*.mp4|AVI files (*.avi)|*.avi"
        default_path = os.path.join(localfiles_info_pnl.local_path, "timelapse.mp4")
        openFileDialog = wx.FileDialog(self, "Select output file", "", default_path, wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        outfile = openFileDialog.GetPath()
        return outfile

    def open_caps_folder_click(self, e):
        # opens the caps folder being used in local files tab and finds all images
        cap_dir = os.path.join(localfiles_info_pnl.local_path, localfiles_info_pnl.caps_folder)
        cap_type = "jpg"
        self.open_caps_folder(cap_dir, cap_type)

    def open_caps_folder(self, cap_dir, cap_type="jpg", cap_set=None):
        MainApp.timelapse_ctrl_pannel.cap_file_paths = []
        for filefound in os.listdir(cap_dir):
            if filefound.endswith(cap_type):
                file_path = os.path.join(cap_dir, filefound)
                if not cap_set == None:
                    if filefound.split("_")[0] == cap_set:
                        MainApp.timelapse_ctrl_pannel.cap_file_paths.append(file_path)
                else: #when using all images in the folder regardless of the set
                    MainApp.timelapse_ctrl_pannel.cap_file_paths.append(file_path)
        MainApp.timelapse_ctrl_pannel.cap_file_paths.sort()
        # fill the infomation boxes
        MainApp.timelapse_info_pannel.images_found_info.SetLabel(str(len(MainApp.timelapse_ctrl_pannel.cap_file_paths)))
        # set first and last images
        MainApp.timelapse_info_pannel.first_frame_no.ChangeValue("1")
        MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(len(MainApp.timelapse_ctrl_pannel.cap_file_paths)))
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[0]
        MainApp.timelapse_info_pannel.set_first_image(filename)
        filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[-1]
        MainApp.timelapse_info_pannel.set_last_image(filename)
        MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def calculate_frames_click(self, e):
        # make frame list
        self.trimmed_frame_list = []
        first_frame= int(MainApp.timelapse_info_pannel.first_frame_no.GetValue()) -1
        last_frame = int(MainApp.timelapse_info_pannel.last_frame_no.GetValue())
        for x in range(first_frame, last_frame):
            self.trimmed_frame_list.append(self.cap_file_paths[x])
        print("-------\nStarting frame count;", len(self.trimmed_frame_list))

        # Limit using date options
        start_point_cutoff = self.trim_list_by_date_self_limit_combo()
        if not start_point_cutoff == None:
            self.trimmed_frame_list = self.limit_list_by_start_point(start_point_cutoff, self.trimmed_frame_list)
        if len(self.trimmed_frame_list) == 0:
            self.mention_zero_length("limit by date")
            return None

        # Limit using filesize minimum
        min_filesize = self.size_min_limit.GetValue()
        if not min_filesize.isdigit():
            min_filesize = 1
        self.trimmed_frame_list = self.remove_using_min_filesize(int(min_filesize), self.trimmed_frame_list)
        if len(self.trimmed_frame_list) == 0:
            self.mention_zero_length("limit by filesize")
            return None

        # limit using range
        # Limit using range function
        use_every = self.range_tc.GetValue()
        if not use_every.isdigit():
            use_every = None
        else:
            use_every = int(use_every)
        if not use_every == None:
            range_type = self.range_combo.GetValue()
            if range_type == "Strict":
                self.trimmed_frame_list = self.take_every_nth(use_every, self.trimmed_frame_list)
            elif range_type == "Average":
                self.trimmed_frame_list = self.find_closest_ave_frames(use_every, self.trimmed_frame_list, type="all")
            elif range_type == "Rolling Average":
                self.trimmed_frame_list = self.find_closest_ave_frames(use_every, self.trimmed_frame_list, type="rolling")
            elif range_type == "Largest":
                self.trimmed_frame_list = self.find_largest_frames(use_every, self.trimmed_frame_list)
            print("List trimmed using " + range_type + " every " + str(use_every) + " list contains " + str(len(self.trimmed_frame_list)) + " frames")
        if len(self.trimmed_frame_list) == 0:
            self.mention_zero_length("use every")
            return None

        # update screen
        MainApp.timelapse_info_pannel.set_frame_count()

    def mention_zero_length(self, cause):
        msg = "The current " + cause + " settings would result in a zero length animation"
        MainApp.status.write_warning(msg)
        #dbox = scroll_text_dialog(None, msg, "Error; zero length animation", False)
        #dbox.ShowModal()
        #dbox.Destroy()
        self.trimmed_frame_list = []
        MainApp.timelapse_info_pannel.set_frame_count()

    def take_every_nth(self, use_every, original_frame_list):
        trimmed_list = []
        for frame in range(0, len(original_frame_list), use_every):
            trimmed_list.append(original_frame_list[frame])
        return trimmed_list

    def find_largest_frames(self, block_size, original_frame_list):
        largest_file_list = []
        for x in range(0, len(original_frame_list), block_size):
            temp_list = []
            for y in range(0, block_size):
                try:
                    temp_list.append(original_frame_list[x+y])
                except:
                    print("index out of range - because of the y probably")
            largest_file_size = 0
            for item in temp_list:
                filesize = os.path.getsize(item)
                if largest_file_size < int(filesize):
                    largest_file_size = int(filesize)
                    largset_file = (item)
            largest_file_list.append(largset_file)
        return largest_file_list

    def find_closest_ave_frames(self, block_size, original_frame_list,type="all"):
        #find average of all files
        if type == "all":
            total_file_size = 0
            for file in original_frame_list:
                total_file_size = total_file_size + int(os.path.getsize(file))
            average_file_size = total_file_size / len(original_frame_list)
            print(average_file_size)
        #
        most_ave_file_list = []
        for x in range(0, len(original_frame_list), block_size):
            temp_list = []
            for y in range(0, block_size):
                try:
                    temp_list.append(original_frame_list[x+y])
                except:
                    print("index out of range - because of the y probably")
            # find rolling average file size
            if type =="rolling":
                total_file_size = 0
                for file in temp_list:
                    total_file_size = total_file_size + int(os.path.getsize(file))
                average_file_size = total_file_size / len(temp_list)
                print(average_file_size)
            # find smallest difference from average
            smallest_diff = average_file_size + 1
            for file in temp_list:
                size = int(os.path.getsize(file))
                size_diff = abs(average_file_size - size)
                if smallest_diff > size_diff:
                    #print("smaller size diference - ", size_diff)
                    most_average_file = file
                    smallest_diff = size_diff
                #else:
                    #print("nope", size_diff)
            most_ave_file_list.append(most_average_file)
        return most_ave_file_list

    def remove_using_min_filesize(self, min_filesize, list_to_trim):
        print("Filesize min, ", min_filesize)
        newly_trimmed_list = []
        for file in list_to_trim:
            filesize = os.path.getsize(file)
            if filesize > int(min_filesize):
                newly_trimmed_list.append(file)
        print("filesize - trimmed list to:", len(newly_trimmed_list))
        return newly_trimmed_list

    def trim_list_by_date_self_limit_combo(self):
        # Establish cut off point
        limit_period_unit = self.limit_combo.GetValue()
        if not limit_period_unit == "all":
            limit_period = self.limit_to_num.GetValue()
            if limit_period.isdigit():
                limit_period = int(limit_period)
            else:
                self.limit_to_num.SetValue("1")
                limit_period = 1
            if limit_period_unit == "days":
                datecheck = datetime.timedelta(days=limit_period)
                start_point_cutoff = datetime.datetime.now() - datecheck
            elif limit_period_unit == "hours":
                datecheck=datetime.timedelta(hours=limit_period)
                start_point_cutoff = datetime.datetime.now() - datecheck
            elif limit_period_unit == "weeks":
                datecheck=datetime.timedelta(weeks=limit_period)
                start_point_cutoff = datetime.datetime.now() - datecheck
            elif limit_period_unit == "months":
                datecheck=datetime.timedelta(weeks=limit_period)
                start_point_cutoff = datetime.datetime.now() - datecheck
            else:
                print(" !!!! Error in trim list by date checkbox?")
            print("Cut off time for animation set to - " + str(start_point_cutoff))
            return start_point_cutoff
        else:
            return None

    def limit_list_by_start_point(self, start_point_cutoff, list_to_trim):
        # loop through taking only those images taken after the start_time_cutoff
        list_trimmed_by_startpoint = []
        for item in list_to_trim:
            pic_time = self.date_from_fn(item)
            if pic_time >= start_point_cutoff:
                list_trimmed_by_startpoint.append(item)
        print("list trimmed to start date " + str(start_point_cutoff) + " now " + str(len(list_trimmed_by_startpoint)) + " frames long")
        return list_trimmed_by_startpoint

    def date_from_fn(self, thefilename):
        #
        # DOUBLE - use one or the other
        #
        if "." in thefilename and "_" in thefilename:
            fdate = thefilename.split(".")[0].split("_")[-1]
            if len(fdate) == 10 and fdate.isdigit():
                fdate = datetime.datetime.utcfromtimestamp(float(fdate))
            else:
                return None
            return fdate
        #elif "-" in thefilename:
        #    try:
        #        date = thefilename.split("-")[1]
        #        # 10-2018 05 05 20 12 12-03
        #        file_datetime = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
        #        text_date = file_datetime.strftime('%Y-%m-%d %H:%M')
        #        return file_datetime
        #    except:
        #        print("!! Tried to parse filename as Motion date but failed " + str(thefilename))
        #        return None, None
        else:
            return None

    def play_timelapse_click(self, e):
        outfile= self.out_file_tc.GetValue()
        cmd = "mpv " + outfile
        os.system(cmd)

class select_text_pos_on_image(wx.Dialog):
    """
    Shows the image on the screen for user to click to place text
        """
    def __init__(self, *args, **kw):
        super(select_text_pos_on_image, self).__init__(*args, **kw)
        self.InitUI()
        pic_one = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0]
        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(pic_one, wx.BITMAP_TYPE_ANY)
        size = bitmap.GetSize()
        self.SetSize((size[0], size[1]))
        self.SetTitle("Click to select text box top-left corner")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # panel
        pnl = wx.Panel(self)
        pic_one = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0]
        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(pic_one, wx.BITMAP_TYPE_ANY)
        size = bitmap.GetSize()
        image = wx.StaticBitmap(self, -1, bitmap, size=(size[0], size[1]))
        image.Bind(wx.EVT_LEFT_DOWN, self.on_click)
        self.SetSize((size[0]), size[1])

    def on_click(self, e):
        x, y = e.GetPosition()
        timelapse_ctrl_pnl.log_x_placement = x
        timelapse_ctrl_pnl.log_y_placement = y
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class make_log_overlay_dialog(wx.Dialog):
    """
    For creating a set of images with log file data overlaid
        """
    def __init__(self, *args, **kw):
        super(make_log_overlay_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 600))
        self.SetTitle("Make Log Overlay Image Set")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        '''
        self.log_file_cb.GetValue()        - name of the log files
        self.example_line.GetLabel()       - an example line, the last non-blank line inte file
        self.split_character_tc.GetValue() - character used to split the info in each line (@, >, etc)
        '''
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Create Log Overlay Image Set')
        box_label.SetFont(shared_data.title_font)
        # log file select - drop down box
        log_path_l = wx.StaticText(self,  label='Log - ')
        local_path = localfiles_info_pnl.local_path
        local_logs_path = os.path.join(local_path, "logs")
        local_log_files = caps_files = os.listdir(local_logs_path)
        self.log_file_cb = wx.ComboBox(self, choices = local_log_files)
        self.log_file_cb.Bind(wx.EVT_TEXT, self.log_file_cb_go)
        self.download_log_btn = wx.Button(self, label='download')
        self.download_log_btn.Bind(wx.EVT_BUTTON, self.download_log_click)
        ##
        # log file data grabbing options (split character, position of date, key/label), value)
        ##
        top_l = wx.StaticText(self,  label='Data Extraction Options')
        top_l.SetFont(shared_data.sub_title_font)
        example_line_l = wx.StaticText(self,  label='Example Line -')
        self.example_line = wx.StaticText(self,  label='')
        # split line character
        split_character_l = wx.StaticText(self,  label='Split Character')
        self.split_character_tc = wx.TextCtrl(self, size=(90, 25))
        self.split_character_tc.Bind(wx.EVT_TEXT, self.split_line_text)
        # row of date related options
        date_pos_l = wx.StaticText(self,  label='Date')
        self.date_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.date_pos_cb.Bind(wx.EVT_TEXT, self.date_pos_go)
        self.date_pos_cb.Disable()
        self.date_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.date_pos_split_tc.Bind(wx.EVT_TEXT, self.date_pos_split_text)
        self.date_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.date_pos_split_cb.Bind(wx.EVT_TEXT, self.date_pos_split_select)
        self.date_pos_ex = wx.StaticText(self,  label='')
        # row of value related options
        value_pos_l = wx.StaticText(self,  label='Value')
        self.value_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.value_pos_cb.Bind(wx.EVT_TEXT, self.value_pos_go)
        self.value_pos_cb.Disable()
        self.value_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.value_pos_split_tc.Bind(wx.EVT_TEXT, self.value_pos_split_text)
        self.value_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.value_pos_split_cb.Bind(wx.EVT_TEXT, self.value_pos_split_go)
        self.value_pos_ex = wx.StaticText(self,  label='')
        # row of key related options
        key_pos_l = wx.StaticText(self,  label='Key')
        self.key_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.key_pos_cb.Bind(wx.EVT_TEXT, self.key_pos_go)
        self.key_pos_cb.Disable()
        self.key_manual_l = wx.StaticText(self,  label='Label -')
        self.key_manual_tc = wx.TextCtrl(self, size=(150, 25))
        self.key_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.key_pos_split_tc.Bind(wx.EVT_TEXT, self.key_pos_split_text)
        self.key_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.key_pos_split_cb.Bind(wx.EVT_TEXT, self.key_pos_split_go)
        self.key_pos_ex = wx.StaticText(self,  label='')
        self.key_matches_l = wx.StaticText(self,  label='Limit to Key Matching -')
        self.key_matches_tc = wx.TextCtrl(self, size=(150, 25))
        ##
        # text placement options (size, colour, placement)
        ##
        display_l = wx.StaticText(self,  label='Display Options')
        display_l.SetFont(shared_data.sub_title_font)
        display_size_l = wx.StaticText(self,  label='Text Size -')
        self.display_size_tc = wx.TextCtrl(self, size=(60, 25), value="50")
        # color
        display_colour_l = wx.StaticText(self,  label='Colour -')
        display_colour_r = wx.StaticText(self,  label='r')
        display_colour_g = wx.StaticText(self,  label='g')
        display_colour_b = wx.StaticText(self,  label='b')
        self.display_colour_r_tc = wx.TextCtrl(self, size=(50, 25), value="0")
        self.display_colour_g_tc = wx.TextCtrl(self, size=(50, 25), value="0")
        self.display_colour_b_tc = wx.TextCtrl(self, size=(50, 25), value="0")
        self.pick_colour_btn = wx.Button(self, label='Pick Colour', size=(175, 30))
        self.pick_colour_btn.Bind(wx.EVT_BUTTON, self.pick_colour_click)
        # pos
        display_pos_l = wx.StaticText(self,  label='Display Position')
        display_x_l = wx.StaticText(self,  label='X (right) -')
        self.display_x_tc = wx.TextCtrl(self, size=(60, 25), value="10")
        max_x, max_y = self.get_image_size()
        self.display_x_max = wx.StaticText(self,  label='max -' + str(max_x))
        display_y_l = wx.StaticText(self,  label='Y (down) -')
        self.display_y_tc = wx.TextCtrl(self, size=(60, 25), value="10")
        self.display_y_max = wx.StaticText(self,  label='max -' + str(max_y))
        self.set_text_pos_btn = wx.Button(self, label='Set Position', size=(175, 30))
        self.set_text_pos_btn.Bind(wx.EVT_BUTTON, self.set_text_pos_click)
        # tick boxes
        self.show_time_diff = wx.CheckBox(self, label='Show Time Diff')
        self.use_prior_log_entries_tb =  wx.CheckBox(self, label='Use Lowest Time Diff')
        self.use_prior_log_entries_tb.SetValue(True)
        min_real_time_to_show_logs_l = wx.StaticText(self,  label='Min (real-time) to show -')
        self.min_real_time_to_show_logs_tc = wx.TextCtrl(self, size=(60, 25), value="15")

        # overwrite or rename checkbox

        # ok and cancel Buttons
        self.make_btn = wx.Button(self, label='Create', size=(175, 30))
        self.make_btn.Bind(wx.EVT_BUTTON, self.make_click)
        self.cancel_btn = wx.Button(self, label='Close', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)


        # Sizers
        log_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_path_sizer.Add(log_path_l, 0, wx.ALL, 3)
        log_path_sizer.Add(self.log_file_cb, 0, wx.ALL, 3)
        log_path_sizer.Add(self.download_log_btn, 0,  wx.ALL, 3)
        # Data Extraction Area
        split_chr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        split_chr_sizer.Add(split_character_l, 0,  wx.ALL, 3)
        split_chr_sizer.Add(self.split_character_tc, 0,  wx.ALL, 3)
        data_extract_example_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        data_extract_example_line_sizer.Add(example_line_l, 0, wx.ALL, 3)
        data_extract_example_line_sizer.Add(self.example_line, 0, wx.ALL, 3)
        data_extract_pos_sizer = wx.GridSizer(3, 5, 0, 0)
        data_extract_pos_sizer.AddMany( [(date_pos_l, 0, wx.EXPAND),
            (self.date_pos_cb, 0, wx.EXPAND),
            (self.date_pos_split_tc, 0, wx.EXPAND),
            (self.date_pos_split_cb, 0, wx.EXPAND),
            (self.date_pos_ex, 0, wx.EXPAND),
            (value_pos_l, 0, wx.EXPAND),
            (self.value_pos_cb, 0, wx.EXPAND),
            (self.value_pos_split_tc, 0, wx.EXPAND),
            (self.value_pos_split_cb, 0, wx.EXPAND),
            (self.value_pos_ex, 0, wx.EXPAND),
            (key_pos_l, 0, wx.EXPAND),
            (self.key_pos_cb, 0, wx.EXPAND),
            (self.key_pos_split_tc, 0, wx.EXPAND),
            (self.key_pos_split_cb, 0, wx.EXPAND),
            (self.key_pos_ex, 0, wx.EXPAND) ])
        key_match_sizer = wx.BoxSizer(wx.HORIZONTAL)
        key_match_sizer.Add(self.key_matches_l, 0, wx.ALL, 3)
        key_match_sizer.Add(self.key_matches_tc, 0, wx.ALL, 3)
        data_extract_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        data_extract_label_sizer.Add(self.key_manual_l, 0 , wx.ALL, 3)
        data_extract_label_sizer.Add(self.key_manual_tc, 0 , wx.ALL, 3)
        data_extract_sizer = wx.BoxSizer(wx.VERTICAL)
        data_extract_sizer.Add(top_l, 0 , wx.ALL, 3)
        data_extract_sizer.Add(data_extract_example_line_sizer, 0 , wx.ALL, 3)
        data_extract_sizer.Add(split_chr_sizer, 0 , wx.ALL, 3)
        data_extract_sizer.Add(data_extract_pos_sizer, 0 , wx.ALIGN_CENTER_HORIZONTAL, 3)
        data_extract_sizer.Add(data_extract_label_sizer, 0, wx.ALL, 3)
        data_extract_sizer.Add(key_match_sizer, 0, wx.ALL, 3)
        # screen pos, colour, style
        text_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_size_sizer.Add(display_size_l, 0, wx.ALL, 3)
        text_size_sizer.Add(self.display_size_tc, 0, wx.ALL, 3)
        text_colour_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text_colour_sizer.Add(display_colour_l, 0, wx.ALL, 3)
        text_colour_sizer.Add(display_colour_r, 0, wx.ALL, 3)
        text_colour_sizer.Add(self.display_colour_r_tc, 0, wx.ALL, 3)
        text_colour_sizer.Add(display_colour_g, 0, wx.ALL, 3)
        text_colour_sizer.Add(self.display_colour_g_tc, 0, wx.ALL, 3)
        text_colour_sizer.Add(display_colour_b, 0, wx.ALL, 3)
        text_colour_sizer.Add(self.display_colour_b_tc, 0, wx.ALL, 3)
        text_colour_sizer.Add(self.pick_colour_btn, 0, wx.ALL, 3)
        test_pos_2ndline_sizer = wx.BoxSizer(wx.HORIZONTAL)
        test_pos_2ndline_sizer.Add(display_x_l, 0, wx.ALL, 3)
        test_pos_2ndline_sizer.Add(self.display_x_tc, 0, wx.ALL, 3)
        test_pos_2ndline_sizer.Add(self.display_x_max, 0, wx.ALL, 3)
        test_pos_2ndline_sizer.Add(display_y_l, 0, wx.ALL, 3)
        test_pos_2ndline_sizer.Add(self.display_y_tc, 0, wx.ALL, 3)
        test_pos_2ndline_sizer.Add(self.display_y_max, 0, wx.ALL, 3)

        test_pos_2ndline_sizer.Add(self.set_text_pos_btn, 0, wx.ALL, 3)
        test_pos_sizer = wx.BoxSizer(wx.VERTICAL)
        test_pos_sizer.Add(display_pos_l, 0, wx.ALL, 3)
        test_pos_sizer.Add(test_pos_2ndline_sizer, 0, wx.ALL, 3)
        text_display_sizer = wx.BoxSizer(wx.VERTICAL)
        text_display_sizer.Add(display_l, 0, wx.ALL, 3)
        text_display_sizer.Add(text_size_sizer, 0, wx.ALL, 3)
        text_display_sizer.Add(text_colour_sizer, 0, wx.ALL, 3)
        text_display_sizer.Add(test_pos_sizer, 0, wx.ALL, 3)
        misc_tick_boxes_sizer = wx.BoxSizer(wx.HORIZONTAL)
        misc_tick_boxes_sizer.Add(self.show_time_diff, 0, wx.ALL, 3)
        misc_tick_boxes_sizer.Add(self.use_prior_log_entries_tb, 0, wx.ALL, 3)
        misc_tick_boxes_sizer.Add(min_real_time_to_show_logs_l, 0, wx.ALL, 3)
        misc_tick_boxes_sizer.Add(self.min_real_time_to_show_logs_tc, 0, wx.ALL, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.make_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(log_path_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(data_extract_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(text_display_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(misc_tick_boxes_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)
        self.key_manual_l.Hide()
        self.key_manual_tc.Hide()
        self.key_matches_l.Hide()
        self.key_matches_tc.Hide()

    def pick_colour_click(self, e):
        data = wx.ColourData()
        data.SetChooseFull(True)
        dialog = wx.ColourDialog(self, data)
        if dialog.ShowModal() == wx.ID_OK:
            retData = dialog.GetColourData()
            col = retData.GetColour()
        self.display_colour_r_tc.SetValue(str(col[0]))
        self.display_colour_g_tc.SetValue(str(col[1]))
        self.display_colour_b_tc.SetValue(str(col[2]))

    def get_image_size(self):
        pic_one = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0]
        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(pic_one, wx.BITMAP_TYPE_ANY)
        size = bitmap.GetSize()
        return size[0], size[1]

    def set_text_pos_click(self, e):
        set_text_pos_dbox = select_text_pos_on_image(None)
        set_text_pos_dbox.ShowModal()
        x = timelapse_ctrl_pnl.log_x_placement
        y = timelapse_ctrl_pnl.log_y_placement
        self.display_x_tc.SetValue(str(x))
        self.display_y_tc.SetValue(str(y))
        #print("set_text_pos_click", x, y)

    def log_file_cb_go(self, e):
        local_path = localfiles_info_pnl.local_path
        log_file_to_use = self.log_file_cb.GetValue()
        log_path = os.path.join(local_path, "logs", log_file_to_use)
        first_line = ""
        #print("- Reading first line -")
        with open(log_path) as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(0, 0)
            if not size == 0:
                while first_line == "":
                    first_line = f.readline()
                    if first_line == "\n" or first_line == "\r\n":
                        first_line = ""
                    if size == f.tell():
                        first_line = ' -- Blank File --'
        first_line = first_line.strip()
        #print("---" + first_line + "---")
        #print("----------------------")
        self.example_line.SetLabel(first_line)
        split_chr_choices = self.get_split_chr(first_line)
        if len(split_chr_choices) == 1:
            self.split_character_tc.SetValue(split_chr_choices[0])
        else:
            self.split_character_tc.SetValue("")
            self.clear_and_reset_fields()

    def get_split_chr(self, line):
        non_split_characters = ["-", ":", ".", ",", " ", "_"]
        non_split_characters += ["a","b","c","d","e","f","g","h","i", "j", "k", "l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        split_chr_choices = []
        for chr in line:
            if not chr.isdigit() and not chr.lower() in non_split_characters:
                if not chr in split_chr_choices:
                    split_chr_choices.append(chr)
        return split_chr_choices

    def clear_and_reset_fields(self):
        self.date_pos_ex.SetLabel("")
        self.value_pos_ex.SetLabel("")
        self.key_pos_ex.SetLabel("")
        self.date_pos_cb.SetValue("")
        self.value_pos_cb.SetValue("")
        self.key_pos_cb.SetValue("None")
        self.date_pos_cb.Disable()
        self.value_pos_cb.Disable()
        self.key_pos_cb.Disable()
        self.date_pos_cb.Clear()
        self.value_pos_cb.Clear()
        self.key_pos_cb.Clear()
        self.key_pos_cb.Append("None")
        self.key_pos_cb.Append("Manual")
        #
        self.date_pos_split_cb.Disable()
        self.date_pos_split_cb.SetValue("")
        self.date_pos_split_cb.Clear()
        self.value_pos_split_cb.Disable()
        self.value_pos_split_cb.SetValue("")
        self.value_pos_split_cb.Clear()
        self.key_pos_split_cb.Disable()
        self.key_pos_split_cb.SetValue("")
        self.key_pos_split_cb.Clear()
        self.date_pos_split_tc.Disable()
        self.value_pos_split_tc.Disable()
        self.key_pos_split_tc.Disable()
        self.date_pos_split_tc.SetValue("")
        self.value_pos_split_tc.SetValue("")
        self.key_pos_split_tc.SetValue("")



    def split_line_text(self, e):
        self.clear_and_reset_fields()
        split_character = self.split_character_tc.GetValue()
        if not split_character == "":
            line = self.example_line.GetLabel()
            if split_character in line:
                self.split_line = line.split(split_character)
                self.date_pos_cb.Enable()
                self.value_pos_cb.Enable()
                self.key_pos_cb.Enable()
                for x in range(0, len(self.split_line)):
                    self.date_pos_cb.Append(str(x))
                    self.value_pos_cb.Append(str(x))
                    self.key_pos_cb.Append(str(x))
            else:
                return None
            # check each entry to see if it's a date format we understand
            found = None
            #self.date_pos_split_tc.SetValue("")
            for item in range(0, len(self.split_line)):
                try:
                    test_date = datetime.datetime.strptime(self.split_line[item], '%Y-%m-%d %H:%M:%S.%f')
                    self.date_pos_cb.SetValue(str(item))
                    self.date_pos_ex.SetLabel(self.split_line[item])
                    self.date_pos_ex.SetForegroundColour((75,200,75))
                    found = str(item)
                except:
                    split_chr_choices = self.get_split_chr(self.split_line[item])
                    if len(split_chr_choices) == 1:
                        item_split_again = self.split_line[item].split(split_chr_choices[0])
                        for position_in_split_again_item in range(0, len(item_split_again)):
                            try:
                                date_to_test = item_split_again[position_in_split_again_item]
                                print(date_to_test)
                                test_date = datetime.datetime.strptime(date_to_test, '%Y-%m-%d %H:%M:%S.%f')
                                self.date_pos_cb.SetValue(str(item))
                                self.date_pos_split_tc.SetValue(split_chr_choices[0])
                            except:
                                pass
                # after sorting through each item in the line react to results and try to guess value if possible
            if found == None:
                print("timelapse make log overlay - Could not auto detect date")
            else:
                if len(self.split_line) == 2:
                    if found == "0":
                        self.value_pos_cb.SetValue("1")
                        self.value_pos_ex.SetLabel(self.split_line[1])
                    elif found == "1":
                        self.value_pos_cb.SetValue("0")
                        self.value_pos_ex.SetLabel(self.split_line[0])

    def key_pos_go(self, e):
        key_pos = self.key_pos_cb.GetValue()
        value_pos = self.key_pos_cb.GetValue()

        if not key_pos == "" and not key_pos == "None" and not key_pos == "Manual" and not key_pos == None:
            self.key_pos_ex.SetLabel(self.split_line[int(key_pos)])
            self.key_pos_split_tc.Enable()
            self.key_pos_split_tc.Show()
            self.key_pos_split_cb.Show()
            self.key_manual_l.Show()
            self.key_manual_tc.Show()
            self.key_matches_l.Show()
            self.key_matches_tc.Show()
            #self.SetSizer(main_sizer)
        elif key_pos == "Manual":
            self.key_pos_split_tc.Hide()
            self.key_pos_split_cb.Hide()
            self.key_pos_split_cb.SetValue("")
            self.key_manual_l.Show()
            self.key_manual_tc.Show()
            self.key_matches_l.Hide()
            self.key_matches_tc.Hide()
            #self.SetSizer(main_sizer)
        elif key_pos == "None" or key_pos == "" or key_pos == None:
        #    self.key_pos_ex.SetLabel("")
            self.key_pos_split_tc.Hide()
            self.key_pos_split_cb.SetValue("")
            self.key_pos_split_cb.Hide()
            self.key_manual_l.Hide()
            self.key_manual_tc.Hide()
            self.key_matches_l.Hide()
            self.key_matches_tc.Hide()
        self.Layout()

    def key_pos_split_text(self, e):
        self.key_pos_split_cb.Clear()
        val_pos_ex = self.key_pos_ex.GetLabel()
        split_symbol = self.key_pos_split_tc.GetValue()
        if not split_symbol == "":
            if split_symbol in val_pos_ex:
                key_split = val_pos_ex.split(split_symbol)
                for x in key_split:
                    self.key_pos_split_cb.Append(x)
                self.key_pos_split_cb.Enable()
            else:
                self.key_pos_split_cb.Disable()
                self.key_pos_split_cb.SetValue("")
                self.key_pos_go("e")
        else:
            self.key_pos_split_cb.Disable()
            self.key_pos_split_cb.SetValue("")
            self.key_pos_go("e")

    def key_pos_split_go(self, e):
        key_pos = self.key_pos_cb.GetValue()
        if key_pos == "None" or key_pos == "Manual":
            self.key_pos_ex.SetLabel("")
        else:
            key_pos_split = self.key_pos_split_cb.GetValue()
            self.key_pos_ex.SetLabel(key_pos_split)

    def value_pos_go(self, e):
        '''
        Triggers when the combobox for selecting which position in the
        split line the value to display is found.
           - The value might then be split again if needed using value_pos_split_tc
        '''
        val_pos = self.value_pos_cb.GetValue()
        if not val_pos == "":
            self.value_pos_ex.SetLabel(self.split_line[int(val_pos)])
            self.value_pos_split_tc.Enable()
        else:
            self.value_pos_split_tc.Disable()
        self.make_btn_enable()

    def value_pos_split_text(self, e):
        '''
        Triggers when the text in the textctrl for splitting the
        value (which should be already split from the log line)
        is changed either by user or machine.
        '''
        self.value_pos_split_cb.Clear()
        val_pos_ex = self.value_pos_ex.GetLabel()
        split_symbol = self.value_pos_split_tc.GetValue()
        if not split_symbol == "":
            if split_symbol in val_pos_ex:
                value_split = val_pos_ex.split(split_symbol)
                for x in value_split:
                    self.value_pos_split_cb.Append(x)
                self.value_pos_split_cb.Enable()
            else:
                self.value_pos_split_cb.Disable()
                self.value_pos_split_cb.SetValue("")
                self.value_pos_go("e")
        else:
            self.value_pos_split_cb.Disable()
            self.value_pos_split_cb.SetValue("")
            self.value_pos_go("e")

    def value_pos_split_go(self, e):
        '''
        displays the text as an example if value has been split again
        after being split from the original log entry line.
        '''
        value_pos_split = self.value_pos_split_cb.GetValue()
        self.value_pos_ex.SetLabel(value_pos_split)

    def date_pos_go(self, e):
        date_pos = self.date_pos_cb.GetValue()
        if date_pos.isdigit():
            date_pos = int(date_pos)
            if not date_pos > len(self.split_line):
                ex_date = self.split_line[date_pos]
                self.date_pos_ex.SetLabel(ex_date)
                try:
                    if "." in ex_date:
                        test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S')
                    self.date_pos_ex.SetForegroundColour((75,200,75))
                    self.date_good = True
                except:
                    self.date_pos_ex.SetForegroundColour((220,75,75))
                    self.date_pos_split_tc.Enable()
                    self.date_good = False
        else:
            self.date_good = False
        self.make_btn_enable()

    def date_pos_split_text(self, e):
        self.date_pos_split_cb.Enable()
        date_pos_ex = self.date_pos_ex.GetLabel()
        split_symbol = self.date_pos_split_tc.GetValue()
        if not split_symbol == "":
            if split_symbol in date_pos_ex:
                date_split = date_pos_ex.split(split_symbol)
                self.date_pos_split_cb.Clear()
                for x in date_split:
                    self.date_pos_split_cb.Append(x)
                if len(date_split) == 2:
                    try:
                        if "." in ex_date:
                            test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S.%f')
                        else:
                            test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S')
                        self.date_pos_split_cb.SetValue(date_split[0])
                    except:
                        try:
                            if "." in ex_date:
                                test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S.%f')
                            else:
                                test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S')
                            self.date_pos_split_cb.SetValue(date_split[1])
                        except:
                            print(" - timelapse logs overlay can't auto determine date - " + str(date_split))
            else:
                self.date_pos_split_cb.Disable()
                self.date_pos_split_cb.SetValue("")
                self.date_pos_go("e")
        else:
            self.date_pos_split_cb.Disable()
            self.date_pos_split_cb.SetValue("")
            self.date_pos_go("e")

    def date_pos_split_select(self, e):
        date_pos = self.date_pos_split_cb.GetValue()
        self.date_pos_ex.SetLabel(date_pos)
        try:
            if "." in ex_date:
                test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S.%f')
            else:
                test_date = datetime.datetime.strptime(ex_date, '%Y-%m-%d %H:%M:%S')
            self.date_pos_ex.SetForegroundColour((75,200,75))
            self.date_good = True
        except:
            self.date_pos_ex.SetForegroundColour((220,75,75))
            self.date_good = False
        self.make_btn_enable()

    def make_btn_enable(self):
        val_pos = self.value_pos_cb.GetValue()
        if self.date_good and val_pos.isdigit():
            self.make_btn.Enable()
        else:
            self.make_btn.Disable()

    def download_log_click(self, e):
        log_to_update = self.log_file_cb.GetValue()
        user_log_loc = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/" + log_to_update
        MainApp.localfiles_ctrl_pannel.download_file_to_folder(user_log_loc, "logs/" + log_to_update)
        print(" - updated local version of - " + log_to_update)

    def make_click(self, e):
        log_file = self.log_file_cb.GetValue()
        local_path = localfiles_info_pnl.local_path
        log_file_path = os.path.join(local_path, "logs", log_file)
        # data extraction options
        split_character = self.split_character_tc.GetValue()
        date_pos = int(self.date_pos_cb.GetValue())
        value_pos = int(self.value_pos_cb.GetValue())
        key_pos = self.key_pos_cb.GetValue()
        if key_pos == "" or key_pos == "None":
            key_pos = None
        if not key_pos == "Manual" and not key_pos == None:
            key_pos = int(key_pos)
        date_split_char = self.date_pos_split_tc.GetValue()
        date_split_pos = self.date_pos_split_cb.GetSelection()
        value_split_char = self.value_pos_split_tc.GetValue()
        value_split_pos = self.value_pos_split_cb.GetSelection()
        key_split_char = self.key_pos_split_tc.GetValue()
        key_split_pos = self.key_pos_split_cb.GetSelection()
        key_matches = self.key_matches_tc.GetValue()
        min_real_time_to_show_logs = int(self.min_real_time_to_show_logs_tc.GetValue())
        use_prior_log_entries = self.use_prior_log_entries_tb.GetValue()


        # Open Log and Read Content into a list of lines
        with open(log_file_path, "r") as log_file:
            log_file_text = log_file.read()
        log_data_list = [] # to be filled with [date, value, key] lists
        for line in log_file_text.splitlines():
            if split_character in line:
                split_line = line.strip().split(split_character)
                # Determine date
                line_date = split_line[date_pos]
                if not date_split_char == "":
                    if not date_split_pos == None:
                        line_date = line_date.split(date_split_char)[date_split_pos]
                try:
                    line_date = datetime.datetime.strptime(line_date, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    line_date == None
                # check date for case where there's no fraction of a second
                if type(line_date) == type(""):
                    try:
                        line_date = datetime.datetime.strptime(line_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        line_date == None
                # Determine Value
                line_value = split_line[value_pos]
                if not value_split_char == "":
                    if not value_split_pos == None:
                        line_value = line_value.split(value_split_char)[value_split_pos]
                # Determine Key
                if not key_pos == None:
                    if key_pos == "Manual":
                        line_key = self.key_manual_tc.GetValue()
                    else:
                        line_key = split_line[key_pos]
                    #
                    if not key_split_char == "":
                        if not key_split_pos == None:
                            line_key = line_key.split(key_split_char)[key_split_pos]
                else:
                    line_key = ""
                # Write all (date, value, key) to log_data_list
                if not line_date == None:
                    if type(line_date) == type(""):
                        print(" Date - " + line_date + " - did not convert, ignoring line.")
                    else:
                        # check if key selection is limited by matching and ignore those that don't match if so...
                        if not key_matches == "":
                            if key_matches == line_key:
                                log_data_list.append([line_key, line_date, line_value])
                        else:
                            log_data_list.append([line_key, line_date, line_value])
                #
        print(" Found " + str(len(log_data_list)) + " items in the log and " + str(len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list)) + " Images" )
        # WE NOW HAVE A LIST OF THE LOG ITEMS

        # find a place to put the new caps, change this up so the user can choose when it works
        new_caps_folder = os.path.join(localfiles_info_pnl.local_path, "new_caps")
        if not os.path.isdir(new_caps_folder):
            os.makedirs(new_caps_folder)
        # associate log entiries with caps files
        print("________________________________________________________________")
        print("---------------Creating new image set---------------------------")
        counter = 0
        for file in MainApp.timelapse_ctrl_pannel.trimmed_frame_list:
            print(" - Working on;" + str(file))
            file_date = MainApp.timelapse_ctrl_pannel.date_from_fn(file)
            closest_log_info = []
            # log data list contains a sequential list of log entries, the most recent is last (assuming that's how the file is written, it should be)
            #print("len log data list - ", len(log_data_list), " counter = ", counter)
            first_log_after = None                           # reset counter and first log location
            while first_log_after == None:                   # loop until we find the first log item after the pics date
                if log_data_list[counter][1] > file_date:    # if the current list item's date is after the current file's date
                    first_log_after = counter                # set first_log_after to the position in the log which finishes this loop
                else:
                    counter = counter + 1                        # otherwise increase the counter and loop again...
                if counter > len(log_data_list):             # unless you're already at the end of the list...
                    first_log_after = len(log_data_list)     # in which case use the final item in the list
            # test previous date
            time_diff = self.directionless_timedelta(log_data_list[counter][1], file_date)
            if use_prior_log_entries == True:
                test_time_diff = self.directionless_timedelta(log_data_list[counter - 1][1], file_date)
                if time_diff > test_time_diff:
                    closest_log_info = log_data_list[first_log_after - 1]
                else:
                    closest_log_info = log_data_list[first_log_after]
            else:
                closest_log_info = log_data_list[first_log_after]
            # closest_log_info now set to the closest date or closest date after the image
            # check selected log entry isn't too old
            max_age_dif = datetime.timedelta(minutes=min_real_time_to_show_logs)
            #time_diff_log_to_cap = closest_log_info[1] - file_date
            time_diff_log_to_cap = self.directionless_timedelta(closest_log_info[1], file_date)
            if not time_diff_log_to_cap > max_age_dif:
                #print(" age is within the limit " + str(time_diff_log_to_cap))
                write_this_one = True
            else:
                #print("log item too old..." + str(time_diff_log_to_cap))
                write_this_one = False
            # display and write the log info onto the image file
            #print(closest_log_info, file)
            text_to_write = closest_log_info[0] + " " + closest_log_info[2]
            if self.show_time_diff.GetValue() == True:
                text_to_write += "\n time diff -- " + str(time_diff_log_to_cap).split(".")[0]
            print("       - " + text_to_write)
            #text_to_write += "\n   -- " + str(file_date) + " - " + str(closest_log_info[1])
            # set colour, size, pos
            font_size = self.display_size_tc.GetValue()
            font = wx.Font(int(font_size), wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
            font_r = self.display_colour_r_tc.GetValue()
            font_g = self.display_colour_g_tc.GetValue()
            font_b = self.display_colour_b_tc.GetValue()
            if not font_r.isdigit():
                font_r = "250"
            if not font_g.isdigit():
                font_g = "250"
            if not font_b.isdigit():
                font_b = "250"
            font_col = [int(font_r), int(font_g), int(font_b)]
            pos_x  = self.display_x_tc.GetValue()
            if not pos_x.isdigit():
                pos_x = "10"
                print("X value set wrong - setting text placement x to 10")
            pos_y  = self.display_y_tc.GetValue()
            if not pos_y.isdigit():
                pos_y = "10"
                print("Y value set wrong - setting text placement y to 10")
            #
            if write_this_one:
                self.WriteTextOnBitmap(text_to_write, file, pos=(pos_x, pos_y), font=font, color=font_col)
            else:
                self.WriteTextOnBitmap("", file, pos=(pos_x, pos_y), font=font, color=font_col)
        print(" - Overlay set complete....")
        # when it's written the whole set
        folder_name_for_output = "edited_caps"
        local_path = localfiles_info_pnl.local_path
        edited_caps_path = os.path.join(local_path, folder_name_for_output)
        created = "  -- Created " + str(len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list)) + " new files in " + edited_caps_path
        print(created)
        msg_text = created + "\n\n" + "Switch to " + edited_caps_path + " folder"
        mbox = wx.MessageDialog(None, msg_text, "Open newly created caps folder?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if sure == wx.ID_YES:
            print("- switching to new folder")
            MainApp.timelapse_ctrl_pannel.range_tc.SetValue("1")
            MainApp.timelapse_ctrl_pannel.size_min_limit.SetValue("")
            timelapse_ctrl_pnl.open_caps_folder(None, edited_caps_path)
        else:
            print("= Not switching to new folder")
        self.Destroy()

    def directionless_timedelta(self, time1, time2):
        if time1 > time2:
            return time1 - time2
        else:
            return time2 - time1

    def WriteTextOnBitmap(self, text, bitmap_path, pos=(0, 0), font=None, color=None):
        folder_name_for_output = "edited_caps"
        new_name = os.path.split(bitmap_path)[1]
        #new_name = "log_" + new_name
        local_path = localfiles_info_pnl.local_path
        local_path = os.path.join(local_path, folder_name_for_output)
        if not os.path.isdir(local_path):
            os.makedirs(local_path)
        new_name = os.path.join(local_path, new_name)
        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(bitmap_path, wx.BITMAP_TYPE_ANY)
        # use memoryDC to writ on the image
        memDC = wx.MemoryDC()
        # set options
        if font:
            memDC.SetFont(font)
        else:
            font = wx.Font(40, wx.TELETYPE, wx.ITALIC, wx.NORMAL)
            memDC.SetFont(font)
        if color:
            text_colour = wx.Colour(int(color[0]), int(color[1]), int(color[2]))
        else:
            text_colour = x.Colour(0,0,0)
        # select image and overlay text
        memDC.SelectObject(bitmap)
        try:
            memDC.SetTextForeground(text_colour) #wxColour(color[0], color[1], color[2]))
            memDC.DrawText(text, int(pos[0]), int(pos[1]))
        except :
            print("unable to add text to image, sorry - " + bitmap_path)
            raise
        memDC.SelectObject(wx.NullBitmap)
        bitmap.SaveFile(new_name, wx.BITMAP_TYPE_JPEG)

    def OnClose(self, e):
        self.Destroy()

class make_combined_image_set_dialog(wx.Dialog):
    """
    For creating a set of images with another set overlaid
        """
    def __init__(self, *args, **kw):
        super(make_combined_image_set_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 600))
        self.SetTitle("Make Image Overlay Image Set")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # set Default
        self.overlay_x = 10
        self.overlay_y = 10
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Create Picture in Picture Set')
        box_label.SetFont(shared_data.title_font)
        # log file select - drop down box
        log_path_l = wx.StaticText(self,  label='Log - ')
        self.select_images_btn = wx.Button(self, label='Select image set to inlay')
        self.select_images_btn.Bind(wx.EVT_BUTTON, self.select_images_click)
        #
        self.set_overlay_pos_btn = wx.Button(self, label='Set Position', size=(175, 30))
        self.set_overlay_pos_btn.Bind(wx.EVT_BUTTON, self.set_overlay_pos_click)

        # ok and cancel Buttons
        self.make_btn = wx.Button(self, label='Create', size=(175, 30))
        self.make_btn.Bind(wx.EVT_BUTTON, self.make_click)
        self.cancel_btn = wx.Button(self, label='Close', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.make_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.select_images_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.set_overlay_pos_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def select_images_click(self, e):
        file = MainApp.timelapse_ctrl_pannel.select_folder()
        caps_to_inlay = os.path.split(file)[0]
        # make list of file names for the image set to be inlaid
        shared_data.second_img_file_paths = []
        for filefound in os.listdir(caps_to_inlay):
            file_path = os.path.join(caps_to_inlay, filefound)
            shared_data.second_img_file_paths.append(file_path)
        shared_data.second_img_file_paths.sort()

    def set_overlay_pos_click(self, e):
        set_overlay_pos_dbox = select_overlay_pos_on_image(None)
        set_overlay_pos_dbox.ShowModal()
        self.overlay_x = timelapse_ctrl_pnl.img_x_placement
        self.overlay_y = timelapse_ctrl_pnl.img_y_placement
        #self.display_x_tc.SetValue(str(x))
        #self.display_y_tc.SetValue(str(y))
        print("set_overlay_pos_click", x, y)


    def make_click(self, e):
        # Check user intended to do this and get name of folder to store images
        msg = 'Choose a name for your new image set\n\n'
        msg += "This will create a new image set containing " + str(len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list))
        msg += " frames."
        folder_name_dbox = wx.TextEntryDialog(self, msg, 'Name Overlaid Image Set', "composit_set")
        if folder_name_dbox.ShowModal() == wx.ID_OK:
            comp_base_name = folder_name_dbox.GetValue()
        else:
            return "cancelled"
        folder_name_dbox.Destroy()
        new_caps_folder = os.path.join(localfiles_info_pnl.local_path, comp_base_name)
        if not os.path.isdir(new_caps_folder):
            os.makedirs(new_caps_folder)
        #

        # cycle through main image set finding finding the appropriate frame to overlay
        for x in range(0, len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list)):
            current_file = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[x]
            base_date_string = current_file.split(".")[0].split("_")[-1]
            base_file_date = MainApp.timelapse_ctrl_pannel.date_from_fn(current_file)
            second_set_frame_num = self.find_closest_frame(base_file_date, shared_data.second_img_file_paths)
            inlay_file_date = timelapse_ctrl_pnl.date_from_fn(None, shared_data.second_img_file_paths[second_set_frame_num])
            time_diff_between_overlay_and_base = make_log_overlay_dialog.directionless_timedelta("s", base_file_date, inlay_file_date)
            # combine images and save to new file
            new_file_name = "two_image_" + base_date_string + ".jpg"
            print(x, "/", len(MainApp.timelapse_ctrl_pannel.trimmed_frame_list), " : ", second_set_frame_num, "/", len(shared_data.second_img_file_paths),  " ---- ", time_diff_between_overlay_and_base)
            new_file_name = os.path.join(new_caps_folder, new_file_name)
            self.paint_image_on_image(current_file, shared_data.second_img_file_paths[second_set_frame_num], new_file_name, time_diff_between_overlay_and_base)
        print(" - Image set ", comp_base_name, " completed -")

    def find_closest_frame(self, base_frame_date, second_cap_file_paths):
        counter = 0
        first_log_after = None
        # loop compairing dates until we find the first log item after the pics date
        while first_log_after == None:
            inlay_file_date = MainApp.timelapse_ctrl_pannel.date_from_fn(second_cap_file_paths[counter])
            if inlay_file_date > base_frame_date:
                first_log_after = counter
            else:
                counter = counter + 1
            if counter > len(second_cap_file_paths):
                first_log_after = len(second_cap_file_paths)

        # check if prior frame is closer
        if not first_log_after == 0:
            time_diff_current_place = make_log_overlay_dialog.directionless_timedelta("s", base_frame_date, inlay_file_date)
            time_diff_prior_place   = make_log_overlay_dialog.directionless_timedelta("s", base_frame_date, MainApp.timelapse_ctrl_pannel.date_from_fn(second_cap_file_paths[first_log_after - 1]))
            #time_diff_current_place  = inlay_file_date - base_frame_date
            #time_diff_prior_place    = MainApp.timelapse_ctrl_pannel.date_from_fn(second_cap_file_paths[first_log_after - 1]) - base_frame_date
            if time_diff_prior_place < time_diff_current_place:
                first_log_after = first_log_after - 1
        return first_log_after

    def paint_image_on_image(self, main_image, sub_image, new_name, time_diff_between_overlay_and_base=""):
        dist_from_top = self.overlay_y
        dist_from_left = self.overlay_x
        scale_to_percent = 50

        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(main_image, wx.BITMAP_TYPE_ANY)
        sub_bitmap = wx.Bitmap(1, 1)
        sub_bitmap.LoadFile(sub_image, wx.BITMAP_TYPE_ANY)
        size_w, size_h = sub_bitmap.GetSize()
        sub_dc = wx.MemoryDC(sub_bitmap)
        dc = wx.MemoryDC(bitmap)
        new_w = size_w / 100 * scale_to_percent
        new_h = size_h / 100 * scale_to_percent
        dc.StretchBlit(dist_from_left, dist_from_top, new_w, new_h, sub_dc, 0, 0, size_w, size_h)
        if not time_diff_between_overlay_and_base == "":
            text = str(time_diff_between_overlay_and_base)
            text_x = dist_from_left + (new_w / 3)
            text_y = dist_from_top + new_h + 10
            dc.SetTextForeground(wx.Colour(240, 120, 90))
            dc.SetFont(wx.Font(40, wx.TELETYPE, wx.ITALIC, wx.NORMAL))
            dc.DrawText(text, text_x, text_y)
        # StretchBlit(self, xdest, ydest, dstWidth, dstHeight, source, xsrc, ysrc, srcWidth, srcHeight, logicalFunc=COPY, useMask=False, xsrcMask=DefaultCoord, ysrcMask=DefaultCoord)
        bitmap.SaveFile(new_name, wx.BITMAP_TYPE_JPEG)

    def OnClose(self, e):
        self.Destroy()

class select_overlay_pos_on_image(wx.Dialog):
    """
    Shows the image on the screen for user to click to place overlay
        """
    def __init__(self, *args, **kw):
        super(select_overlay_pos_on_image, self).__init__(*args, **kw)
        self.InitUI()
        self.SetTitle("Click to select overlay images top-left corner")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # panel
        pnl = wx.Panel(self)
        self.scale_to_percent = 50
        # ok and cancel Buttons
        self.ok_btn = wx.Button(self, label='Ok', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Close', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # display the image
        pic_one = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0]
        self.base_bitmap = wx.Bitmap(1, 1)
        self.base_bitmap.LoadFile(pic_one, wx.BITMAP_TYPE_ANY)
        size = self.base_bitmap.GetSize()
        self.image = wx.StaticBitmap(self, -1, self.base_bitmap, size=(size[0], size[1]))
        self.image.Bind(wx.EVT_LEFT_DOWN, self.on_click)

        #self.SetSize((size[0]), size[1])

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0,  wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.image, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizerAndFit(main_sizer)


    def on_click(self, e):
        self.x, self.y = e.GetPosition()
        #
        overlay_ex_image = shared_data.second_img_file_paths[0]
        print (overlay_ex_image)
        inlay_bitmap = wx.Bitmap(1, 1)
        inlay_bitmap.LoadFile(overlay_ex_image, wx.BITMAP_TYPE_ANY)
        base_bitmap_path = MainApp.timelapse_ctrl_pannel.trimmed_frame_list[0]
        base_bitmap = wx.Bitmap(1, 1)
        base_bitmap.LoadFile(base_bitmap_path, wx.BITMAP_TYPE_ANY)
        #

        size_w, size_h = inlay_bitmap.GetSize()
        sub_dc = wx.MemoryDC(inlay_bitmap)
        base_dc = wx.MemoryDC(base_bitmap)
        new_w = size_w / 100 * self.scale_to_percent
        new_h = size_h / 100 * self.scale_to_percent
        base_dc.StretchBlit(self.x, self.y, new_w, new_h, sub_dc, 0, 0, size_w, size_h)
        self.image.SetBitmap(base_bitmap)


    def ok_click(self, e):
        timelapse_ctrl_pnl.img_x_placement = self.x
        timelapse_ctrl_pnl.img_y_placement = self.y
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()
#
#
#
##  Additional Sensor Tab
#
#
#

class sensors_info_pnl(wx.Panel):
    """
    This deals with sensors that are listed in to Pigrows config file,
        the format it expects is;
             sensor_chirp01_type=chirp
             sensor_chirp01_log=/home/pi/Pigrow/logs/chirp01.txt
             sensor_chirp01_loc=i2c:0x31
             sensor_chirp01_extra=min:100,max:1000,power_gpio=20,etc:,etc:etc,etc
    """
    #
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # Tab Title
        title_l = wx.StaticText(self,  label='Sensor Control Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Link aditional sensors to the pigrow', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)
        # placing the information boxes
        # sensor table
        self.sensor_list = self.sensor_table(self, 1)
        self.sensor_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.sensor_table.double_click)
        self.sensor_list.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        self.sensor_list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.sensor_got_focus)
        # trigger table
        trigger_sub_title =  wx.StaticText(self,  label='Log Triggers ')
        trigger_sub_title.SetFont(shared_data.sub_title_font)
        self.trigger_script_activity_cron =  wx.StaticText(self,  label="")
        self.trigger_script_activity_live =  wx.StaticText(self,  label="")
        self.trigger_list = self.trigger_table(self, 1)
        self.trigger_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.trigger_table.double_click)
        self.trigger_list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.trigger_got_focus)
        self.trigger_list.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        # sizers
        trigger_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        trigger_label_sizer.Add(trigger_sub_title, 1, wx.ALL, 3)
        trigger_label_sizer.Add(self.trigger_script_activity_cron, 1, wx.ALL, 3)
        trigger_label_sizer.Add(self.trigger_script_activity_live, 1, wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.sensor_list, 1, wx.ALL|wx.EXPAND, 3)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(trigger_label_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.trigger_list, 1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def sensor_got_focus(self, e):
        trigger_focus = self.trigger_list.GetFocusedItem()
        self.trigger_list.Select(trigger_focus, on=0)

    def trigger_got_focus(self, e):
        sensor_focus = self.sensor_list.GetFocusedItem()
        self.sensor_list.Select(sensor_focus, on=0)

    def del_item(self, e):
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
                mbox = wx.MessageDialog(None, "Delete selected item?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
                sure = mbox.ShowModal()
                if sure == wx.ID_YES:
                    if self.sensor_list.GetSelectedItemCount() == 1:
                        name = MainApp.sensors_info_pannel.sensor_list.GetItem(self.sensor_list.GetFocusedItem(), 0).GetText()
                        #
                        # Delete cron job
                        last_index = cron_list_pnl.repeat_cron.GetItemCount()
                        if not last_index == 0:
                            for index in range(0, last_index):
                                job_name  = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                                job_extra = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                                if "log_sensor_module.py" in job_name:
                                    if "name=" + name in job_extra:
                                        cron_list_pnl.repeat_cron.DeleteItem(index)
                                        MainApp.cron_info_pannel.update_cron_click("e")
                        #
                        print(self.sensor_list.DeleteItem(self.sensor_list.GetFocusedItem()))
                        if "sensor_" + name + "_type" in MainApp.config_ctrl_pannel.config_dict:
                            del MainApp.config_ctrl_pannel.config_dict["sensor_" + name + "_type"]
                        if "sensor_" + name + "_log" in MainApp.config_ctrl_pannel.config_dict:
                            del MainApp.config_ctrl_pannel.config_dict["sensor_" + name + "_log"]
                        if "sensor_" + name + "_loc" in MainApp.config_ctrl_pannel.config_dict:
                            del MainApp.config_ctrl_pannel.config_dict["sensor_" + name + "_loc"]
                        if "sensor_" + name + "_extra" in MainApp.config_ctrl_pannel.config_dict:
                            del MainApp.config_ctrl_pannel.config_dict["sensor_" + name + "_extra"]
                        MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
                    if self.trigger_list.GetSelectedItemCount() == 1:
                        print(self.trigger_list.DeleteItem(self.trigger_list.GetFocusedItem()))
                        MainApp.sensors_info_pannel.trigger_list.save_table_to_pi()
                    # remove from config dict


    def check_trigger_script_activity(self):
        # Check Cron
        script_has_cronjob, script_enabled, script_startupcron_index = install_dialog.check_for_control_script("", scriptname='trigger_watcher.py')
        if script_has_cronjob and script_enabled:
            self.trigger_script_activity_cron.SetForegroundColour((80,150,80))
            self.trigger_script_activity_cron.SetLabel("trigger_watcher.py starting on boot")
        elif script_has_cronjob and not script_enabled:
            self.trigger_script_activity_cron.SetForegroundColour((200,110,110))
            self.trigger_script_activity_cron.SetLabel("trigger_watcher.py cronjob disabled, won't start on boot")
        elif not script_has_cronjob:
            self.trigger_script_activity_cron.SetForegroundColour((200,75,75))
            self.trigger_script_activity_cron.SetLabel("No trigger_watcher.py in startup cron, this is required.")
        # Check running
        cmd = "pidof /home/" + pi_link_pnl.target_user + "/Pigrow/scripts/autorun/trigger_watcher.py -x"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        if len(out) > 0:
            self.trigger_script_activity_live.SetLabel(" trigger_watcher.py currently running ")
            self.trigger_script_activity_live.SetForegroundColour((80,150,80))
        else:
            self.trigger_script_activity_live.SetLabel(" trigger_watcher.py NOT currently running ")
            self.trigger_script_activity_live.SetForegroundColour((200,75,75))
        MainApp.window_self.Layout()

    class sensor_table(wx.ListCtrl):
        def __init__(self, parent, id):
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Sensor')
            self.InsertColumn(1, 'Type')
            self.InsertColumn(2, 'Log')
            self.InsertColumn(3, 'Location')
            self.InsertColumn(4, 'Extra')
            self.InsertColumn(5, 'log freq')
            self.SetColumnWidth(0, 125)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 300)
            self.SetColumnWidth(3, 100)
            self.SetColumnWidth(4, 175)
            self.SetColumnWidth(5, 100)

        def read_sensor_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            # Type
            if prefix + item_name + "_type" in config_dict:
                type  = config_dict[prefix + item_name + "_type"]
            else:
                type = ""
            # log location
            if prefix + item_name + "_log" in config_dict:
                log   = config_dict[prefix + item_name + "_log"]
            else:
                log = ""
            # sensor location (connection type and pin / address)
            if prefix + item_name + "_loc" in config_dict:
                loc   = config_dict[prefix + item_name + "_loc"]
            else:
                loc = ""
            # extra settings string (possibly obsolete)
            if prefix + item_name + "_extra" in config_dict:
                extra = config_dict[prefix + item_name + "_extra"]
            else:
                extra = ""
            return type, log, loc, extra

        def make_sensor_table(self, e=""):
            sensor_name_list = []
            button_name_list = []
            print("  - Using config_dict to fill sensor table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(MainApp.config_ctrl_pannel.config_dict.items()):
                if "_type" in key:
                    if "sensor_" in key:
                        sensor_name_list.append(key.split("_")[1])
                    if "button_" in key:
                        button_name_list.append(key.split("_")[1])
            # add buttons to table
            for button_name in button_name_list:
                type, log, loc, extra = self.read_sensor_conf(button_name, MainApp.config_ctrl_pannel.config_dict, "button_")
                self.add_to_sensor_list(button_name, type, log, loc, extra, "button")
            # add sensors to table
            for sensor_name in sensor_name_list:
                type, log, loc, extra = self.read_sensor_conf(sensor_name, MainApp.config_ctrl_pannel.config_dict, "sensor_")
                #
                # check cron to see if sensor is being logged and how often
                #
                last_index = cron_list_pnl.repeat_cron.GetItemCount()
                log_freq = "not found"
                if not last_index == 0:
                    for index in range(0, last_index):
                        job_name  = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                        job_extra = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                        extra_name  = "name=" + str(sensor_name)
                        if "log_chirp.py" in job_name:
                            if loc[4:] in job_extra:
                                log_freq = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
                                freq_num, freq_text = cron_list_pnl.repeating_cron_list.parse_cron_string(self, log_freq)
                                log_freq = str(freq_num) + " " + freq_text
                        if "log_dstemp.py" in job_name:
                            if loc in job_extra:
                                log_freq = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
                                freq_num, freq_text = cron_list_pnl.repeating_cron_list.parse_cron_string(self, log_freq)
                                log_freq = str(freq_num) + " " + freq_text
                        if "log_ads1115.py" in job_name:
                            if loc[0:3] in job_extra:
                                log_freq = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
                                freq_num, freq_text = cron_list_pnl.repeating_cron_list.parse_cron_string(self, log_freq)
                                log_freq = str(freq_num) + " " + freq_text
                        # modular sensors
                        if "log_sensor_module.py" in job_name:
                            if "name=" + sensor_name in job_extra:
                                log_freq = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
                                freq_num, freq_text = cron_list_pnl.repeating_cron_list.parse_cron_string(self, log_freq)
                                log_freq = str(freq_num) + " " + freq_text

                # get settings for buttons
                #
                self.add_to_sensor_list(sensor_name, type, log, loc, extra, log_freq)

        def add_to_sensor_list(self, sensor, type, log, loc, extra='', log_freq=''):
            #MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(sensor,type,log,loc,extra)
            self.InsertItem(0, str(sensor))
            self.SetItem(0, 1, str(type))
            self.SetItem(0, 2, str(log))
            self.SetItem(0, 3, str(loc))
            self.SetItem(0, 4, str(extra))
            self.SetItem(0, 5, str(log_freq))

        def double_click(e):
            index =  e.GetIndex()
            #get info for dialogue box
            name = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 0).GetText()
            type = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 1).GetText()
            log = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 2).GetText()
            loc = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 3).GetText()
            extra = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 4).GetText()
            timing_string = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 5).GetText()
            #print(" Selected item - " + name + " - " + type + " - " + loc + " - " + extra + " - " + timing_string)
            MainApp.sensors_info_pannel.sensor_list.s_name = name
            MainApp.sensors_info_pannel.sensor_list.s_type = type
            MainApp.sensors_info_pannel.sensor_list.s_log = log
            MainApp.sensors_info_pannel.sensor_list.s_loc = loc
            MainApp.sensors_info_pannel.sensor_list.s_extra = extra
            MainApp.sensors_info_pannel.sensor_list.s_timing = timing_string
            if timing_string == "button":
                add_button = add_button_dialog(None)
                add_button.ShowModal()
            else:
                # old style sensors
                if type == 'chirp':
                    edit_chirp_dbox = chirp_dialog(None)
                    edit_chirp_dbox.ShowModal()
                elif type == "DS18B20":
                    ds18b20_dialog_box = ds18b20_dialog(None)
                    ds18b20_dialog_box.ShowModal()
                elif type == "ADS1115":
                    ads1115_dialog_box = ads1115_dialog(None)
                    ads1115_dialog_box.ShowModal()
                # modular sensors
                else:
                    modular_sensor_dialog_box = add_sensor_from_module_dialog(None)
                    modular_sensor_dialog_box.ShowModal()

    class trigger_table(wx.ListCtrl):
        def __init__(self, parent, id):
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT|wx.LC_VRULES)
            self.InsertColumn(0, 'Log')
            self.InsertColumn(1, 'Value Label')
            self.InsertColumn(2, 'Type')
            self.InsertColumn(3, 'Value')
            self.InsertColumn(4, 'Condition Name')
            self.InsertColumn(5, 'Set')
            self.InsertColumn(6, 'lock (min)')
            self.InsertColumn(7, 'Shell Command')
            self.SetColumnWidth(0, 125)
            self.SetColumnWidth(1, 125)
            self.SetColumnWidth(2, 85)
            self.SetColumnWidth(3, 90)
            self.SetColumnWidth(4, 140)
            self.SetColumnWidth(5, 100)
            self.SetColumnWidth(6, 120)
            self.SetColumnWidth(7, 500)

        def make_trigger_table(self):
            self.DeleteAllItems()
            print("  - Filling Trigger Table - ")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /home/" + pi_link_pnl.target_user + "/Pigrow/config/trigger_events.txt")
            for line in out.splitlines():
                first_comma = line.find(",")
                second_comma  = first_comma + 1 + line[first_comma+1:].find(",")
                third_comma   = second_comma + 1 + line[second_comma+1:].find(",")
                fourth_comma  = third_comma + 1 + line[third_comma+1:].find(",")
                fifth_comma   = fourth_comma + 1 + line[fourth_comma+1:].find(",")
                sixth_comma   = fifth_comma + 1 + line[fifth_comma+1:].find(",")
                seventh_comma = sixth_comma + 1 + line[sixth_comma+1:].find(",")
                eighth_comma = seventh_comma + 1 + line[seventh_comma+1:].find(",")
                # find values between commas
                log_name        = line[:first_comma].strip()
                value_label     = line[first_comma  +1 :second_comma].strip()
                trigger_type    = line[second_comma +1 :third_comma].strip()
                trigger_value   = line[third_comma  +1 :fourth_comma].strip()
                condition_name  = line[fourth_comma +1 :fifth_comma].strip()
                trig_direction  = line[fifth_comma  +1 :sixth_comma].strip()
                trig_cooldown   = line[sixth_comma  +1 :seventh_comma].strip()
                cmd            = line[seventh_comma+1:].strip()
                self.add_to_trigger_list(log_name, value_label, trigger_type, trigger_value, condition_name, trig_direction, trig_cooldown, cmd)

        def add_to_trigger_list(self, log, label, type, value, name, set, cooldown, cmd):
            #MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(sensor,type,log,loc,extra)
            self.InsertItem(0, str(log))
            self.SetItem(0, 1, str(label))
            self.SetItem(0, 2, str(type))
            self.SetItem(0, 3, str(value))
            self.SetItem(0, 4, str(name))
            self.SetItem(0, 5, str(set))
            self.SetItem(0, 6, str(cooldown))
            self.SetItem(0, 7, str(cmd))

        def update_table_line(self, index, log, label, type, value, name, set, cooldown, cmd):
            self.SetItem(index, 0, str(log))
            self.SetItem(index, 1, str(label))
            self.SetItem(index, 2, str(type))
            self.SetItem(index, 3, str(value))
            self.SetItem(index, 4, str(name))
            self.SetItem(index, 5, str(set))
            self.SetItem(index, 6, str(cooldown))
            self.SetItem(index, 7, str(cmd))

        def save_table_to_pi(self):
            trigger_file_text = ""

            for index in range(0, MainApp.sensors_info_pannel.trigger_list.GetItemCount()):
                log      = self.GetItem(index,0).GetText()
                label    = self.GetItem(index,1).GetText()
                type     = self.GetItem(index,2).GetText()
                value    = self.GetItem(index,3).GetText()
                name     = self.GetItem(index,4).GetText()
                set      = self.GetItem(index,5).GetText()
                cooldown = self.GetItem(index,6).GetText()
                cmd      = self.GetItem(index,7).GetText()
                trigger_file_text += log + "," + label + "," + type + "," + value + "," + name + "," + set + "," + cooldown + "," + cmd + "\n"
            if len(trigger_file_text) > 1:
                if trigger_file_text[0:-2] == "\n":
                    trigger_file_text = trigger_file_text[0:-2]
            # Write Temporary file
            temp_trigger_file_location = temp_local = os.path.join(localfiles_info_pnl.local_path, "temp/")
            if not os.path.isdir(temp_trigger_file_location):
                os.makedirs(temp_trigger_file_location)
            temp_trigger_file_location = temp_local = os.path.join(temp_trigger_file_location, "trigger_events.txt")
            with open(temp_trigger_file_location, "w") as f:
                f.write(trigger_file_text)
            # copy tempory file onto pigrow over existing trigger file
            pi_trigger_events_file = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/trigger_events.txt"
            MainApp.localfiles_ctrl_pannel.upload_file_to_folder(temp_trigger_file_location, pi_trigger_events_file)



        def double_click(e):
            index =  e.GetIndex()
            MainApp.sensors_info_pannel.trigger_list.initial_log = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 0).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_val_label = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 1).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_type = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 2).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_value = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 3).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_cond_name = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 4).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_set = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 5).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_lock = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 6).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_cmd = MainApp.sensors_info_pannel.trigger_list.GetItem(index, 7).GetText()
            MainApp.sensors_info_pannel.trigger_list.initial_index = index
            trigger_edit_box = set_trigger_dialog(None)
            trigger_edit_box.ShowModal()


class sensors_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
        #
        # Soil Moisture Controlls
        # Refresh page button
        self.make_table_btn = wx.Button(self, label='make table')
        self.make_table_btn.Bind(wx.EVT_BUTTON, self.make_tables_click)
        #    --  Chirp options
        self.chirp_l = wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
        self.config_chirp_btn = wx.Button(self, label='add new chirp')
        self.config_chirp_btn.Bind(wx.EVT_BUTTON, self.add_new_chirp_click)
        self.address_chirp_btn = wx.Button(self, label='change chirp address')
        self.address_chirp_btn.Bind(wx.EVT_BUTTON, self.address_chirp_click)
        #   -- DS18B20 waterproof temp sensor
        self.ds18b20_l = wx.StaticText(self,  label='DS18B20 Temp Sensor;')
        self.add_ds18b20 = wx.Button(self, label='add new DS18B20')
        self.add_ds18b20.Bind(wx.EVT_BUTTON, self.add_ds18b20_click)
        #   == ADS1115 Analog to Digital converter i2c_check
        self.ads1115_l = wx.StaticText(self,  label='ADS1115 ADC;')
        self.add_ads1115 = wx.Button(self, label='add new ADS1115')
        self.add_ads1115.Bind(wx.EVT_BUTTON, self.add_ads1115_click)
        #  == Modular Sensor Controlls
        self.modular_sensor_l = wx.StaticText(self,  label='Modular Sensors;')
        self.sensor_module_list_cb = wx.ComboBox(self,  size=(150, 30), choices = get_module_options("sensor_", "sensor_modules"))
        self.add_modular_sensor = wx.Button(self, label='Add')
        self.add_modular_sensor.Bind(wx.EVT_BUTTON, self.add_modular_sensor_click)
        #  == Button Controlls
        self.buttons_l = wx.StaticText(self,  label='Buttons;')
        self.add_button = wx.Button(self, label='Add')
        self.add_button.Bind(wx.EVT_BUTTON, self.add_button_click)
        #  == Add Trigger
        self.triggers_l = wx.StaticText(self,  label='Triggers;')
        self.add_trigger = wx.Button(self, label='Add')
        self.add_trigger.Bind(wx.EVT_BUTTON, self.add_trigger_click)

        # Sizers

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.make_table_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.chirp_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.config_chirp_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.address_chirp_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.ds18b20_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_ds18b20, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.ads1115_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_ads1115, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.modular_sensor_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.sensor_module_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_modular_sensor, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttons_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_button, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.triggers_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_trigger, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def make_tables_click(self, e):
        MainApp.sensors_info_pannel.sensor_list.make_sensor_table()
        MainApp.sensors_info_pannel.trigger_list.make_trigger_table()
        MainApp.sensors_info_pannel.check_trigger_script_activity()

    def add_modular_sensor_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        # set blanks for dialog box
        module_name = MainApp.sensors_ctrl_pannel.sensor_module_list_cb.GetValue()
        MainApp.sensors_info_pannel.sensor_list.s_type = module_name
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"] +  module_name + "_log.txt"
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        # call dialog box
        add_module_sensor = add_sensor_from_module_dialog(None)
        add_module_sensor.ShowModal()

    def add_button_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        # set blanks for dialog box
        module_name = MainApp.sensors_ctrl_pannel.sensor_module_list_cb.GetValue()
        MainApp.sensors_info_pannel.sensor_list.s_type = ""
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"] + "button_log.txt"
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        # call dialog box
        add_button = add_button_dialog(None)
        add_button.ShowModal()


    def add_ads1115_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        # set blanks for dialog box
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"] + "ads1115_log.txt"
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        # call dialog box
        add_ads1115 = ads1115_dialog(None)
        add_ads1115.ShowModal()

    def add_ds18b20_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        # set blanks for dialog box
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"] + "dstemp_log.txt"
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        # call dialog box
        add_ds18b20 = ds18b20_dialog(None)
        add_ds18b20.ShowModal()

    def add_new_chirp_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        print("adding a new chirp sensor")
        # set black variables
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"]
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ":"
        MainApp.sensors_info_pannel.sensor_list.s_extra = "min: max:"
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        # call the chirp config dialog box
        add_chirp_dbox = chirp_dialog(None, title='Chirp Sensor Config')
        add_chirp_dbox.ShowModal()

    def address_chirp_click(self, e):
        # Ask user to select the chirp they want to readdress
        msg_text =  "This will change the address of your Chirp on the i2c bus, \n"
        msg_text += "please input the current address of the sensor you wish you change. \n"
        msg_text += "You must use the format 0x** - e.g. 0x20, 0x21, etc. \n\n"
        msg_text += "If your sensor is plugged in correctly but doesn't show on the i2c bus \n"
        msg_text += "it's likely to be at 0x01 or possibly 0x00 or 0x02. \n"
        current_add_dbox = wx.TextEntryDialog(self, msg_text, 'Change i2c address', "")
        if current_add_dbox.ShowModal() == wx.ID_OK:
            current_chirp_add = current_add_dbox.GetValue()
        else:
            return "cancelled"
        current_add_dbox.Destroy()
        # ask which address the user wants to change it to
        msg_text = "Input new address to set chirp sensor to\n"
        msg_text += "You must use the format 0x20, 0x21, etc."
        new_add_dbox = wx.TextEntryDialog(self, msg_text, 'Change i2c address', "")
        if new_add_dbox.ShowModal() == wx.ID_OK:
            new_chirp_add = new_add_dbox.GetValue()
        else:
            return "cancelled"
        new_add_dbox.Destroy()
        path = MainApp.config_ctrl_pannel.dirlocs_dict["path"]
        cmd = os.path.join(path, "scripts/sensors/chirp_i2c_address.py")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd + " current=" + current_chirp_add + " new=" + new_chirp_add)
        # tell the uesr what happened
        msg_text = "Script output; " + str(out) + " " + str(error)
        dbox = show_script_cat(None, msg_text, "chirp_i2c_address.py output")
        dbox.ShowModal()
        dbox.Destroy()

    def sensor_combo_go(self, e):
        # hide all controls
        self.soil_sensor_cb.Hide()
        # show selected controls
        if self.sensor_cb.GetValue() == "Soil Moisture":
            self.soil_sensor_cb.Hide()

    def add_trigger_click(self, e):
        MainApp.sensors_ctrl_pannel.make_tables_click("e")
        MainApp.sensors_info_pannel.trigger_list.initial_log = ""
        MainApp.sensors_info_pannel.trigger_list.initial_val_label = ""
        MainApp.sensors_info_pannel.trigger_list.initial_type = ""
        MainApp.sensors_info_pannel.trigger_list.initial_value = ""
        MainApp.sensors_info_pannel.trigger_list.initial_cond_name = ""
        MainApp.sensors_info_pannel.trigger_list.initial_set = ""
        MainApp.sensors_info_pannel.trigger_list.initial_lock = ""
        MainApp.sensors_info_pannel.trigger_list.initial_cmd = ""
        MainApp.sensors_info_pannel.trigger_list.initial_index = -1
        trigger_edit_box = set_trigger_dialog(None)
        trigger_edit_box.ShowModal()

class add_sensor_from_module_dialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(add_sensor_from_module_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Sensor Setup from Module")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = MainApp.sensors_info_pannel.sensor_list.s_name
        self.s_type  = MainApp.sensors_info_pannel.sensor_list.s_type
        self.s_log   = MainApp.sensors_info_pannel.sensor_list.s_log
        self.s_loc   = MainApp.sensors_info_pannel.sensor_list.s_loc
        self.s_extra = MainApp.sensors_info_pannel.sensor_list.s_extra
        self.timing_string = MainApp.sensors_info_pannel.sensor_list.s_timing
        try:
            s_rep     = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[0]
            s_rep_txt = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[1]
        except:
            s_rep = ""
            s_rep_txt = ""
        self.import_sensor_module()
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Sensor module: ' + self.s_type)
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        self.show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        self.show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        # buttons_
        self.add_btn = wx.Button(self, label='OK', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # hardware information
        name_l = wx.StaticText(self,  label='Unique Name')
        self.name_tc = wx.TextCtrl(self, size=(400,30))
        log_l = wx.StaticText(self,  label='Log Location')
        self.log_tc = wx.TextCtrl(self, size=(400,30))
        self.graph_btn = wx.Button(self, label='Graph', size=(175, 30))
        # self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_click)
        sensor_l = wx.StaticText(self,  label='Sensor Location')

        # loaded settungs
        self.sensor_connection = wx.StaticText(self,  label="")
        self.loc_cb = wx.ComboBox(self, choices = [], size=(170, 25))
        # Read sensor button
        self.read_sensor_btn = wx.Button(self, label='Read Sensor')
        self.read_sensor_btn.Bind(wx.EVT_BUTTON, self.read_sensor_click)
        self.read_output_l = wx.StaticText(self,  label='')
        # timing string
        timeing_l = wx.StaticText(self,  label='Repeating every ')
        self.rep_num_tc = wx.TextCtrl(self, size=(70,30))
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, size=(100, 30))

        # Information request
        self.request_info_l = wx.StaticText(self,  label='Request Information')
        self.request_info_cb = wx.ComboBox(self, choices = [''], size=(200, 30))
        self.request_info_btn = wx.Button(self, label='Send')
        self.request_info_btn.Bind(wx.EVT_BUTTON, self.request_info_click)
        self.request_output_l = wx.StaticText(self,  label='-')
        # Change Setting
        self.change_setting_l = wx.StaticText(self,  label='Change Settings')
        self.change_setting_cb = wx.ComboBox(self, choices=[''], size=(200, 30))
        self.change_setting_tc = wx.TextCtrl(self, size=(70,30))
        self.change_setting_btn = wx.Button(self, label='Set')
        self.change_setting_btn.Bind(wx.EVT_BUTTON, self.change_setting_click)
        self.change_setting_out_l = wx.StaticText(self,  label='-')



        self.read_mod_settings()
        # Sizers
        top_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_line_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 3)
        top_line_sizer.AddStretchSpacer(1)
        top_line_sizer.Add(self.show_guide_btn, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(self.sensor_connection, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.loc_cb, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.read_sensor_btn, 0, wx.ALL, 3)
        loc_sizer.Add(self.read_output_l, 0, wx.ALL, 3)
        timing_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_sizer.Add(self.rep_num_tc, 0, wx.ALL, 3)
        timing_sizer.Add(self.rep_opts_cb, 0, wx.ALL, 3)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_tc, 2, wx.ALL, 3)
        log_sizer.Add(self.graph_btn, 0, wx.ALL, 3)
        options_sizer = wx.FlexGridSizer(4, 2, 1, 4)
        options_sizer.AddMany([ (name_l, 0, wx.EXPAND),
            (self.name_tc, 0, wx.EXPAND),
            (log_l, 0, wx.EXPAND),
            (log_sizer, 0, wx.EXPAND),
            (sensor_l, 0, wx.EXPAND),
            (loc_sizer, 0, wx.EXPAND),
            (timeing_l, 0, wx.EXPAND),
            (timing_sizer, 0, wx.EXPAND) ])
        request_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        request_info_sizer.Add(self.request_info_l, 0,  wx.ALL, 3)
        request_info_sizer.Add(self.request_info_cb, 0,  wx.ALL, 3)
        request_info_sizer.Add(self.request_info_btn, 0,  wx.ALL, 3)
        change_setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
        change_setting_sizer.Add(self.change_setting_l, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_cb, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_tc, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_btn, 0,  wx.ALL, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_line_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(request_info_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.request_output_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(change_setting_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.change_setting_out_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        # set values for when reading from double click
        self.name_tc.SetValue(self.s_name)
        self.log_tc.SetValue(self.s_log)
        if not self.s_loc == "":
            self.loc_cb.SetValue(self.s_loc)
        self.rep_num_tc.SetValue(s_rep)
        self.rep_opts_cb.SetValue(s_rep_txt)

    def show_guide_click(self, e):
        guide_path = "guide_" + self.s_type + ".png"
        guide_path = os.path.join(shared_data.sensor_modules_path, guide_path)
        guide = wx.Image(guide_path, wx.BITMAP_TYPE_ANY)
        guide = guide.ConvertToBitmap()
        if os.path.isfile(guide_path):
            dbox = show_image_dialog(None, guide, self.s_type)
            dbox.ShowModal()
            dbox.Destroy()
        else:
            print(" - Sensor does not have an associated guide")
            print("     " + guide_path + " not found")

    def change_setting_click(self, e):
        sensor_name = self.name_tc.GetValue()
        setting_to_change = self.change_setting_cb.GetValue()
        sensor_location = self.loc_cb.GetValue()
        setting_value = self.change_setting_tc.GetValue()
        if not setting_to_change == "":
            module_name = self.s_type
            sensor_module_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/sensor_" + module_name + ".py"
            check_message = "Are you sure you want to change " + setting_to_change + " to " + setting_value + "?"
            dbox = wx.MessageDialog(self, check_message, "Change Setting?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(sensor_module_path + " location=" + sensor_location + " set=" + setting_to_change + "=" + setting_value + " name=" + sensor_name)
                out = out.strip()
                self.change_setting_out_l.SetLabel(setting_to_change + ": " + out + error)
                print(setting_to_change + ": " + out + error)
                self.Layout()

    def request_info_click(self, e):
        sensor_name = self.name_tc.GetValue()
        item_to_request = self.request_info_cb.GetValue()
        sensor_location = self.loc_cb.GetValue()
        if not item_to_request == "":
            module_name = self.s_type
            sensor_module_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/sensor_" + module_name + ".py"
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(sensor_module_path + " location=" + sensor_location + " request=" + item_to_request + " name=" + sensor_name)
            out = out.strip()
            self.request_output_l.SetLabel(item_to_request + ": " + out + error)
            print(item_to_request + ": " + out + error)
            self.Layout()

    def read_mod_settings(self):
        print(" -- READING MODULE SETTINGS -- ")
        module_name = self.s_type
        sensor_module_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/sensor_" + module_name + ".py"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(sensor_module_path + " -config")
        print(out, error)
        print(" -------------------------------------- ")
        def_address = ""
        only_option = False
        for line in out.strip().splitlines():
            if "=" in line:
                setting = line.split("=")[0]
                value = line.split("=")[1]
                if setting == "connection_type":
                    print(" currently no box for connection type ")
                    # write to connection type box which doesn't yet exist
                elif setting == "connection_address_list":
                    self.loc_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            #---- add function here to remove sensors already added
                            self.loc_cb.Append(item)
                    else:
                        self.loc_cb.Append(value)
                        self.loc_cb.SetValue(value)
                        only_option = True
                elif setting == "default_connection_address":
                    def_address = value
                elif setting == "available_info":
                    self.request_info_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            self.request_info_cb.Append(item)
                    else:
                        self.request_info_cb.Append(value)
                        self.request_info_cb.SetValue(value)
                # settings options
                elif setting == "available_settings":
                    self.change_setting_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            self.change_setting_cb.Append(item)
                    else:
                        self.change_setting_cb.Append(value)
                        self.change_setting_cb.SetValue(value)

        if not only_option == True:
            self.loc_cb.SetValue(def_address)

    def import_sensor_module(self):
        module_name = self.s_type
        print(" Importing module; " + module_name)
        module_name = "sensor_" + module_name
        if module_name in sys.modules:
            del sys.modules[module_name]
        exec('import ' + module_name + ' as sensor_module', globals())

    def read_sensor_click(self, e):
        module_name = self.s_type
        sensor_name = self.name_tc.GetValue()
        print(" - attenmpting to read sensor using module -" + module_name)
        module_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/sensor_" + module_name + ".py location=" + self.loc_cb.GetValue() + " name=" + sensor_name
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(module_path)
        self.read_output_l.SetLabel(out)
        print(out, error)

    def edit_cron_job(self, start_name, new_name, new_cron_txt, new_cron_num):
    # check to find cron job handling this sensor
        #print(" - Checking cron for existing jobs")
        line_number_repeting_cron = -1
        if not start_name == "":
            for index in range(0, cron_list_pnl.repeat_cron.GetItemCount()):
                cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                if "log_sensor_module.py" in cmd_path:
                    #print("    -Found  ;- " + cmd_path)
                    cmd_args = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                    if  "name=" + start_name in cmd_args:
                        #print("    -Located; " + start_name)
                        line_number_repeting_cron = index

        # check to see if this is a new job or not
        if not line_number_repeting_cron == -1:
            cron_enabled = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 1).GetText()
            cron_task    = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 3).GetText()
            # cron_args_original = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 4).GetText()
            cron_args    = "name=" + new_name
            cron_comment = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 5).GetText()
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, new_cron_txt, new_cron_num)
            print("    - Cron job; " + str(line_number_repeting_cron) + " modified " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            cron_list_pnl.repeat_cron.DeleteItem(line_number_repeting_cron)
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'modified', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")
        else:
            #print("    - Job not currently in cron, adding it...")
            cron_enabled = "True"
            cron_task = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/log_sensor_module.py"
            cron_args = "name=" + new_name
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, new_cron_txt, new_cron_num)
            cron_comment = ""
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            print("    - New Cron job; " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")

    def add_click(self, e):
        o_name = self.name_tc.GetValue()
        o_log = self.log_tc.GetValue()
        o_loc = self.loc_cb.GetValue()
        new_cron_num = self.rep_num_tc.GetValue()
        new_cron_txt = self.rep_opts_cb.GetValue()
        new_timing_string = str(new_cron_num) + " " + new_cron_txt
        # check to see if changes have been made
        changed = "probably something"
        if self.s_name == o_name:
            #print("name not changed")
            if self.s_log == o_log:
                #print("log path not changed")
                if self.s_loc == o_loc:
                    #print("wiring location not changed")
                        changed = "nothing"
                        #nothing has changed in the config file so no need to update.
        # check to see if changes have been made to the cron timing
        if self.timing_string == new_timing_string and self.s_name == o_name:
            print(" -- Timing string didn't change, nor did the name so no need to chagne cron-- ")
        else:
            self.edit_cron_job(self.s_name, o_name, new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            log_freq = str(new_cron_num) + " " + new_cron_txt
            extra_string = "cat /home/" + pi_link_pnl.target_user + "/Pigrow/config/pigrow_config.txt |grep sensor_" + self.s_name + "_extra"
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(extra_string)
            o_extra = out.strip().strip("sensor_" + self.s_name + "_extra=")
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,self.s_type,o_log,o_loc,o_extra,log_freq)
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = self.s_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            #MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e', ask="no")
        self.Destroy()

    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()

class add_button_dialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(add_button_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Button Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = MainApp.sensors_info_pannel.sensor_list.s_name
        self.s_type  = MainApp.sensors_info_pannel.sensor_list.s_type
        self.s_log   = MainApp.sensors_info_pannel.sensor_list.s_log
        self.s_loc   = MainApp.sensors_info_pannel.sensor_list.s_loc
        self.s_extra = MainApp.sensors_info_pannel.sensor_list.s_extra
        self.timing_string = MainApp.sensors_info_pannel.sensor_list.s_timing
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='THIS IS A TEST FEATURE - FULL VERSION COMING SOON\nButton type: ' + self.s_type)
        box_label.SetFont(shared_data.title_font)
        # buttons_
        self.add_btn = wx.Button(self, label='OK', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # hardware information
        name_l = wx.StaticText(self,  label='Unique Name')
        self.name_tc = wx.TextCtrl(self, size=(400,30))
        log_l = wx.StaticText(self,  label='Log Location')
        self.log_tc = wx.TextCtrl(self, size=(400,30))
        self.graph_btn = wx.Button(self, label='Graph', size=(175, 30))
        # self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_click)
        gpio_l = wx.StaticText(self,  label='GPIO pin')

             #---- add function here to remove sensors already added
        self.sensor_connection = wx.StaticText(self,  label="")
        self.loc_cb = wx.ComboBox(self, choices = ["-"], size=(170, 25))

        # timing string
        self.jobexist_l = wx.StaticText(self,  label='Start on Reboot')
        self.running_l = wx.StaticText(self,  label='Running Now')


        # Sizers
        loc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(self.sensor_connection, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.loc_cb, 0, wx.ALL|wx.EXPAND, 3)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_tc, 2, wx.ALL, 3)
        log_sizer.Add(self.graph_btn, 0, wx.ALL, 3)
        options_sizer = wx.FlexGridSizer(3, 2, 1, 4)
        options_sizer.AddMany([ (name_l, 0, wx.EXPAND),
            (self.name_tc, 0, wx.EXPAND),
            (log_l, 0, wx.EXPAND),
            (log_sizer, 0, wx.EXPAND),
            (gpio_l, 0, wx.EXPAND),
            (loc_sizer, 0, wx.EXPAND) ])
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.jobexist_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.running_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        # set values for when reading from double click
        self.name_tc.SetValue(self.s_name)
        self.colour_job_exists(self.s_name)
        self.colour_if_script_running(self.s_name)
        self.log_tc.SetValue(self.s_log)
        if not self.s_loc == "":
            self.loc_cb.SetValue(self.s_loc)


    def make_extra_settings_string(self):
        print(" -Extra settings string not yet implemented, coming sooon")
        return ""

    def find_cron_job(self, cmd, name):
        print(" - Checking cron for existing jobs")
        line_number_start_cron = -1
        for index in range(0, cron_list_pnl.startup_cron.GetItemCount()):
            cmd_path = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
            if cmd in cmd_path:
                print("    -Found  ;- " + cmd_path)
                cmd_args = cron_list_pnl.startup_cron.GetItem(index, 4).GetText()
                if  "name=" + name in cmd_args.lower():
                    print("    -Located; " + name)
                    line_number_start_cron = index
        return line_number_start_cron

    def colour_job_exists(self, name):
        line_number_start_cron = self.find_cron_job("watcher_button.py", name)
        # check to see if this is a new job or not
        if not line_number_start_cron == -1:
            cron_enabled = cron_list_pnl.startup_cron.GetItem(line_number_start_cron, 1).GetText()
            if "True" in cron_enabled:
                self.jobexist_l.SetForegroundColour((75,200,75))
            else:
                self.jobexist_l.SetForegroundColour((175,175,75))
        else:
            self.jobexist_l.SetForegroundColour((200,75,75))
        #return line_number_start_cron

    def colour_if_script_running(self, name):
        script = "watcher_button.py"
        pgrep_text, error = MainApp.localfiles_ctrl_pannel.run_on_pi("pgrep -af  " + str(script))
        pgrep_split = pgrep_text.strip().splitlines()
        found_running = 0
        for line in pgrep_split:
            if "name=" + name in line:
                found_running = found_running + 1
        #
        if found_running == 0:
            print(" - didn't find a running verson of " + script + "name=" + name)
            self.running_l.SetForegroundColour((200,75,75))
        elif found_running == 1:
            print(" - " + script + " name=" + name + " running" )
            self.running_l.SetForegroundColour((75,200,75))
        elif found_running > 1:
            print(" - Too many versions of " + script + " running, should kill all and restart")
            self.running_l.SetForegroundColour((75,75,200))




    def edit_cron_job(self, start_name, new_name):
        print(" - This does not yet check or write the cron job, comin soon - make sure it starts on boot by looking in the cron tab of the gui")
        # check to find cron job handling this sensor
        line_number_start_cron = self.find_cron_job("watcher_button.py", start_name)

        # check to see if this is a new job or not
        if not line_number_start_cron == -1:
            cron_enabled = cron_list_pnl.startup_cron.GetItem(line_number_start_cron, 1).GetText()
            cron_task    = cron_list_pnl.startup_cron.GetItem(line_number_start_cron, 3).GetText()
            # cron_args_original = cron_list_pnl.repeat_cron.GetItem(line_number_start_cron, 4).GetText()
            cron_args    = "name=" + new_name
            cron_comment = cron_list_pnl.startup_cron.GetItem(line_number_start_cron, 5).GetText()
            print("    - Cron job; " + str(line_number_start_cron) + " modified " + cron_enabled + " " + cron_task + " " + cron_args + " " + cron_comment)
            cron_list_pnl.startup_cron.DeleteItem(line_number_start_cron)
            cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'modified', "True", cron_task, cron_args, "")
            MainApp.cron_info_pannel.update_cron_click("e")
        else:
            print("    - Job not currently in cron, adding it...")
            cron_enabled = "True"
            cron_task = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/autorun/watcher_button.py"
            cron_args = "name=" + new_name
            cron_comment = ""
            cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', "True", cron_task, cron_args, "")
            print("    - New Cron job; " + cron_enabled + " "  + cron_task + " " + cron_args + " " + cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")

    def add_click(self, e):
        o_name = self.name_tc.GetValue()
        o_log = self.log_tc.GetValue()
        o_loc = self.loc_cb.GetValue()
        o_extra = self.make_extra_settings_string()
        # check to see if changes have been made
        changed = "probably something"
        if self.s_name == o_name:
            #print("name not changed")
            if self.s_log == o_log:
                #print("log path not changed")
                if self.s_loc == o_loc:
                    #print("wiring location not changed")
                    if self.s_extra == o_extra:
                        #print("extra field not changed")
                        changed = "nothing"
                        #nothing has changed in the config file so no need to update.

        # check to see if changes have been made to the cron timing
        self.edit_cron_job(self.s_name, o_name)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            log_freq = "button"
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,self.s_type,o_log,o_loc,o_extra,log_freq)
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = self.s_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
        self.Destroy()

    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()

class set_trigger_dialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(set_trigger_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Sensor Setup from Module")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        '''
        Before this is called these values must be set;
        MainApp.sensors_info_pannel.trigger_list.initial_log
        MainApp.sensors_info_pannel.trigger_list.initial_val_label
        MainApp.sensors_info_pannel.trigger_list.initial_type
        MainApp.sensors_info_pannel.trigger_list.initial_value
        MainApp.sensors_info_pannel.trigger_list.initial_cond_name
        MainApp.sensors_info_pannel.trigger_list.initial_set
        MainApp.sensors_info_pannel.trigger_list.initial_lock
        MainApp.sensors_info_pannel.trigger_list.initial_cmd
        MainApp.sensors_info_pannel.trigger_list.initial_index = -1 for new, index number of trigger table otherwise
        '''
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Log Triggers')
        box_label.SetFont(shared_data.title_font)
        box_sub_title =  wx.StaticText(self,  label='Trigger conditions are checked every time a log entry is written', size=(550,30))
        box_sub_title.SetFont(shared_data.sub_title_font)
        # buttons_
        self.ok_btn = wx.Button(self, label='OK', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # trigger information
        log_l = wx.StaticText(self,  label='Log')
        log_opts = self.get_log_options()
        self.log_cb = wx.ComboBox(self, choices = log_opts, value=MainApp.sensors_info_pannel.trigger_list.initial_log)
        self.log_cb.Bind(wx.EVT_COMBOBOX, self.set_label_opts)

        val_label_l = wx.StaticText(self,  label='Value Label')
        val_label_opts = self.get_value_label_ops()
        self.val_label_cb = wx.ComboBox(self, choices = val_label_opts, value=MainApp.sensors_info_pannel.trigger_list.initial_val_label)

        type_l = wx.StaticText(self,  label='Type')
        type_opts = ['above', 'below', 'window', 'frame', 'all']
        self.type_cb = wx.ComboBox(self, choices = type_opts, value=MainApp.sensors_info_pannel.trigger_list.initial_type)
        self.type_cb.Bind(wx.EVT_COMBOBOX, self.type_cb_select)

        value_l = wx.StaticText(self,  label='value')
        self.value_tc = wx.TextCtrl(self, value=MainApp.sensors_info_pannel.trigger_list.initial_value, size=(400,30))

        cond_name_l = wx.StaticText(self,  label='Condition Name')
        self.cond_name_tc = wx.TextCtrl(self, value=MainApp.sensors_info_pannel.trigger_list.initial_cond_name, size=(400,30))

        set_l = wx.StaticText(self,  label='Set to')
        set_opts = ['on', 'off', 'pause']
        self.set_cb = wx.ComboBox(self, choices = set_opts, value=MainApp.sensors_info_pannel.trigger_list.initial_set)

        lock_l = wx.StaticText(self,  label='Cooldown Lock')
        self.lock_tc = wx.TextCtrl(self, value=MainApp.sensors_info_pannel.trigger_list.initial_lock, size=(400,30))

        cmd_l = wx.StaticText(self,  label='Shell Command')
        self.cmd_tc = wx.TextCtrl(self, value=MainApp.sensors_info_pannel.trigger_list.initial_cmd, size=(500,30))


        # Read trigger conditions
        triggger_cond_l = wx.StaticText(self,  label='Current Trigger Condition;', size=(550,30))
        self.read_trig_cond_btn = wx.Button(self, label='Read Current Trigger Conditions')
        self.read_trig_cond_btn.Bind(wx.EVT_BUTTON, self.read_trigger_conditions_click)
        self.read_output_l = wx.StaticText(self,  label='')

        # Mirror
        if MainApp.sensors_info_pannel.trigger_list.initial_index == -1:
            mirror_label = "Create Mirror"
        else:
            mirror_label = "Change Mirror"
        self.mirror_l = wx.CheckBox(self,  label=mirror_label)

        # Sizers
        trig_options_sizer = wx.FlexGridSizer(8, 2, 1, 4)
        trig_options_sizer.AddMany([ (log_l, 0, wx.EXPAND),
            (self.log_cb, 0, wx.EXPAND),
            (val_label_l, 0, wx.EXPAND),
            (self.val_label_cb, 0, wx.EXPAND),
            (type_l, 0, wx.EXPAND),
            (self.type_cb, 0, wx.EXPAND),
            (value_l, 0, wx.EXPAND),
            (self.value_tc, 0, wx.EXPAND),
            (cond_name_l, 0, wx.EXPAND),
            (self.cond_name_tc, 0, wx.EXPAND),
            (set_l, 0, wx.EXPAND),
            (self.set_cb, 0, wx.EXPAND),
            (lock_l, 0, wx.EXPAND),
            (self.lock_tc, 0, wx.EXPAND),
            (cmd_l, 0, wx.EXPAND),
            (self.cmd_tc, 0, wx.EXPAND) ])
        trigger_conditions_sizer = wx.BoxSizer(wx.VERTICAL)
        trigger_conditions_sizer.Add(triggger_cond_l, 0, wx.EXPAND, 3)
        trigger_conditions_sizer.Add(self.read_trig_cond_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        trigger_conditions_sizer.Add(self.read_output_l, 0, wx.EXPAND, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(box_sub_title, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(trig_options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(trigger_conditions_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.mirror_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        if not MainApp.sensors_info_pannel.trigger_list.initial_type == "above" and not MainApp.sensors_info_pannel.trigger_list.initial_type == "below":
            self.mirror_l.Hide()
        if not self.find_mirror() > -1:
            self.mirror_l.SetLabel("Create Mirror")
        else:
            self.mirror_l.SetForegroundColour((75,190,75))
            self.mirror_l.SetValue(True)


    def find_mirror(self):
        print(" looking for mirror")
        mirror_trigger_index = -1
        for index in range(0, MainApp.sensors_info_pannel.trigger_list.GetItemCount()):
            if not index == MainApp.sensors_info_pannel.trigger_list.initial_index:
                log      = MainApp.sensors_info_pannel.trigger_list.GetItem(index,0).GetText()
                label    = MainApp.sensors_info_pannel.trigger_list.GetItem(index,1).GetText()
                value    = MainApp.sensors_info_pannel.trigger_list.GetItem(index,3).GetText()
                name     = MainApp.sensors_info_pannel.trigger_list.GetItem(index,4).GetText()
                if MainApp.sensors_info_pannel.trigger_list.initial_log == log:
                    if MainApp.sensors_info_pannel.trigger_list.initial_val_label == label:
                        if MainApp.sensors_info_pannel.trigger_list.initial_value == value:
                            if MainApp.sensors_info_pannel.trigger_list.initial_cond_name == name:
                                mirror_trigger_index = index
        return mirror_trigger_index

    def create_mirror(self, log, label, type, value, name, set, cooldown, cmd):
        # flip set direction
        if set == "on":
            set = "off"
        elif set == "off":
            set = "on"
        # flip relay command if it's a relay command or similar
        if "_on.py" in cmd:
            cmd = cmd.replace("_on.py", "_off.py")
        elif "_off.py" in cmd:
            cmd = cmd.replace("_off.py", "_on.py")
        # flip type direction
        if type == "above":
            MainApp.sensors_info_pannel.trigger_list.add_to_trigger_list(log, label, "below", value, name, set, cooldown, cmd)
        elif type == "below":
            MainApp.sensors_info_pannel.trigger_list.add_to_trigger_list(log, label, "above", value, name, set, cooldown, cmd)

    def change_mirror(self, mirror_index, log, label, value, name):
        MainApp.sensors_info_pannel.trigger_list.SetItem(mirror_index,0, log)
        MainApp.sensors_info_pannel.trigger_list.SetItem(mirror_index,1, label)
        MainApp.sensors_info_pannel.trigger_list.SetItem(mirror_index,3, value)
        MainApp.sensors_info_pannel.trigger_list.SetItem(mirror_index,4, name)

    def get_log_options(self):
        log_list = []
        # logs listen in sensor table
        for index in range(0, MainApp.sensors_info_pannel.sensor_list.GetItemCount()):
            log = MainApp.sensors_info_pannel.sensor_list.GetItem(index, 2).GetText()
            if "/logs/" in log:
                log = log.split('/logs/')[1]
            if not log in log_list:
                log_list.append(log)
        # logs on the pigrow
        log_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls -1 " + log_path)
        logs = out.splitlines()
        for log in logs:
            if not log in log_list:
                log_list.append(log)
        # return list of all logs
        return log_list

    def set_label_opts(self, e=""):
        opts=self.get_value_label_ops()
        self.val_label_cb.Clear()
        self.val_label_cb.Append(opts)

    def get_value_label_ops(self):
        log_name = self.log_cb.GetValue().strip()
        label_opts = []
        if log_name == "":
            return []
        log_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/" + log_name
        cmd = "tail -1 " + log_path
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        if ">" in out:
            items = out.split(">")
            for item in items:
                if "=" in item:
                    label_opts.append(item.split("=")[0])
        return label_opts

    def type_cb_select(self, e):
        type = self.type_cb.GetValue()
        if type == "all":
            self.value_tc.Disable()
        else:
            self.value_tc.Enable()
        if type == "above" or type == "below":
            self.mirror_l.Show()
        else:
            self.mirror_l.Hide()
        self.Layout()

    def read_trigger_conditions_click(self, e):
        self.read_output_l.SetLabel("")
        conditions_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/trigger_conditions.txt"
        cmd = "cat " + conditions_path
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        condition_list = out.splitlines()
        for condition in condition_list:
            if self.cond_name_tc.GetValue().strip() in condition:
                self.read_output_l.SetLabel(condition)

    def check_if_change(self):
        if not MainApp.sensors_info_pannel.trigger_list.initial_log == self.log_cb.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_val_label == self.val_label_cb.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_type == self.type_cb.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_value == self.value_tc.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_cond_name == self.cond_name_tc.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_set == self.set_cb.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_lock == self.lock_tc.GetValue():
            return True
        if not MainApp.sensors_info_pannel.trigger_list.initial_cmd == self.cmd_tc.GetValue():
            return True
        if self.mirror_l.GetValue() == True and self.mirror_l.GetLabel() == 'Create Mirror':
            return True
        # If nothing has changed and the users not asking to create a new mirror trigger
        return False

    def add_click(self, e):
        if self.check_if_change():
            print(" - Saving Changes to Trigger Events File -")
            log = self.log_cb.GetValue()
            label = self.val_label_cb.GetValue()
            type = self.type_cb.GetValue()
            value = self.value_tc.GetValue()
            name = self.cond_name_tc.GetValue()
            set = self.set_cb.GetValue()
            cooldown = self.lock_tc.GetValue()
            cmd = self.cmd_tc.GetValue()
            tt_index = MainApp.sensors_info_pannel.trigger_list.initial_index
            # if new create a new item in the table
            if tt_index == -1:
                # If not already in the table
                MainApp.sensors_info_pannel.trigger_list.add_to_trigger_list(log, label, type, value, name, set, cooldown, cmd)
                if self.mirror_l.GetValue() == True:
                    self.create_mirror(log, label, type, value, name, set, cooldown, cmd)
            else:
                # Fot existing triggers
                MainApp.sensors_info_pannel.trigger_list.update_table_line(tt_index, log, label, type, value, name, set, cooldown, cmd)
                if self.mirror_l.GetValue() == True:
                    mirror_index = self.find_mirror()
                    if type == "above" or type == "below":
                        if mirror_index > -1:
                            print(" -- might be be editing the mirror -- ")
                            self.change_mirror(mirror_index, log, label, value, name)
                        else:
                            self.create_mirror(log, label, type, value, name, set, cooldown, cmd)
            MainApp.sensors_info_pannel.trigger_list.save_table_to_pi()
        self.Destroy()

    def OnClose(self, e):

        self.Destroy()


class ads1115_dialog(wx.Dialog):
    """
    For setting up a ds18b20 temp sensor
        """
    def __init__(self, *args, **kw):
        super(ads1115_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("ADS1115 Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # read values for when editing existing entry
        self.s_name  = MainApp.sensors_info_pannel.sensor_list.s_name
        self.s_type  = "ADS1115"
        self.s_log   = MainApp.sensors_info_pannel.sensor_list.s_log
        self.s_loc   = MainApp.sensors_info_pannel.sensor_list.s_loc
        self.s_extra = MainApp.sensors_info_pannel.sensor_list.s_extra
        self.timing_string = MainApp.sensors_info_pannel.sensor_list.s_timing
        try:
            s_rep     = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[0]
            s_rep_txt = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[1]
        except:
            s_rep = ""
            s_rep_txt = ""
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='ADS1115 Analog to Digital Converter')
        box_label.SetFont(shared_data.title_font)
        # buttons_
        self.add_btn = wx.Button(self, label='OK', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # hardware information
        name_l = wx.StaticText(self,  label='Unique Name')
        self.name_tc = wx.TextCtrl(self, size=(400,30))
        log_l = wx.StaticText(self,  label='Log Location')
        self.log_tc = wx.TextCtrl(self, size=(400,30))
        self.graph_btn = wx.Button(self, label='Graph', size=(175, 30))
        self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_click)
        sensor_l = wx.StaticText(self,  label='Sensor Location')
        # auto list i2c sensors
        asd_list = self.find_ads1115_devices()
             #---- add line here to remove sensors already added
        self.loc_cb = wx.ComboBox(self, choices = asd_list, size=(170, 25))
        self.read_ads1115_btn = wx.Button(self, label='Read ADS1115')
        self.read_ads1115_btn.Bind(wx.EVT_BUTTON, self.read_ads1115_click)
        # timing string
        timeing_l = wx.StaticText(self,  label='Repeating every ')
        self.rep_num_tc = wx.TextCtrl(self, size=(70,30))
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, size=(100, 30))
        # Channel settings
        chan_l = wx.StaticText(self,  label='Channel')
        chan_0_l = wx.StaticText(self,  label='A0')
        chan_1_l = wx.StaticText(self,  label='A1')
        chan_2_l = wx.StaticText(self,  label='A2')
        chan_3_l = wx.StaticText(self,  label='A3')
        values_l = wx.StaticText(self,  label='Value:')
        self.value_0_l = wx.StaticText(self,  label='--')
        self.value_1_l = wx.StaticText(self,  label='--')
        self.value_2_l = wx.StaticText(self,  label='--')
        self.value_3_l = wx.StaticText(self,  label='--')
        gain_l = wx.StaticText(self,  label='Gain')
        gain_opts = ["1", "2", "4", "8", "16"]
        self.gain0_cb = wx.ComboBox(self, choices = gain_opts, size=(100, 30))
        self.gain1_cb = wx.ComboBox(self, choices = gain_opts, size=(100, 30))
        self.gain2_cb = wx.ComboBox(self, choices = gain_opts, size=(100, 30))
        self.gain3_cb = wx.ComboBox(self, choices = gain_opts, size=(100, 30))
        sps_l = wx.StaticText(self,  label='Samples Per Second')
        #sps_opts_1015 = ["128", "250", "490", "920", "1600", "2400", "3300"]
        sps_opts_1115= ["8", "16", "32", "64", "128", "250", "475", "860"]
        self.sps_0_cb = wx.ComboBox(self, choices = sps_opts_1115, size=(100, 30))
        self.sps_1_cb = wx.ComboBox(self, choices = sps_opts_1115, size=(100, 30))
        self.sps_2_cb = wx.ComboBox(self, choices = sps_opts_1115, size=(100, 30))
        self.sps_3_cb = wx.ComboBox(self, choices = sps_opts_1115, size=(100, 30))
        show_as_l = wx.StaticText(self,  label='Show as')
        show_as_opts = ['raw', 'volt', 'percent']
                    # raw - basic output
                    # volt - gives the voltage value ajusted for gain
                    # percent - not yet supported in log_ads1115.py
        self.show_as_0_cb = wx.ComboBox(self, choices = show_as_opts, size=(100, 30))
        self.show_as_1_cb = wx.ComboBox(self, choices = show_as_opts, size=(100, 30))
        self.show_as_2_cb = wx.ComboBox(self, choices = show_as_opts, size=(100, 30))
        self.show_as_3_cb = wx.ComboBox(self, choices = show_as_opts, size=(100, 30))
        centralise_l = wx.StaticText(self,  label='Centralise')
        self.centralise_0 = wx.CheckBox(self, label='')
        self.centralise_1 = wx.CheckBox(self, label='')
        self.centralise_2 = wx.CheckBox(self, label='')
        self.centralise_3 = wx.CheckBox(self, label='') # not yet properly supported in log_ads1115.py needs min and max points.
        # min-max triggers and script path
        self.use_script_triggers = wx.StaticText(self, label='Min - Max Triggers')
        max_l = wx.StaticText(self,  label='Max')
        self.val0_max_val = wx.TextCtrl(self)
        self.val1_max_val = wx.TextCtrl(self)
        self.val2_max_val = wx.TextCtrl(self)
        self.val3_max_val = wx.TextCtrl(self)
        max_s_l = wx.StaticText(self,  label='Max Script')
        self.val0_max_script = wx.TextCtrl(self)
        self.val1_max_script = wx.TextCtrl(self)
        self.val2_max_script = wx.TextCtrl(self)
        self.val3_max_script = wx.TextCtrl(self)
        min_l = wx.StaticText(self,  label='Min')
        self.val0_min_val = wx.TextCtrl(self)
        self.val1_min_val = wx.TextCtrl(self)
        self.val2_min_val = wx.TextCtrl(self)
        self.val3_min_val = wx.TextCtrl(self)
        min_s_l = wx.StaticText(self,  label='Min Script')
        self.val0_min_script = wx.TextCtrl(self)
        self.val1_min_script = wx.TextCtrl(self)
        self.val2_min_script = wx.TextCtrl(self)
        self.val3_min_script = wx.TextCtrl(self)
        # universal setting_string_tb
        max_volt_l = wx.StaticText(self,  label='Max Voltage')
        self.max_volt_tc = wx.TextCtrl(self, value="3.2767", size=(400,30))
        tound_to_l = wx.StaticText(self,  label='Round to ... decimal places')
        self.round_to_tc = wx.TextCtrl(self, value="4", size=(400,30))

        # min-max sizer
        trigger_sizer = wx.GridSizer(4, 5, 1, 4)
        trigger_sizer.AddMany([ (max_l, 0, wx.EXPAND),
            (self.val0_max_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_max_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_max_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_max_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (max_s_l, 0, wx.EXPAND),
            (self.val0_max_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_max_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_max_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_max_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (min_l, 0, wx.EXPAND),
            (self.val0_min_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_min_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_min_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_min_val, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (min_s_l, 0, wx.EXPAND),
            (self.val0_min_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_min_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_min_script, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_min_script, 0, wx.ALIGN_CENTER_HORIZONTAL)])

        # need four lines one for each channel, set value type, ranges, +- correction, and tools to perform tuning and calibration.

        # Sizers
        loc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(self.loc_cb, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.read_ads1115_btn, 0, wx.ALL, 3)
        timing_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_sizer.Add(self.rep_num_tc, 0, wx.ALL, 3)
        timing_sizer.Add(self.rep_opts_cb, 0, wx.ALL, 3)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_tc, 2, wx.ALL, 3)
        log_sizer.Add(self.graph_btn, 0, wx.ALL, 3)
        options_sizer = wx.GridSizer(4, 2, 1, 4)
        options_sizer.AddMany([ (name_l, 0, wx.EXPAND),
            (self.name_tc, 0, wx.EXPAND),
            (log_l, 0, wx.EXPAND),
            (log_sizer, 0, wx.EXPAND),
            (sensor_l, 0, wx.EXPAND),
            (loc_sizer, 0, wx.EXPAND),
            (timeing_l, 0, wx.EXPAND),
            (timing_sizer, 0, wx.EXPAND) ])
        channels_sizer = wx.GridSizer(6, 5, 1, 4)
        channels_sizer.AddMany([ (chan_l, 0, wx.EXPAND),
            (chan_0_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (chan_1_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (chan_2_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (chan_3_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (values_l, 0, wx.EXPAND),
            (self.value_0_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_1_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_2_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_3_l, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (gain_l, 0, wx.EXPAND),
            (self.gain0_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain1_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain2_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain3_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (sps_l, 0, wx.EXPAND),
            (self.sps_0_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_1_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_2_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_3_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (show_as_l, 0, wx.EXPAND),
            (self.show_as_0_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_1_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_2_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_3_cb, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (centralise_l, 0, wx.EXPAND),
            (self.centralise_0, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_1, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_2, 0, wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_3, 0, wx.ALIGN_CENTER_HORIZONTAL) ])
        max_volt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_volt_sizer.Add(max_volt_l, 0,  wx.ALL, 3)
        max_volt_sizer.Add(self.max_volt_tc, 0,  wx.ALL, 3)
        round_to_sizer = wx.BoxSizer(wx.HORIZONTAL)
        round_to_sizer.Add(tound_to_l, 0,  wx.ALL, 3)
        round_to_sizer.Add(self.round_to_tc, 0,  wx.ALL, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(channels_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.use_script_triggers, 0, wx.ALL, 3)
        main_sizer.Add(trigger_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(max_volt_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(round_to_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)




        # set values for when reading from double click
        self.name_tc.SetValue(self.s_name)
        self.log_tc.SetValue(self.s_log)
        self.loc_cb.SetValue(self.s_loc)
        self.rep_num_tc.SetValue(s_rep)
        self.rep_opts_cb.SetValue(s_rep_txt)
        self.set_extras_from_string(self.s_extra)

    def set_extras_from_string(self, extras_string):
        #print (extras_string)
        extra_list = extras_string.split(" ")
        for item in extra_list:
            if ":" in item:
                item = item.split(":")
                item_key = item[0]
                item_value = item[1]
                print(item_key, item_value)
                if item_key == "gain0":
                    self.gain0_cb.SetValue(item_value)
                elif item_key == "gain1":
                    self.gain1_cb.SetValue(item_value)
                elif item_key == "gain2":
                    self.gain2_cb.SetValue(item_value)
                elif item_key == "gain3":
                    self.gain3_cb.SetValue(item_value)
                elif item_key == "sps0":
                    self.sps_0_cb.SetValue(item_value)
                elif item_key == "sps1":
                    self.sps_1_cb.SetValue(item_value)
                elif item_key == "sps2":
                    self.sps_2_cb.SetValue(item_value)
                elif item_key == "sps3":
                    self.sps_3_cb.SetValue(item_value)
                elif item_key == "show0":
                    self.show_as_0_cb.SetValue(item_value)
                elif item_key == "show1":
                    self.show_as_1_cb.SetValue(item_value)
                elif item_key == "show2":
                    self.show_as_2_cb.SetValue(item_value)
                elif item_key == "show3":
                    self.show_as_3_cb.SetValue(item_value)
                elif item_key == "centralise0":
                    self.centralise_0.SetValue(bool(item_value))
                elif item_key == "centralise1":
                    self.centralise_1.SetValue(bool(item_value))
                elif item_key == "centralise2":
                    self.centralise_2.SetValue(bool(item_value))
                elif item_key == "centralise3":
                    self.centralise_3.SetValue(bool(item_value))
                elif item_key == "gain":
                    self.gain0_cb.SetValue(item_value)
                    self.gain1_cb.SetValue(item_value)
                    self.gain2_cb.SetValue(item_value)
                    self.gain3_cb.SetValue(item_value)
                elif item_key == "sps":
                    self.sps_0_cb.SetValue(item_value)
                    self.sps_1_cb.SetValue(item_value)
                    self.sps_2_cb.SetValue(item_value)
                    self.sps_3_cb.SetValue(item_value)
                elif item_key == "show":
                    self.show_as_0_cb.SetValue(item_value)
                    self.show_as_1_cb.SetValue(item_value)
                    self.show_as_2_cb.SetValue(item_value)
                    self.show_as_3_cb.SetValue(item_value)
                elif item_key == "centralise":
                    self.centralise_0.SetValue(bool(item_value))
                    self.centralise_1.SetValue(bool(item_value))
                    self.centralise_2.SetValue(bool(item_value))
                    self.centralise_3.SetValue(bool(item_value))
                elif item_key == "max_volt":
                    self.max_volt_tc.SetValue(item_value)
                elif item_key == "round":
                    self.round_to_tc.SetValue(item_value)
                # max values and scripts
                elif item_key == "max_trigger":
                    self.val0_max_val.SetValue(item_value)
                    self.val1_max_val.SetValue(item_value)
                    self.val2_max_val.SetValue(item_value)
                    self.val3_max_val.SetValue(item_value)
                elif item_key == "val0_max_trigger":
                    self.val0_max_val.SetValue(item_value)
                elif item_key == "val1_max_trigger":
                    self.val1_max_val.SetValue(item_value)
                elif item_key == "val2_max_trigger":
                    self.val2_max_val.SetValue(item_value)
                elif item_key == "val3_max_trigger":
                    self.val3_max_val.SetValue(item_value)
                elif item_key == "max_script":
                    self.val0_max_script.SetValue(item_value)
                    self.val1_max_script.SetValue(item_value)
                    self.val2_max_script.SetValue(item_value)
                    self.val3_max_script.SetValue(item_value)
                elif item_key == "val0_max_script":
                    self.val0_max_script.SetValue(item_value)
                elif item_key == "val1_max_script":
                    self.val1_max_script.SetValue(item_value)
                elif item_key == "val2_max_script":
                    self.val2_max_script.SetValue(item_value)
                elif item_key == "val3_max_script":
                    self.val3_max_script.SetValue(item_value)
                # min values and scripts
                elif item_key == "min_trigger":
                    self.val0_min_val.SetValue(item_value)
                    self.val1_min_val.SetValue(item_value)
                    self.val2_min_val.SetValue(item_value)
                    self.val3_min_val.SetValue(item_value)
                elif item_key == "val0_min_trigger":
                    self.val0_min_val.SetValue(item_value)
                elif item_key == "val1_min_trigger":
                    self.val1_min_val.SetValue(item_value)
                elif item_key == "val2_min_trigger":
                    self.val2_min_val.SetValue(item_value)
                elif item_key == "val3_min_trigger":
                    self.val3_min_val.SetValue(item_value)
                elif item_key == "max_script":
                    self.val0_min_script.SetValue(item_value)
                    self.val1_min_script.SetValue(item_value)
                    self.val2_min_script.SetValue(item_value)
                    self.val3_min_script.SetValue(item_value)
                elif item_key == "val0_max_script":
                    self.val0_min_script.SetValue(item_value)
                elif item_key == "val1_max_script":
                    self.val1_min_script.SetValue(item_value)
                elif item_key == "val2_max_script":
                    self.val2_min_script.SetValue(item_value)
                elif item_key == "val3_max_script":
                    self.val3_min_script.SetValue(item_value)


    def read_ads1115_click(self, e):
        script_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/log_ads1115.py "
        test_log = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/ads1115_button_test.txt"
        arg_extra = self.make_extra_settings_string()
        arg_extra = arg_extra.replace(":", "=")
        cmd = script_path + "log=" + test_log + " address=" + self.loc_cb.GetValue()[0:3] + arg_extra
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        val0 = None
        for line in out.splitlines():
            if "Written;" in line:
                line = line.split(">")
                val0 = line[1]
                val1 = line[2]
                val2 = line[3]
                val3 = line[4]
                print("ads1115 reading; ", val0, val1, val2, val3)
                self.value_0_l.SetLabel(val0)
                self.value_1_l.SetLabel(val1)
                self.value_2_l.SetLabel(val2)
                self.value_3_l.SetLabel(val3)
        if val0 == None:
            print("Could not read ADS1115 located at " + self.loc_cb.GetValue())

    def find_ads1115_devices(self):
        pos_list = ["GND - (0x48)", "VDD - (0x49)", "SDA - (0x4A)", "SCL - (0x4B)"]
        i2c_devices = system_ctrl_pnl.find_i2c_devices(MainApp.system_ctrl_pannel, "e")
        ads1115_list = []
        if not i2c_devices == None:
            for device in i2c_devices:
                for possibly in pos_list:
                    if device in possibly:
                        ads1115_list.append(possibly)
        return ads1115_list

    def graph_click(self, e):
        log = self.log_tc.GetValue()
        print("Graphing ads1115 log - " + log)
        MainApp.graphing_ctrl_pannel.graph_cb.SetValue('Pigrow')
        MainApp.graphing_ctrl_pannel.select_script_cb.SetValue('graph_ads1115.py')
        #MainApp.graphing_ctrl_pannel.get_opts_tb.SetValue(True)
        MainApp.graphing_ctrl_pannel.extra_args.SetValue("log="+log)
        MainApp.view_pnl.view_cb.SetValue("Graphs")
        MainApp.graphing_ctrl_pannel.make_graph_click("e")

    def make_extra_settings_string(self):
        # get individual channel settings
        new_a0_gain = self.gain0_cb.GetValue()
        new_a1_gain = self.gain1_cb.GetValue()
        new_a2_gain = self.gain2_cb.GetValue()
        new_a3_gain = self.gain3_cb.GetValue()
        new_a0_sps = self.sps_0_cb.GetValue()
        new_a1_sps = self.sps_1_cb.GetValue()
        new_a2_sps = self.sps_2_cb.GetValue()
        new_a3_sps = self.sps_3_cb.GetValue()
        new_a0_show_as = self.show_as_0_cb.GetValue()
        new_a1_show_as = self.show_as_1_cb.GetValue()
        new_a2_show_as = self.show_as_2_cb.GetValue()
        new_a3_show_as = self.show_as_3_cb.GetValue()
        new_a0_centralise= str(self.centralise_0.GetValue())
        new_a1_centralise= str(self.centralise_1.GetValue())
        new_a2_centralise= str(self.centralise_2.GetValue())
        new_a3_centralise= str(self.centralise_3.GetValue())
        new_max_volt = self.max_volt_tc.GetValue()
        # min - max values and script triggers
        val0_max_val = self.val0_max_val.GetValue()
        val1_max_val = self.val1_max_val.GetValue()
        val2_max_val = self.val2_max_val.GetValue()
        val3_max_val = self.val3_max_val.GetValue()
        val0_max_script = self.val0_max_script.GetValue()
        val1_max_script = self.val1_max_script.GetValue()
        val2_max_script = self.val2_max_script.GetValue()
        val3_max_script = self.val3_max_script.GetValue()
        val0_min_val = self.val0_min_val.GetValue()
        val1_min_val = self.val1_min_val.GetValue()
        val2_min_val = self.val2_min_val.GetValue()
        val3_min_val = self.val3_min_val.GetValue()
        val0_min_script = self.val0_min_script.GetValue()
        val1_min_script = self.val1_min_script.GetValue()
        val2_min_script = self.val2_min_script.GetValue()
        val3_min_script = self.val3_min_script.GetValue()
        if new_max_volt == "":
            new_max_volt = "3.2767"
            self.max_volt_tc.SetValue(new_max_volt)
        new_round_to = self.round_to_tc.GetValue()
        if new_round_to == "":
            new_round_to = "4"
            self.round_to_tc.SetValue(new_round_to)
        # create args string
        # make a text string for each channel
        a0_sets = ""
        if not new_a0_gain == "":
            a0_sets += " gain0:" + new_a0_gain
        if not new_a0_sps == "":
            a0_sets += " sps0:" + new_a0_sps
        if not new_a0_show_as == "":
            a0_sets += " show0:" + new_a0_show_as
        if not new_a0_centralise == "False":
            a0_sets += " centralise0:" + new_a0_centralise
        a1_sets = ""
        if not new_a1_gain == "":
            a1_sets += " gain1:" + new_a1_gain
        if not new_a1_sps == "":
            a1_sets += " sps1:" + new_a1_sps
        if not new_a1_show_as == "":
            a1_sets += " show1:" + new_a1_show_as
        if not new_a1_centralise == "False":
            a1_sets += " centralise1:" + new_a1_centralise
        a2_sets = ""
        if not new_a2_gain == "":
            a2_sets += " gain2:" + new_a2_gain
        if not new_a2_sps == "":
            a2_sets += " sps2:" + new_a2_sps
        if not new_a2_show_as == "":
            a2_sets += " show2:" + new_a2_show_as
        if not new_a2_centralise == "False":
            a2_sets += " centralise2:" + new_a2_centralise
        a3_sets = ""
        if not new_a3_gain == "":
            a3_sets += " gain3:" + new_a3_gain
        if not new_a3_sps == "":
            a3_sets += " sps3:" + new_a3_sps
        if not new_a3_show_as == "":
            a3_sets += " show3:" + new_a3_show_as
        if not new_a3_centralise == "False":
            a3_sets += " centralise3:" + new_a3_centralise
        universal_sets = ""
        if not new_max_volt == "3.2767":
            universal_sets += " max_volt:" + new_max_volt
        if not new_round_to == "4":
            universal_sets += " round:" + new_round_to
        # min max
        min_max_sets = ""
        if not val0_max_val == "":
            min_max_sets += " val0_max_trigger:" + val0_max_val
        if not val1_max_val == "":
            min_max_sets += " val1_max_trigger:" + val1_max_val
        if not val2_max_val == "":
            min_max_sets += " val2_max_trigger:" + val2_max_val
        if not val3_max_val == "":
            min_max_sets += " val3_max_trigger:" + val3_max_val
        if not val0_max_script == "":
            min_max_sets += " val0_max_script:" + val0_max_script
        if not val1_max_script == "":
            min_max_sets += " val1_max_script:" + val1_max_script
        if not val2_max_script == "":
            min_max_sets += " val2_max_script:" + val2_max_script
        if not val3_max_script == "":
            min_max_sets += " val3_max_script:" + val3_max_script
        if not val0_min_val == "":
            min_max_sets += " val0_min_trigger:" + val0_min_val
        if not val1_min_val == "":
            min_max_sets += " val1_min_trigger:" + val1_min_val
        if not val2_min_val == "":
            min_max_sets += " val2_min_trigger:" + val2_min_val
        if not val3_min_val == "":
            min_max_sets += " val3_min_trigger:" + val3_min_val
        if not val0_min_script == "":
            min_max_sets += "val0_min_script:" + val0_min_script
        if not val1_min_script == "":
            min_max_sets += "val1_min_script:" + val1_min_script
        if not val2_min_script == "":
            min_max_sets += "val2_min_script:" + val2_min_script
        if not val3_min_script == "":
            min_max_sets += "val3_min_script:" + val3_min_script
        # put all four together
        o_extra = a0_sets + a1_sets + a2_sets + a3_sets + universal_sets + min_max_sets
        return o_extra

    def add_click(self, e):
        o_name = self.name_tc.GetValue()
        o_type = "ADS1115"
        o_log = self.log_tc.GetValue()
        o_loc = self.loc_cb.GetValue()
        new_cron_num = self.rep_num_tc.GetValue()
        new_cron_txt = self.rep_opts_cb.GetValue()
        new_timing_string = str(new_cron_num) + " " + new_cron_txt
        o_extra = self.make_extra_settings_string()
        # check to see if changes have been made
        changed = "probably something"
        if self.s_name == o_name:
            #print("name not changed")
            if self.s_log == o_log:
                #print("log path not changed")
                if self.s_loc == o_loc:
                    #print("wiring location not changed")
                    if self.s_extra == o_extra:
                        #print("extra field not changed")
                        changed = "nothing"
                        #nothing has changed in the config file so no need to update.
        # check to see if changes have been made to the cron timing
        if self.timing_string == new_timing_string and changed == "nothing":
            print(" -- Timing string didn't change, not did any settings -- ")
        else:
            self.edit_cron_job(o_log, o_loc[0:3], new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            log_freq = str(new_cron_num) + " " + new_cron_txt
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,o_type,o_log,o_loc,o_extra,log_freq)
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = o_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
        self.Destroy()

    def edit_cron_job(self, o_log, o_loc, job_repeat, job_repnum):
        print("changing cron...")
        # check to find cron job handling this sensor
        line_number_repeting_cron = -1
        for index in range(0, cron_list_pnl.repeat_cron.GetItemCount()):
            cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
            if "log_ads1115.py" in cmd_path:
                print("    -Found  ;- " + cmd_path)
                cmd_args = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                if o_loc[0:3].lower() in cmd_args.lower():
                    print("    -Located; " + o_loc)
                    line_number_repeting_cron = index
        # check to see if this is a new job or not
        if not line_number_repeting_cron == -1:
            cron_enabled = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 1).GetText()
            cron_task    = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 3).GetText()
            cron_args_original = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 4).GetText()
            if "address=" in cron_args_original:
                sensor_args = cron_args_original.split("address=")[1].split(" ")[0]
                sensor_loc = self.loc_cb.GetValue()[0:3]
            else:
                print("Sorry, address= not found in cronjob, try deleting the cronjob and adding this sensor again")
                return None
            args_extra = self.make_extra_settings_string()
            args_extra = args_extra.replace(":","=")
            cron_args    = "log=" + self.log_tc.GetValue() + " address=" + sensor_loc + args_extra
            cron_comment = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 5).GetText()
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            #print("Cron job; " + "modified" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            cron_list_pnl.repeat_cron.DeleteItem(line_number_repeting_cron)
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'modified', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")
        else:
            print("Job not currently in cron, adding it...")
            cron_enabled = "True"
            cron_task = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/log_ads1115.py"
            args_extra = self.make_extra_settings_string()
            args_extra = args_extra.replace(":","=")
            cron_args = "log=" + self.log_tc.GetValue() + " address=" + self.loc_cb.GetValue()[0:3] + " " + args_extra
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            cron_comment = ""
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            #print("Cron job; " + "new" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")


    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()

class ds18b20_dialog(wx.Dialog):
    """
    For setting up a ds18b20 temp sensor
        """
    def __init__(self, *args, **kw):
        super(ds18b20_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 300))
        self.SetTitle("DS18B20 Temp Sensor Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # read values for when editing existing entry
        self.s_name  = MainApp.sensors_info_pannel.sensor_list.s_name
        self.s_type  = "DS18B20"
        self.s_log   = MainApp.sensors_info_pannel.sensor_list.s_log
        self.s_loc   = MainApp.sensors_info_pannel.sensor_list.s_loc
        self.s_extra = MainApp.sensors_info_pannel.sensor_list.s_extra
        self.timing_string = MainApp.sensors_info_pannel.sensor_list.s_timing
        try:
            s_rep     = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[0]
            s_rep_txt = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[1]
        except:
            s_rep = ""
            s_rep_txt = ""
        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='DS18B20 Temp Sensor\n DO NOT USE THIS IS DEPRECIATED NOW')
        box_label.SetFont(shared_data.title_font)
        # table information
        name_l = wx.StaticText(self,  label='Unique Name')
        self.name_tc = wx.TextCtrl(self, size=(400,30))
        log_l = wx.StaticText(self,  label='Log Location')
        self.log_tc = wx.TextCtrl(self, size=(400,30))
        sensor_l = wx.StaticText(self,  label='Sensor Location')
        # auto list temp sensors
        temp_sensor_list = MainApp.system_ctrl_pannel.find_ds18b20_devices()
             #---- add line here to remove sensors already added
        self.temp_sensor_cb = wx.ComboBox(self, choices = temp_sensor_list, size=(170, 25))
        self.read_temp_btn = wx.Button(self, label='Read Temp')
        self.read_temp_btn.Bind(wx.EVT_BUTTON, self.read_temp_click)
        self.temp_value = wx.StaticText(self,  label='--')
        # timing string
        timeing_l = wx.StaticText(self,  label='Repeating every ')
        self.rep_num_tc = wx.TextCtrl(self, size=(70,30))
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, size=(100, 30))
        # ok and cancel Buttons
        self.graph_btn = wx.Button(self, label='Graph', size=(175, 30))
        self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_click)
        self.add_btn = wx.Button(self, label='OK', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # set values for when reading from double click
        self.name_tc.SetValue(self.s_name)
        self.log_tc.SetValue(self.s_log)
        self.temp_sensor_cb.SetValue(self.s_loc)
        self.rep_num_tc.SetValue(s_rep)
        self.rep_opts_cb.SetValue(s_rep_txt)

        #
        temp_sensor_sizer = wx.BoxSizer(wx.HORIZONTAL)
        temp_sensor_sizer.Add(self.temp_sensor_cb, 0, wx.ALL|wx.EXPAND, 3)
        temp_sensor_sizer.Add(self.read_temp_btn, 0, wx.ALL, 3)
        temp_sensor_sizer.Add(self.temp_value, 0, wx.ALL|wx.EXPAND, 3)
        timing_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_sizer.Add(self.rep_num_tc, 0, wx.ALL, 3)
        timing_sizer.Add(self.rep_opts_cb, 0, wx.ALL, 3)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_tc, 2, wx.ALL, 3)
        log_sizer.Add(self.graph_btn, 0, wx.ALL, 3)
        options_sizer = wx.GridSizer(4, 2, 1, 4)
        options_sizer.AddMany([ (name_l, 0, wx.EXPAND),
            (self.name_tc, 0, wx.EXPAND),
            (log_l, 0, wx.EXPAND),
            (log_sizer, 0, wx.EXPAND),
            (sensor_l, 0, wx.EXPAND),
            (temp_sensor_sizer, 0, wx.EXPAND),
            (timeing_l, 0, wx.EXPAND),
            (timing_sizer, 0, wx.EXPAND) ])
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)

        main_sizer.AddStretchSpacer(1)

        self.SetSizer(main_sizer)

    def graph_click(self, e):
        log = self.log_tc.GetValue()
        print("wants to graph ds18b20 log - " + log)
        MainApp.graphing_ctrl_pannel.graph_cb.SetValue('Pigrow')
        MainApp.graphing_ctrl_pannel.select_script_cb.SetValue('dstemp_graph.py')
        #MainApp.graphing_ctrl_pannel.get_opts_tb.SetValue(True)
        MainApp.graphing_ctrl_pannel.extra_args.SetValue("log="+log)
        MainApp.view_pnl.view_cb.SetValue("Graphs")
        MainApp.graphing_ctrl_pannel.make_graph_click("e")


    def read_temp_click(self, e):
        sensor = self.temp_sensor_cb.GetValue()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /sys/bus/w1/devices/" + sensor + "/w1_slave")
        for line in out.splitlines():
            if "t=" in line:
                temp = str(int(line.split("t=")[1]) / 1000) + " C"
                print("Temp = " + temp)
                self.temp_value.SetLabel(temp)

    def add_click(self, e):
        o_name = self.name_tc.GetValue()
        o_type = "DS18B20"
        o_log = self.log_tc.GetValue()
        o_loc = self.temp_sensor_cb.GetValue()
        o_extra = ""
        new_cron_num = self.rep_num_tc.GetValue()
        new_cron_txt = self.rep_opts_cb.GetValue()
        new_timing_string = str(new_cron_num) + " " + new_cron_txt

        # print("adding; ")
        # print(o_name)
        # print(o_type)
        # print(o_log)
        # print(o_loc)
        # print("______")
        # check to see if changes have been made
        changed = "probably something"
        if self.s_name == o_name:
            #print("name not changed")
            if self.s_log == o_log:
                #print("log path not changed")
                if self.s_loc == o_loc:
                    #print("wiring location not changed")
                    if self.s_extra == o_extra:
                        #print("extra field not changed")
                        changed = "nothing"
                        #nothing has changed in the config file so no need to update.
        # check to see if changes have been made to the cron timing
        if self.timing_string == new_timing_string and changed == "nothing":
            print(" -- Timing string didn't change or any cron settings -- ")
        else:
            self.edit_cron_job(o_log, o_loc, new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            log_freq = str(new_cron_num) + " " + new_cron_txt
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,o_type,o_log,o_loc,o_extra,log_freq)
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = o_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
        self.Destroy()

    def edit_cron_job(self, o_log, o_loc, job_repeat, job_repnum):
        print("changing cron...")
        # check to find cron job handling this sensor
        line_number_repeting_cron = -1
        for index in range(0, cron_list_pnl.repeat_cron.GetItemCount()):
            cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
            if "log_dstemp.py" in cmd_path:
                print(" found - " + cmd_path)
                cmd_args = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                if o_loc in cmd_args:
                    print("Located " + o_loc)
                    line_number_repeting_cron = index
        if not line_number_repeting_cron == -1:
            cron_enabled = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 1).GetText()
            cron_task    = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 3).GetText()
            sensor_location = self.temp_sensor_cb.GetValue()
            cron_args_original = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 4).GetText()
            if "sensor=" in cron_args_original:
                sensor_args = cron_args_original.split("sensor=")[1].split(" ")[0]
                if "," in sensor_args:
                    sensor_list = sensor_args.split(",")
                else:
                    sensor_list = [sensor_args]
            else:
                sensor_list = [self.temp_sensor_cb.GetValue()]
            sensor_list_text = ""
            for sensor in sensor_list:
                sensor_list_text += sensor + ","
            sensor_list_text = sensor_list_text[0:-1]
            cron_args    = "log=" + self.log_tc.GetValue() + " sensor=" + sensor_list_text
            cron_comment = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 5).GetText()
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            #print("Cron job; " + "modified" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            cron_list_pnl.repeat_cron.DeleteItem(line_number_repeting_cron)
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'modified', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")
        else:
            print("Job not currently in cron, adding it...")
            cron_enabled = "True"
            cron_task = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/log_dstemp.py"
            cron_args = "log=" + self.log_tc.GetValue() + " sensor=" + self.temp_sensor_cb.GetValue()
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            cron_comment = ""
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            #print("Cron job; " + "new" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")

    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()

class chirp_dialog(wx.Dialog):
    """
    This initializes and reads data from these locations;
          s_name   = MainApp.sensors_info_pannel.sensor_list.s_name
          s_log    = MainApp.sensors_info_pannel.sensor_list.s_log
          s_loc    = MainApp.sensors_info_pannel.sensor_list.s_loc
          s_extra  = MainApp.sensors_info_pannel.sensor_list.s_extra
          s_timing = MainApp.sensors_info_pannel.sensor_list.s_timing
     The final info will be stored as so in the config file;
         pigrow_config.txt
            sensor_chirp01_type=chirp
            sensor_chirp01_log=/home/pi/Pigrow/logs/chirp01.txt
            sensor_chirp01_loc=i2c:0x31
            sensor_chirp01_extra=min:100 max:1000 etc: etc:
     The gui uses it in the sensor table on the sensors tab;
         sensor_table
            0   name = chirp01
            1   type = chirp
            2   log = /home/pi/Pigrow/logs/chirp01.txt
            3   loc = i2c:0x31
            4   extra = min:100 max:1000 etc: etc:etc,etc # split with " " to make lists
                                                       # then settings are split with ":"
        """
    def __init__(self, *args, **kw):
        super(chirp_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 400))
        self.SetTitle("Chirp Sensor Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        self.s_name  = MainApp.sensors_info_pannel.sensor_list.s_name
        self.s_log   = MainApp.sensors_info_pannel.sensor_list.s_log
        self.s_loc   = MainApp.sensors_info_pannel.sensor_list.s_loc
        self.s_extra = MainApp.sensors_info_pannel.sensor_list.s_extra
        self.timing_string = MainApp.sensors_info_pannel.sensor_list.s_timing
        try:
            s_rep     = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[0]
            s_rep_txt = MainApp.sensors_info_pannel.sensor_list.s_timing.split(" ")[1]
        except:
            s_rep = ""
            s_rep_txt = ""
        # Split s_extra into a list called extras
        if " " in self.s_extra:
            extras = self.s_extra.split(" ")
        else:
            extras = [self.s_extra]
        # Sort list of extras for important information
        s_min = ""
        s_max = ""
        extra_extra = ""
        for item in extras:
            if "min:" in item:
                s_min = item.split(":")[1]
                print("found min - " + str(s_min))
            elif "max:" in item:
                s_max = item.split(":")[1]
                print("found max - " + str(s_max))
            else:
                if not item == "":
                    extra_extra += item + ","
        if len(extra_extra) > 0:
            if extra_extra[-1] == ",":
                extra_extra = extra_extra[:-1]
        # split wiring location into wiring type and number
        #                                from e.g. i2c:0x10
        s_loc_a = ""
        s_loc_b = ""
        if ":" in self.s_loc:
            s_loc_a = self.s_loc.split(":")[0]
            s_loc_b = self.s_loc.split(":")[1]
        elif not self.s_loc == "":
            print(" Can't Split the Wiring Location of the Chirp Sensor into pieces ")
            print("     -- " + str(s_loc) + " --")

        #draw the pannel
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Chirp Soil Moisture Sensor', pos=(25, 10))
        wx.StaticText(self,  label='Unique Name', pos=(2, 50))
        wx.StaticText(self,  label='Log Location', pos=(2, 80))
        self.name_tc = wx.TextCtrl(self,  pos=(100, 50), size=(400,30))
        self.log_tc = wx.TextCtrl(self,  pos=(100, 80), size=(400,30))
        # wiring location / address
        wx.StaticText(self,  label='Wired Into', pos=(2, 110))
        wiring_choices = ['i2c', 'others not yet supprted']
        self.wire_type_combo = wx.ComboBox(self, choices = wiring_choices, pos=(100,110), size=(80, 25))
        self.wire_loc_tc = wx.TextCtrl(self,  pos=(200, 110), size=(150,30))
        wx.StaticText(self,  label='e.g. 0x20', pos=(360, 115))
        # min, max
        wx.StaticText(self,  label='Calibration Levels', pos=(2, 145))
        wx.StaticText(self,  label='Min', pos=(145, 145))
        self.min_tc = wx.TextCtrl(self,  pos=(180, 140), size=(100,30))
        wx.StaticText(self,  label='Max', pos=(295, 145))
        self.max_tc = wx.TextCtrl(self,  pos=(330, 140), size=(100,30))
        # extra
        wx.StaticText(self,  label='Extra Info', pos=(2, 170))
        self.extra_tc = wx.TextCtrl(self,  pos=(100, 170), size=(400,30))
        # timing string
        wx.StaticText(self,  label='Repeating every ', pos=(2, 200))
        self.rep_num_tc = wx.TextCtrl(self,  pos=(100, 200), size=(70,30))
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, pos=(170,200), size=(100, 30))
        #
        self.name_tc.SetValue(self.s_name)
        self.log_tc.SetValue(self.s_log)
        self.wire_type_combo.SetValue(s_loc_a)
        self.wire_loc_tc.SetValue(s_loc_b)
        self.min_tc.SetValue(s_min)
        self.max_tc.SetValue(s_max)
        self.extra_tc.SetValue(extra_extra)
        self.rep_num_tc.SetValue(s_rep)
        self.rep_opts_cb.SetValue(s_rep_txt)
        # Buttons
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 250), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.calibrate_btn = wx.Button(self, label='Calibrate', pos=(200, 250), size=(175, 30))
        self.calibrate_btn.Bind(wx.EVT_BUTTON, self.calibrate_click)

    def calibrate_click(self, e):
        #print("oh shit this is gonna get cray-cray")
        warning_messaage =  "Are you sure you want to calibrate this sensor, it'll take ages "
        warning_messaage += "and you'll need to have a glass of water handy. \n\n"
        warning_messaage += "Please make sure nothing else is using the sensor at the same time."
        dbox = wx.MessageDialog(self, warning_messaage, "Calibrate Chirp?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            # running phase one - finding a max value
            instruction_text =  "Chirp Calibration phase 1; \n\n  Make sure the sensor is clean, "
            instruction_text += " place the probe in a glass of water.  This will give us a maximum value."
            instruction_text += "\n\n Once started please be patient, it will take a few min"
            dbox = wx.MessageDialog(self, instruction_text, "Phase one", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                cmd = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/chirp_calibrate.py max chirp_address=" + self.wire_loc_tc.GetValue()
                print (cmd)
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
                # checking to see if they want to use the results
                instruction_text = "Great, we got a value of " + str(out)
                instruction_text+= " do you want to use this value as the maximum?"
                dbox = wx.MessageDialog(self, instruction_text, "Phase one", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                dbox.Destroy()
                if (answer == wx.ID_OK):
                    chirp_max = out.strip()
                    print("They're going to use " + str(chirp_max) + " as the maximum value")
                    self.max_tc.SetValue(chirp_max)
                else:
                    print("bloody waste of time that was then!")
            # running phase two - finding a min value
            instruction_text =  "Chirp Calibration phase 2; \n\n  Make sure the sensor is clean and dry, "
            instruction_text += " place the probe in free air.  This will give us a minimum value."
            instruction_text += "\n\n Once started please be patient, it will take a few min"
            dbox = wx.MessageDialog(self, instruction_text, "Phase two", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                print("ready to run the calibration tool")
                cmd = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/chirp_calibrate.py min chirp_address=" + self.wire_loc_tc.GetValue()
                out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
                # checking to see if they want to use the results
                instruction_text = "Great, we got a value of " + str(out)
                instruction_text+= " do you want to use this value as the minimum?"
                dbox = wx.MessageDialog(self, instruction_text, "Phase two", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                answer = dbox.ShowModal()
                dbox.Destroy()
                if (answer == wx.ID_OK):
                    chirp_min = out.strip()
                    print("They're going to use " + str(chirp_min) + " as the maximum value")
                    self.min_tc.SetValue(chirp_min)
                else:
                    print("bloody waste of time that was then!")

    def ok_click(self, e):
        o_name = self.name_tc.GetValue()
        o_type = "chirp"
        o_log = self.log_tc.GetValue()
        o_loc = self.wire_type_combo.GetValue() + ":" + self.wire_loc_tc.GetValue()
        o_extra = self.make_extra_settings_string()
        new_cron_num = self.rep_num_tc.GetValue()
        new_cron_txt = self.rep_opts_cb.GetValue()
        changed = "probably something"
        if self.s_name == o_name:
            #print("name not changed")
            if self.s_log == o_log:
                #print("log path not changed")
                if self.s_loc == o_loc:
                    #print("wiring location not changed")
                    if self.s_extra == o_extra:
                        #print("extra field not changed")
                        #print("--- no reason to update anything ---")
                        changed = "nothing"
                    else:
                        print(self.s_extra, o_extra)
        new_num = self.rep_num_tc.GetValue()
        new_txt = self.rep_opts_cb.GetValue()
        new_timing_string = str(new_num) + " " + new_txt
        if self.timing_string == new_timing_string and changed == "nothing":
            print(" -- Timing string didn't change or any settings referenced in cron -- ")
        else:
            self.edit_cron_job(o_log, o_loc, new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            print("!-!-!-! CONFIG SETTINGS CHANGED !-!-!-!")
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,o_type,o_log,o_loc,o_extra)
            #print(" MOVE THE LINE ABOVE THIS TO THE CORRECT LOCATION")
            #print(" IT NEEDS TO GO AFTER THE DBOX HAS BEEN CALLED AND PULL THE INFO")
            #print(" SO IT CAN DECIDE IF IT NEEDS TO ADD NEW OR UPDATE THE LINE")
            #print("                    ##yawn##")
            #print("")
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = o_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            #print(MainApp.config_ctrl_pannel.config_dict)
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
        self.Destroy()

    def make_extra_settings_string(self):
        o_min = self.min_tc.GetValue()
        o_max = self.max_tc.GetValue()
        min_max = "min:" + o_min + " max:" + o_max
        extra = min_max + " " + self.extra_tc.GetValue()
        if extra[-1] == " ":
            extra = extra[:-1]
        return extra


    def edit_cron_job(self, o_log, o_loc, job_repeat, job_repnum):
        print("changing cron...")
        # check to find cron job handling this sensor
        line_number_repeting_cron = -1
        for index in range(0, cron_list_pnl.repeat_cron.GetItemCount()):
            cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
            if "log_chirp.py" in cmd_path:
                print(" found - " + cmd_path)
                cmd_args = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                if o_loc[4:] in cmd_args:
                    print("Located " + o_loc)
                    line_number_repeting_cron = index
        if not line_number_repeting_cron == -1:
            cron_enabled = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 1).GetText()
            cron_task    = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 3).GetText()
            args_extra = self.make_extra_settings_string()
            args_extra = args_extra.replace(":","=")
            cron_args = "log=" + self.log_tc.GetValue() + " address=" + self.wire_loc_tc.GetValue() + " " + args_extra
            cron_comment = cron_list_pnl.repeat_cron.GetItem(line_number_repeting_cron, 5).GetText()
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            #print("Cron job; " + "modified" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            cron_list_pnl.repeat_cron.DeleteItem(line_number_repeting_cron)
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'modified', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")
        else:
            print("Job not currently in cron, adding it...")
            cron_enabled = "True"
            cron_task = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/sensors/log_chirp.py"
            args_extra = self.make_extra_settings_string()
            args_extra = args_extra.replace(":","=")
            cron_args = "log=" + self.log_tc.GetValue() + " address=" + self.wire_loc_tc.GetValue() + " " + args_extra
            timing_string = cron_info_pnl.make_repeating_cron_timestring(self, job_repeat, job_repnum)
            cron_comment = ""
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', cron_enabled, timing_string, cron_task, cron_args, cron_comment)
            #print("Cron job; " + "new" + " " + cron_enabled + " " + timing_string + " " + cron_task + " " + cron_args + " " + cron_comment)
            MainApp.cron_info_pannel.update_cron_click("e")

    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()

#
#
## user logs tab
#
#

class user_log_info_pnl(wx.Panel):
    """
    This panel allows users to record their own logs manually, things like watering times and height
    """
    #
    #
    def __init__( self, parent ):
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.TAB_TRAVERSAL )
        # Tab Title
        title_l = wx.StaticText(self,  label='User Log Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Record information and Log variables manually', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)
        user_log_location_l = wx.StaticText(self, label='User log location - ')
        self.user_log_location_tc = wx.TextCtrl(self, value="", size=(450, 30))
        # user notes
        user_notes_title =  wx.StaticText(self,  label='User Notes', size=(300,30))
        user_notes_title.SetFont(shared_data.sub_title_font)
        self.ui_user_notes_list = self.user_notes_list(self, 1)
        # user log
        user_log_title =  wx.StaticText(self,  label='User Log', size=(300,30))
        user_log_title.SetFont(shared_data.sub_title_font)
        self.show_log_cb = wx.CheckBox(self, label='Show')
        self.download_log_cb = wx.CheckBox(self, label='Download')
        self.show_log_cb.SetValue(True)
        self.download_log_cb.SetValue(True)
        self.ui_user_log_list = self.user_log_list(self, 1)
        # user log info and user log field info
        user_info_title =  wx.StaticText(self,  label='Info and User Log Fields;', size=(300,30))
        user_info_title.SetFont(shared_data.sub_title_font)
        new_field_l =  wx.StaticText(self,  label='New User Log Field -')
        self.field_title = wx.TextCtrl(self, -1, "", size=(300,30))
        opts = ["num", "text", "date only"]
        self.user_log_variable_type = wx.ComboBox(self, choices=opts, size=(110, 30), value="num", style=wx.TE_READONLY)
        self.add_field_btn = wx.Button(self, label='Add new field')
        self.add_field_btn.Bind(wx.EVT_BUTTON, self.add_new_user_log_field)
        new_user_note_l =  wx.StaticText(self,  label='Add new user note -')
        self.user_note = wx.TextCtrl(self, -1, "", size=(300,75), style=wx.TE_MULTILINE)
        self.add_user_note_btn = wx.Button(self, label='Add note')
        self.add_user_note_btn.Bind(wx.EVT_BUTTON, self.add_user_note)

        # User Log Input Area
        add_box_title =  wx.StaticText(self,  label='Write to user log;', size=(300,30))
        add_box_title.SetFont(shared_data.sub_title_font)
        item_l =  wx.StaticText(self,  label='Item -', size=(50,30))
        variables = []
        self.user_log_variable_text = wx.ComboBox(self, choices = variables, size=(250, 30), style=wx.TE_READONLY)
        self.user_log_variable_text.Bind(wx.EVT_COMBOBOX, self.user_log_field_select)
        self.user_log_input_text = wx.TextCtrl(self, -1, "text to record", size=(300,100), style=wx.TE_MULTILINE)
        self.user_log_input_num = wx.TextCtrl(self, -1, size=(100,30))
        self.add_to_user_log_btn = wx.Button(self, label='Add to User Log')
        self.add_to_user_log_btn.Bind(wx.EVT_BUTTON, self.add_to_user_log)
        self.add_to_user_log_btn.Disable()


        #Sizers
        user_notes_sizer = wx.BoxSizer(wx.VERTICAL)
        user_notes_sizer.Add(user_notes_title,0, wx.ALL, 3)
        user_notes_sizer.Add(self.ui_user_notes_list,0, wx.ALL, 3)
        add_field_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_field_line_sizer.Add(new_field_l,0, wx.ALL, 3)
        add_field_line_sizer.Add(self.field_title, 0, wx.ALL, 3)
        add_field_line_sizer.Add(self.user_log_variable_type, 0, wx.ALL, 3)
        add_field_line_sizer.Add(self.add_field_btn,0, wx.ALL, 3)
        add_user_note_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_user_note_sizer.Add(new_user_note_l, 0, wx.ALL, 3)
        add_user_note_sizer.Add(self.user_note, 0, wx.ALL, 3)
        add_user_note_sizer.Add(self.add_user_note_btn, 0, wx.ALL, 3)
        info_and_new_field_sizer = wx.BoxSizer(wx.VERTICAL)
        info_and_new_field_sizer.Add(user_info_title, 0, wx.ALL, 3)
        info_and_new_field_sizer.Add(add_field_line_sizer, 0, wx.ALL, 3)
        info_and_new_field_sizer.Add(add_user_note_sizer, 0, wx.ALL, 3)
        user_log_input_item_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_log_input_item_sizer.Add(item_l, 0, wx.ALL, 3)
        user_log_input_item_sizer.Add(self.user_log_variable_text, 0, wx.ALL, 3)
        user_log_checkbox_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_log_checkbox_sizer.Add(self.show_log_cb, 0, wx.ALL, 3)
        user_log_checkbox_sizer.Add(self.download_log_cb, 0, wx.ALL, 3)
        user_log_sizer = wx.BoxSizer(wx.VERTICAL)
        user_log_sizer.Add(user_log_title,0, wx.ALL, 3)
        user_log_sizer.Add(user_log_checkbox_sizer, 0, wx.ALL, 3)
        user_log_sizer.Add(self.ui_user_log_list,0, wx.ALL, 3)
        user_log_input_sizer = wx.BoxSizer(wx.VERTICAL)
        user_log_input_sizer.Add(add_box_title, 0, wx.ALL, 3)
        user_log_input_sizer.Add(user_log_input_item_sizer, 0, wx.ALL, 3)
        user_log_input_sizer.Add(self.user_log_input_num, 0, wx.ALL, 3)
        user_log_input_sizer.Add(self.user_log_input_text, 0, wx.ALL, 3)
        user_log_input_sizer.Add(self.add_to_user_log_btn, 0, wx.ALIGN_RIGHT, 3)
        user_log_2pannel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_log_2pannel_sizer.Add(user_log_input_sizer, 0, wx.ALL, 3)
        user_log_2pannel_sizer.Add(user_log_sizer, 0, wx.ALL, 3)
        user_log_loc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        user_log_loc_sizer.Add(user_log_location_l, 0, wx.ALL, 3)
        user_log_loc_sizer.Add(self.user_log_location_tc, 0, wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(user_log_loc_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(user_notes_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(user_log_2pannel_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(info_and_new_field_sizer, 0, wx.ALL, 3)
        self.SetSizer(main_sizer)

    def user_log_field_select(self, e):
        self.ui_user_log_list.DeleteAllItems()
        show_log = self.show_log_cb.GetValue()
        download_log = self.download_log_cb.GetValue()
        show_log_amount = 100
        # if no local files folder is set then don't bother trying to load and display file
        if localfiles_info_pnl.local_path == "":
            show_log = False
        # Display the log in the list ctrl if option to do so is selected
        if show_log:
            field = self.user_log_variable_text.GetValue()
            if download_log == True:
                try:
                    user_log_loc = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/user_log.txt"
                    MainApp.localfiles_ctrl_pannel.download_file_to_folder(user_log_loc, "logs/user_log.txt")
                    self.download_log_cb.SetValue(False)
                except:
                    pass
            # open local user_log and sort for info
            local_path = localfiles_info_pnl.local_path
            local_user_log = os.path.join(local_path, "logs/", "user_log.txt")
            if os.path.isfile(local_user_log):
                with open(local_user_log, "r") as file:
                    userlog = file.read()
                userlog = userlog.splitlines()
            else:
                userlog = []
            # limit to last X amount of lines (100)
            if len(userlog) > show_log_amount:
                userlog = userlog[-show_log_amount:]
            # cycle through and put into text ctrl
            for line in userlog:
                if "@" in line:
                    line = line.split("@")
                    if line[0] == field:
                        self.ui_user_log_list.InsertItem(0, str(line[2]))
                        self.ui_user_log_list.SetItem(0, 1, str(line[1]))
        # select which type of input to expect
        #self.user_log_type = "num"
        self.user_log_type = None
        for item in MainApp.user_log_ctrl_pannel.field_list:
            if item[0] == field:
                self.user_log_type = item[1]
        if self.user_log_type == None:
            print("This field has no type info")
            self.user_log_type = "text"
        self.user_log_input_text.SetValue("")
        #self.user_log_input_num.SetValue("")
        if self.user_log_type == "num":
            self.user_log_input_num.Show()
            self.user_log_input_text.Hide()
        elif self.user_log_type == "text":
            self.user_log_input_num.Hide()
            self.user_log_input_text.Show()
        elif self.user_log_type == "date only":
            self.user_log_input_text.Hide()
            self.user_log_input_num.Hide()
        MainApp.window_self.Layout()

    def write_to_user_info_file(self, label, text, third_col=""):
        text = text.replace("\n", "  ")
        text = text.replace(">", "~|~")
        line = str(label) + ">" + str(text) + ">" + str(third_col)
        user_log_info = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/user_info.txt"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi('echo "' + line + '" >> ' + user_log_info)
        print(" - Written " + line + " to " + user_log_info)

    def fill_user_log_field_list(self):
        self.user_log_variable_text.Clear()
        MainApp.user_log_ctrl_pannel.read_user_log("fake event")

    def add_user_note(self, e):
        text = self.user_note.GetValue()
        label = "user note"
        date = str(datetime.datetime.now())
        if not text == "":
            self.write_to_user_info_file(label, text, date)
            MainApp.user_log_info_pannel.ui_user_notes_list.InsertItem(0, str(text))
            MainApp.user_log_info_pannel.ui_user_notes_list.SetItem(0, 1, date)

    def add_new_user_log_field(self, e):
        var_type = self.user_log_variable_type.GetValue()
        text = self.field_title.GetValue()
        label = "user field"
        if not text == "":
            self.write_to_user_info_file(label, text, var_type)
            self.fill_user_log_field_list()

    def add_to_user_log(self, e):
        # collect field name from combo box
        variable = self.user_log_variable_text.GetValue() # get from dropdown box selection
        # determine which box to use for the value
        if self.user_log_type == "num":
            message = str(self.user_log_input_num.GetValue()) #get from text control
            if not message.isdigit():
                msg_text = "Value must a number"
                dbox = wx.MessageDialog(self, msg_text, "Error", wx.OK | wx.ICON_ERROR)
                dbox.ShowModal()
                dbox.Destroy()
                return None

        elif self.user_log_type == "text":
            message = self.user_log_input_text.GetValue() #get from text control
        elif self.user_log_type == "date only":
            message = variable
        # find log
        log_location = self.user_log_location_tc.GetValue()
        # remove any awkward characters like newline's and seperators
        single_line_message = ""
        for line in message.splitlines():
            single_line_message += " " + line
        single_line_message == single_line_message.replace("@", "~~at~~")
        # assemble the line to write to the file
        timenow = str(datetime.datetime.now())
        line = variable + "@" + timenow + "@" + single_line_message
        # write line to end of userlog on pi using echo "line" >> user_log.txt
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi('echo "' + line + '" >> ' + log_location)
        # tell the user we done it
        MainApp.status.write_bar("Written - " + line + " - to " + log_location)
        print("Written - " + line + " - to " + log_location)
        # add to the user_log_list list control box
        self.ui_user_log_list.InsertItem(0, str(single_line_message))
        self.ui_user_log_list.SetItem(0, 1, str(timenow))
        self.download_log_cb.SetValue(True)

    class user_notes_list(wx.ListCtrl):
        def __init__(self, parent, id, size=(800,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Note')
            self.InsertColumn(1, 'Date')
            self.SetColumnWidth(0, 550)
            self.SetColumnWidth(1, 250)

    class user_log_list(wx.ListCtrl):
        def __init__(self, parent, id, size=(475,150)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Value')
            self.InsertColumn(1, 'Date')
            self.SetColumnWidth(0, 200)
            self.SetColumnWidth(1, 250)

class user_log_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        top_label = wx.StaticText(self,  label='User Logs')
        #
        self.read_user_log_btn = wx.Button(self, label='Read User Log')
        self.read_user_log_btn.Bind(wx.EVT_BUTTON, self.read_user_log)

        # Sizers
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.read_user_log_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.Add(, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.Add(, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def read_user_log(self, e):
        user_log_loc = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/user_log.txt"
        MainApp.user_log_info_pannel.user_log_location_tc.SetValue(user_log_loc)
        user_log_info_location = "/home/" + pi_link_pnl.target_user + "/Pigrow/logs/user_info.txt"
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi('cat ' + user_log_info_location)
        user_log_info_text = out.splitlines()
        self.field_list = []
        self.user_note_list = []
        for line in user_log_info_text:
            if ">" in line:
                line = line.split(">")
                if line[0] == "user field":
                    if len(line) > 2:
                        self.field_list.append([line[1], line[2]])
                    else:
                        self.field_list.append([line[1], "text"])
                elif line[0] == "user note":
                    if len(line) > 2:
                        self.user_note_list.append([line[1], line[2]])
                    else:
                        self.user_note_list.append([line[1], ""])
        # User notes
        MainApp.user_log_info_pannel.ui_user_notes_list.DeleteAllItems()
        for item in self.user_note_list:
            MainApp.user_log_info_pannel.ui_user_notes_list.InsertItem(0, str(item[0]))
            MainApp.user_log_info_pannel.ui_user_notes_list.SetItem(0, 1, str(item[1]))

        # fiel list in user log dropdown box
        MainApp.user_log_info_pannel.user_log_variable_text.Clear()
        for item in self.field_list:
            MainApp.user_log_info_pannel.user_log_variable_text.Append(item[0])
        MainApp.user_log_info_pannel.add_to_user_log_btn.Enable()
        MainApp.user_log_info_pannel.user_log_input_num.Hide()
        MainApp.user_log_info_pannel.user_log_input_text.Hide()


#
#
## gui control pannels - network link, tab select bar, splash screen
#
#
class pi_link_pnl(wx.Panel):
    #
    # Creates the pannel with the raspberry pi data in it
    # and connects ssh to the pi when button is pressed
    # or allows seeking
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        pi_link_pnl.target_ip = ''
        pi_link_pnl.target_user = ''
        pi_link_pnl.target_pass = ''
        pi_link_pnl.config_location_on_pi = '/home/pi/Pigrow/config/pigrow_config.txt'
        ## the three boxes for pi's connection details, IP, Username and Password
        self.l_ip = wx.StaticText(self,  label='address')
        self.tb_ip = wx.TextCtrl(self)
        self.tb_ip.SetValue("192.168.1.")
        self.l_user = wx.StaticText(self,  label='Username')
        self.tb_user = wx.TextCtrl(self)
        self.tb_user.SetValue("pi")
        self.l_pass = wx.StaticText(self,  label='Password')
        self.tb_pass = wx.TextCtrl(self)
        self.tb_pass.SetValue("raspberry")
        ## link with pi button
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi')
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --')
        ## seek next pi button
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek next')
        self.seek_for_pigrows_btn.Bind(wx.EVT_BUTTON, self.seek_for_pigrows_click)
        ##  sizers
        login_sizer = wx.GridSizer(3, 2, 0, 0)
        login_sizer.AddMany( [(self.l_ip, 0, wx.EXPAND),
            (self.tb_ip, 2, wx.EXPAND),
            (self.l_user, 0, wx.EXPAND),
            (self.tb_user, 2, wx.EXPAND),
            (self.l_pass, 0, wx.EXPAND),
            (self.tb_pass, 2, wx.EXPAND)])
        link_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        link_buttons_sizer.Add(self.link_with_pi_btn, 1, wx.EXPAND)
        link_buttons_sizer.Add(self.seek_for_pigrows_btn, 0, wx.EXPAND)
        link_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        link_text_sizer.Add(self.link_status_text, 1, wx.EXPAND)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(login_sizer, 0, wx.EXPAND)
        main_sizer.Add(link_buttons_sizer, 0, wx.EXPAND)
        main_sizer.Add(link_text_sizer, 0, wx.EXPAND)
        self.SetSizer(main_sizer)

    def __del__(self):
        print("psssst it did that thing, the _del_ one you like so much...")
        pass

    def seek_for_pigrows_click(self, e):
        print("seeking for pigrows...")
        number_of_tries_per_host = 1
        pi_link_pnl.target_ip = self.tb_ip.GetValue()
        pi_link_pnl.target_user = self.tb_user.GetValue()
        pi_link_pnl.target_pass = self.tb_pass.GetValue()
        if pi_link_pnl.target_ip.split(".")[3] == '':
            pi_link_pnl.target_ip = pi_link_pnl.target_ip + '0'
        start_from = pi_link_pnl.target_ip.split(".")[3]
        lastdigits = len(str(start_from))
        hostrange = pi_link_pnl.target_ip[:-lastdigits]
        #Iterate through the ip_to_test and stop when  pigrow is found
        for ip_to_test in range(int(start_from)+1,255):
            host = hostrange + str(ip_to_test)
            pi_link_pnl.target_ip = self.tb_ip.SetValue(host)
            seek_attempt = 1
            log_on_test = False
            while True:
                print(("Trying to connect to " + host))
                try:
                    ssh.connect(host, port=shared_data.ssh_port, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                    MainApp.status.write_bar("Connected to " + host)
                    print(("#sb# Connected to " + host))
                    log_on_test = True
                    box_name = self.get_box_name()
                    MainApp.status.write_bar("Pigrow Found; " + str(box_name))
                    print("#sb# Pigrow Found; " + str(box_name))
                    self.set_link_pi_text(log_on_test, box_name)
                    pi_link_pnl.target_ip = self.tb_ip.GetValue()
                    return box_name #this just exits the loop
                except paramiko.AuthenticationException:
                    MainApp.status.write_bar("Authentication failed when connecting to " + str(host))
                    print(("#sb# Authentication failed when connecting to " + str(host)))
                except Exception as e:
                    MainApp.status.write_bar("Could not SSH to " + host + " because:" + str(e))
                    print(("#sb# Could not SSH to " + host + " because:" + str(e)))
                    seek_attempt += 1
                # check if final attempt and if so stop trying
                if seek_attempt == number_of_tries_per_host + 1:
                    MainApp.status.write_bar("Could not connect to " + host + " Giving up")
                    print(("#sb# Could not connect to " + host + " Giving up"))
                    break #end while loop and look at next host

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            MainApp.status.write_bar("breaking ssh connection")
            print("breaking ssh connection")
            ssh.close()
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.tb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
            self.blank_settings()
            #MainApp.welcome_pannel.Show()
            MainApp.view_pnl.view_cb.SetValue("")
            MainApp.view_pnl.view_combo_go("e")
            MainApp.window_self.Layout()
        else:
            #clear_temp_folder()
            pi_link_pnl.target_ip = self.tb_ip.GetValue()
            pi_link_pnl.target_user = self.tb_user.GetValue()
            pi_link_pnl.target_pass = self.tb_pass.GetValue()
            try:
                ssh.connect(pi_link_pnl.target_ip, port=shared_data.ssh_port, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                MainApp.status.write_bar("Connected to " + pi_link_pnl.target_ip)
                print("#sb# Connected to " + pi_link_pnl.target_ip)
                log_on_test = True
            except Exception as e:
                MainApp.status.write_bar("Failed to log on due to; " + str(e))
                print(("#sb# Failed to log on due to; " + str(e)))
            # IF connected
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)
            MainApp.window_self.Layout()

    def blank_settings(self):
        print("clearing settings")
        # clear system pannel text
        MainApp.system_info_pannel.sys_hdd_total.SetLabel("")
        MainApp.system_info_pannel.sys_hdd_remain.SetLabel("")
        MainApp.system_info_pannel.sys_hdd_used.SetLabel("")
        MainApp.system_info_pannel.sys_pigrow_folder.SetLabel("")
        MainApp.system_info_pannel.sys_os_name.SetLabel("")
        MainApp.system_info_pannel.sys_pigrow_update.SetLabel("")
        MainApp.system_info_pannel.sys_network_name.SetLabel("")
        MainApp.system_info_pannel.available_wifi_list.SetLabel('')
        MainApp.system_info_pannel.wifi_list.SetLabel("")
        MainApp.system_info_pannel.sys_power_status.SetLabel("")
        MainApp.system_info_pannel.sys_camera_info.SetLabel("")
        MainApp.system_info_pannel.sys_pi_revision.SetLabel("")
        MainApp.system_info_pannel.sys_pi_date.SetLabel("")
        MainApp.system_info_pannel.sys_pc_date.SetLabel("")
        MainApp.system_info_pannel.sys_i2c_info.SetLabel("")
        MainApp.system_info_pannel.sys_uart_info.SetLabel("")
        MainApp.system_info_pannel.sys_1wire_info.SetLabel("")
        MainApp.system_ctrl_pannel.i2c_baudrate_btn.Disable()
        MainApp.system_ctrl_pannel.add_1wire_btn.Disable()
        MainApp.system_ctrl_pannel.edit_1wire_btn.Disable()
        MainApp.system_ctrl_pannel.remove_1wire_btn.Disable()
        # clear config ctrl text and tables
        try:
            MainApp.config_ctrl_pannel.dirlocs_dict.clear()
        except:
            pass
        try:
            MainApp.config_ctrl_pannel.config_dict.clear()
        except:
            pass
        try:
            MainApp.config_ctrl_pannel.gpio_dict.clear()
        except:
            pass
        try:
            MainApp.config_ctrl_pannel.gpio_on_dict.clear()
        except:
            pass
        MainApp.config_info_pannel.gpio_table.DeleteAllItems()
        config_info_pnl.boxname_text.SetValue("")
        config_info_pnl.location_text.SetLabel("")
        config_info_pnl.config_text.SetLabel("")
        config_info_pnl.lamp_text.SetLabel("")
        config_info_pnl.dht_text.SetLabel("")
        # clear cron tables
        cron_list_pnl.startup_cron.DeleteAllItems()
        cron_list_pnl.repeat_cron.DeleteAllItems()
        cron_list_pnl.timed_cron.DeleteAllItems()
        # clear local files text and images
        localfiles_info_pnl.cron_info.SetLabel("")
        localfiles_info_pnl.local_path_txt.SetLabel("")
        localfiles_info_pnl.folder_text.SetLabel("") ## check this updates on reconnect
        localfiles_info_pnl.photo_text.SetLabel("")
        localfiles_info_pnl.first_photo_title.SetLabel("")
        localfiles_info_pnl.last_photo_title.SetLabel("")

        blank = wx.Bitmap(220, 220)
        try:
            localfiles_info_pnl.photo_folder_first_pic.SetBitmap(blank)
            localfiles_info_pnl.photo_folder_last_pic.SetBitmap(blank)
        except:
            pass
        # clear local file info
        localfiles_info_pnl.local_path = ""
        localfiles_info_pnl.config_files.DeleteAllItems()
        localfiles_info_pnl.logs_files.DeleteAllItems()
        # graphing tab clear
        graphing_ctrl_pnl.blank_options_ui_elements(MainApp.graphing_ctrl_pannel)
        MainApp.graphing_ctrl_pannel.graph_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.select_script_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.opts_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.pigraph_text.Hide()
        MainApp.graphing_ctrl_pannel.script_text.Hide()
        MainApp.graphing_ctrl_pannel.select_script_cb.Hide()
        MainApp.graphing_ctrl_pannel.get_opts_tb.Hide()
        MainApp.user_log_info_pannel.user_log_variable_text.Clear()
        MainApp.user_log_info_pannel.add_to_user_log_btn.Disable()
        MainApp.window_self.Layout()



    def set_link_pi_text(self, log_on_test, box_name):
        pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(pi_link_pnl.boxname))
            MainApp.view_pnl.view_cb.SetValue("Pigrow Setup")
            MainApp.view_pnl.view_combo_go("e")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
            # Run the functions to fill the pages
            MainApp.cron_info_pannel.read_cron_click("event")
            # MainApp.system_ctrl_pannel.read_system_click("event")
            MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("event")
            MainApp.localfiles_ctrl_pannel.update_local_filelist_click("event")
            # camera config
            MainApp.camconf_info_pannel.seek_cam_configs()
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("No Pigrow config file")
            MainApp.view_pnl.view_cb.SetValue("System Config")
            MainApp.view_pnl.view_combo_go("e")
            MainApp.system_ctrl_pannel.read_system_click("event")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
        MainApp.window_self.Layout()

    def get_box_name(self=None):
        boxname = None
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /home/" + pi_link_pnl.target_user + "/Pigrow/config/pigrow_config.txt | grep box_name")
        if "=" in out:
            boxname = out.strip().split("=")[1]
            MainApp.status.write_bar("Pigrow Found; " + boxname)
            print("#sb# Pigrow Found; " + boxname)
        else:
            MainApp.status.write_bar("Can't read Pigrow name, probably not installed")
            print("#sb# Can't read Pigrow's name ")
        if boxname == '':
            boxname = None
        return boxname

class view_pnl(wx.Panel):
    #
    # Creates the little pannel with the navigation tabs
    # small and simple, it changes which pannels are visible
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((230,200,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        #Showing only completed tabs
        view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'Local Files', 'Timelapse', 'Graphs', 'Sensors', "User Logs"]
        self.view_cb = wx.ComboBox(self, choices = view_opts)
        self.view_cb.Bind(wx.EVT_TEXT, self.view_combo_go)
        # sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.view_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def view_combo_go(self, e):
        display = self.view_cb.GetValue()
        #hide all the pannels
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.config_ctrl_pannel.Hide()
        MainApp.config_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.localfiles_ctrl_pannel.Hide()
        MainApp.localfiles_info_pannel.Hide()
        MainApp.welcome_pannel.Hide()
        MainApp.graphing_ctrl_pannel.Hide()
        MainApp.graphing_info_pannel.Hide()
        MainApp.camconf_ctrl_pannel.Hide()
        MainApp.camconf_info_pannel.Hide()
        MainApp.timelapse_info_pannel.Hide()
        MainApp.timelapse_ctrl_pannel.Hide()
        MainApp.sensors_info_pannel.Hide()
        MainApp.sensors_ctrl_pannel.Hide()
        MainApp.user_log_ctrl_pannel.Hide()
        MainApp.user_log_info_pannel.Hide()
        #show whichever pannels correlate to the option selected
        if display == 'System Config':
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
            if MainApp.system_info_pannel.sys_pi_revision.GetLabel() == "--":
                MainApp.window_self.Layout()
                MainApp.system_ctrl_pannel.read_system_click("event")
        elif display == 'Pigrow Setup':
            MainApp.config_ctrl_pannel.Show()
            MainApp.config_info_pannel.Show()
        elif display == 'Camera Config':
            MainApp.camconf_ctrl_pannel.Show()
            MainApp.camconf_info_pannel.Show()
        elif display == 'Cron Timing':
            MainApp.cron_list_pannel.Show()
            MainApp.cron_info_pannel.Show()
        elif display == 'Multi-script':
            print("changing window display like i'm Mr Polly on coke")
        elif display == 'Local Files':
            MainApp.localfiles_ctrl_pannel.Show()
            MainApp.localfiles_info_pannel.Show()
        elif display == 'Timelapse':
            MainApp.timelapse_info_pannel.Show()
            MainApp.timelapse_ctrl_pannel.Show()
        elif display == 'Graphs':
            MainApp.graphing_ctrl_pannel.Show()
            MainApp.graphing_info_pannel.Show()
        elif display == 'Live View':
            print("changing window display like i'm Mr Polly on LSD")
        elif display == 'pieye watcher':
            print("changing window display like i'm Mr Polly in a daydream")
        elif display == 'Sensors':
            MainApp.sensors_info_pannel.Show()
            MainApp.sensors_ctrl_pannel.Show()
            MainApp.sensors_ctrl_pannel.make_tables_click("e")
        elif display == "User Logs":
            MainApp.user_log_ctrl_pannel.Show()
            MainApp.user_log_info_pannel.Show()
        elif display == "":
            MainApp.welcome_pannel.Show()
        else:
            print("!!! Option not recognised, this is a programming error! sorry")
            print("          message me and tell me about it and i'll be very thankful")
        MainApp.window_self.Layout()


class welcome_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, evt):
        # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("./splash.png")
        dc.DrawBitmap(bmp, 0, 0)

class status_bar(wx.Panel):
    #
    # The bar at the bottom of the screen for displaying the current status
    #
    # #    MainApp.status.write_bar("Status bar normal text")       # normal background with black text
    # #    MainApp.status.write_warning("Status bar warning text")  # red back with black text
    #
    def __init__( self, parent ):
        width_of_window = gui_set.width_of_window
        height_of_window = gui_set.height_of_window
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,150,120)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        self.status_text = wx.StaticText(self,  label='-- starting -- ')
        font = self.GetFont()
        font.SetPointSize(15)
        self.status_text.SetFont(font)
        # sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.status_text, -1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)


    def write_bar(self, text):
        self.SetBackgroundColour((150, 150, 120))
        self.status_text.SetForegroundColour(wx.Colour(50,50,50))
        self.status_text.SetLabel(text)
        wx.GetApp().Yield()
    def write_blue_bar(self, text):
        self.SetBackgroundColour((50, 50, 200))
        self.status_text.SetForegroundColour(wx.Colour(0,0,0))
        self.status_text.SetLabel(text)
        wx.GetApp().Yield()
    def write_warning(self, text):
        self.SetBackgroundColour((200, 100, 100))
        self.status_text.SetForegroundColour(wx.Colour(0,0,0))
        self.status_text.SetLabel(text)
        wx.GetApp().Yield()


class gui_settings:
    #
    # Called as gui_set
    #
    #     fot example use
    #             window_width = gui_set.width_of_window
    #     to return the size of the gui's window
    #
    def __init__( self):
        # Settings Sizes
        self.width_of_window = 1200
        self.height_of_window = 800

        # storing important information extracted from pigrow

        # move MainApp.config_ctrl_pannel.dirlocs_dict to here



#
#
#  The main bit of the program
#           EXCITING HU?!!!?
#
class MainFrame ( wx.Frame ):
    def __init__( self, parent ):
        # Settings
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Pigrow Remote Interface", pos = wx.DefaultPosition, style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.Bind(wx.EVT_SIZE, self.resize_window)

        # always shown pannels
        MainApp.pi_link_pnl = pi_link_pnl(self)
        MainApp.view_pnl = view_pnl(self)
        #
        #Set the local file paths for this computer_username
        self.set_local_options()
        #
        # loads all the pages at the start then hides them,
        #         maybe i should change this later but let's make it work first
        #
        # Auto-Start Pages
        MainApp.welcome_pannel = welcome_pnl(self)
        MainApp.status = status_bar(self)
        MainApp.system_ctrl_pannel = system_ctrl_pnl(self)
        MainApp.system_info_pannel = system_info_pnl(self)
        MainApp.config_ctrl_pannel = config_ctrl_pnl(self)
        MainApp.config_info_pannel = config_info_pnl(self)
        MainApp.cron_list_pannel = cron_list_pnl(self)
        MainApp.cron_info_pannel = cron_info_pnl(self)
        MainApp.localfiles_ctrl_pannel = localfiles_ctrl_pnl(self)
        MainApp.localfiles_info_pannel = localfiles_info_pnl(self)
        MainApp.graphing_ctrl_pannel = graphing_ctrl_pnl(self)
        MainApp.graphing_info_pannel = graphing_info_pnl(self)
        MainApp.camconf_ctrl_pannel = camconf_ctrl_pnl(self)
        MainApp.camconf_info_pannel = camconf_info_pnl(self)
        MainApp.timelapse_info_pannel = timelapse_info_pnl(self)
        MainApp.timelapse_ctrl_pannel = timelapse_ctrl_pnl(self)
        MainApp.sensors_info_pannel = sensors_info_pnl(self)
        MainApp.sensors_ctrl_pannel = sensors_ctrl_pnl(self)
        MainApp.user_log_ctrl_pannel = user_log_ctrl_pnl(self)
        MainApp.user_log_info_pannel = user_log_info_pnl(self)
        #hide all except the welcome pannel
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.config_ctrl_pannel.Hide()
        MainApp.config_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.localfiles_ctrl_pannel.Hide()
        MainApp.localfiles_info_pannel.Hide()
        MainApp.graphing_ctrl_pannel.Hide()
        MainApp.graphing_info_pannel.Hide()
        MainApp.camconf_ctrl_pannel.Hide()
        MainApp.camconf_info_pannel.Hide()
        MainApp.timelapse_info_pannel.Hide()
        MainApp.timelapse_ctrl_pannel.Hide()
        MainApp.sensors_info_pannel.Hide()
        MainApp.sensors_ctrl_pannel.Hide()
        MainApp.user_log_ctrl_pannel.Hide()
        MainApp.user_log_info_pannel.Hide()
        MainApp.status.write_bar("ready...")
        # Sizers
        # left bar
        MainApp.side_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        MainApp.side_bar_sizer.SetMinSize(200,5)
        MainApp.side_bar_sizer.Add(MainApp.pi_link_pnl, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.view_pnl, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.system_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.config_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.cron_info_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.localfiles_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.graphing_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.camconf_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.timelapse_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.sensors_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.user_log_ctrl_pannel, 0, wx.EXPAND)
        # main AREA
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(MainApp.side_bar_sizer, 0)
        main_sizer.Add(MainApp.welcome_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.system_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.config_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.cron_list_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.localfiles_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.graphing_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.camconf_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.timelapse_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.sensors_info_pannel, 0, wx.EXPAND)
        main_sizer.Add(MainApp.user_log_info_pannel, 0, wx.EXPAND)
        MainApp.window_sizer = wx.BoxSizer(wx.VERTICAL)
        MainApp.window_sizer.Add(main_sizer, 0, wx.EXPAND)
        MainApp.window_sizer.Add(MainApp.status, 1, wx.EXPAND)
        MainApp.window_sizer.Fit(self)
        self.SetSizer(MainApp.window_sizer)
        MainApp.window_self = self
        # setup the window layout
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.Layout()
        self.Centre( wx.BOTH )

    def resize_window(self, e):
        win_width = e.GetSize()[0]
        win_height = e.GetSize()[1]
        w_space_left = win_width - 285
        size = wx.Size(win_width, win_height-75)
        #self.SetMinSize(size)
        MainApp.system_info_pannel.SetMinSize(size)
        MainApp.config_info_pannel.SetMinSize(size)
        MainApp.cron_list_pannel.SetMinSize(size)
        MainApp.localfiles_info_pannel.SetMinSize(size)
        MainApp.graphing_info_pannel.SetMinSize(size)
        MainApp.camconf_info_pannel.SetMinSize(size)
        MainApp.timelapse_info_pannel.SetMinSize(size)
        MainApp.sensors_info_pannel.SetMinSize(size)
        MainApp.user_log_info_pannel.SetMinSize(size)
        MainApp.welcome_pannel.SetMinSize(size)

        try:
            MainApp.window_self.Layout()
        except:
            pass #to avoid the error on first init
        MainApp.graphing_info_pannel.SetupScrolling()


    def __del__( self ):
        pass

class MainApp(MainFrame):
    def __init__(self, parent):
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, e):
        #Closes SSH connection even on quit
        # need to add 'ya sure?' question if there's unsaved data
        print("Closing SSH connection")
        ssh.close()
        sys.exit(0)

    def set_local_options(self):
        try:
            MainApp.OS =  platform.system()
            if MainApp.OS == "Linux":
                computer_username = os.getlogin()
                localpath = os.path.join("/home", computer_username)
                localpath = os.path.join(localpath, "frompigrow")
                MainApp.localfiles_path = localpath
            else:
                localpath = os.getcwd()
                localpath = os.path.join(localpath, "frompigrow")
                MainApp.localfiles_path = localpath
        except:
            localpath = os.getcwd()
            localpath = os.path.join(localpath, "frompigrow")
            MainApp.localfiles_path = localpath


def main():
    app = wx.App()
    shared_data()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    gui_set = gui_settings()
    try:
        # if run from a desktop icon or something
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    main()
