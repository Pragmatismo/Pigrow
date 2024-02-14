import wx


class ctrl_pnl(wx.Panel):
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        ## log
        self.log_cb = wx.ComboBox(self, choices = [])
        self.log_cb.Bind(wx.EVT_COMBOBOX, self.on_log_select)
        refresh_list_btn = wx.Button(self, label='refresh')
        refresh_list_btn.Bind(wx.EVT_BUTTON, self.refresh_list_click)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_cb, 0, wx.ALL, 5)
        log_sizer.Add(refresh_list_btn, 0, wx.ALL, 5)

        new_log_btn = wx.Button(self, label='New Log')
        new_log_btn.Bind(wx.EVT_BUTTON, self.new_log_click)

        ## Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(log_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(new_log_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def connect_to_pigrow(self):
        self.refresh_list_click(None)

    def on_log_select(self, event):
        selected_item = self.log_cb.GetValue()
        usrlog = "userlog_" + selected_item + ".txt"
        I_pnl = self.parent.dict_I_pnl['userlog_pnl']
        I_pnl.log_path.SetLabel(usrlog)
        I_pnl.Layout()

    def refresh_list_click(self, e):
        if self.parent.shared_data.remote_pigrow_path == "":
            return None
        r_log_path = self.parent.shared_data.remote_pigrow_path + "logs"
        out, error = self.parent.link_pnl.run_on_pi("ls " + r_log_path)
        files = out.splitlines()

        # Filter files starting with 'userlog_' and ending with '.txt'
        log_files = [file[8:-4] for file in files if file.startswith('userlog_') and file.endswith('.txt')]
        print("Found", len(log_files), "user logs in", r_log_path)
        # Update ComboBox choices
        self.log_cb.Clear()
        self.log_cb.AppendItems(log_files)


    def new_log_click(self, e):
        print("-- new log click, does nothing.")



class info_pnl(wx.Panel):
    #
    def __init__( self, parent ):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['userlog_pnl']
        w = 1000
        wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self,  label='Userlog')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This tool reads and edits user created logs stored on the raspberry pi. "
        sub_title_text += "\n\nThere will be tools available to write to the logs from a phone app or on the pi itself."
        page_sub_title =  wx.StaticText(self,  label=sub_title_text)

        # Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.make_log_tool_sizer(), 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def make_log_tool_sizer(self):
        self.SetFont(self.shared_data.item_title_font)
        log_title_l = wx.StaticText(self,  label='Log Tools')
        # log path label
        self.SetFont(self.shared_data.info_font)
        log_path_l = wx.StaticText(self,  label='Log Path')
        self.log_path = wx.StaticText(self,  label='')
        log_path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_path_sizer.Add(log_path_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        log_path_sizer.Add(self.log_path, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)

        # field edit buttons
        add_field_btn = wx.Button(self, label='Add field')
        add_field_btn.Bind(wx.EVT_BUTTON, self.add_field_click)
        edit_field_btn = wx.Button(self, label='Edit field')
        edit_field_btn.Bind(wx.EVT_BUTTON, self.edit_field_click)
        del_field_btn = wx.Button(self, label='Delete field')
        del_field_btn.Bind(wx.EVT_BUTTON, self.del_field_click)
        field_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        field_but_sizer.Add(add_field_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        field_but_sizer.Add(edit_field_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)
        field_but_sizer.Add(del_field_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 15)

        # log sizer
        log_sizer = wx.BoxSizer(wx.VERTICAL)
        log_sizer.Add(log_title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        log_sizer.Add(log_path_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        log_sizer.Add(field_but_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        return log_sizer

    def add_field_click(self, e):
        print("Sorry no new fields for you :P")

    def edit_field_click(self, e):
        print("Not editing a field that would be tiresome")

    def del_field_click(self, e):
        print("sorry I refuse to remove any fields")
