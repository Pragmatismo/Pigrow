import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170))
        self.l = wx.StaticText(self,  label=' POWER ')
        self.fill_table_btn = wx.Button(self, label='Fill Table', size=(75, 30))
        self.fill_table_btn.Bind(wx.EVT_BUTTON, self.fill_tables_click)

        self.add_relay_btn = wx.Button(self, label='Add\nRelay Control')
        self.add_relay_btn.Bind(wx.EVT_BUTTON, self.add_relay_click)

        self.lamp_confirm_btn = wx.Button(self, label='Config\nLamp Confirm')
        self.lamp_confirm_btn.Bind(wx.EVT_BUTTON, self.lamp_confirm_click)

        self.add_hbridge_btn = wx.Button(self, label='Add\nH-Bridge Control')
        self.add_hbridge_btn.Bind(wx.EVT_BUTTON, self.add_hbridge_click)

        self.add_pca_btn = wx.Button(self, label='Add\npca9685 Control')
        self.add_pca_btn.Bind(wx.EVT_BUTTON, self.add_pca_click)

        self.add_hwpwm_btn = wx.Button(self, label='Add\nHardware PWM')
        self.add_hwpwm_btn.Bind(wx.EVT_BUTTON, self.add_hwpwm_click)

        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.l, 0, wx.ALL|wx.EXPAND, 5)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.fill_table_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.lamp_confirm_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.add_relay_btn, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.add_hbridge_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.add_hwpwm_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.add_pca_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def fill_tables_click(self, e):
        self.parent.shared_data.read_pigrow_settings_file()
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        i_pnl.relay_ctrl_lst.make_table()
        i_pnl.motor_ctrl_lst.make_table()
        i_pnl.pwm_device_lst.make_table()

    def add_relay_click(self, e):
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        # load config from file and fill tables so there are no conflicts
        self.fill_tables_click("e")
        # set blanks for dialog box
        i_pnl.relay_ctrl_lst.s_name = ""
        i_pnl.relay_ctrl_lst.s_gpio = ""
        i_pnl.relay_ctrl_lst.s_wiring = ""
    #    i_pnl.motor_ctrl_lst.s_current = ""
        # call dialog box
        add_button = relay_dialog(i_pnl.relay_ctrl_lst, i_pnl.relay_ctrl_lst.parent)
        add_button.ShowModal()
        self.fill_tables_click("e")

    def lamp_confirm_click(self, e):
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        # load config from file and fill tables so there are no conflicts
        self.fill_tables_click("e")

        # call dialog box
        lc_dbox = lampcon_dialog(self, self.parent)
        lc_dbox.ShowModal()

    def add_hbridge_click(self, e):
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        # load config from file and fill tables so there are no conflicts
        self.fill_tables_click("e")
        # set blanks for dialog box
        i_pnl.motor_ctrl_lst.s_name = ""
        i_pnl.motor_ctrl_lst.s_gpioA = ""
        i_pnl.motor_ctrl_lst.s_gpioB = ""
        i_pnl.motor_ctrl_lst.s_pwm = ""
        # call dialog box
        add_button = hbridge_dialog(i_pnl.motor_ctrl_lst, i_pnl.motor_ctrl_lst.parent)
        add_button.ShowModal()
        self.fill_tables_click("e")

    def add_pca_click(self, e):
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        # load config from file and fill tables so there are no conflicts
        self.fill_tables_click("e")
        # set blanks for dialog box
        i_pnl.pwm_device_lst.s_name = ""
        i_pnl.pwm_device_lst.s_loc = ""
        i_pnl.pwm_device_lst.s_freq = ""
        # call dialog box
        add_button = pca_dialog(i_pnl.pwm_device_lst, i_pnl.pwm_device_lst.parent)
        add_button.ShowModal()
        self.fill_tables_click("e")

    def add_hwpwm_click(self, e):
        i_pnl = self.parent.dict_I_pnl['power_pnl']
        # load config from file and fill tables so there are no conflicts
        self.fill_tables_click("e")
        # set blanks for dialog box
        i_pnl.pwm_device_lst.s_name = ""
        i_pnl.pwm_device_lst.s_loc = ""
        i_pnl.pwm_device_lst.s_freq = ""
        # call dialog box
        add_button = hwpwm_dialog(i_pnl.pwm_device_lst, i_pnl.pwm_device_lst.parent)
        add_button.ShowModal()
        self.fill_tables_click("e")


    def connect_to_pigrow(self):
        '''
        This is called every time a connection to a pigrow is made
        '''
        self.fill_tables_click("e")
        pass

class info_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        self.parent = parent
        self.c_pnl = parent.dict_C_pnl['power_pnl']
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        #self.SetBackgroundColour((50,50,50))
        self.SetFont(shared_data.title_font)
        self.title = wx.StaticText(self,  label=' Power Control Devices')
        self.SetFont(shared_data.sub_title_font)

        # relay control
        self.relay_l = wx.StaticText(self,  label='Relay Control')
        self.relay_help_btn = wx.Button(self, label='Guide', size=(75, 30))
        self.relay_help_btn.Bind(wx.EVT_BUTTON, self.relay_help_click)
        relay_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
        relay_l_sizer.Add(self.relay_l, 0, wx.ALL, 3)
        relay_l_sizer.AddStretchSpacer(1)
        relay_l_sizer.Add(self.relay_help_btn, 0, wx.ALL, 3)

        self.relay_ctrl_lst = self.relay_control_list(self, 1)
        self.relay_ctrl_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.relay_ctrl_lst.doubleclick)

        relay_sizer = wx.BoxSizer(wx.VERTICAL)
        relay_sizer.Add(relay_l_sizer, 0, wx.ALL|wx.EXPAND, 3)
        relay_sizer.Add(self.relay_ctrl_lst, 0, wx.ALL|wx.EXPAND, 3)

        # motor control
        self.motor_l = wx.StaticText(self,  label='H-Bridge Motor Control')
        self.motor_help_btn = wx.Button(self, label='Guide', size=(75, 30))
        self.motor_help_btn.Bind(wx.EVT_BUTTON, self.motor_help_click)
        motor_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
        motor_l_sizer.Add(self.motor_l, 0, wx.ALL, 3)
        motor_l_sizer.AddStretchSpacer(1)
        motor_l_sizer.Add(self.motor_help_btn, 0, wx.ALL, 3)

        self.motor_ctrl_lst = self.motor_control_list(self, 1)
        self.motor_ctrl_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.motor_ctrl_lst.doubleclick)

        motor_sizer = wx.BoxSizer(wx.VERTICAL)
        motor_sizer.Add(motor_l_sizer, 0, wx.ALL|wx.EXPAND, 3)
        motor_sizer.Add(self.motor_ctrl_lst, 0, wx.ALL|wx.EXPAND, 3)

        # PCA9685
        self.pca_l = wx.StaticText(self,  label='PCA9685 - PWM Control')
        self.pca_help_btn = wx.Button(self, label='Guide', size=(75, 30))
        self.pca_help_btn.Bind(wx.EVT_BUTTON, self.pca_help_click)
        pca_l_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pca_l_sizer.Add(self.pca_l, 0, wx.ALL, 3)
        pca_l_sizer.AddStretchSpacer(1)
        pca_l_sizer.Add(self.pca_help_btn, 0, wx.ALL, 3)

        self.pwm_device_lst = self.pwm_list(self, 1)
        self.pwm_device_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.pwm_device_lst.doubleclick)
        self.pca_chan_sizer =  wx.BoxSizer(wx.VERTICAL)

        pca_sizer = wx.BoxSizer(wx.VERTICAL)
        pca_sizer.Add(pca_l_sizer, 0, wx.ALL|wx.EXPAND, 3)
        pca_sizer.Add(self.pwm_device_lst, 0, wx.ALL|wx.EXPAND, 3)
        pca_sizer.Add(self.pca_chan_sizer, 0, wx.ALL|wx.EXPAND, 3)


        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.title, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(relay_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(motor_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(pca_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        #main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.make_chan_ctrl()
        self.SetSizer(main_sizer)

    def relay_help_click(self, e):
        self.parent.shared_data.show_help('relay_help.png')

    def motor_help_click(self, e):
        self.parent.shared_data.show_help('motor_help.png')

    def pca_help_click(self, e):
        self.parent.shared_data.show_help('pca_help.png')

    def make_chan_ctrl(self):
        selected = self.pwm_device_lst.GetNextSelected(-1)
        name = ""
        if not selected == -1:
            name = self.pwm_device_lst.GetItemText(selected, 0)
        self.pca_chan_l = wx.StaticText(self,  label='PCA Channel info ' + name)

        self.pca_chan_sizer.Add(self.pca_chan_l, 0, wx.ALL|wx.EXPAND, 5)
        self.Layout()
        self.parent.Layout()

    class relay_control_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'gpio')
            self.InsertColumn(2, 'wiring')
            self.InsertColumn(3, 'currently')
            self.autosizeme()

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            relay_list = []
            print("  - Using config_dict to fill relay table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "gpio_" in key:
                    name = key.split("_")[1]
                    if not name in relay_list:
                        relay_list.append(name)

            switch_status = self.get_switch_dict()
            for relay_name in relay_list:
                gpio, wiring = self.read_relay_conf(relay_name, config_dict, "gpio_")
                if not relay_name == "dht22sensor": #ignore
                    s_state = switch_status.get(relay_name, "not found")
                    self.add_to_relay_table(relay_name, gpio, wiring, s_state)
            self.autosizeme()

        def get_switch_dict(self):
            cmd = self.parent.parent.shared_data.remote_pigrow_path + "scripts/gui/info_modules/info_switch_position.py"
            out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
            switch_lines = out.splitlines()

            switches = {}
            for line in switch_lines:
                parts = line.split(" is ")
                if len(parts) == 2:
                    switch_name = parts[0].strip()
                    status = parts[1].strip().lower()
                    switches[switch_name] = status
            return switches

        def read_relay_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["",
                          "_on"]
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

        def add_to_relay_table(self, name, gpio, wiring, switch_status):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(gpio))
            self.SetItem(0, 2, str(wiring))
            self.SetItem(0, 3, str(switch_status))

        def doubleclick(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            self.s_name  = self.GetItem(index, 0).GetText()
            self.s_gpio = self.GetItem(index, 1).GetText()
            self.s_wiring = self.GetItem(index, 2).GetText()
        #    self.s_current   = self.GetItem(index, 3).GetText()
            relay_box = relay_dialog(self, self.parent)
            relay_box.ShowModal()
            self.parent.c_pnl.fill_tables_click("e")

        def read_pin_state(self, gpio_pin):
            """
            Remotely read GPIO state, using:
              1) existing sysfs export
              2) sysfs export if needed
              3) gpioget fallback
            """
            remote = self.parent.parent.link_pnl
            sys_path = f"/sys/class/gpio/gpio{gpio_pin}"
            value_path = f"{sys_path}/value"
            direction_path = f"{sys_path}/direction"

            # 1) If already exported via sysfs, read it
            out, err = remote.run_on_pi(f"if [ -d {sys_path} ]; then echo yes; else echo no; fi")
            if out.strip() == "yes":
                # If it's an output pin, bail out
                out_dir, _ = remote.run_on_pi(f"cat {direction_path} 2>/dev/null")
                if out_dir.strip() == "out":
                    return f"GPIO {gpio_pin} is set as OUTPUT and cannot be read."
                # Otherwise read its value
                out_val, _ = remote.run_on_pi(f"cat {value_path}")
                return out_val.strip()

            # 2) Try to export via sysfs (older kernels)
            out_exp, _ = remote.run_on_pi(
                f"echo {gpio_pin} > /sys/class/gpio/export 2>/dev/null && echo success || echo fail"
            )
            if out_exp.strip() == "success":
                # small pause to let sysfs create the directory
                remote.run_on_pi("sleep 0.1")
                out_val, _ = remote.run_on_pi(f"cat {value_path}")
                return out_val.strip()

            # 3) Fallback to gpioget if available
            out_chk, _ = remote.run_on_pi("command -v gpioget >/dev/null 2>&1 && echo yes || echo no")
            if out_chk.strip() == "yes":
                out_val, _ = remote.run_on_pi(f"gpioget gpiochip0 {gpio_pin}")
                return out_val.strip()

            # If all else fails
            return f"Unable to determine GPIO {gpio_pin} status."

        def determine_device_state(self, pin_state, wiring):
            text = "unset"
            if pin_state == "1":
                if wiring == "low":
                    text = "off"
                elif wiring == "high":
                    text = "on"

            elif pin_state == "0":
                if wiring == "low":
                    text = "on"
                elif wiring == "high":
                    text = "off"

            return text

    class motor_control_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'gpio A')
            self.InsertColumn(2, 'gpio B')
            self.InsertColumn(3, 'pwm control')
            self.autosizeme()

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            motor_list = []
            print("  - Using config_dict to fill motor table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "hbridge_" in key:
                    name = key.split("_")[1]
                    if not name in motor_list:
                        motor_list.append(name)

            for motor_name in motor_list:
                gpioA, gpioB, pwm = self.read_motor_conf(motor_name, config_dict, "hbridge_")
                self.add_to_motor_table(motor_name, gpioA, gpioB, pwm)
            self.autosizeme()

        def read_motor_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["_gpioA",
                          "_gpioB",
                          "_pwm"]
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

        def add_to_motor_table(self, name, gpioA, gpioB, pwm_ctrl):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(gpioA))
            self.SetItem(0, 2, str(gpioB))
            self.SetItem(0, 3, str(pwm_ctrl))

        def doubleclick(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            self.s_name  = self.GetItem(index, 0).GetText()
            self.s_gpioA = self.GetItem(index, 1).GetText()
            self.s_gpioB = self.GetItem(index, 2).GetText()
            self.s_pwm   = self.GetItem(index, 3).GetText()
            h_dialog_box = hbridge_dialog(self, self.parent)
            h_dialog_box.ShowModal()
            self.parent.c_pnl.fill_tables_click("e")

    class pwm_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Type')
            self.InsertColumn(1, 'Unique Name')
            self.InsertColumn(2, 'i2c address')
            self.InsertColumn(3, 'Frequency')
            self.autosizeme()

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            pca_list = []
            hwpwm_list = []
            print("  - Using config_dict to fill PWM table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "pca_" in key:
                    name = key.split("_")[1]
                    if not name in pca_list:
                        pca_list.append(name)
                if "hwpwm_" in key:
                    name = key.split("_")[1]
                    if not name in hwpwm_list:
                        hwpwm_list.append(name)

            for pca_name in pca_list:
                i2c, freq = self.read_pwm_conf(pca_name, config_dict, "pca_")
                self.add_to_pwm_list(pca_name, 'pca', i2c, freq)

            for hwpwm_name in hwpwm_list:
                gpio, freq = self.read_pwm_conf(hwpwm_name, config_dict, 'hwpwm_')
                self.add_to_pwm_list(hwpwm_name, 'hwpwm',gpio, freq)
            self.autosizeme()

        def read_pwm_conf(self, item_name, config_dict, prefix):
            # Extract sensor config info from config dictionary
            field_list = ["_loc",
                          "_freq"]
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

        def add_to_pwm_list(self, name, type, i2c, freq):
            self.InsertItem(0, str(type))
            self.SetItem(0, 1,str(name))
            self.SetItem(0, 2, str(i2c))
            self.SetItem(0, 3, str(freq))

        def doubleclick(self, e):
            index =  e.GetIndex()
            self.s_type = self.GetItem(index, 0).GetText()
            self.s_name  = self.GetItem(index, 1).GetText()
            self.s_loc = self.GetItem(index, 2).GetText()
            self.s_freq = self.GetItem(index, 3).GetText()
            if self.s_type == 'pca':
                h_dialog_box = pca_dialog(self, self.parent)
                h_dialog_box.ShowModal()
                self.parent.c_pnl.fill_tables_click("e")
            if self.s_type == 'hwpwm':
                dialog_box = hwpwm_dialog(self, self.parent)
                dialog_box.ShowModal()
                self.parent.c_pnl.fill_tables_click("e")

            else:
                print("Error - type of PWM device not recognised")

class relay_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(relay_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Relay setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['power_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        self.relay_ctrl_lst = i_pnl.relay_ctrl_lst
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = self.relay_ctrl_lst.s_name
        self.s_gpio = self.relay_ctrl_lst.s_gpio
        self.s_wiring = self.relay_ctrl_lst.s_wiring

        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Relay control')
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
        ## gpio
        gpio_label = wx.StaticText(self,  label='gpio')
        self.gpio_tc = wx.TextCtrl(self, value=self.s_gpio)
        gpio_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        gpio_sizer.Add(gpio_label, 0, wx.ALL|wx.EXPAND, 5)
        gpio_sizer.Add(self.gpio_tc, 0, wx.ALL|wx.EXPAND, 5)

        ## wiring
        wiring_label = wx.StaticText(self,  label='wiring')
        wiring_choices = ['low', 'high']
        self.wiring_combo = wx.ComboBox(self, choices = wiring_choices, value=self.s_wiring, size=(110, 30))
        #self.wiring_tc = wx.TextCtrl(self, value=self.s_wiring, size=(200,30))
        wiring_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        wiring_sizer.Add(wiring_label, 0, wx.ALL|wx.EXPAND, 5)
        wiring_sizer.Add(self.wiring_combo, 0, wx.ALL|wx.EXPAND, 5)

        # Read relay directon
        self.read_m_btn = wx.Button(self, label='Read Relay Direction', size=(175, 30))
        self.read_m_btn.Bind(wx.EVT_BUTTON, self.read_relay_directon)
        self.read_m_label = wx.StaticText(self,  label='')
        read_m_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        read_m_sizer.Add(self.read_m_btn, 0, wx.ALL|wx.EXPAND, 5)
        read_m_sizer.Add(self.read_m_label, 0, wx.ALL|wx.EXPAND, 5)

        self.switch_relay_label = wx.StaticText(self,  label='Switch Relay - ')
        self.switch_relay_on_btn = wx.Button(self, label='On')
        self.switch_relay_on_btn.Bind(wx.EVT_BUTTON, self.switch_relay_on)
        self.switch_relay_off_btn = wx.Button(self, label='Off')
        self.switch_relay_off_btn.Bind(wx.EVT_BUTTON, self.switch_relay_off)
        switch_m_d_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        switch_m_d_sizer.Add(self.switch_relay_label, 0, wx.ALL|wx.EXPAND, 5)
        switch_m_d_sizer.Add(self.switch_relay_on_btn, 0, wx.ALL|wx.EXPAND, 5)
        switch_m_d_sizer.Add(self.switch_relay_off_btn, 0, wx.ALL|wx.EXPAND, 5)

        self.switch_warn_label = wx.StaticText(self,  label='WARNING: changes it directly, for testing only')

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
        main_sizer.Add(gpio_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(wiring_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(read_m_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(switch_m_d_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.switch_warn_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.parent.shared_data.show_help('relay_help.png')

    def OnClose(self, e):
        self.relay_ctrl_lst.s_name  = ""
        self.relay_ctrl_lst.s_gpio = ""
        self.relay_ctrl_lst.s_wiring = ""
        self.Destroy()

    def save_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        n_name  = self.name_tc.GetValue()
        n_gpio = self.gpio_tc.GetValue()
        n_wiring = self.wiring_combo.GetValue()
        #n_pwm   =
        # as yet unused self.s_pwm
        changed = "yes"
        if self.s_name == n_name:
            if self.s_gpio == n_gpio:
                if self.s_wiring == n_wiring:
                    changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            name_start = "gpio_" + n_name
            shared_data.config_dict[name_start + ""] = n_gpio
            shared_data.config_dict[name_start + "_on"] = n_wiring
            #shared_data.config_dict[name_start + "_pwm"] = n_pwm

            # If name changed delete old entries
            if not n_name == self.s_name:
                name_start = "gpio_" + self.s_name
                possible_keys = [name_start + "",
                                 name_start + "_on"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()


    def read_relay_directon(self, e):
        gpio_a = self.gpio_tc.GetValue()
        state_a = self.parent.read_pin_state(gpio_a)
        wiring = self.wiring_combo.GetValue()
        msg = "pin value = " + state_a + "\n"
        text = self.parent.determine_device_state(state_a, wiring)
        msg += "Device = " + text
        self.read_m_label.SetLabel(msg)



    def switch_relay_on(self, e):
        shared_data = self.parent.parent.parent.shared_data
        #
        gpio = self.gpio_tc.GetValue()
        wiring = self.wiring_combo.GetValue()
        if not wiring == "low" and not wiring == "high":
                return None
        #
        cmd = shared_data.remote_pigrow_path + "scripts/switches/generic_"
        cmd += wiring + ".py log=none "
        cmd += "gpio=" + gpio
        print("running ",cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out,error)

        self.read_relay_directon("e")

    def switch_relay_off(self, e):
        shared_data = self.parent.parent.parent.shared_data
        gpio = self.gpio_tc.GetValue()
        wiring = self.wiring_combo.GetValue()
        if not wiring == "low" and not wiring == "high":
                return None
        if wiring == "low":
            w_off = "high"
        elif wiring == "high":
            w_off = "low"
        #
        cmd = shared_data.remote_pigrow_path + "scripts/switches/generic_"
        cmd += w_off + ".py log=none "
        cmd += "gpio=" + gpio
        print("running ",cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out,error)
        self.read_relay_directon("e")

class hbridge_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(hbridge_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((650, 450))
        self.SetTitle("H-Bridge setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['power_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        self.motor_ctrl_lst = i_pnl.motor_ctrl_lst
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = self.motor_ctrl_lst.s_name
        self.s_gpioA = self.motor_ctrl_lst.s_gpioA
        self.s_gpioB = self.motor_ctrl_lst.s_gpioB
        self.s_pwm   = self.motor_ctrl_lst.s_pwm

        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='H-bridge motor controller')
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
        ## gpioA
        gpioA_label = wx.StaticText(self,  label='gpioA')
        self.gpioA_tc = wx.TextCtrl(self, value=self.s_gpioA, size=(200,30))
        gpioA_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        gpioA_sizer.Add(gpioA_label, 0, wx.ALL|wx.EXPAND, 5)
        gpioA_sizer.Add(self.gpioA_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## gpioB
        gpioB_label = wx.StaticText(self,  label='gpioB')
        self.gpioB_tc = wx.TextCtrl(self, value=self.s_gpioB, size=(200,30))
        gpioB_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        gpioB_sizer.Add(gpioB_label, 0, wx.ALL|wx.EXPAND, 5)
        gpioB_sizer.Add(self.gpioB_tc, 0, wx.ALL|wx.EXPAND, 5)

        # Read motor directon
        self.read_m_btn = wx.Button(self, label='Read Motor Direction', size=(175, 30))
        self.read_m_btn.Bind(wx.EVT_BUTTON, self.read_motor_directon)
        self.read_m_label = wx.StaticText(self,  label='')
        read_m_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        read_m_sizer.Add(self.read_m_btn, 0, wx.ALL|wx.EXPAND, 5)
        read_m_sizer.Add(self.read_m_label, 0, wx.ALL|wx.EXPAND, 5)

        self.switch_m_d_label = wx.StaticText(self,  label='Set direction - ')
        self.switch_m_d_a_btn = wx.Button(self, label='<<   A +')
        self.switch_m_d_a_btn.Bind(wx.EVT_BUTTON, self.switch_m_d_a)
        self.switch_m_d_off_btn = wx.Button(self, label='Off')
        self.switch_m_d_off_btn.Bind(wx.EVT_BUTTON, self.switch_m_d_off)
        self.switch_m_d_b_btn = wx.Button(self, label='B +   >>')
        self.switch_m_d_b_btn.Bind(wx.EVT_BUTTON, self.switch_m_d_b)
        switch_m_d_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        switch_m_d_sizer.Add(self.switch_m_d_label, 0, wx.ALL|wx.EXPAND, 5)
        switch_m_d_sizer.Add(self.switch_m_d_a_btn, 0, wx.ALL|wx.EXPAND, 5)
        switch_m_d_sizer.Add(self.switch_m_d_off_btn, 0, wx.ALL|wx.EXPAND, 5)
        switch_m_d_sizer.Add(self.switch_m_d_b_btn, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.Add(name_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(gpioA_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(gpioB_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(read_m_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(switch_m_d_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.parent.shared_data.show_help('motor_help.png')

    def OnClose(self, e):
        self.motor_ctrl_lst.s_name  = ""
        self.motor_ctrl_lst.s_gpioA = ""
        self.motor_ctrl_lst.s_gpioB = ""
        self.motor_ctrl_lst.s_pwm   = ""
        self.Destroy()

    def save_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        n_name  = self.name_tc.GetValue()
        n_gpioA = self.gpioA_tc.GetValue()
        n_gpioB = self.gpioB_tc.GetValue()
        #n_pwm   =
        # as yet unused self.s_pwm
        changed = "yes"
        if self.s_name == n_name:
            if self.s_gpioA == n_gpioA:
                if self.s_gpioB == n_gpioB:
                    changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            name_start = "hbridge_" + n_name
            shared_data.config_dict[name_start + "_gpioA"] = n_gpioA
            shared_data.config_dict[name_start + "_gpioB"] = n_gpioB
            #shared_data.config_dict[name_start + "_pwm"] = n_pwm

            # If name changed delete old entries
            if not n_name == self.s_name:
                name_start = "hbridge_" + self.s_name
                possible_keys = [name_start + "_gpioA",
                                 name_start + "_gpioB",
                                 name_start + "_pwm"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()


    def read_motor_directon(self, e):
        gpio_a = self.gpioA_tc.GetValue()
        gpio_b = self.gpioB_tc.GetValue()
        state_a = self.read_pin_state(gpio_a)
        state_b = self.read_pin_state(gpio_b)
        msg = "A = " + state_a + "  B = " + state_b + "\n"
        if state_a == "1" and state_b == "0":
            msg += "Direction set to +"
        elif state_a == "0" and state_b == "1":
            msg += "Direction set to -"
        elif state_b == "0" and state_a == "0":
            msg += "Motor Off"
        else:
            msg += "Not a valid direction setting."
        self.read_m_label.SetLabel(msg)

    def read_pin_state(self, gpio_pin):
        """
        Remotely read GPIO state, using:
          1) existing sysfs export
          2) sysfs export if needed
          3) gpioget fallback
        """
        remote = self.parent.parent.link_pnl
        sys_path = f"/sys/class/gpio/gpio{gpio_pin}"
        value_path = f"{sys_path}/value"
        direction_path = f"{sys_path}/direction"

        # 1) If already exported via sysfs, read it
        out, err = remote.run_on_pi(f"if [ -d {sys_path} ]; then echo yes; else echo no; fi")
        if out.strip() == "yes":
            # If it's an output pin, bail out
            out_dir, _ = remote.run_on_pi(f"cat {direction_path} 2>/dev/null")
            if out_dir.strip() == "out":
                return f"GPIO {gpio_pin} is set as OUTPUT and cannot be read."
            # Otherwise read its value
            out_val, _ = remote.run_on_pi(f"cat {value_path}")
            return out_val.strip()

        # 2) Try to export via sysfs (older kernels)
        out_exp, _ = remote.run_on_pi(
            f"echo {gpio_pin} > /sys/class/gpio/export 2>/dev/null && echo success || echo fail"
        )
        if out_exp.strip() == "success":
            # small pause to let sysfs create the directory
            remote.run_on_pi("sleep 0.1")
            out_val, _ = remote.run_on_pi(f"cat {value_path}")
            return out_val.strip()

        # 3) Fallback to gpioget if available
        out_chk, _ = remote.run_on_pi("command -v gpioget >/dev/null 2>&1 && echo yes || echo no")
        if out_chk.strip() == "yes":
            out_val, _ = remote.run_on_pi(f"gpioget gpiochip0 {gpio_pin}")
            return out_val.strip()

        # If all else fails
        return f"Unable to determine GPIO {gpio_pin} status."

    def set_pin(self, pin, dir):
        cmd = "gpio -g mode " + str(pin) + " out"
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        cmd = "gpio -g write " + str(pin) + " " + str(dir)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)

    def switch_m_d_a(self, e):
        gpio_a = self.gpioA_tc.GetValue()
        gpio_b = self.gpioB_tc.GetValue()
        self.set_pin(gpio_b, 0)
        self.set_pin(gpio_a, 1)
        self.read_motor_directon("e")

    def switch_m_d_off(self, e):
        gpio_a = self.gpioA_tc.GetValue()
        gpio_b = self.gpioB_tc.GetValue()
        self.set_pin(gpio_a, 0)
        self.set_pin(gpio_b, 0)
        self.read_motor_directon("e")

    def switch_m_d_b(self, e):
        gpio_a = self.gpioA_tc.GetValue()
        gpio_b = self.gpioB_tc.GetValue()
        self.set_pin(gpio_a, 0)
        self.set_pin(gpio_b, 1)
        self.read_motor_directon("e")

class pca_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(pca_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((650, 450))
        self.SetTitle("PCA9685 setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['power_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        self.pwm_device_lst = i_pnl.pwm_device_lst
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = self.pwm_device_lst.s_name
        self.s_loc= self.pwm_device_lst.s_loc
        self.s_freq = self.pwm_device_lst.s_freq

        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='PCA9685 controller')
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
        ## i2c
        loc_label = wx.StaticText(self,  label='i2c address')
        self.loc_tc = wx.TextCtrl(self, value=self.s_loc, size=(200,30))
        loc_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(loc_label, 0, wx.ALL|wx.EXPAND, 5)
        loc_sizer.Add(self.loc_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## freq
        freq_label = wx.StaticText(self,  label='freq')
        self.freq_tc = wx.TextCtrl(self, value=self.s_freq, size=(200,30))
        freq_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        freq_sizer.Add(freq_label, 0, wx.ALL|wx.EXPAND, 5)
        freq_sizer.Add(self.freq_tc, 0, wx.ALL|wx.EXPAND, 5)

        #controlls
        set_value_btn = wx.Button(self, label='Set')
        set_value_btn.Bind(wx.EVT_BUTTON, self.set_value_click)
        channel_l = wx.StaticText(self,  label='channel')
        self.channel_tc = wx.TextCtrl(self, value="0")
        power_l = wx.StaticText(self,  label='power %')
        self.power_tc = wx.TextCtrl(self, value="100")

        set_val_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        set_val_sizer.Add(set_value_btn, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(channel_l, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(self.channel_tc, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(power_l, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(self.power_tc, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.Add(name_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(loc_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(freq_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(set_val_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def OnClose(self, e):
        self.pwm_device_lst.s_name  = ""
        self.pwm_device_lst.s_loc = ""
        self.pwm_device_lst.s_freq = ""
        self.Destroy()

    def set_value_click(self, e):
        i2c = self.loc_tc.GetValue()
        freq = self.freq_tc.GetValue()
        chan  = self.channel_tc.GetValue()
        power = self.power_tc.GetValue()
        cmd = self.parent.parent.parent.shared_data.remote_pigrow_path
        cmd += "scripts/switches/pca9685_set.py i2c=" + i2c + " freq=" + freq
        cmd += " chan=" + chan + " value=" + power
        print(cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)


    def save_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        n_name  = self.name_tc.GetValue()
        n_loc = self.loc_tc.GetValue()
        n_freq = self.freq_tc.GetValue()

        changed = "yes"
        if self.s_name == n_name:
            if self.s_loc == n_loc:
                if self.s_freq == n_freq:
                    changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            print(" - Something changed")
            name_start = "pca_" + n_name
            shared_data.config_dict[name_start + "_loc"] = n_loc
            shared_data.config_dict[name_start + "_freq"] = n_freq

            # If name changed delete old entries
            if not n_name == self.s_name:
                name_start = "pca_" + self.s_name
                possible_keys = [name_start + "_loc",
                                 name_start + "_freq"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()

    def show_guide_click(self, e):
        self.parent.parent.parent.shared_data.show_help('pca_help.png')

class hwpwm_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(hwpwm_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((650, 450))
        self.SetTitle("Hardware PWM setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        i_pnl = self.parent.parent.parent.dict_I_pnl['power_pnl']
        shared_data = self.parent.parent.parent.shared_data
        #link_pnl = self.parent.parent.parent.link_pnl
        self.pwm_device_lst = i_pnl.pwm_device_lst
        # read values - blank for adding a new sensor, used when editing existing entry
        self.s_name  = self.pwm_device_lst.s_name
        self.s_loc= self.pwm_device_lst.s_loc
        self.s_freq = self.pwm_device_lst.s_freq

        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Hardware PWM settings')
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
        ## i2c
        loc_label = wx.StaticText(self,  label='gpio pin')
        self.loc_tc = wx.TextCtrl(self, value=self.s_loc, size=(200,30))
        loc_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(loc_label, 0, wx.ALL|wx.EXPAND, 5)
        loc_sizer.Add(self.loc_tc, 0, wx.ALL|wx.EXPAND, 5)
        ## freq
        freq_label = wx.StaticText(self,  label='freq')
        self.freq_tc = wx.TextCtrl(self, value=self.s_freq, size=(200,30))
        freq_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        freq_sizer.Add(freq_label, 0, wx.ALL|wx.EXPAND, 5)
        freq_sizer.Add(self.freq_tc, 0, wx.ALL|wx.EXPAND, 5)

        #controlls
        set_value_btn = wx.Button(self, label='Set')
        set_value_btn.Bind(wx.EVT_BUTTON, self.set_value_click)
#        channel_l = wx.StaticText(self,  label='channel')
#        self.channel_tc = wx.TextCtrl(self, value="0")
        power_l = wx.StaticText(self,  label='power %')
        self.power_tc = wx.TextCtrl(self, value="100")

        set_val_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        set_val_sizer.Add(set_value_btn, 0, wx.ALL|wx.EXPAND, 5)
#        set_val_sizer.Add(channel_l, 0, wx.ALL|wx.EXPAND, 5)
#        set_val_sizer.Add(self.channel_tc, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(power_l, 0, wx.ALL|wx.EXPAND, 5)
        set_val_sizer.Add(self.power_tc, 0, wx.ALL|wx.EXPAND, 5)

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
        main_sizer.Add(name_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(loc_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(freq_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(set_val_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def OnClose(self, e):
        self.pwm_device_lst.s_name  = ""
        self.pwm_device_lst.s_loc = ""
        self.pwm_device_lst.s_freq = ""
        self.Destroy()

    def set_value_click(self, e):
        gpio = self.loc_tc.GetValue()
        freq = self.freq_tc.GetValue()
        power = self.power_tc.GetValue()
        cmd = self.parent.parent.parent.shared_data.remote_pigrow_path
        cmd += "scripts/switches/hwpwm_set.py pin=" + gpio
        cmd += " freq=" + freq
        cmd += " value=" + power
        print(cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)


    def save_click(self, e):
        shared_data = self.parent.parent.parent.shared_data
        n_name  = self.name_tc.GetValue()
        n_loc = self.loc_tc.GetValue()
        n_freq = self.freq_tc.GetValue()

        changed = "yes"
        if self.s_name == n_name:
            if self.s_loc == n_loc:
                if self.s_freq == n_freq:
                    changed = None

        if changed == None:
            print(" - Nothing changed, no need to save ")
        else:
            print(" - Something changed")
            name_start = "hwpwm_" + n_name
            shared_data.config_dict[name_start + "_loc"] = n_loc
            shared_data.config_dict[name_start + "_freq"] = n_freq

            # If name changed delete old entries
            if not n_name == self.s_name:
                name_start = "hwpwm_" + self.s_name
                possible_keys = [name_start + "_loc",
                                 name_start + "_freq"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            shared_data.update_pigrow_config_file_on_pi()
        self.Destroy()

    def show_guide_click(self, e):
        self.parent.parent.parent.shared_data.show_help('hwpwm_help.png')

class lampcon_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(lampcon_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 700))
        self.SetTitle("Lamp with Confirmation")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        #i_pnl = self.parent.parent.parent.dict_I_pnl['power_pnl']
        shared_data = self.parent.parent.shared_data

        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Lamp with Confirmation Test')
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)


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
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.parent.shared_data.show_help('lampcon_help.png')

    def OnClose(self, e):
        self.Destroy()

    def save_click(self, e):
        print("Save is not written yet.")