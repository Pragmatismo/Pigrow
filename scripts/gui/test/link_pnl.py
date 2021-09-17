import wx
import os
import sys
import time
from getmac import get_mac_address
import wx.lib.delayedresult as delayedresult
import  wx.lib.newevent

FileDownloadEvent, EVT_FILE_DOWNLOAD = wx.lib.newevent.NewEvent()
#SomeNewCommandEvent, EVT_SOME_NEW_COMMAND_EVENT = wx.lib.newevent.NewCommandEvent()

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
        self.selected_files   = []
        self.selected_folders = []
        self.parent = parent
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
        list_of_ips = ["000.000.00.000"] # self.discover_ip_list()
        self.cb_ip = wx.ComboBox(self, choices = list_of_ips)
        self.cb_ip.SetFont(shared_data.button_font)
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
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek IPs')
        self.seek_for_pigrows_btn.SetFont(shared_data.button_font)
        self.seek_for_pigrows_btn.Bind(wx.EVT_BUTTON, self.seek_for_pigrows_click)
        ##  sizers
        login_sizer = wx.FlexGridSizer(3, 2, 3, 5)
        login_sizer.AddMany( [(self.l_ip, 0, wx.EXPAND),
            (self.cb_ip, 2, wx.EXPAND),
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

        # This code to get around the fontsize being ignored, possibly unneeded on win
        size = self.cb_ip.GetSize()
        self.cb_ip.Clear()
        size[0] = size[0]  * 1.2
        self.cb_ip.SetMinSize(size)
        self.cb_ip.SetValue(shared_data.gui_set_dict['default_address'])

    def discover_ip_list(self):
        default_ip = self.parent.shared_data.gui_set_dict['default_address']
        ip_ranges = ["192.168.0.", "192.168.1."]
        # read mac addresses of all devices on ip_range
        raspi_ips = []
        other_ips = []
        for ip_range in ip_ranges:
            for x in range(0,255):
                ip_mac = get_mac_address(ip=ip_range + str(x))
                if not ip_mac == None:
                    if not "00:00:00" in ip_mac:
                        if "b8:27:eb" in ip_mac:
                            raspi_ips.append(ip_range + str(x))
                        else:
                            other_ips.append(ip_range + str(x))
        # read ipv6 addresses
        ip6_mac = get_mac_address(ip6="::1")
        # combine lsts
        final_ip_list = raspi_ips
        if not other_ips == []:
            final_ip_list += ["-----"] + other_ips
        if not ip6_mac == None:
            final_ip_list += ["-----"] + ip6_mac
        if other_ips == [] and raspi_ips == []:
            return ip6_mac
        return final_ip_list

    def seek_for_pigrows_click(self, e):
        self.cb_ip.Clear()
        self.cb_ip.Append(self.discover_ip_list())

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

    #def __del__(self):
    #    print("psssst it did that thing, the _del_ one you like so much...")
    #    pass

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            #MainApp.status.write_bar("breaking ssh connection")
            print("breaking ssh connection")
            self.ssh.close()
            # reset ui to connect
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.cb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
    #        self.blank_settings()
            #MainApp.welcome_pannel.Show()
            #Mainapp..view_cb.SetValue("")
            #MainApp.view_pnl.view_combo_go("e")
            #MainApp.window_self.Layout()
            self.set_shared_info_on_connect("")
        else:
            #clear_temp_folder()
            self.target_ip = self.cb_ip.GetValue()
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
            self.set_shared_info_on_connect(box_name)
            #MainApp.window_self.Layout()

    def set_link_pi_text(self, log_on_test, box_name):
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(box_name))
            #MainApp.view_cb.SetValue("Pigrow Setup")
            #self.view_combo_go("e")
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.cb_ip.Disable()
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
            self.cb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()

    def set_shared_info_on_connect(self, box_name):
        shared_data = self.parent.shared_data
        if not box_name == "" and not box_name == None:
            shared_data.frompi_path = os.path.join(shared_data.frompi_base_path, box_name)
            shared_data.remote_pigrow_path = "/home/" + self.tb_user.GetValue() + "/Pigrow/"
            self.parent.tell_pnls_connected()
        else:
            shared_data.frompi_path = ""
            shared_data.remote_pigrow_path = ""

    # Commands for use by other sections of the gui

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

    def write_textfile_to_pi(self, text, location):
        '''
          text     - string containing file to be written
          location - full path on the pi to write to
        '''
        sftp = self.ssh.open_sftp()
        try:
            folder = os.path.split(location)[0]
            sftp.mkdir(folder)
        except IOError:
            pass
        f = sftp.open(location, 'w')
        f.write(text)
        f.close()

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

    '''
    # write text file to pi
    self.parent.parent.link_pnl.write_textfile_to_pi( trigger_file_text, pi_trigger_events_file )

    # check file is valid
    cmd = "cat " + pi_trigger_events_file
    out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
    out = "".join(l + "\n" for l in out.splitlines() if l)
    if out.strip() == trigger_file_text.strip():
        print(" - Copied trigger file matches expected text. ")
    else:
        print(" - ERROR - copied trigger file does not match expected text! reverted to original")
        cmd = "mv " + backup_events_file + " " + pi_trigger_events_file
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        msg_text = "There was an error copying the file, the written file did not match the expected text changes not saved."
        dbox = wx.MessageDialog(self, msg_text, "Error", wx.OK | wx.ICON_ERROR)
        dbox.ShowModal()
        dbox.Destroy()
    '''

    # download files

    def download_file_to_folder(self, remote_file, local_name):
        '''
          Downloads a single file into the frompigrow local folder
                 remote_file - full path to file on pi
                  local_name - doesn't require .../frompigrow/boxname/
          local_path = link_pnl.download_file_to_folder(remote_file, local_name)
        '''
        local_base_path = self.parent.shared_data.frompi_path
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
        port = int(self.parent.shared_data.gui_set_dict['ssh_port'])
        print("  - connecting transport pipe... " + self.target_ip + " port:" + str(port))
        print("    to  download " + remote_file + " to " + local_path)
        ssh_tran = paramiko.Transport((self.target_ip, port))
        ssh_tran.connect(username=self.target_user, password=self.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        self.sftp.get(remote_file, local_path)
        self.sftp.close()
        ssh_tran.close()
        print(("    file copied to " + str(local_path)))
        return local_path

    def download_folder(self, folder, overwrite=True, dest=None, extra_files=[]):
        print("Downloading folder - ", folder, " overwrite = ", str(overwrite))
        if type(folder) == type('str'):
            if folder == "":
                return None
            folder = [folder]
        if len(folder) == 0 and len(extra_files) == 0:
            return None
        # connect sftp pipe
        port = int(self.parent.shared_data.gui_set_dict['ssh_port'])
        ssh_tran = paramiko.Transport((self.target_ip, port))
        ssh_tran.connect(username=self.target_user, password=self.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        # create list of files
        self.files_to_download = []
        for fold in folder:
            if type(fold) == type('str'):
                # determine save location from path
                if 'Pigrow' in fold:
                    base = fold.split('Pigrow')[1]
                    base = base[1:]
                elif self.target_user in fold:
                    base = fold.split(self.target_user)[1]
                else:
                    base = fold
                local_base = self.parent.shared_data.frompi_path
                local_f = os.path.join(local_base, base)
            #    print("lol")
            else:
                # when handed [remote, local] paths
                local_f = fold[1]
                fold = fold[0]

            # make folder if it doesn't exist
            if not os.path.isdir(local_f):
                os.makedirs(local_f)
            # create list of from and to paths
            f_file_list = self.sftp.listdir(fold)
            for item in f_file_list:
                if overwrite == True:
                    local_item = os.path.join(local_f, item)
                    self.files_to_download.append([fold + "/" + item, local_item])
                else:
                    local_item = os.path.join(local_f, item)
                    if not os.path.isfile(local_item):
                        self.files_to_download.append([fold + "/" + item, local_item])
        # open dialogue box which displays from and to info then closes when done or cancelled
        self.files_to_download = self.files_to_download + extra_files
        print ("files to download", self.files_to_download)
        if not len(self.files_to_download) == 0:
            print("Downlaoding ", len(self.files_to_download), " files")
            file_dbox = files_download_dialog(self, self.parent)
            file_dbox.ShowModal()
            #file_dbox.Destroy()

        #disconnect the sftp pipe
        self.sftp.close()
        ssh_tran.close()

    def select_files_on_pi(self, single_folder=False, create_file=False, default_path=""):
        print("selecting files on pi")
        self.single_folder = single_folder
        self.create_file   = create_file
        self.default_path  = default_path
        select_file_dbox = select_files_on_pi_dialog(self, self.parent)
        select_file_dbox.ShowModal()

   # upload files

    def upload_files(self, file_list):
        port = int(self.parent.shared_data.gui_set_dict['ssh_port'])
        print("  - connecting transport pipe... " + self.target_ip + " port:" + str(port))
        print("    to  upload ", len(file_list), "files")
        ssh_tran = paramiko.Transport((self.target_ip, port))
        ssh_tran.connect(username=self.target_user, password=self.target_pass)
        self.sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        for file in file_list:
            local_path, remote_path = file
            self.sftp.put(local_path, remote_path)
        self.sftp.close()
        ssh_tran.close()
        print(("    file copied to " + str(local_path)))



class select_files_on_pi_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.single_folder = parent.single_folder
        self.create_file   = parent.create_file
        self.default_path  = parent.default_path
        self.parent.selected_folders = []
        self.parent.selected_files   = []
        super(select_files_on_pi_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 500))
        self.SetTitle("Select file on pi")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        #draw the pannel
        label = wx.StaticText(self,  label='Select file or folder;')
        # folder
        if self.default_path == "":
            s_path = self.parent.parent.shared_data.remote_pigrow_path
        else:
            s_path = os.path.split(self.default_path)[0]

        self.folder_path = wx.StaticText(self,  label=s_path)
        self.up_a_level_btn = wx.Button(self, label='..')
        self.up_a_level_btn.Bind(wx.EVT_BUTTON, self.up_a_level_click)
        folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        folder_sizer.Add(self.folder_path, 0, wx.ALL|wx.EXPAND, 5)
        folder_sizer.Add(self.up_a_level_btn, 0, wx.ALL, 5)
        # files
        if self.single_folder == True:
            print("Single Folder mode activated ")
            self.file_list = wx.ListCtrl(self, size=(600,300), style=wx.LC_REPORT|wx.BORDER_SUNKEN|wx.LC_SINGLE_SEL)
        else:
            self.file_list = wx.ListCtrl(self, size=(600,300), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.file_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.DoubleClick_filelist)
        if self.create_file == True:
            self.file_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.selected_item)
        self.file_list.InsertColumn(0, 'Filename')
        self.file_list.InsertColumn(1, 'size')
        self.file_list.InsertColumn(2, 'modified')
        self.fill_filelist()
        # buttons
        self.select_file_btn = wx.Button(self, label='Select')
        self.select_file_btn.Bind(wx.EVT_BUTTON, self.select_item_click)
        self.cancel_btn = wx.Button(self, label='Cancel')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.select_file_btn, 0, wx.ALL|wx.EXPAND, 5)
        button_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        # for creating a file rather than selecting one
        if self.create_file == True:
            filename_l = wx.StaticText(self, label="Filename")
            fn = os.path.split(self.default_path)[1]
            self.filename_tc = wx.TextCtrl(self, value=fn, size=(600,30))
            filename_sizer = wx.BoxSizer(wx.HORIZONTAL)
            filename_sizer.Add(filename_l, 0, wx.ALL, 5)
            filename_sizer.Add(self.filename_tc, 0, wx.ALL|wx.EXPAND, 5)

        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(folder_sizer, 0, wx.LEFT|wx.EXPAND, 25)
        main_sizer.Add(self.file_list, 0, wx.LEFT|wx.EXPAND, 25)
        if self.create_file == True:
            main_sizer.Add(filename_sizer, 0, wx.LEFT|wx.EXPAND, 25)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(button_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def selected_item(self, e):
        selected_num = self.file_list.GetFocusedItem()

        colour = self.file_list.GetItemTextColour(selected_num)
        name = self.file_list.GetItem(selected_num, 0).GetText()
        if not colour == (90, 100, 190, 255):
            self.filename_tc.SetValue(str(name))

    def fill_filelist(self):
        current_folder = self.folder_path.GetLabel()
        out, error = self.parent.parent.link_pnl.run_on_pi("ls -d " + current_folder + "*/")
        p_folders = []
        for item in out.splitlines():
            item = item.replace(current_folder, "")
            item = item.replace("/", "")
            p_folders.append(item)
        cmd = "ls " + current_folder + " -G -g --time-style=long --group-directories-first"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        p_files = out.splitlines()
        self.file_list.DeleteAllItems()
        p_files.reverse()
        for item in p_files:
            if ":" in item:  ### items over a year old show year not time
                name = str(item.split(":")[1])[2:].strip()
                modified = item.replace(name, "").strip()[-16:]
                size = item.replace(modified, "").replace(name, "").strip().split(" ")[-1]
                count = item.replace(modified, "").replace(name, "").replace(size, "").strip().split(" ")[-1]
                count = str(int(count) - 2)
                if not name in p_folders:
                    # normal colour
                    self.file_list.InsertItem(0, str(name))
                    self.file_list.SetItem(0, 1, str(size))
                    self.file_list.SetItem(0, 2, str(modified))
                else:
                    # colour blue
                    self.file_list.InsertItem(0, str(name))
                    self.file_list.SetItem(0, 1, str(count))
                    self.file_list.SetItem(0, 2, str(modified))
                    self.file_list.SetItemTextColour(0, (90, 100, 190))
        # Set column sizes to fit new data
        self.file_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.file_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.file_list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

    def up_a_level_click(self, e):
        current_folder = self.folder_path.GetLabel()
        from pathlib import Path
        p = Path(current_folder)
        self.folder_path.SetLabel(str(p.parent).replace("\", "/") + "/")
        self.fill_filelist()

    def OnClose(self, e):
        print(" Closing the dialog box without doing anything")
        self.selected_files = []
        self.parent.selected_folders = []
        self.parent.selected_files   = []
        self.Destroy()

    def DoubleClick_filelist(self, e):
        current_folder = self.folder_path.GetLabel()
        index =  e.GetIndex()
        name = self.file_list.GetItem(index, 0).GetText()
        colour = self.file_list.GetItemTextColour(index)
        print("colour", str(colour))
        if colour == (90, 100, 190, 255):
            new_path = current_folder + name + "/"
            new_path.replace("\", "/")
            self.folder_path.SetLabel(new_path)
            self.Layout()
            self.fill_filelist()
        else:
            print("Not doing anthing with files when double clicked on, lol")
            file_selected = current_folder + name
            print("doubeclick selected - ", file_selected)

    def select_item_click(self, e):
        local_base = self.parent.shared_data.frompi_path
        current_folder = self.folder_path.GetLabel()
        if self.create_file == True:
            filename = self.filename_tc.GetValue()
            if filename == "":
                return None
            item = current_folder + filename
            self.parent.selected_files.append(item)

        else:
            first_selected = self.file_list.GetNextSelected(-1)
            s_count = self.file_list.GetSelectedItemCount()
            s_folder_list = []
            if s_count == 1:
                print("one thing")
            elif s_count == 0:
                print("no file selected, using folder")
                s_folder_list.append(current_folder)

            s_file_list = []
            selected_more = True
            selected_num = -1
            while selected_more == True:
                selected_num = self.file_list.GetNextSelected(selected_num)
                if selected_num == -1:
                    selected_more = False
                else:
                    colour = self.file_list.GetItemTextColour(selected_num)
                    name = self.file_list.GetItem(selected_num, 0).GetText()
                    if colour == (90, 100, 190, 255):
                        s_folder_list.append(current_folder + name + "/")
                    else:
                        local_f = os.path.join(local_base, name) #local_base should be changed to using the location of the file on the pi with folders and sub folders
                        s_file_list.append([current_folder + name, local_f])
            #print(self.file_list.GetFocusedItem())
            #print(self.file_list.GetNextSelected(-1))
            if self.single_folder == True and len(s_folder_list) == 0:
                filename = s_file_list[0][0]
                folder = os.path.dirname(filename)
                s_file_list = []
                s_folder_list = [folder]
            print("folders ", s_folder_list)
            print("files ", s_file_list)

            for item in s_folder_list:
                self.parent.selected_folders.append(item)
            for item in s_file_list:
                self.parent.selected_files.append(item)

        self.Destroy()


class files_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(files_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.Bind(EVT_FILE_DOWNLOAD, self.handler)
        self.SetSize((700, 200))
        self.SetTitle("Downloading")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.jobID = 0
        self.abortEvent = delayedresult.AbortEvent()
        delayedresult.startWorker(self._resultConsumer, self._resultProducer,
                                  wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

    def InitUI(self):
        #draw the pannel
        label = wx.StaticText(self,  label='Downloading files from Pigrow;')
        self.current_file_txt = wx.StaticText(self,  label='from: ')
        self.current_dest_txt = wx.StaticText(self,  label='  to: ')
        self.cancel_btn = wx.Button(self, label='Cancel')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.current_file_txt, 0, wx.LEFT|wx.EXPAND, 25)
        main_sizer.Add(self.current_dest_txt, 0, wx.LEFT|wx.EXPAND, 25)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.cancel_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def handler(self, evt):
        if evt.from_p == "Done":
            self.Destroy()
        self.current_file_txt.SetLabel("from; " + evt.from_p)
        self.current_dest_txt.SetLabel("  to; " + evt.to_p)

    def OnClose(self, e):
        self.abortEvent.set()
        self.Destroy()

    def _resultConsumer(self, delayedResult):
        pass

    def _resultProducer(self, jobID, abortEvent):
        """Run the file download with delayedresult module"""
        files_list = self.parent.files_to_download
        for file in files_list:
            if abortEvent():
                return None
            else:
                # Call event which updates dialog box text
                evt = FileDownloadEvent(from_p=file[0], to_p=file[1])
                wx.PostEvent(self, evt)
                # download the file
                try:
                    self.parent.sftp.get(file[0], file[1])
                except:
                    if os.path.isfile(file[1]):
                        os.remove(file[1])
                    print(" - couldn't download " + file[0] + " probably a folder or something.")
        wx.PostEvent(self,FileDownloadEvent(from_p="Done", to_p="Done"))
        print("Download completed")
        return jobID
