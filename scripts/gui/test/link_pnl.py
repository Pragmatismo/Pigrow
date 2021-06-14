import wx
#import os
#import sys

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


class link_pnl(wx.Panel):
    #
    # Creates the pannel with the raspberry pi data in it
    # and connects ssh to the pi when button is pressed
    # or allows seeking
    #
    def __init__( self, parent, shared_data ):
        # intiation
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.shared_data = shared_data
        # pannel
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour((150,230,170))
        ## UI
        # IP address
        self.l_ip = wx.StaticText(self,  label='address')
        self.l_ip.SetFont(shared_data.button_font)
        self.tb_ip = wx.TextCtrl(self)
        self.tb_ip.SetValue(shared_data.gui_set_dict['default_address'])
        self.tb_ip.SetFont(shared_data.button_font)
        # Username
        self.l_user = wx.StaticText(self,  label='Username')
        self.l_user.SetFont(shared_data.button_font)
        self.tb_user = wx.TextCtrl(self)
        self.tb_user.SetValue(shared_data.gui_set_dict['username'])
        self.tb_user.SetFont(shared_data.button_font)
        # Password
        self.l_pass = wx.StaticText(self,  label='Password')
        self.l_pass.SetFont(shared_data.button_font)
        self.tb_pass = wx.TextCtrl(self)
        self.tb_pass.SetValue(shared_data.gui_set_dict['password'])
        self.tb_pass.SetFont(shared_data.button_font)
        # link with pi button
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi')
        self.link_with_pi_btn.SetFont(shared_data.button_font)
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label=' -- no link -- ')
        self.link_status_text.SetFont(shared_data.button_font)
        # seek next pi button
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek next')
        self.seek_for_pigrows_btn.SetFont(shared_data.button_font)
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

    #def __del__(self):
        print("psssst it did that thing, the _del_ one you like so much...")
        pass

    def seek_for_pigrows_click(self, e):
        print("seeking for pigrows...")
        number_of_tries_per_host = 1
        self.target_ip = self.tb_ip.GetValue()
        self.target_user = self.tb_user.GetValue()
        self.target_pass = self.tb_pass.GetValue()
        if self.target_ip.split(".")[3] == '':
            self.target_ip = self.target_ip + '0'
        start_from = self.target_ip.split(".")[3]
        lastdigits = len(str(start_from))
        hostrange = self.target_ip[:-lastdigits]
        #Iterate through the ip_to_test and stop when  pigrow is found
        for ip_to_test in range(int(start_from)+1,255):
            host = hostrange + str(ip_to_test)
            self.target_ip = self.tb_ip.SetValue(host)
            seek_attempt = 1
            log_on_test = False
            while True:
                print(("Trying to connect to " + host))
                try:
                    port = int(self.shared_data.gui_set_dict['ssh_port'])
                    self.ssh.connect(host, port=port, username=self.target_user, password=self.target_pass, timeout=3)
                    #MainApp.status.write_bar("Connected to " + host)
                    print(("#sb# Connected to " + host))
                    log_on_test = True
                    box_name = self.get_box_name()
                    #MainApp.status.write_bar("Pigrow Found; " + str(box_name))
                    print("#sb# Pigrow Found; " + str(box_name))
                    self.set_link_pi_text(log_on_test, box_name)
                    self.target_ip = self.tb_ip.GetValue()
                    return box_name #this just exits the loop
                except paramiko.AuthenticationException:
                    #MainApp.status.write_bar("Authentication failed when connecting to " + str(host))
                    print(("#sb# Authentication failed when connecting to " + str(host)))
                except Exception as e:
                    #MainApp.status.write_bar("Could not SSH to " + host + " because:" + str(e))
                    print(("#sb# Could not SSH to " + host + " because:" + str(e)))
                    seek_attempt += 1
                # check if final attempt and if so stop trying
                if seek_attempt == number_of_tries_per_host + 1:
                    #MainApp.status.write_bar("Could not connect to " + host + " Giving up")
                    print(("#sb# Could not connect to " + host + " Giving up"))
                    break #end while loop and look at next host

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            #MainApp.status.write_bar("breaking ssh connection")
            print("breaking ssh connection")
            self.ssh.close()
            # reset ui to connect
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.tb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
    #        self.blank_settings()
            #MainApp.welcome_pannel.Show()
            #Mainapp..view_cb.SetValue("")
            #MainApp.view_pnl.view_combo_go("e")
            #MainApp.window_self.Layout()
        else:
            #clear_temp_folder()
            self.target_ip = self.tb_ip.GetValue()
            self.target_user = self.tb_user.GetValue()
            self.target_pass = self.tb_pass.GetValue()
            try:
                port = int(self.shared_data.gui_set_dict['ssh_port'])
                self.ssh.connect(self.target_ip, port=port, username=self.target_user, password=self.target_pass, timeout=3)
                #MainApp.status.write_bar("Connected to " + self.target_ip)
                print("#sb# Connected to " + self.target_ip)
                log_on_test = True
            except Exception as e:
                #MainApp.status.write_bar("Failed to log on due to; " + str(e))
                print(("#sb# Failed to log on due to; " + str(e)))
            # when connected
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)
            #MainApp.window_self.Layout()

#    def blank_settings(self):
        return None
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
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(box_name))
            #MainApp.view_cb.SetValue("Pigrow Setup")
            #self.view_combo_go("e")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
            # Run the functions to fill the pages
            #MainApp.cron_info_pannel.read_cron_click("event")
            # MainApp.system_ctrl_pannel.read_system_click("event")
            #MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("event")
            #MainApp.localfiles_ctrl_pannel.update_local_filelist_click("event")
            # camera config
            #MainApp.camconf_info_pannel.seek_cam_configs()
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            self.ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("No Pigrow config file")
            #self.view_cb.SetValue("System Config")
            #self.view_combo_go("e")
            #MainApp.system_ctrl_pannel.read_system_click("event")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
        #MainApp.window_self.Layout()

    def run_on_pi(self, command, write_status=True):
        #Runs a command on the pigrow and returns output and error
        #  out, error = .run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        #if write_status == True:
            #MainApp.status.write_blue_bar("Running; " + command)
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            out = stdout.read()
            error = stderr.read()
            out = out.decode()
            error = error.decode()
            #if write_status == True:
            #    MainApp.status.write_bar("ready...")
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            #if write_status == True:
            #    MainApp.status.write_warning("FAILED: Check your connection")
            return "", error
        return out, error

    def update_config_file_on_pi(self, text, config_file):
        # create paths
        temp_file = config_file.split("/")[-1]
        folder = "/home/" + str(self.target_user) + "/Pigrow/temp/"
        full_path = folder + temp_file
        # open sftp link to pi and write file
        sftp = self.ssh.open_sftp()
        out, error = self.run_on_pi("mkdir " + folder)
        f = sftp.open(full_path, 'w')
        f.write(text)
        f.close()
    # add verification step
        # copy temp file into position
        copy_cmd = "sudo cp --no-preserve=mode,ownership " + full_path + " " + config_file
        out, error = self.run_on_pi(copy_cmd)
    #    if not error.strip() == "":
        print("Pi's " + config_file + " updated")
    #    else:
    #        print("Error writing " + config_file + " ; " + error )


    def get_box_name(self=None):
        boxname = None
        out, error = self.run_on_pi("cat /home/" + self.target_user + "/Pigrow/config/pigrow_config.txt | grep box_name")
        if "=" in out:
            boxname = out.strip().split("=")[1]
            #MainApp.status.write_bar("Pigrow Found; " + boxname)
            print("#sb# Pigrow Found; " + boxname)
        else:
            #MainApp.status.write_bar("Can't read Pigrow name, probably not installed")
            print("#sb# Can't read Pigrow's name ")
        if boxname == '':
            boxname = None
        return boxname
