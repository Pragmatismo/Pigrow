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
        print(usrlog, "has been selected")

    def refresh_list_click(self, e):
        if self.parent.shared_data.remote_pigrow_path == "":
            return None
        r_log_path = self.parent.shared_data.remote_pigrow_path + "logs"
        out, error = self.parent.link_pnl.run_on_pi("ls " + r_log_path)
        files = out.splitlines()

        # Filter files starting with 'userlog_' and ending with '.txt'
        log_files = [file[:-4] for file in files if file.startswith('userlog_') and file.endswith('.txt')]
        print("Found ", len(log_files), "user logs in", r_log_path)
        # Update ComboBox choices
        self.log_cb.Clear()
        self.log_cb.AppendItems(log_files)


    def new_log_click(self, e):
        print("-- new log click, does nothing.")



class info_pnl(wx.Panel):
    #
        def __init__( self, parent ):
            self.parent = parent
            shared_data = parent.shared_data
            self.c_pnl = parent.dict_C_pnl['userlog_pnl']
            w = 1000
            wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

            # Tab Title
            self.SetFont(shared_data.title_font)
            title_l = wx.StaticText(self,  label='Userlog')
            self.SetFont(shared_data.sub_title_font)
            sub_title_text = "This tool reads and edits user created logs stored on the raspberry pi. "
            sub_title_text += "\n\nThere will be tools available to write to the logs from a phone app or on the pi itself."
            page_sub_title =  wx.StaticText(self,  label=sub_title_text)

            # Main Sizer
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            #main_sizer.AddStretchSpacer(1)
            self.SetSizer(main_sizer)
