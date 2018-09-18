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
##    MainApp.localfiles_ctrl_pannel.upload_file_to_fodler(local_path, remote_path):
#           local_path and remote_path should be full and explicit paths
####     MainApp.localfiles_ctrl_pannel.upload_file_to_fodler(localfiles_info_pnl.local_path + "temp/temp.txt", "/home/" + pi_link_pnl.target_user + "/Pigrow/temp/temp.txt")
#
#
#
###      Useful Variables - Path info
##
##  temp_local = localfiles_info_pnl.local_path + "temp/"
##  remote_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/"
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
from stat import S_ISDIR
try:
    import wx
    import  wx.lib.scrolledpanel as scrolled
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
    print("     sudo apt-get install python3-setuptools")
    print("     sudo easy_install3 pip")
    print("     pip3 install wxpython")
    print(" or")
    print("   sudo apt install python-wxgtk3.0 ")
    print("")
    print(" Note: wx must be installed for python3")
    sys.exit(1)
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
    def __init__(self, parent,  text_to_show, title, cancel=True):
        wx.Dialog.__init__(self, parent, title=(title))
        text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        btnsizer = wx.BoxSizer()
        btn = wx.Button(self, wx.ID_OK)
        btnsizer.Add(btn, 0, wx.ALL, 5)
        btnsizer.Add((5,-1), 0, wx.ALL, 5)
        if cancel==True:
            cancel_btn = wx.Button(self, wx.ID_CANCEL)
            btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
        sizer.Add(text, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizerAndFit(sizer)


#
#
## System Pannel
#
#
class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        # tab info
        self.tab_label = wx.StaticText(self,  label='System Config Menu')
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
        self.find_1wire_btn = wx.Button(self, label='1 wire check')
        self.find_1wire_btn.Bind(wx.EVT_BUTTON, self.find_1wire_devices)
        self.i2c_baudrate_btn = wx.Button(self, label='baudrate')
        self.i2c_baudrate_btn.Bind(wx.EVT_BUTTON, self.set_baudrate)
        # run command on pi button
        self.run_cmd_on_pi_btn = wx.Button(self, label='Run Command On Pi')
        self.run_cmd_on_pi_btn.Bind(wx.EVT_BUTTON, self.run_cmd_on_pi_click)

        # Sizers
        power_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_sizer.Add(self.reboot_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        power_sizer.Add(self.shutdown_pi_btn, 0, wx.ALL|wx.EXPAND, 3)
        i2c_sizer = wx.BoxSizer(wx.HORIZONTAL)
        i2c_sizer.Add(self.find_i2c_btn, 0, wx.ALL|wx.EXPAND, 3)
        i2c_sizer.Add(self.i2c_baudrate_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.tab_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.read_system_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.install_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(power_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(i2c_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.find_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.run_cmd_on_pi_btn, 0, wx.ALL|wx.EXPAND, 3)

        self.SetSizer(main_sizer)




    def find_1wire_devices(self, e):
        print("looking to see if 1wire overlay is turned on")
        #/boot/config.txt file to include the line 'dtoverlay=w1-gpio'
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat /boot/config.txt")
        config_file = out.splitlines()
        overlay_count = 0
        for line in config_file:
            line = line.strip()
            if "dtoverlay" in line and "w1-gpio" in line:
                if line[0] == "#":
                    print ("dtoverlay=w1-gpio is disabled")
                    overlay_count += 1
                    onewire_msg = "onewire overlay disabled"
                else:
                    print("dtoverlay=w1-gpio found and active")
                    overlay_count += 1
                    onewire_msg = "onewire overlay enabled"
        if overlay_count == 0:
            print("dtoverlay=w1-gpio not found in config enabled or otherwise")
            onewire_msg = "onewire overlay not in config file"
        print("looking for 1wire devices...")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /sys/bus/w1/devices")
        print(out)
        onewire_devices = out.splitlines()
        ds_temp_list = []
        for line in onewire_devices:
            if "28-" in line:
                ds_temp_list.append(line)
            else:
                print("unknown device type " + str(line))
        print(" found " + str(len(ds_temp_list)) + "ds.. temp sensors")
        print(ds_temp_list)
        system_info_pnl.sys_1wire_info.SetLabel(onewire_msg)

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
        for line in raspberry_config:
            if "dtparam=i2c_baudrate=" in line:
                line = "dtparam=i2c_baudrate=" + new_i2c_baudrate
                print (line)
            config_text = config_text + line + "\n"
        # set file path, check temp folder exists, set temp file name
        #temp_local = localfiles_info_pnl.local_path + "temp/"
        temp_local = os.path.join(localfiles_info_pnl.local_path, "temp")
        if not os.path.isdir(temp_local):
            os.makedirs(temp_local)
        temp_rasp_config = temp_local + "rasp_config.txt"
        # write file to local temp folder
        with open(temp_rasp_config, "w") as file_to_save:
            file_to_save.write(config_text)
        # copy onto the raspberry pi
        MainApp.localfiles_ctrl_pannel.upload_file_to_fodler(temp_rasp_config, "/home/pi/config_temp.txt")
        # move it into place using super user permissions
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo mv /home/pi/config_temp.txt /boot/config.txt")


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
            return "not found"
        # if i2c bus found perform aditional checks, updates the textbox and returns the bus number
        # check if baurdrate is changed in Config
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
        # returns a list of i2c addresses.
        ##
        # calsl i2c_check to locate the active i2c bus
        i2c_bus_number = self.i2c_check()
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
        return i2c_addresses

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
        system_info_pnl.sys_1wire_info = wx.StaticText(self,  label='-1 wire info (not implimented)-')

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
        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Upgrade Pigrow', pos=(20, 10))
        wx.StaticText(self,  label='Use GIT to update the Pigrow to the newest version.', pos=(5, 40))
        wx.StaticText(self,  label='Current Status;', pos=(10, 90))
        # see which files are changed locally
        wx.StaticText(self,  label='Local;', pos=(10, 120))
        local_changes_tb = wx.StaticText(self,  label='--', pos=(90, 120), size=(150,150))
        changes = self.read_git_dif()
        local_changes_tb.SetLabel(str(changes))
        # see which files are changed remotely
        wx.StaticText(self,  label='Repo;', pos=(10, 270))
        remote_changes_tb = wx.StaticText(self,  label='--', pos=(90, 270), size=(150,150))
        repo_changes, num_repo_changed_files = self.read_repo_changes()
        remote_changes_tb.SetLabel(repo_changes)
        # upgrade type
        wx.StaticText(self,  label='Local Status;', pos=(10, 350))
        upgrade_type = self.determine_upgrade_type(repo_changes)
        upgrade_type_tb = wx.StaticText(self,  label=upgrade_type, pos=(150, 350))
        # upgrade and cancel buttons
        self.upgrade_btn = wx.Button(self, label='Upgrade', pos=(15, 400), size=(175, 30))
        self.upgrade_btn.Bind(wx.EVT_BUTTON, self.upgrade_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 400), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

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
            if "deletions" in git_local_details:
                num_deletions = git_local_details.split("(+), ")[1]
                num_deletions = num_deletions.split(" deletions")[0]
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
        self.SetSize((600, 600))
        self.SetTitle("Install Pigrow")
    def InitUI(self):
        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Install Pigrow', pos=(20, 10))
        wx.StaticText(self,  label='Tool for installing pigrow code and dependencies', pos=(10, 40))
        # Installed components
        pigrow_base_check = wx.StaticText(self,  label='Pigrow base', pos=(25, 90))
        #python modules
        wx.StaticText(self,  label='Python modules;', pos=(10, 120))
        self.matplotlib_check = wx.StaticText(self,  label='Matplotlib', pos=(25, 150))
        self.adaDHT_check = wx.StaticText(self,  label='Adafruit_DHT', pos=(25, 180))
        self.start_btn = wx.Button(self, label='install', pos=(155, 180), size=(70, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.ada_dht_click)
        self.cron_check = wx.StaticText(self,  label='crontab', pos=(25, 210))
        self.praw_check = wx.StaticText(self,  label='praw', pos=(300, 150))
        self.pexpect_check = wx.StaticText(self,  label='pexpect', pos=(300, 180))
        #programs
        wx.StaticText(self,  label='Programs;', pos=(10, 240))
        self.uvccapture_check = wx.StaticText(self,  label='uvccapture', pos=(25, 270))
        self.mpv_check = wx.StaticText(self,  label='mpv', pos=(25, 300))
        self.sshpass_check = wx.StaticText(self,  label='sshpass', pos=(300, 270))
        #status text
        self.currently_doing = wx.StaticText(self,  label="Currently:", pos=(15, 340))
        self.currently_doing = wx.StaticText(self,  label='...', pos=(100, 340))
        self.progress = wx.StaticText(self,  label='...', pos=(15, 370))

        #ok and cancel buttons
        self.start_btn = wx.Button(self, label='Start', pos=(15, 400), size=(175, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(315, 400), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)
        #run initial checks
        wx.Yield() #update screen to show changes
        self.check_python_dependencies()
        wx.Yield() #update screen to show changes
        self.check_program_dependencies()

    def install_pigrow(self):
        self.currently_doing.SetLabel("using git to clone (download) pigrow code")
        self.progress.SetLabel("####~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
        self.currently_doing.SetLabel("creating folders and config")
        self.progress.SetLabel("#####~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/caps/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/graphs/")
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("mkdir ~/Pigrow/logs/")
        # make dirlocs with pi's username
        dirlocs_template, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat ~/Pigrow/config/templates/dirlocs_temp.txt")
        dirlocs_template = dirlocs_template.replace("**", str("/home/" + pi_link_pnl.target_user))
        #temp_dirlocs_local = localfiles_info_pnl.local_path + "temp/dirlocs.txt"
        temp_dirlocs_local = os.path.join(localfiles_info_pnl.local_path, "temp/dirlocs.txt")
        local_temp = os.path.join(localfiles_info_pnl.local_path, "temp")
        if not os.path.isdir(local_temp):
            os.makedirs(local_temp)
        with open(temp_dirlocs_local, "w") as temp_local:
            temp_local.write(dirlocs_template)
        MainApp.localfiles_ctrl_pannel.upload_file_to_fodler(temp_dirlocs_local, "/home/" + pi_link_pnl.target_user + "/Pigrow/config/dirlocs.txt")

        self.currently_doing.SetLabel("-")
        self.progress.SetLabel("######~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()

    def install_all_pip(self):
        #updating pip
        self.currently_doing.SetLabel("Updating PIP the python install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install -U pip")
        print (out)
        #installing dependencies with pip
        self.currently_doing.SetLabel("Using pip to install praw and pexpect")
        self.progress.SetLabel("###########~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo pip install praw pexpect")
        print (out)
        self.currently_doing.SetLabel(".")
        self.progress.SetLabel("#############~~~~~~~~~~~~~~~~")
        wx.Yield()
        return out

    def install_all_apt(self):
        #updating apt package list
        self.currently_doing.SetLabel("updating apt the system package manager on the raspberry pi")
        self.progress.SetLabel("################~~~~~~~~~~~~~~~")
        wx.Yield()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt update --yes")
        print (out, error)
        #installing dependencies with apt
        self.currently_doing.SetLabel("using apt to install matplot lib, sshpass, python-crontab")
        self.progress.SetLabel("##################~~~~~~~~~~~~~")
        wx.Yield()
        python_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install python-matplotlib sshpass python-crontab")
        print (python_dep, error)
        self.currently_doing.SetLabel("Using apt to install uvccaptre and mpv")
        self.progress.SetLabel("####################~~~~~~~~~~~")
        wx.Yield()
        image_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install uvccapture mpv")
        print (image_dep, error)
        self.currently_doing.SetLabel("..")
        self.progress.SetLabel("######################~~~~~~~~~")
        wx.Yield()

    def install_adafruit_DHT(self):
        print("starting adafruit install")
        print("installing dependencies using apt")
        self.currently_doing.SetLabel("Using apt to install adafruit_dht dependencies")
        self.progress.SetLabel("##########################~~~~~~")
        wx.Yield()
        adafruit_dep, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt --yes install build-essential python-dev python-openssl")
        print (adafruit_dep, error)
        print("- Downloading Adafruit_Python_DHT from Github")
        ada_dir = "/home/" + pi_link_pnl.target_user + "/Pigrow/resources/Adafruit_Python_DHT/"
        self.currently_doing.SetLabel("Using git to clone (download) the adafruit code")
        self.progress.SetLabel("###########################~~~~")
        wx.Yield()
        adafruit_clone, error = MainApp.localfiles_ctrl_pannel.run_on_pi("git clone https://github.com/adafruit/Adafruit_Python_DHT.git " + ada_dir)
        print((adafruit_clone, error))
        print("- Dependencies installed, running adafruit_dht : sudo python setup.py install")
        self.currently_doing.SetLabel("Using the adafruit_DHT setup.py to install the module")
        self.progress.SetLabel("#############################~~")
        wx.Yield()
        adafruit_install, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo python "+ ada_dir +" setup.py install")
        print(adafruit_install, error)
        self.currently_doing.SetLabel("...")
        self.progress.SetLabel("##############################~")
        wx.Yield()
        print (adafruit_install)

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
        if "mpv" in working_programs:
            self.mpv_check.SetForegroundColour((75,200,75))
        else:
            self.mpv_check.SetForegroundColour((255,75,75))
        if "sshpass" in working_programs:
            self.sshpass_check.SetForegroundColour((75,200,75))
        else:
            self.sshpass_check.SetForegroundColour((255,75,75))


    def check_python_dependencies(self):
        python_dependencies = ["matplotlib", "Adafruit_DHT", "praw", "pexpect", "crontab"]
        working_modules = []
        nonworking_modules = []
        for module in python_dependencies:
            #print module
#this mess is the code that gets run on the pi
            module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
#that gets run with bash on the pi in this next line
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python -c " + module_question)
        # this is the old way that doesn't always work
            #out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("python -m " + str(module))
            #if len(out) > 0:
            #    working_modules.append(module)
            #    print("WARNING I THINK THAT MODULE " + module + " may have just run... it's probably fine though." )
            #elif len(error) > 0:
            #    if not "is a package and cannot be directly executed" in error and not "No code object available for" in error:
            #        nonworking_modules.append(module)
            #    else:
            #        working_modules.append(module)
        # that was the old way
            if "True" in out:
                working_modules.append(module)
            else:
                nonworking_modules.append(module)
        # colour UI
        if "matplotlib" in working_modules:
            self.matplotlib_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib_check.SetForegroundColour((255,75,75))
        wx.Yield()
        if "Adafruit_DHT" in working_modules:
            self.adaDHT_check.SetForegroundColour((75,200,75))
        else:
            self.adaDHT_check.SetForegroundColour((255,75,75))
        if "crontab" in working_modules:
            self.cron_check.SetForegroundColour((75,200,75))
        else:
            self.cron_check.SetForegroundColour((255,75,75))
        if "praw" in working_modules:
            self.praw_check.SetForegroundColour((75,200,75))
        else:
            self.praw_check.SetForegroundColour((255,75,75))
        if "pexpect" in working_modules:
            self.pexpect_check.SetForegroundColour((75,200,75))
        else:
            self.pexpect_check.SetForegroundColour((255,75,75))

    def start_click(self, e):
        print("Install process started;")
        self.progress.SetLabel("##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        self.install_pigrow()
        self.progress.SetLabel("#######~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.Yield()
        pip_text = self.install_all_pip()
        self.progress.SetLabel("##############~~~~~~~~~~~~~~~~~")
        wx.Yield()
        self.install_all_apt()
        self.progress.SetLabel("#######################~~~~~~~~")
        wx.Yield()
        self.install_adafruit_DHT()
        self.progress.SetLabel("####### INSTALL COMPLETE ######")
        wx.Yield()
        self.start_btn.Disable()
        self.cancel_btn.SetLabel("OK")

    def ada_dht_click(self, e):
        self.install_adafruit_DHT()
        self.progress.SetLabel("####### INSTALLED adafruit dht22 module ######")
        wx.Yield()


    def cancel_click(self, e):
        self.Destroy()

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
        self.config_dht_btn = wx.Button(self, label='config dht')
        self.config_dht_btn.Bind(wx.EVT_BUTTON, self.config_dht_click)
        self.new_gpio_btn = wx.Button(self, label='Add new relay device')
        self.new_gpio_btn.Bind(wx.EVT_BUTTON, self.add_new_device_relay)
        self.update_config_btn = wx.Button(self, label='read config from pigrow')
        self.update_config_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_setup_pannel_information_click)
        self.update_settings_btn = wx.Button(self, label='update pigrow settings')
        self.update_settings_btn.Bind(wx.EVT_BUTTON, self.update_setting_file_on_pi_click)
        #sizers
        self.main_sizer =  wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(self.config_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.update_config_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.update_settings_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.name_box_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.dht_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.config_dht_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.relay_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.config_lamp_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.new_gpio_btn , 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.SetSizer(self.main_sizer)




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
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_settings_path)
        pigrow_settings = out.splitlines()
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
            MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("e")

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
            gpio_config_block += "\ngpio_" + device + "=" + gpio
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
                    #MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("e")


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

class config_lamp_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing the lamp timing settings
    def __init__(self, *args, **kw):
        super(config_lamp_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 600))
        self.SetTitle("Config Lamp")
    def InitUI(self):
        #
        on_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[0])
        on_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_on"].split(":")[1])
        off_hour = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[0])
        off_min = int(MainApp.config_ctrl_pannel.config_dict["time_lamp_off"].split(":")[1])

        # draw the pannel and text
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Lamp Config;', pos=(20, 10))
        # hour on - first line
        wx.StaticText(self,  label='on time', pos=(10, 50))
        self.on_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(on_hour), pos=(80, 35), size=(60, 50))
        self.on_hour_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label=':', pos=(145, 50))
        self.on_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(on_min), pos=(155, 35), size=(60, 50))
        self.on_min_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        # length on on period - second line
        wx.StaticText(self,  label='Lamp on for ', pos=(25, 100))
        self.on_period_h_spin = wx.SpinCtrl(self, min=0, max=23, value="", pos=(130, 85), size=(60, 50))
        self.on_period_h_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label='hours and ', pos=(195, 100))
        self.on_period_m_spin = wx.SpinCtrl(self, min=0, max=59, value="", pos=(280, 85), size=(60, 50))
        self.on_period_m_spin.Bind(wx.EVT_SPINCTRL, self.on_spun)
        wx.StaticText(self,  label='min', pos=(345, 100))
        # off time - third line (worked out by above or manual input)
        wx.StaticText(self,  label='off time', pos=(10, 150))
        self.off_hour_spin = wx.SpinCtrl(self, min=0, max=23, value=str(off_hour), pos=(80, 135), size=(60, 50))
        self.off_hour_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        wx.StaticText(self,  label=':', pos=(145, 150))
        self.off_min_spin = wx.SpinCtrl(self, min=0, max=59, value=str(off_min), pos=(155, 135), size=(60, 50))
        self.off_min_spin.Bind(wx.EVT_SPINCTRL, self.off_spun)
        # cron timing of switches
        wx.StaticText(self,  label='Cron Timing of Switches;', pos=(10, 250))
        wx.StaticText(self,  label='Current                          New', pos=(50, 280))
        lamp_on_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_on.py").strip()
        lamp_off_string = MainApp.config_ctrl_pannel.get_cron_time("lamp_off.py").strip()
        wx.StaticText(self,  label=" on;", pos=(20, 310))
        wx.StaticText(self,  label="off;", pos=(20, 340))
        self.cron_lamp_on = wx.StaticText(self,  label=lamp_on_string, pos=(60, 310))
        self.cron_lamp_off = wx.StaticText(self,  label=lamp_off_string, pos=(60, 340))
        new_on_string = (str(on_min) + " " + str(on_hour) + " * * *")
        new_off_string = (str(off_min) + " " + str(off_hour) + " * * *")
        self.new_on_string_text = wx.StaticText(self,  label=new_on_string, pos=(220, 310))
        self.new_off_string_text = wx.StaticText(self,  label=new_off_string, pos=(220, 340))
        # set lamp period values
        on_period_hour, on_period_min = self.calc_light_period(on_hour, on_min, off_hour, off_min)
        self.on_period_h_spin.SetValue(on_period_hour)
        self.on_period_m_spin.SetValue(on_period_min)
        #ok and cancel buttons
        self.ok_btn = wx.Button(self, label='Ok', pos=(15, 450), size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(250, 450), size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

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
            MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("e")
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
        print("does nothing")
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
        print("nothing happens")
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
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string = '*'
        if repeat == 'hour':
            if int(repeat_num) in range(0,23):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'day':
            if int(repeat_num) in range(1,31):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'month':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'dow':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
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
        cron_repeat_l = wx.StaticText(self,  label='Repeating Jobs;')
        cron_list_pnl.repeat_cron = self.repeating_cron_list(self, 1)
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        cron_timed_l = wx.StaticText(self,  label='One time triggers;')
        cron_list_pnl.timed_cron = self.other_cron_list(self, 1)
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)
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
        wx.StaticText(self,  label='cron type;', pos=(165, 10))
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
        blank_img = wx.EmptyBitmap(255, 255)
        localfiles_info_pnl.photo_folder_first_pic = wx.StaticBitmap(self, -1, blank_img, size=(255, 255))
        localfiles_info_pnl.last_photo_title = wx.StaticText(self,  label='last image')
        localfiles_info_pnl.photo_folder_last_pic = wx.StaticBitmap(self, -1, blank_img, size=(255, 255))
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
            first = first.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
            first = first.ConvertToBitmap()
            localfiles_info_pnl.photo_folder_first_pic.SetBitmap(first)
        except:
            print("!! First image in local caps folder didn't work.")
        # load and display last image
        try:
            last = wx.Image(last_pic, wx.BITMAP_TYPE_ANY)
            last = last.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
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
        print("and nothing happens")

    def onDoubleClick_logs(self, e):
        print("and nothing happens")

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
        self.clear_downed_btn = wx.Button(self, label='clear downloaded\n from pigrow')
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
                the_remote_file = os.path.join(pi_caps_path, the_remote_file)
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
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            return "", error
        if write_status == True:
            MainApp.status.write_bar("ready...")
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
            localfiles_info_pnl.local_path_txt.SetLabel("no local data, press download to create folder \n " + localfiles_info_pnl.local_path)
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
                        # local caps files
                        if len(caps_files) > 1:
                            #lable first and last image with name
                            localfiles_info_pnl.first_photo_title.SetLabel(caps_files[0])
                            localfiles_info_pnl.last_photo_title.SetLabel(caps_files[-1])
                            #determine date range of images

                            first_date, first_dt = self.filename_to_date(caps_files[0])
                            last_date, last_dt = self.filename_to_date(caps_files[-1])
                            if not last_dt == None and not first_dt == None:
                                caps_message += "  " + str(first_date) + " - " + str(last_date)
                                length_of_local = last_dt - first_dt
                                caps_message += '\n     ' + str(length_of_local)
                            #draw first and last imagess to the screen
                            first_image_path = os.path.join(item_path, caps_files[0])
                            final_image_path = os.path.join(item_path, caps_files[-1])
                            localfiles_info_pnl.draw_photo_folder_images(MainApp.localfiles_info_pannel, first_image_path, final_image_path)
                        caps_message += "\n" + str(len(remote_caps)) + " files on Pigrow \n"
                        # remote image files
                        if len(remote_caps) > 1:
                            first_remote, first_r_dt = self.filename_to_date(remote_caps[0])
                            last_remote, last_r_dt = self.filename_to_date(remote_caps[-1])
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

    def upload_file_to_fodler(self, local_path, remote_path):
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
        win_height = gui_set.height_of_window
        win_width = gui_set.width_of_window
        w_space_left = win_width - 285
        scrolled.ScrolledPanel.__init__ ( self, parent, id = wx.ID_ANY, size = wx.Size(w_space_left , win_height-20), style = wx.HSCROLL|wx.VSCROLL )
        ## Draw UI elements
        graphing_info_pnl.graph_txt = wx.StaticText(self,  label='Graphs;')
        # Sizers
        self.graph_sizer = wx.BoxSizer(wx.VERTICAL)
        #self.graph_sizer.Add(wx.StaticText(self,  label='problem'), 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer =  wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(graphing_info_pnl.graph_txt, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_sizer, 0, wx.ALL, 0)
        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

class graphing_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        # Start drawing the UI elements
        #graphing engine selection
        make_graph_l = wx.StaticText(self,  label='Make graphs on;')
        graph_opts = ['Pigrow', 'local']
        self.graph_cb = wx.ComboBox(self, choices = graph_opts)
        self.graph_cb.Bind(wx.EVT_COMBOBOX, self.graph_engine_combo_go)
        # shared buttons
        self.make_graph_btn = wx.Button(self, label='Make Graph')
        self.make_graph_btn.Bind(wx.EVT_BUTTON, self.make_graph_click)
        self.download_graph = wx.CheckBox(self, label='download')
        self.download_graph.SetValue(True)
        #
        ### for pi based graphing only
        self.pigraph_text = wx.StaticText(self,  label='Graphing directly on the pigrow\n saves having to download logs')
        # select graphing script
        self.script_text = wx.StaticText(self,  label='Graphing Script;')
        select_script_opts = ['BLANK']
        self.select_script_cb = wx.ComboBox(self, choices = select_script_opts)
        self.select_script_cb.Bind(wx.EVT_COMBOBOX, self.select_script_combo_go)
        script_opts_opts = ['BLANK']
        self.opts_cb = wx.ComboBox(self, choices = script_opts_opts)
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
        # hideing all pigrow graphing UI elements until graph on pigrow is selected
        self.pigraph_text.Hide()
        self.script_text.Hide()
        self.select_script_cb.Hide()
        self.get_opts_tb.Hide()
        self.blank_options_ui_elements()
        #self.opts_cb.Hide()
        #self.opts_text.Hide()
        #self.command_line_opts_value_list_cb.Hide()
        #self.add_arg_btn.Hide()

        # Sizers
        make_graph_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        make_graph_sizer.Add(self.make_graph_btn, 0, wx.ALL|wx.EXPAND, 3)
        make_graph_sizer.Add(self.download_graph, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(make_graph_l, 0, wx.ALL|wx.EXPAND, 3)
        self.main_sizer.Add(self.graph_cb, 0, wx.ALL|wx.EXPAND, 3)
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
        self.SetSizer(self.main_sizer)


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

    def graph_engine_combo_go(self, e):
        # combo box selects if you want to make graphs on pi or locally
        # then shows the relevent UI elements for that option.
        graph_mode = self.graph_cb.GetValue()
        if graph_mode == 'Pigrow':
            select_script_opts = self.get_graphing_scripts()
            self.pigraph_text.Show()
            self.script_text.Show()
            self.select_script_cb.Show()
            self.select_script_cb.Clear()
            for x in select_script_opts:
                self.select_script_cb.Append(x)
            self.get_opts_tb.Show()
        if graph_mode == 'local':
            self.pigraph_text.Hide()
            self.script_text.Hide()
            self.select_script_cb.Hide()
            self.get_opts_tb.Hide()
            print("Yah, that's not really an option yet...")
        MainApp.graphing_ctrl_pannel.Layout()
        MainApp.window_self.Layout()

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
        self.camconf_path_tc = wx.TextCtrl(self, value="cam config path", size=(350, 30))
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
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
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
        self.take_unset_btn = wx.Button(self, label='  Take\n  cam\ndefault', size=(95, 60))
        self.take_unset_btn.Bind(wx.EVT_BUTTON, self.take_unset_click)
        self.take_set_btn = wx.Button(self, label='      Take\n      using\nlocal settings', size=(95, 60))
        self.take_set_btn.Bind(wx.EVT_BUTTON, self.take_set_click)
        self.take_s_set_btn = wx.Button(self, label='      Take\n      using\nsaved settings', size=(95, 60))
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
        self.take_range_btn = wx.Button(self, label='  Take\n  \nrange')
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
        take_single_photo_btns_sizer.Add(self.take_unset_btn, 0, wx.ALL|wx.EXPAND, 0)
        take_single_photo_btns_sizer.Add(self.take_set_btn, 0, wx.ALL|wx.EXPAND, 0)
        take_single_photo_btns_sizer.Add(self.take_s_set_btn, 0, wx.ALL|wx.EXPAND, 0)
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
        main_sizer.Add(take_single_photo_btns_sizer, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(range_sizer, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)


    def read_cam_config_click(self, e):
        #
        try:
            MainApp.camconf_info_pannel.camconf_path_tc.SetValue(MainApp.config_ctrl_pannel.dirlocs_dict['camera_settings'])
        except:
            raise
            MainApp.camconf_info_pannel.camconf_path_tc.SetValue("none")
            print("Camera config not set in dirlocs")
        #
        pi_cam_settings_path = MainApp.camconf_info_pannel.camconf_path_tc.GetValue()
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pi_cam_settings_path)
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
    #    chgdep = upload_dialog(None, title='upload settings to pi')
    #    chgdep.ShowModal()
    #    name_of_file = chgdep.settings_file_name
    #    chgdep.Destroy()
        filename_dbox = wx.TextEntryDialog(self, 'Upload config file with name, \n\nChange when using more than one camera', 'Upload config to Pi?', 'camera_settings.txt')
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
        remote_path = MainApp.config_ctrl_pannel.dirlocs_dict['path']
        remote_conf_path = os.path.join(remote_path, 'config/', cam_config_file_name)
        MainApp.localfiles_ctrl_pannel.upload_file_to_fodler(local_cam_settings_file, remote_conf_path)


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
        outpath = '/home/' + pi_link_pnl.target_user + '/Pigrow/temp/'
        cmd = '/home/' + pi_link_pnl.target_user + '/Pigrow/scripts/cron/camcap.py caps=' + outpath
        out, error = MainApp.localfiles_ctrl_pannel.run_on_pi(cmd)
        output = out + error
        print (out, error)
        path = output.split("Saving image to:")[1].strip()
        print (path)
        img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, path, "/temp/test_settings.jpg")
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
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, remote_img_path, "/temp/test_settings.jpg")
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
            img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, photo_path, "/temp/" + picture_name)
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
        img_path = localfiles_ctrl_pnl.download_file_to_folder(MainApp.localfiles_ctrl_pannel, remote_img_path, "/temp/test_defaults.jpg")
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
        blank_img = wx.EmptyBitmap(400, 400)
        self.first_img_l = wx.StaticText(self,  label='-first image- (date)')
        self.first_image = wx.StaticBitmap(self, -1, blank_img, size=(400, 400))
        first_prev_btn = wx.Button(self, label='<')
        self.first_frame_no = wx.TextCtrl(self, size=(75, 25), style=wx.TE_CENTRE)
        first_next_start_btn = wx.Button(self, label='>')
        self.last_img_l = wx.StaticText(self,  label='-last image- (date)')
        self.last_image = wx.StaticBitmap(self, -1, blank_img, size=(400, 400))
        last_prev_btn = wx.Button(self, label='<')
        self.last_frame_no = wx.TextCtrl(self, size=(75, 25), style=wx.TE_CENTRE)
        last_next_start_btn = wx.Button(self, label='>')
        # information area - left GridSizer
        self.images_found_l = wx.StaticText(self,  label='Images found')
        self.images_found_info = wx.StaticText(self,  label='-images found-')
        self.spare_l = wx.StaticText(self,  label='spare')
        self.spare_info = wx.StaticText(self,  label='-spare-')
        # graph area - right side
        self.size_graph = wx.StaticBitmap(self, -1, blank_img, size=(400, 400))
        # sizers
        # image area
        first_img_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        first_img_buttons_sizer.Add(first_prev_btn, 0, wx.ALL, 2)
        first_img_buttons_sizer.Add(self.first_frame_no, 0, wx.ALL, 2)
        first_img_buttons_sizer.Add(first_next_start_btn, 0, wx.ALL, 2)
        first_img_sizer = wx.BoxSizer(wx.VERTICAL)
        first_img_sizer.Add(self.first_img_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        first_img_sizer.Add(self.first_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        first_img_sizer.Add(first_img_buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        last_img_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        last_img_buttons_sizer.Add(last_prev_btn, 0, wx.ALL, 2)
        last_img_buttons_sizer.Add(self.last_frame_no, 0, wx.ALL, 2)
        last_img_buttons_sizer.Add(last_next_start_btn, 0, wx.ALL, 2)
        last_img_sizer = wx.BoxSizer(wx.VERTICAL)
        last_img_sizer.Add(self.last_img_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
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
        lower_half_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lower_half_sizer.AddStretchSpacer(1)
        lower_half_sizer.Add(info_panel_sizer, 0, wx.ALL, 3)
        lower_half_sizer.AddStretchSpacer(1)
        lower_half_sizer.Add(self.size_graph, 0, wx.ALL, 3)
        lower_half_sizer.AddStretchSpacer(1)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(img_panels_sizer, 0, wx.ALL, 3)
        main_sizer.Add(lower_half_sizer, 0,  wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

class timelapse_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        # Capture controlls
        quick_capture_l = wx.StaticText(self,  label='Quick Capture')
        capture_start_btn = wx.Button(self, label='Start capture')
        capture_start_btn.Bind(wx.EVT_BUTTON, self.start_capture_click)
        # path options
        path_l = wx.StaticText(self,  label='Path')
        open_caps_folder_btn = wx.Button(self, label='Open Caps Folder')
        open_caps_folder_btn.Bind(wx.EVT_BUTTON, self.open_caps_folder_click)
        outfile_l = wx.StaticText(self,  label='Outfile')
        out_file_tc = wx.TextCtrl(self)
        # render controlls
        render_l = wx.StaticText(self,  label='Render')
        make_timelapse_btn = wx.Button(self, label='Make Timelapse')
        make_timelapse_btn.Bind(wx.EVT_BUTTON, self.make_timelapse_click)
        play_timelapse_btn = wx.Button(self, label='Play')
        play_timelapse_btn.Bind(wx.EVT_BUTTON, self.play_timelapse_click)

        # Sizers
        capture_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        capture_bar_sizer.Add(quick_capture_l, 0, wx.ALL|wx.EXPAND, 3)
        capture_bar_sizer.Add(capture_start_btn, 0, wx.ALL|wx.EXPAND, 3)
        file_name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_name_sizer.Add(outfile_l, 0, wx.ALL, 3)
        file_name_sizer.Add(out_file_tc, 1, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        file_bar_sizer.Add(path_l, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer.Add(open_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 3)
        file_bar_sizer.Add(file_name_sizer, 0, wx.ALL|wx.EXPAND, 3)
        render_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        render_buttons_sizer.Add(make_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_buttons_sizer.Add(play_timelapse_btn, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer =  wx.BoxSizer(wx.VERTICAL)
        render_bar_sizer.Add(render_l, 0, wx.ALL|wx.EXPAND, 3)
        render_bar_sizer.Add(render_buttons_sizer, 0, wx.ALL|wx.EXPAND, 3)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(capture_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(file_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(render_bar_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)

        self.SetSizer(main_sizer)

    def start_capture_click(self, e):
        print("Doesn't do anything yet!")

    def make_timelapse_click(self, e):
        print("Doesn't do anything yet!")

    def open_caps_folder_click(self, e):
        # opens the caps folder being used in local files tab and finds all images
        capsdir = os.path.join(localfiles_info_pnl.local_path, localfiles_info_pnl.caps_folder)
        cap_type = "jpg"
        self.cap_file_paths = []
        motion_files = []
        for filefound in os.listdir(capsdir):
            if filefound.endswith(cap_type):
                file_path = os.path.join(capsdir, filefound)
                self.cap_file_paths.append(file_path)
        self.cap_file_paths.sort()
        MainApp.timelapse_info_pannel.images_found_info.SetLabel(str(len(self.cap_file_paths)))
        # set first and last images
        try:
            first = wx.Image(self.cap_file_paths[0], wx.BITMAP_TYPE_ANY)
            first = first.Scale(400, 400, wx.IMAGE_QUALITY_HIGH)
            first = first.ConvertToBitmap()
            MainApp.timelapse_info_pannel.first_image.SetBitmap(first)
            MainApp.timelapse_info_pannel.first_frame_no.SetValue("0")
            MainApp.timelapse_info_pannel.first_img_l.SetLabel(self.cap_file_paths[0].split("/")[-1] + str(" (add date here)"))
        except:
            print("!! First image in local caps folder didn't work for timelapse tab.")
        try:
            last = wx.Image(self.cap_file_paths[-1], wx.BITMAP_TYPE_ANY)
            last = last.Scale(400, 400, wx.IMAGE_QUALITY_HIGH)
            last = last.ConvertToBitmap()
            MainApp.timelapse_info_pannel.last_image.SetBitmap(last)
            MainApp.timelapse_info_pannel.last_frame_no.SetValue(str(len(self.cap_file_paths)))
            MainApp.timelapse_info_pannel.last_img_l.SetLabel(self.cap_file_paths[-1].split("/")[-1] + str(" (add date here)"))
        except:
            print("!! Last image in local caps folder didn't work for timelapse tab.")

        #print(self.cap_file_paths)


    def play_timelapse_click(self, e):
        print("Doesn't do anything yet!")

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
                             if extra_name in job_extra:
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
            print(" Selected item - " + name + " - " + type + " - " + loc + " - " + extra + " - " + timing_string)
            if type == 'chirp':
                MainApp.sensors_info_pannel.sensor_list.s_name = name
                MainApp.sensors_info_pannel.sensor_list.s_log = log
                MainApp.sensors_info_pannel.sensor_list.s_loc = loc
                MainApp.sensors_info_pannel.sensor_list.s_extra = extra
                MainApp.sensors_info_pannel.sensor_list.s_timing = timing_string
                edit_chirp_dbox = chirp_dialog(None)
                edit_chirp_dbox.ShowModal()

class sensors_ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
    #    sensor_opts = ["Soil Moisture"]
    #    self.sensor_cb = wx.ComboBox(self, choices = sensor_opts, pos=(10,30), size=(265, 30))
    #    self.sensor_cb.Bind(wx.EVT_COMBOBOX, self.sensor_combo_go)
        #
        # THE FOLLOWING IS PROBABLY SHITE
        #
        # Soil Moisture Controlls
        #
    #    soil_sensor_opts = ["Soil Moisture"]
    #    self.soil_sensor_cb = wx.ComboBox(self, choices = soil_sensor_opts, pos=(10,130), size=(265, 30))
    #    self.soil_sensor_cb.Bind(wx.EVT_COMBOBOX, self.soil_sensor_combo_go)
        #
        #
        # Refresh page button
        self.make_table_btn = wx.Button(self, label='make table')
        self.make_table_btn.Bind(wx.EVT_BUTTON, MainApp.sensors_info_pannel.sensor_list.make_sensor_table)
        #    --  Chirp options
        self.chirp_l = wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
        self.config_chirp_btn = wx.Button(self, label='add new chirp')
        self.config_chirp_btn.Bind(wx.EVT_BUTTON, self.add_new_chirp_click)
        self.address_chirp_btn = wx.Button(self, label='change chirp address')
        self.address_chirp_btn.Bind(wx.EVT_BUTTON, self.address_chirp_click)
        #
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
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def add_new_chirp_click(self, e):
        print("adding a new chirp sensor")
        # set black variables
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        log_path = ""
        if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
            log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"]
        MainApp.sensors_info_pannel.sensor_list.s_log = log_path
        MainApp.sensors_info_pannel.sensor_list.s_loc = ":"
        MainApp.sensors_info_pannel.sensor_list.s_extra = "min:,max:"
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

    def soil_sensor_combo_go(self, e):
        if self.soil_sensor_cb.GetValue() == "chirp":
            print("Selected Chirp")

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
            sensor_chirp01_extra=min:100,max:1000,etc:,etc:etc,etc
     The gui uses it in the sensor table on the sensors tab;
         sensor_table
            0   name = chirp01
            1   type = chirp
            2   log = /home/pi/Pigrow/logs/chirp01.txt
            3   loc = i2c:0x31
            4   extra = min:100,max:1000,etc:,etc:etc,etc # split with "," to make lists
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
        if "," in self.s_extra:
            extras = self.s_extra.split(",")
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
        print("oh shit this is gonna get cray-cray")
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
        o_min = self.min_tc.GetValue()
        o_max = self.max_tc.GetValue()
        min_max = "min:" + o_min + ",max:" + o_max + ","
        o_extra = min_max + self.extra_tc.GetValue()
        if o_extra[-1] == ",":
            o_extra = o_extra[:-1]
        # print("adding; ")
        # print(o_name)
        # print(o_type)
        # print(o_log)
        # print(o_loc)
        # print(o_extra)
        # print("______")
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
        if self.timing_string == new_timing_string:
            print(" -- Timing string didn't change -- ")
        else:
            print(" !!! cron job needs to change for this sensor, not doing it tho !!! ")

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            print("!-!-!-! CONFIG SETTINGS CHANGED !-!-!-!")
            MainApp.sensors_info_pannel.sensor_list.add_to_sensor_list(o_name,o_type,o_log,o_loc,o_extra)
            print(" MOVE THE LINE ABOVE THIS TO THE CORRECT LOCATION")
            print(" IT NEEDS TO GO AFTER THE DBOX HAS BEEN CALLED AND PULL THE INFO")
            print(" SO IT CAN DECIDE IF IT NEEDS TO ADD NEW OR UPDATE THE LINE")
            print("                    ##yawn##")
            print("")
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_type"] = o_type
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_log"] = o_log
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_loc"] = o_loc
            MainApp.config_ctrl_pannel.config_dict["sensor_" + o_name + "_extra"] = o_extra
            print(MainApp.config_ctrl_pannel.config_dict)
            MainApp.config_ctrl_pannel.update_setting_file_on_pi_click('e')
        self.Destroy()

    def OnClose(self, e):
        MainApp.sensors_info_pannel.sensor_list.s_name = ""
        MainApp.sensors_info_pannel.sensor_list.s_log = ""
        MainApp.sensors_info_pannel.sensor_list.s_loc = ""
        MainApp.sensors_info_pannel.sensor_list.s_extra = ""
        MainApp.sensors_info_pannel.sensor_list.s_timing = ""
        self.Destroy()


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
        #system_info_pnl.sys_time_diff.SetLabel("")
        # clear config ctrl text and tables
        try:
            MainApp.config_ctrl_pannel.dirlocs_dict.clear()
            MainApp.config_ctrl_pannel.config_dict.clear()
            MainApp.config_ctrl_pannel.gpio_dict.clear()
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

        blank = wx.EmptyBitmap(220, 220)
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
        graphing_info_pnl.graph_img_box.SetBitmap(blank)
        graphing_ctrl_pnl.blank_options_ui_elements(MainApp.graphing_ctrl_pannel)
        MainApp.graphing_ctrl_pannel.graph_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.select_script_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.opts_cb.SetValue("")
        MainApp.graphing_ctrl_pannel.pigraph_text.Hide()
        MainApp.graphing_ctrl_pannel.script_text.Hide()
        MainApp.graphing_ctrl_pannel.select_script_cb.Hide()
        MainApp.graphing_ctrl_pannel.get_opts_tb.Hide()



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

    def get_box_name(self):
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
        view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'Local Files', 'Timelapse', 'Graphs', 'Sensors']
        self.view_cb = wx.ComboBox(self, choices = view_opts)
        self.view_cb.Bind(wx.EVT_COMBOBOX, self.view_combo_go)
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
        self.view_pnl = view_pnl(self)
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
        MainApp.status.write_bar("ready...")
        # Sizers
        # left bar
        MainApp.side_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        MainApp.side_bar_sizer.Add(MainApp.pi_link_pnl, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(self.view_pnl, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.system_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.config_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.cron_info_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.localfiles_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.graphing_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.camconf_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.timelapse_ctrl_pannel, 0, wx.EXPAND)
        MainApp.side_bar_sizer.Add(MainApp.sensors_ctrl_pannel, 0, wx.EXPAND)
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
