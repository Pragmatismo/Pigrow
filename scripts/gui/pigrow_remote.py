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
#    graphing_info_pnl
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
import platform
import time
import datetime
import numpy as np
from stat import S_ISDIR
try:
    import wx
    import wx.adv
    import  wx.lib.scrolledpanel as scrolled
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
        sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizerAndFit(sizer)
    def ok_click(self, e):
        scroll_text_dialog.text = self.text.GetValue()
        self.Destroy()

class show_image_dialog(wx.Dialog):
    def __init__(self, parent,  image_to_show, title):
        wx.Dialog.__init__(self, parent, title=(title))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticBitmap(self, -1, image_to_show))
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

#
#
## System Pannel
#
#
class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        sub_title_font = wx.Font(13, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.tab_label = wx.StaticText(self,  label='System Config Menu')
        self.pigrow_side_label = wx.StaticText(self,  label='Pigrow Software')
        self.system_side_label = wx.StaticText(self,  label='System')
        self.i2c_side_label = wx.StaticText(self,  label='I2C')
        self.onewire_side_label = wx.StaticText(self,  label='1Wire')
        self.tab_label.SetFont(sub_title_font)
        self.pigrow_side_label.SetFont(sub_title_font)
        self.system_side_label.SetFont(sub_title_font)
        self.i2c_side_label.SetFont(sub_title_font)
        self.onewire_side_label.SetFont(sub_title_font)
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
        main_sizer.Add(self.edit_1wire_btn, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        main_sizer.Add(self.remove_1wire_btn, 0, wx.ALL|wx.ALIGN_RIGHT, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

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
        system_info_pnl.sys_1wire_info.SetLabel(final_1wire_text)
        MainApp.window_self.Layout()

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
            folder = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/temp/"
            f = sftp.open(folder + 'boot_config.txt', 'w')
            f.write(config_text)
            f.close()
            copy_cmd = "sudo mv /home/" + pi_link_pnl.target_user + "/Pigrow/temp/boot_config.txt /boot/config.txt"
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(copy_cmd)
            print(out, error)
            print("Pi's /boot/config,txt file changed")
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
            system_info_pnl.sys_i2c_info.SetLabel("i2c bus not found")
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
        system_info_pnl.sys_i2c_info.SetLabel(i2c_text)
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
            i2c_text = system_info_pnl.sys_i2c_info.GetLabel().split("\n")[0]
            if len(i2c_addresses) > 0:
                i2c_text += "\nfound " + str(len(i2c_addresses)) + " devices at; " + str(i2c_addresses)
            else:
                i2c_text += "\nNo devices found"
            system_info_pnl.sys_i2c_info.SetLabel(i2c_text)
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
            system_info_pnl.sys_pigrow_update.SetLabel("update required, " + str(git_num) + " updates behind")
            update_type = "clean"
        elif update_needed == False:
            system_info_pnl.sys_pigrow_update.SetLabel("master branch is upto date")
            update_type = "none"
        elif update_needed == 'ahead':
            system_info_pnl.sys_pigrow_update.SetLabel("Caution Required!\nYou modified your Pigrow code")
            update_type = "merge"
        elif update_needed == 'diverged':
            system_info_pnl.sys_pigrow_update.SetLabel("Caution Required!\nYou modified your Pigrow code")
            update_type = "merge"
        elif update_needed == 'error':
            if install_needed == True:
                system_info_pnl.sys_pigrow_update.SetLabel("Pigrow folder not found.")
                update_type = "error"
        else:
            system_info_pnl.sys_pigrow_update.SetLabel("Some confusion with git, sorry.")
            update_type = "error"
        return update_type

    def check_pi_power_warning(self):
        #check for low power WARNING
        # this only works on certain versions of the pi
        # it checks the power led value
        # it's normally turned off as a LOW POWER warning
        if not "pi 3" in system_info_pnl.sys_pi_revision.GetLabel().lower():
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /sys/class/leds/led1/brightness")
            if out == "255":
                system_info_pnl.sys_power_status.SetLabel("no warning")
            elif out == "" or out == None:
                system_info_pnl.sys_power_status.SetLabel("error, not supported")
            else:
                system_info_pnl.sys_power_status.SetLabel("reads " + str(out) + " low power warning!")
        else:
            system_info_pnl.sys_power_status.SetLabel("feature disabled on pi 3")

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
        # camera info
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/video*")
        if "No such file or directory" in error:
            cam_text = "No camera detected"
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
                            cam_name = "possibly picam?"
                        else:
                            cam_name = out.split("=")[1].strip()
                            cam_text = cam_name + "\n       on " + cam + "\n"
            except:
                print("probably a picam")
                cam_text = "possibly a pi cam is connected?"
        return cam_text

    def get_pi_time_diff(self):
        # just asks the pi the data at the same time grabs local datetime
        # returns to the user as strings
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("date")
        local_time = datetime.datetime.now()
        local_time_text = local_time.strftime("%a %d %b %X") + " " + str(time.tzname[0]) + " " + local_time.strftime("%Y")
        pi_time = out.strip()
        return local_time_text, out
    # buttons
    def read_system_click(self, e):
        ### pi system interrogation
        # disk space
        hdd_total, hdd_percent, hdd_available, hdd_used = self.check_pi_diskspace()
        system_info_pnl.sys_hdd_total.SetLabel(str(hdd_total) + " KB")
        system_info_pnl.sys_hdd_remain.SetLabel(str(hdd_available) + " KB")
        system_info_pnl.sys_hdd_used.SetLabel(str(hdd_used) + " KB (" + str(hdd_percent) + ")")
        # installed OS
        os_name = self.check_pi_os()
        system_info_pnl.sys_os_name.SetLabel(os_name)
        # check if pigrow folder exits and read size
        pigrow_size, folder_pcent = self.check_for_pigrow_folder(hdd_used)
        if pigrow_size == "not found":
            system_info_pnl.sys_pigrow_folder.SetLabel("Pigrow folder now found")
        else:
            system_info_pnl.sys_pigrow_folder.SetLabel(str(pigrow_size) + " KB (" +str(folder_pcent) + "% of used)")
        # check if git upate needed
        self.check_git() #ugly and deals with UI itself, needs upgrade and clean but git is a headfuck so like oneday...
        # pi board revision
        pi_version = self.check_pi_version()
        system_info_pnl.sys_pi_revision.SetLabel(pi_version)
        # check for low power warning
        self.check_pi_power_warning()
        # WIFI
        network_name = self.find_network_name()
        system_info_pnl.sys_network_name.SetLabel(network_name)
        network_text = self.find_added_wifi()
        system_info_pnl.wifi_list.SetLabel(network_text)
        # camera info
        camera_names = self.find_connected_webcams()
        system_info_pnl.sys_camera_info.SetLabel(camera_names)
        # datetimes and difference
        local_time, pi_time = self.get_pi_time_diff()
        system_info_pnl.sys_pi_date.SetLabel(pi_time)
        system_info_pnl.sys_pc_date.SetLabel(str(local_time))
        # GPIO info pannel
        self.i2c_check()

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
        main_sizer.Add(header, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(self.config_text, 0, wx.EXPAND|wx.ALL, 3)
        main_sizer.Add(post, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title = wx.StaticText(self,  label='Change 1wire Pin')
        title.SetFont(title_font)
        sub_text = wx.StaticText(self,  label="Editing the /boot/config.txt file's \ndtoverlay=w1-gpio,gpiopin= lines")
        sub_text.SetFont(sub_title_font)
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
        buttons_sizer.Add(self.ok_btn, 0, wx.ALIGN_LEFT, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALIGN_RIGHT, 2)
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
        old_line = "dtoverlay=w1-gpio,gpiopin=" + self.tochange_gpiopin_cb.GetValue()
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title = wx.StaticText(self,  label='Remove 1wire Pin')
        title.SetFont(title_font)
        sub_text = wx.StaticText(self,  label="Editing the /boot/config.txt file and removing \n the selected dtoverlay=w1-gpio,gpiopin= line")
        sub_text.SetFont(sub_title_font)
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
        buttons_sizer.Add(self.ok_btn, 0, wx.ALIGN_LEFT, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALIGN_RIGHT, 2)
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
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        # Tab Title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='System Control Panel', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Configure the raspberry pi on which the pigrow code runs', size=(550,30))
        page_sub_title.SetFont(sub_title_font)
        # placing the information boxes
        item_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        # base system info (Top - Left) Sizer Pannel
        # Raspberry Pi revision
        pi_rev_l = wx.StaticText(self,  label='Hardware -')
        system_info_pnl.sys_pi_revision = wx.StaticText(self,  label='-raspberry pi version-')
        #SDcard details
        storage_space_l = wx.StaticText(self,  label='Storage Space', size=(25,25))
        storage_space_l.SetFont(item_title_font)
        total_hdd_l = wx.StaticText(self,  label='Total  -')
        system_info_pnl.sys_hdd_total = wx.StaticText(self,  label='-total -')
        free_hdd_l = wx.StaticText(self,  label='Free  -')
        system_info_pnl.sys_hdd_remain = wx.StaticText(self,  label='-free -')
        used_hdd_l = wx.StaticText(self,  label='Used  -')
        system_info_pnl.sys_hdd_used = wx.StaticText(self,  label='-Used-')
        pigrow_folder_hdd_l = wx.StaticText(self,  label='Pigrow folder -')
        system_info_pnl.sys_pigrow_folder = wx.StaticText(self,  label='-Pigrow folder-')
        #Software details
        system_l = wx.StaticText(self,  label='System', size=(25,25))
        system_l.SetFont(item_title_font)
        system_info_pnl.sys_pigrow_update = wx.StaticText(self,  label='-Pigrow update status-')
        os_name_l = wx.StaticText(self,  label='OS installed -')
        system_info_pnl.sys_os_name = wx.StaticText(self,  label='-os installed-')
        pigrow_l = wx.StaticText(self,  label='Pigrow', size=(25,25))
        pigrow_l.SetFont(item_title_font)
        update_status_l = wx.StaticText(self,  label='Update Status -')
        #power level warning details
        power_l = wx.StaticText(self,  label='Power', size=(25,25))
        power_l.SetFont(item_title_font)
        power_status_l = wx.StaticText(self,  label='Power Warning -')
        system_info_pnl.sys_power_status = wx.StaticText(self,  label='-power status-')
        # Pi datetime vs local pc datetime
        time_l = wx.StaticText(self,  label='Date and Time', size=(25,25))
        time_l.SetFont(item_title_font)
        pi_time_l = wx.StaticText(self,  label='Time on Pi -')
        system_info_pnl.sys_pi_date = wx.StaticText(self,  label='-datetime on pi-')
        local_time_l = wx.StaticText(self,  label='Time on local pc -')
        system_info_pnl.sys_pc_date = wx.StaticText(self,  label='-datetime on local pc-')
        # peripheral hardware (top-right)
        #camera details
        camera_title_l = wx.StaticText(self,  label='Camera', size=(25,25))
        camera_title_l.SetFont(item_title_font)
        camera_l = wx.StaticText(self,  label='Detected -')
        system_info_pnl.sys_camera_info = wx.StaticText(self,  label='-camera info-')
        # GPIO set up details
        gpio_overlay_l = wx.StaticText(self,  label='GPIO Overlays', size=(25,25))
        gpio_overlay_l.SetFont(item_title_font)
        i2c_l = wx.StaticText(self,  label='I2C -')
        system_info_pnl.sys_i2c_info = wx.StaticText(self,  label='-i2c info-')
        uart_l = wx.StaticText(self,  label='UART -')
        system_info_pnl.sys_uart_info = wx.StaticText(self,  label='-uart info (not implimented)-')
        onewire_l = wx.StaticText(self,  label='1 Wire -')
        system_info_pnl.sys_1wire_info = wx.StaticText(self,  label='-1 wire info-')

        # network pannel - lower half
        #wifi deatils
        network_l = wx.StaticText(self,  label='Network', size=(90,30))
        network_l.SetFont(item_title_font)
        current_network_l = wx.StaticText(self,  label='Connected to -')
        system_info_pnl.sys_network_name = wx.StaticText(self,  label='-network name-')
        saved_wifi_l = wx.StaticText(self,  label='Saved Wifi Networks')
        system_info_pnl.wifi_list = wx.StaticText(self,  label='-wifi list-')
        found_wifi_l = wx.StaticText(self,  label='Found Wifi Networks')
        system_info_pnl.available_wifi_list = wx.StaticText(self,  label='-feature not implimented-')
        #
        # Sizers
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        # base system info (Top - Left) Sizer Pannel
        hardware_version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hardware_version_sizer.Add(pi_rev_l, 0, wx.ALL, 3)
        hardware_version_sizer.Add(system_info_pnl.sys_pi_revision, 0, wx.ALL|wx.EXPAND, 3)
        total_hdd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        total_hdd_sizer.Add(total_hdd_l, 0, wx.ALL|wx.EXPAND, 3)
        total_hdd_sizer.Add(system_info_pnl.sys_hdd_total, 0, wx.ALL|wx.EXPAND, 3)
        free_hdd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        free_hdd_sizer.Add(free_hdd_l, 0, wx.ALL|wx.EXPAND, 3)
        free_hdd_sizer.Add(system_info_pnl.sys_hdd_remain, 0, wx.ALL|wx.EXPAND, 3)
        used_hdd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        used_hdd_sizer.Add(used_hdd_l, 0, wx.ALL|wx.EXPAND, 3)
        used_hdd_sizer.Add(system_info_pnl.sys_hdd_used, 0, wx.ALL|wx.EXPAND, 3)
        pigrow_folder_hdd_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pigrow_folder_hdd_sizer.Add(pigrow_folder_hdd_l, 0, wx.ALL|wx.EXPAND, 3)
        pigrow_folder_hdd_sizer.Add(system_info_pnl.sys_pigrow_folder, 0, wx.ALL|wx.EXPAND, 3)
        update_status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        update_status_sizer.Add(update_status_l, 0, wx.ALL, 3)
        update_status_sizer.Add(system_info_pnl.sys_pigrow_update, 0, wx.ALL|wx.EXPAND, 3)
        os_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        os_name_sizer.Add(os_name_l, 0, wx.ALL, 3)
        os_name_sizer.Add(system_info_pnl.sys_os_name, 0, wx.ALL|wx.EXPAND, 3)
        power_status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_status_sizer.Add(power_status_l, 0, wx.ALL, 3)
        power_status_sizer.Add(system_info_pnl.sys_power_status, 0, wx.ALL|wx.EXPAND, 3)
        pi_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pi_time_sizer.Add(pi_time_l, 0, wx.ALL, 3)
        pi_time_sizer.Add(system_info_pnl.sys_pi_date, 0, wx.ALL|wx.EXPAND, 3)
        pc_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pc_time_sizer.Add(local_time_l, 0, wx.ALL, 3)
        pc_time_sizer.Add(system_info_pnl.sys_pc_date, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer = wx.BoxSizer(wx.VERTICAL)
        base_system_info_sizer.Add(system_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(hardware_version_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(os_name_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(pigrow_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(update_status_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(storage_space_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(total_hdd_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(free_hdd_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(used_hdd_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(pigrow_folder_hdd_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(power_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(power_status_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(time_l, 0, wx.ALL|wx.EXPAND, 3)
        base_system_info_sizer.Add(pi_time_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        base_system_info_sizer.Add(pc_time_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        # peripheral hardware (top-right)
        peripheral_device_sizer = wx.BoxSizer(wx.VERTICAL)
        peripheral_device_sizer.Add(camera_title_l, 0, wx.ALL|wx.EXPAND, 3)
        cam_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cam_name_sizer.Add(camera_l, 0, wx.ALL, 3)
        cam_name_sizer.Add(system_info_pnl.sys_camera_info, 0, wx.ALL|wx.EXPAND, 3)
        peripheral_device_sizer.Add(cam_name_sizer, 0, wx.LEFT|wx.EXPAND, 30)
        peripheral_device_sizer.Add(gpio_overlay_l, 0, wx.ALL|wx.EXPAND, 3)

        i2c_sizer = wx.BoxSizer(wx.HORIZONTAL)
        i2c_sizer.Add(i2c_l, 1, wx.ALIGN_RIGHT)
        i2c_sizer.Add(system_info_pnl.sys_i2c_info, 3, wx.EXPAND)
        uart_sizer = wx.BoxSizer(wx.HORIZONTAL)
        uart_sizer.Add(uart_l, 1, wx.ALIGN_RIGHT)
        uart_sizer.Add(system_info_pnl.sys_uart_info, 3, wx.EXPAND)
        onewire_sizer = wx.BoxSizer(wx.HORIZONTAL)
        onewire_sizer.Add(onewire_l, 1, wx.ALIGN_RIGHT)
        onewire_sizer.Add(system_info_pnl.sys_1wire_info, 3, wx.EXPAND)
        peripheral_device_sizer.Add(i2c_sizer, 0, wx.LEFT, 30)
        peripheral_device_sizer.Add(uart_sizer, 0, wx.LEFT, 30)
        peripheral_device_sizer.Add(onewire_sizer, 0, wx.LEFT, 30)
        panel_area_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_area_sizer.Add(base_system_info_sizer, 0, wx.ALL, 0)
        panel_area_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        panel_area_sizer.Add(peripheral_device_sizer, 0, wx.ALL, 0)
        # wifi area sizers
        current_network_sizer = wx.BoxSizer(wx.HORIZONTAL)
        current_network_sizer.Add(current_network_l, 0, wx.LEFT, 3)
        current_network_sizer.Add(system_info_pnl.sys_network_name, 0, wx.LEFT, 30)
        wifi_area_sizer = wx.BoxSizer(wx.VERTICAL)
        wifi_area_sizer.Add(network_l, 0, wx.ALL, 0)
        saved_wifi_sizer = wx.BoxSizer(wx.VERTICAL)
        saved_wifi_sizer.Add(saved_wifi_l, 0, wx.ALL, 5)
        saved_wifi_sizer.Add(system_info_pnl.wifi_list, 0, wx.LEFT, 30)
        found_wifi_sizer = wx.BoxSizer(wx.VERTICAL)
        found_wifi_sizer.Add(found_wifi_l, 0, wx.ALL, 5)
        found_wifi_sizer.Add(system_info_pnl.available_wifi_list, 0, wx.LEFT, 30)
        wifi_panels_sizer = wx.BoxSizer(wx.HORIZONTAL)
        wifi_panels_sizer.Add(saved_wifi_sizer, 0, wx.ALL, 20)
        wifi_panels_sizer.Add(found_wifi_sizer, 0, wx.ALL, 20)
        wifi_area_sizer.Add(current_network_sizer, 0, wx.LEFT, 30)
        wifi_area_sizer.Add(wifi_panels_sizer, 0, wx.ALL, 0)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(panel_area_sizer, 0, wx.ALL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(wifi_area_sizer, 0, wx.ALL, 7)
        self.SetSizer(main_sizer)

class upgrade_pigrow_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(upgrade_pigrow_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 600))
        self.SetTitle("Upgrade Pigrow")
    def InitUI(self):
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        info_font = wx.Font(16, wx.MODERN, wx.ITALIC, wx.NORMAL)
        # draw the pannel and text
        pnl = wx.Panel(self)
        title = wx.StaticText(self,  label='Upgrade Pigrow')
        sub_title = wx.StaticText(self,  label='Use GIT to update the Pigrow to the newest version.')
        title.SetFont(title_font)
        sub_title.SetFont(sub_title_font)
        # see which files are changed locally
        local_l = wx.StaticText(self,  label='Local;')
        local_l.SetFont(sub_title_font)
        local_changes_tb = wx.StaticText(self,  label='--')
        changes = self.read_git_dif()
        local_changes_tb.SetLabel(str(changes))
        # see which files are changed remotely
        repo_l = wx.StaticText(self,  label='Repo;')
        repo_l.SetFont(sub_title_font)
        remote_changes_tb = wx.StaticText(self,  label='--')
        repo_changes, num_repo_changed_files = self.read_repo_changes()
        remote_changes_tb.SetLabel(repo_changes)
        # upgrade type
        pigrow_status = wx.StaticText(self,  label='Pigrow Status;')
        pigrow_status.SetFont(sub_title_font)
        upgrade_type = self.determine_upgrade_type(repo_changes)
        upgrade_type_tb = wx.StaticText(self,  label=upgrade_type)
        if upgrade_type == "behind":
            upgrade_type_tb.SetForegroundColour((255,75,75))
        elif upgrade_type == "up-to-date":
            upgrade_type_tb.SetForegroundColour((25,150,25))
        upgrade_type_tb.SetFont(info_font)
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
        local_sizer.Add(local_changes_tb, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 4)
        remote_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remote_sizer.Add(repo_l, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        remote_sizer.Add(remote_changes_tb, 0, wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, 4)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upgrade_btn, 0, wx.ALIGN_LEFT, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALIGN_RIGHT, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(upgrade_type_sizer, 0, wx.TOP, 15)
        main_sizer.Add(remote_sizer, 0, wx.TOP, 25)
        main_sizer.Add(local_sizer, 0, wx.TOP, 10)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL, 3)
        self.SetSizer(main_sizer)


    # git diff --name-only HEAD@{0} HEAD@{1}      #shows the most recent changes

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
        display_text = str(num_files_changed) + " Files changed;"
        for item in changed_files:
            display_text += "\n     " + str(item)
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
                    system_info_pnl.sys_pigrow_update.SetLabel("--UPDATE ERROR--\n" + error)
                else:
                    system_info_pnl.sys_pigrow_update.SetLabel("--UPDATED--")
                self.Destroy()

class install_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(install_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 600))
        self.SetTitle("Install Pigrow")
    def InitUI(self):
        pnl = wx.Panel(self)
        # Header
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        header_title = wx.StaticText(self,  label='Install Pigrow')
        header_sub = wx.StaticText(self,  label='Tool for installing pigrow code and dependencies')
        header_title.SetFont(title_font)
        header_sub.SetFont(sub_title_font)
        # Installed components
        # Core
        label_core = wx.StaticText(self,  label='Core components;')
        label_core.SetFont(sub_title_font)
        self.pigrow_base_check = wx.CheckBox(self,  label='Pigrow base')
        self.pigrow_dirlocs_check = wx.CheckBox(self,  label='Locations File')
        self.cron_check = wx.CheckBox(self,  label='crontab')
        # sensors
        label_sensors = wx.StaticText(self,  label='Sensors;')
        label_sensors.SetFont(sub_title_font)
        self.adaDHT_check = wx.CheckBox(self,  label='Adafruit_DHT')
        self.ada1115_check = wx.CheckBox(self,  label='Adafruit ADS1115')
        # Camera
        label_camera = wx.StaticText(self,  label='Camera;')
        label_camera.SetFont(sub_title_font)
        self.uvccapture_check = wx.CheckBox(self,  label='uvccapture')
        # Visualisation
        label_visualisation = wx.StaticText(self,  label='Visualisation;')
        label_visualisation.SetFont(sub_title_font)
        self.matplotlib_check = wx.CheckBox(self,  label='Matplotlib')
        self.mpv_check = wx.CheckBox(self,  label='mpv')
        # Networking
        label_networking = wx.StaticText(self,  label='Networking;')
        label_networking.SetFont(sub_title_font)
        self.praw_check = wx.CheckBox(self,  label='praw')
        self.sshpass_check = wx.CheckBox(self,  label='sshpass')
        self.pexpect_check = wx.CheckBox(self,  label='pexpect')
        #status text
        self.currently_doing_l = wx.StaticText(self,  label="Currently:")
        self.currently_doing = wx.StaticText(self,  label='...')
        self.progress = wx.StaticText(self,  label='...')

        #ok and cancel buttons
        self.start_btn = wx.Button(self, label='Start', size=(175, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        # sizers
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer.Add(header_title, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)
        header_sizer.Add(header_sub, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3)
        base_sizer = wx.BoxSizer(wx.VERTICAL)
        base_sizer.Add(label_core, 0, wx.EXPAND|wx.ALL, 3)
        base_sizer.Add(self.pigrow_base_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.pigrow_dirlocs_check, 0, wx.EXPAND|wx.LEFT, 30)
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
        visualisation_sizer.Add(self.mpv_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer = wx.BoxSizer(wx.VERTICAL)
        networking_sizer.Add(label_networking, 0, wx.EXPAND|wx.ALL, 3)
        networking_sizer.Add(self.praw_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.sshpass_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.pexpect_check, 0, wx.EXPAND|wx.LEFT, 30)

        status_text_sizer = wx.BoxSizer(wx.VERTICAL)
        status_text_sizer.Add(self.currently_doing_l, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.currently_doing, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.progress, 0, wx.EXPAND|wx.ALL, 3)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.start_btn, 0,  wx.ALIGN_LEFT, 3)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALIGN_RIGHT, 3)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(base_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(sensor_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(camera_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(visualisation_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(networking_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(status_text_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 2)
        self.SetSizer(main_sizer)





        #run initial checks
        wx.Yield() #update screen to show changes
        if not pi_link_pnl.get_box_name() == None:
            self.pigrow_base_check.SetForegroundColour((75,200,75))
        else:
            self.pigrow_base_check.SetForegroundColour((255,75,75))
            self.pigrow_base_check.SetValue(True)
        self.check_dirlocs()
        self.check_python_dependencies()
        self.check_python3_dependencies()
        wx.Yield() #update screen to show changes
        self.check_program_dependencies()

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
        self.pigrow_base_check.SetValue(True)
        return False



    def install_pigrow(self):
        print(" Cloning git repo onto pi")
        self.currently_doing.SetLabel("using git to clone (download) pigrow code")
        self.progress.SetLabel("####~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
        print(out, error)
        self.currently_doing.SetLabel("creating empty folders")
        self.progress.SetLabel("#####~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/caps/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/graphs/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/logs/")
        wx.Yield()

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
        print(" - uploaded new dirlocs to pigrow config folder")

    def update_pip(self):
        # update pip the python package manager
        self.currently_doing.SetLabel("Updating PIP the python install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install -U pip")
        print (out)

    def update_pip3(self):
        # update pip the python package manager
        self.currently_doing.SetLabel("Updating PIP the python3 install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install -U pip")
        print (out)

    def install_praw(self):
        # praw is the module for connecting to reddit
        self.currently_doing.SetLabel("Using pip3 to install praw")
        self.progress.SetLabel("###########~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip3 install praw")
        print (out)

    def install_pexpect(self):
        # pexpect is the tool used to connect to other pigrows if using pigrow log
        self.currently_doing.SetLabel("using pip to install pexpect")
        self.progress.SetLabel("#############~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install pexpect")
        print (out)

    def install_adafruit_DHT(self):
        print("starting adafruit install")
        self.progress.SetLabel("###############~~~~~~~~~~~~~~")
        self.currently_doing.SetLabel("Using pip to install adafruit_DHT module")
        wx.Yield()
        adafruit_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install Adafruit_DHT")
        print (adafruit_install)

    def install_adafruit_ads1115(self):
        print("starting adafruit install")
        self.progress.SetLabel("################~~~~~~~~~~~~~")
        self.currently_doing.SetLabel("Using pip3 to install adafruit's ADS1x15 driver")
        wx.Yield()
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
        self.currently_doing.SetLabel("updating apt the system package manager on the raspberry pi")
        self.progress.SetLabel("################~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get update --yes")
        print (out, error)

    def install_uvccaptre(self):
        self.currently_doing.SetLabel("Using apt to install uvccaptre")
        self.progress.SetLabel("####################~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install uvccapture")
        print (out, error)

    def install_mpv(self):
        self.currently_doing.SetLabel("Using apt to install mpv")
        self.progress.SetLabel("#####################~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install mpv")
        print (out, error)

    def install_python_matplotlib(self):
        self.currently_doing.SetLabel("Using apt to install python-matplotlib")
        self.progress.SetLabel("######################~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install python-matplotlib")
        print (out, error)

    def install_sshpass(self):
        self.currently_doing.SetLabel("Using apt to install sshpass")
        self.progress.SetLabel("#######################~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install sshpass")
        print (out, error)

    def install_python_crontab(self):
        self.currently_doing.SetLabel("Using apt to install python-crontab")
        self.progress.SetLabel("########################~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get --yes install python-crontab")
        print (out, error)

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
        wx.Yield()
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

    def start_click(self, e):
        print("Install process started;")
        self.progress.SetLabel("##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        # Base installed via Git Clone
        if self.pigrow_base_check.GetValue() == True:
            self.install_pigrow()
            self.progress.SetLabel("#####~~~~~~~~~~~~~~~~~~~~~~~~~~")
            wx.Yield()
        # make dirlocs with pi's username
        if self.pigrow_dirlocs_check.GetValue() == True:
            self.create_dirlocs_from_template()
            self.currently_doing.SetLabel("-")
            self.progress.SetLabel("########~~~~~~~~~~~~~~~~~~~~~~~")
            wx.Yield()
        # Dependencies installed using pip
        if self.pexpect_check.GetValue() == True or self.adaDHT_check.GetValue() == True:
            self.update_pip()
        if self.pexpect_check.GetValue() == True:
            self.install_pexpect()
        if self.adaDHT_check.GetValue() == True:
            self.install_adafruit_DHT()
        # installed using update_pip3
        if self.ada1115_check.GetValue() == True or self.praw_check.GetValue() == True:
            self.update_pip3()
        if self.ada1115_check.GetValue() == True:
            self.install_adafruit_ads1115()
        if self.praw_check.GetValue() == True:
            self.install_praw()
        # Dependencies installed using apt
        if self.uvccapture_check.GetValue() == True or self.mpv_check.GetValue() == True or self.sshpass_check.GetValue() == True or self.matplotlib_check.GetValue() == True or self.cron_check.GetValue() == True:
            self.update_apt()
        if self.uvccapture_check.GetValue() == True:
            self.install_uvccaptre()
        if self.mpv_check.GetValue() == True:
            self.install_mpv()
        if self.sshpass_check.GetValue() == True:
            self.install_sshpass()
        if self.matplotlib_check.GetValue() == True:
            self.install_python_matplotlib()
        if self.cron_check.GetValue() == True:
            self.install_python_crontab()

        # Final message
        self.progress.SetLabel("####### INSTALL COMPLETE ######")
        wx.Yield()
        self.start_btn.Disable()
        self.cancel_btn.SetLabel("OK")

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
                    item = item.split("=")
                    line_split = item[0].split("_")
                    if line_split[0] == 'gpio' and not item[1] == "":
                        if len(line_split) == 2:
                            self.gpio_dict[line_split[1]] = item[1]
                        elif len(line_split) == 3:
                            self.gpio_on_dict[str(line_split[1])] = item[1]
                    else:
                        if not item[1] == "":
                            self.config_dict[item[0]] = item[1]
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

    def update_setting_file_on_pi_click(self, e):
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
        dbox = wx.MessageDialog(self, config_text, "upload to pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        #if user said ok then upload file to pi
        if (answer == wx.ID_OK):
            #
            # REPLACE THE FOLLOWING WITH A FUNCTION THAT ANYONE CAN CALL TO UPLOAD A FILE
            #
            sftp = ssh.open_sftp()
            folder = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/config/"
            f = sftp.open(folder + '/pigrow_config.txt', 'w')
            f.write(config_text)
            f.close()
            self.update_pigrow_setup_pannel_information_click("e")

class config_info_pnl(scrolled.ScrolledPanel):
    #  This displays the config info
    # controlled by the config_ctrl_pnl
    def __init__( self, parent ):
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.HSCROLL|wx.VSCROLL)
        font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        # Tab Title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Pigrow Setup', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Tools to set up the climate control functions of the Pigrow', size=(550,40))
        page_sub_title.SetFont(sub_title_font)
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
        self.dht_l = wx.StaticText(self,  label='DHT Sensor;', size=(100,25))
        self.dht_l.SetFont(font)
        config_info_pnl.dht_text = wx.StaticText(self,  label='dht')
        self.relay_l = wx.StaticText(self,  label='Relay GPIO link;', size=(100,25))
        self.relay_l.SetFont(font)
        config_info_pnl.gpio_table = self.GPIO_list(self, 1)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_GPIO)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_KEY_DOWN, self.del_gpio_item)
        gpio_pin_image = wx.Image('./pi_zero.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
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
            config_info_pnl.gpio_table.SetStringItem(index, 0, str(new_device))
            config_info_pnl.gpio_table.SetStringItem(index, 1, str(new_gpio))
            config_info_pnl.gpio_table.SetStringItem(index, 2, str(new_wiring))
            config_info_pnl.gpio_table.SetStringItem(index, 3, str(new_currently))
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Lamp Config')
        title_l.SetFont(title_font)
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Watering Config')
        title_l.SetFont(title_font)
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
        title_font = wx.Font(26, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Calibrate Water Flow Rate')
        title_l.SetFont(title_font)
        msg = 'Time how long it takes to fill a measured\ncontainer to determine the flow rate of\nyour pump.'
        sub_title_l = wx.StaticText(self,  label=msg)
        sub_title_l.SetFont(sub_title_font)
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
            self.SetColumnWidth(0, 100)
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
            self.SetColumnWidth(0, 75)
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
        def __init__(self, parent, id, pos=(5,530), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Time')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 75)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 400)
            self.SetColumnWidth(4, 300)
            self.SetColumnWidth(5, 100)

    def __init__( self, parent ):
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        wx.Panel.__init__(self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.TAB_TRAVERSAL)
        # Tab Title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Cron Tab Control', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Use cron on the pigrow to time events and trigger devices', size=(550,30))
        page_sub_title.SetFont(sub_title_font)
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
        sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
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
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.HSCROLL|wx.VSCROLL)
        #set blank variables
        localfiles_info_pnl.local_path = ""
        # top title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(17, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        item_title_font = wx.Font(17, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        page_title =  wx.StaticText(self,  label='Local Files', size=(300,40))
        page_sub_title =  wx.StaticText(self,  label='Files downloaded from the pi and stored locally', size=(550,30))
        page_title.SetFont(title_font)
        page_sub_title.SetFont(sub_title_font)
        # placing the information boxes
        local_path_l =  wx.StaticText(self,  label='Local Path -', size=(135, 25))
        local_path_l.SetFont(item_title_font)
        localfiles_info_pnl.local_path_txt = wx.StaticText(self,  label='local path')
        #local photo storage info
        photo_l = wx.StaticText(self,  label='Photos', size=(75,25))
        photo_l.SetFont(item_title_font)
        caps_folder_l = wx.StaticText(self,  label='Caps Folder;')
        localfiles_info_pnl.caps_folder = 'caps'
        localfiles_info_pnl.folder_text = wx.StaticText(self,  label=localfiles_info_pnl.caps_folder)
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
        config_l.SetFont(item_title_font)
        localfiles_info_pnl.config_files = self.config_file_list(self, 1)
        localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        logs_l = wx.StaticText(self,  label='Logs', size=(75,25))
        logs_l.SetFont(item_title_font)
        localfiles_info_pnl.logs_files = self.logs_file_list(self, 1)
        localfiles_info_pnl.logs_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_logs)
        #localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
    #    localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        #cron info text
        cron_l = wx.StaticText(self,  label='Cron', size=(75,25))
        cron_l.SetFont(item_title_font)
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
        caps_folder_sizer.Add(localfiles_info_pnl.folder_text , 0, wx.ALL|wx.EXPAND, 3)
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
                wx.Yield()
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
        port = 22
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
        port = 22
        print(("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port)))
        print(("    to  upload " + local_path + " to " + remote_path))
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        self.sftp.put(local_path, remote_path)
        self.sftp.close()
        ssh_tran.close()
        print((" file copied to " + str(remote_path)))

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
        port = 22
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
            wx.Yield() #update screen to show changes
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
        port = 22
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
                wx.Yield()
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
            wx.Yield()
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
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.HSCROLL|wx.VSCROLL )
        ## Draw UI elements
        self.graph_txt = wx.StaticText(self,  label='Graphs;')
        self.graph_txt.SetFont(sub_title_font)
        # for local graphing
        self.data_extraction_l = wx.StaticText(self,  label='Data Extraction Options')
        self.data_extraction_l.SetFont(sub_title_font)
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
        self.data_controls.SetFont(sub_title_font)
        self.start_date_l = wx.StaticText(self,  label='Start at -')
        self.start_time_picer = wx.adv.TimePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.start_date_picer = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.end_date_l = wx.StaticText(self,  label='Finish at -')
        self.end_time_picer = wx.adv.TimePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.end_date_picer = wx.adv.DatePickerCtrl( self, wx.ID_ANY, wx.DefaultDateTime)
        self.limit_date_to_last_l = wx.StaticText(self,  label='Limit to ')
        limit_choices = ["none", "day", "week", "month", "year"]
        self.limit_date_to_last_cb = wx.ComboBox(self, size=(90, 25),choices = limit_choices)
        self.limit_date_to_last_cb.Bind(wx.EVT_TEXT, self.limit_date_to_last_go)
        time_and_date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_and_date_sizer.Add(self.start_date_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.start_time_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.start_date_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_date_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_time_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.end_date_picer, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.limit_date_to_last_l, 0, wx.ALL, 2)
        time_and_date_sizer.Add(self.limit_date_to_last_cb, 0, wx.ALL, 2)
        data_trimming_sizer = wx.BoxSizer(wx.VERTICAL)
        data_trimming_sizer.Add(self.data_controls, 0, wx.ALL|wx.EXPAND, 4)
        data_trimming_sizer.Add(time_and_date_sizer, 0, wx.ALL, 0)
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
        data_extract_sizer = wx.BoxSizer(wx.VERTICAL)
        data_extract_sizer.Add(self.data_extraction_l, 0, wx.ALL, 5)
        data_extract_sizer.Add(example_line_sizer, 0, wx.ALL, 5)
        data_extract_sizer.Add(fields_extract_sizer, 0, wx.ALL, 3)

        #
        self.graph_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.graph_sizer.Add(wx.StaticText(self,  label='problem'), 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer =  wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(data_extract_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(data_trimming_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(high_low_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(axis_limits_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_txt, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_sizer, 0, wx.ALL, 0)
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()
        self.hide_data_extract()

    def hide_data_extract(self):
        self.data_extraction_l.Hide()
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
        self.size_h_l.Hide()
        self.size_h_cb.Hide()
        self.size_v_l.Hide()
        self.size_v_cb.Hide()
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
        self.start_date_l.Hide()
        self.start_time_picer.Hide()
        self.start_date_picer.Hide()
        self.end_date_l.Hide()
        self.end_time_picer.Hide()
        self.end_date_picer.Hide()
        self.limit_date_to_last_l.Hide()
        self.limit_date_to_last_cb.Hide()
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
        self.key_matches_l.Show()
        self.key_matches_tc.Show()
        self.rem_from_val_l.Show()
        self.rem_from_val_tc.Show()
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
        self.start_date_l.Show()
        self.start_time_picer.Show()
        self.start_date_picer.Show()
        self.end_date_l.Show()
        self.end_time_picer.Show()
        self.end_date_picer.Show()
        self.limit_date_to_last_l.Show()
        self.limit_date_to_last_cb.Show()
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
                    if found == "0":
                        self.value_pos_cb.SetValue("1")
                        self.value_pos_ex.SetLabel(self.split_line[1])
                    elif found == "1":
                        self.value_pos_cb.SetValue("0")
                        self.value_pos_ex.SetLabel(self.split_line[0])

    def key_pos_go(self, e):
        key_pos = self.key_pos_cb.GetValue()
        if not key_pos == "" and not key_pos == "None" and not key_pos == "Manual" and not key_pos == None:
            self.key_pos_ex.SetLabel(self.split_line[int(key_pos)])
            self.key_pos_split_tc.Enable()
            self.key_pos_split_tc.Show()
            self.key_pos_split_cb.Show()
            self.key_manual_l.Hide()
            self.key_manual_tc.Hide()
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
            self.key_manual_l.Hide()
            self.key_manual_tc.Hide()
            self.key_matches_l.Hide()
            self.key_matches_tc.Hide()
            self.key_pos_ex.SetLabel("")
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
            self.make_btn_enable()
        else:
            self.value_pos_split_tc.Disable()

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
                    MainApp.graphing_ctrl_pannel.set_dates_to_log()
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
                    except:
                        try:
                            test_date = datetime.datetime.strptime(date_split[1], '%Y-%m-%d %H:%M:%S.%f')
                            self.date_pos_split_cb.SetValue(date_split[1])
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
            MainApp.graphing_ctrl_pannel.set_dates_to_log()
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
            MainApp.graphing_ctrl_pannel.local_simple_line.Enable()
            MainApp.graphing_ctrl_pannel.local_color_line.Enable()
            MainApp.graphing_ctrl_pannel.local_simple_bar.Enable()
            MainApp.graphing_ctrl_pannel.local_box_plot.Enable()
            MainApp.graphing_ctrl_pannel.over_threasholds_by_hour.Enable()
            MainApp.graphing_ctrl_pannel.threasholds_pie.Enable()
            MainApp.graphing_ctrl_pannel.dividied_daily.Enable()
            MainApp.graphing_ctrl_pannel.value_diff_graph.Enable()
        else:
            #print("local graphing - not got valid data")
            MainApp.graphing_ctrl_pannel.local_simple_line.Disable()
            MainApp.graphing_ctrl_pannel.local_color_line.Disable()
            MainApp.graphing_ctrl_pannel.local_simple_bar.Disable()
            MainApp.graphing_ctrl_pannel.local_box_plot.Disable()
            MainApp.graphing_ctrl_pannel.over_threasholds_by_hour.Disable()
            MainApp.graphing_ctrl_pannel.threasholds_pie.Disable()
            MainApp.graphing_ctrl_pannel.dividied_daily.Disable()
            MainApp.graphing_ctrl_pannel.value_diff_graph.Disable()

    def limit_date_to_last_go(self, e):
        current_datetime = datetime.datetime.now()
        limit_setting = self.limit_date_to_last_cb.GetValue()
        is_set, range_start, range_end = MainApp.graphing_info_pannel.end_date_picer.GetRange()
        MainApp.graphing_info_pannel.end_date_picer.SetRange(range_start, current_datetime)
        MainApp.graphing_info_pannel.start_date_picer.SetRange(range_start, current_datetime)
        print("Limiting date to ", limit_setting)
        if limit_setting == "none":
            if not self.date_pos_cb.GetValue() == "":
                MainApp.graphing_ctrl_pannel.set_dates_to_log()
            return None
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
            first_time = MainApp.graphing_info_pannel.start_time_picer.GetValue()
            first_date = MainApp.graphing_info_pannel.start_date_picer.GetValue()
            first_datetime = datetime.datetime(year = first_date.year, month = first_date.month + 1, day = first_date.day, hour = first_time.hour, minute = first_time.minute, second = first_time.second)
            last_time = MainApp.graphing_info_pannel.end_time_picer.GetValue()
            last_date = MainApp.graphing_info_pannel.end_date_picer.GetValue()
            last_datetime = datetime.datetime(year = last_date.year, month = last_date.month + 1, day = last_date.day, hour = last_time.hour, minute = last_time.minute, second = last_time.second)
            #print(first_datetime, last_datetime)

        # read log into lists
        print("Reading log")
        date_list = []
        value_list = []
        key_list = []
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

            if key_pos == 'Manual':
                key_manual = self.key_manual_tc.GetValue()
                key_pos = ""
            else:
                key_manual = ""
                if not key_pos == 'None':
                    key_pos = int(key_pos)
                else:
                    key_pos = ""
            if self.key_matches_tc.IsEnabled() == True:
                key_matches = self.key_matches_tc.GetValue()
            else:
                key_matches = ""
        # date
        #print("length of log " + str(len(MainApp.graphing_ctrl_pannel.log_to_graph)))
        for line in MainApp.graphing_ctrl_pannel.log_to_graph:
            line_items = line.split(split_chr)
            # date
            date = line_items[date_pos]
            if not date_split == "":
                date = date.split(date_split)[date_split_pos]
            if "." in date:
                date = date.split(".")[0]
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if limit_by_date == True:
                    if date > last_datetime or date < first_datetime:
                        date = ""
            except:
                raise
                print("date not valid -" + str(date))
                date = ""
            # value
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
                # key
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
        #print("len date list read log:", len(date_list))
        if len(date_list) == 0:
            dmsg = "No valid log entries were found, check settings and try again"
            wx.MessageBox(dmsg, 'No data', wx.OK | wx.ICON_INFORMATION)
        if date_only == False:
            return date_list, value_list, key_list
        else:
            return date_list

    def show_local_graph(self, graph_path):
        MainApp.graphing_info_pannel.graph_sizer.Add(wx.StaticBitmap(MainApp.graphing_info_pannel, -1, wx.Image(graph_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        #MainApp.graphing_info_pannel.graph_sizer.Layout()
        MainApp.graphing_info_pannel.main_sizer.Layout()
        #MainApp.camconf_info_pannel.SetSizer(MainApp.graphing_info_pannel.main_sizer)
        MainApp.graphing_info_pannel.SetupScrolling()
        MainApp.window_self.Layout()


class graphing_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # Start drawing the UI elements
        #graphing engine selection
        make_graph_l = wx.StaticText(self,  label='Make graphs on;')
        graph_opts = ['Pigrow', 'local']
        self.graph_cb = wx.ComboBox(self, choices = graph_opts)
        self.graph_cb.Bind(wx.EVT_TEXT, self.graph_engine_combo_go)
        # remote buttons
        self.make_graph_btn = wx.Button(self, label='Make Graph')
        self.make_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_click)
        self.download_graph = wx.CheckBox(self, label='download')
        self.download_graph.SetValue(True)
        #
        ### for pi based graphing only
        self.pigraph_text = wx.StaticText(self,  label='Graphing directly on the pigrow\n saves having to download logs')
        # select graphing script
        #presets
        self.preset_text = wx.StaticText(self,  label='Preset')
        self.graph_presets_cb = wx.ComboBox(self, choices=['BLANK'])
        self.graph_presets_cb.Bind(wx.EVT_COMBOBOX, self.graph_preset_cb_go)
        self.graph_preset_all = wx.CheckBox(self, label='all')
        self.graph_preset_all.Bind(wx.EVT_CHECKBOX, self.preset_all_click)
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
        #
        ### for local graph construction
        self.select_log_btn = wx.Button(self, label='Select Log File')
        self.select_log_btn.Bind(wx.EVT_BUTTON, self.select_log_click)
        # make_graph_from_imported_module
        self.refresh_module_graph_btn = wx.Button(self, label='R')
        self.refresh_module_graph_btn.Bind(wx.EVT_BUTTON, self.refresh_module_graph_go)
        self.module_graph_choice = wx.ComboBox(self,  size=(200, 30), choices = self.get_module_options())
        self.module_graph_btn = wx.Button(self, label='Make')
        self.module_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_from_imported_module)
        module_graph_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        module_graph_sizer.Add(self.refresh_module_graph_btn, 0, wx.ALL, 3)
        module_graph_sizer.Add(self.module_graph_choice, 0, wx.ALL|wx.EXPAND, 3)
        module_graph_sizer.Add(self.module_graph_btn, 0, wx.ALL, 3)

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
        # local opts size
        local_opts_sizer = wx.BoxSizer(wx.VERTICAL)
        local_opts_sizer.Add(self.select_log_btn, 0, wx.ALL, 3)
        local_opts_sizer.AddStretchSpacer(1)
        local_opts_sizer.Add(module_graph_sizer, 0, wx.ALL, 3)
        local_opts_sizer.AddStretchSpacer(1)
        local_opts_sizer.Add(self.local_simple_line, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_color_line, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_simple_bar, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.local_box_plot, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.over_threasholds_by_hour, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.threasholds_pie, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.dividied_daily, 0, wx.ALL, 3)
        local_opts_sizer.AddStretchSpacer(1)
        local_opts_sizer.Add(self.value_diff_graph, 0, wx.ALL, 3)
        local_opts_sizer.Add(self.log_time_diff_graph, 0, wx.ALL, 3)

        local_opts_sizer.AddStretchSpacer(1)
        local_opts_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        local_opts_sizer.Add(self.switch_log_graph, 0, wx.ALL, 3)
        local_opts_sizer.AddStretchSpacer(1)
        make_graph_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        make_graph_sizer.Add(self.make_graph_btn, 0, wx.ALL|wx.EXPAND, 3)
        make_graph_sizer.Add(self.download_graph, 0, wx.ALL|wx.EXPAND, 3)
        graph_preset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        graph_preset_sizer.Add(self.graph_presets_cb, 0, wx.ALL|wx.EXPAND, 3)
        graph_preset_sizer.Add(self.graph_preset_all, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(make_graph_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.preset_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(graph_preset_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.pigraph_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.script_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.select_script_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.get_opts_tb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.opts_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.command_line_opts_value_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.opts_text, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.add_arg_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.extra_args_label, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.extra_args, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(make_graph_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(local_opts_sizer, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(self.main_sizer)

        # hideing all pigrow graphing UI elements until graph on pigrow is selected
        self.hide_make_on_pi_ui_elements()
        self.hide_make_local_ui_elements()

    def hide_make_on_pi_ui_elements(self):
        self.pigraph_text.Hide()
        self.script_text.Hide()
        self.select_script_cb.Hide()
        self.get_opts_tb.Hide()
        self.extra_args_label.Hide()
        self.extra_args.Hide()
        self.make_graph_btn.Hide()
        self.download_graph.Hide()
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

    def hide_make_local_ui_elements(self):
        self.select_log_btn.Hide()
        self.preset_text.Hide()
        self.graph_presets_cb.Hide()
        self.graph_preset_all.Hide()
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
        self.module_graph_choice.Hide()
        self.module_graph_btn.Hide()
        self.refresh_module_graph_btn.Hide()

        try:
            MainApp.graphing_info_pannel.hide_data_extract()
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
        self.refresh_module_graph_btn.Show()

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
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

    # Make locally controlls
    def select_log_click(self, e):
        wildcard = "TXT and LOG files (*.txt;*.log)|*.txt;*.log"
        openFileDialog = wx.FileDialog(self, "Select log file", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetDirectory(localfiles_info_pnl.local_path)
        openFileDialog.SetMessage("Select log file to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            print("Cancelled")
            return None
        log_path = openFileDialog.GetPath()
        print(" - Using ", log_path, " to make a graph locally" )
        MainApp.graphing_info_pannel.show_data_extract()
        # Open log file
        with open(log_path) as f:
            self.log_to_graph = f.read()
        self.log_to_graph = self.log_to_graph.splitlines()
        if len(self.log_to_graph) == 0:
            print(" --- Log file is empty")
        MainApp.graphing_info_pannel.example_line.SetLabel(self.log_to_graph[0])
        split_chr_choices = self.get_split_chr(self.log_to_graph[0])
        if len(split_chr_choices) == 1:
            MainApp.graphing_info_pannel.split_character_tc.SetValue(split_chr_choices[0])
        else:
            MainApp.graphing_info_pannel.split_character_tc.SetValue("")
            MainApp.graphing_info_pannel.clear_and_reset_fields()

    def set_dates_to_log(self):
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

    # graph presets

    def discover_graph_presets(self, e=""):
        show_all = self.graph_preset_all.GetValue()
        graph_presets_path = os.path.join(os.getcwd(), "graph_presets")
        graph_presets = os.listdir(graph_presets_path)
        self.graph_presets_cb.Clear()
        graph_preset_list = []
        for file in graph_presets:
            if show_all == False:
                current_presets_path = os.path.join(graph_presets_path, file)
                log_path = self.get_log_path_from_preset(current_presets_path)
                if not log_path == None:
                    if os.path.isfile(log_path) == True:
                        graph_preset_list.append(file)
            else:
                graph_preset_list.append(file)
        graph_preset_list.sort()
        self.graph_presets_cb.Append(graph_preset_list)



    def get_log_path_from_preset(self, graph_presets_path):
        local_logs_path = os.path.join(localfiles_info_pnl.local_path, "logs")
        with open(graph_presets_path) as f:
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

    def graph_preset_cb_go(self ,e):
        # blank settings from prior use
        limit_setting = MainApp.graphing_info_pannel.limit_date_to_last_cb.SetValue('none')
        # load presets
        graph_option = self.graph_presets_cb.GetValue()
        MainApp.graphing_info_pannel.show_data_extract()
        print("Want's to use preset from " + graph_option)
        graph_presets_path = os.path.join(os.getcwd(), "graph_presets")
        graph_presets_path = os.path.join(graph_presets_path, graph_option)
        with open(graph_presets_path) as f:
            graph_presets = f.read()
        graph_presets = graph_presets.splitlines()
        preset_settings = {}
        for line in graph_presets:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos + 1:]
                preset_settings[key]=value
        #
        # set and load log
        if "log_path" in preset_settings:
            local_logs_path = os.path.join(localfiles_info_pnl.local_path, "logs")
            log_path = os.path.join(local_logs_path, preset_settings["log_path"])
            with open(log_path) as f:
                self.log_to_graph = f.read()
            self.log_to_graph = self.log_to_graph.splitlines()
            if len(self.log_to_graph) == 0:
                print(" --- Log file " + log_path + " is empty")
            else:
                MainApp.graphing_info_pannel.example_line.SetLabel(self.log_to_graph[0])
        else:
            print("Log path not found in presets file")
        # set boxes
        # data extract
        if "split_chr" in preset_settings:
            MainApp.graphing_info_pannel.split_character_tc.SetValue(preset_settings["split_chr"])
        # date
        if "date_pos" in preset_settings:
            MainApp.graphing_info_pannel.date_pos_cb.SetValue(preset_settings["date_pos"])
        if "date_split" in preset_settings:
            if not preset_settings["date_split_pos"] == "":
                MainApp.graphing_info_pannel.date_pos_split_tc.SetValue(preset_settings["date_split"])
        if "date_split_pos" in preset_settings:
            if not preset_settings["date_split_pos"] == "":
                MainApp.graphing_info_pannel.date_pos_split_cb.SetSelection(int(preset_settings["date_split_pos"]))
        # value
        if "value_rem" in preset_settings:
            MainApp.graphing_info_pannel.rem_from_val_tc.SetValue(preset_settings["value_rem"])
        if "value_pos" in preset_settings:
            MainApp.graphing_info_pannel.value_pos_cb.SetValue(preset_settings["value_pos"])
        if "value_split" in preset_settings:
            if not preset_settings["value_split"] == "":
                MainApp.graphing_info_pannel.value_pos_split_tc.SetValue(preset_settings["value_split"])
        if "value_split_pos" in preset_settings:
            if not preset_settings["value_split_pos"] == "":
                MainApp.graphing_info_pannel.value_pos_split_cb.SetSelection(int(preset_settings["value_split_pos"]))
                MainApp.graphing_info_pannel.value_pos_split_go("e")
        # key
        if "key_pos" in preset_settings:
            MainApp.graphing_info_pannel.key_pos_cb.SetValue(preset_settings["key_pos"])
        if "key_split" in preset_settings:
            if not preset_settings["key_split"] == "":
                MainApp.graphing_info_pannel.key_pos_split_tc.SetValue(preset_settings["key_split"])
        if "key_split_pos" in preset_settings:
            if not preset_settings["key_split_pos"] == "":
                MainApp.graphing_info_pannel.key_pos_split_cb.SetSelection(int(preset_settings["key_split_pos"]))
                MainApp.graphing_info_pannel.key_pos_split_go("e")
        if "key_match" in preset_settings:
            MainApp.graphing_info_pannel.key_matches_tc.SetValue(preset_settings["key_match"])
        if "key_manual" in preset_settings:
            if not preset_settings["key_manual"] == "":
                MainApp.graphing_info_pannel.key_manual_tc.SetValue(preset_settings["key_manual"])
        # setting
        if "value_range_source" in preset_settings:
            value_range_source = preset_settings["value_range_source"]
        if value_range_source == "config":
            if "low" in preset_settings:
                low_loc = preset_settings["low"]
                if not low_loc == "":
                    if low_loc in MainApp.config_ctrl_pannel.config_dict:
                        low_value = MainApp.config_ctrl_pannel.config_dict[low_loc]
                        MainApp.graphing_info_pannel.low_tc.SetValue(low_value)
                        danger_low = ((float(low_value) / 100) * 80)
                        MainApp.graphing_info_pannel.danger_low_tc.SetValue(str(danger_low))
            if "high" in preset_settings:
                high_loc = preset_settings["high"]
                if not high_loc == "":
                    if high_loc in MainApp.config_ctrl_pannel.config_dict:
                        high_value = MainApp.config_ctrl_pannel.config_dict[high_loc]
                        MainApp.graphing_info_pannel.high_tc.SetValue(high_value)
                        danger_high = ((float(high_value) / 100) * 120)
                        MainApp.graphing_info_pannel.danger_high_tc.SetValue(str(danger_high))
        else:
            MainApp.graphing_info_pannel.low_tc.SetValue(preset_settings["low"])
            MainApp.graphing_info_pannel.danger_low_tc.SetValue(preset_settings["danger_low"])
            MainApp.graphing_info_pannel.high_tc.SetValue(preset_settings["high"])
            MainApp.graphing_info_pannel.danger_high_tc.SetValue(preset_settings["danger_high"])

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

    def get_module_options(self):
        list_of_modules = []
        graph_modules_folder = os.path.join(os.getcwd(), "graph_modules")
        module_options = os.listdir(graph_modules_folder)
        for file in module_options:
            if "graph_" in file:
                file = file.split("graph_")[1]
                if ".py" in file:
                    file = file.split(".py")[0]
                    list_of_modules.append(file)
        return list_of_modules

    def refresh_module_graph_go(self, e):
        self.module_graph_choice.Clear()
        module_list = self.get_module_options()
        self.module_graph_choice.Append(module_list)


    def make_graph_from_imported_module(self, e):
        print("Want's to create a graph using a external module...  ")
        # read data from log
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
            return None
        MainApp.status.write_bar("-- Creating a graph from a module using  " + str(len(date_list)) + " values")
        module_path = graph_presets_path = os.path.join(os.getcwd(), "graph_modules", "simple_line.py")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        dangercold = float(MainApp.graphing_info_pannel.danger_low_tc.GetValue())
        toocold = float(MainApp.graphing_info_pannel.low_tc.GetValue())
        toohot = float(MainApp.graphing_info_pannel.high_tc.GetValue())
        dangerhot = float(MainApp.graphing_info_pannel.danger_high_tc.GetValue())
        size_h, size_v = self.get_graph_size_from_ui()
        module_name = self.module_graph_choice.GetValue()
        file_name = module_name + "_graph.png"
        graph_path = os.path.join(localfiles_info_pnl.local_path, file_name)
        # import and run the graph script
        graph_modules_folder = os.path.join(os.getcwd(), "graph_modules")
        sys.path.append(graph_modules_folder)
        module_name = "graph_" + module_name
        if module_name in sys.modules:
            del sys.modules[module_name]
        exec("from " + module_name + " import make_graph", globals())
        make_graph(date_list, value_list, key_list, graph_path, ymax, ymin, size_h, size_v, dangerhot, toohot, toocold, dangercold)
        #
        print("module_graph created and saved to " + graph_path)
        MainApp.graphing_info_pannel.show_local_graph(graph_path)
        MainApp.status.write_bar("ready...")


    # make graphs
    def local_simple_line_go(self, e):
        print("Want's to create a simple line graph...  ")
        # read data from log
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
        plt.ylabel(key_list[0]) # + " in " + key_unit)
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        ax.plot(date_list, value_list, color='black', lw=1)
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
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
            return None
        MainApp.status.write_bar("-- Creating a simple bar graph from " + str(len(date_list)) + " values")
        # read graph settings from ui boxes
        key_unit = ""
        ymax = MainApp.graphing_info_pannel.axis_y_max_cb.GetValue()
        ymin = MainApp.graphing_info_pannel.axis_y_min_cb.GetValue()
        size_h, size_v = self.get_graph_size_from_ui()
        # define the graph space
        fig, ax = plt.subplots(figsize=(size_h, size_v))
        fig.canvas.set_window_title('Simple Bar Graph')
        plt.title("Time Perod; " + str(date_list[0].strftime("%b-%d %H:%M")) + " to " + str(date_list[-1].strftime("%b-%d %H:%M")) + " ")
        plt.ylabel(key_list[0]) # + " in " + key_unit)
        if not ymax == "":
            plt.ylim(ymax=int(ymax))
        if not ymin == "":
            plt.ylim(ymin=int(ymin))
        ax.bar(date_list, value_list,width=0.01, linewidth = 1 )
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
        date_list, temp_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
            if temp_list[i] >= dangerhot:
                dangerhotArray[h] += 1
            elif temp_list[i] >= toohot:
                toohotArray[h] += 1
            elif temp_list[i] <= dangercold:
                dangercoldArray[h] += 1
            elif temp_list[i] <= toocold:
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
        date_list, temp_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
            if temp_list[i] >= dangerhot:
                tempCount[0] += 1
            elif temp_list[i] >= toohot:
                tempCount[1] += 1
            elif temp_list[i] <= dangercold:
                tempCount[4] += 1
            elif temp_list[i] <= toocold:
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
        date_list, temp_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
            hours[h].append(temp_list[i])

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
        date_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True, date_only=True)
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
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
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
        date_list, value_list, key_list = MainApp.graphing_info_pannel.read_log_date_and_value(numbers_only=True)
        if len(date_list) == 0:
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
            wx.Yield()
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

    def clear_graph_area(self):
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
    #
    def __init__( self, parent ):
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.HSCROLL|wx.VSCROLL )
        ## Draw UI elements
        # placing the information boxes
        # top row
        ccf_label = wx.StaticText(self,  label='Camera Config file', size=(150,30))
        self.camconf_path_tc = wx.TextCtrl(self, value="", size=(350, 30))
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
        self.extra_cmds_string_fs_tb = wx.TextCtrl(self, size=(200,40), style=wx.TE_MULTILINE)
        ## uvccaptre only controlls
        self.extra_cmds_uvc_label = wx.StaticText(self,  label='extra commands for uvc;')
        self.extra_cmds_string_uvc_tb = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        #####


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
        #self.uvc_opts_sizer.Hide()

        # NEED TO BE ADDED - generic extra args for legacy + extra args for other camera opts
        #2nd row Pannels sizers
        panels_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panels_sizer.Add(basic_settings_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(image_size_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(fswebcam_opts_sizer, 0, wx.ALL, 5)
        panels_sizer.Add(fswebcam_args_sizer, 0, wx.ALL|wx.EXPAND, 5)
        panels_sizer.Add(self.uvc_opts_sizer, 0, wx.ALL|wx.EXPAND, 5)
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


        # set sizers and scrolling
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def hide_uvc_control(self):
        self.extra_cmds_uvc_label.Hide()
        self.extra_cmds_string_uvc_tb.Hide()
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def show_uvc_control(self):
        print("SHOWING UVC CONTROL")
        self.extra_cmds_uvc_label.Show()
        self.extra_cmds_string_uvc_tb.Show()
        self.hide_fswebcam_control()
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
        test_str = self.setting_string_tb.GetValue()
        test_val = self.setting_value_tb.GetValue()
        cmd_str = self.extra_cmds_string_fs_tb.GetValue()
        if test_str in cmd_str:
            cmd_str = self.modify_cmd_str(cmd_str, test_str, test_val)
        else:
            cmd_str += ' --set "' + str(test_str) + '"=' + str(test_val)
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
        self.read_cam_config_btn = wx.Button(self, label='read cam config')
        self.read_cam_config_btn.Bind(wx.EVT_BUTTON, self.read_cam_config_click)
        self.save_cam_config_btn = wx.Button(self, label='save to pi')
        self.save_cam_config_btn.Bind(wx.EVT_BUTTON, self.save_cam_config_click)
        #camera options
        self.cam_select_l = wx.StaticText(self,  label='Camera selection;')
        self.list_cams_btn = wx.Button(self, label='find', size=(30, 30))
        self.list_cams_btn.Bind(wx.EVT_BUTTON, self.list_cams_click)
        cam_opts = [""]
        self.cam_cb = wx.ComboBox(self, choices = cam_opts, size=(225, 30))
        self.cam_cb.Bind(wx.EVT_COMBOBOX, self.cam_combo_go)
        #
        # UI for WEBCAM
        #
        self.cap_tool_l = wx.StaticText(self,  label='Capture tool;')
        webcam_opts = ['uvccapture', 'fswebcam']
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
        self.range_start_tc.SetValue("1")
        self.range_end_tc.SetValue("255")
        self.range_every_tc.SetValue("20")
        # take range button
        self.take_range_btn = wx.Button(self, label='Take\nrange', size=(50,-1))
        self.take_range_btn.Bind(wx.EVT_BUTTON, self.range_btn_click)

        #
        # UI for Picam coming soon
        #
        #not addded yet

        # Sizers
        load_save_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        load_save_btn_sizer.Add(self.read_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        load_save_btn_sizer.Add(self.save_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        find_select_cam_sizer = wx.BoxSizer(wx.HORIZONTAL)
        find_select_cam_sizer.Add(self.list_cams_btn, 0, wx.ALL, 0)
        find_select_cam_sizer.Add(self.cam_cb, 0, wx.ALL|wx.EXPAND, 0)
        take_single_photo_btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        take_single_photo_btns_sizer.Add(self.take_unset_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        take_single_photo_btns_sizer.Add(self.take_s_set_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
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
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)


    def read_cam_config_click(self, e):
        #
        if MainApp.camconf_info_pannel.camconf_path_tc.GetValue() == "":
            try:
                MainApp.camconf_info_pannel.camconf_path_tc.SetValue(MainApp.config_ctrl_pannel.dirlocs_dict['camera_settings'])
            except:
                #raise
                MainApp.camconf_info_pannel.camconf_path_tc.SetValue("/home/" + pi_link_pnl.target_user + "/Pigrow/config.camera_settings.txt")
                print("Camera config location not set in dirlocs, using default location.")
        #
        pi_cam_settings_path = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pi_cam_settings_path)
        if out == "":
            print("Unable to read settings file -" + pi_cam_settings_path)
            return None
        cam_settings = out.splitlines()
        self.camera_settings_dict = {}
        for line in cam_settings:
            if "=" in line:
                key = line.split('=')[0]
                value = line.split('=')[1]
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
        if "cam_fsw_extra" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.SetValue(self.camera_settings_dict['cam_fsw_extra'])
        if "cam_uvc_extra" in self.camera_settings_dict:
            MainApp.camconf_info_pannel.extra_cmds_string_uvc_tb.SetValue(self.camera_settings_dict['cam_uvc_extra'])


    def save_cam_config_click(self, e):
        # Construct camera config file
        config_text = "s_val=" + str(MainApp.camconf_info_pannel.tb_s.GetValue()) + "\n"
        config_text += "c_val=" + str(MainApp.camconf_info_pannel.tb_c.GetValue()) + "\n"
        config_text += "g_val=" + str(MainApp.camconf_info_pannel.tb_g.GetValue()) + "\n"
        config_text += "b_val=" + str(MainApp.camconf_info_pannel.tb_b.GetValue()) + "\n"
        config_text += "x_dim=" + str(MainApp.camconf_info_pannel.tb_x.GetValue()) + "\n"
        config_text += "y_dim=" + str(MainApp.camconf_info_pannel.tb_y.GetValue()) + "\n"
        config_text += "cam_num=" + str(self.cam_cb.GetValue()) + "\n"
        config_text += "cam_opt=" + str(self.webcam_cb.GetValue()) + "\n"
        config_text += "additonal_commands=" + str(MainApp.camconf_info_pannel.cmds_string_tb.GetValue()) + "\n"
        config_text += "fsw_extra=" + str(MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.GetValue()) + "\n"
    #    config_text += "uvc_extra=" + str("")
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
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /dev/video*")
        cam_list = out.strip().split("\n")
        self.cam_cb.Clear()
        for cam in cam_list:
            self.cam_cb.Append(cam)

    def clear_picture_area(self):
        children = MainApp.camconf_info_pannel.picture_sizer.GetChildren()
        for child in children:
            item = child.GetWindow()
            item.Destroy()

    def take_saved_set_click(self, e):
        print("Taking photo using camcap.py")
        settings_file = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        outpath = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/'
        cmd = '/home/' + pi_link_pnl.target_user + '/Pigrow/scripts/cron/camcap.py caps=' + outpath + ' set=' + settings_file
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        output = out + error
        print (out, error)
        path = output.split("Saving image to:")[1].split("\n")[0].strip()
        #print (path)
        local_temp_img_path = os.path.join("temp", "test_settings.jpg")
        img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, path, local_temp_img_path)
        #MainApp.camconf_info_pannel.picture_sizer.Clear()
        self.clear_picture_area()
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticText(MainApp.camconf_info_pannel,  label="Taken with settings stored on the Pigrow"), 0, wx.ALL, 2)
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticBitmap(MainApp.camconf_info_pannel, -1, wx.Image(img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        MainApp.camconf_info_pannel.SetSizer(MainApp.camconf_info_pannel.main_sizer)
        MainApp.camconf_info_pannel.SetupScrolling()

    def get_camopt_spesific_additional_cmds(self):
        cam_opt = self.webcam_cb.GetValue()
        if cam_opt == "fswebcam":
            cam_additional = MainApp.camconf_info_pannel.extra_cmds_string_fs_tb.GetValue()
        elif cam_opt == "uvccapture":
            cam_additional = "link to text control for uvc opts here please" # .GetValue()
        else:
            print("!!!! YOU FORGOT TO SET UP OPTIONS HANDLING FOR THIS CAMERA CAPTURE TOOL")
            cam_additional = ""
        return cam_additional

    def take_set_click(self, e):
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
            local_temp_img_path = os.path.join("temp", "test_settings.jpg")
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, remote_img_path, local_temp_img_path)
            self.clear_picture_area()
            MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticText(MainApp.camconf_info_pannel,  label="Image taken using local settings"), 0, wx.ALL, 2)
            MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticBitmap(MainApp.camconf_info_pannel, -1, wx.Image(img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
            MainApp.camconf_info_pannel.SetSizer(MainApp.camconf_info_pannel.main_sizer)
            MainApp.camconf_info_pannel.SetupScrolling()

    def install_fswebcam(self):
        print("user asked to install fswebcam on the pi")
        dbox = wx.MessageDialog(self, "fswebcam isn't installed on the pigrow, would you like to install it?", "install fswebcam?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("installing fswebcam on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt install fswebcam --force-yes -y")
            print(out, error)

    def range_btn_click(self, e):
        print("Taking a range of images is not yet supported, working on it right this second")
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
        range_photo_set = []
        outfolder= '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/'
        #cycle through the selected range taking a photo at each point and adding the remote path to range_photo_set
        for changing_range in range(int(range_start), int(range_end), int(range_every)):
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
        print(range_photo_set)
        img_set = []
        self.clear_picture_area()
        #MainApp.camconf_info_pannel.Clear()
        #MainApp.camconf_info_pannel.Refresh()
        for photo_path in range_photo_set:
            picture_name = photo_path.split("/")[-1]
            local_temp_img_path = os.path.join("temp", picture_name)
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, photo_path, local_temp_img_path)
            print (img_path)
            img_set.append(img_path)
            print("Adding " + img_path)
            MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticLine(MainApp.camconf_info_pannel, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
            MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticText(MainApp.camconf_info_pannel,  label=picture_name), 0, wx.ALL, 2)
            MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticBitmap(MainApp.camconf_info_pannel, -1, wx.Image(img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)

        MainApp.camconf_info_pannel.SetSizer(MainApp.camconf_info_pannel.main_sizer)
        MainApp.camconf_info_pannel.SetupScrolling()


    def take_test_image(self, s_val, c_val, g_val, b_val, x_dim=800, y_dim=600,
                        cam_select='/dev/video0', cam_capture_choice='uvccapture', output_file='~/test_cam_settings.jpg',
                        ctrl_test_value=None, ctrl_text_string=None, cmd_str=''):
        cam_output = '!!!--NO READING--!!!'
        print("preparing to take test image...")
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
                cam_cmd += " --set " + ctrl_text_string + "=" + str(ctrl_test_value)
            cam_cmd += cmd_str
            cam_cmd += " --jpeg 90" #jpeg quality
            # cam_cmd += ' --info "HELLO INFO TEXT"'
            cam_cmd += " " + output_file  #output filename'
        else:
            print("NOT IMPLIMENTED - SELECT CAM CHOICE OF UVC OR FSWEBCAM PLZ")
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
        self.clear_picture_area()
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticText(MainApp.camconf_info_pannel,  label="Picture taken using camera default"), 0, wx.ALL, 2)
        MainApp.camconf_info_pannel.picture_sizer.Add(wx.StaticBitmap(MainApp.camconf_info_pannel, -1, wx.Image(img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        MainApp.camconf_info_pannel.SetSizer(MainApp.camconf_info_pannel.main_sizer)
        MainApp.camconf_info_pannel.SetupScrolling()

    def take_unset_test_image(self, x_dim=10000, y_dim=10000, additonal_commands='',
                              cam_capture_choice='uvccapture',
                              output_file=None):
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
            cam_cmd += " -D 2"      #the delay in seconds before taking photo
            cam_cmd += " -S 5"      #number of frames to skip before taking image
            cam_cmd += " --jpeg 90" #jpeg quality
            cam_cmd += " " + output_file  #output filename'
        else:
            print("not yet implimented please select uv or fs webcam as you option")

        print("---Doing: " + cam_cmd)
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cam_cmd)
        MainApp.status.write_bar("Camera output; " + out)
        return out, output_file

    def cam_combo_go(self, e):
        print(self.cam_cb.GetValue())
        if self.cam_cb.GetValue() == "Picam":
            self.webcam_cb.Hide()
            print("Picam")
        else:
            self.webcam_cb.Show()

    def webcam_combo_go(self, e):
        if self.webcam_cb.GetValue() == 'fswebcam':
            MainApp.camconf_info_pannel.hide_uvc_control()
            MainApp.camconf_info_pannel.show_fswebcam_control()
        elif self.webcam_cb.GetValue() == 'uvccapture':
            MainApp.camconf_info_pannel.hide_fswebcam_control()
            MainApp.camconf_info_pannel.show_uvc_control()
        else:
            MainApp.camconf_info_pannel.hide_fswebcam_control()
            MainApp.camconf_info_pannel.hide_uvc_control()

#
#
#
##  Timelapse Maker Control Panel
#
#
#

class timelapse_info_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.TAB_TRAVERSAL )
        # Tab Title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Timelapse Control Panel', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Making timelapse videos using files downloaded from the pigrow', size=(700,30))
        page_sub_title.SetFont(sub_title_font)
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
        main_sizer.Add(lower_half_sizer, 0,  wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 3)
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
        sub_title_font = wx.Font(13, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        # Capture controlls
        quick_capture_l = wx.StaticText(self,  label='Quick Capture',size=(100,25))
        quick_capture_l.SetFont(sub_title_font)
        capture_start_btn = wx.Button(self, label='Start capture')
        capture_start_btn.Bind(wx.EVT_BUTTON, self.start_capture_click)
        # path options
        path_l = wx.StaticText(self,  label='Image Path',size=(100,25))
        path_l.SetFont(sub_title_font)
        open_caps_folder_btn = wx.Button(self, label='Open Caps Folder')
        open_caps_folder_btn.Bind(wx.EVT_BUTTON, self.open_caps_folder_click)
        select_set_btn = wx.Button(self, label='Select\nCaps Set')
        select_set_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_set_click)
        select_folder_btn = wx.Button(self, label='Select\nCaps Folder')
        select_folder_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_folder_click)
        # frame slect - range, limit to start / end dates, etc
        frame_select_l = wx.StaticText(self,  label='Frames',size=(100,25))
        frame_select_l.SetFont(sub_title_font)
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
        # out file
        outfile_l = wx.StaticText(self,  label='Outfile')
        self.out_file_tc = wx.TextCtrl(self)
        set_outfile_btn = wx.Button(self, label='...', size=(27,27))
        set_outfile_btn.Bind(wx.EVT_BUTTON, self.set_outfile_click)
        # render controlls
        render_l = wx.StaticText(self,  label='Render',size=(100,25))
        render_l.SetFont(sub_title_font)
        fps_l = wx.StaticText(self,  label='FPS')
        self.fps_tc = wx.TextCtrl(self, value="25", size=(50,25))
        make_timelapse_btn = wx.Button(self, label='Make Timelapse')
        make_timelapse_btn.Bind(wx.EVT_BUTTON, self.make_timelapse_click)
        play_timelapse_btn = wx.Button(self, label='Play')
        play_timelapse_btn.Bind(wx.EVT_BUTTON, self.play_timelapse_click)

        # Sizers
        capture_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        capture_bar_sizer.Add(quick_capture_l, 0, wx.ALL|wx.EXPAND, 3)
        capture_bar_sizer.Add(capture_start_btn, 0, wx.ALL|wx.EXPAND, 3)
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
        render_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        render_buttons_sizer.Add(make_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_buttons_sizer.Add(play_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        render_bar_sizer.Add(render_l, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(fps_sizer, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(file_name_sizer, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(render_buttons_sizer, 0, wx.ALL|wx.EXPAND, 3)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(capture_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(file_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(frame_select_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(make_overlay_set_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(render_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        #create blank lists
        self.trimmed_frame_list = []
        self.cap_file_paths = []

    def start_capture_click(self, e):
        print("Quick Capture feature not yet enabled")

    def make_log_overlay_set(self, e):
        make_log_overlay_dbox = make_log_overlay_dialog(None)
        make_log_overlay_dbox.ShowModal()

    def make_timelapse_click(self, e):
        # write text file of frame to use
        temp_folder = os.path.join(localfiles_info_pnl.local_path, "temp")
        if not os.path.isdir(temp_folder):
            os.makedirs(temp_folder)
        listfile = os.path.join(temp_folder, "frame_list.txt")
        frame_list_text_file = open(listfile, "w")
        for file in self.trimmed_frame_list:
            frame_list_text_file.write(file + "\n")
        frame_list_text_file.close()
        ofps  = self.fps_tc.GetValue()
        outfile= self.out_file_tc.GetValue()
        extra_commands = ""
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        #box_label = wx.StaticText(self,  label='Select Text Placement')
        #box_label.SetFont(title_font)
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        box_label = wx.StaticText(self,  label='Create Log Overlay Image Set')
        box_label.SetFont(title_font)
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
        top_l.SetFont(sub_title_font)
        example_line_l = wx.StaticText(self,  label='Example Line -')
        self.example_line = wx.StaticText(self,  label='')
        # split line character
        split_character_l = wx.StaticText(self,  label='Split Character')
        self.split_character_tc = wx.TextCtrl(self, size=(90, 25))
        self.split_character_tc.Bind(wx.EVT_TEXT, self.split_line_text)
        # row of date related options
        date_pos_l = wx.StaticText(self,  label='Date Position')
        self.date_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.date_pos_cb.Bind(wx.EVT_TEXT, self.date_pos_go)
        self.date_pos_cb.Disable()
        self.date_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.date_pos_split_tc.Bind(wx.EVT_TEXT, self.date_pos_split_text)
        self.date_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.date_pos_split_cb.Bind(wx.EVT_TEXT, self.date_pos_split_select)
        self.date_pos_ex = wx.StaticText(self,  label='')
        # row of value related options
        value_pos_l = wx.StaticText(self,  label='Value Position')
        self.value_pos_cb = wx.ComboBox(self, size=(90, 25),choices = [])
        self.value_pos_cb.Bind(wx.EVT_TEXT, self.value_pos_go)
        self.value_pos_cb.Disable()
        self.value_pos_split_tc = wx.TextCtrl(self, size=(60, 25))
        self.value_pos_split_tc.Bind(wx.EVT_TEXT, self.value_pos_split_text)
        self.value_pos_split_cb = wx.ComboBox(self, size=(60, 25))
        self.value_pos_split_cb.Bind(wx.EVT_TEXT, self.value_pos_split_go)
        self.value_pos_ex = wx.StaticText(self,  label='')
        # row of key related options
        key_pos_l = wx.StaticText(self,  label='Key Position')
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
        display_l.SetFont(sub_title_font)
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
        buttons_sizer.Add(self.make_btn, 0,  wx.ALIGN_LEFT, 3)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALIGN_RIGHT, 3)
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
        if not key_pos == "" and not key_pos == "None" and not key_pos == "Manual" and not key_pos == None:
            self.key_pos_ex.SetLabel(self.split_line[int(key_pos)])
            self.key_pos_split_tc.Enable()
            self.key_pos_split_tc.Show()
            self.key_pos_split_cb.Show()
            self.key_manual_l.Hide()
            self.key_manual_tc.Hide()
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
                    except:
                        try:
                            test_date = datetime.datetime.strptime(date_split[1], '%Y-%m-%d %H:%M:%S.%f')
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
            test_date = datetime.datetime.strptime(date_pos, '%Y-%m-%d %H:%M:%S.%f')
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
        print(" Found " + str(len(log_data_list)) + " items in the log" )
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
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.TAB_TRAVERSAL )
        # Tab Title
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='Sensor Control Panel', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Link aditional sensors to the pigrow', size=(550,30))
        page_sub_title.SetFont(sub_title_font)
        # placing the information boxes
        self.sensor_list = self.sensor_table(self, 1)
        self.sensor_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.sensor_table.double_click)
        # sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.sensor_list, 1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

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
            self.SetColumnWidth(3, 75)
            self.SetColumnWidth(4, 175)
            self.SetColumnWidth(5, 100)

        def make_sensor_table(self, e):
            sensor_name_list = []
            print("Using config_dict to fill sensor table")
            self.DeleteAllItems()
            for key, value in list(MainApp.config_ctrl_pannel.config_dict.items()):
                if "sensor_" in key:
                    if "_type" in key:
                        sensor_name_list.append(key.split("_")[1])
            for sensor in sensor_name_list:
                type  = MainApp.config_ctrl_pannel.config_dict['sensor_' + sensor + "_type"]
                log   = MainApp.config_ctrl_pannel.config_dict['sensor_' + sensor + "_log"]
                loc   = MainApp.config_ctrl_pannel.config_dict['sensor_' + sensor + "_loc"]
                extra = MainApp.config_ctrl_pannel.config_dict['sensor_' + sensor + "_extra"]
                #
                # check cron to see if sensor is being logged and how often
                #
                last_index = cron_list_pnl.repeat_cron.GetItemCount()
                log_freq = "not found"
                if not last_index == 0:
                    for index in range(0, last_index):
                        job_name  = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                        job_extra = cron_list_pnl.repeat_cron.GetItem(index, 4).GetText()
                        extra_name  = "name=" + str(sensor)
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
                #
                self.add_to_sensor_list(sensor, type, log, loc, extra, log_freq)

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
            MainApp.sensors_info_pannel.sensor_list.s_log = log
            MainApp.sensors_info_pannel.sensor_list.s_loc = loc
            MainApp.sensors_info_pannel.sensor_list.s_extra = extra
            MainApp.sensors_info_pannel.sensor_list.s_timing = timing_string
            if type == 'chirp':
                edit_chirp_dbox = chirp_dialog(None)
                edit_chirp_dbox.ShowModal()
            elif type == "DS18B20":
                ds18b20_dialog_box = ds18b20_dialog(None)
                ds18b20_dialog_box.ShowModal()
            elif type == "ADS1115":
                ads1115_dialog_box = ads1115_dialog(None)
                ads1115_dialog_box.ShowModal()

class sensors_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
        #
        # Soil Moisture Controlls
        # Refresh page button
        self.make_table_btn = wx.Button(self, label='make table')
        self.make_table_btn.Bind(wx.EVT_BUTTON, MainApp.sensors_info_pannel.sensor_list.make_sensor_table)
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
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def add_ads1115_click(self, e):
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        box_label = wx.StaticText(self,  label='ADS1115 Analog to Digital Converter')
        box_label.SetFont(title_font)
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
            (self.val0_max_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_max_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_max_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_max_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (max_s_l, 0, wx.EXPAND),
            (self.val0_max_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_max_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_max_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_max_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (min_l, 0, wx.EXPAND),
            (self.val0_min_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_min_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_min_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_min_val, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (min_s_l, 0, wx.EXPAND),
            (self.val0_min_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val1_min_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val2_min_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.val3_min_script, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)])

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
            (chan_0_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (chan_1_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (chan_2_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (chan_3_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (values_l, 0, wx.EXPAND),
            (self.value_0_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_1_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_2_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.value_3_l, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (gain_l, 0, wx.EXPAND),
            (self.gain0_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain1_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain2_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.gain3_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (sps_l, 0, wx.EXPAND),
            (self.sps_0_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_1_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_2_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.sps_3_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (show_as_l, 0, wx.EXPAND),
            (self.show_as_0_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_1_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_2_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.show_as_3_cb, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (centralise_l, 0, wx.EXPAND),
            (self.centralise_0, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_1, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_2, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL),
            (self.centralise_3, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL) ])
        max_volt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_volt_sizer.Add(max_volt_l, 0,  wx.ALL, 3)
        max_volt_sizer.Add(self.max_volt_tc, 0,  wx.ALL, 3)
        round_to_sizer = wx.BoxSizer(wx.HORIZONTAL)
        round_to_sizer.Add(tound_to_l, 0,  wx.ALL, 3)
        round_to_sizer.Add(self.round_to_tc, 0,  wx.ALL, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALIGN_LEFT, 3)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALIGN_RIGHT, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(channels_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.use_script_triggers, 0, wx.ALL, 3)
        main_sizer.Add(trigger_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 3)
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        box_label = wx.StaticText(self,  label='DS18B20 Temp Sensor')
        box_label.SetFont(title_font)
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
        buttons_sizer.Add(self.add_btn, 0,  wx.ALIGN_LEFT, 3)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALIGN_RIGHT, 3)
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
            print("the absolute madman wants to do it!!!!")
            # running phase one - finding a max value
            instruction_text =  "Chirp Calibration phase 1; \n\n  Make sure the sensor is clean, "
            instruction_text += " place the probe in a glass of water.  This will give us a maximum value."
            instruction_text += "\n\n Once started please be patient, it will take a few min"
            dbox = wx.MessageDialog(self, instruction_text, "Phase one", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                print("ready to run the calibration tool")
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
        title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        title_l = wx.StaticText(self,  label='User Log Panel', size=(500,40))
        title_l.SetFont(title_font)
        page_sub_title =  wx.StaticText(self,  label='Record information and Log variables manually', size=(550,30))
        page_sub_title.SetFont(sub_title_font)
        user_log_location_l = wx.StaticText(self, label='User log location - ')
        self.user_log_location_tc = wx.TextCtrl(self, value="", size=(450, 30))
        # user notes
        user_notes_title =  wx.StaticText(self,  label='User Notes', size=(300,30))
        user_notes_title.SetFont(sub_title_font)
        self.ui_user_notes_list = self.user_notes_list(self, 1)
        # user log
        user_log_title =  wx.StaticText(self,  label='User Log', size=(300,30))
        user_log_title.SetFont(sub_title_font)
        self.show_log_cb = wx.CheckBox(self, label='Show')
        self.download_log_cb = wx.CheckBox(self, label='Download')
        self.show_log_cb.SetValue(True)
        self.download_log_cb.SetValue(True)
        self.ui_user_log_list = self.user_log_list(self, 1)
        # user log info and user log field info
        user_info_title =  wx.StaticText(self,  label='Info and User Log Fields;', size=(300,30))
        user_info_title.SetFont(sub_title_font)
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
        add_box_title.SetFont(sub_title_font)
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
        link_text_sizer.Add(self.link_status_text, 1, wx.EXPAND|wx.ALIGN_CENTER)
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
                    ssh.connect(host, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
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
            MainApp.welcome_pannel.Show()
        else:
            #clear_temp_folder()
            pi_link_pnl.target_ip = self.tb_ip.GetValue()
            pi_link_pnl.target_user = self.tb_user.GetValue()
            pi_link_pnl.target_pass = self.tb_pass.GetValue()
            try:
                ssh.connect(pi_link_pnl.target_ip, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                MainApp.status.write_bar("Connected to " + pi_link_pnl.target_ip)
                print("#sb# Connected to " + pi_link_pnl.target_ip)
                log_on_test = True
            except Exception as e:
                MainApp.status.write_bar("Failed to log on due to; " + str(e))
                print(("#sb# Failed to log on due to; " + str(e)))
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)
            MainApp.window_self.Layout()

    def blank_settings(self):
        print("clearing settings")
        # clear system pannel text
        system_info_pnl.sys_hdd_total.SetLabel("")
        system_info_pnl.sys_hdd_remain.SetLabel("")
        system_info_pnl.sys_hdd_used.SetLabel("")
        system_info_pnl.sys_pigrow_folder.SetLabel("")
        system_info_pnl.sys_os_name.SetLabel("")
        #system_info_pnl.sys_pigrow_version.SetLabel("")
        system_info_pnl.sys_pigrow_update.SetLabel("")
        system_info_pnl.sys_network_name.SetLabel("")
        system_info_pnl.wifi_list.SetLabel("")
        system_info_pnl.sys_power_status.SetLabel("")
        system_info_pnl.sys_camera_info.SetLabel("")
        system_info_pnl.sys_pi_revision.SetLabel("")
        system_info_pnl.sys_pi_date.SetLabel("")
        system_info_pnl.sys_pc_date.SetLabel("")
        system_info_pnl.sys_i2c_info.SetLabel("")
        system_info_pnl.sys_uart_info.SetLabel("")
        system_info_pnl.sys_1wire_info.SetLabel("")
        MainApp.system_ctrl_pannel.i2c_baudrate_btn.Disable()
        MainApp.system_ctrl_pannel.add_1wire_btn.Disable()
        MainApp.system_ctrl_pannel.edit_1wire_btn.Disable()
        MainApp.system_ctrl_pannel.remove_1wire_btn.Disable()
        #system_info_pnl.sys_time_diff.SetLabel("")
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
            MainApp.welcome_pannel.Hide()
            MainApp.config_ctrl_pannel.Show()
            MainApp.config_info_pannel.Show()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
            cron_info_pnl.read_cron_click(MainApp.cron_info_pannel, "event")
            system_ctrl_pnl.read_system_click(MainApp.system_ctrl_pannel, "event")
            config_ctrl_pnl.update_pigrow_setup_pannel_information_click(MainApp.config_ctrl_pannel, "event")
            localfiles_ctrl_pnl.update_local_filelist_click(MainApp.localfiles_ctrl_pannel, "event")

        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("No Pigrow config file")
            MainApp.welcome_pannel.Hide()
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
            system_ctrl_pnl.read_system_click(MainApp.system_ctrl_pannel, "event")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()

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
        #view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'multi-script', 'Local Files', 'Timelapse', 'Graphs', 'Live View', 'pieye watcher']
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
        elif display == "User Logs":
            MainApp.user_log_ctrl_pannel.Show()
            MainApp.user_log_info_pannel.Show()
            #MainApp.sensors_info_pannel.sensor_table.make_sensor_table(MainApp.sensors_info_pannel.sensor_table, 'e')
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
        wx.Yield()
    def write_blue_bar(self, text):
        self.SetBackgroundColour((50, 50, 200))
        self.status_text.SetForegroundColour(wx.Colour(0,0,0))
        self.status_text.SetLabel(text)
        wx.Yield()
    def write_warning(self, text):
        self.SetBackgroundColour((200, 100, 100))
        self.status_text.SetForegroundColour(wx.Colour(0,0,0))
        self.status_text.SetLabel(text)
        wx.Yield()


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
        main_sizer.Add(MainApp.welcome_pannel, 0)
        main_sizer.Add(MainApp.system_info_pannel, 0)
        main_sizer.Add(MainApp.config_info_pannel, 0)
        main_sizer.Add(MainApp.cron_list_pannel, 0)
        main_sizer.Add(MainApp.localfiles_info_pannel, 0)
        main_sizer.Add(MainApp.graphing_info_pannel, 0)
        main_sizer.Add(MainApp.camconf_info_pannel, 0)
        main_sizer.Add(MainApp.timelapse_info_pannel, 0)
        main_sizer.Add(MainApp.sensors_info_pannel, 0)
        main_sizer.Add(MainApp.user_log_info_pannel, 0)
        MainApp.window_sizer = wx.BoxSizer(wx.VERTICAL)
        MainApp.window_sizer.Add(main_sizer, 0)
        MainApp.window_sizer.Add(MainApp.status, 1, wx.EXPAND)
        MainApp.window_sizer.Fit(self)
        self.SetSizer(MainApp.window_sizer)
        MainApp.window_self = self
        # setup the window layout
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.Layout()
        self.Centre( wx.BOTH )
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
