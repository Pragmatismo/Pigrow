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

        self.link_sensor_btn = wx.Button(self, label='Link Level Sensor')
        #self.link_sensor_btn.Bind(wx.EVT_BUTTON, self.link_sensor_click)

        self.link_pump_btn = wx.Button(self, label='Link Pump')
        self.link_pump_btn.Bind(wx.EVT_BUTTON, self.link_pump_click)

        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.fill_table_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.add_tank_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.link_sensor_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.link_pump_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def fill_table_click(self, e):
        self.parent.shared_data.read_pigrow_settings_file()
        i_pnl = self.parent.dict_I_pnl['watering_pnl']
        i_pnl.wtank_lst.make_table()
        i_pnl.lev_s_lst.make_table()

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

    def link_pump_click(self, e):
        pump_dialog.s_name = ""
        tank_table = self.parent.dict_I_pnl['watering_pnl'].wtank_lst
        index = tank_table.GetFocusedItem()
        if index == -1:
            pump_dialog.s_link = "no tanks to select from"
        else:
            pump_dialog.s_link = tank_table.GetItem(index, 0).GetText()
        pump_dialog.s_rate = ""
        pump_dialog.s_type = ""
        link_pump_dlb = pump_dialog(self, self.parent)
        link_pump_dlb.ShowModal()

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
        self.wtank_lst.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.wtank_select)

        tank_table_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_table_sizer.Add(tank_l, 1, wx.ALL|wx.EXPAND, 3)
        tank_table_sizer.Add(self.wtank_lst, 0, wx.ALL|wx.EXPAND, 3)

        # Selected Tank Info Sizer
        swtinfo_title =  wx.StaticText(self,  label='Selected Water Tank Sensor and Info:')
        self.lev_s_lst = self.level_sensor_list(self, 1)
    #    self.lev_s_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.level_sensor_list.doubleclick)
        self.swtinfo_sizer = wx.BoxSizer(wx.VERTICAL)
        self.swtinfo_sizer.Add(swtinfo_title, 1, wx.ALL, 3)
        self.swtinfo_sizer.Add(self.lev_s_lst, 0, wx.ALL|wx.EXPAND, 3)

        # water pump table
        pump_l =  wx.StaticText(self,  label='Water Pumps and Pipes')
    #    pump_l.SetFont(shared_data.sub_title_font)
        self.wpump_lst = self.pump_list(self, 1)
        self.wpump_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.wpump_lst.doubleclick)
        self.wpump_lst.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.wpump_select)
        self.tt_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tt_sizer.Add(pump_l, 1, wx.ALL|wx.EXPAND, 3)
        self.tt_sizer.Add(self.wpump_lst, 0, wx.ALL|wx.EXPAND, 3)


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

        #pump timer sizer
        self.pt_sizer = wx.BoxSizer(wx.VERTICAL)

        # Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tank_table_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.swtinfo_sizer, 1, wx.ALL, 3)
        main_sizer.Add(self.tt_sizer, 1, wx.ALL, 3)
        main_sizer.Add(self.pt_sizer, 1, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(tank_size_sizer, 1, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def wtank_select(self, e):
        # make sensor table
        self.lev_s_lst.make_table()
        # make pump table
        self.wpump_lst.make_table()

    def wpump_select(self, e):
        selected_pump = self.wpump_lst.GetFocusedItem()
        if selected_pump == -1:
            print("No water pump currently selected, unable to list linked pumps")
            pump_name = "None"
        #
        pump_name = self.wpump_lst.GetItem(selected_pump, 0).GetText()
        print("Selected pump;", pump_name)
        self.fill_pumptiming_sizer(pump_name)

    def fill_pumptiming_sizer(self, pump_name):
        label = "Pump timing; " + str(pump_name)
        pumptime_l = wx.StaticText(self, label=label)
        self.pt_sizer.Clear()
        self.pt_sizer.Add(pumptime_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        # repeating cron only so far
                       #############
                      ###############
                     #################
        pump_time_rep_list = self.get_cron_pump_list(pump_name)
        for item in pump_time_rep_list:
            #pump time list each item has [index, enabled, freq_num, freq_text, cmd_args]
            index, enabled, freq_num, freq_text, cmd_args = item
            cmd_args = cmd_args.split(" ")
            for arg in cmd_args:
                if "duration" in arg:
                    duration = arg.split("=")[1]
            txt_line = "cron line" + str(index) + " watering for " + str(duration) + " seconds every " + str(freq_num) + " " + freq_text
            self.pt_sizer.Add(wx.StaticText(self, label=txt_line), 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.Layout()

    def get_cron_pump_list(self, pump_name):
        print(" Checking cron for pump timing jobs")
        script = "TESTtimed_water.py"
        key = "pump"
        cron_I = self.parent.dict_I_pnl['cron_pnl']
        repeating_list = cron_I.list_repeat_by_key(script, key, pump_name)
        return repeating_list


    class water_tank_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'Size')
            self.InsertColumn(2, 'Current ml')
            self.InsertColumn(3, 'Last Watered')
            self.InsertColumn(4, 'Enabled')
            self.InsertColumn(5, 'Type')
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
                self.SetColumnWidth(4, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(5, wx.LIST_AUTOSIZE_USEHEADER)
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(4, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(5, wx.LIST_AUTOSIZE)

        def add_to_relay_table(self, name, size, type):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(size))
            self.SetItem(0, 5, str(type))
            tank_ml, tank_last, tank_active = self.read_tank_state(name)
            self.SetItem(0, 2, str(tank_ml))
            self.SetItem(0, 3, str(tank_last))
            self.SetItem(0, 4, str(tank_active))

        def doubleclick(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            tank_dialog.s_name  = self.GetItem(index, 0).GetText()
            tank_dialog.s_volume = self.GetItem(index, 1).GetText()
            tank_dialog.s_mode = self.GetItem(index, 2).GetText()
            relay_box = tank_dialog(self.parent.c_pnl, self.parent.c_pnl.parent)
            relay_box.ShowModal()
            self.parent.c_pnl.fill_table_click("e")

        def read_tank_state(self, tank_name):
            tankstat_path = self.parent.parent.shared_data.remote_pigrow_path
            tankstat_path += "logs/tankstat_" + tank_name + ".txt"
            out, err = self.parent.parent.link_pnl.run_on_pi("cat " + tankstat_path)
            current_ml = "not found"
            last_water = "not_found"
            active = "not found"
            if "current_ml=" in out:
                lines = out.splitlines()
                for line in lines:
                    if "=" in line:
                        pos = line.find("=")
                        key = line[:pos]
                        value = line[pos+1:]
                        if key == "current_ml":
                            current_ml = value
                        if key == "last_watered":
                            last_water = value
                        if key == "active":
                            active = value
            return current_ml, last_water, active


    class level_sensor_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, size=(-1,100))
            self.InsertColumn(0, 'Button Name')
            self.InsertColumn(1, 'Position %')
            self.InsertColumn(2, 'Status')
            self.InsertColumn(3, 'Trigger On')
            self.InsertColumn(4, 'Trigger Off')
            self.autosizeme()

        def autosizeme(self):
            col_n = 4
            textsize = 50
            if self.GetItemCount() == 0:
                for i in range(0, col_n):
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetMinSize((-1, 50))
            else:
                for i in range(0,col_n):
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                height = 50 + (self.GetItemCount() * textsize)
                self.SetMinSize((-1, height))

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            level_sensor_list = []
            print(" LEVEL SENSOR LIST BEING MADE - kinda ")
            self.DeleteAllItems()

            selected_tank = self.parent.wtank_lst.GetFocusedItem()
            if not selected_tank == -1:
                tank_name = self.parent.wtank_lst.GetItem(selected_tank, 0).GetText()

                setting_name = "wtank_" + tank_name + "_levsw"
                if setting_name in config_dict:
                    s_raw = config_dict[setting_name]
                    if "," in s_raw:
                        s_raw.split(",")
                    else:
                        s_raw = [s_raw]
                    # make list of sensors
                    stls_list = []
                    for item in s_raw:
                        if ":" in s_raw:
                            name, pos = item.split(":")
                            trig_on, trig_off = self.read_switch_trigs(self, name)
                            stls_list.append([name, pos, trig_on, trig_off])

                    # add to relay table
                    for item in stls_list:
                        name, pos, trig_on, trig_off = item
                        self.add_to_relay_table(name, pos, trig_on, trig_off)

        def read_switch_trigs(self):
            return "not coded", "NOT CODED!"

        def add_to_relay_table(self, name, pos, trig_on, trig_off):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(pos))
            s_status = self.read_switch_state(name)
            self.SetItem(0, 2, str(s_status))
            self.SetItem(0, 3, str(trig_on))
            self.SetItem(0, 4, str(trig_off))

        def read_switch_state(self, name):
            return "not coded"


    class pump_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, size=(-1, 100))
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'ml per min')
            self.InsertColumn(2, 'Type')
            self.autosizeme()

        def make_table(self):
            # Get tank name
            selected_tank = self.parent.wtank_lst.GetFocusedItem()
            if not selected_tank == -1:
                tank_name = self.parent.wtank_lst.GetItem(selected_tank, 0).GetText()
            else:
                print("No water tank currently selected, unable to list linked pumps")
                return None
            #

            wpump_list = []
            print("  - Using config_dict to fill pump table")
            self.DeleteAllItems()
            # Get list of linked pumps
            config_dict = self.parent.parent.shared_data.config_dict
            # pumps are linked in config using; wtank_TANKNAME_pumps=pump1, pump2
            lp_key = "wtank_" + tank_name + "_pumps"
            if lp_key in config_dict:
                linked_pumps = config_dict[lp_key].split(',')
            else:
                linked_pumps = []
            for pump in linked_pumps:
                pump = pump.strip()
                rate, type = self.read_wpump_conf(pump, config_dict, "pump_")
                self.add_to_pump_table(pump, rate, type)

        def read_wpump_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["_mlps",
                          "_type"]
            info = []
            for field in field_list:
                field_key = prefix + item_name + field
                if field_key in config_dict:
                    info.append(config_dict[field_key])
                else:
                    info.append("")
            return info

        def autosizeme(self):
            textsize = 50
            if self.GetItemCount() == 0:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetMinSize((-1,50))
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
                height = 50 + (self.GetItemCount() * textsize)
                self.SetMinSize((-1, height))
            #self.PostSizeEventToParent()
            self.parent.Layout()

        def add_to_pump_table(self, name, rate, type):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(rate))
            self.SetItem(0, 2, str(type))

        def doubleclick(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            tank_table = self.parent.parent.dict_I_pnl['watering_pnl'].wtank_lst
            t_index = tank_table.GetFocusedItem()
            if t_index == -1:
                pump_dialog.s_link = "no tanks to select from"
            else:
                pump_dialog.s_link = tank_table.GetItem(t_index, 0).GetText()

            pump_dialog.s_name = self.GetItem(index, 0).GetText()
            pump_dialog.s_rate = self.GetItem(index, 1).GetText()
            pump_dialog.s_mode = self.GetItem(index, 2).GetText()
            pumpd_box = pump_dialog(self.parent.c_pnl, self.parent.c_pnl.parent)
            pumpd_box.ShowModal()
            self.parent.c_pnl.fill_table_click("e")



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

class pump_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(pump_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Pump Sensor Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Pump Sensor Config')
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        ## unique name
        name_label = wx.StaticText(self,  label='relay name')
        self.name_cb = wx.ComboBox(self, choices = self.list_relays(), size=(200, 40), style=wx.CB_READONLY)
        self.name_cb.SetValue(self.s_name)
        #self.name_tc = wx.TextCtrl(self, value=self.s_name, size=(200,30))
        name_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALL|wx.EXPAND, 5)
        name_sizer.Add(self.name_cb, 0, wx.ALL|wx.EXPAND, 5)

        ## linked to tank_l
        link_label = wx.StaticText(self,  label='Tank')
        self.link_cb = wx.ComboBox(self, choices = self.list_tanks(), size=(200, 40))
        self.link_cb.SetValue(self.s_link)
        link_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        link_sizer.Add(link_label, 0, wx.ALL|wx.EXPAND, 5)
        link_sizer.Add(self.link_cb, 0, wx.ALL|wx.EXPAND, 5)


        ## rate ml per min
        rate_label = wx.StaticText(self,  label='flow rate l per min')
        self.rate_tc = wx.TextCtrl(self, value=self.s_rate)
        self.cal_btn = wx.Button(self, label='Calibrate', size=(175, 30))
        self.cal_btn.Bind(wx.EVT_BUTTON, self.cal_click)
        rate_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        rate_sizer.Add(rate_label, 0, wx.ALL|wx.EXPAND, 5)
        rate_sizer.Add(self.rate_tc, 0, wx.ALL|wx.EXPAND, 5)
        rate_sizer.Add(self.cal_btn, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.Add(link_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(rate_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.Add(mode_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def cal_click(self, e):
        calibrate_water_dbox = calibrate_water_flow_rate_dialog(self, self.parent)
        calibrate_water_dbox.ShowModal()

    def list_relays(self):
        relay_table = self.parent.parent.dict_I_pnl['power_pnl'].relay_ctrl_lst
        relay_names = []
        count = relay_table.GetItemCount()
        for item in range(0, count):
            name = relay_table.GetItem(item, 0).GetText()
            relay_names.append(name)
        return relay_names


    def list_tanks(self):
        I_pnl = self.parent.parent.dict_I_pnl['watering_pnl']
        tank_table = I_pnl.wtank_lst
        tank_names = []
        count = tank_table.GetItemCount()
        for item in range(0, count):
            name = tank_table.GetItem(item, 0).GetText()
            tank_names.append(name)
        return tank_names

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('pump_help.png')

    def save_click(self, e):
        shared_data = self.parent.parent.shared_data

        n_name  = self.name_cb.GetValue()
        n_rate = self.rate_tc.GetValue()
        n_mode = "" # self.mode_combo.GetValue()
        n_tank = self.link_cb.GetValue()
        changed = "yes"
        if self.s_name == n_name:
            if self.s_rate == n_rate:
                if self.s_type == n_mode:
                    if self.s_link == n_tank:
                        changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            name_start = "pump_" + n_name
            shared_data.config_dict[name_start + "_mlps"] = n_rate
            shared_data.config_dict[name_start + "_type"] = n_mode
            #shared_data.config_dict[name_start + "_pwm"] = n_pwm

            # If name changed delete old entries
            if not n_name == self.s_name and not self.s_name == "":
                name_start = "pump_" + self.s_name
                possible_keys = [name_start + "_mlps",
                                 name_start + "_type"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]
                # changing the name in  tank link config text
                self.update_tanklink_name(n_name, n_tank)

            # when name not changed but link has
            else:
                self.update_tanklink_name(n_name, n_tank)

            # save config to pi
            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()

    def update_tanklink_name(self, n_name, n_tank):
        shared_data = self.parent.parent.shared_data
        if not n_tank == "":
            # set the wtank_TANKNAME(new tank)_pumps list for the new tank and name
            # if the tank we're linking to already has a pumps list in conf
            n_tank_key = "wtank_" + n_tank + "_pumps"
            if n_tank_key in shared_data.config_dict:
                link_text = shared_data.config_dict[n_tank_key]
                # if old in the config line replace with the new name, if not add it
                if self.s_name in link_text and not self.s_name == "":
                    link_text.replace(self.s_name, n_name)
                    print(self.s_name, link_text, n_tank_key)
                else:
                    if len(link_text) > 0:
                        link_text += "," + n_name
                    else:
                        link_text = n_name
           # if new tank has no list
            else:
                link_text = n_name
            shared_data.config_dict[n_tank_key] = link_text
            # remove from old pump list if changing from established set up
            o_tank_key = "wtank_" + self.s_link + "_pumps"
            if not o_tank_key == n_tank_key:
                if o_tank_key in shared_data.config_dict:
                    o_pump_txt = shared_data.config_dict[o_tank_key]
                    if self.s_name in o_pump_txt:
                        o_pump_list = o_pump_txt.split(",")
                        o_pump_list.remove(self.s_name)
                        no_pump_txt = ""
                        for item in o_pump_list:
                            no_pump_txt += "," + item
                        shared_data.config_dict[o_tank_key] = no_pump_txt[1:]


    def OnClose(self, e):
        self.Destroy()

class calibrate_water_flow_rate_dialog(wx.Dialog):
    #Dialog box for creating for adding or editing water flowrate config data
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(calibrate_water_flow_rate_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((450, 300))
        self.SetTitle("Calibrate Water Flow Rate")
    def InitUI(self):
        shared_data = self.parent.parent.parent.shared_data
        # draw the pannel and text
        pnl = wx.Panel(self)
        title_l = wx.StaticText(self,  label='Calibrate Water Flow Rate')
        title_l.SetFont(shared_data.title_font)
        msg = 'Time how long it takes to fill a measured\ncontainer to determine the flow rate of\nyour pump.'
        sub_title_l = wx.StaticText(self,  label=msg)
        sub_title_l.SetFont(shared_data.sub_title_font)
        # container size input
        self.container_size_l = wx.StaticText(self,  label='Container Size')
        self.container_size_box = wx.TextCtrl(self, size=(70,30))
        self.vol_unit_l = wx.StaticText(self,  label='Litre')
        # Running Time
        self.running_time_l = wx.StaticText(self,  label='Time Elapsed; ')
        self.running_time_value = wx.StaticText(self,  label='--')
        # ok / cancel buttons
        self.go_btn = wx.Button(self, label='Start', pos=(15, 450), size=(175, 30))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Cancel', pos=(250, 450), size=(175, 30))
    #    self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)

        flow_rate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        flow_rate_sizer.Add(self.container_size_l, 0, wx.ALL, 5)
        flow_rate_sizer.Add(self.container_size_box, 0, wx.ALL, 5)
        flow_rate_sizer.Add(self.vol_unit_l, 0, wx.ALL, 5)
        running_time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        running_time_sizer.Add(self.running_time_l, 0, wx.ALL, 5)
        running_time_sizer.Add(self.running_time_value, 0, wx.ALL, 5)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.go_btn, 0, wx.ALL, 5)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(sub_title_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(flow_rate_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(running_time_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer , 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

        # Timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)

    def update(self, event):
        self.time_count = self.time_count + 1
        self.running_time_value.SetLabel(str(self.time_count))

    def go_click(self, e):
        #
    #    water_gpio_pin = MainApp.config_ctrl_pannel.water_dbox.gpio_loc_box.GetValue()
    #    water_gpio_direction = MainApp.config_ctrl_pannel.water_dbox.gpio_direction_box.GetValue()
        #
        button_label = self.go_btn.GetLabel()
        if button_label == "Start":
            self.time_count = 0
            self.timer.Start(1000)
            self.go_btn.SetLabel("Stop")
    #        print(" Setting GPIO " + water_gpio_pin + " to " + water_gpio_direction + " ( - ON - )")
    #        self.turn_on(water_gpio_pin, water_gpio_direction)
        else:
            self.timer.Stop()
            self.go_btn.SetLabel("Start")
    #        print(" Setting GPIO " + water_gpio_pin + " to the opposite of " + water_gpio_direction + " ( - OFF - )")
    #        self.turn_off(water_gpio_pin, water_gpio_direction)
            total_time = int(self.running_time_value.GetLabel())
            container_size = int(self.container_size_box.GetValue())
            flowrate = round(container_size / total_time, 4)
            lpermin = round((flowrate*60), 2)
            print(" Total Time - " + str(total_time) + " seconds to fill a " + str(container_size) + " litre container")
            print(" Flowrate of " + str(flowrate) + " litres per second, or " + str(lpermin) + ' litres per min')
            msg = "Set the flow rate to " + str(lpermin) + " litres per minute"
            mbox = wx.MessageDialog(None, msg, "Set flow rate?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                self.parent.rate_tc.SetValue(str(lpermin))
                self.Destroy()
