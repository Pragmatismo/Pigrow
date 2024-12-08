import wx
import os
import sys
import time
from getmac import get_mac_address
import wx.lib.delayedresult as delayedresult
import  wx.lib.newevent
import threading
import platform

import subprocess
from datetime import datetime

FileDownloadEvent, EVT_FILE_DOWNLOAD = wx.lib.newevent.NewEvent()

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
        self.cb_ip = wx.ComboBox(self, choices = list_of_ips, style=wx.TE_PROCESS_ENTER)
        self.cb_ip.Bind(wx.EVT_TEXT_ENTER, self.combo_return)
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
        self.tb_pass = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER| wx.TE_PASSWORD)
        self.tb_pass.Bind(wx.EVT_TEXT_ENTER, self.combo_return)
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
        size[0] = int(size[0]  * 1.2)
        self.cb_ip.SetMinSize(size)
        self.cb_ip.SetValue(shared_data.gui_set_dict['default_address'])

    def combo_return(self, e):
        self.link_with_pi_btn_click(None)

    def discover_ip_list(self):
        default_ip = self.parent.shared_data.gui_set_dict['default_address']
        ip_ranges = ["192.168.0.", "192.168.1."]

        def ping_sweep(ip_range):
            """Ping all IPs in the range to populate the ARP table."""
            for x in range(0, 255):
                print(f"pinging {x}")
                ip = f"{ip_range}{x}"
                param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
                os.system(f"ping {param} -w 1 {ip} > /dev/null 2>&1")

        # Initialize lists for Raspberry Pi and other IPs
        raspi_ips = []
        other_ips = []

        # Perform ping sweep and MAC address lookup
        for ip_range in ip_ranges:
            print(f"Sweeping range {ip_range}")
            ping_sweep(ip_range)  # Populate the ARP table
            for x in range(0, 255):
                ip = f"{ip_range}{x}"
                ip_mac = get_mac_address(ip=ip)
                if ip_mac is not None:
                    if "00:00:00" not in ip_mac:
                        if "b8:27:eb" in ip_mac:  # Raspberry Pi MAC prefix
                            raspi_ips.append(ip)
                            print(f"Found {ip}")
                        else:
                            other_ips.append(ip)

        # IPv6 discovery (basic example)
        ip6_mac = get_mac_address(ip6="::1")

        # Combine results into the final IP list
        final_ip_list = raspi_ips
        if other_ips:
            final_ip_list += ["-----"] + other_ips
        if ip6_mac is not None:
            final_ip_list += ["-----"] + [ip6_mac]
        if not final_ip_list:  # No devices found
            return ip6_mac
        return final_ip_list

    def seek_for_pigrows_click(self, event):
        dlg = DiscoverIPDialog(self, title="Discovery Options")
        if dlg.ShowModal() == wx.ID_OK:
            ip_list = dlg.get_ip_list()
            self.cb_ip.Clear()
            for item in ip_list:
                self.cb_ip.Append(item)
        dlg.Destroy()

    def get_box_name(self):
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
            #self.blank_settings()
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
                self.update_ip_store(self.target_ip)
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
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            self.ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("No Pigrow config file")
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

    def update_ip_store(self, ip):
        if self.parent.shared_data.gui_set_dict['save_ip'] == "False":
            return None

        self.parent.shared_data.gui_set_dict['default_address'] = ip
        self.parent.shared_data.save_gui_settings()

    # Commands for use by other sections of the gui

    def run_on_pi(self, command, write_status=True, in_background=False):
        '''Runs a command on the pigrow and returns the output and error'''
        try:
            command = f"/bin/bash -l -c '{command}'"
            if in_background:
                command = 'nohup ' + command + ' > /dev/null 2>&1 &'

            stdin, stdout, stderr = self.ssh.exec_command(command)
            out = stdout.read().decode()
            error = stderr.read().decode()
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
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
        if not local_base_path in local_name:
            if local_name[0] == "/":
                local_name = local_name[1:]
            local_path = os.path.join(local_base_path, local_name)
        else:
            local_path = local_name
        #print (" -- local path -- " + local_path)
        without_filename = os.path.split(local_path)[0]
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
        #print ("files to download", self.files_to_download)
        if not len(self.files_to_download) == 0:
            print("Downlaoding ", len(self.files_to_download), " files")
            file_dbox = files_download_dialog(self, self.parent)
            file_dbox.ShowModal()
            #file_dbox.Destroy()

        #disconnect the sftp pipe
        self.sftp.close()
        ssh_tran.close()

    def select_files_on_pi(self, single_folder=False, create_file=False, default_path=""):
        print("Selecting files on pi")
        select_file_dbox = select_files_on_pi_dialog(self,
                                                    single_folder=single_folder,
                                                    create_file=create_file,
                                                    default_path=default_path
                                                    )
        select_file_dbox.ShowModal()
        selected_files = select_file_dbox.selected_files
        selected_folders = select_file_dbox.selected_folders
        return selected_files, selected_folders


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
        print(("    file copied to " + str(remote_path)))


     # Run on pi with input and output pipes

    class RemoteScriptPipes(wx.EvtHandler):
        def __init__(self, parent, script_path, the_link_pnl):
            super().__init__()
            self.id = wx.NewId()
            self.script_path = script_path
            self.active_ssh = the_link_pnl.ssh
            self.parent = parent
            self.channel = None
            self.connected = False
            self.connect()

        def connect(self):
            self.channel = self.active_ssh.get_transport().open_session()
            self.channel.exec_command(self.script_path)
            print("- Connected transport pipes for", self.script_path)
            self.connected = True
            threading.Thread(target=self._receive_output, daemon=True).start()

        def _receive_output(self):
            print("- Started listening for pipe output")
            while self.connected:
                if self.channel.recv_ready():
                    output = self.channel.recv(1024).decode('utf-8').strip()
                    if not output == "":
                        #print("- Received from pipe:", output)
                        self.parent.post_output_event(output)
                time.sleep(0.1)

        def send(self, command):
            print("- Sending through pipe:", command)
            if not command[-1:] == "\n":
                command += "\n"
            if self.connected and self.channel.active:
                self.channel.send(command)
            else:
                print("- Can't send; pipe is not connected.")
                self.parent.post_output_event("Error - not connected")

        def close_pipe(self):
            print("- Closing transport pipe for", self.script_path)
            self.channel.close()
            kill_command = f"pkill -f {self.script_path}"
            stdin, stdout, stderr = self.active_ssh.exec_command(kill_command)
            self.connected = False

        def GetId(self):
            return self.id



class select_files_on_pi_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, single_folder=False, create_file=False, default_path=""):
        self.parent = parent
        self.single_folder = single_folder
        self.create_file   = create_file
        self.default_path  = default_path

        self.selected_folders = []
        self.selected_files = []
        super(select_files_on_pi_dialog, self).__init__(parent)
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
        if not s_path[-1:] == "/":
            s_path = s_path + "/"

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

        self.fill_filelist()

    def selected_item(self, e):
        selected_num = self.file_list.GetFocusedItem()

        colour = self.file_list.GetItemTextColour(selected_num)
        name = self.file_list.GetItem(selected_num, 0).GetText()
        if not colour == (90, 100, 190, 255):
            self.filename_tc.SetValue(str(name))

    def fill_filelist(self):
        current_folder = self.folder_path.GetLabel().strip()
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
        if current_folder[-1:] == "/":
            current_folder = current_folder[:-1]
        top_f = current_folder.split("/")[-1] #+ "/"
        p = current_folder.replace(top_f, "")
        self.folder_path.SetLabel(p)
        self.fill_filelist()

    def OnClose(self, e):
        self.Destroy()

    def DoubleClick_filelist(self, e):
        current_folder = self.folder_path.GetLabel()
        index =  e.GetIndex()
        name = self.file_list.GetItem(index, 0).GetText()
        colour = self.file_list.GetItemTextColour(index)
        if colour == (90, 100, 190, 255):
            new_path = current_folder + name + "/"
            self.folder_path.SetLabel(new_path)
            self.Layout()
            self.fill_filelist()
        else:
            if self.single_folder == True:
                self.selected_folders.append(current_folder)
                self.Destroy()
            else:
                print("double click only enabled in single_folder mode")
                file_selected = current_folder + name
                #print("doubeclick selected - ", file_selected)

    def select_item_click(self, e):
        local_base = self.parent.shared_data.frompi_path
        current_folder = self.folder_path.GetLabel()
        if self.create_file == True:
            filename = self.filename_tc.GetValue()
            if filename == "":
                return None
            item = current_folder + filename
            self.selected_files.append(item)

        else:
            first_selected = self.file_list.GetNextSelected(-1)
            s_count = self.file_list.GetSelectedItemCount()
            s_folder_list = []
            if s_count == 1:
                pass
                #print("one thing")
            elif s_count == 0:
                #print("no file selected, using folder")
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

            for item in s_folder_list:
                self.selected_folders.append(item)
            for item in s_file_list:
                self.selected_files.append(item)

        self.Destroy()


class files_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.counter = 0
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
        self.dl_txt = " of " + str(len(self.parent.files_to_download))
        self.download_counter = wx.StaticText(self, label="0" + self.dl_txt)
        self.current_file_txt = wx.StaticText(self, label='from: ')
        self.current_dest_txt = wx.StaticText(self, label='  to: ')
        self.cancel_btn = wx.Button(self, label='Cancel')
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.download_counter, 0, wx.LEFT|wx.ALIGN_CENTER_HORIZONTAL, 5)
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
        self.counter += 1
        self.download_counter.SetLabel(str(self.counter) + self.dl_txt)

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

class DiscoverIPDialog(wx.Dialog):
    def __init__(self, parent, title="Discover IP Options"):
        super(DiscoverIPDialog, self).__init__(parent, title=title, size=(550, 600))

        self.parent = parent
        self.ip_list = []  # Will store discovered IPs after scanning
        self.stop_requested = threading.Event()  # Used to signal thread to stop
        self.scanning_thread = None

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        info_text = (
            "Discover IP addresses on your local network:\n"
            "- 'Use get_mac': Will attempt to using get_mac to check for MAC address, if devices aren't showing we can populate the ARP tables by pinging devices, note this is slow.\n"
            "- 'Use nmap': Will use nmap to discover hosts, then get MACs. nmap must be installed.\n\n"
            "Raspberry Pi devices are identified by certain MAC prefixes, Raspi's will apear at the top of the list\n\n"
            "You can also enable IPv6 scanning for a basic check.\n"
        )
        lbl_info = wx.StaticText(panel, label=info_text)
        vbox.Add(lbl_info, 0, wx.ALL|wx.EXPAND, 10)

        # Method selection
        method_choices = ["Use nmap", "Use get_mac"]
        self.rdo_method = wx.RadioBox(panel, label="Discovery Method",
                                      choices=method_choices, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.rdo_method.SetSelection(1)  # Default to get_mac
        vbox.Add(self.rdo_method, 0, wx.ALL|wx.EXPAND, 10)
        self.rdo_method.Bind(wx.EVT_RADIOBOX, self.on_method_changed)

        # Ping checkbox
        self.chk_ping = wx.CheckBox(panel, label="Enable Ping Sweep before 'get_mac' discovery")
        self.chk_ping.SetValue(True)  # Default checked
        vbox.Add(self.chk_ping, 0, wx.ALL|wx.EXPAND, 10)

        # IPv6 checkbox
        self.chk_ipv6 = wx.CheckBox(panel, label="Enable IPv6 Scanning")
        self.chk_ipv6.SetValue(False)
        vbox.Add(self.chk_ipv6, 0, wx.ALL|wx.EXPAND, 10)

        # IP Range selection (editable ComboBox)
        vbox.Add(wx.StaticText(panel, label="IP Range Prefix (e.g. '192.168.0.'):"), 0, wx.ALL|wx.EXPAND, 5)
        self.cb_ip_range = wx.ComboBox(panel, style=wx.CB_DROPDOWN)
        self.cb_ip_range.Append("192.168.0.")
        self.cb_ip_range.Append("192.168.1.")
        self.cb_ip_range.SetSelection(0)  # default selection
        vbox.Add(self.cb_ip_range, 0, wx.ALL|wx.EXPAND, 10)

        # Status label
        self.lbl_status = wx.StaticText(panel, label="Status: Idle")
        vbox.Add(self.lbl_status, 0, wx.ALL|wx.EXPAND, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_ok = wx.Button(panel, wx.ID_OK, label="OK (Start Scan)")
        self.btn_cancel = wx.Button(panel, wx.ID_CANCEL, label="Cancel")
        btn_sizer.Add(self.btn_ok, 0, wx.ALL, 5)
        btn_sizer.Add(self.btn_cancel, 0, wx.ALL, 5)
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 10)

        panel.SetSizer(vbox)
        self.Layout()

        # Bind events
        self.btn_ok.Bind(wx.EVT_BUTTON, self.on_ok)
        self.btn_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.on_method_changed(None)  # Set initial state of ping checkbox

    def on_method_changed(self, event):
        # If method is "Use nmap", disable ping checkbox
        method = self.rdo_method.GetStringSelection()
        if method == "Use nmap":
            self.chk_ping.Disable()
        else:
            self.chk_ping.Enable()

    def get_options(self):
        method = self.rdo_method.GetStringSelection()  # "Use nmap" or "Use get_mac"
        enable_ping = self.chk_ping.GetValue() if method == "Use get_mac" else False
        ipv6_enabled = self.chk_ipv6.GetValue()
        ip_range_prefix = self.cb_ip_range.GetValue().strip()
        if not ip_range_prefix.endswith('.'):
            ip_range_prefix += '.'
        return enable_ping, method, ipv6_enabled, ip_range_prefix

    def on_ok(self, event):
        # If scanning not started yet, start it; else do nothing since the dialog will close automatically
        if not self.scanning_thread or not self.scanning_thread.is_alive():
            enable_ping, method, ipv6_enabled, ip_range_prefix = self.get_options()

            # Disable OK during scan
            self.btn_ok.Disable()
            self.stop_requested.clear()
            self.ip_list = []

            self.set_status("Starting scan...")
            self.scanning_thread = threading.Thread(target=self.scan_network,
                                                    args=(enable_ping, method, ipv6_enabled, ip_range_prefix))
            self.scanning_thread.start()
        # If already scanning, do nothing here - waiting for completion or cancel

    def on_cancel(self, event):
        # If scanning is in progress, request stop
        if self.scanning_thread and self.scanning_thread.is_alive():
            self.set_status("Stop requested, please wait...")
            self.stop_requested.set()
        else:
            # No scanning in progress, just close
            self.EndModal(wx.ID_CANCEL)

    def set_status(self, msg):
        # Update status label safely from main thread
        wx.CallAfter(self.lbl_status.SetLabel, f"Status: {msg}")

    def scan_network(self, enable_ping, method, ipv6_enabled, ip_range_prefix):
        # Actual scanning logic in another thread
        # We'll have a single ip_range from the combo box now
        ip_ranges = [ip_range_prefix]  # Just one selected range

        def check_stop():
            return self.stop_requested.is_set()

        def ping_sweep(ip_range):
            for x in range(0, 255):
                if check_stop():
                    return
                ip = f"{ip_range}{x}"
                param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
                self.set_status(f"Pinging {ip}")
                os.system(f"ping {param} -w 1 {ip} > /dev/null 2>&1")

        def nmap_scan(ip_range):
            if check_stop():
                return []
            self.set_status(f"Running nmap on {ip_range}0/24")
            cmd = f"nmap -sn {ip_range}0/24"
            try:
                result = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            except subprocess.CalledProcessError:
                result = ""
            found_ips = []
            for line in result.splitlines():
                if check_stop():
                    return found_ips
                if "Nmap scan report for" in line:
                    parts = line.split()
                    ip = parts[-1] if parts else ""
                    if ip:
                        found_ips.append(ip)
            return list(dict.fromkeys(found_ips))

        def classify_ips_by_mac(ip_list_to_check):
            raspi_ips = []
            other_ips = []
            total = len(ip_list_to_check)
            for idx, ip in enumerate(ip_list_to_check):
                if check_stop():
                    return raspi_ips + (["-----"] + other_ips if other_ips else [])
                self.set_status(f"Checking MAC for {ip} ({idx+1}/{total})")
                ip_mac = get_mac_address(ip=ip)
                if ip_mac is not None and "00:00:00" not in ip_mac:
                    if "b8:27:eb" in ip_mac or "dc:a6:32" in ip_mac:
                        raspi_ips.append(ip)
                    else:
                        other_ips.append(ip)
            final_list = raspi_ips
            if other_ips:
                final_list += ["-----"] + other_ips
            if not final_list:
                final_list = ["No devices found."]
            return final_list

        def get_mac_approach(ip_ranges, do_ping):
            raspi_ips = []
            other_ips = []
            for ip_range in ip_ranges:
                if do_ping:
                    self.set_status(f"Ping sweeping {ip_range}0/24...")
                    ping_sweep(ip_range)
                    if check_stop():
                        return raspi_ips + other_ips
                count = 0
                total_ips = 255 * len(ip_ranges)
                for x in range(0, 255):
                    if check_stop():
                        return raspi_ips + other_ips
                    count += 1
                    ip = f"{ip_range}{x}"
                    self.set_status(f"Checking MAC {count}/{total_ips} - {ip}")
                    ip_mac = get_mac_address(ip=ip)
                    if ip_mac is not None and "00:00:00" not in ip_mac:
                        if "b8:27:eb" in ip_mac or "dc:a6:32" in ip_mac:
                            raspi_ips.append(ip)
                        else:
                            other_ips.append(ip)
            final_list = raspi_ips
            if other_ips:
                final_list += ["-----"] + other_ips
            if not final_list:
                final_list = ["No devices found."]
            return final_list

        final_ip_list = []
        if method == "Use nmap":
            # No ping sweep
            for ip_range in ip_ranges:
                if check_stop():
                    break
                found_ips = nmap_scan(ip_range)
                if check_stop():
                    break
                # classify by mac after scanning
                if found_ips and "No devices found." not in found_ips:
                    final_ip_list += found_ips
            # remove duplicates
            final_ip_list = list(dict.fromkeys(final_ip_list))
            if final_ip_list and not check_stop():
                final_ip_list = classify_ips_by_mac(final_ip_list)
            else:
                if not final_ip_list and not check_stop():
                    final_ip_list = ["No devices found."]
        else:
            # Use get_mac approach
            final_ip_list = get_mac_approach(ip_ranges, enable_ping)
            if check_stop() and not final_ip_list:
                final_ip_list = ["No devices found."]

        # IPv6 check if enabled
        if ipv6_enabled and not check_stop():
            self.set_status("Checking IPv6...")
            ip6_mac = get_mac_address(ip6="::1")
            if ip6_mac:
                # Insert after a separator
                final_ip_list += ["-----"] + [f"IPv6:: {ip6_mac}"]
            # If we want to do more complex IPv6 scanning, implement here.

        if check_stop():
            self.set_status("Scanning canceled.")
            # partial results returned
        else:
            self.set_status("Scanning complete.")

        self.ip_list = final_ip_list if final_ip_list else ["No devices found."]
        # Re-enable OK button so user can close dialog
        wx.CallAfter(self.btn_ok.Enable)

        if self.stop_requested.is_set():
            self.set_status("Scanning canceled.")
            wx.CallAfter(self.EndModal, wx.ID_CANCEL)
        else:
            self.set_status("Scanning complete.")
            # Now that scanning is done, close the dialog and return the list
            wx.CallAfter(self.EndModal, wx.ID_OK)

    def get_ip_list(self):
        return self.ip_list