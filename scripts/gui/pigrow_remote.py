#!/usr/bin/python

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
#
# - useful functions
# run_on_pi(self, command)    -   Runs a command on the pigrow and returns output and error
####    out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
#
#
#

print("")
print(" THIS IS A WORK IN PROGRESS SCRIPT (ain't they all)")
print("     At the moment it does a few useful things ")
print("     enough to be kinda useful but some of it might not work properly...")
print(" !! some of it might cause problems !!")
print("  but it's like, totally awesome tho, right?")
print("")

import os
import time
import datetime
try:
    import wx
    import wx.lib.scrolledpanel
except:
    print(" You don't have WX Python installed, this makes the gui")
    print(" google 'installing wx python' for your operating system")
    print("on ubuntu try the command;")
    print("   sudo apt install python-wxgtk3.0 ")
    sys.exit(1)
try:
    import paramiko
except:
    print("  You don't have paramiko installed, this is what connects to the pi")
    print(" google 'installing paramiko python' for your operating system")
    print(" on ubuntu;")
    print(" use the command ' pip install paramiko ' to install.")
    sys.exit(1)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='System Config Menu', pos=(25, 10))
        self.read_system_btn = wx.Button(self, label='Read System Info', pos=(10, 70), size=(175, 30))
        self.read_system_btn.Bind(wx.EVT_BUTTON, self.read_system_click)
        self.update_pigrow_btn = wx.Button(self, label='update pigrow', pos=(10, 100), size=(175, 30))
        self.update_pigrow_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_click)

    def read_system_click(self, e):
        #check for hdd space
        try:
            stdin, stdout, stderr = ssh.exec_command("df -l /")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("oh! " + str(e))
        if len(responce) > 1:
            responce_list = []
            for item in responce.split(" "):
                if len(item) > 0:
                    responce_list.append(item)
            hdd_total = responce_list[-5]
            hdd_percent = responce_list[-2]
            hdd_available = responce_list[-3]
            hdd_used = responce_list[-4]
        system_info_pnl.sys_hdd_total.SetLabel(str(hdd_total) + " KB")
        system_info_pnl.sys_hdd_remain.SetLabel(str(hdd_available) + " KB")
        system_info_pnl.sys_hdd_used.SetLabel(str(hdd_used) + " KB (" + str(hdd_percent) + ")")
        #check installed OS
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("ahhh! " + str(e))
        for line in responce.split("\n"):
            if "PRETTY_NAME=" in line:
                os_name = line.split('"')[1]
        system_info_pnl.sys_os_name.SetLabel(os_name)
        #check if pigrow folder exits and read size
        try:
            stdin, stdout, stderr = ssh.exec_command("du -s ~/Pigrow/")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce, error
        except Exception as e:
            print("ahhh! " + str(e))
        if not "No such file or directory" in error:
            self.update_pigrow_btn.SetLabel("update pigrow")
            pigrow_size = responce.split("\t")[0]
            self.pigrow_folder_size = pigrow_size
            #print pigrow_size
            not_pigrow = (int(hdd_used) - int(pigrow_size))
            #print not_pigrow
            folder_pcent = float(pigrow_size) / float(hdd_used) * 100
            folder_pcent = format(folder_pcent, '.2f')
            system_info_pnl.sys_pigrow_folder.SetLabel(str(pigrow_size) + " KB (" +str(folder_pcent) + "% of used)")
        else:
            system_info_pnl.sys_pigrow_folder.SetLabel("No Pigrow folder detected")
            self.update_pigrow_btn.SetLabel("install pigrow")

        #check if git upate needed
        update_needed = False
        try:
            stdin, stdout, stderr = ssh.exec_command("git -C ~/Pigrow/ remote -v update")
            responce = stdout.read().strip()
            error = stderr.read()
            #print 'responce;' +  str(responce)
            #print 'error:' + str(error)
        except Exception as e:
            print("ooops! " + str(e))
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
                print("ERROR NO MASTER BRANCH?!!?!")
            elif count == 1:
                if "[up to date]" in master_branch:
                    print("master branch is upto date")
                else:
                    print("Master branch requires updating")
                    update_needed = True
        #print master_branch
        #Read git status
        try:
            stdin, stdout, stderr = ssh.exec_command("git -C ~/Pigrow/ status --untracked-files no")
            responce = stdout.read().strip()
            error = stderr.read()
            #print responce
            #print 'error:' + str(error)
        except Exception as e:
            print("ooops! " + str(e))
        if "Your branch and 'origin/master' have diverged" in responce:
            update_needed = 'diverged'
        elif "Your branch is" in responce:
            git_line = responce.split("\n")[1]
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

        if update_needed == True:
            system_info_pnl.sys_pigrow_update.SetLabel("update required, " + str(git_num) + " updates behind")
            self.update_type = "clean"
        elif update_needed == False:
            system_info_pnl.sys_pigrow_update.SetLabel("master branch is upto date")
        elif update_needed == 'ahead':
            system_info_pnl.sys_pigrow_update.SetLabel("you've modified the core pigrow code, caution required!")
            self.update_type = "merge"
        elif update_needed == 'diverged':
            system_info_pnl.sys_pigrow_update.SetLabel("you've modified the core pigrow code, caution required!")
            self.update_type = "merge"
        elif update_needed == 'error':
            system_info_pnl.sys_pigrow_update.SetLabel("some confusion with git, sorry.")
        #check for low power WARNING
        # not entirely sure if this works on all version of the pi, it looks to see if the power light is on
        # it's normally turned off as a LOW POWER warning
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /sys/class/leds/led1/brightness")
            responce = stdout.read().strip()
            error = stderr.read()
            if responce == "255":
                system_info_pnl.sys_power_status.SetLabel("no warning")
            else:
                system_info_pnl.sys_power_status.SetLabel("reads " + str(responce) + " low power warning!")
        except Exception as e:
            print("lookit! a problem - " + str(e))
            system_info_pnl.sys_power_status.SetLabel("unable to read")
        # WIFI
        # Read the currently connected network name
        try:
            stdin, stdout, stderr = ssh.exec_command("/sbin/iwgetid")
            responce = stdout.read().strip()
            error = stderr.read()
            print responce
            print error
            network_name = responce.split('"')[1]
            system_info_pnl.sys_network_name.SetLabel(network_name)
        except Exception as e:
            print("fiddle and fidgets! - " + str(e))
            system_info_pnl.sys_network_name.SetLabel("unable to read")

    def update_pigrow_click(self, e):
        #reads button lable for check if update or install is required
        if self.update_pigrow_btn.GetLabel() == "update pigrow":
            do_upgrade = True
        #checks to determine best git merge stratergy
            if self.update_type == "clean":
                git_command = "git -C ~/Pigrow/ pull"
            elif self.update_type == "merge":
                print("WARNING WARNING _ THIS CODE IS VERY MUCH IN THE TESTING PHASE")
                print("if you're doing odd things it's very likely to mess up!")
                #this can cause odd confusions which requires use of 'git rebase'
                #reokace command line question with dialog box
                question = raw_input("merge using default, ours or theirs?")
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
                if raw_input("type yes if you really want to update your pigrow") == "yes":
                    try:
                        stdin, stdout, stderr = ssh.exec_command(git_command)
                        responce = stdout.read().strip()
                        error = stderr.read()
                        print responce
                        if len(error) > 0:
                            print 'error:' + str(error)
                        system_info_pnl.sys_pigrow_update.SetLabel("--UPDATED--")
                    except Exception as e:
                        print("ooops! " + str(e))
                        system_info_pnl.sys_pigrow_update.SetLabel("--UPDATE ERROR--")
        elif self.update_pigrow_btn.GetLabel() == "install pigrow":
            print("Downloading Pigrow code onto Pi")
            try:
                stdin, stdout, stderr = ssh.exec_command("git clone https://github.com/Pragmatismo/Pigrow ~/")
                responce = stdout.read().strip()
                error = stderr.read()
                print responce, error
                system_info_pnl.sys_pigrow_update.SetLabel("--NEW INSTALL--")
            except Exception as e:
                print("installing a pigrow failed! " + str(e))




class system_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        png = wx.Image('./sysconf.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
        #SDcard details
        system_info_pnl.sys_hdd_total = wx.StaticText(self,  label='total;', pos=(250, 180), size=(200,30))
        system_info_pnl.sys_hdd_remain = wx.StaticText(self,  label='free;', pos=(250, 250), size=(200,30))
        system_info_pnl.sys_hdd_used = wx.StaticText(self,  label='Used;', pos=(250, 215), size=(200,30))
        system_info_pnl.sys_pigrow_folder = wx.StaticText(self,  label='Pigrow folder;', pos=(250, 285), size=(200,30))
        #Software details
        system_info_pnl.sys_os_name = wx.StaticText(self,  label='os installed;', pos=(250, 365), size=(200,30))
        system_info_pnl.sys_pigrow_version = wx.StaticText(self,  label='pigrow version;', pos=(250, 405), size=(200,30))
        system_info_pnl.sys_pigrow_update = wx.StaticText(self,  label='Pigrow update status', pos=(250, 450), size=(200,30))
        #wifi deatils
        system_info_pnl.sys_network_name = wx.StaticText(self,  label='network name', pos=(250, 535), size=(200,30))

        #camera details

        #power level warning details
        system_info_pnl.sys_power_status = wx.StaticText(self,  label='power status', pos=(625, 390), size=(200,30))

class config_ctrl_pnl(wx.Panel):
    #this controlls the data displayed on config_info_pnl
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='Pigrow Config', pos=(25, 10))
        self.update_config_btn = wx.Button(self, label='read config from pigrow', pos=(15, 60), size=(175, 30))
        self.update_config_btn.Bind(wx.EVT_BUTTON, self.update_config_click)
        self.new_gpio_btn = wx.Button(self, label='Add new device GPIO link', pos=(15, 95), size=(175, 30))
        self.new_gpio_btn.Bind(wx.EVT_BUTTON, self.add_new_device_gpio)

    def update_config_click(self, e):
        #define file locations
        pigrow_config_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/"
        pigrow_dirlocs = pigrow_config_folder + "dirlocs.txt"
        #read pigrow locations file
        try:
            stdin, stdout, stderr = ssh.exec_command("cat " + pigrow_dirlocs)
            dirlocs = stdout.read().splitlines()
        except Exception as e:
            print("reading dirlocs.txt failed; " + str(e))
        dirlocs_dict = {}
        if len(dirlocs) > 1:
            for item in dirlocs:
                try:
                    item = item.split("=")
                    #dirlocs_dict = {item[0]:item[1]}
                    dirlocs_dict[item[0]] = item[1]
                except:
                    print("!!error reading value from dirlocs; " + str(item))
        #We've now created dirlocs_dict with key:value for every setting:value in dirlocs
        #now we grab some of the important ones from the dictionary
         #folder location info (having this in a file on the pi makes it easier if doing things odd ways)
        location_msg = ""
        location_problems = []
        try:
            pigrow_path = dirlocs_dict['path']
        #    location_msg += pigrow_path + "\n"
        except:
            location_msg += ("No path locaion info in pigrow dirlocs\n")
            pigrow_path = ""
            location_problems.append("path")
        try:
            pigrow_logs_path = dirlocs_dict['log_path']
        #    location_msg += pigrow_logs_path + "\n"
        except:
            location_msg += ("No logs locaion info in pigrow dirlocs\n")
            pigrow_logs_path = ""
            location_problems.append("log_path")
        try:
            pigrow_graph_path = dirlocs_dict['graph_path']
        #    location_msg += pigrow_graph_path + "\n"
        except:
            location_msg += ("No graph locaion info in pigrow dirlocs\n")
            pigrow_graph_path = ""
            location_problems.append("graph_path")
        try:
            pigrow_caps_path = dirlocs_dict['caps_path']
        #    location_msg += pigrow_caps_path + "\n"
        except:
            location_msg += ("No caps locaion info in pigrow dirlocs\n")
            pigrow_caps_path = ""
            location_problems.append("caps_path")

         #settings file locations
        try:
            pigrow_settings_path = dirlocs_dict['loc_settings']
        except:
            location_msg += ("No pigrow config file locaion info in pigrow dirlocs\n")
            pigrow_settings_path = ""
            location_problems.append("loc_settings")
        try:
            pigrow_cam_settings_path = dirlocs_dict['camera_settings']
        except:
            location_msg +=("no camera settings file locaion info in pigrow dirlocs (optional)\n")
            pigrow_cam_settings_path = ""

         # log file locations
        try:
            pigrow_err_log_path = dirlocs_dict['err_log']
        except:
            location_msg += ("No err log locaion info in pigrow dirlocs\n")
            pigrow_err_log_path = ""
            location_problems.append("err_log")
        try:
            pigrow_self_log_path = dirlocs_dict['self_log']
        except:
            location_msg += ("No self_log locaion info in pigrow dirlocs (optional)\n")
            pigrow_self_log_path = ""
        try:
            pigrow_switchlog_path = dirlocs_dict['loc_switchlog']
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
        #read pigrow config file
        try:
            stdin, stdout, stderr = ssh.exec_command("cat " + pigrow_settings_path)
            pigrow_settings = stdout.read().splitlines()
        except Exception as e:
            print("reading dirlocs.txt failed; " + str(e))
        #define empty dictionaries
        config_dict = {}
        gpio_dict = {}
        gpio_on_dict = {}
        #go through the setting file and put them in the correct dictionary
        if len(pigrow_settings) > 1:
            for item in pigrow_settings:
                try:
                    item = item.split("=")
                    line_split = item[0].split("_")
                    if line_split[0] == 'gpio' and not item[1] == "":
                        if len(line_split) == 2:
                            gpio_dict[line_split[1]] = item[1]
                        elif len(line_split) == 3:
                            gpio_on_dict[str(line_split[1])] = item[1]
                    else:
                        config_dict[item[0]] = item[1]
                except:
                    print("!!error reading value from config file; " + str(item))
        # we've now created config_dict with a list of all the items in the config file
        #   and gpio_dict and gpio_on_dict with gpio numbers and low/high pin direction info

        #unpack non-gpio information from config file
        config_problems = []
        config_msg = ''
        dht_msg = ''
        #lamp timeing
        if "lamp" in gpio_dict:
            if "time_lamp_on" in config_dict:
                lamp_on_hour = int(config_dict["time_lamp_on"].split(":")[0])
                lamp_on_min = int(config_dict["time_lamp_on"].split(":")[1])

            else:
                config_msg += "lamp on time not set\n"
                config_problems.append('lamp')
            if "time_lamp_off" in config_dict:
                lamp_off_hour = int(config_dict["time_lamp_off"].split(":")[0])
                lamp_off_min = int(config_dict["time_lamp_off"].split(":")[1])
            else:
                config_msg += "lamp off time not set\n"
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
            config_msg += "Lamp turning on at " + str(on_time)[:-3] + " and off at " + str(off_time)[:-3]
            config_msg += " (" + str(length_lamp_on)[:-3] + " on, "  +str(aday - length_lamp_on)[:-3] + " off)\n"
        else:
            config_msg += "no lamp linked to gpio, ignoring lamp timing settings\n"
     #heater on and off temps
        if "heater" in gpio_dict:
            if "heater_templow" in config_dict:
                heater_templow =  config_dict["heater_templow"]
                config_msg += "Temp low; " + str(heater_templow)
            else:
                config_msg += "\nheater low temp not set\n"
                config_problems.append('heater_templow')
            if "heater_temphigh" in config_dict:
                heater_temphigh = config_dict["heater_temphigh"]
                config_msg += " temp high: " + str(heater_temphigh) + " (Centigrade)\n"
            else:
                config_msg += "heater high temp not set\n"
                config_problems.append('heater_temphigh')
        else:
            config_msg += "no heater linked to gpio, ignoring heater temp settings\n"
        # read humid info
        if "humid" in gpio_dict or "dehumid" in gpio_dict:
            if "humid_low" in config_dict:
                humid_low = config_dict["humid_low"]
                config_msg += "humidity low; " + str(humid_low)
            else:
                config_msg += "\nHumid low not set\n"
                config_problems.append('humid_low')
            if "humid_high" in config_dict:
                humid_high = config_dict["humid_high"]
                config_msg += " humidity high: " + str(humid_high) + "\n"
            else:
                config_msg += "humid high not set\n"
                config_problems.append('heater_temphigh')
        else:
            config_msg += "no humidifier or dehumidifier linked to gpio"

        #add gpio message to the message text
        config_msg += "We have " + str(len(gpio_dict)) + " devices linked to the GPIO\n"
        if "dht22sensor" in gpio_dict:
            dht_msg += "DHT Sensor on pin " + str(gpio_dict['dht22sensor'] + "\n")
            if "log_frequency" in config_dict:
                log_frequency = config_dict["log_frequency"]
                dht_msg += "Logging dht every " + str(log_frequency) + " seconds. \n"
            else:
                log_frequency = ""
                dht_msg += "DHT Logging frequency not set\n"
                config_problems.append('dht_log_frequency')
            #check to see if log location is set in dirlocs.txt
            try:
                dht_msg += "logging to; " + dirlocs_dict['loc_dht_log'] + "\n"
            except:
                dht_msg += "No DHT log locaion in pigrow dirlocs\n"
                pigrow_dht_log_path = ""
                config_problems.append('dht_log_location')
        else:
            dht_msg += "DHT Sensor not linked\n"
        #checks to see if gpio devices with on directions are also linked to a gpio pin and counts them
        relay_list_text = "Device - Pin - Switch direction for power on - current device state"
        for key in gpio_on_dict:
            if key in gpio_dict:
                info = ''
                self.add_to_GPIO_list(str(key), gpio_dict[key], gpio_on_dict[key], info=info)
        #listing config problems at end of config messsage
        if len(config_problems) > 0:
            config_msg += "found " + len(config_problems) + " config problems; "
        for item in config_problems:
            config_msg += item + ", "
        #putting the info on the screen
        config_info_pnl.config_text.SetLabel(config_msg)
        config_info_pnl.dht_text.SetLabel(dht_msg)

    def add_new_device_gpio(self, e):
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
            print device, gpio, wiring
            config_ctrl_pnl.add_to_GPIO_list(MainApp.config_ctrl_pannel, device, gpio, wiring, currently='UNLINKED')
        else:
            print "cancelled"

    def check_device_status(self, gpio_pin, on_power_state):
        #Checks if a device is on or off by reading the pin and compairing to the relay wiring direction
        try:
            ssh.exec_command("echo "+ str(gpio_pin) +" > /sys/class/gpio/export")
            stdin, stdout, stderr = ssh.exec_command("cat /sys/class/gpio/gpio" + str(gpio_pin) + "/value") # returns 0 or 1
            gpio_status = stdout.read().strip()
            gpio_err = stderr.read().strip()
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
        except Exception as e:
            print("Error asking pi about gpio status; " + str(e))
            return "error " + str(e)
        return device_status

    def add_to_GPIO_list(self, device, gpio, wiring, currently='', info=''):
        #config_ctrl_pnl.add_to_GPIO_list(self, device, gpio, wiring, currently='', info='')
        if currently == '':
            currently = self.check_device_status(gpio, wiring)
        config_info_pnl.gpio_table.InsertStringItem(0, str(device))
        config_info_pnl.gpio_table.SetStringItem(0, 1, str(gpio))
        config_info_pnl.gpio_table.SetStringItem(0, 2, str(wiring))
        config_info_pnl.gpio_table.SetStringItem(0, 3, str(currently))
        config_info_pnl.gpio_table.SetStringItem(0, 4, str(info))


class config_info_pnl(wx.Panel):
    #  This displays the config info
    # controlled by the config_ctrl_pnl
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        ## Draw UI elements
        png = wx.Image('./config_info.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
        #SDcard details
        config_info_pnl.location_text = wx.StaticText(self,  label='locations', pos=(25, 130), size=(200,30))
        config_info_pnl.config_text = wx.StaticText(self,  label='config', pos=(10, 210), size=(200,30))
        config_info_pnl.dht_text = wx.StaticText(self,  label='dht', pos=(10, 415), size=(200,30))
        config_info_pnl.gpio_table = self.GPIO_list(self, 1)
        config_info_pnl.gpio_table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_GPIO)

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



class doubleclick_gpio_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing device gpio config data
    def __init__(self, *args, **kw):
        super(doubleclick_gpio_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((400, 200))
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
                print out   # shows box with switch info from pigrow
                if not error == "": print error
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
        self.SetSize((750, 300))
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
        png = wx.Image('./relaydialogue.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
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

class cron_info_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        wx.StaticText(self,  label='Cron Config Menu', pos=(25, 10))
        self.read_cron_btn = wx.Button(self, label='Read Crontab', pos=(10, 40), size=(175, 30))
        self.read_cron_btn.Bind(wx.EVT_BUTTON, self.read_cron_click)
        self.new_cron_btn = wx.Button(self, label='New cron job', pos=(10, 80), size=(175, 30))
        self.new_cron_btn.Bind(wx.EVT_BUTTON, self.new_cron_click)
        self.update_cron_btn = wx.Button(self, label='Update Cron', pos=(10, 120), size=(175, 30))
        self.update_cron_btn.Bind(wx.EVT_BUTTON, self.update_cron_click)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS

        bSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer.Add(self.read_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.new_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.update_cron_btn, 0, wx.ALL, 5)
        self.SetSizer(bSizer)

    def update_cron_click(self, e):
        #make a text file of all the cron jobs
        cron_text = ''
        startup_num = cron_list_pnl.startup_cron.GetItemCount()
        for num in range(0, startup_num):
            cron_line = ''
            if cron_list_pnl.startup_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += '@reboot ' + cron_list_pnl.startup_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
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
            print "Updating remote cron"
            # save cron text onto pigrow as text file then import into cron
            sftp = ssh.open_sftp()
            try:
                tempfolder = '/home/pi/Pigrow/temp'
                sftp.mkdir(tempfolder)
            except IOError:
                pass
            f = sftp.open(tempfolder + '/remotecron.txt', 'w')
            f.write(cron_text)
            f.close()
            try:
                stdin, stdout, stderr = ssh.exec_command("crontab " + tempfolder + '/remotecron.txt')
                responce = stdout.read()
                error = stderr.read()
                print responce, error
            except Exception as e:
                print("this ain't right, it just ain't right! " + str(e))
        else:
            print("Updating cron cancelled")
        mbox.Destroy()
        #refresh cron list
        self.read_cron_click("event")


    def read_cron_click(self, event):
        #reads pi's crontab then puts jobs in correct table
        try:
            stdin, stdout, stderr = ssh.exec_command("crontab -l")
            cron_text = stdout.read().split('\n')
        except Exception as e:
            print("oh - that didn't work! " + str(e))
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
                    print job_enabled, timing_string, cron_jobtype, cron_task, cron_extra_args, cron_comment
                    if cron_jobtype == 'reboot':
                        self.add_to_startup_list(line_number, job_enabled, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'one time':
                        self.add_to_onetime_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'repeating':
                        self.add_to_repeat_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def test_if_script_running(self, script):
        stdin, stdout, stderr = ssh.exec_command("pidof -x " + str(script))
        script_text = stdout.read().strip()
        #error_text = stderr.read().strip()
        if script_text == '':
            return False
        else:
            #print 'pid of = ' + str(script_text)
            return True

    def add_to_startup_list(self, line_number, job_enabled, cron_task, cron_extra_args='', cron_comment=''):
        is_running = self.test_if_script_running(cron_task)
        cron_list_pnl.startup_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.startup_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.startup_cron.SetStringItem(0, 2, str(is_running))   #tests if script it currently running on pi
        cron_list_pnl.startup_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.startup_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.startup_cron.SetStringItem(0, 5, cron_comment)

    def add_to_repeat_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.repeat_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.repeat_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.repeat_cron.SetStringItem(0, 2, timing_string)
        cron_list_pnl.repeat_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.repeat_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.repeat_cron.SetStringItem(0, 5, cron_comment)

    def add_to_onetime_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.timed_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.timed_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.timed_cron.SetStringItem(0, 2, timing_string)
        cron_list_pnl.timed_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.timed_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.timed_cron.SetStringItem(0, 5, cron_comment)

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
        cron_info_pnl.cron_path_toedit = '/home/pi/Pigrow/scripts/cron/'
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
            self.SetColumnWidth(3, 650)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

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
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

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
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    def __init__( self, parent ):
        #find size
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )

        wx.StaticText(self,  label='Cron start up;', pos=(5, 10))
        cron_list_pnl.startup_cron = self.startup_cron_list(self, 1, pos=(5, 40), size=(w_space_left-10, 200))
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_startup)
        wx.StaticText(self,  label='Repeating Jobs;', pos=(5,245))
        cron_list_pnl.repeat_cron = self.repeating_cron_list(self, 1, pos=(5, 280), size=(w_space_left-10, 200))
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        wx.StaticText(self,  label='One time triggers;', pos=(5,500))
        cron_list_pnl.timed_cron = self.other_cron_list(self, 1, pos=(5, 530), size=(w_space_left-10, 200))
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)

    # TESTING CODE WHILE SCRIPT WRITING IS IN PROGRESS
        self.SetBackgroundColour('sea green')  ###THIS IS JUST TO TEST SIZE REMOVE TO STOP THE UGLY

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
        cron_stars = timing_string.split(' ')
        if not timing_string == 'fail':
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
            cron_rep = 'min'
            cron_num = '5'


        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = cron_rep
        cron_info_pnl.cron_everynum_toedit = cron_num
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
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
        self.SetSize((750, 300))
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
        cron_path_opts = ['/home/pi/Pigrow/scripts/cron/', '/home/pi/Pigrow/scripts/autorun/', '/home/pi/Pigrow/scripts/switches/']
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
        #opens an ssh pipe and runs a cat command to get the text of the script
        target_ip = pi_link_pnl.target_ip
        target_user = pi_link_pnl.target_user
        target_pass = pi_link_pnl.target_pass
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        script_to_ask = script_path + script_name
        try:
        #    ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
            print "Connected to " + target_ip
            print("running; cat " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command("cat " + str(script_to_ask))
            script_text = stdout.read().strip()
            error_text = stderr.read().strip()
            if not error_text == '':
                msg_text =  'Error reading script \n\n'
                msg_text += str(error_text)
            else:
                msg_text = script_to_ask + '\n\n'
                msg_text += str(script_text)
            wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            print("oh bother, this seems wrong... " + str(e))

    def get_cronable_scripts(self, script_path):
        #this opens an ssh channel and reads the files in the path provided
        #then creates a list of all .py and .sh scripts in that folder
        cron_opts = []
        try:
            print("reading " + str(script_path))
            stdin, stdout, stderr = ssh.exec_command("ls " + str(script_path))
            cron_dir_list = stdout.read().split('\n')
            for filename in cron_dir_list:
                if filename.endswith("py") or filename.endswith('sh'):
                    cron_opts.append(filename)
        except Exception as e:
            print("aggghhhhh cap'ain something ain't right! " + str(e))
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
        try:
            print("reading " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command(str(script_to_ask) + " -h")
            helpfile = stdout.read().strip()
        except Exception as e:
            print("sheee-it something ain't right! " + str(e))
        return helpfile
    def show_help(self, e):
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        helpfile = self.get_help_text(str(script_path + script_name))
        msg_text =  script_name + ' \n \n'
        msg_text += str(helpfile)
        wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
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

class localfiles_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        #set blank variables
        localfiles_info_pnl.local_path = ""
        ## Draw UI elements
        png = wx.Image('./localfiles.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))
        # placing the information boxes
        localfiles_info_pnl.local_path_txt = wx.StaticText(self,  label='local path', pos=(220, 80), size=(200,30))
        #local photo storage info
        localfiles_info_pnl.caps_folder = 'caps'
        localfiles_info_pnl.folder_text = wx.StaticText(self,  label=' ' + localfiles_info_pnl.caps_folder, pos=(720, 130), size=(200,30))
        localfiles_info_pnl.photo_text = wx.StaticText(self,  label='photo text', pos=(575, 166), size=(170,30))
        localfiles_info_pnl.first_photo_title = wx.StaticText(self,  label='first image', pos=(575, 290), size=(170,30))
        localfiles_info_pnl.last_photo_title = wx.StaticText(self,  label='last image', pos=(575, 540), size=(170,30))
        #file list boxes
        localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
        localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        localfiles_info_pnl.logs_files = self.logs_file_list(self, 1, pos=(5, 390), size=(550, 200))
        localfiles_info_pnl.logs_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_logs)
        #localfiles_info_pnl.config_files = self.config_file_list(self, 1, pos=(5, 160), size=(550, 200))
    #    localfiles_info_pnl.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_config)
        #cron info text
        localfiles_info_pnl.cron_info = wx.StaticText(self,  label='cron info', pos=(290, 635), size=(200,30))

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
        first = wx.Image(first_pic, wx.BITMAP_TYPE_ANY)
        first = first.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
        first = first.ConvertToBitmap()
        photo_folder_first_pic = wx.StaticBitmap(self, -1, first, (620, 310), (first.GetWidth(), first.GetHeight()))
        # load and display last image
        last = wx.Image(last_pic, wx.BITMAP_TYPE_ANY)
        last = last.Scale(225, 225, wx.IMAGE_QUALITY_HIGH)
        last = last.ConvertToBitmap()
        photo_folder_last_pic = wx.StaticBitmap(self, -1, last, (620, 565), (last.GetWidth(), last.GetHeight()))

    def add_to_config_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.config_files.InsertStringItem(0, str(name))
        localfiles_info_pnl.config_files.SetStringItem(0, 1, str(mod_date))
        localfiles_info_pnl.config_files.SetStringItem(0, 2, str(age))
        localfiles_info_pnl.config_files.SetStringItem(0, 3, str(update_status))

    def add_to_logs_list(self, name, mod_date, age, update_status):
        localfiles_info_pnl.logs_files.InsertStringItem(0, str(name))
        localfiles_info_pnl.logs_files.SetStringItem(0, 1, str(mod_date))
        localfiles_info_pnl.logs_files.SetStringItem(0, 2, str(age))
        localfiles_info_pnl.logs_files.SetStringItem(0, 3, str(update_status))

    def onDoubleClick_config(self, e):
        print("and nothing happens")

    def onDoubleClick_logs(self, e):
        print("and nothing happens")


class localfiles_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        # Start drawing the UI elements
        wx.StaticText(self,  label='Local file and backup options', pos=(25, 10))
        self.update_local_filelist_btn = wx.Button(self, label='Refresh Filelist Info', pos=(15, 60), size=(175, 30))
        self.update_local_filelist_btn.Bind(wx.EVT_BUTTON, self.update_local_filelist_click)
        self.download_btn = wx.Button(self, label='Download files', pos=(15, 95), size=(175, 30))
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)
        self.upload_btn = wx.Button(self, label='Restore to pi', pos=(15, 130), size=(175, 30))
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)

    def run_on_pi(self, command):
        #Runs a command on the pigrow and returns output and error
        #  out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        try:
            stdin, stdout, stderr = ssh.exec_command(command)
            out = stdout.read()
            error = stderr.read()
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            return "", error
        return out, error

    def update_local_filelist_click(self, e):
        #set local files path
        if localfiles_info_pnl.local_path == "":
            computer_username = "pragmo" #change this to make the right path for all users and operating systems
            localfiles_info_pnl.local_path = "/home/" + computer_username + "/frompigrow/" + str(pi_link_pnl.boxname) + "/"
            localfiles_info_pnl.local_path_txt.SetLabel("\n" + localfiles_info_pnl.local_path)
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
                if os.path.isdir(localfiles_info_pnl.local_path + item) == True:
                    folder_files = os.listdir(localfiles_info_pnl.local_path + item)
                    counter = 0
                    for thing in folder_files:
                        counter = counter + 1
                    folder_list.append([item, counter])
                    #add local config files to list and generate info
                    if item == "config":
                        config_list = []
                        config_files = os.listdir(localfiles_info_pnl.local_path + item)
                        for thing in config_files:
                            if thing.endswith("txt"):
                                modified = os.path.getmtime(localfiles_info_pnl.local_path + item + "/" + thing)
                                #config_list.append([thing, modified])
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_config_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    if item == "logs":
                        logs_list = []
                        logs_files = os.listdir(localfiles_info_pnl.local_path + item)
                        for thing in logs_files:
                            if thing.endswith("txt"):
                                modified = os.path.getmtime(localfiles_info_pnl.local_path + item + "/" + thing)
                                modified = datetime.datetime.fromtimestamp(modified)
                                file_age = datetime.datetime.now() - modified
                                modified = modified.strftime("%Y-%m-%d %H:%M")
                                file_age = str(file_age).split(".")[0]
                                update_status = "unchecked"
                                localfiles_info_pnl.add_to_logs_list(MainApp.localfiles_info_pannel, thing, modified, file_age, update_status)
                    #read caps info and make report
                    if item == localfiles_info_pnl.caps_folder:
                        caps_files = os.listdir(localfiles_info_pnl.local_path + item)
                        caps_files.sort()
                        caps_message = str(len(caps_files)) + " files locally \n"
                        #read pi's caps folder
                        try:
                            stdin, stdout, stderr = ssh.exec_command("ls /home/" + pi_link_pnl.target_user + "/Pigrow/" + localfiles_info_pnl.caps_folder)
                            remote_caps = stdout.read().splitlines()
                        except Exception as e:
                            print("reading remote caps folder failed; " + str(e))
                            remote_caps = []
                        if len(caps_files) > 1:
                            #lable first and last image with name
                            localfiles_info_pnl.first_photo_title.SetLabel(caps_files[0])
                            localfiles_info_pnl.last_photo_title .SetLabel(caps_files[-1])
                            #determine date range of images
                            first_date, first_dt = self.filename_to_date(caps_files[0])
                            last_date, last_dt = self.filename_to_date(caps_files[-1])
                            caps_message += "  " + str(first_date) + " - " + str(last_date)
                            length_of_local = last_dt - first_dt
                            caps_message += '\n     ' + str(length_of_local)
                            #draw first and last imagess to the screen
                            localfiles_info_pnl.draw_photo_folder_images(MainApp.localfiles_info_pannel, localfiles_info_pnl.local_path + item + "/" + caps_files[0], localfiles_info_pnl.local_path + item + "/" + caps_files[-1])
                        caps_message += "\n" + str(len(remote_caps)) + " files on Pigrow \n"
                        if len(remote_caps) > 1:
                            first_remote, first_r_dt = self.filename_to_date(remote_caps[0])
                            last_remote, last_r_dt = self.filename_to_date(remote_caps[-1])
                            caps_message += "  " + str(first_remote) + " - " + str(last_remote)
                            length_of_remote = last_r_dt - first_r_dt
                            caps_message += '\n     ' + str(length_of_remote)
                        else:
                            caps_message += " "

                        #update the caps info pannel with caps message
                        localfiles_info_pnl.photo_text.SetLabel(caps_message)


                    # check to see if crontab is saved locally
                    localfiles_ctrl_pnl.cron_backup_file = localfiles_info_pnl.local_path + "crontab_backup.txt"
                    if os.path.isfile(localfiles_ctrl_pnl.cron_backup_file) == True:
                        #checks time of local crontab_backup and determines age
                        modified = os.path.getmtime(localfiles_ctrl_pnl.cron_backup_file)
                        modified = datetime.datetime.fromtimestamp(modified)
                        file_age = datetime.datetime.now() - modified
                        modified = modified.strftime("%Y-%m-%d %H:%M")
                        file_age = str(file_age).split(".")[0]
                        #checks to see if local and remote files are the same
                        try:
                            stdin, stdout, stderr = ssh.exec_command("crontab -l")
                            remote_cron_text = stdout.read()
                        except Exception as e:
                            print("failed to read cron due to;" + str(e))
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

    def filename_to_date(self, filename):
        date = float(filename.split(".")[0].split("_")[-1])
        file_datetime = datetime.datetime.fromtimestamp(date)
        date = time.strftime('%Y-%m-%d %H:%M', time.localtime(date))
        return date, file_datetime

    def download_click(self, e):
        #show download dialog boxes
        file_dbox = file_download_dialog(None, title='Download dialog box')
        file_dbox.ShowModal()

    def upload_click(self, e):
        upload_dbox = upload_dialog(None, title='Upload dialog box')
        upload_dbox.ShowModal()

class file_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(file_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 300))
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
        self.close_btn = wx.Button(self, label='Close', pos=(415, 240), size=(175, 50))
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
            try:
                stdin, stdout, stderr = ssh.exec_command("crontab -l")
                cron_text = stdout.read()
            except Exception as e:
                print("failed to read cron due to;" + str(e))
            with open(localfiles_ctrl_pnl.cron_backup_file, "w") as file_to_save:
                file_to_save.write(cron_text)
        ## Downloading files from the pi
        # connecting the sftp pipe
        port = 22
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        print("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        # creating a list of files to be download from the pigrow
        if self.cb_all.GetValue() == False:
        # make list using selected components to be downloaded, list contains two elemnts [remote file, local destination]
            if self.cb_conf.GetValue() == True:
                local_config = localfiles_info_pnl.local_path + "config/"
                if not os.path.isdir(local_config):
                    os.makedirs(local_config)
                target_config_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                remote_config = sftp.listdir(target_config_files)
                for item in remote_config:
                    files_to_download.append([target_config_files + item, local_config + item])
            if self.cb_logs.GetValue() == True:
                local_logs = localfiles_info_pnl.local_path + "logs/"
                if not os.path.isdir(local_logs):
                    os.makedirs(local_logs)
                target_logs_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                remote_logs = sftp.listdir(target_logs_files)
                for item in remote_logs:
                    files_to_download.append([target_logs_files + item, local_logs + item])
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                if not os.path.isdir(local_pics):
                    os.makedirs(local_pics)
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                remote_caps = sftp.listdir(target_caps_files)
                for item in remote_caps:
                    if item not in listofcaps_local:
                        files_to_download.append([target_caps_files + item, local_pics + item])
            if self.cb_graph.GetValue() == True:
                target_graph_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                local_graphs = localfiles_info_pnl.local_path + "graphs/"
                if not os.path.isdir(local_graphs):
                    os.makedirs(local_graphs)
                remote_graphs = sftp.listdir(target_graph_files)
                for item in remote_graphs:
                    files_to_download.append([target_graph_files + item, local_graphs + item])
        else:
            # make list of all ~/Pigrow/ files using os.walk
            #    - this is for complete backups ignoring the file system.
            print("downloading entire pigrow folder (not yet implimented)")
        print files_to_download
        print(len(files_to_download))
        for remote_file in files_to_download:
            #grabs all files in the list and overwrites them if they already exist locally.
            self.current_file_txt.SetLabel("from; " + remote_file[0])
            self.current_dest_txt.SetLabel("to; " + remote_file[1])
            wx.Yield()
            sftp.get(remote_file[0], remote_file[1])
        self.current_file_txt.SetLabel("Done")
        self.current_dest_txt.SetLabel("--")
        #disconnect the sftp pipe
        sftp.close()
        ssh_tran.close()
        print("train has reached the depot")

    def OnClose(self, e):
        #closes the dialogue box
        self.Destroy()

class upload_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, *args, **kw):
        super(upload_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 355))
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
        self.close_btn = wx.Button(self, label='Close', pos=(415, 300), size=(175, 50))
        self.close_btn.Bind(wx.EVT_BUTTON, self.OnClose)
         ## universal controls
        pnl = wx.Panel(self)

    def start_upload_click(self, e):
        files_to_upload  = []
        ## connecting the sftp pipe
        port = 22
        ssh_tran = paramiko.Transport((pi_link_pnl.target_ip, port))
        print("  - connecting transport pipe... " + pi_link_pnl.target_ip + " port:" + str(port))
        ssh_tran.connect(username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        ## Downloading files from the pi
        # creating a list of files to be download from the pigrow
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
                try:
                    stdin, stdout, stderr = ssh.exec_command("crontab " + cron_temp)
                except Exception as e:
                    print("failed to read cron due to;" + str(e))
        # make list using selected components to be uploaded, list contains two elemnts [local file, remote destination]
            if self.cb_conf.GetValue() == True:
                local_config = localfiles_info_pnl.local_path + "config/"
                target_config = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/config/"
                local_config_files = os.listdir(local_config)
                for item in local_config_files:
                    files_to_upload.append([local_config + item, target_config + item])
            #do the same for the logs folder
            if self.cb_logs.GetValue() == True:
                local_logs = localfiles_info_pnl.local_path + "logs/"
                target_logs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/logs/"
                target_logs_files = os.listdir(local_logs)
                for item in target_logs_files:
                    files_to_upload.append([local_logs + item, target_logs + item])
            #and the graphs folder
            if self.cb_graph.GetValue() == True:
                local_graphs = localfiles_info_pnl.local_path + "graphs/"
                target_graphs = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/graphs/"
                local_graph_files = os.listdir(local_graphs)
                for item in local_graph_files:
                    files_to_upload.append([local_graphs + item, target_graphs + item])
            ## for photos only upload photos that don't already exost on pi
            if self.cb_pics.GetValue() == True:
                caps_folder = localfiles_info_pnl.caps_folder
                local_pics = localfiles_info_pnl.local_path + caps_folder + "/"
                #get list of pics we already have
                listofcaps_local = os.listdir(local_pics)
                #get list of remote images
                target_caps_files = "/home/" + str(pi_link_pnl.target_user) + "/Pigrow/" + caps_folder + "/"
                remote_caps = sftp.listdir(target_caps_files)
                for item in listofcaps_local:
                    if item not in remote_caps:
                        files_to_upload.append([local_pics + item, target_caps_files + item])
        else:
            # make list of all ~/Pigrow/ files using os.walk
            #    - this is for complete backups ignoring the file system.
            print("restoring entire pigrow folder (not yet implimented)")
        print files_to_upload
        print(len(files_to_upload))
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



class pi_link_pnl(wx.Panel):
    #
    # Creates the pannel with the raspberry pi data in it
    # and connects ssh to the pi when button is pressed
    # or allows seeking
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0,0), size = wx.Size( 285,190 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        pi_link_pnl.target_ip = ''
        pi_link_pnl.target_user = ''
        pi_link_pnl.target_pass = ''
        pi_link_pnl.config_location_on_pi = '/home/pi/Pigrow/config/pigrow_config.txt'
     ## the three boxes for pi's connection details, IP, Username and Password
        self.l_ip = wx.StaticText(self,  label='address', pos=(10, 20))
        self.tb_ip = wx.TextCtrl(self, pos=(125, 25), size=(150, 25))
        self.tb_ip.SetValue("192.168.1.")
        self.l_user = wx.StaticText(self,  label='Username', pos=(10, 60))
        self.tb_user = wx.TextCtrl(self, pos=(125, 60), size=(150, 25))
        self.tb_user.SetValue("pi")
        self.l_pass = wx.StaticText(self,  label='Password', pos=(10, 95))
        self.tb_pass = wx.TextCtrl(self, pos=(125, 95), size=(150, 25))
        self.tb_pass.SetValue("raspberry")
     ## link with pi button
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi', pos=(10, 125), size=(175, 30))
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --', pos=(25, 160))
     ## seek next pi button
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek next', pos=(190,125))
        self.seek_for_pigrows_btn.Bind(wx.EVT_BUTTON, self.seek_for_pigrows_click)
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
                print("Trying to connect to " + host)
                try:
                    ssh.connect(host, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                    print("Connected to " + host)
                    log_on_test = True
                    stdin, stdout, stderr = ssh.exec_command("cat " + pi_link_pnl.config_location_on_pi  + " | grep box_name")
                    box_name = stdout.read().strip().split("=")[1]
                    print("Pigrow Found; " + box_name)
                    self.set_link_pi_text(log_on_test, box_name)
                    return box_name #this just exits the loop
                except paramiko.AuthenticationException:
                    print("Authentication failed when connecting to " + str(host))
                except Exception as e:
                    print("Could not SSH to " + host + " because:" + str(e))
                    seek_attempt += 1
                if seek_attempt == number_of_tries_per_host + 1:
                    print("Could not connect to " + host + " Giving up")
                    break #end while loop and look at next host

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            print("breaking ssh connection")
            ssh.close()
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.tb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
            MainApp.welcome_pannel.Show()
        else:
            #clear_temp_folder()
            pi_link_pnl.target_ip = self.tb_ip.GetValue()
            pi_link_pnl.target_user = self.tb_user.GetValue()
            pi_link_pnl.target_pass = self.tb_pass.GetValue()
            try:
                ssh.connect(pi_link_pnl.target_ip, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                print("Connected to " + pi_link_pnl.target_ip)
                log_on_test = True
            except Exception as e:
                print("Failed to log on due to; " + str(e))
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)

    def set_link_pi_text(self, log_on_test, box_name):
        pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(pi_link_pnl.boxname))
            MainApp.welcome_pannel.Hide()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("Found raspberry pi, but not pigrow")
            MainApp.welcome_pannel.Hide()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()

    def get_box_name(self):
        boxname = None
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
            boxname = stdout.read().strip().split("=")[1]
            print "Pigrow Found; " + boxname
        except Exception as e:
            print("dang - can't connect to pigrow! " + str(e))
        if boxname == '':
            boxname = None
        return boxname


class welcome_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        png = wx.Image('./splash.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))


class view_pnl(wx.Panel):
    #
    # Creates the little pannel with the navigation tabs
    # small and simple, it changes which pannels are visible
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, 190), size = wx.Size( 285,35 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((230,200,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'multi-script', 'Local Files', 'Timelapse', 'Graphs', 'Live View', 'pieye watcher']
        self.view_cb = wx.ComboBox(self, choices = view_opts, pos=(10,2), size=(265, 30))
        self.view_cb.Bind(wx.EVT_COMBOBOX, self.view_combo_go)
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
        #show whichever pannels correlate to the option selected
        if display == 'System Config':
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
        elif display == 'Pigrow Setup':
            MainApp.config_ctrl_pannel.Show()
            MainApp.config_info_pannel.Show()
        elif display == 'Camera Config':
            print("changing window display like i'm Mr Polly on weed")
        elif display == 'Cron Timing':
            MainApp.cron_list_pannel.Show()
            MainApp.cron_info_pannel.Show()
        elif display == 'Multi-script':
            print("changing window display like i'm Mr Polly on coke")
        elif display == 'Local Files':
            MainApp.localfiles_ctrl_pannel.Show()
            MainApp.localfiles_info_pannel.Show()
        elif display == 'Timelapse':
            print("changing window display like i'm Mr Polly on crack")
        elif display == 'Graphs':
            print("changing window display like i'm Mr Polly on speed")
        elif display == 'Live View':
            print("changing window display like i'm Mr Polly on LSD")
        elif display == 'pieye watcher':
            print("changing window display like i'm Mr Polly in a daydream")
        else:
            print("!!! Option not recognised, this is a programming error! sorry")
            print("          message me and tell me about it and i'll be very thankful")

#
#
#  The main bit of the program
#           EXCITING HU?!!!?
#

class MainFrame ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.Layout()
        self.Centre( wx.BOTH )
    def __del__( self ):
        pass

class MainApp(MainFrame):
    def __init__(self, parent):
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.pi_link_pnl = pi_link_pnl(self)
        self.view_pnl = view_pnl(self)
        #
        # loads all the pages at the start then hides them,
        #         maybe i should change this later but let's make it work first
        MainApp.welcome_pannel = welcome_pnl(self)
        MainApp.system_ctrl_pannel = system_ctrl_pnl(self)
        MainApp.system_info_pannel = system_info_pnl(self)
        MainApp.config_ctrl_pannel = config_ctrl_pnl(self)
        MainApp.config_info_pannel = config_info_pnl(self)
        MainApp.cron_list_pannel = cron_list_pnl(self)
        MainApp.cron_info_pannel = cron_info_pnl(self)
        MainApp.localfiles_ctrl_pannel = localfiles_ctrl_pnl(self)
        MainApp.localfiles_info_pannel = localfiles_info_pnl(self)
        #hide all except the welcome pannel
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.config_ctrl_pannel.Hide()
        MainApp.config_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.localfiles_ctrl_pannel.Hide()
        MainApp.localfiles_info_pannel.Hide()

    def OnClose(self, e):
        #Closes SSH connection even on quit
        # need to add 'ya sure?' question if there's unsaved data
        print("Closing SSH connection")
        ssh.close()
        exit(0)


def main():
    app = wx.App()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
