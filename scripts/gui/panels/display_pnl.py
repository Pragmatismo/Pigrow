import os
import datetime
import wx
import wx.lib.scrolledpanel as scrolled

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # button to refresh pnl information
        self.refresh_btn = wx.Button(self, label='Refresh Info')
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.refresh_btn, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def connect_to_pigrow(self):
        print("display pannel connected to pigrow and doing nothing with it :D lol")

    def refresh_click(self, e):
        self.parent.shared_data.read_pigrow_settings_file()
        i_pnl = self.parent.dict_I_pnl['display_pnl']
        i_pnl.led_lst.make_table()


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        #c_pnl = parent.dict_C_pnl['display_pnl']
        w = 1000
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (w,-1))

        # Title and Subtitle
        self.SetFont(shared_data.title_font)
        page_title =  wx.StaticText(self,  label='Display')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Show output from the pigrow via local displays')
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # LED
        led_title =  wx.StaticText(self,  label='LED')
        led_guide_btn = wx.Button(self, label='Guide')
        led_guide_btn.Bind(wx.EVT_BUTTON, self.led_guide_click)
        # list ctrl containing leds
        self.led_lst = self.led_list(self, 1)
        self.led_lst.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.led_lst.doubleclick)
        # LED button bar
        new_led_btn = wx.Button(self, label='Add LED')
        new_led_btn.Bind(wx.EVT_BUTTON, self.new_led_click)
        del_led_btn = wx.Button(self, label='del LED')
        del_led_btn.Bind(wx.EVT_BUTTON, self.del_led_click)
        led_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        led_but_sizer.Add(new_led_btn, 1,wx.ALL, 5)
        led_but_sizer.Add(del_led_btn, 1,wx.ALL, 5)


        # led dialog box
        #      - set gpio
        #      - test led
        #      - make cmd for copypaste / trigger
        #             - set mode, if manual slso blink time on and off
        #             - auto include name of led

        led_sizer = wx.BoxSizer(wx.VERTICAL)
        led_sizer.Add(led_title, 0,wx.ALL, 5)
        led_sizer.Add(led_guide_btn, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        led_sizer.Add(self.led_lst, 1,wx.ALL, 5)
        led_sizer.Add(led_but_sizer, 1,wx.ALL, 5)


        # Datawall
        datawall_title =  wx.StaticText(self,  label='Datawall')
        datawall_guide_btn = wx.Button(self, label='Guide')
        datawall_guide_btn.Bind(wx.EVT_BUTTON, self.datawall_guide_click)
        # datawall - hdmi
        # datawall - remote upload
        #                 - modular using script
        datawall_sizer = wx.BoxSizer(wx.VERTICAL)
        datawall_sizer.Add(datawall_title, 1,wx.ALL, 5)
        datawall_sizer.Add(datawall_guide_btn, 1,wx.ALL|wx.ALIGN_RIGHT, 5)


        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(led_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(datawall_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)

    def led_guide_click(self, e):
        self.parent.shared_data.show_help('led_help.png')

    def datawall_guide_click(self, e):
        self.parent.shared_data.show_help('datawall_display_help.png')

    def new_led_click(self, e):
        led_dialog.s_name    = ""
        led_dialog.s_loc     = ""
        led_dialog.s_reboot = ""
        led_box = led_dialog(self, self.parent)
        led_box.ShowModal()
        self.led_lst.make_table()

    def del_led_click(self, e):
        print(" Sorry, deleting LEDs isn't coded yet.")

    class led_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, size=(800, 150), style=wx.LC_REPORT)
            self.InsertColumn(0, 'Unique Name')
            self.InsertColumn(1, 'GPIO pin')
            self.InsertColumn(2, 'set on reboot')
            self.InsertColumn(3, 'status')
            self.autosizeme()

        def make_table(self):
            config_dict = self.parent.parent.shared_data.config_dict
            led_list = []
            print("  - Using config_dict to fill led table")
            self.DeleteAllItems()
            # Create a list of items
            for key, value in list(config_dict.items()):
                if "led_" in key:
                    name = key.split("_")[1]
                    if not name in led_list:
                        led_list.append(name)

            blinking = self.find_running_blink()
            for name in led_list:
                loc, reboot = self.read_conf(name, config_dict, "led_")
                self.add_to_relay_table(name, loc, reboot, blinking)

            self.autosizeme()

        def read_conf(self, item_name, config_dict, prefix):
            # Extracting config info from config dictionary
            field_list = ["_loc",
                          "_reboot"]
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

        def add_to_relay_table(self, name, loc, reboot, blinking):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(loc))
            self.SetItem(0, 2, str(reboot))
            status = self.get_led_status(name, blinking)
            self.SetItem(0, 3, str(status))

        def get_led_status(self, name, blinking):
            modes = {'500':'blink',
                     '1000':'slow',
                     '100':'fast',
                     '250:1000':'dash'}
            for item in blinking:
                if item[0] == name:
                    if item[1] in modes:
                        return modes[item[1]]
                    else:
                        return item[1]

            return "not blinking"

        def find_running_blink(self):
            """
            Find all running blink_led.py processes (old & new shebangs) and return
            a list of [name, speed] pairs for those matching name=<...> and speed=<...>.
            """
            blink_path = (
                    self.parent.parent.shared_data.remote_pigrow_path
                    + "scripts/persistent/blink_led.py"
            )

            # 1) Try the old-style lookup
            out, error = self.parent.parent.link_pnl.run_on_pi(
                f"pidof -x {blink_path}"
            )
            pid_text = out.strip()

            # 2) Fallback to pgrep -f if nothing found
            if not pid_text:
                out2, err2 = self.parent.parent.link_pnl.run_on_pi(
                    f"pgrep -f {blink_path}"
                )
                pid_text = out2.strip()

            # No blink process at all?
            if not pid_text:
                return []

            # Split into individual PIDs
            pids = pid_text.split()

            blink_names = []
            for pid in pids:
                ps_out, ps_err = self.parent.parent.link_pnl.run_on_pi(
                    f"ps -fp {pid}"
                )
                line = ps_out.strip() + " "

                # extract name=<...> and speed=<...>
                if "name=" in line:
                    name = line.split("name=")[1].split(" ")[0]
                    speed = None
                    if "speed=" in line:
                        speed = line.split("speed=")[1].split(" ")[0]
                    # only append if we have both name and speed
                    blink_names.append([name, speed or ""])
            return blink_names

        def doubleclick(self, e):
            index =  e.GetIndex()
            #get info for dialogue box
            led_dialog.s_name    = self.GetItem(index, 0).GetText()
            led_dialog.s_loc     = self.GetItem(index, 1).GetText()
            led_dialog.s_reboot  = self.GetItem(index, 2).GetText()
            led_box = led_dialog(self.parent, self.parent.parent)
            led_box.ShowModal()
            self.make_table()


class led_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(led_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("LED Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        self.SetFont(shared_data.title_font)
        box_label = wx.StaticText(self,  label='LED Config')
        self.SetFont(shared_data.info_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        ## unique name
        name_label = wx.StaticText(self,  label='name')
        self.name_tc = wx.TextCtrl(self, value=self.s_name, size=(200,30))
        self.name_tc.Bind(wx.EVT_TEXT, self.set_blink_cmd)
        name_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        name_sizer.Add(name_label, 0, wx.ALL|wx.EXPAND, 5)
        name_sizer.Add(self.name_tc, 0, wx.ALL|wx.EXPAND, 5)

        ## gpio pin - location
        loc_label = wx.StaticText(self,  label='gpio pin')
        self.loc_tc = wx.TextCtrl(self, value=self.s_loc, size=(200,30))
        self.loc_tc.Bind(wx.EVT_TEXT, self.on_loc_text_changed)
        loc_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        loc_sizer.Add(loc_label, 0, wx.ALL|wx.EXPAND, 5)
        loc_sizer.Add(self.loc_tc, 0, wx.ALL|wx.EXPAND, 5)

        ## persist on reboot
        self.reboot_ckb = wx.CheckBox(self,  label="Persist on reboot")
        self.reboot_ckb.Bind(wx.EVT_CHECKBOX, self.set_save_but)

        if not self.s_reboot.lower() == "false":
            self.reboot_ckb.SetValue(True)
        reboot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        reboot_sizer.Add(self.reboot_ckb, 0, wx.ALL|wx.EXPAND, 5)

        ## Test a blink patten
        opts = ["on", "off", "slow", "blink", "fast", "dash", "time:500:250"]
        self.blink_combo = wx.ComboBox(self, choices=opts, style=wx.CB_DROPDOWN)
        self.blink_combo.Bind(wx.EVT_COMBOBOX, self.set_blink_cmd)

        # Create the button
        self.blink_button = wx.Button(self, label="Test")
        self.blink_button.Bind(wx.EVT_BUTTON, self.on_blink_button)
        if self.s_name == "":
            self.blink_button.Disable()

        test_blink_sizer = wx.BoxSizer(wx.HORIZONTAL)
        test_blink_sizer.Add(self.blink_combo, flag=wx.EXPAND|wx.ALL, border=5)
        test_blink_sizer.Add(self.blink_button, flag=wx.EXPAND|wx.ALL, border=5)

        self.blink_cmd_tc = wx.TextCtrl(self, value="--")

        # buttons_
        self.save_btn = wx.Button(self, label='Save', size=(175, 30))
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_click)
        self.cancel_btn = wx.Button(self, label='Done', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.save_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)

        self.set_blink_cmd()

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(name_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(loc_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(reboot_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(test_blink_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.blink_cmd_tc, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def set_blink_cmd(self, e=""):
        self.set_save_but()
        name = self.name_tc.GetValue()
        mode = self.blink_combo.GetValue()
        if name == "" or mode == "":
            return None

        set_led_path = self.parent.parent.shared_data.remote_pigrow_path + "scripts/triggers/set_led.py"
        cmd = set_led_path + " name=" + name + " set=" + mode
        self.blink_cmd_tc.SetValue(cmd)

    def on_loc_text_changed(self, event):
        if self.loc_tc.GetValue() == self.s_loc:
            if not self.s_name == "":
                self.blink_button.Enable()
        else:
            self.blink_button.Disable()

        self.set_save_but()

    def set_save_but(self, e=""):
        if self.loc_tc.GetValue() == self.s_loc:
            if self.name_tc.GetValue() == self.s_name:
                if str(self.reboot_ckb.GetValue()) == self.s_reboot:
                    self.save_btn.Disable()
                    return None
        self.save_btn.Enable()

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('led_help.png')

    def on_blink_button(self, event):
        name = self.s_name
        mode = self.blink_combo.GetValue()
        set_led_path = self.parent.parent.shared_data.remote_pigrow_path + "scripts/triggers/set_led.py"
        cmd = set_led_path + " name=" + name + " set=" + mode
        print("Testing LED blink pattern: " + cmd)
        self.parent.parent.link_pnl.run_on_pi(cmd, in_background=True)


    def save_click(self, e):
        shared_data = self.parent.parent.shared_data

        n_name   = self.name_tc.GetValue()
        n_loc    = self.loc_tc.GetValue()
        n_reboot = str(self.reboot_ckb.GetValue())

        changed = "yes"
        if self.s_name == n_name:
            if self.s_loc == n_loc:
                if self.s_reboot == n_reboot:
                    changed = None

        if not changed == None:
            name_start = "led_" + n_name
            shared_data.config_dict[name_start + "_loc"] = n_loc
            shared_data.config_dict[name_start + "_reboot"] = n_reboot

            # If name changed delete old entries
            if not n_name == self.s_name and not self.s_name == "":
                name_start = "led_" + self.s_name
                possible_keys = [name_start + "_loc",
                                 name_start + "_reboot"]
                for possible_key in possible_keys:
                    if possible_key in shared_data.config_dict:
                        del shared_data.config_dict[possible_key]

            # save config to pi
            shared_data.update_pigrow_config_file_on_pi()
            self.blink_button.Enable()
            self.s_name = n_name
            self.s_loc = n_loc
            self.s_reboot = n_reboot
            self.save_btn.Disable()

    def OnClose(self, event):
        if self.save_btn.IsEnabled():
            dlg = wx.MessageDialog(self, "Do you want to save the changes before closing?",
                                   "Confirm Exit", wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()
            dlg.Destroy()

            if result == wx.ID_YES:
                self.save_click(None)

        self.Destroy()
