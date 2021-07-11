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
        self.read_btn = wx.Button(self, label='read config')
        self.read_btn.Bind(wx.EVT_BUTTON, self.read_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.read_btn, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)

    def read_click(self, e):
        if self.parent.shared_data.frompi_path == "":
            print("No frompi folder set, check link to pi is active")
            return None
        config_folder = "config"
        logs_folder   = "logs"
        print(" This button does almost nothing.")
        I_pnl = self.parent.dict_I_pnl['localfiles_pnl']
        I_pnl.config_file_list.read_configs(I_pnl.config_files, config_folder)
        I_pnl.log_file_list.read_logs(I_pnl.log_files, logs_folder)


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
