import os
import datetime
import shutil
import wx
import wx.lib.scrolledpanel as scrolled
import wx.lib.delayedresult as delayedresult
import wx.lib.newevent

FileClearEvent, EVT_FILE_CLEAR = wx.lib.newevent.NewEvent()

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # button to read local files
        self.read_btn = wx.Button(self, label='Read local files')
        self.read_btn.Bind(wx.EVT_BUTTON, self.read_click)
        # buttons to open file transfer dialogue boxes
        self.download_btn = wx.Button(self, label='Download')
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)
        self.upload_btn = wx.Button(self, label='Upload to pi')
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)
        self.clear_downed_btn = wx.Button(self, label='clear downloaded caps')
        self.clear_downed_btn.Bind(wx.EVT_BUTTON, self.clear_downed_click)
        # buttons to backup config, restore config, archive grow + start fresh with same or loaded config
        archive_label =  wx.StaticText(self,  label=' Archive')
        self.saveconf_btn = wx.Button(self, label='Save Config')
        self.saveconf_btn.Bind(wx.EVT_BUTTON, self.saveconf_click)
        self.loadconf_btn = wx.Button(self, label='Load Config')
        self.loadconf_btn.Bind(wx.EVT_BUTTON, self.loadconf_click)
        self.endgrow_btn = wx.Button(self, label='End Current Grow')
        self.endgrow_btn.Bind(wx.EVT_BUTTON, self.endcurrentgrow_click)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.read_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.download_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.upload_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.clear_downed_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        #
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(archive_label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.saveconf_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.loadconf_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.endgrow_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(main_sizer)

    def read_click(self, e):
        if self.parent.shared_data.frompi_path == "":
            print("No frompi folder set, check link to pi is active")
            return None
        config_folder = "config"
        logs_folder   = "logs"
        caps_folder   = 'caps'
        I_pnl = self.parent.dict_I_pnl['localfiles_pnl']
        I_pnl.config_file_list.read_configs(I_pnl.config_files, config_folder)
        I_pnl.log_file_list.read_logs(I_pnl.log_files, logs_folder)
        if I_pnl.r_folder_text.GetLabel().strip() == "caps":
            remote_caps = self.parent.shared_data.remote_pigrow_path + caps_folder
            I_pnl.r_folder_text.SetLabel(remote_caps)
        if I_pnl.folder_text.GetLabel().strip() == "caps":
            local_caps  = os.path.join(self.parent.shared_data.frompi_path, caps_folder)
            I_pnl.folder_text.SetLabel(local_caps)
        I_pnl.set_r_caps_text()
        I_pnl.read_caps_info()

    def download_click(self, e):
        file_dbox = file_download_dialog(self, self.parent)
        file_dbox.ShowModal()
        file_dbox.Destroy()
        self.read_click("e")

    def upload_click(self, e):
        file_dbox = file_upload_dialog(self, self.parent)
        file_dbox.ShowModal()
        file_dbox.Destroy()

    def saveconf_click(self, e):
        # tell user this will save the current pi's config to the local folder
        # give config a name   - folder name;  config_NAME
        msg = "Choose a name for this settings configuration"
        name_dbox = wx.TextEntryDialog(self, msg, 'Select name for config', '')
        if name_dbox.ShowModal() == wx.ID_OK:
            conf_name = name_dbox.GetValue()
        else:
            return "cancelled"
        name_dbox.Destroy()
        # make backup folder with selected name
        folder_name = "config_" + conf_name
        confstore_dir = os.path.join(self.parent.shared_data.frompi_path, folder_name)
        if not os.path.exists(confstore_dir):
            print(" Creating config store folder " + confstore_dir)
            os.makedirs(confstore_dir)
        else:
            # delete everything from full folder
            print(" Config store folder already exists.")
            question_text = "config store with name " + confstore_dir + " already exists, do you want to replace it?"
            question_text += "\n This will delete everything in the folder."
            dbox = wx.MessageDialog(self, question_text, "Replace existing config store?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                dir_list = os.listdir(path=confstore_dir)
                for file in dir_list:
                    if not os.path.isdir(file):
                        local_path = os.path.join(confstore_dir, file)
                        os.remove(local_path)
            else:
                return None
        # list config files & download
        #  list files
        pi_conf_folder = self.parent.shared_data.remote_pigrow_path + "config/"
        out, error = self.parent.link_pnl.run_on_pi("ls " + pi_conf_folder)
        pi_conf_list = out.splitlines()
        #  create local paths
        folders = []
        for file in pi_conf_list:
            #filename = file.split("/")[-1]
            remote_path = pi_conf_folder + file
            local_path = os.path.join(confstore_dir, file)
            folders.append([remote_path, local_path])

        self.parent.link_pnl.download_folder([], extra_files=folders, overwrite=True) #, extra_files=extra_files_over)
        # save cron to confstore
        cron_save_path = os.path.join(confstore_dir, 'cron_store.txt')
        out, error = self.parent.link_pnl.run_on_pi("crontab -l ")
        with open(cron_save_path, "w") as cron_file:
            cron_file.write(out.rstrip('\r'))

    def loadconf_click(self, e):
        # list saved configs - folder name; config_NAME
        conf_folder = []
        defpath = self.parent.shared_data.frompi_path
        dialog = wx.DirDialog(self, "Select config folder", defaultPath=defpath, style=wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            conf_folder = dialog.GetPath()
        if len(conf_folder) == 0:
            return None
        print("Selected ", conf_folder)
        # show diff between current and selected config dialog box
        self.compare_config_folders(conf_folder)

    def compare_config_folders(self, conf_folder):
        self.conf_local = conf_folder
        self.conf_remote = self.parent.shared_data.remote_pigrow_path + "config/"
        conf_dbox = config_compare_dialog(self, self.parent)
        conf_dbox.ShowModal()
        conf_dbox.Destroy()

    def endcurrentgrow_click(self, e):
        endgrow_dbox = endgrow_dialog(self, self.parent)
        endgrow_dbox.ShowModal()
        endgrow_dbox.Destroy()

    def connect_to_pigrow(self):
        self.read_click("e")
        self.parent.dict_I_pnl['localfiles_pnl'].set_auto_localpath()


    def clear_downed_click(self, e):
        self.clearcaps_dbox = clearcaps_dialog(self, self.parent)
        self.clearcaps_dbox.ShowModal()
        if self.clearcaps_dbox:
            if not self.clearcaps_dbox.IsBeingDeleted():
                self.clearcaps_dbox.Destroy()
        self.parent.dict_I_pnl['localfiles_pnl'].set_r_caps_text()


class clearcaps_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(clearcaps_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 250))
        self.SetTitle("Clear Downloaded Caps from Pigrow")
        self.Bind(wx.EVT_CLOSE, self.cancel_click)

    def InitUI(self):
        # draw the pannel
        title = wx.StaticText(self,  label='Clearing Downloaded Images from Pigrow')

        #buttons
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)

        self.clear_txt = " of them cleared"
        self.clear_counter = wx.StaticText(self, label="0" + self.clear_txt)

        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(self.clear_counter, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)

        self.counter   = 1

        self.jobID = 100
        self.Bind(EVT_FILE_CLEAR, self.handler)
        self.abortEvent = delayedresult.AbortEvent()
        delayedresult.startWorker(self._resultConsumer, self._resultProducer,
                                  wargs=(self.jobID,self.abortEvent), jobID=self.jobID)

    def handler(self, evt):
        if evt.result == "Done":
            print("Finished clearing caps")
            self.Destroy()
        self.counter += 1
        self.clear_counter.SetLabel(str(self.counter) + self.clear_txt)


    def _resultConsumer(self, delayedResult):
        pass

    def _resultProducer(self, jobID, abortEvent):
        """Run clear caps with delayedresult module"""
        caps_files, remote_caps, remote_caps_path = self.make_list()

        # Clear Files
        for the_remote_file in remote_caps:
            if abortEvent():
                return None

            if the_remote_file in caps_files:
                the_remote_file = remote_caps_path + "/" + the_remote_file
                wx.PostEvent(self,FileClearEvent(result="cleared"))
                self.parent.parent.link_pnl.run_on_pi("rm " + the_remote_file, False)
            else:
                wx.PostEvent(self,FileClearEvent(result="left"))

        wx.PostEvent(self,FileClearEvent(result="Done"))


    def make_list(self):
        # looks at local files an remote files removing any from the pigrows
        # that are already stored in the local caps folder for that pigrow
        I_pnl = self.parent.parent.dict_I_pnl['localfiles_pnl']
        remote_caps_path = I_pnl.r_folder_text.GetLabel()
        local_caps_path  = I_pnl.folder_text.GetLabel()

        # Read local caps files
        caps_files = os.listdir(local_caps_path)
        caps_files.sort()
        print (len(caps_files), "Files locally")

        # Read pi's caps folder
        try:
            out, error = self.parent.parent.link_pnl.run_on_pi("ls " + remote_caps_path)
            remote_caps = out.splitlines()
            self.clear_txt = " of " + str(len(remote_caps))
            print(len(remote_caps), " Files remotely")
        except Exception as e:
            print ("-- Reading remote caps folder failed;", str(e))
            remote_caps = []

        return caps_files, remote_caps, remote_caps_path

    def cancel_click(self, e):
        self.abortEvent.set()
        self.Destroy()



class endgrow_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(endgrow_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 500))
        self.SetTitle("Start New Grow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # draw the pannel
        title = wx.StaticText(self,  label='Archive and Start New Grow')
        sub_msg = "To create a fresh grow this tool updates the local files and copies them "
        sub_msg += "to a subfolder in the archive folder then clears the log files on the pi."
        sub_label = wx.StaticText(self,  label=sub_msg, size=(400, 90))

        # archive
        n_label = wx.StaticText(self,  label='Archive name')
        self.name_tc = wx.TextCtrl(self, value=self.get_name(), size=(200,30))
        n_sizer = wx.BoxSizer(wx.HORIZONTAL)
        n_sizer.Add(n_label, 0,  wx.ALL, 3)
        n_sizer.Add(self.name_tc, 0,  wx.ALL, 3)

        a_label = wx.StaticText(self,  label='Download from Pi;')
        self.cb_caps = wx.CheckBox(self, label='caps')
        self.cb_logs = wx.CheckBox(self, label='Logs')
        self.cb_conf = wx.CheckBox(self, label='Config')
        self.cb_caps.SetValue(True)
        self.cb_logs.SetValue(True)
        self.cb_conf.SetValue(True)
        arc_sizer = wx.BoxSizer(wx.VERTICAL)
        arc_sizer.Add(a_label, 0,  wx.ALL, 3)
        arc_sizer.Add(self.cb_caps, 0,  wx.LEFT, 50)
        arc_sizer.Add(self.cb_logs, 0,  wx.LEFT, 50)
        arc_sizer.Add(self.cb_conf, 0,  wx.LEFT, 50)

        r_label = wx.StaticText(self,  label='Remove from Pi;')
        self.cb_rcaps = wx.CheckBox(self, label='caps')
        self.cb_rlogs = wx.CheckBox(self, label='Logs')
        self.cb_rcaps.SetValue(True)
        self.cb_rlogs.SetValue(True)
        rem_sizer = wx.BoxSizer(wx.VERTICAL)
        rem_sizer.Add(r_label, 0,  wx.ALL, 3)
        rem_sizer.Add(self.cb_rcaps, 0,  wx.LEFT, 50)
        rem_sizer.Add(self.cb_rlogs, 0,  wx.LEFT, 50)

        #buttons
        self.go_btn = wx.Button(self, label='Start New Grow', size=(175, 50))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.go_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)

        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.Add(sub_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(n_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.Add(arc_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(rem_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)

    def get_name(self):
        current_date = datetime.datetime.now()
        name = 'ending-' + str(current_date.year) + current_date.strftime('%b').lower() + str(current_date.day)
        return name


    def go_click(self, e):
        remote_path = self.parent.parent.shared_data.remote_pigrow_path
        frompi_path = self.parent.parent.shared_data.frompi_path
        arcconf = self.cb_conf.GetValue()
        remote_conf = remote_path + "config"
        arclogs = self.cb_logs.GetValue()
        remote_logs = remote_path + "logs"
        arccaps = self.cb_caps.GetValue()
        remote_caps = remote_path + "caps"
        arc_name = self.name_tc.GetValue()
        arc_path = output_path = os.path.join(frompi_path, "archive/" + arc_name + "/")

        # make archive folder
        if arcconf or arclogs or arccaps:
            if not os.path.exists(arc_path):
                try:
                    os.makedirs(arc_path)
                except OSError as e:
                    print("Error creating folder at " + arc_path)
            else:
                err_msg = "An archive of that name already exists, "
                err_msg += "please pick a new name or delete the existing archive."
                print(err_msg)
                dialog = wx.MessageDialog(None, err_msg, "Error", wx.OK | wx.ICON_ERROR)
                result = dialog.ShowModal()
                dialog.Destroy()
                return None


        # update local files
        folders_overwrite = []
        folders_newonly = []
        log_sizes = []
        out, error = self.parent.parent.link_pnl.run_on_pi("ls " + remote_logs)
        filelist = out.splitlines()
        filelist = [item for item in filelist if item != 'trigger_conditions.txt']
        if arclogs == True:
            folders_overwrite.append(remote_logs)
            # get file sizes to check download worked
            for filename in filelist:
                path = remote_logs + "/" + filename
                cmd = "ls -l --block-size=1 " + path + " | awk '{print $5}'"
                r_size, error = self.parent.parent.link_pnl.run_on_pi(cmd)
                r_size = r_size.strip()
                l_path = os.path.join(frompi_path, 'logs', filename)
                log_sizes.append([filename, path, r_size, l_path])
                print("remote file size: ", filename, r_size)
        if arcconf == True:
            folders_overwrite.append(remote_conf)
        if arccaps == True:
            folders_newonly.append(remote_caps)

        if not len(folders_newonly) == 0:
            self.parent.parent.link_pnl.download_folder(folders_newonly, overwrite=False)
        if not len(folders_overwrite) == 0:
            self.parent.parent.link_pnl.download_folder(folders_overwrite, overwrite=True)

        # verify copy worked
        errors = []
        for log in log_sizes:
            filename, path, r_size, l_path = log[0], log[1], log[2], log[3]
            l_size = str(os.path.getsize(l_path)).strip()
            if not r_size == l_size:
                print("file sizes do not match" + filename)
                errors.append([filename, path, r_size, l_path, l_size])
            else:
                print("file sizes match - " + filename)

        if not len(errors) == 0:
            err_msg = "file not downloaded;"
            for err in errors:
                err_msg += "\n     " + err[0]
            err_msg += "continue anyway? \n\n This will remove the log files on the pi"
            err_d = wx.MessageDialog(None, err_msg, "Error", wx.YES_NO | wx.ICON_ERROR)
            result = dialog.ShowModal()
            dialog.Destroy()
            if not result == wx.ID_YES:
                return None

        # clear log files from pi
        if self.cb_rcaps.GetValue() == True:
            self.parent.clear_downed_click(None)
            #print(" REMOVING CAPS IS NOT YET WRITTEN - USE THE OTHER TOOL FOR IT BEFORE THIS POINT")
        if self.cb_rlogs.GetValue() == True:
            for filename in filelist:
                path = remote_logs + "/" + filename
                out, error = self.parent.parent.link_pnl.run_on_pi("rm " + path)
                print("Removed " + path)

        # copy local files to archive
        c_result = self.copy_to_arc(frompi_path, arc_name)
        if c_result == "fail":
            err_msg = "Moving some or all local files into the archive has failed, there may be a system lock or resource error - try moving them manually into the created folder."
            print(err_msg)
            dialog = wx.MessageDialog(None, err_msg, "Error", wx.OK | wx.ICON_ERROR)
            result = dialog.ShowModal()
            dialog.Destroy()

        # tell user the results
        print(" - Archive crated; " + arc_name)
        self.Destroy()

    def copy_to_arc(self, folder_path, archive_name):
        # Ensure folder_path is a valid directory
        if not os.path.isdir(folder_path):
            print(f"Error: {folder_path} is not a valid directory.")
            return "fail"

        # Create the 'archive' folder if it doesn't exist
        archive_folder = os.path.join(folder_path, 'archive')
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)

        # Create a subfolder within 'archive' using the provided archive_name
        archive_subfolder = os.path.join(archive_folder, archive_name)
        if not os.path.exists(archive_subfolder):
            os.makedirs(archive_subfolder)

        # Copy everything from folder_path to the 'archive' folder
        for root, dirs, files in os.walk(folder_path):
            # Skip the 'archive' folder and its subfolders
            print(os.path.basename(root))
            if os.path.basename(root) == 'archive':
                dirs.clear()
                continue

            # Calculate the relative path within the 'archive' folder
            relative_path = os.path.relpath(root, folder_path)
            destination_path = os.path.join(archive_subfolder, relative_path)

            # Create the destination folder if it doesn't exist
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            # Copy files to the destination folder
            for file in files:
                source_file_path = os.path.join(root, file)
                destination_file_path = os.path.join(destination_path, file)
                shutil.move(source_file_path, destination_file_path)
        print(f"Contents of {folder_path} moved to {archive_subfolder}")


    def OnClose(self, e):
        self.Destroy()

class config_compare_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(config_compare_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 600))
        self.SetTitle("Replace current config?")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # draw the pannel
        label = wx.StaticText(self,  label='Config files to be replaced;')

        #buttons
        self.upload_btn = wx.Button(self, label='Upload', size=(175, 50))
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upload_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.scroll_box = self.scroll_area(self)
        self.main_sizer.Add(self.scroll_box, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)

    def upload_click(self, e):
        ignore_files = self.scroll_box.ignore_files
        files_add = self.scroll_box.files_add
        files_replace = self.scroll_box.files_replace
        files_remove = self.scroll_box.files_remove
        conf_remote = self.parent.conf_remote
        conf_local = self.parent.conf_local
        #print('ignoring;', ignore_files)
        # add and replace
        add_list = files_add + files_replace
        upload_list = []
        for filename in add_list:
            if not filename in ignore_files:
                local_file_path = os.path.join(conf_local, filename)
                remote_file_path = conf_remote + filename
                upload_list.append([local_file_path, remote_file_path])
        #print('copying;', upload_list)
        if not len(upload_list) == 0:
            self.parent.parent.link_pnl.upload_files(upload_list)
        # remove from pi
        #print("removing;")
        for filename in files_remove:
            if not filename in ignore_files:
                cmd = 'rm ' + conf_remote + filename
                print (cmd)
                out, error = self.parent.parent.link_pnl.run_on_pi(cmd)

        # cron replacement
        if 'Cron will be updated' in ignore_files:
            print("ignoring cron when updating config")
        else:
            if self.scroll_box.cron_match == False:
                self.upload_cron()
            #else:
            #    print(" Cron's are the same, no need to update.")

        # close dialog
        self.Destroy()

    def upload_cron(self):
        conf_local = self.parent.conf_local
        local_cronstore_path = os.path.join(conf_local, 'cron_store.txt')

        with open(local_cronstore_path, "r") as config_file:
            l_c_file = config_file.read()
        cron_text = l_c_file.rstrip('\r')

        temp_cronstore_path = self.parent.parent.shared_data.remote_pigrow_path + "temp/cron_store.txt"
        self.parent.parent.link_pnl.write_textfile_to_pi(cron_text, temp_cronstore_path)

        #self.parent.parent.link_pnl.upload_files([[local_cronstore_path, temp_cronstore_path]])
        # check they match
        out, error = self.parent.parent.link_pnl.run_on_pi("cat " + temp_cronstore_path)

        if out.rstrip('\r') == l_c_file:
            #print(" The uploaded cron file is the same as the one we uploaded, no corruption here")
            out, error = self.parent.parent.link_pnl.run_on_pi("crontab " + temp_cronstore_path)
            out, error = self.parent.parent.link_pnl.run_on_pi("crontab -l")
            if out == l_c_file:
                print(" Cron updated correctly.")
            else:
                print(" !!!! WARNING !!!!!!")
                print("   Cron update has failed, your cron might be messed up!!!!")
                print(" !!!! WARNING !!!!!! (it might just be an OS thing though, best check)")

        else:
            print(" !!! Something went wrong with the cron_store transfer, copied file arrived different - terminating action!")
            return None


    def OnClose(self, e):
        self.Destroy()

    class scroll_area(scrolled.ScrolledPanel):
        def __init__(self, parent):
            self.parent = parent
            self.conf_local = parent.parent.conf_local
            self.conf_remote = parent.parent.conf_remote
            scrolled.ScrolledPanel.__init__(self, parent, -1, size=(600,400))
            vbox = wx.BoxSizer(wx.VERTICAL)
            vbox.Add(self.make_conf_sizer(), 0, wx.ALIGN_LEFT | wx.ALL, 5)
            self.SetSizer(vbox)
            self.SetupScrolling()

        def make_conf_sizer(self):
            print(" making a sizer for conf file comparison")
            # list files
            confstore_files, cron_exists = self.list_confstore()
            remote_conf = self.list_remote_conf()

            # create settings sizers for config files (added, removed and modified)
            # create compare lists
            self.files_remove = []
            self.files_add = []
            self.files_replace = []
            self.ignore_files = []
            for file in confstore_files:
                if file not in remote_conf:
                    self.files_add.append(file)
                else:
                    if not self.read_diff(file, to_return="answer"):
                        self.files_replace.append(file)
            for r_file in remote_conf:
                if r_file not in confstore_files:
                    self.files_remove.append(r_file)
            # create add file sizer
            self.add_sizer = wx.BoxSizer(wx.VERTICAL)
            for file in self.files_add:
                item_sizer = self.make_conf_element(file, "Add")
                self.add_sizer.Add(item_sizer, 0, wx.ALL|wx.EXPAND, 5)

            # create remove file sizer
            self.rm_sizer = wx.BoxSizer(wx.VERTICAL)
            for file in self.files_remove:
                item_sizer = self.make_conf_element(file, "Remove")
                self.rm_sizer.Add(item_sizer, 0, wx.ALL|wx.EXPAND, 5)

            # create modify file sizer
            self.mod_sizer = wx.BoxSizer(wx.VERTICAL)
            for file in self.files_replace:
                item_sizer = self.make_conf_element(file, "Modify")
                self.mod_sizer.Add(item_sizer, 0, wx.ALL|wx.EXPAND, 5)

            #create combined sizer
            # labels
            add_l = wx.StaticText(self, label=str(len(self.files_add)) + ' files to be added;')
            add_view = wx.Button(self, label='Hide', size=(40, 20))
            add_view.Bind(wx.EVT_BUTTON, self.add_view_click)
            add_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
            add_l_sizer.Add(add_l, 0, wx.ALL|wx.EXPAND, 5)
            add_l_sizer.Add(add_view, 0, wx.ALL|wx.EXPAND, 5)
            if len(self.files_add) == 0:
                add_view.Hide()

            rm_l = wx.StaticText(self, label=str(len(self.files_remove)) + ' files to be removed;')
            rm_view = wx.Button(self, label='Hide', size=(40, 20))
            rm_view.Bind(wx.EVT_BUTTON, self.rm_view_click)
            rm_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
            rm_l_sizer.Add(rm_l, 0, wx.ALL|wx.EXPAND, 5)
            rm_l_sizer.Add(rm_view, 0, wx.ALL|wx.EXPAND, 5)
            if len(self.files_remove) == 0:
                rm_view.Hide()

            mod_l = wx.StaticText(self, label=str(len(self.files_replace)) + ' files to be replaced;')
            mod_view = wx.Button(self, label='Hide', size=(40, 20))
            mod_view.Bind(wx.EVT_BUTTON, self.mod_view_click)
            mod_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
            mod_l_sizer.Add(mod_l, 0, wx.ALL|wx.EXPAND, 5)
            mod_l_sizer.Add(mod_view, 0, wx.ALL|wx.EXPAND, 5)
            if len(self.files_replace) == 0:
                rm_view.Hide()

            # cron compare
            cron_l_sizer, self.cron_sizer = self.make_cron_sizers(cron_exists)

            # final sizer
            self.conf_sizer = wx.BoxSizer(wx.VERTICAL)
            self.conf_sizer.Add(cron_l_sizer, 0, wx.LEFT|wx.ALIGN_LEFT, 25)
            self.conf_sizer.Add(self.cron_sizer, 0, wx.ALL|wx.EXPAND, 5)
            self.conf_sizer.Add(add_l_sizer, 0, wx.LEFT|wx.ALIGN_LEFT, 25)
            self.conf_sizer.Add(self.add_sizer, 0, wx.ALL|wx.EXPAND, 5)
            self.conf_sizer.Add(rm_l_sizer, 0, wx.LEFT|wx.ALIGN_LEFT, 25)
            self.conf_sizer.Add(self.rm_sizer, 0, wx.ALL|wx.EXPAND, 5)
            self.conf_sizer.Add(mod_l_sizer, 0, wx.LEFT|wx.ALIGN_LEFT, 25)
            self.conf_sizer.Add(self.mod_sizer, 0, wx.ALL|wx.EXPAND, 5)

            return self.conf_sizer

        def make_cron_sizers(self, cron_exists):
            # cron label
            cron_l = wx.StaticText(self, label='Cron task schedular')
        #    cron_view = wx.Button(self, label='Hide', size=(40, 20))
        #    cron_view.Bind(wx.EVT_BUTTON, self.add_view_click)
            cron_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
            cron_l_sizer.Add(cron_l, 0, wx.ALL|wx.EXPAND, 5)
        #    cron_l_sizer.Add(cron_view, 0, wx.ALL|wx.EXPAND, 5)
            # cron text
            self.cron_match = True
            if cron_exists:
                if self.compare_cron():
                    c_txt = "Both cron files are the same"
                else:
                    c_txt = "Cron will be updated"
                    self.cron_match = False
            else:
                c_txt = "No saved cron, keeping original"

            ###
            if cron_exists:
                # create button instead of label
                status_c = wx.Button(self, label='view', size=(40, 20))
                status_c.Bind(wx.EVT_BUTTON, self.view_cron_click)
            else:
                status_c = wx.StaticText(self,  label="")
            ###
            use_cb = wx.CheckBox(self, label='')
            use_cb.SetValue(True)
            use_cb.Bind(wx.EVT_CHECKBOX, self.checkbox_click)
            name_l = wx.StaticText(self,  label=c_txt)

            cron_sizer = wx.BoxSizer(wx.HORIZONTAL)
            cron_sizer.Add(use_cb, 0, wx.ALL|wx.EXPAND, 5)
            cron_sizer.Add(name_l, 0, wx.ALL|wx.EXPAND, 5)
            cron_sizer.Add(status_c, 0, wx.ALL|wx.EXPAND, 5)
            if self.cron_match == True:
                use_cb.Hide()

            return cron_l_sizer, cron_sizer

        def view_cron_click(self, e):
            # load local file
            local_file_path = os.path.join(self.conf_local, "cron_store.txt")
            with open(local_file_path, "r") as config_file:
                l_c_file = config_file.read()
            # show text
            shared_data = self.parent.parent.parent.shared_data
            dbox = shared_data.scroll_text_dialog(None, l_c_file, "Local Cron", cancel=False)
            dbox.ShowModal()
            dbox.Destroy()

        def compare_cron(self):
            # load remote file
            r_cron, error = self.parent.parent.parent.link_pnl.run_on_pi("crontab -l ")
            # load local file
            local_file_path = os.path.join(self.conf_local, "cron_store.txt")
            with open(local_file_path, "r") as l_cron_file:
                l_cron = l_cron_file.read()
            # compare
            if l_cron == r_cron:
                print("The crons are the same")
                return True
            else:
                print("The crons are different")
                return False

        def list_confstore(self):
            print("Listing local confstore")
            dir_list = os.listdir(path=self.conf_local)
            cron_exists = False
            if 'cron_store.txt' in dir_list:
                dir_list.remove('cron_store.txt')
                cron_exists = True
            return dir_list, cron_exists

        def list_remote_conf(self):
            print("listing remote conf")
            out, error = self.parent.parent.parent.link_pnl.run_on_pi("ls -p " + self.conf_remote + " | grep -v / ")
            pi_conf_list = out.splitlines()
            return pi_conf_list

        def add_view_click(self, e):
            button = e.GetEventObject()
            if button.GetLabel() == "Hide":
                button.SetLabel("Show")
                self.conf_sizer.Hide(self.add_sizer)
            else:
                button.SetLabel("Hide")
                self.conf_sizer.Show(self.add_sizer)
            self.parent.Layout()

        def rm_view_click(self, e):
            button = e.GetEventObject()
            if button.GetLabel() == "Hide":
                button.SetLabel("Show")
                self.conf_sizer.Hide(self.rm_sizer)
            else:
                button.SetLabel("Hide")
                self.conf_sizer.Show(self.rm_sizer)
            self.parent.Layout()

        def mod_view_click(self, e):
            button = e.GetEventObject()
            if button.GetLabel() == "Hide":
                button.SetLabel("Show")
                self.conf_sizer.Hide(self.mod_sizer)
            else:
                button.SetLabel("Hide")
                self.conf_sizer.Show(self.mod_sizer)
            self.parent.Layout()

        def make_conf_element(self, name, status="--"):
            if status == 'Modify':
                # create button instead of label
                status_c = wx.Button(self, label='diff', size=(40, 20))
                status_c.Bind(wx.EVT_BUTTON, self.dif_view_click)
            else:
                status_c = wx.StaticText(self,  label=status)

            use_cb = wx.CheckBox(self, label='')
            use_cb.SetValue(True)
            use_cb.Bind(wx.EVT_CHECKBOX, self.checkbox_click)
            name_l = wx.StaticText(self,  label=name)

            item_sizer = wx.BoxSizer(wx.HORIZONTAL)
            item_sizer.Add(use_cb, 0, wx.ALL|wx.EXPAND, 5)
            item_sizer.Add(name_l, 0, wx.ALL|wx.EXPAND, 5)
            item_sizer.Add(status_c, 0, wx.ALL|wx.EXPAND, 5)

            return item_sizer

        def checkbox_click(self, e):
            # get name of the file from sizer
            cb = e.GetEventObject()
            cb_sizer = cb.ContainingSizer
            kids = cb_sizer.GetChildren()
            text_box = kids[1].GetWindow()
            filename = text_box.GetLabel()
            # add or remove from ignore list
            if cb.GetValue() == False:
                self.ignore_files.append(filename)
            else:
                if filename in self.ignore_files:
                    self.ignore_files.remove(filename)

        def dif_view_click(self, e):
            # get name of the file from sizer
            button = e.GetEventObject()
            button_sizer = button.ContainingSizer
            kids = button_sizer.GetChildren()
            text_box = kids[1].GetWindow()
            filename = text_box.GetLabel()
            # load remote and local copies of the file
            r_file, l_file = self.read_diff(filename, to_return="text")
            # break both down into simple k:d dicts & cycle through
            self.conf_l_txt = l_file
            self.conf_r_txt = r_file
            self.conf_filename = filename
            conf_dbox = compare_conf_file_dialog(self, self.parent)
            conf_dbox.ShowModal()
            conf_dbox.Destroy()

        def read_diff(self, filename, to_return="answer"):
            # load remote file
            remote_file_path = self.conf_remote + filename
            r_file, error = self.parent.parent.parent.link_pnl.run_on_pi("cat " + remote_file_path)

            # load local file
            local_file_path = os.path.join(self.conf_local, filename)
            with open(local_file_path, "r") as config_file:
                l_file = config_file.read()

            print("Compairing; ", local_file_path, " and ", remote_file_path)
            if to_return == "text":
                return r_file, l_file
            elif to_return == "answer":
                if r_file.strip() == l_file.strip():
                    return True
                else:
                    return False

class compare_conf_file_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.conf_l_txt = parent.conf_l_txt
        self.conf_r_txt = parent.conf_r_txt
        self.conf_filename = parent.conf_filename
        super(compare_conf_file_dialog, self).__init__(*args, **kw)
        self.SetSize((700, 400))
        self.InitUI()
        self.SetTitle("Compairing config files")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # label
        label = wx.StaticText(self,  label='Compairing ' + self.conf_filename)
        #buttons
        self.ok_btn = wx.Button(self, label='ok', size=(175, 50))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.scroll_section(self))
        main_sizer.Add(self.ok_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizerAndFit(main_sizer)

    def OnClose(self, e):
        self.Destroy()

    class scroll_section(scrolled.ScrolledPanel):
        def __init__(self, parent):
            self.parent = parent
            scrolled.ScrolledPanel.__init__(self, parent, -1, size=(600,400))
            vbox = wx.BoxSizer(wx.VERTICAL)
            vbox.Add(self.make_com_sizer(), 0, wx.ALIGN_LEFT | wx.ALL, 5)
            self.SetSizer(vbox)
            self.SetupScrolling()

        def make_com_sizer(self):
            # create dicts from files
            l_txt = self.parent.conf_l_txt
            r_txt = self.parent.conf_r_txt
            l_dict = self.read_conf_to_dict(l_txt)
            r_dict = self.read_conf_to_dict(r_txt)
            # compare
            changed = []
            unchanged = []
            for item in l_dict:
                if item not in r_dict:
                    changed.append([item, 'NEW =' + l_dict[item]])
                else:
                    if not r_dict[item] == l_dict[item]:
                        changed.append([item, ' change from ' + r_dict[item] + " to " + l_dict[item]])
                    else:
                        unchanged.append(item)
            for item in r_dict:
                if item not in l_dict:
                    changed.append([item, 'REMOVED'])

            # make and fill sizer
            #  changed
            conf_sizer = wx.BoxSizer(wx.VERTICAL)
            changed_list_l = wx.StaticText(self,  label="Changed;")
            conf_sizer.Add((10,10))
            conf_sizer.Add(changed_list_l, 0, wx.LEFT, 50)
            conf_sizer.Add((10,10))
            for item in changed:
                changed_text = item[0] + " " + item[1]
                changed_l = wx.StaticText(self,  label=changed_text)
                conf_sizer.Add(changed_l, 0, wx.LEFT, 25)
            #  unchanged
            unchanged_list_l = wx.StaticText(self,  label="Unchanged;")
            conf_sizer.Add((10,10))
            conf_sizer.Add(unchanged_list_l, 0, wx.LEFT, 50)
            conf_sizer.Add((10,10))
            for item in unchanged:
                txt = item + " " + l_dict[item]
                changed_l = wx.StaticText(self,  label=txt)
                conf_sizer.Add(changed_l, 0, wx.LEFT, 25)

            return conf_sizer

        def read_conf_to_dict(self, conf):
            conf = conf.splitlines()
            conf_dict = {}
            for line in conf:
                place = line.find("=")
                if not place == -1:
                    conf_dict[line[:place]] = line[place+1:]

            return conf_dict

class file_upload_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.user_files_to_upload = []
        self.user_folders_to_upload = []
        super(file_upload_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 400))
        self.SetTitle("Upload files to Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # draw the pannel
        label = wx.StaticText(self,  label='Select elements to upload onto pi')

        # select files or folders to download
        self.select_file_btn = wx.Button(self, label='Select files', size=(175, 50))
        self.select_file_btn.Bind(wx.EVT_BUTTON, self.select_file_click)
        # select files
        self.cb_overwrite = wx.CheckBox(self, label='Overwrite existing')
        self.selected_files_l = wx.StaticText(self,  label='--')
        select_file_sizer = wx.BoxSizer(wx.VERTICAL)
        select_file_sizer.Add(self.select_file_btn, 0, wx.ALL|wx.EXPAND, 5)
        select_file_sizer.Add(self.cb_overwrite, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #

        self.selected_dest_folder_l = wx.StaticText(self,  label='--')
        self.select_upload_folder_btn = wx.Button(self, label='Select upload folder', size=(175, 50))
        self.select_upload_folder_btn.Bind(wx.EVT_BUTTON, self.select_upload_folder_click)
        select_dest_sizer = wx.BoxSizer(wx.HORIZONTAL)
        select_dest_sizer.Add(self.selected_dest_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        select_dest_sizer.Add(self.select_upload_folder_btn, 0, wx.ALL|wx.EXPAND, 5)

        #buttons
        self.upload_btn = wx.Button(self, label='Upload', size=(175, 50))
        self.upload_btn.Bind(wx.EVT_BUTTON, self.start_upload_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upload_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(select_file_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(select_dest_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def select_file_click(self, e):
        dialog = wx.FileDialog(self, "Select files to upload to pi", style=wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.filelist = dialog.GetPaths()
        self.Layout()

    def select_upload_folder_click(self, e):
        self.selected_files, self.selected_folders = self.parent.parent.link_pnl.select_files_on_pi(single_folder=True)
        self.selected_dest_folder_l.SetLabel(self.selected_folders[0])
        self.Layout()

    def start_upload_click(self, e):
        dest_fold = self.selected_folders[0]
        tocopy_files = self.filelist
        print("Wants to copy", len(tocopy_files), " files to", dest_fold)
        copy_list = []
        for file in tocopy_files:
            dest = dest_fold + os.path.split(file)[1]
            copy_list.append([file, dest])
        self.parent.parent.link_pnl.upload_files(copy_list)
        self.Layout()
        self.Destroy()

    def OnClose(self, e):
        #closes the dialogue box
    #    self.user_files_to_upload = []
    #    self.user_folders_to_upload = []
        self.Destroy()

class file_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.user_files_to_download = []
        self.user_folders_to_download = []
        super(file_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 400))
        self.SetTitle("Download files from Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # draw the pannel
        label = wx.StaticText(self,  label='Select elements to download to local storage')
        # tick boxes for default folder select
        self.cb_conf = wx.CheckBox(self,  label='Config')
        self.cb_logs = wx.CheckBox(self,  label='Logs')
        self.cb_caps = wx.CheckBox(self,  label='Photos')
        self.cb_graph = wx.CheckBox(self, label='Graphs')
        tickbox_sizer = wx.BoxSizer(wx.VERTICAL)
        tickbox_sizer.Add(self.cb_conf, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_logs, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_caps, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_graph, 0, wx.ALL|wx.EXPAND, 5)
        # select files or folders to download
        self.select_file_btn = wx.Button(self, label='Select Folder', size=(175, 50))
        self.select_file_btn.Bind(wx.EVT_BUTTON, self.select_file_click)
        self.cb_overwrite = wx.CheckBox(self, label='Overwrite existing')
        self.selected_files_l = wx.StaticText(self,  label='--')
        self.selected_folders_l = wx.StaticText(self,  label='--')
        select_file_sizer = wx.BoxSizer(wx.VERTICAL)
        select_file_sizer.Add(self.select_file_btn, 0, wx.ALL|wx.EXPAND, 5)
        select_file_sizer.Add(self.cb_overwrite, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        select_file_sizer.Add(self.selected_files_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        select_file_sizer.Add(self.selected_folders_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #buttons
        self.download_btn = wx.Button(self, label='Download', size=(175, 50))
        self.download_btn.Bind(wx.EVT_BUTTON, self.start_download_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.download_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # mid pnl
        mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mid_sizer.AddStretchSpacer(1)
        mid_sizer.Add(tickbox_sizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        mid_sizer.AddStretchSpacer(1)
        mid_sizer.Add(select_file_sizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        mid_sizer.AddStretchSpacer(1)
        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(mid_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def select_file_click(self, e):
        selected_files, selected_folders = self.parent.parent.link_pnl.select_files_on_pi()
        if len(selected_files) == 0 and len(selected_folders) == 0:
            return None
        # folders
        if len(selected_folders) > 0:
            in_fold_list = self.selected_folders_l.GetLabel()
            for fold in selected_folders:
                in_fold_list += "\n" + fold
                self.user_folders_to_download.append(fold)
            in_fold_list = in_fold_list.replace("--\n", "")
            self.selected_folders_l.SetLabel(in_fold_list)

        # files
        file_list = self.user_files_to_download
        if len(selected_files) > 0:
            for s_file in selected_files:
                if not s_file in self.user_files_to_download:
                    self.user_files_to_download.append(s_file)
            # make text
            in_file_text = ""
            for item in self.user_files_to_download:
                in_file_text += item[0] + "\n"
            self.selected_files_l.SetLabel(in_file_text)
        self.Layout()


    def start_download_click(self, e):
        folders_overwrite = []
        folders_newonly   = []
        remote_path = self.parent.parent.shared_data.remote_pigrow_path
        if self.cb_conf.GetValue() == True:
            folders_overwrite.append(remote_path + "config")
        if self.cb_logs.GetValue() == True:
            folders_overwrite.append(remote_path + "logs")
        if self.cb_caps.GetValue() == True:
            remote_caps_path = self.parent.parent.dict_I_pnl['localfiles_pnl'].r_folder_text.GetLabel()
            print(" ---remote---- ", remote_caps_path, " --------- ")
            local_caps_path = self.parent.parent.dict_I_pnl['localfiles_pnl'].folder_text.GetLabel()
            print(" ---local---- ", local_caps_path, " --------- ")
            folders_newonly.append([remote_caps_path, local_caps_path])
        if self.cb_graph.GetValue() == True:
            folders_overwrite.append(remote_path + "graphs")
        # set if overwrite is ticked
        if self.cb_overwrite.GetValue() == True:
            #print(" OVERWRITING FILES")
            folders_overwrite = folders_overwrite + self.user_folders_to_download
            extra_files_over = []
            extra_files = self.user_files_to_download
        else:
            #print(" NOT OVERWRITING FILES")
            folders_newonly = folders_newonly + self.user_folders_to_download
            extra_files_over = self.user_files_to_download
            extra_files = []
        #
        #if len(extra_files) > 0 or len(extra_files_over) > 0:
        #    print(" HAS USER FILES TO DOWNLOAD!!!! ")
        #if len(self.user_folders_to_download) > 0:
        #    print(" HAS USER FOLDERS TO DOWNLOAD!!!! ")

        # only run if something to download
        if not len(folders_overwrite) == 0 or not len(extra_files_over) == 0:
            self.parent.parent.link_pnl.download_folder(folders_overwrite, overwrite=True, extra_files=extra_files_over)
        if not len(folders_newonly) == 0 or not len(extra_files) == 0:
            self.parent.parent.link_pnl.download_folder(folders_newonly, overwrite=False, extra_files=extra_files)

        #if not len(folders_overwrite) == 0 or not len(folders_newonly) == 0:
        self.user_files_to_download = []
        self.user_folders_to_download = []
        self.Destroy()

    def OnClose(self, e):
        #closes the dialogue box
        self.user_files_to_download = []
        self.user_folders_to_download = []
        self.Destroy()

class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['localfiles_pnl']
        w = 1000
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (w,-1))
        # Title and Subtitle
        self.SetFont(self.shared_data.title_font)
        page_title =  wx.StaticText(self,  label='Local Files')
        self.SetFont(self.shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Files downloaded from the pi and stored locally')
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Config Files
        config_l = wx.StaticText(self,  label='Config')
        config_l.SetFont(self.shared_data.item_title_font)
        self.config_files = self.config_file_list(self, 1)
        self.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.config_files.doubleclick_config)
        # Log Files
        log_l = wx.StaticText(self,  label='Log')
        log_l.SetFont(self.shared_data.info_font)
        self.log_files = self.log_file_list(self, 1)
        self.log_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.log_files.doubleclick_log)

        tables_sizer = wx.BoxSizer(wx.VERTICAL)
        tables_sizer.Add(config_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.config_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(log_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.log_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.SetItemMinSize(self.config_files, (w, -1))
        tables_sizer.SetItemMinSize(self.log_files, (w, -1))

        # Photo sizer and label
        self.SetFont(self.shared_data.item_title_font)
        photo_l = wx.StaticText(self,  label='Photos')
        photo_sizer = self.make_photo_sizer()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(tables_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(photo_l, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(photo_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)

    def make_photo_sizer(self):
        # local caps folder
        self.auto_path_checkbox = wx.CheckBox(self, label='Automatic local path')
        self.auto_path_checkbox.Bind(wx.EVT_CHECKBOX, self.on_auto_path_checkbox)
        self.auto_path_checkbox.SetValue(True)
        auto_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        auto_path_sizer.AddStretchSpacer()
        auto_path_sizer.Add(self.auto_path_checkbox, 0, wx.ALIGN_CENTER)
        #
        self.SetFont(self.shared_data.info_font)
        caps_folder_l = wx.StaticText(self,  label='Local;')
        caps_folder = os.path.join(self.shared_data.frompi_path, 'caps')
        self.folder_text = wx.StaticText(self,  label=caps_folder)
        self.set_caps_folder_btn = wx.Button(self, label='...')
        self.set_caps_folder_btn.Bind(wx.EVT_BUTTON, self.set_caps_folder_click)
        self.set_caps_folder_btn.Disable()
        caps_folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        caps_folder_sizer.Add(caps_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        caps_folder_sizer.Add(self.folder_text, 0, wx.ALL|wx.EXPAND, 5)
        caps_folder_sizer.Add(self.set_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 5)

        # remote caps folder
        r_caps_folder_l = wx.StaticText(self,  label='Remote;')
        r_caps_folder = self.shared_data.remote_pigrow_path + 'caps'
        self.r_folder_text = wx.StaticText(self,  label=r_caps_folder)
        self.set_r_caps_folder_btn = wx.Button(self, label='...')
        self.set_r_caps_folder_btn.Bind(wx.EVT_BUTTON, self.set_r_caps_folder_click)
        r_caps_folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        r_caps_folder_sizer.Add(r_caps_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        r_caps_folder_sizer.Add(self.r_folder_text, 0, wx.ALL|wx.EXPAND, 5)
        r_caps_folder_sizer.Add(self.set_r_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 5)

        # download most recent pic buttons
        get_newest_cap_btn = wx.Button(self, label='Get most recent cap')
        get_newest_cap_btn.Bind(wx.EVT_BUTTON, self.get_newest_cap_click)
        cap_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cap_but_sizer.Add(get_newest_cap_btn, 0, wx.ALL, 5)

        self.photo_first_text = wx.StaticText(self, label='--')
        self.photo_mid_text   = wx.StaticText(self, label='--', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.r_mid_text       = wx.StaticText(self, label='--', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.photo_last_text  = wx.StaticText(self, label='--')

        photo_dates_sizer = wx.BoxSizer(wx.HORIZONTAL)
        photo_dates_sizer.Add(self.photo_first_text, 0, wx.RIGHT, 5)
        photo_dates_sizer.AddStretchSpacer(1)
        photo_dates_sizer.Add(self.photo_last_text, 0, wx.LEFT, 5)
        photo_mid_sizer = wx.BoxSizer(wx.VERTICAL)
        photo_mid_sizer.Add(auto_path_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_mid_sizer.Add(caps_folder_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_mid_sizer.Add(r_caps_folder_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_mid_sizer.Add(photo_dates_sizer, 0, wx.ALL|wx.EXPAND, 1)
        photo_mid_sizer.Add(self.photo_mid_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        photo_mid_sizer.Add(self.r_mid_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        photo_mid_sizer.Add(cap_but_sizer, 0, wx.ALL|wx.EXPAND, 5)

        blank_img = wx.Bitmap(255, 255)
        self.first_photo_title = wx.StaticText(self,  label='first image')
        self.photo_folder_first_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        self.photo_folder_first_pic.SetToolTip("none")
        self.photo_folder_first_pic.Bind(wx.EVT_BUTTON, self.img_click)
        self.last_photo_title = wx.StaticText(self,  label='last image')
        self.photo_folder_last_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        self.photo_folder_last_pic.SetToolTip("none")
        self.photo_folder_last_pic.Bind(wx.EVT_BUTTON, self.img_click)
        first_pic_sizer = wx.BoxSizer(wx.VERTICAL)
        first_pic_sizer.Add(self.photo_folder_first_pic, 0, wx.ALL|wx.EXPAND, 5)
        first_pic_sizer.Add(self.first_photo_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        last_pic_sizer = wx.BoxSizer(wx.VERTICAL)
        last_pic_sizer.Add(self.photo_folder_last_pic, 0, wx.ALL|wx.EXPAND, 5)
        last_pic_sizer.Add(self.last_photo_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        photo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        photo_sizer.Add(first_pic_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_sizer.Add(photo_mid_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_sizer.Add(last_pic_sizer, 0, wx.ALL|wx.EXPAND, 5)

        return photo_sizer

    def on_auto_path_checkbox(self, e):
        is_checked = self.auto_path_checkbox.GetValue()
        self.set_caps_folder_btn.Enable(not is_checked)
        if is_checked:
            self.set_auto_localpath()

    def set_auto_localpath(self):
        r_path = self.r_folder_text.GetLabel()
        if "Pigrow/" in r_path:
            print("found pigrow")
            folder = r_path.split("Pigrow/")[1]
            l_path = os.path.join(self.parent.shared_data.frompi_path, folder)
        else:
            name = os.path.basename(os.path.normpath(r_path))
            l_path = os.path.join(self.parent.shared_data.frompi_path, name)
        self.folder_text.SetLabel(l_path)
        self.read_caps_info()
        self.Layout()

    def set_r_caps_folder_click(self, e):
        selected_files, selected_folders = self.parent.link_pnl.select_files_on_pi(single_folder=True)
        self.r_folder_text.SetLabel(selected_folders[0])
        self.set_r_caps_text()

        if self.auto_path_checkbox.GetValue():
            self.set_auto_localpath()

        self.Layout()

    def set_r_caps_text(self):
        r_path = self.r_folder_text.GetLabel()
        out, error = self.parent.link_pnl.run_on_pi("ls " + r_path)
        r_file_list = out.splitlines()
        text = "Remote folder " + str(len(r_file_list)) + " files"
        if len(r_file_list) > 1:
            f_pic_date = self.parent.shared_data.date_from_fn(r_file_list[0])
            l_pic_date = self.parent.shared_data.date_from_fn(r_file_list[-1])
            if f_pic_date == None or l_pic_date == None:
                text += "\nfilename dates not readable"
            else:
                time_delta = l_pic_date - f_pic_date
                text += "\n" + str(f_pic_date) + " - " + str(l_pic_date)
                text += "\nDuration " + str(time_delta)

        self.r_mid_text.SetLabel(text)

    def img_click(self, e):
        obj = e.GetEventObject()
        tip_path = obj.GetToolTipText()
        print (tip_path)
        if not tip_path == "none":
            dbox = self.parent.shared_data.show_image_dialog(None, tip_path, "First image")
            dbox.ShowModal()
            dbox.Destroy()

    def set_caps_folder_click(self, e):
        # get folder

        #
        default = self.parent.shared_data.frompi_path
        openFileDialog = wx.DirDialog(self, "Select caps folder", default, style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST | wx.DD_NEW_DIR_BUTTON)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()
        #
        self.folder_text.SetLabel(new_cap_path)
        self.read_caps_info()
        self.Layout()

    def read_caps_info(self):
        caps_folder = self.folder_text.GetLabel()

        if not os.path.exists(caps_folder):
            os.makedirs(caps_folder)

        file_list = os.listdir(caps_folder)
        pic_list = []
        img_types = ['jpg', 'gif', 'png', 'bmp', 'raw']
        for item in file_list:
            if "." in item:
                img_type = item.split(".")[1]
                if img_type in img_types:
                    full_path = os.path.join(caps_folder, item)
                    pic_list.append(full_path)
        pic_list.sort()

        self.set_mid_text(pic_list)
        if len(pic_list) > 0:
            name = os.path.split(pic_list[0])[1]
            self.first_photo_title.SetLabel(name)
            self.set_image_preview(pic_list[0], 'first')
            self.photo_first_text.SetLabel(self.make_image_text(pic_list[0]))
            if len(pic_list) > 1:
                name = os.path.split(pic_list[-1])[1]
                self.last_photo_title.SetLabel(name)
                self.set_image_preview(pic_list[-1], 'last')
                self.photo_last_text.SetLabel(self.make_image_text(name))
            else:
                print(" Only one image in caps folder")
                self.last_photo_title.SetLabel("--")
                self.set_image_preview(None, 'last')
        else:
            print(" No image files to load")
            self.first_photo_title.SetLabel("--")
            self.last_photo_title.SetLabel("--")
            self.set_image_preview(None, 'first')
            self.set_image_preview(None, 'last')

    def set_image_preview(self, img_path, place):
        #print("Loading -", img_path, "to", place)
        try:
            pic = wx.Image(img_path, wx.BITMAP_TYPE_ANY)
            pic = self.parent.shared_data.scale_pic(pic, 300)
            pic = pic.ConvertToBitmap()
            if place == 'first':
                self.photo_folder_first_pic.SetToolTip(img_path)
                self.photo_folder_first_pic.SetBitmap(pic)
            if place == 'last':
                self.photo_folder_last_pic.SetToolTip(img_path)
                self.photo_folder_last_pic.SetBitmap(pic)
        except:
            #raise
            if not img_path == None:
                print("!! image in local caps folder didn't work.", img_path)
            blank_bitmap = wx.Bitmap(100, 100)
            if place == 'first':
                self.photo_folder_first_pic.SetToolTip('no image')
                self.photo_folder_first_pic.SetBitmap(blank_bitmap)
            elif place == "last":
                self.photo_folder_last_pic.SetToolTip('no image')
                self.photo_folder_last_pic.SetBitmap(blank_bitmap)

    def make_image_text(self, pic_path):
        pic_date = self.parent.shared_data.date_from_fn(pic_path)
        pic_text = str(pic_date)
        return pic_text

    def set_mid_text(self, pic_list):
        mid_text = str(len(pic_list)) + " files locally"
        # length of image dates
        if len(pic_list) > 1:
            date_f = self.parent.shared_data.date_from_fn(pic_list[0])
            date_l = self.parent.shared_data.date_from_fn(pic_list[-1])
            if date_f == None or date_l == None:
                mid_text += "\ndates not readable"
            else:
                caps_delta = date_l - date_f
                mid_text += "\nDuration " + str(caps_delta)

        self.photo_mid_text.SetLabel(mid_text)
        self.Layout()

    def get_newest_cap_click(self, e):
        #print("wants to download the newest cap")
        r_path = self.r_folder_text.GetLabel()
        out, error = self.parent.link_pnl.run_on_pi("ls " + r_path)
        file_list = out.splitlines()
        last_pic = self.get_last_pic(file_list)
        print("Newest cap is", last_pic)
        #
        remote_path = r_path + "/" + last_pic
        local_path  = os.path.join(self.folder_text.GetLabel(), last_pic)
        if not os.path.isfile(local_path):
            print("Copying", remote_path, "to", local_path)
            self.parent.link_pnl.download_file_to_folder(remote_path, local_path)
        else:
            print("Already downloaded most recent cap")
        #
        pic_date = self.parent.shared_data.date_from_fn(last_pic)
        age = datetime.datetime.now() - pic_date
        age = str(age).split(".")[0]
        title = "Most recent image, age: " + str(age)
        dbox = self.parent.shared_data.show_image_dialog(None, local_path, title)
        dbox.ShowModal()
        dbox.Destroy()

    def get_last_pic(self, file_list):
        file_list.reverse()
        for file in file_list:
            if ".jpg" in file or ".png" in file:
                return file

    class config_file_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified', format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(2, 'age', format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(3, 'size', format=wx.LIST_FORMAT_CENTER)
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, l + 15)
                else:
                    self.SetColumnWidth(i, h + 15)

        def add_to_config_list(self, name, mod_date, age, size):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))
            self.SetItem(0, 3, str(size))

        def read_configs(self, folder_name):
            self.DeleteAllItems()
            print("Loading content of config folder into listctrl")
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            if not os.path.exists(full_path):
                print(" - folder not found " + full_path)
                return None
            config_files = os.listdir(full_path)
            for file in config_files:
                if file.endswith("txt"):
                    thing_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(thing_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    file_size = os.path.getsize(thing_path)
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    file_size = self.format_size(file_size)
                    self.add_to_config_list(file, modified, file_age, file_size)
            self.autosizeme()

        def format_size(self, size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:3.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"

        def doubleclick_config(self, e):
            shared_data = self.parent.parent.shared_data
            index =  e.GetIndex()
            filename = self.GetItem(index, 0).GetText()
            file_path = os.path.join(shared_data.frompi_path, "config", filename)
            with open(file_path, "r") as config_file:
                config_file_text = config_file.read()
            dbox = shared_data.scroll_text_dialog(None, config_file_text, "Editing " + filename, True, False)
            dbox.ShowModal()
            out_conf = dbox.text
            dbox.Destroy()
            if out_conf == None:
                #print("User aborted")
                return None
            else:
                if not out_conf == config_file_text:
                    question_text = "Save changes to config file?"
                    question_text += "\n\nNote: This will not change it on the pi until you upload it over writing the original."
                    dbox = wx.MessageDialog(self, question_text, "Save Changes?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    if (answer == wx.ID_OK):
                        with open(file_path, "w") as config_file:
                            config_file.write(out_conf)
                        print(" Config file " + filename + " changes saved")
                else:
                    #print("Config file unchanged")
                    return None

    class log_file_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified', format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(2, 'age', format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(3, 'size', format=wx.LIST_FORMAT_CENTER)
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, l + 15)
                else:
                    self.SetColumnWidth(i, h + 15)

        def doubleclick_log(self, e):
            shared_data = self.parent.parent.shared_data
            index =  e.GetIndex()
            filename = self.GetItem(index, 0).GetText()
            full_path = os.path.join(shared_data.frompi_path, "logs", filename)
            log_dialog = log_detail_dialog(self, filename, full_path)
            log_dialog.ShowModal()
            log_dialog.Destroy()

        def add_to_logs_list(self, name, mod_date, age, size):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))
            self.SetItem(0, 3, str(size))

        def read_logs(self, folder_name):
            self.DeleteAllItems()
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            if not os.path.exists(full_path):
                print(" - folder not found " + full_path)
                return None
            logs_files = os.listdir(full_path)
            for file in logs_files:
                if file.endswith("txt"):
                    file_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(file_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    file_size = os.path.getsize(file_path)
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    file_size = self.format_size(file_size)
                    self.add_to_logs_list(file, modified, file_age, file_size)
            self.autosizeme()

        def format_size(self, size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:3.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"


class log_detail_dialog(wx.Dialog):
    def __init__(self, parent, filename, file_path):
        super(log_detail_dialog, self).__init__(parent, title=f"Log details - {filename}")
        self.file_path = file_path
        self.filename = filename
        self.SetSize((800, 600))
        self.showing_full_log = False
        self.InitUI()

    def InitUI(self):
        stat_info = os.stat(self.file_path)
        modified = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        age = datetime.datetime.now() - modified
        readable_age = str(age).split(".")[0]
        readable_date = modified.strftime("%Y-%m-%d %H:%M")
        file_size = self.format_size(stat_info.st_size)
        with open(self.file_path, "r") as log_file:
            self.log_lines = log_file.read().splitlines()
        last_lines = "\n".join(self.log_lines[-10:])

        filename_l = wx.StaticText(self, label=f"Name: {self.filename}")
        date_l = wx.StaticText(self, label=f"Date: {readable_date}")
        age_l = wx.StaticText(self, label=f"Age: {readable_age}")
        size_l = wx.StaticText(self, label=f"Size: {file_size}")

        self.log_text = wx.TextCtrl(self, value=last_lines, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.log_text.SetMinSize((750, 250))

        self.show_full_btn = wx.Button(self, label='Show full log')
        self.show_full_btn.Bind(wx.EVT_BUTTON, self.show_full_log)

        self.graph_btn = wx.Button(self, label='Graph log')
        self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_log)

        log_type = self.detect_log_type(self.log_lines)
        log_type_l = wx.StaticText(self, label=f"Log type: {log_type}")

        type_sizer = wx.BoxSizer(wx.VERTICAL)
        type_sizer.Add(log_type_l, 0, wx.ALL, 5)

        if log_type == 'k=v>':
            kv_panel = self.build_kv_summary(self.log_lines)
            type_sizer.Add(kv_panel, 0, wx.ALL | wx.EXPAND, 5)

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_sizer.Add(filename_l, 0, wx.ALL, 5)
        info_sizer.Add(date_l, 0, wx.ALL, 5)
        info_sizer.Add(age_l, 0, wx.ALL, 5)
        info_sizer.Add(size_l, 0, wx.ALL, 5)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.show_full_btn, 0, wx.ALL, 5)
        button_sizer.Add(self.graph_btn, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(info_sizer, 0, wx.ALL, 5)
        main_sizer.Add(self.log_text, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(button_sizer, 0, wx.ALL, 5)
        main_sizer.Add(type_sizer, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(main_sizer)

    def show_full_log(self, e):
        if not self.showing_full_log:
            full_text = "\n".join(self.log_lines)
            self.log_text.SetValue(full_text)
            self.show_full_btn.SetLabel('Show last 10 lines')
            self.showing_full_log = True
        else:
            self.log_text.SetValue("\n".join(self.log_lines[-10:]))
            self.show_full_btn.SetLabel('Show full log')
            self.showing_full_log = False

    def graph_log(self, e):
        print('graph link coming soon')

    def detect_log_type(self, lines):
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if '>' in stripped and '=' in stripped:
                segments = [seg for seg in stripped.split('>') if seg]
                if segments and all('=' in seg for seg in segments):
                    return 'k=v>'
            break
        return 'unknown'

    def build_kv_summary(self, lines):
        stats = {}
        for line in lines:
            segments = [seg for seg in line.strip().split('>') if seg]
            for seg in segments:
                if '=' not in seg:
                    continue
                key, value = seg.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key not in stats:
                    stats[key] = []
                stats[key].append(value)

        panel = wx.Panel(self)
        grid = wx.FlexGridSizer(rows=len(stats) + 1, cols=4, hgap=10, vgap=5)
        headers = ['Key', 'Most recent', 'Min', 'Max']
        for header in headers:
            grid.Add(wx.StaticText(panel, label=header), 0, wx.ALL, 5)

        for key, values in stats.items():
            min_val, max_val = self.calculate_min_max(values)
            grid.Add(wx.StaticText(panel, label=key), 0, wx.ALL, 5)
            grid.Add(wx.StaticText(panel, label=values[-1]), 0, wx.ALL, 5)
            grid.Add(wx.StaticText(panel, label=min_val), 0, wx.ALL, 5)
            grid.Add(wx.StaticText(panel, label=max_val), 0, wx.ALL, 5)

        panel.SetSizer(grid)
        return panel

    def calculate_min_max(self, values):
        numeric_values = []
        for val in values:
            try:
                numeric_values.append(float(val))
            except ValueError:
                numeric_values = []
                break
        if numeric_values:
            min_val = str(min(numeric_values))
            max_val = str(max(numeric_values))
        else:
            min_val = min(values)
            max_val = max(values)
        return min_val, max_val

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:3.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
