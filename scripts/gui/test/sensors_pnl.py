import os
import sys
import wx
import wx.lib.scrolledpanel as scrolled

#class ctrl_pnl(wx.Panel):
    #
    #
#    def __init__( self, parent ):
#        shared_data = parent.shared_data
#        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
#        self.SetBackgroundColour((150,230,170))
#        self.l = wx.StaticText(self,  label=('Sensors'))

#    def connect_to_pigrow(self):
#        '''
#        This is called every time a connection to a pigrow is made
#        '''
#        pass

class info_pnl(scrolled.ScrolledPanel):
    #'''
    #    This deals with sensors that are listed in to Pigrows config file,
    #    the format it expects is;
    #         sensor_chirp01_type=chirp
    #         sensor_chirp01_log=/home/pi/Pigrow/logs/chirp01.txt
    #         sensor_chirp01_loc=i2c:0x31
    #         sensor_chirp01_extra=min:100,max:1000,power_gpio=20,etc:,etc:etc,etc
    #'''
    #
    def __init__( self, parent ):
        self.parent = parent
        self.c_pnl = parent.dict_C_pnl['sensors_pnl']
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        shared_data = parent.shared_data
        # Tab Title
        self.SetFont(shared_data.title_font)
        title_l = wx.StaticText(self,  label='Sensor Control Panel')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Link aditional sensors to the pigrow')
        # placing the information boxes
        # sensor table
        self.SetFont(shared_data.info_font)
        self.sensor_list = self.sensor_table(self, 1)
        self.sensor_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.sensor_list.double_click)
        self.sensor_list.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        self.sensor_list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.sensor_got_focus)
        # trigger table
        self.SetFont(shared_data.sub_title_font)
        trigger_sub_title =  wx.StaticText(self,  label='Log Triggers ')
        self.trigger_script_activity_cron =  wx.StaticText(self,  label="")
        self.trigger_script_activity_live =  wx.StaticText(self,  label="")
        self.SetFont(shared_data.info_font)
        self.trigger_list = self.trigger_table(self, 1)
        self.trigger_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.trigger_list.double_click)
        self.trigger_list.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.trigger_got_focus)
        self.trigger_list.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        # sizers
        trigger_label_sizer = wx.BoxSizer(wx.HORIZONTAL)
        trigger_label_sizer.Add(trigger_sub_title, 1, wx.ALL, 3)
        trigger_label_sizer.Add(self.trigger_script_activity_cron, 1, wx.ALL, 3)
        trigger_label_sizer.Add(self.trigger_script_activity_live, 1, wx.ALL, 3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.sensor_list, 1, wx.ALL|wx.EXPAND, 3)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(trigger_label_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.trigger_list, 1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def sensor_got_focus(self, e):
        trigger_focus = self.trigger_list.GetFocusedItem()
        self.trigger_list.Select(trigger_focus, on=0)

    def trigger_got_focus(self, e):
        sensor_focus = self.sensor_list.GetFocusedItem()
        self.sensor_list.Select(sensor_focus, on=0)


    def del_item(self, e):
        # cron_list_pnl - needs to be set before this works
        cron_list_pnl = self.parent.dict_C_pnl['cron_pnl']
        #                 also other cron stuff
        trigger_list = self.trigger_list
        config_dict  = self.parent.shared_data.config_dict
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
                mbox = wx.MessageDialog(None, "Delete selected item?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
                sure = mbox.ShowModal()
                if sure == wx.ID_YES:
                    if self.sensor_list.GetSelectedItemCount() == 1:
                        # Delete cron job
                        sensor_script = "log_sensor_module.py"
                        name = self.sensor_list.GetItem(self.sensor_list.GetFocusedItem(), 0).GetText()
                        repeat_cron = self.parent.dict_I_pnl['cron_pnl'] #.repeating_cron_list
                        repeat_cron.remove_by_name(sensor_script, name)

                        ## remove from config dict
                        logfreq = self.sensor_list.GetItem(self.sensor_list.GetFocusedItem(), 5).GetText()
                        if logfreq == "button":
                            prefix = "button"
                        else:
                            prefix = "sensor"
                        # make list of keys
                        keys = ['type', 'log', 'logtype', 'loc', 'extra', 'cmdD', 'cmdU']
                        list_of_keys = []
                        for key in keys:
                            list_of_keys.append(prefix + "_" + name + "_" + key)
                        # remove keys
                        for key in list_of_keys:
                            if key in config_dict:
                                del config_dict[key]

                        self.parent.shared_data.update_pigrow_config_file_on_pi() #ask="no")
                    if trigger_list.GetSelectedItemCount() == 1:
                        # if deleted item from trigger list remove and save file
                        print(trigger_list.DeleteItem(trigger_list.GetFocusedItem()))
                        trigger_list.save_table_to_pi()


    def check_trigger_script_activity(self):
        cron_C_pnl = self.parent.dict_C_pnl['cron_pnl']
        script = 'trigger_watcher.py'
        script_path = self.parent.shared_data.remote_pigrow_path + "scripts/autorun/trigger_watcher.py"

        # check if script in startup cron
        script_status = cron_C_pnl.check_if_script_in_startup(script)
        if script_status == "enabled":
            self.trigger_script_activity_cron.SetForegroundColour((80,150,80))
            self.trigger_script_activity_cron.SetLabel("trigger_watcher.py starting on boot")
        elif script_status == "disabled":
            self.trigger_script_activity_cron.SetForegroundColour((200,110,110))
            self.trigger_script_activity_cron.SetLabel("trigger_watcher.py cronjob disabled, won't start on boot")
        elif script_status == "none":
            self.trigger_script_activity_cron.SetForegroundColour((200,75,75))
            self.trigger_script_activity_cron.SetLabel("No trigger_watcher.py in startup cron, this is required.")

        # Check running
        is_running = cron_C_pnl.test_if_script_running(script_path, "")
        if is_running == True:
            self.trigger_script_activity_live.SetLabel(" trigger_watcher.py currently running ")
            self.trigger_script_activity_live.SetForegroundColour((80,150,80))
        else:
            self.trigger_script_activity_live.SetLabel(" trigger_watcher.py NOT currently running ")
            self.trigger_script_activity_live.SetForegroundColour((200,75,75))
        #self.Layout()


    class sensor_table(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Sensor')
            self.InsertColumn(1, 'Type')
            self.InsertColumn(2, 'Log')
            self.InsertColumn(3, 'Location')
            self.InsertColumn(4, 'Extra')
            self.InsertColumn(5, 'log freq')
            self.InsertColumn(6, 'cmdD')
            self.InsertColumn(7, 'cmdU')
            self.InsertColumn(8, 'logtype')
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

        def read_sensor_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["_type",
                          "_log",
                          "_logtype",
                          "_loc",
                          "_extra",
                          "_cmdD",
                          "_cmdU"]
            info = []
            for field in field_list:
                field_key = prefix + item_name + field
                if field_key in config_dict:
                    info.append(config_dict[field_key])
                else:
                    info.append("")

            return info

        def make_sensor_table(self):
            #self.parent.shared_data.
            config_dict = self.parent.parent.shared_data.config_dict
            sensor_name_list = []
            button_name_list = []
            print("  - Using config_dict to fill sensor table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "_type" in key:
                    if "sensor_" in key:
                        sensor_name_list.append(key.split("_")[1])
                    if "button_" in key:
                        button_name_list.append(key.split("_")[1])
            # add buttons to table
            for button_name in button_name_list:
                type, log, logtype, loc, extra, cmdD, cmdU = self.read_sensor_conf(button_name, config_dict, "button_")
                self.add_to_sensor_list(button_name, type, log, loc, extra, "button", cmdD, cmdU, logtype)
            # add sensors to table
            for sensor_name in sensor_name_list:
                type, log, logtype, loc, extra, cmdD, cmdU = self.read_sensor_conf(sensor_name, config_dict, "sensor_")
                log_freq = self.find_cron_freq(sensor_name, type, loc)
                # get settings for buttons
                self.add_to_sensor_list(sensor_name, type, log, loc, extra, log_freq)
            # resize cols
            self.autosizeme()

        def find_cron_freq(self, sensor_name, type, loc):
            '''
               check cron to see if sensor is being logged and how often
            '''
            cron_I_pnl  = self.parent.parent.dict_I_pnl['cron_pnl']
            script = "log_sensor_module.py"
            freq_num, freq_text = cron_I_pnl.time_text_from_name(script, sensor_name)
            log_freq = str(freq_num) + " " + freq_text
            return log_freq
            #
            # The prior version had special controlls for which will soon be
            # obsolete, so currently not including them here
            # "log_chirp.py", "log_ads1115.py"

        def add_to_sensor_list(self, sensor, type, log, loc, extra='', log_freq='', cmdD="", cmdU="", logtype=""):
            self.InsertItem(0, str(sensor))
            self.SetItem(0, 1, str(type))
            self.SetItem(0, 2, str(log))
            self.SetItem(0, 3, str(loc))
            self.SetItem(0, 4, str(extra))
            self.SetItem(0, 5, str(log_freq))
            self.SetItem(0, 6, str(cmdD))
            self.SetItem(0, 7, str(cmdU))
            self.SetItem(0, 8, str(logtype))

        def double_click(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            self.s_name = self.GetItem(index, 0).GetText()
            self.s_type = self.GetItem(index, 1).GetText()
            self.s_log  = self.GetItem(index, 2).GetText()
            self.s_loc  = self.GetItem(index, 3).GetText()
            self.s_extra = self.GetItem(index, 4).GetText()
            self.s_timing = self.GetItem(index, 5).GetText()
            self.s_cmdD = self.GetItem(index, 6).GetText()
            self.s_cmdU = self.GetItem(index, 7).GetText()
            self.s_logtype = self.GetItem(index, 8).GetText()
            #
            if self.s_timing == "button":
                add_button = button_dialog(self, self.parent)
                add_button.ShowModal()
            else:
                # old style sensors
                if self.s_type == 'chirp':
                    print(" Chirp dialog not written, switch to chirpM in modular sensors")
                    #edit_chirp_dbox = chirp_dialog(None)
                    #edit_chirp_dbox.ShowModal()
                elif self.s_type == "ADS1115":
                    print(" ADS1115 dialog not written")
                    #ads1115_dialog_box = ads1115_dialog(None)
                    #ads1115_dialog_box.ShowModal()
                # modular sensors
                else:
                    modular_sensor_dialog_box = sensor_from_module_dialog(self, self.parent)
                    modular_sensor_dialog_box.ShowModal()
                    self.make_sensor_table()


    class trigger_table(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT|wx.LC_VRULES)
            self.InsertColumn(0, 'Log')
            self.InsertColumn(1, 'Value Label')
            self.InsertColumn(2, 'Type')
            self.InsertColumn(3, 'Value')
            self.InsertColumn(4, 'Condition Name')
            self.InsertColumn(5, 'Set')
            self.InsertColumn(6, 'lock (min)')
            self.InsertColumn(7, 'Shell Command')
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

        def make_trigger_table(self):
            self.DeleteAllItems()
            print("  - Filling Trigger Table - ")
            trig_path = self.parent.parent.shared_data.remote_pigrow_path + "config/trigger_events.txt"
            out, error = self.parent.parent.link_pnl.run_on_pi("cat " + trig_path)
            for line in out.splitlines():
                first_comma = line.find(",")
                second_comma  = first_comma + 1 + line[first_comma+1:].find(",")
                third_comma   = second_comma + 1 + line[second_comma+1:].find(",")
                fourth_comma  = third_comma + 1 + line[third_comma+1:].find(",")
                fifth_comma   = fourth_comma + 1 + line[fourth_comma+1:].find(",")
                sixth_comma   = fifth_comma + 1 + line[fifth_comma+1:].find(",")
                seventh_comma = sixth_comma + 1 + line[sixth_comma+1:].find(",")
                eighth_comma = seventh_comma + 1 + line[seventh_comma+1:].find(",")
                # find values between commas
                log_name        = line[:first_comma].strip()
                value_label     = line[first_comma  +1 :second_comma].strip()
                trigger_type    = line[second_comma +1 :third_comma].strip()
                trigger_value   = line[third_comma  +1 :fourth_comma].strip()
                condition_name  = line[fourth_comma +1 :fifth_comma].strip()
                trig_direction  = line[fifth_comma  +1 :sixth_comma].strip()
                trig_cooldown   = line[sixth_comma  +1 :seventh_comma].strip()
                cmd            = line[seventh_comma+1:].strip()
                self.add_to_trigger_list(log_name, value_label, trigger_type, trigger_value, condition_name, trig_direction, trig_cooldown, cmd)
            # resize
            self.autosizeme()

        def add_to_trigger_list(self, log, label, type, value, name, set, cooldown, cmd):
            self.InsertItem(0, str(log))
            self.SetItem(0, 1, str(label))
            self.SetItem(0, 2, str(type))
            self.SetItem(0, 3, str(value))
            self.SetItem(0, 4, str(name))
            self.SetItem(0, 5, str(set))
            self.SetItem(0, 6, str(cooldown))
            self.SetItem(0, 7, str(cmd))

        def update_table_line(self, index, log, label, type, value, name, set, cooldown, cmd):
            self.SetItem(index, 0, str(log))
            self.SetItem(index, 1, str(label))
            self.SetItem(index, 2, str(type))
            self.SetItem(index, 3, str(value))
            self.SetItem(index, 4, str(name))
            self.SetItem(index, 5, str(set))
            self.SetItem(index, 6, str(cooldown))
            self.SetItem(index, 7, str(cmd))

        def save_table_to_pi(self):
            trigger_file_text = ""

            for index in range(0, self.parent.trigger_list.GetItemCount()):
                log      = self.GetItem(index,0).GetText()
                label    = self.GetItem(index,1).GetText()
                type     = self.GetItem(index,2).GetText()
                value    = self.GetItem(index,3).GetText()
                name     = self.GetItem(index,4).GetText()
                set      = self.GetItem(index,5).GetText()
                cooldown = self.GetItem(index,6).GetText()
                cmd      = self.GetItem(index,7).GetText()
                trigger_file_text += log + "," + label + "," + type + "," + value + "," + name + "," + set + "," + cooldown + "," + cmd + "\n"
            # remove trailing line from file
            if len(trigger_file_text) > 1:
                if trigger_file_text[0:-2] == "\n":
                    trigger_file_text = trigger_file_text[0:-2]

            # back up current trigger events file
            remote_pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
            pi_trigger_events_file = remote_pigrow_path + "config/trigger_events.txt"
            backup_events_file     = remote_pigrow_path + "config/trigger_events_prev.txt"
            cmd = "mv " + pi_trigger_events_file + " " + backup_events_file
            out, error = self.parent.parent.link_pnl.run_on_pi(cmd)

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

        def double_click(self, e):
            print(self, e)
            index =  e.GetIndex()
            print(index)
            self.initial_log       = self.GetItem(index, 0).GetText()
            self.initial_val_label = self.GetItem(index, 1).GetText()
            self.initial_type      = self.GetItem(index, 2).GetText()
            self.initial_value     = self.GetItem(index, 3).GetText()
            self.initial_cond_name = self.GetItem(index, 4).GetText()
            self.initial_set       = self.GetItem(index, 5).GetText()
            self.initial_lock      = self.GetItem(index, 6).GetText()
            self.initial_cmd       = self.GetItem(index, 7).GetText()
            self.initial_index = index
            trigger_edit_box = set_trigger_dialog(self, self.parent)
            trigger_edit_box.ShowModal()

class ctrl_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        #self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        # Refresh page button
        self.make_table_btn = wx.Button(self, label='make table')
        self.make_table_btn.Bind(wx.EVT_BUTTON, self.make_tables_click)
        # Soil Moisture Controls
        #    --  Chirp options
        self.chirp_l = wx.StaticText(self,  label='Chirp Soil Moisture Sensor;')
        #self.config_chirp_btn = wx.Button(self, label='add new chirp')
        #self.config_chirp_btn.Bind(wx.EVT_BUTTON, self.add_new_chirp_click)
        self.address_chirp_btn = wx.Button(self, label='change chirp address')
        self.address_chirp_btn.Bind(wx.EVT_BUTTON, self.address_chirp_click)
        #   == ADS1115 Analog to Digital converter i2c_check
        #self.ads1115_l = wx.StaticText(self,  label='ADS1115 ADC;')
        #self.add_ads1115 = wx.Button(self, label='add new ADS1115')
        #self.add_ads1115.Bind(wx.EVT_BUTTON, self.add_ads1115_click)
        #  == Modular Sensor Controlls
        self.modular_sensor_l = wx.StaticText(self,  label='Modular Sensors;')
        self.sensor_module_list_cb = wx.ComboBox(self,  size=(150, 30), choices = self.parent.shared_data.get_module_options("sensor_", "sensor_modules"))
        self.add_modular_sensor = wx.Button(self, label='Add')
        self.add_modular_sensor.Bind(wx.EVT_BUTTON, self.add_modular_sensor_click)
        #  == Button Controlls
        self.buttons_l = wx.StaticText(self,  label='Buttons;')
        self.add_button = wx.Button(self, label='Add')
        self.add_button.Bind(wx.EVT_BUTTON, self.add_button_click)
        #  == Add Trigger
        self.triggers_l = wx.StaticText(self,  label='Triggers;')
        self.add_trigger = wx.Button(self, label='Add')
        self.add_trigger.Bind(wx.EVT_BUTTON, self.add_trigger_click)

        # Sizers

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.make_table_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.modular_sensor_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.sensor_module_list_cb, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_modular_sensor, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.Add(self.ads1115_l, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(self.add_ads1115, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.buttons_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_button, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.triggers_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.add_trigger, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.chirp_l, 0, wx.ALL|wx.EXPAND, 3)
        #main_sizer.Add(self.config_chirp_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.address_chirp_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def updated_config(self):
        self.make_tables_click("e")

    def make_tables_click(self, e):
        self.parent.shared_data.read_pigrow_settings_file()
        i_pnl = self.parent.dict_I_pnl['sensors_pnl']
        i_pnl.sensor_list.make_sensor_table()
        i_pnl.trigger_list.make_trigger_table()
        i_pnl.check_trigger_script_activity()

    def add_modular_sensor_click(self, e):
        i_pnl = self.parent.dict_I_pnl['sensors_pnl']
        self.make_tables_click("e")
        # set blanks for dialog box
        module_name = self.sensor_module_list_cb.GetValue()
        if module_name == "":
            return None
        i_pnl.sensor_list.s_type = module_name
        i_pnl.sensor_list.s_name = ""
        log_path = self.parent.shared_data.remote_pigrow_path + "logs/" +  module_name + "_log.txt"
        i_pnl.sensor_list.s_log = log_path
        i_pnl.sensor_list.s_loc = ""
        i_pnl.sensor_list.s_extra = ""
        i_pnl.sensor_list.s_timing = ""
        # call dialog box
        add_module_sensor = sensor_from_module_dialog(i_pnl.sensor_list, i_pnl.sensor_list.parent)
        add_module_sensor.ShowModal()
        self.make_sensor_table()

    def add_button_click(self, e):
        i_pnl = self.parent.dict_I_pnl['sensors_pnl']
        # load config from file and fill tables so there are no conflicts
        self.make_tables_click("e")
        # set blanks for dialog box
        module_name = self.sensor_module_list_cb.GetValue()
        i_pnl.sensor_list.s_type = ""
        i_pnl.sensor_list.s_name = ""
        i_pnl.sensor_list.s_log = ""
        i_pnl.sensor_list.s_logtype = ""
        i_pnl.sensor_list.s_loc = ""
        i_pnl.sensor_list.s_extra = ""
        i_pnl.sensor_list.s_timing = ""
        i_pnl.sensor_list.s_cmdD = ""
        i_pnl.sensor_list.s_cmdU = ""
        # call dialog box
        add_button = button_dialog(i_pnl.sensor_list, i_pnl.sensor_list.parent)
        add_button.ShowModal()


    # def add_ads1115_click(self, e):
    #     MainApp.sensors_ctrl_pannel.make_tables_click("e")
    #     # set blanks for dialog box
    #     MainApp.sensors_info_pannel.sensor_list.s_name = ""
    #     log_path = ""
    #     if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
    #         log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"] + "ads1115_log.txt"
    #     MainApp.sensors_info_pannel.sensor_list.s_log = log_path
    #     MainApp.sensors_info_pannel.sensor_list.s_loc = ""
    #     MainApp.sensors_info_pannel.sensor_list.s_extra = ""
    #     MainApp.sensors_info_pannel.sensor_list.s_timing = ""
    #     # call dialog box
    #     add_ads1115 = ads1115_dialog(None)
    #     add_ads1115.ShowModal()
    #
    # def add_new_chirp_click(self, e):
    #     MainApp.sensors_ctrl_pannel.make_tables_click("e")
    #     print("adding a new chirp sensor")
    #     # set black variables
    #     MainApp.sensors_info_pannel.sensor_list.s_name = ""
    #     log_path = ""
    #     if 'log_path' in MainApp.config_ctrl_pannel.dirlocs_dict:
    #         log_path = MainApp.config_ctrl_pannel.dirlocs_dict["log_path"]
    #     MainApp.sensors_info_pannel.sensor_list.s_log = log_path
    #     MainApp.sensors_info_pannel.sensor_list.s_loc = ":"
    #     MainApp.sensors_info_pannel.sensor_list.s_extra = "min: max:"
    #     MainApp.sensors_info_pannel.sensor_list.s_timing = ""
    #     # call the chirp config dialog box
    #     add_chirp_dbox = chirp_dialog(None, title='Chirp Sensor Config')
    #     add_chirp_dbox.ShowModal()

    def address_chirp_click(self, e):
        # Ask user to select the chirp they want to readdress
        msg_text =  "This will change the address of your Chirp on the i2c bus, \n"
        msg_text += "please input the current address of the sensor you wish you change. \n"
        msg_text += "You must use the format 0x** - e.g. 0x20, 0x21, etc. \n\n"
        msg_text += "If your sensor is plugged in correctly but doesn't show on the i2c bus \n"
        msg_text += "it's likely to be at 0x01 or possibly 0x00 or 0x02. \n"
        current_add_dbox = wx.TextEntryDialog(self, msg_text, 'Change i2c address', "")
        if current_add_dbox.ShowModal() == wx.ID_OK:
            current_chirp_add = current_add_dbox.GetValue()
        else:
            return "cancelled"
        current_add_dbox.Destroy()
        # ask which address the user wants to change it to
        msg_text = "Input new address to set chirp sensor to\n"
        msg_text += "You must use the format 0x20, 0x21, etc."
        new_add_dbox = wx.TextEntryDialog(self, msg_text, 'Change i2c address', "")
        if new_add_dbox.ShowModal() == wx.ID_OK:
            new_chirp_add = new_add_dbox.GetValue()
        else:
            return "cancelled"
        new_add_dbox.Destroy()

        path = self.parent.shared_data.remote_pigrow_path
        cmd = os.path.join(path, "scripts/sensors/chirp_i2c_address.py")
        out, error = self.parent.link_pnl.run_on_pi(cmd + " current=" + current_chirp_add + " new=" + new_chirp_add)
        # tell the uesr what happened
        msg_text = "Script output; " + str(out) + " " + str(error)
        dbox = self.parent.shared_data.scroll_text_dialog(None, msg_text, "chirp_i2c_address.py output", cancel=False)
        dbox.ShowModal()
        dbox.Destroy()

    def sensor_combo_go(self, e):
        # hide all controls
        self.soil_sensor_cb.Hide()
        # show selected controls
        if self.sensor_cb.GetValue() == "Soil Moisture":
            self.soil_sensor_cb.Hide()

    def add_trigger_click(self, e):
        i_pnl = self.parent.dict_I_pnl['sensors_pnl']
        trigger_list = i_pnl.trigger_list
        self.make_tables_click("e")
        trigger_list.initial_log = ""
        trigger_list.initial_val_label = ""
        trigger_list.initial_type = ""
        trigger_list.initial_value = ""
        trigger_list.initial_cond_name = ""
        trigger_list.initial_set = ""
        trigger_list.initial_lock = ""
        trigger_list.initial_cmd = ""
        trigger_list.initial_index = -1
        trigger_edit_box = set_trigger_dialog(trigger_list, trigger_list.parent)
        trigger_edit_box.ShowModal()

    def run_test_cmd(self, cmd):
        shared_data = self.parent.shared_data
        # ask user if they're sure they want to run the script
        q_text = "Are you sure you want to run the command; "
        q_text += cmd
        q_text += "\n\n Note: You will not be able to do anything until the script has finished running."
        dbox = wx.MessageDialog(self, q_text, "Run on pi?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        if not answer == wx.ID_OK:
            return None

        # run the script
        out, error = self.parent.link_pnl.run_on_pi(cmd)
        # make output for user
        out = out.strip()
        error = error.strip()
        txt = ""
        if not out == "":
            txt = "output:\n" + out + "\n\n"
        if not error == "":
            txt += "error:\n" + out
        if out == "" and error == "":
            txt = "Script finished without output"
        # show the user the output
        dbox = shared_data.scroll_text_dialog(None, txt, "cmd response from pi", cancel=False, readonly=True)
        dbox.ShowModal()
        dbox.Destroy()

    def select_file(self, text_control, default_path=""):
        set_path = text_control.GetValue()
        if default_path == "":
            default_path = self.parent.shared_data.remote_pigrow_path
        if set_path == "":
            set_path = default_path
        self.parent.link_pnl.select_files_on_pi(create_file=True, default_path=set_path)
        selected_files = self.parent.link_pnl.selected_files
        selected_folders = self.parent.link_pnl.selected_folders
        if len(selected_files) == 0 and len(selected_folders) == 0:
            return None
        else:
            text_control.SetValue(selected_files[0])



class set_trigger_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(set_trigger_dialog, self).__init__(*args, **kw)
        print(" INITing UI....")
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Sensor Setup from Module")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.parent.shared_data
        trigger_list = self.parent.parent.trigger_list
        '''
        Before this is called these values must be set;
        trigger_list.initial_log
        trigger_list.initial_val_label
        trigger_list.initial_type
        trigger_list.initial_value
        trigger_list.initial_cond_name
        trigger_list.initial_set
        trigger_list.initial_lock
        trigger_list.initial_cmd
        trigger_list.initial_index = -1 for new, index number of trigger table otherwise
        '''
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Log Triggers')
        box_label.SetFont(shared_data.title_font)
        box_sub_title =  wx.StaticText(self,  label='Trigger conditions are checked every time a log entry is written', size=(550,30))
        box_sub_title.SetFont(shared_data.sub_title_font)
        # buttons_
        self.ok_btn = wx.Button(self, label='OK', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # trigger information
        log_l = wx.StaticText(self,  label='Log')
        log_opts = self.get_log_options()
        self.log_cb = wx.ComboBox(self, choices = log_opts, value=trigger_list.initial_log)
        self.log_cb.Bind(wx.EVT_COMBOBOX, self.set_label_opts)

        val_label_l = wx.StaticText(self,  label='Value Label')
        val_label_opts = self.get_value_label_ops()
        self.val_label_cb = wx.ComboBox(self, choices = val_label_opts, value=trigger_list.initial_val_label)
        type_l = wx.StaticText(self,  label='Type')
        type_opts = ['above', 'below', 'window', 'frame', 'all']
        self.type_cb = wx.ComboBox(self, choices = type_opts, value=trigger_list.initial_type)
        self.type_cb.Bind(wx.EVT_COMBOBOX, self.type_cb_select)

        value_l = wx.StaticText(self,  label='value')
        self.value_tc = wx.TextCtrl(self, value=trigger_list.initial_value, size=(400,30))

        cond_name_l = wx.StaticText(self,  label='Condition Name')
        self.cond_name_tc = wx.TextCtrl(self, value=trigger_list.initial_cond_name, size=(400,30))

        set_l = wx.StaticText(self,  label='Set to')
        set_opts = ['on', 'off', 'pause']
        self.set_cb = wx.ComboBox(self, choices = set_opts, value=trigger_list.initial_set)

        lock_l = wx.StaticText(self,  label='Cooldown Lock')
        self.lock_tc = wx.TextCtrl(self, value=trigger_list.initial_lock, size=(400,30))

        # shell comand
        cmd_l = wx.StaticText(self,  label='Shell Command')
        self.cmd_tc = wx.TextCtrl(self, value=trigger_list.initial_cmd, size=(500,30))
        self.find_cmd_btn = wx.Button(self, label='...', size=(50, 30))
        self.find_cmd_btn.Bind(wx.EVT_BUTTON, self.find_cmd_click)

        self.test_cmd_btn = wx.Button(self, label='Test', size=(100, 30))
        self.test_cmd_btn.Bind(wx.EVT_BUTTON, self.testcmd)


        # Read trigger conditions
        triggger_cond_l = wx.StaticText(self,  label='Current Trigger Condition;', size=(550,30))
        self.read_trig_cond_btn = wx.Button(self, label='Read Current Trigger Conditions')
        self.read_trig_cond_btn.Bind(wx.EVT_BUTTON, self.read_trigger_conditions_click)
        self.read_output_l = wx.StaticText(self,  label='')

        # Mirror
        if trigger_list.initial_index == -1:
            mirror_label = "Create Mirror"
        else:
            mirror_label = "Change Mirror"
        self.mirror_l = wx.CheckBox(self,  label=mirror_label)

        trig_options_sizer = wx.GridBagSizer(8, 4)
        trig_options_sizer.AddMany([
            (log_l, (0, 0), (1, 1), wx.EXPAND),
            (self.log_cb, (0, 1), (1, 1), wx.EXPAND),
            (val_label_l, (1, 0), (1, 1), wx.EXPAND),
            (self.val_label_cb, (1, 1), (1, 1), wx.EXPAND),
            (type_l, (2, 0), (1, 1), wx.EXPAND),
            (self.type_cb, (2, 1), (1, 1), wx.EXPAND),
            (value_l, (3, 0), (1, 1), wx.EXPAND),
            (self.value_tc, (3, 1), (1, 1), wx.EXPAND),
            (cond_name_l, (4, 0), (1, 1), wx.EXPAND),
            (self.cond_name_tc, (4, 1), (1, 1), wx.EXPAND),
            (set_l, (5, 0), (1, 1), wx.EXPAND),
            (self.set_cb, (5, 1), (1, 1), wx.EXPAND),
            (lock_l, (6, 0), (1, 1), wx.EXPAND),
            (self.lock_tc, (6, 1), (1, 1), wx.EXPAND),
            (cmd_l, (7, 0), (1, 1), wx.EXPAND),
            (self.cmd_tc, (7, 1), (1, 1), wx.EXPAND),
            (self.find_cmd_btn, (7, 2), (1, 1), wx.EXPAND),
            (self.test_cmd_btn, (7, 3), (1, 1), wx.EXPAND)
        ])

        trigger_conditions_sizer = wx.BoxSizer(wx.VERTICAL)
        trigger_conditions_sizer.Add(triggger_cond_l, 0, wx.EXPAND, 3)
        trigger_conditions_sizer.Add(self.read_trig_cond_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        trigger_conditions_sizer.Add(self.read_output_l, 0, wx.EXPAND, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(box_sub_title, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(trig_options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(trigger_conditions_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.mirror_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        if not trigger_list.initial_type == "above" and not trigger_list.initial_type == "below":
            self.mirror_l.Hide()
        if not self.find_mirror() > -1:
            self.mirror_l.SetLabel("Create Mirror")
        else:
            self.mirror_l.SetForegroundColour((75,190,75))
            self.mirror_l.SetValue(True)

    def find_cmd_click(self, e=""):
        shared_data = self.parent.parent.parent.shared_data
        scripts_path = shared_data.remote_pigrow_path + "scripts/"
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.select_file(self.cmd_tc, scripts_path)


    def testcmd(self, e=""):
        cmd = self.cmd_tc.GetValue()
        if not cmd == "":
            c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
            c_pnl.run_test_cmd(cmd)


    def find_mirror(self):
        print(" looking for mirror")
        trigger_list = self.parent.parent.trigger_list
        mirror_trigger_index = -1
        for index in range(0, trigger_list.GetItemCount()):
            if not index == trigger_list.initial_index:
                log      = trigger_list.GetItem(index,0).GetText()
                label    = trigger_list.GetItem(index,1).GetText()
                value    = trigger_list.GetItem(index,3).GetText()
                name     = trigger_list.GetItem(index,4).GetText()
                if trigger_list.initial_log == log:
                    if trigger_list.initial_val_label == label:
                        if trigger_list.initial_value == value:
                            if trigger_list.initial_cond_name == name:
                                mirror_trigger_index = index
        return mirror_trigger_index

    def create_mirror(self, log, label, type, value, name, set, cooldown, cmd):
        trigger_list = self.parent.parent.trigger_list
        # flip set direction
        if set == "on":
            set = "off"
        elif set == "off":
            set = "on"
        # flip relay command if it's a relay command or similar
        if "_on.py" in cmd:
            cmd = cmd.replace("_on.py", "_off.py")
        elif "_off.py" in cmd:
            cmd = cmd.replace("_off.py", "_on.py")
        # flip type direction
        if type == "above":
            trigger_list.add_to_trigger_list(log, label, "below", value, name, set, cooldown, cmd)
        elif type == "below":
            trigger_list.add_to_trigger_list(log, label, "above", value, name, set, cooldown, cmd)

    def change_mirror(self, mirror_index, log, label, value, name):
        trigger_list = self.parent.parent.trigger_list
        trigger_list.SetItem(mirror_index,0, log)
        trigger_list.SetItem(mirror_index,1, label)
        trigger_list.SetItem(mirror_index,3, value)
        trigger_list.SetItem(mirror_index,4, name)

    def get_log_options(self):
        sensor_list = self.parent.parent.sensor_list
        link_pnl = self.parent.parent.parent.link_pnl
        shared_data = self.parent.parent.parent.shared_data
        log_list = []
        # logs listen in sensor table
        for index in range(0, sensor_list.GetItemCount()):
            log = sensor_list.GetItem(index, 2).GetText()
            if "/logs/" in log:
                log = log.split('/logs/')[1]
            if not log in log_list:
                log_list.append(log)
        # logs on the pigrow
        log_path = shared_data.remote_pigrow_path + "logs/"
        out, error = link_pnl.run_on_pi("ls -1 " + log_path)
        logs = out.splitlines()
        for log in logs:
            if not log in log_list:
                log_list.append(log)
        # return list of all logs
        return log_list

    def set_label_opts(self, e=""):
        opts=self.get_value_label_ops()
        self.val_label_cb.Clear()
        self.val_label_cb.Append(opts)

    def get_value_label_ops(self):
        shared_data = self.parent.parent.parent.shared_data
        link_pnl = self.parent.parent.parent.link_pnl
        log_name = self.log_cb.GetValue().strip()
        label_opts = []
        if log_name == "":
            return []
        log_path = shared_data.remote_pigrow_path + "logs/" + log_name
        cmd = "tail -1 " + log_path
        out, error = link_pnl.run_on_pi(cmd)
        if ">" in out:
            items = out.split(">")
            for item in items:
                if "=" in item:
                    label_opts.append(item.split("=")[0])
        return label_opts

    def type_cb_select(self, e):
        type = self.type_cb.GetValue()
        if type == "all":
            self.value_tc.Disable()
        else:
            self.value_tc.Enable()
        if type == "above" or type == "below":
            self.mirror_l.Show()
        else:
            self.mirror_l.Hide()
        self.Layout()

    def read_trigger_conditions_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        link_pnl = self.parent.parent.parent.link_pnl
        self.read_output_l.SetLabel("")
        conditions_path = shared_data.remote_pigrow_path + "logs/trigger_conditions.txt"
        cmd = "cat " + conditions_path
        out, error = link_pnl.run_on_pi(cmd)
        condition_list = out.splitlines()
        for condition in condition_list:
            if self.cond_name_tc.GetValue().strip() in condition:
                self.read_output_l.SetLabel(condition)

    def check_if_change(self):
        trigger_list = self.parent.parent.trigger_list
        if not trigger_list.initial_log == self.log_cb.GetValue():
            return True
        if not trigger_list.initial_val_label == self.val_label_cb.GetValue():
            return True
        if not trigger_list.initial_type == self.type_cb.GetValue():
            return True
        if not trigger_list.initial_value == self.value_tc.GetValue():
            return True
        if not trigger_list.initial_cond_name == self.cond_name_tc.GetValue():
            return True
        if not trigger_list.initial_set == self.set_cb.GetValue():
            return True
        if not trigger_list.initial_lock == self.lock_tc.GetValue():
            return True
        if not trigger_list.initial_cmd == self.cmd_tc.GetValue():
            return True
        if self.mirror_l.GetValue() == True and self.mirror_l.GetLabel() == 'Create Mirror':
            return True
        # If nothing has changed and the users not asking to create a new mirror trigger
        return False

    def add_click(self, e):
        trigger_list = self.parent.parent.trigger_list
        if self.check_if_change():
            print(" - Saving Changes to Trigger Events File -")
            log = self.log_cb.GetValue()
            label = self.val_label_cb.GetValue()
            type = self.type_cb.GetValue()
            value = self.value_tc.GetValue()
            name = self.cond_name_tc.GetValue()
            set = self.set_cb.GetValue()
            cooldown = self.lock_tc.GetValue()
            cmd = self.cmd_tc.GetValue()
            tt_index = trigger_list.initial_index
            # if new create a new item in the table
            if tt_index == -1:
                # If not already in the table
                trigger_list.add_to_trigger_list(log, label, type, value, name, set, cooldown, cmd)
                if self.mirror_l.GetValue() == True:
                    self.create_mirror(log, label, type, value, name, set, cooldown, cmd)
            else:
                # Fot existing triggers
                trigger_list.update_table_line(tt_index, log, label, type, value, name, set, cooldown, cmd)
                if self.mirror_l.GetValue() == True:
                    mirror_index = self.find_mirror()
                    if type == "above" or type == "below":
                        if mirror_index > -1:
                            print(" -- might be be editing the mirror -- ")
                            self.change_mirror(mirror_index, log, label, value, name)
                        else:
                            self.create_mirror(log, label, type, value, name, set, cooldown, cmd)
            trigger_list.save_table_to_pi()
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class sensor_from_module_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(sensor_from_module_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Sensor Setup from Module")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        sensor_list = i_pnl.sensor_list
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = sensor_list.s_name
        self.s_type  = sensor_list.s_type
        self.s_log   = sensor_list.s_log
        self.s_loc   = sensor_list.s_loc
        self.s_extra = sensor_list.s_extra
        self.timing_string = sensor_list.s_timing
        try:
            s_rep     = sensor_list.s_timing.split(" ")[0]
            s_rep_txt = sensor_list.s_timing.split(" ")[1]
        except:
            s_rep = ""
            s_rep_txt = ""

        # import s_type sensor module as sensor_module
        #       this doesn't appear to be needed anymore
        #self.import_sensor_module()

        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Sensor module: ' + self.s_type)
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        self.show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        self.show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        # buttons_
        self.add_btn = wx.Button(self, label='OK', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # hardware information
        name_l = wx.StaticText(self,  label='Unique Name')
        self.name_tc = wx.TextCtrl(self, size=(400,30))
        log_l = wx.StaticText(self,  label='Log Location')
        self.log_tc = wx.TextCtrl(self, size=(400,30))
        self.graph_btn = wx.Button(self, label='Graph', size=(175, 30))
        # self.graph_btn.Bind(wx.EVT_BUTTON, self.graph_click)
        sensor_l = wx.StaticText(self,  label='Sensor Location')

        # loaded settungs
        self.sensor_connection = wx.StaticText(self,  label="")
        self.loc_cb = wx.ComboBox(self, choices = [], size=(170, 25))
        # Read sensor button
        self.read_sensor_btn = wx.Button(self, label='Read Sensor')
        self.read_sensor_btn.Bind(wx.EVT_BUTTON, self.read_sensor_click)
        self.read_output_l = wx.StaticText(self,  label='')
        # timing string
        timeing_l = wx.StaticText(self,  label='Repeating every ')
        self.rep_num_tc = wx.TextCtrl(self, size=(70,30))
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.rep_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, size=(100, 30))

        # Information request
        self.request_info_l = wx.StaticText(self,  label='Request Information')
        self.request_info_cb = wx.ComboBox(self, choices = [''], size=(200, 30))
        self.request_info_btn = wx.Button(self, label='Send')
        self.request_info_btn.Bind(wx.EVT_BUTTON, self.request_info_click)
        self.request_output_l = wx.StaticText(self,  label='-')
        # Change Setting
        self.change_setting_l = wx.StaticText(self,  label='Change Settings')
        self.change_setting_cb = wx.ComboBox(self, choices=[''], size=(200, 30))
        self.change_setting_tc = wx.TextCtrl(self, size=(70,30))
        self.change_setting_btn = wx.Button(self, label='Set')
        self.change_setting_btn.Bind(wx.EVT_BUTTON, self.change_setting_click)
        self.change_setting_out_l = wx.StaticText(self,  label='-')

        self.read_mod_settings()

        # Sizers
        top_line_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_line_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 3)
        top_line_sizer.AddStretchSpacer(1)
        top_line_sizer.Add(self.show_guide_btn, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(self.sensor_connection, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.loc_cb, 0, wx.ALL|wx.EXPAND, 3)
        loc_sizer.Add(self.read_sensor_btn, 0, wx.ALL, 3)
        loc_sizer.Add(self.read_output_l, 0, wx.ALL, 3)
        timing_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_sizer.Add(self.rep_num_tc, 0, wx.ALL, 3)
        timing_sizer.Add(self.rep_opts_cb, 0, wx.ALL, 3)
        log_sizer = wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(self.log_tc, 2, wx.ALL, 3)
        log_sizer.Add(self.graph_btn, 0, wx.ALL, 3)
        options_sizer = wx.FlexGridSizer(4, 2, 1, 4)
        options_sizer.AddMany([ (name_l, 0, wx.EXPAND),
            (self.name_tc, 0, wx.EXPAND),
            (log_l, 0, wx.EXPAND),
            (log_sizer, 0, wx.EXPAND),
            (sensor_l, 0, wx.EXPAND),
            (loc_sizer, 0, wx.EXPAND),
            (timeing_l, 0, wx.EXPAND),
            (timing_sizer, 0, wx.EXPAND) ])
        request_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        request_info_sizer.Add(self.request_info_l, 0,  wx.ALL, 3)
        request_info_sizer.Add(self.request_info_cb, 0,  wx.ALL, 3)
        request_info_sizer.Add(self.request_info_btn, 0,  wx.ALL, 3)
        change_setting_sizer = wx.BoxSizer(wx.HORIZONTAL)
        change_setting_sizer.Add(self.change_setting_l, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_cb, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_tc, 0,  wx.ALL, 3)
        change_setting_sizer.Add(self.change_setting_btn, 0,  wx.ALL, 3)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.add_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(top_line_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(options_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(request_info_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.request_output_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(change_setting_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.change_setting_out_l, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

        # set values for when reading from double click
        self.name_tc.SetValue(self.s_name)
        self.log_tc.SetValue(self.s_log)
        if not self.s_loc == "":
            self.loc_cb.SetValue(self.s_loc)
        self.rep_num_tc.SetValue(s_rep)
        self.rep_opts_cb.SetValue(s_rep_txt)

    def show_guide_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        guide_path = "guide_" + self.s_type + ".png"
        guide_path = os.path.join(shared_data.sensor_modules_path, guide_path)
        guide = wx.Image(guide_path, wx.BITMAP_TYPE_ANY)
        guide = guide.ConvertToBitmap()
        if os.path.isfile(guide_path):
            dbox = shared_data.show_image_dialog(None, guide, self.s_type)
            dbox.ShowModal()
            dbox.Destroy()
        else:
            print(" - Sensor does not have an associated guide")
            print("     " + guide_path + " not found")

    def change_setting_click(self, e):
        link_pnl = self.parent.parent.parent.link_pnl
        shared_data = self.parent.parent.parent.shared_data
        sensor_name = self.name_tc.GetValue()
        setting_to_change = self.change_setting_cb.GetValue()
        sensor_location = self.loc_cb.GetValue()
        setting_value = self.change_setting_tc.GetValue()
        if not setting_to_change == "":
            module_name = self.s_type
            sensor_module_path = shared_data.remote_pigrow_path + "scripts/gui/sensor_modules/sensor_" + module_name + ".py"
            check_message = "Are you sure you want to change " + setting_to_change + " to " + setting_value + "?"
            dbox = wx.MessageDialog(self, check_message, "Change Setting?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            if (answer == wx.ID_OK):
                out, error = link_pnl.run_on_pi(sensor_module_path + " location=" + sensor_location + " set=" + setting_to_change + "=" + setting_value + " name=" + sensor_name)
                out = out.strip()
                self.change_setting_out_l.SetLabel(setting_to_change + ": " + out + error)
                print(setting_to_change + ": " + out + error)
                self.Layout()

    def request_info_click(self, e):
        link_pnl = self.parent.parent.parent.link_pnl
        shared_data = self.parent.parent.parent.shared_data
        sensor_name = self.name_tc.GetValue()
        item_to_request = self.request_info_cb.GetValue()
        sensor_location = self.loc_cb.GetValue()
        if not item_to_request == "":
            module_name = self.s_type
            sensor_module_path = shared_data.remote_pigrow_path + "scripts/gui/sensor_modules/sensor_" + module_name + ".py"
            out, error = link_pnl.run_on_pi(sensor_module_path + " location=" + sensor_location + " request=" + item_to_request + " name=" + sensor_name)
            out = out.strip()
            self.request_output_l.SetLabel(item_to_request + ": " + out + error)
            print(item_to_request + ": " + out + error)
            self.Layout()

    def read_mod_settings(self):
        link_pnl = self.parent.parent.parent.link_pnl
        shared_data = self.parent.parent.parent.shared_data
        print(" -- READING MODULE SETTINGS -- ")
        module_name = self.s_type
        sensor_module_path = shared_data.remote_pigrow_path + "scripts/gui/sensor_modules/sensor_" + module_name + ".py"
        out, error = link_pnl.run_on_pi(sensor_module_path + " -config")
        print(out, error)
        print(" -------------------------------------- ")
        def_address = ""
        only_option = False
        for line in out.strip().splitlines():
            if "=" in line:
                setting = line.split("=")[0]
                value = line.split("=")[1]
                if setting == "connection_type":
                    print(" currently no box for connection type ")
                    # write to connection type box which doesn't yet exist
                elif setting == "connection_address_list":
                    self.loc_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            #---- add function here to remove sensors already added
                            self.loc_cb.Append(item)
                    else:
                        self.loc_cb.Append(value)
                        self.loc_cb.SetValue(value)
                        only_option = True
                elif setting == "default_connection_address":
                    def_address = value
                elif setting == "available_info":
                    self.request_info_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            self.request_info_cb.Append(item)
                    else:
                        self.request_info_cb.Append(value)
                        self.request_info_cb.SetValue(value)
                # settings options
                elif setting == "available_settings":
                    self.change_setting_cb.Clear()
                    if "," in value:
                        for item in value.split(","):
                            self.change_setting_cb.Append(item)
                    else:
                        self.change_setting_cb.Append(value)
                        self.change_setting_cb.SetValue(value)

        if not only_option == True:
            self.loc_cb.SetValue(def_address)

    def import_sensor_module(self):
        module_name = self.s_type
        print(" Importing module; " + module_name)
        module_name = "sensor_" + module_name
        if module_name in sys.modules:
            del sys.modules[module_name]
        exec('import ' + module_name + ' as sensor_module', globals())

    def read_sensor_click(self, e):
        link_pnl = self.parent.parent.parent.link_pnl
        shared_data = self.parent.parent.parent.shared_data
        module_name = self.s_type
        sensor_name = self.name_tc.GetValue()
        print(" - attempting to read sensor using module -" + module_name)
        module_path = shared_data.remote_pigrow_path + "scripts/gui/sensor_modules/sensor_" + module_name + ".py location=" + self.loc_cb.GetValue() + " name=" + sensor_name
        out, error = link_pnl.run_on_pi(module_path)
        self.read_output_l.SetLabel(out)
        print(out, error)
        print(" ")

    def read_current_o_extra(self, name):
        # this is needed because the sensor modules
        # might edit the sensors extra string
        # while the dialog box is open
        shared_data = self.parent.parent.parent.shared_data
        config_path = shared_data.remote_pigrow_path + "config/pigrow_config.txt"
        sensor_string = "sensor_" + name + "_extra="
        read_extra_cmd = "cat " + config_path + " |grep " + sensor_string
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(read_extra_cmd)
        return out.strip().strip(sensor_string)

    def add_click(self, e):
        i_pnl       = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        cron_i_pnl  = self.parent.parent.parent.dict_I_pnl['cron_pnl']
        shared_data = self.parent.parent.parent.shared_data
        link_pnl    = self.parent.parent.parent.link_pnl
        sensor_list = i_pnl.sensor_list
        o_name = self.name_tc.GetValue()
        o_log = self.log_tc.GetValue()
        o_loc = self.loc_cb.GetValue()
        new_cron_num = self.rep_num_tc.GetValue()
        new_cron_txt = self.rep_opts_cb.GetValue()
        new_timing_string = str(new_cron_num) + " " + new_cron_txt

        # check to see if changes have been made
        changed = "probably something"
        if self.s_name == o_name:
            if self.s_log == o_log:
                if self.s_loc == o_loc:
                        changed = "nothing"
                        #nothing has changed in the config file so no need to update.

        # check to see if changes have been made to the cron timing
        if self.timing_string == new_timing_string and self.s_name == o_name:
            print(" -- Timing string didn't change, nor did the name so no need to chagne cron-- ")
        else:
            script_path = shared_data.remote_pigrow_path + "scripts/sensors/log_sensor_module.py"
            cron_i_pnl.edit_repeat_job_by_name(script_path, self.s_name, o_name, new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            o_extra = self.read_current_o_extra(self.s_name)
            shared_data.config_dict["sensor_" + o_name + "_type"] = self.s_type
            shared_data.config_dict["sensor_" + o_name + "_log"] = o_log
            shared_data.config_dict["sensor_" + o_name + "_loc"] = o_loc
            if not o_extra.strip() == "":
                shared_data.config_dict["sensor_" + o_name + "_extra"] = o_extra
            # if renaming remove the sensor with the old name
            if not o_name == self.s_name:
                possible_keys = ["sensor_" + self.s_name + "_type",
                                 "sensor_" + self.s_name + "_log",
                                 "sensor_" + self.s_name + "_loc",
                                 "sensor_" + self.s_name + "_extra"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]
            # save setting to pi
            shared_data.update_pigrow_config_file_on_pi() #ask="no")
        self.Destroy()

    def OnClose(self, e):
        i_pnl = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        sensor_list = i_pnl.sensor_list
        sensor_list.s_name = ""
        sensor_list.s_log = ""
        sensor_list.s_loc = ""
        sensor_list.s_extra = ""
        sensor_list.s_timing = ""
        self.Destroy()

class button_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(button_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Button setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        sensor_list = i_pnl.sensor_list
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = sensor_list.s_name
        self.s_type  = sensor_list.s_type
        self.s_log   = sensor_list.s_log
        self.s_logtype = sensor_list.s_logtype
        self.s_loc   = sensor_list.s_loc
        self.s_extra = sensor_list.s_extra
        self.s_cmdD  = sensor_list.s_cmdD
        self.s_cmdU  = sensor_list.s_cmdU
        #self.timing_string = sensor_list.s_timing

        # panel
        pnl = wx.Panel(self)
        box_label = wx.StaticText(self,  label='Button')
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        # controls
        ## unique name
        name_label = wx.StaticText(self,  label='Unique name')
        self.name_tc = wx.TextCtrl(self, value=self.s_name, size=(200,30))
        name_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALL|wx.EXPAND, 5)
        name_sizer.Add(self.name_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## type  - GND or HIGH depending on which the non-gpio wire is attached to
        type_label = wx.StaticText(self,  label='Type')
        self.type_cb = wx.ComboBox(self, choices = ['GND', 'High'], value=self.s_type, size=(100,30))
        type_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        type_sizer.Add(type_label, 0, wx.ALL|wx.EXPAND, 5)
        type_sizer.Add(self.type_cb, 0, wx.ALL|wx.EXPAND, 5)
        ## gpio pin
        gpio_label = wx.StaticText(self,  label='GPIO pin')
        self.gpio_tc = wx.TextCtrl(self, value=self.s_loc)
        #self.gpio_tc.SetValue()
        gpio_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        gpio_sizer.Add(gpio_label, 0, wx.ALL, 5)
        gpio_sizer.Add(self.gpio_tc, 0, wx.ALL, 5)
        # read button state button
        self.read_but_btn = wx.Button(self, label='Read Button', size=(175, 30))
        self.read_but_btn.Bind(wx.EVT_BUTTON, self.read_but_click)
        self.read_but_text = wx.StaticText(self,  label='\n \n \n')
        readbut_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        readbut_sizer.Add(self.read_but_btn, 0, wx.ALL, 5)
        readbut_sizer.Add(self.read_but_text, 0, wx.ALL, 5)

        main_ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        main_ctrl_sizer.Add(name_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_ctrl_sizer.Add(type_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_ctrl_sizer.Add(gpio_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_ctrl_sizer.Add(readbut_sizer, 0, wx.ALL, 3)

        # controls used by button_watcher.py
        watcher_label = wx.StaticText(self,  label='button_watcher.py')
        watcher_label.SetFont(shared_data.sub_title_font)
        ## log path  - path for log
        log_label = wx.StaticText(self,  label='Log path')
        self.log_tc = wx.TextCtrl(self, value=self.s_log, size=(400,30))
        self.log_btn = wx.Button(self, label='..', size=(75, 30))
        self.log_btn.Bind(wx.EVT_BUTTON, self.log_click)
        log_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        log_sizer.Add(log_label, 0, wx.ALL|wx.EXPAND, 5)
        log_sizer.Add(self.log_tc, 0, wx.ALL|wx.EXPAND, 5)
        log_sizer.Add(self.log_btn, 0, wx.ALL|wx.EXPAND, 5)
        ## button or switch
        self.logtype_cb = wx.CheckBox(self, 0, label="Log as Switch")
        if self.s_logtype == "True":
            self.logtype_cb.SetValue(True)
        ## cmd_D - command to run when button pressed down
        cmdD_label = wx.StaticText(self,  label='Run on Down')
        self.cmdD_tc = wx.TextCtrl(self, value=self.s_cmdD, size=(400,30))
        self.cmdD_btn = wx.Button(self, label='..', size=(75, 30))
        self.cmdD_btn.Bind(wx.EVT_BUTTON, self.cmdD_click)
        self.cmdD_test_btn = wx.Button(self, label='test', size=(75, 30))
        self.cmdD_test_btn.Bind(wx.EVT_BUTTON, self.cmdD_test_click)
        cmdD_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        cmdD_sizer.Add(cmdD_label, 0, wx.ALL|wx.EXPAND, 5)
        cmdD_sizer.Add(self.cmdD_tc, 0, wx.ALL|wx.EXPAND, 5)
        cmdD_sizer.Add(self.cmdD_btn, 0, wx.ALL|wx.EXPAND, 5)
        cmdD_sizer.Add(self.cmdD_test_btn, 0, wx.ALL|wx.EXPAND, 5)
        ## cmd_U - command to run when button released
        cmdU_label = wx.StaticText(self,  label='Run on Up')
        self.cmdU_tc = wx.TextCtrl(self, value=self.s_cmdU, size=(400,30))
        self.cmdU_btn = wx.Button(self, label='..', size=(75, 30))
        self.cmdU_btn.Bind(wx.EVT_BUTTON, self.cmdU_click)
        self.cmdU_test_btn = wx.Button(self, label='test', size=(75, 30))
        self.cmdU_test_btn.Bind(wx.EVT_BUTTON, self.cmdU_test_click)
        cmdU_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        cmdU_sizer.Add(cmdU_label, 0, wx.ALL|wx.EXPAND, 5)
        cmdU_sizer.Add(self.cmdU_tc, 0, wx.ALL|wx.EXPAND, 5)
        cmdU_sizer.Add(self.cmdU_btn, 0, wx.ALL|wx.EXPAND, 5)
        cmdU_sizer.Add(self.cmdU_test_btn, 0, wx.ALL|wx.EXPAND, 5)

        watcher_ctrl_sizer = wx.BoxSizer(wx.VERTICAL)
        watcher_ctrl_sizer.Add(watcher_label, 0, wx.ALL|wx.EXPAND, 3)
        watcher_ctrl_sizer.Add(log_sizer, 0, wx.ALL|wx.EXPAND, 3)
        watcher_ctrl_sizer.Add(self.logtype_cb, 0, wx.ALL|wx.EXPAND, 3)
        watcher_ctrl_sizer.Add(cmdD_sizer, 0, wx.ALL|wx.EXPAND, 3)
        watcher_ctrl_sizer.Add(cmdU_sizer, 0, wx.ALL|wx.EXPAND, 3)

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
        main_sizer.Add(main_ctrl_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(watcher_ctrl_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def log_click(self, e):
        pigrow_log_path = self.parent.parent.parent.shared_data.remote_pigrow_path
        log_path = pigrow_log_path + "logs/button_" + self.name_tc.GetValue() + ".txt"
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.select_file(self.log_tc, log_path)

    def cmdD_click(self, e):
        scripts_path = self.parent.parent.parent.shared_data.remote_pigrow_path + "scripts/"
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.select_file(self.cmdD_tc, scripts_path)

    def cmdD_test_click(self, e):
        print(" TESTING d")
        cmd = self.cmdD_tc.GetValue()
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.run_test_cmd(cmd)

    def cmdU_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        scripts_path = shared_data.remote_pigrow_path + "scripts/"
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.select_file(self.cmdU_tc, scripts_path)

    def cmdU_test_click(self, e):
        print(" TESTING u")
        cmd = self.cmdU_tc.GetValue()
        c_pnl = self.parent.parent.parent.dict_C_pnl['sensors_pnl']
        c_pnl.run_test_cmd(cmd)

    def save_click(self, e):
        i_pnl       = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        cron_i_pnl  = self.parent.parent.parent.dict_I_pnl['cron_pnl']
        shared_data = self.parent.parent.parent.shared_data
        link_pnl    = self.parent.parent.parent.link_pnl
        sensor_list = i_pnl.sensor_list

        o_type  = self.type_cb.GetValue()
        o_name  = self.name_tc.GetValue()
        o_log   = self.log_tc.GetValue()
        o_logtype = str(self.logtype_cb.GetValue())
        o_loc   = self.gpio_tc.GetValue()
        o_cmdD  = self.cmdD_tc.GetValue()
        o_cmdU  = self.cmdU_tc.GetValue()

        # check to see if changes have been made
        changed = "probably something"
        if self.s_type == o_type:
            if self.s_name == o_name:
                if self.s_log == o_log:
                    if self.s_loc == o_loc:
                        if self.s_cmdD == o_cmdD:
                            if self.s_cmdU == o_cmdU:
                                if self.s_logtype == o_logtype:
                                    changed = "nothing"
                                    #nothing has changed in the config file so no need to update.

        # check to see if changes have been made to the cron timing
        if self.s_name == o_name:
            print(" -- Name didn't change so no need to update cron-- ")
        else:
            print(" !!! NOT CURRENTLY CHANGING NAME IN CRONJOB, THIS IS A PROBLEM! need to add code to update bootup jobs")
                    #script_path = shared_data.remote_pigrow_path + "scripts/sensors/log_sensor_module.py"
                    #cron_i_pnl.edit_repeat_job_by_name(script_path, self.s_name, o_name, new_cron_txt, new_cron_num)

        # config file changes
        if changed == "nothing":
            print("------- config settings not changed -------")
        else:
            name_start = "button_" + o_name
            shared_data.config_dict[name_start + "_type"] = o_type
            shared_data.config_dict[name_start + "_loc"] = o_loc
            shared_data.config_dict[name_start + "_log"] = o_log
            shared_data.config_dict[name_start + "_logtype"] = o_logtype
            shared_data.config_dict[name_start + "_cmdD"] = o_cmdD
            shared_data.config_dict[name_start + "_cmdU"] = o_cmdU

            # if renaming remove the sensor with the old name
            if not o_name == self.s_name:
                possible_keys = ["button_" + self.s_name + "_type",
                                 "button_" + self.s_name + "_log",
                                 "button_" + self.s_name + "_logtype",
                                 "button_" + self.s_name + "_loc",
                                 "button_" + self.s_name + "_cmdD",
                                 "button_" + self.s_name + "_cmdU"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]
            # save setting to pi
            shared_data.update_pigrow_config_file_on_pi() #ask="no")
        self.Destroy()

    def read_but_click(self, e):
        gpio = self.gpio_tc.GetValue()
        type = "GND"
        if not gpio == "":
            script = self.parent.parent.parent.shared_data.remote_pigrow_path + "scripts/triggers/read_switch.py"
            cmd = script + " gpio=" + gpio + " type=" + type
            out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
            self.read_but_text.SetLabel(out)


    def show_guide_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        guide_path = os.path.join(shared_data.ui_img_path, "button_help.png")

        if os.path.isfile(guide_path):
            guide = wx.Image(guide_path, wx.BITMAP_TYPE_ANY)
            guide = guide.ConvertToBitmap()
            dbox = shared_data.show_image_dialog(None, guide, "Button Help")
            dbox.ShowModal()
            dbox.Destroy()
        else:
            print(" - Button help file not found, sorry.")
            print("     No file at " + guide_path)

    def OnClose(self, e):
        i_pnl = self.parent.parent.parent.dict_I_pnl['sensors_pnl']
        sensor_list = i_pnl.sensor_list
        sensor_list.s_name   = ""
        sensor_list.s_log    = ""
        sensor_list.s_logtype = ""
        sensor_list.s_loc    = ""
        sensor_list.s_timing = ""
        sensor_list.s_extra  = ""
        sensor_list.s_cmdD   = ""
        sensor_list.s_cmdU   = ""
        self.Destroy()
