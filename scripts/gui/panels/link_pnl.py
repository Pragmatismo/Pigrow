import wx
import os
import sys
import time
import wx.lib.delayedresult as delayedresult
import  wx.lib.newevent
import threading
import uuid

from pigrow_profiles import (find_address_conflicts, normalized_address,
                             record_connection)
from panels.pigrow_discovery import DiscoverIPDialog
from panels.pigrow_profiles_dialog import PigrowProfilesDialog


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
    def __init__(self, parent, shared_data):
        self.selected_files = []
        self.selected_folders = []
        self.parent = parent
        self.shared_data = shared_data
        self.connected = False
        self.selected_profile_id = None
        self._last_profile_sync = None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour((150, 230, 170))

        self.link_status_text = wx.StaticText(self, label='disconnected')
        self.pigrow_choice = wx.Choice(self)
        self.pigrow_choice.Bind(wx.EVT_CHOICE, self.select_pigrow)
        self.link_with_pi_btn = wx.Button(self, label='Connect')
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.edit_pigrows_btn = wx.Button(self, label='Edit list')
        self.edit_pigrows_btn.Bind(wx.EVT_BUTTON, self.edit_pigrows_click)
        self.quick_controls_btn = wx.Button(self, label='\u25bc', size=(40, -1))
        self.quick_controls_btn.SetToolTip('Show address, username and password')
        self.quick_controls_btn.Bind(wx.EVT_BUTTON, self.toggle_quick_controls)

        self.quick_controls = wx.Panel(self)
        self.l_ip = wx.StaticText(self.quick_controls, label='Address')
        self.cb_ip = wx.ComboBox(self.quick_controls, style=wx.TE_PROCESS_ENTER)
        self.cb_ip.Bind(wx.EVT_TEXT_ENTER, self.combo_return)
        self.l_user = wx.StaticText(self.quick_controls, label='Username')
        self.tb_user = wx.TextCtrl(self.quick_controls, style=wx.TE_PROCESS_ENTER)
        self.tb_user.Bind(wx.EVT_TEXT_ENTER, self.combo_return)
        self.l_pass = wx.StaticText(self.quick_controls, label='Password')
        self.tb_pass = wx.TextCtrl(self.quick_controls,
                                  style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
        self.tb_pass.Bind(wx.EVT_TEXT_ENTER, self.combo_return)
        for control in (self.link_status_text, self.pigrow_choice,
                        self.link_with_pi_btn, self.edit_pigrows_btn,
                        self.quick_controls_btn, self.l_ip, self.cb_ip,
                        self.l_user, self.tb_user, self.l_pass, self.tb_pass):
            control.SetFont(shared_data.button_font)
        self.cb_ip.SetMinSize((180, -1))
        login_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        login_sizer.AddGrowableCol(1)
        for label, field in ((self.l_ip, self.cb_ip),
                             (self.l_user, self.tb_user),
                             (self.l_pass, self.tb_pass)):
            login_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            login_sizer.Add(field, 1, wx.EXPAND)
        self.quick_controls.SetSizer(login_sizer)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(self.link_with_pi_btn, 1, wx.EXPAND)
        buttons.Add(self.edit_pigrows_btn, 1, wx.EXPAND | wx.LEFT, 4)
        buttons.Add(self.quick_controls_btn, 0, wx.EXPAND | wx.LEFT, 4)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.link_status_text, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.pigrow_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        self.main_sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.quick_controls, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.main_sizer.Hide(self.quick_controls)
        stored_id = shared_data.gui_set_dict.get('selected_pigrow')
        profiles = shared_data.get_pigrow_profiles()
        self.refresh_profiles(stored_id or (profiles[0]['id'] if profiles else None))
        self.set_status('disconnected', (170, 0, 0))

    def relayout(self):
        self.InvalidateBestSize()
        self.Layout()
        self.parent.Layout()

    def set_status(self, text, colour):
        self.link_status_text.SetLabel(text)
        self.link_status_text.SetForegroundColour(colour)
        self.link_status_text.SetToolTip(text)
        self.link_status_text.Wrap(max(260, self.GetClientSize().width - 10))
        self.relayout()

    def refresh_profiles(self, selected_id=None, load_fields=True):
        self.profiles = self.shared_data.get_pigrow_profiles()
        self.pigrow_choice.Clear()
        self.profile_ids = []
        for profile in self.profiles:
            label = profile['box_name']
            if profile['tentative']:
                label += ' (' + (profile['address'] or 'unlinked') + ')'
            self.pigrow_choice.Append(label)
            self.profile_ids.append(profile['id'])
        self.pigrow_choice.Append('New connection\u2026')
        self.profile_ids.append(None)
        if selected_id not in self.profile_ids:
            selected_id = self.profile_ids[0]
        self.pigrow_choice.SetSelection(self.profile_ids.index(selected_id))
        self.selected_profile_id = selected_id
        if load_fields:
            self.load_selected_fields()
        self.relayout()

    def load_selected_fields(self):
        profile = next((p for p in self.profiles
                        if p['id'] == self.selected_profile_id), None)
        defaults = self.shared_data.gui_set_dict
        self.cb_ip.Clear()
        for address in dict.fromkeys(p['address'] for p in self.profiles if p['address']):
            self.cb_ip.Append(address)
        self.cb_ip.SetValue(profile['address'] if profile else defaults['default_address'])
        self.tb_user.ChangeValue(profile['username'] if profile else defaults['username'])
        self.tb_pass.ChangeValue(profile['password'] if profile else defaults['password'])

    def select_pigrow(self, event):
        self.selected_profile_id = self.profile_ids[self.pigrow_choice.GetSelection()]
        self.load_selected_fields()
        if not self.cb_ip.GetValue().strip() or self.selected_profile_id is None:
            self.show_quick_controls(True)

    def show_quick_controls(self, show):
        self.main_sizer.Show(self.quick_controls, show)
        self.quick_controls_btn.SetLabel('\u25b2' if show else '\u25bc')
        self.quick_controls_btn.SetToolTip(
            'Hide login details' if show else 'Show address, username and password')
        self.relayout()

    def toggle_quick_controls(self, event):
        self.show_quick_controls(not self.quick_controls.IsShown())

    def combo_return(self, event):
        if not self.connected:
            self.link_with_pi_btn_click(None)

    def edit_pigrows_click(self, event):
        settings = self.shared_data.gui_set_dict
        dlg = PigrowProfilesDialog(
            self, self.shared_data.get_pigrow_profiles(),
            default_username=settings['username'],
            default_password=settings['password'],
            ssh_port=int(settings['ssh_port']),
            selected_profile_id=self.selected_profile_id)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                selected_id = dlg.get_selected_profile_id()
                try:
                    self.shared_data.save_pigrow_profiles(dlg.get_profiles(), selected_id)
                except OSError as error:
                    wx.MessageBox('Could not save Pigrow settings: ' + str(error),
                                  'Settings error', wx.OK | wx.ICON_ERROR, self)
                    return
                self.refresh_profiles(selected_id)
                if not self.cb_ip.GetValue().strip():
                    self.show_quick_controls(True)
        finally:
            dlg.Destroy()

    def seek_for_pigrows_click(self, event):
        # Kept for callers of the old panel API; discovery now lives in Edit list.
        self.edit_pigrows_click(event)

    def get_box_name(self):
        out, error = self.run_on_pi('cat ~/Pigrow/config/pigrow_config.txt')
        boxname = None
        if not error:
            for line in out.splitlines():
                key, separator, value = line.partition('=')
                if separator and key.strip() == 'box_name':
                    boxname = value.strip() or None
                    break
        self.shared_data.box_name = boxname
        if self.connected and boxname:
            self.sync_connected_profile(boxname)
        return boxname

    def sync_connected_profile(self, box_name):
        if not self.connected:
            return
        profiles = self.shared_data.get_pigrow_profiles()
        selected = next((p for p in profiles if p['id'] == self.selected_profile_id), None)
        name = box_name or (selected['box_name'] if selected else 'unknown pi')
        fingerprint = (name, self.target_ip, self.target_user, self.target_pass,
                       self.selected_profile_id)
        if fingerprint == self._last_profile_sync:
            return
        actions = {}
        conflicts = find_address_conflicts(profiles, self.target_ip, name)
        # A hostname connection also detects an older entry stored by its IP.
        try:
            peer_ip = self.ssh.get_transport().sock.getpeername()[0]
        except (AttributeError, OSError, TypeError):
            peer_ip = self.target_ip
        for profile in find_address_conflicts(profiles, peer_ip, name):
            if profile['id'] not in {p['id'] for p in conflicts}:
                conflicts.append(profile)
        for profile in conflicts:
            dlg = AddressConflictDialog(self, profile, name, self.target_ip)
            try:
                dlg.ShowModal()
                actions[profile['id']] = dlg.action
            finally:
                dlg.Destroy()
        record_selected_id = self.selected_profile_id
        if box_name and selected is None:
            sighting = next((p for p in profiles if p['tentative']
                             and normalized_address(p['address']) == normalized_address(peer_ip)), None)
            if sighting:
                record_selected_id = sighting['id']
        updated, selected_id = record_connection(
            profiles, box_name or name, self.target_ip, self.target_user,
            self.target_pass, selected_id=record_selected_id,
            conflict_actions=actions)
        if box_name:
            # IP and hostname sightings become one device once its name is known.
            updated = [p for p in updated if p['id'] == selected_id
                       or not (p['tentative'] and normalized_address(p['address'])
                               == normalized_address(peer_ip))]
        try:
            self.shared_data.save_pigrow_profiles(updated, selected_id)
        except OSError as error:
            wx.MessageBox('Connected, but could not save Pigrow settings: ' + str(error),
                          'Settings error', wx.OK | wx.ICON_ERROR, self)
            return
        self.refresh_profiles(selected_id, load_fields=False)
        self._last_profile_sync = (name, self.target_ip, self.target_user,
                                   self.target_pass, selected_id)
        if box_name:
            self.shared_data.box_name = box_name
            self.shared_data.frompi_path = os.path.join(
                self.shared_data.frompi_base_path, box_name)

    def set_connection_controls(self, connected):
        self.link_with_pi_btn.SetLabel('Disconnect' if connected else 'Connect')
        for control in (self.pigrow_choice, self.edit_pigrows_btn,
                        self.cb_ip, self.tb_user, self.tb_pass):
            control.Enable(not connected)

    def link_with_pi_btn_click(self, event):
        if self.connected:
            self.ssh.close()
            self.connected = False
            self._last_profile_sync = None
            self.shared_data.box_name = None
            self.set_connection_controls(False)
            self.set_status('disconnected', (170, 0, 0))
            self.set_shared_info_on_connect(None)
            return
        self.target_ip = self.cb_ip.GetValue().strip()
        self.target_user = self.tb_user.GetValue().strip()
        self.target_pass = self.tb_pass.GetValue()
        if not self.target_ip or not self.target_user:
            self.show_quick_controls(True)
            self.set_status('unable to connect: enter an address and username', (0, 0, 139))
            return
        self.set_status('connecting...', (0, 0, 139))
        self.link_with_pi_btn.Disable()
        try:
            port = int(self.shared_data.gui_set_dict['ssh_port'])
            self.ssh.connect(self.target_ip, port=port, username=self.target_user,
                             password=self.target_pass, timeout=3,
                             auth_timeout=3, banner_timeout=3)
        except Exception as error:
            self.ssh.close()
            self.connected = False
            self.set_connection_controls(False)
            self.set_status('unable to connect: ' + str(error), (0, 0, 139))
            self.set_shared_info_on_connect(None)
            return
        finally:
            self.link_with_pi_btn.Enable()
        self.connected = True
        self.set_connection_controls(True)
        self.set_status('connected', (0, 110, 0))
        box_name = self.get_box_name()
        if not box_name:
            self.sync_connected_profile(None)
        self.set_shared_info_on_connect(box_name)

    def set_link_pi_text(self, log_on_test, box_name):
        # Installer and system panels use this after a confirmed name change.
        self.connected = bool(log_on_test)
        self.set_connection_controls(self.connected)
        if self.connected:
            self.set_status('connected', (0, 110, 0))
            self.sync_connected_profile(box_name)
        else:
            self.ssh.close()
            self.set_status('unable to connect', (0, 0, 139))

    def set_shared_info_on_connect(self, box_name):
        shared_data = self.parent.shared_data
        if not box_name == "" and not box_name == None:
            shared_data.frompi_path = os.path.join(shared_data.frompi_base_path, box_name)
            shared_data.remote_pigrow_path = "/home/" + self.target_user + "/Pigrow/"
            shared_data.config_txt_path = self.determine_boot_config_path()
            # The start panel runs first, before other panels refresh the config.
            shared_data.read_pigrow_settings_file()
            self.parent.tell_pnls_connected()
        else:
            shared_data.frompi_path = ""
            shared_data.remote_pigrow_path = ""

    def determine_boot_config_path(self):
        """
        On newer Raspberry Pi OS the config lives in /boot/firmware/config.txt;
        on older releases it’s still at /boot/config.txt.  We ssh out to the Pi
        and test for the presence of each file in turn, returning the first one
        we find.
        """
        # 1) check new path
        out, error = self.run_on_pi(
            "if [ -f /boot/firmware/config.txt ]; then echo exists; fi"
        )
        if out.strip() == "exists":
            return "/boot/firmware/config.txt"

        # 2) fallback to old path (even if it’s just the “DO NOT EDIT” stub,
        #    at least it’ll always exist)
        return "/boot/config.txt"

    def update_ip_store(self, ip):
        # Saved profiles replace the old single-address store.
        if self.connected:
            self.sync_connected_profile(self.shared_data.box_name)

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

    def cmd_on_pi(self, command, write_status=True):
        """Run a command on the pi with live output buffers and cancel support."""
        stdout_buffer = []
        stderr_buffer = []
        token = f"PIGROW_CMD_TOKEN_{uuid.uuid4().hex}"
        command_with_token = f"PIGROW_CMD_TOKEN={token} {command}"
        channel = None

        class CmdOnPiHandle:
            def __init__(self):
                self.is_running = True
                self.stdout = stdout_buffer
                self.stderr = stderr_buffer

            def cancel(self, kill_remote=True):
                if channel is None:
                    return
                try:
                    if kill_remote:
                        link_pnl_self.run_on_pi(f"pkill -f {token}", write_status=False)
                finally:
                    try:
                        channel.close()
                    except Exception:
                        pass
                    self.is_running = False

        link_pnl_self = self
        handle = CmdOnPiHandle()

        def read_output():
            try:
                while True:
                    if channel.recv_ready():
                        data = channel.recv(4096)
                        if data:
                            stdout_buffer.append(data.decode())
                    if channel.recv_stderr_ready():
                        data = channel.recv_stderr(4096)
                        if data:
                            stderr_buffer.append(data.decode())
                    if channel.exit_status_ready():
                        if not channel.recv_ready() and not channel.recv_stderr_ready():
                            break
                    time.sleep(0.05)
            finally:
                try:
                    channel.close()
                except Exception:
                    pass
                handle.is_running = False

        try:
            full_command = f"/bin/bash -l -c '{command_with_token}'"
            transport = self.ssh.get_transport()
            channel = transport.open_session()
            channel.exec_command(full_command)
            output_thread = threading.Thread(target=read_output, daemon=True)
            output_thread.start()
        except Exception as e:
            error = "failed running command;" + str(command) + " with error - " + str(e)
            print(error)
            stderr_buffer.append(error)
            handle.is_running = False
        return handle

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


class AddressConflictDialog(wx.Dialog):
    def __init__(self, parent, older, new_name, address):
        super().__init__(parent, title='Pigrow name changed')
        self.action = 'ignore'
        text = wx.StaticText(self, label=(
            'Connected to "' + new_name + '" at ' + address + '.\n'
            '"' + older['box_name'] + '" already uses this address.\n'
            'Remove deletes the older entry.\n'
            'Unlink keeps its name and login details, clearing its address.\n'
            'Ignore keeps both entries.'))
        text.Wrap(460)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        for label, action in (('Remove', 'remove'), ('Unlink', 'unlink'), ('Ignore', 'ignore')):
            button = wx.Button(self, label=label)
            button.Bind(wx.EVT_BUTTON, lambda event, choice=action: self.choose(choice))
            buttons.Add(button, 0, wx.ALL, 5)
            if action == 'ignore':
                button.SetDefault()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 12)
        sizer.Add(buttons, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE, lambda event: self.choose('ignore'))
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def choose(self, action):
        self.action = action
        self.EndModal(wx.ID_OK)

    def on_key(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.choose('ignore')
        else:
            event.Skip()


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
