import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170))


        self.fill_table_btn = wx.Button(self, label='Fill Table')
        self.fill_table_btn.Bind(wx.EVT_BUTTON, self.fill_table_click)

        self.add_tank_btn = wx.Button(self, label='Add Tank')
        self.add_tank_btn.Bind(wx.EVT_BUTTON, self.add_tank_click)

        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.fill_table_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.add_tank_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def fill_table_click(self, e):
        self.parent.shared_data.read_pigrow_settings_file()
        i_pnl = self.parent.dict_I_pnl['watering_pnl']
        i_pnl.wtank_lst.make_table()

    def add_tank_click(self, e):
        #i_pnl = self.parent.dict_I_pnl['watering_pnl']
        # load config from file and fill tables so there are no conflicts
    #    self.fill_tables_click("e")
        # set blanks for dialog box
        # call dialog box
        tank_dialog.s_name = ""
        tank_dialog.s_volume = ""
        tank_dialog.s_mode = ""
        add_dlb = tank_dialog(self, self.parent)
        add_dlb.ShowModal()
    #    self.fill_tables_click("e")

    def connect_to_pigrow(self):
        '''
        This is called every time a connection to a pigrow is made
        '''
        # Set values from config for set
        #if '---setting name goes here------' in shared_data.gui_set_dict:
        #self.tank_size_tc.SetValue(shared_data.gui_set_dict['---setting name goes here------'])
        pass

class info_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['watering_pnl']
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        #self.SetBackgroundColour((50,50,50))

        # Tab Title
        title_l = wx.StaticText(self,  label='Watering Control Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Self Watering System Control', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)

        # water tank table
        tank_l =  wx.StaticText(self,  label='Water Tank')
        tank_l.SetFont(shared_data.sub_title_font)
        self.wtank_lst = self.water_tank_list(self, 1)
        self.wtank_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.wtank_lst.doubleclick)

        tank_table_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_table_sizer.Add(tank_l, 1, wx.ALL|wx.EXPAND, 3)
        tank_table_sizer.Add(self.wtank_lst, 0, wx.ALL|wx.EXPAND, 3)

        # Tank Size Panel
        tank_size_title =  wx.StaticText(self,  label='Tank Size Calculations')
        self.tank_size_st = wx.StaticText(self, label='Tank Size in mL')
        self.tank_size_tc = wx.TextCtrl(self)
        t_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        t_size_sizer.Add(self.tank_size_st, 1, wx.ALL, 3)
        t_size_sizer.Add(self.tank_size_tc, 1, wx.ALL, 3)

        tank_size_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_size_sizer.Add(tank_size_title, 1, wx.ALL|wx.EXPAND, 3)
        tank_size_sizer.Add(t_size_sizer, 1, wx.ALL, 3)

        # Main Sizer 
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tank_table_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(tank_size_sizer, 1, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    class water_tank_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'Size')
            self.InsertColumn(2, 'Type')
            self.InsertColumn(3, 'Status')
            self.autosizeme()

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            wtank_list = []
            print("  - Using config_dict to fill water tank table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "wtank_" in key:
                    name = key.split("_")[1]
                    if not name in wtank_list:
                        wtank_list.append(name)

            for name in wtank_list:
                size, type = self.read_wtank_conf(name, config_dict, "wtank_")
                self.add_to_relay_table(name, size, type)

        def read_wtank_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["_vol",
                          "_mode"]
            info = []
            for field in field_list:
                field_key = prefix + item_name + field
                if field_key in config_dict:
                    info.append(config_dict[field_key])
                else:
                    info.append("")
            return info

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

        def add_to_relay_table(self, name, size, type):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(size))
            self.SetItem(0, 2, str(type))
            tank_status = self.read_tank_state()
            self.SetItem(0, 3, str(tank_status))

        def doubleclick(self, e):
            index =  e.GetIndex()
            print(" please don't click on " + str(e) + " it does nothing")
            #get info for dialogue box
            tank_dialog.s_name  = self.GetItem(index, 0).GetText()
            tank_dialog.s_volume = self.GetItem(index, 1).GetText()
            tank_dialog.s_mode = self.GetItem(index, 2).GetText()
            relay_box = tank_dialog(self.parent.c_pnl, self.parent.c_pnl.parent)
            relay_box.ShowModal()
            self.parent.c_pnl.fill_table_click("e")

        def read_tank_state(tank_name):
            return "not coded"


class tank_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(tank_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Water Tank Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Water Tank Config')
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        ## unique name
        name_label = wx.StaticText(self,  label='Unique name')
        self.name_tc = wx.TextCtrl(self, value=self.s_name, size=(200,30))
        name_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALL|wx.EXPAND, 5)
        name_sizer.Add(self.name_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## volume ml
        vol_label = wx.StaticText(self,  label='volume ml')
        self.vol_tc = wx.TextCtrl(self, value=self.s_volume)
        vol_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        vol_sizer.Add(vol_label, 0, wx.ALL|wx.EXPAND, 5)
        vol_sizer.Add(self.vol_tc, 0, wx.ALL|wx.EXPAND, 5)

        # buttons_
        self.save_btn = wx.Button(self, label='Save', size=(175, 30))
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.save_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(name_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(vol_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.Add(mode_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('wtank_help.png')

    def save_click(self, e):
        shared_data = self.parent.parent.shared_data
        n_name  = self.name_tc.GetValue()
        n_vol = self.vol_tc.GetValue()
        n_mode = "" #self.mode_combo.GetValue()
        changed = "yes"
        if self.s_name == n_name:
            if self.s_volume == n_vol:
                if self.s_mode == n_mode:
                    changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            name_start = "wtank_" + n_name
            shared_data.config_dict[name_start + "_vol"] = n_vol
            shared_data.config_dict[name_start + "_mode"] = n_mode
            #shared_data.config_dict[name_start + "_pwm"] = n_pwm

            # If name changed delete old entries
            if not n_name == self.s_name:
                name_start = "wtank_" + self.s_name
                possible_keys = [name_start + "_vol",
                                 name_start + "_mode"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()

    def OnClose(self, e):
        self.s_name  = ""
        self.s_volume = ""
        self.s_mode = ""
        self.Destroy()
