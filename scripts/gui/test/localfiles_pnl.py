import os
import datetime
import wx
import wx.lib.scrolledpanel as scrolled

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # read / save cam config button
        self.read_btn = wx.Button(self, label='Read local files')
        self.read_btn.Bind(wx.EVT_BUTTON, self.read_click)
        self.download_btn = wx.Button(self, label='Download')
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.read_btn, 0, wx.ALL, 0)
        main_sizer.Add(self.download_btn, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)

    def read_click(self, e):
        if self.parent.shared_data.frompi_path == "":
            print("No frompi folder set, check link to pi is active")
            return None
        config_folder = "config"
        logs_folder   = "logs"
        I_pnl = self.parent.dict_I_pnl['localfiles_pnl']
        I_pnl.config_file_list.read_configs(I_pnl.config_files, config_folder)
        I_pnl.log_file_list.read_logs(I_pnl.log_files, logs_folder)

    def download_click(self, e):
        file_dbox = file_download_dialog(self, self.parent)
        file_dbox.ShowModal()
        file_dbox.Destroy()
        #self.read_click("e")

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
        print(" THE BUTTON HAS BEEN PRESSED ")
        self.parent.parent.link_pnl.select_files_on_pi()
        selected_files = self.parent.parent.link_pnl.selected_files
        selected_folders = self.parent.parent.link_pnl.selected_folders
        if len(selected_files) == 0 and len(selected_folders) == 0:
            print("Nothing selected so not doing nothing lol")
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
            folders_newonly.append(remote_path + "caps")
        if self.cb_graph.GetValue() == True:
            folders_overwrite.append(remote_path + "graphs")
        # set if overwrite is ticked
        if self.cb_overwrite.GetValue() == True:
            print(" OVERWRITING FILES")
            folders_overwrite = folders_overwrite + self.user_folders_to_download
            extra_files_over = []
            extra_files = self.user_files_to_download
        else:
            print(" NOT OVERWRITING FILES")
            folders_newonly = folders_newonly + self.user_folders_to_download
            extra_files_over = self.user_files_to_download
            extra_files = []
        #
        if len(extra_files) > 0 or len(extra_files_over) > 0:
            print(" HAS USER FILES TO DOWNLOAD!!!! ")
        if len(self.user_folders_to_download) > 0:
            print(" HAS USER FOLDERS TO DOWNLOAD!!!! ")

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
        self.Destroy()

#class info_pnl(wx.Panel):
class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['localfiles_pnl']
        w = 1000
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (w,-1))
        # Title and Subtitle
        page_title =  wx.StaticText(self,  label='Local Files')
        page_sub_title =  wx.StaticText(self,  label='Files downloaded from the pi and stored locally')
        page_title.SetFont(shared_data.title_font)
        page_sub_title.SetFont(shared_data.sub_title_font)
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Config Files
        config_l = wx.StaticText(self,  label='Config')
        config_l.SetFont(shared_data.item_title_font)
        self.config_files = self.config_file_list(self, 1)
        self.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.config_files.doubleclick_config)
        # Log Files
        log_l = wx.StaticText(self,  label='Log')
        log_l.SetFont(shared_data.item_title_font)
        self.log_files = self.log_file_list(self, 1)
        self.log_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.log_files.doubleclick_log)

        tables_sizer = wx.BoxSizer(wx.VERTICAL)
        tables_sizer.Add(config_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.config_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(log_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.log_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.SetItemMinSize(self.config_files, (w, -1))
        tables_sizer.SetItemMinSize(self.log_files, (w, -1))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(tables_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)

    class config_file_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.autosizeme()

        def autosizeme(self):
            if self.GetItemCount() == 0:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(3, wx.LIST_AUTOSIZE)

        def add_to_config_list(self, name, mod_date, age, update_status):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))
            self.SetItem(0, 3, str(update_status))

        def read_configs(self, folder_name):
            self.DeleteAllItems()
            print("Loading content of config folder into listctrl")
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            config_files = os.listdir(full_path)
            for file in config_files:
                if file.endswith("txt"):
                    thing_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(thing_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    update_status = "unchecked"
                    self.add_to_config_list(file, modified, file_age, update_status)
            self.autosizeme()

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
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.autosizeme()

        def doubleclick_log(self, e):
            shared_data = self.parent.parent.shared_data
            index =  e.GetIndex()
            filename = self.GetItem(index, 0).GetText()

        def autosizeme(self):
            if self.GetItemCount() == 0:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        def add_to_logs_list(self, name, mod_date, age):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))

        def read_logs(self, folder_name):
            self.DeleteAllItems()
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            logs_files = os.listdir(full_path)
            for file in logs_files:
                if file.endswith("txt"):
                    file_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(file_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    self.add_to_logs_list(file, modified, file_age)
            self.autosizeme()
