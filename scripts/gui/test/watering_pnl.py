import os
import wx
import wx.lib.scrolledpanel as scrolled
import make_water_display


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
        self.link_sensor_btn.Bind(wx.EVT_BUTTON, self.link_lvl_sensor_click)

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
        # set blanks for dialog box
        tank_dialog.s_name = ""
        tank_dialog.s_volume = ""
        tank_dialog.s_mode = ""
        # call dialog box
        add_dlb = tank_dialog(self, self.parent)
        add_dlb.ShowModal()
        # fill table
        self.fill_table_click("e")

    def link_lvl_sensor_click(self, e):
        # call dialog box
        lvl_sensor_dlb = lvl_sensor_dialog(self, self.parent)
        lvl_sensor_dlb.ShowModal()


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
        # call dialog
        link_pump_dlb = pump_dialog(self, self.parent)
        link_pump_dlb.ShowModal()
        # refresh waterpump table
        self.parent.dict_I_pnl['watering_pnl'].wtank_lst.make_table()

    def connect_to_pigrow(self):
        '''
        This is called every time a connection to a pigrow is made
        '''
        # Set values from config for set
        #if '---setting name goes here------' in shared_data.gui_set_dict:
        #self.tank_size_tc.SetValue(shared_data.gui_set_dict['---setting name goes here------'])
        pass

class info_pnl(scrolled.ScrolledPanel):
    #
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['watering_pnl']
        w = 1000
        wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        # Tab Title
        self.SetFont(shared_data.title_font)
        title_l = wx.StaticText(self,  label='Watering Control Panel')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Self Watering System Control')

        # water tank table
        self.SetFont(shared_data.item_title_font)
        tank_l =  wx.StaticText(self,  label='Water Tank')
        self.wtank_lst = self.water_tank_list(self, 1)
        self.wtank_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.wtank_lst.doubleclick)
        self.wtank_lst.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.wtank_select)
        self.del_tank_btn = wx.Button(self, label='Delete Tank')
        self.del_tank_btn.Bind(wx.EVT_BUTTON, self.del_tank_click)
        self.full_tank_btn = wx.Button(self, label='Set Tank Full')
        self.full_tank_btn.Bind(wx.EVT_BUTTON, self.full_tank_click)
        self.enable_tank_btn = wx.Button(self, label='Enable Tank')
        self.enable_tank_btn.Bind(wx.EVT_BUTTON, self.enable_tank_click)

        tank_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tank_but_sizer.Add(self.del_tank_btn, 1, wx.LEFT, 50)
        tank_but_sizer.Add(self.full_tank_btn, 1, wx.LEFT, 50)
        tank_but_sizer.Add(self.enable_tank_btn, 1, wx.LEFT, 50)

        tank_table_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_table_sizer.Add(tank_l, 1, wx.LEFT, 50)
        tank_table_sizer.Add(self.wtank_lst, 0, wx.ALL, 3)
        tank_table_sizer.Add(tank_but_sizer, 0, wx.ALL, 3)

        # Selected Tank Info Sizer
        self.SetFont(shared_data.sub_title_font)
        swtinfo_title =  wx.StaticText(self,  label='Selected Water Tank Info:')
        self.SetFont(shared_data.item_title_font)
        linked_s_title =  wx.StaticText(self,  label='Linked level sensors')
        self.lev_s_lst = self.level_sensor_list(self, 1)
    #    self.lev_s_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.level_sensor_list.doubleclick)
        self.swtinfo_sizer = wx.BoxSizer(wx.VERTICAL)
        self.swtinfo_sizer.Add(swtinfo_title, 0, wx.ALL, 3)
        self.swtinfo_sizer.Add(linked_s_title, 0, wx.LEFT, 50)
        self.swtinfo_sizer.Add(self.lev_s_lst, 0, wx.ALL, 3)

        # water pump table
        pump_l =  wx.StaticText(self,  label='Water Pumps and Pipes')
        # buttons sizer
        self.del_pump_link_btn = wx.Button(self, label='Delete Link')
        self.del_pump_link_btn.Bind(wx.EVT_BUTTON, self.del_pump_link_click)
        pump_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pump_but_sizer.Add(self.del_pump_link_btn, 1, wx.LEFT, 50)
        # table
        self.wpump_lst = self.pump_list(self, 1)
        self.wpump_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.wpump_lst.doubleclick)
        self.wpump_lst.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.wpump_select)
        # table and buttons sizer
        self.tt_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tt_sizer.Add(pump_l, 0, wx.LEFT, 50)
        self.tt_sizer.Add(self.wpump_lst, 0, wx.ALL, 3)
        self.tt_sizer.Add(pump_but_sizer, 0, wx.ALL, 3)

        #pump timer sizer (filled when pump selected)
        self.pt_sizer = wx.BoxSizer(wx.VERTICAL)

        # pump pnls sizer
        self.pump_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pump_sizer.Add(self.tt_sizer, 0, wx.ALL, 3)
        self.pump_sizer.Add(self.pt_sizer, 0, wx.ALL, 3)

        # Tank Size Panel
        tank_size_title =  wx.StaticText(self,  label='Tank level past and future')
        img_w = 1000
        img_h = 800
        self.tank_pic = wx.StaticBitmap(self, -1, size=(img_w, img_h))

        tank_pic_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_pic_sizer.Add(tank_size_title, 0, wx.ALL|wx.EXPAND, 3)
        tank_pic_sizer.Add(self.tank_pic, 0, wx.ALL|wx.EXPAND, 3)

        # Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(tank_table_sizer, 0, wx.ALL, 3)
        main_sizer.Add(self.swtinfo_sizer, 0, wx.ALL, 3)
        main_sizer.Add(self.pump_sizer, 0, wx.ALL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(tank_pic_sizer, 0, wx.ALL, 3)
        main_sizer.SetItemMinSize(tank_pic_sizer, (img_w, img_h+ 50))
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)

        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(main_sizer)

    def del_pump_link_click(self, e=""):
        # get relay_name to clear from pump list
        selected_pump = self.wpump_lst.GetFocusedItem()
        if not selected_pump == -1:
            relay_name = self.wpump_lst.GetItem(selected_pump, 0).GetText()
        else:
            return None
        # get tank name for pump link field in config dict
        selected_tank = self.wtank_lst.GetFocusedItem()
        tank_name = self.wtank_lst.GetItem(selected_tank, 0).GetText()
        # remove the link
        msg = "Unlink " + relay_name  + "?"
        mbox = wx.MessageDialog(None, msg, "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if sure == wx.ID_YES:
            self.remove_from_linked_pumps(tank_name, relay_name)

            # remove pump info
            ## ask if they want to
            config_dict = self.parent.shared_data.config_dict
            mbox = wx.MessageDialog(None, "Delete pump calibration info for " + relay_name  + "?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                keys = ["pump_" + relay_name + "_mlps",
                        "pump_" + relay_name + "_type"]
                for key in keys:
                    if key in config_dict:
                        del config_dict[key]

            # save updated config
            self.parent.shared_data.update_pigrow_config_file_on_pi()
            C_pnl = self.parent.dict_C_pnl['watering_pnl']
            C_pnl.fill_table_click("e")

    def remove_from_linked_pumps(self, tank_name, to_remove):
        config_dict = self.parent.shared_data.config_dict
        pump_list_key = "wtank_" + tank_name + "_pumps"
        if pump_list_key in config_dict:
            pump_list = config_dict[pump_list_key]
            if to_remove in pump_list:
                if "," in pump_list:
                    list_list = pump_list.split(",")
                    new_p_list = ""
                    for item in list_list:
                        if not item == to_remove:
                            new_p_list += item + ","
                    new_p_list = new_p_list[:-1]
                    config_dict[pump_list_key] = new_p_list
                else:
                    del config_dict[pump_list_key]
            else:
                print("Not found in linked pumps")
                return None

    def full_tank_click(self, e=""):
        selected_tank = self.wtank_lst.GetFocusedItem()
        full_val = self.wtank_lst.GetItem(selected_tank, 1).GetText()
        if not selected_tank == -1:
            tank_name = self.wtank_lst.GetItem(selected_tank, 0).GetText()
        else:
            return None
        try:
            int(full_val)
        except:
            print(" Unable to convert level value to int, unable to continue")
            return None
        self.set_tankstat_setting(tank_name, "current_ml", full_val)

    def enable_tank_click(self, e=""):
        selected_tank = self.wtank_lst.GetFocusedItem()
        if not selected_tank == -1:
            tank_name = self.wtank_lst.GetItem(selected_tank, 0).GetText()
        else:
            return None
        self.set_tankstat_setting(tank_name, "active", "true")

    def set_tankstat_setting(self, tank_name, setting, value):
        # check tankstate file eixsts
        tankstat_path = self.parent.shared_data.remote_pigrow_path
        tankstat_path += "logs/tankstat_" + tank_name + ".txt"
        out, err = self.parent.link_pnl.run_on_pi("ls " + tankstat_path)
        if out.strip() == "":
            print(" no tank state file, creating one")
            tank_state_txt = setting + "=" + value
        else:
            out, err = self.parent.link_pnl.run_on_pi("cat " + tankstat_path)
            tank_state_txt = ""
            found = False
            for line in out.splitlines():
                if "=" in line:
                    e_pos = line.find("=")
                    key,val = line[:e_pos], line[e_pos+1:]
                    if key == setting:
                        found = True
                        if not value == val:
                            line = key + "=" + val
                tank_state_txt += line + "\n"
        if not found:
            tank_state_txt += setting + "=" + value
        cmd = 'echo "' + tank_state_txt + '" > ' + tankstat_path
        out, err = self.parent.link_pnl.run_on_pi(cmd)
        print(" Tank state file updated ", tankstat_path)
        C_pnl = self.parent.dict_C_pnl['watering_pnl']
        C_pnl.fill_table_click("e")

    def del_tank_click(self, e):
        selected_tank = self.wtank_lst.GetFocusedItem()
        if not selected_tank == -1:
            tank_name = self.wtank_lst.GetItem(selected_tank, 0).GetText()
        else:
            return None
        # confirm with user
        mbox = wx.MessageDialog(None, "Delete tank " + tank_name  + "?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if not sure == wx.ID_YES:
            print ("Delete aborted, nothing changed.")
            return None

        config_dict = self.parent.shared_data.config_dict
         # list linked pumps
        lp_key = "wtank_" + tank_name + "_pumps"
        if lp_key in config_dict:
            linked_pumps = config_dict[lp_key].split(',')
        else:
            linked_pumps = []

        # clear in config
        field_list = ["_vol",
                      "_mode",
                      "_pumps"]
        for field in field_list:
            field_key = "wtank_" + tank_name + field
            if field_key in config_dict:
                del config_dict[field_key]

        # offer to delete linked pump info or keep if moving pump
        #                  (warn moving pump physical loc may require recalibation)

        # delete linked pumps / sensors extra info
         # list pump info to remove
        field_list = ["_mlps",
                       "_type"]
        for pump_name in linked_pumps:
            # confirm with user
            mbox = wx.MessageDialog(None, "Delete pump calibration info " + pump_name  + "?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
            sure = mbox.ShowModal()
            if sure == wx.ID_YES:
                for field in field_list:
                    field_key = "pump_" + pump_name + field
                    if field_key in config_dict:
                        del config_dict[field_key]

        # save updated config
        self.parent.shared_data.update_pigrow_config_file_on_pi()
        C_pnl = self.parent.dict_C_pnl['watering_pnl']
        C_pnl.fill_table_click("e")


        # clear tank status file
        tankstat_path = self.parent.shared_data.remote_pigrow_path
        tankstat_path += "logs/tankstat_" + tank_name + ".txt"
        print(" removing from pi, " + tankstat_path)
        out, err = self.parent.link_pnl.run_on_pi("rm " + tankstat_path)

    def wtank_select(self, e):
        #
        selected_tank = self.wtank_lst.GetFocusedItem()
        if not selected_tank == -1:
            tank_name = self.wtank_lst.GetItem(selected_tank, 0).GetText()
            tank_vol = self.wtank_lst.GetItem(selected_tank, 1).GetText()
        else:
            print("No water tank currently selected, unable to list linked pumps")
            return None
        #
        # make sensor table
        self.lev_s_lst.make_table()
        # make pump table
        self.c_linked_pumps = []
        self.pt_sizer.Clear(True)
        self.wpump_lst.make_table(tank_name)
        #
        self.make_tank_graph_pic(self.c_linked_pumps, tank_name, tank_vol)
        #
        self.Layout()
        self.SetupScrolling()

    def wpump_select(self, e):
        selected_pump = self.wpump_lst.GetFocusedItem()
        if selected_pump == -1:
            print("No water pump currently selected, unable to list linked pumps")
            pump_name = "None"
        else:
            pump_name = self.wpump_lst.GetItem(selected_pump, 0).GetText()
            print("Selected pump;", pump_name)
            pump_type = self.wpump_lst.GetItem(selected_pump, 2).GetText()
            if "sensor" in pump_type:
                self.pt_sizer.Clear(True)
                txt = "\n\nMoisture sensor based watering"
                txt+= "\n not yet supported in the gui."
                print(txt)
                st = wx.StaticText(self, label=txt)
                self.pt_sizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
                self.Layout()
            else:
                self.fill_pumptiming_sizer(pump_name)

    def fill_pumptiming_sizer(self, pump_name=None):
        if pump_name == None:
            i = self.wpump_lst.GetFocusedItem()
            pump_name = self.wpump_lst.GetItem(i, 0).GetText()
        print(" Setting pump timing sizer")
        #
        self.SetFont(self.parent.shared_data.item_title_font)
        label = "\n\nPump timing; " + str(pump_name)
        pumptime_l = wx.StaticText(self, label=label)

        self.add_time_btn = wx.Button(self, label='Add pump\n timing')
        self.add_time_btn.Bind(wx.EVT_BUTTON, self.add_time_click)


        self.pt_sizer.Clear(True)
        self.pt_sizer.Add(pumptime_l, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.pt_sizer.Add(self.add_time_btn, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)
        # repeating cron
        pump_rep_list, pump_timed_list = self.get_cron_pump_list(pump_name)
        self.SetFont(self.parent.shared_data.info_font)
        for item in pump_rep_list:
            #pump time list each item has [index, enabled, freq_num, freq_text, cmd_args]
            index, enabled, freq_num, freq_text, cmd_args = item
            cmd_args = cmd_args.replace('"', "").strip()
            duration = self.get_duration(cmd_args)
            txt_line = "Watering for " + str(duration)
            txt_line += " seconds every " + str(freq_num) + " " + freq_text
            st = wx.StaticText(self, label=txt_line)
            self.pt_sizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        # timed cron
        for item in pump_timed_list:
            index, enabled, cron_time_string, cmd_args = item
            cmd_args = cmd_args.replace('"', "").strip()
            duration = self.get_duration(cmd_args)
            txt_line = "Watering for " + str(duration)
            txt_line += " seconds, cron string " + cron_time_string
            st = wx.StaticText(self, label=txt_line)
            self.pt_sizer.Add(st, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.Layout()

    def add_time_click(self, e):
        # call dialog box
        time_dlb = w_time_dialog(self, self.parent)
        time_dlb.ShowModal()
        self.fill_pumptiming_sizer()

    def make_tank_graph_pic(self, linked_pump_list, tank_name, tank_vol):
        if linked_pump_list == [''] or len(linked_pump_list) == 0:
            blankbmp = wx.Bitmap.FromRGBA(10, 10, alpha=255)
            self.tank_pic.SetBitmap(blankbmp)
            return None
        #
        link_pnl    = self.parent.link_pnl
        shared_data = self.parent.shared_data

        # Colect cron pump timings for each pump linked to the tank
        #    creates a list of pump timings for each pump
        #       [pumpname, [pump_rep_list, pump_timed-list]]
        pump_timings = []
        for pump_name in linked_pump_list:
            pump_rep_list, pump_timed_list = self.get_cron_pump_list(pump_name)
            pump_timing = [pump_name, pump_rep_list, pump_timed_list]
            pump_timings.append(pump_timing)
            print(" Sending cron info about pump;", pump_name)

        # read tank state file from the pi
        current_ml, last_water, active = self.wtank_lst.read_tank_state(tank_name)

        # download most recent switch log
        l_switch_log = os.path.join(shared_data.frompi_path, "logs/switch_log.txt")
        l_config_path = os.path.join(shared_data.frompi_path, "config/pigrow_config.txt")
        download_log = False
        if download_log == True:
            try:
                r_switch_log = shared_data.remote_pigrow_path + "logs/switch_log.txt"
                link_pnl.download_file_to_folder(r_switch_log, l_switch_log)
            except:
                print(" Unable to download most recent switch_log.txt, using stored folder" )
        # make graphic
        config_dict = self.parent.shared_data.config_dict
        graphic = make_water_display.make_display(tank_name,
                                                  tank_vol,
                                                  current_ml,
                                                  tank_active = active,
                                                  switch_log_path=l_switch_log,
                                                  config_dict = config_dict,
                                                  pump_timings = pump_timings,
                                                  days_to_show=30)
        # convert pill image to wx bitmap and show on screen
        width, height = graphic.size
        #pic = wx.BitmapFromBuffer(width, height, graphic.tobytes())
        pic = wx.Bitmap.FromBuffer(width, height, graphic.convert("RGB").tobytes())
        self.tank_pic.SetBitmap(pic)


    def get_duration(self, cmd_args):
        duration = None
        cmd_args = cmd_args.split(" ")
        for arg in cmd_args:
            if "duration" in arg:
                duration = arg.split("=")[1]
        return duration

    def get_cron_pump_list(self, pump_name):
        print(" Checking cron for pump timing jobs")
        script = "TESTtimed_water.py"
        key = "pump"
        cron_I = self.parent.dict_I_pnl['cron_pnl']
        repeating_list = cron_I.list_repeat_by_key(script, key, pump_name)
        timed_list = cron_I.list_timed_by_key(script, key, pump_name)
        return repeating_list, timed_list


    class water_tank_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, size=(800, 150), style=wx.LC_REPORT)
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
            self.autosizeme()

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
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

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
            if "=" in out:
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
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, size=(800,100))
            self.InsertColumn(0, 'Button Name')
            self.InsertColumn(1, 'Position %')
            self.InsertColumn(2, 'Status')
            self.InsertColumn(3, 'Trigger On')
            self.InsertColumn(4, 'Trigger Off')
            self.autosizeme()

        def autosizeme(self):
            col_n = self.GetColumnCount()
            if self.GetItemCount() == 0:
                for i in range(0, col_n):
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                # decrease vertical height to just show header
                self.SetMinSize((800, 50))
            else:
                for i in range(0,col_n):
                    self.check_col_size(i)
                # set vertical height
                textsize = 50
                height = 50 + (self.GetItemCount() * textsize)
                self.SetMinSize((800, height))

        def check_col_size(self, i):
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            l = self.GetColumnWidth(i)
            self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
            h = self.GetColumnWidth(i)
            if l > h:
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

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
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, size=(150, 100))
            self.InsertColumn(0, 'Relay Name')
            self.InsertColumn(1, 'ml per min')
            self.InsertColumn(2, 'Type')
            self.autosizeme()

        def make_table(self, tank_name):
            # Get tank name
            # selected_tank = self.parent.wtank_lst.GetFocusedItem()
            # if not selected_tank == -1:
            #     tank_name = self.parent.wtank_lst.GetItem(selected_tank, 0).GetText()
            # else:
            #     print("No water tank currently selected, unable to list linked pumps")
            #     return None
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
            print (" LINKED PUMPS:", linked_pumps  )
            self.parent.c_linked_pumps = linked_pumps
            # cycle through and add to table
            for pump in linked_pumps:
                pump = pump.strip()
                rate, type = self.read_wpump_conf(pump, config_dict, "pump_")
                self.add_to_pump_table(pump, rate, type)

            # set size
            self.autosizeme()
            # select first item if there is one
            if self.GetItemCount() > 0:
                if self.GetSelectedItemCount() == 0:
                    self.Select(0)
                    self.parent.wpump_select(None)
            self.parent.Layout()

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
            # set col width
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
            # set vertical
            textsize = 50
            if self.GetItemCount() == 0:
                self.SetMinSize((-1,50))
            else:
                height = 50 + (self.GetItemCount() * textsize)
                self.SetMinSize((-1, height))
            self.parent.Layout()

        def add_to_pump_table(self, name, rate, type):
            print("adding linked_pump ;", name, rate, type)
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
            pump_dialog.s_type = self.GetItem(index, 2).GetText()
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
        self.SetFont(shared_data.title_font)
        box_label = wx.StaticText(self,  label='Water Tank Config')
        self.SetFont(shared_data.info_font)
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

            # If name changed delete old entries
            if not n_name == self.s_name:
                if not self.s_name == "":
                    self.rename_tank_stat_file(self.s_name, n_name)
                    name_start = "wtank_" + self.s_name
                    possible_keys = [name_start + "_vol",
                                     name_start + "_mode"]
                    for possible_key in possible_keys:
                        if possible_key in shared_data.config_dict:
                            del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
            if self.s_name == "":
                self.create_tank_stat_file(n_name)
        self.Destroy()

    def create_tank_stat_file(self, tank_name):
        print("--  Creating new tank stat file")
        # set path for tankstate file
        tankstat_path = self.parent.parent.shared_data.remote_pigrow_path
        tankstat_path += "logs/tankstat_" + tank_name + ".txt"
        # check for existing file
        out, err = self.parent.parent.link_pnl.run_on_pi("ls " + tankstat_path)
        if out.strip() == "":
            print(" no tank state file")
        else:
            print(" tank file exists, should offer chance to overwrite")

        file_txt = "active=True"
        write_cmd = 'echo "' + file_txt + '" > ' + tankstat_path
        out, err = self.parent.parent.link_pnl.run_on_pi(write_cmd)


    def rename_tank_stat_file(self, s_name, n_name):
        print("--  Renaming tank stat file")
        rpp_path = self.parent.parent.shared_data.remote_pigrow_path
        s_path = rpp_path +"logs/tankstat_" + s_name + ".txt"
        out, err = self.parent.parent.link_pnl.run_on_pi("ls " + s_path)
        if 'No such file or directory' in out.strip():
            self.create_tank_stat_file(n_name)
        else:
            new_path = rpp_path +"logs/tankstat_" + n_name + ".txt"
            cmd = "mv " + s_path + " " + new_path
            out, err = self.parent.parent.link_pnl.run_on_pi(cmd)


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
        self.SetFont(shared_data.title_font)
        box_label = wx.StaticText(self,  label='Pump Sensor Config')
        self.SetFont(shared_data.info_font)
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

        ## type
        if ":" in self.s_type:
            s_a_type, s_l_type = self.s_type.split(":")
        else:
            s_a_type, s_l_type = "timed", "lost"
        # activation mode
        acti_txt = "How is the pump triggered?"
        acti_l = wx.StaticText(self,  label=acti_txt)
        acti_opts = ['timed', 'sensor']
        self.acti_cb = wx.ComboBox(self, choices = acti_opts)
        self.acti_cb.SetValue(s_a_type)
        acti_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        acti_sizer.Add(acti_l, 0, wx.ALL|wx.EXPAND, 5)
        acti_sizer.Add(self.acti_cb, 0, wx.ALL|wx.EXPAND, 5)
        # water level control mode
        lctrl_txt = "Does excess water\nreturn to the tank?"
        lctrl_l = wx.StaticText(self,  label=lctrl_txt)
        lctrl_opts = ['lost', 'return']
        self.lctrl_cb = wx.ComboBox(self, choices = lctrl_opts)
        self.lctrl_cb.SetValue(s_l_type)
        lctlr_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        lctlr_sizer.Add(lctrl_l, 0, wx.ALL|wx.EXPAND, 5)
        lctlr_sizer.Add(self.lctrl_cb, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.Add(acti_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(lctlr_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
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
        type_a = self.acti_cb.GetValue()
        type_lc = self.lctrl_cb.GetValue()
        n_mode = type_a + ":" + type_lc
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

class w_time_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(w_time_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Water timing job")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        self.SetFont(shared_data.title_font)
        box_label = wx.StaticText(self,  label='Water Timing Cron Job')
        self.SetFont(shared_data.info_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        # total delivered
        vol_label = wx.StaticText(self,  label='total water delivered')
        self.vol_tc = wx.TextCtrl(self, value="", size=(200,30))
        self.vol_tc.Bind(wx.EVT_TEXT, self.change_vol)
        vol_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        vol_sizer.Add(vol_label, 0, wx.ALL|wx.EXPAND, 5)
        vol_sizer.Add(self.vol_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## watering info
        I_pnl = self.parent.parent.dict_I_pnl['watering_pnl']
        index = I_pnl.wpump_lst.GetFocusedItem()
        self.pump_name = I_pnl.wpump_lst.GetItem(index, 0).GetText()
        self.flow_rate = I_pnl.wpump_lst.GetItem(index, 1).GetText()
        self.unknown_flow = False
        try:
            self.flow_rate = int(self.flow_rate)
        except:
            self.flow_rate = 1
            self.unknown_flow = True
            self.vol_tc.SetValue("Flowrate Unknown")
            self.vol_tc.Disable()
        # duration
        dur_label = wx.StaticText(self,  label='watering duration')
        self.dur_tc = wx.TextCtrl(self, value="", size=(200,30))
        self.dur_tc.Bind(wx.EVT_TEXT, self.change_dur)

        dur_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        dur_sizer.Add(dur_label, 0, wx.ALL|wx.EXPAND, 5)
        dur_sizer.Add(self.dur_tc, 0, wx.ALL|wx.EXPAND, 5)

        ## timing info


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
        main_sizer.Add(vol_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(dur_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def change_vol(self, e):
        if self.unknown_flow == True:
            return None
        vol = self.vol_tc.GetValue()
        new_dur = ""
        if not vol == "":
            try:
                new_dur = float(vol) / float(self.flow_rate)
            except:
                pass
        self.dur_tc.ChangeValue(str(new_dur))

    def change_dur(self, e):
        if self.unknown_flow == True:
            return None
        dur = self.dur_tc.GetValue()
        new_vol = ""
        if not dur == "":
            try:
                new_vol = float(dur) * float(self.flow_rate)
            except:
                pass
        self.vol_tc.ChangeValue(str(new_vol))

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('pump_cron_help.png')

    def save_click(self, e):
        duration = round(float(self.dur_tc.GetValue()), 2)
        args = 'pump="' + self.pump_name + '" duration="' + str(duration) + '"'
        print(" Args for cron job;", args)
        cron_pnl = self.parent.parent.dict_C_pnl['cron_pnl']
        # open cron dialog
        pi_path = self.parent.parent.shared_data.remote_pigrow_path + "scripts/switches/"
        cron_set_dict = {"path":pi_path,
                        "task":"TESTtimed_water.py",
                        "args":args,
                        "type":"repeating",
                        "everystr":"day",
                        "everynum":"3",
                        "min":"30",
                        "hour":"8",}
        cron_pnl.new_cron_click(set_dict=cron_set_dict)
        cron_pnl.update_cron_click()
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class lvl_sensor_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(lvl_sensor_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Water Level Sensor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        self.SetFont(shared_data.title_font)
        msg = "\n FEATURE NOT FINISHED"
        box_label = wx.StaticText(self,  label='Tank Level Sensor' + msg)
        self.SetFont(shared_data.info_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        ## unique name
        name_label = wx.StaticText(self,  label='not coded')
        self.name_tc = wx.TextCtrl(self, value="", size=(200,30))
        name_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALL|wx.EXPAND, 5)
        name_sizer.Add(self.name_tc, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('lvl_sensor_help.png')

    def save_click(self, e):
        print(" Sorry not yet doing anything")

    def OnClose(self, e):
        self.Destroy()
