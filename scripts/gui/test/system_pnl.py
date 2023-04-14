import wx
import wx.lib.scrolledpanel as scrolled
import os
import time
import threading

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        # labels
        self.SetFont(shared_data.sub_title_font)
        self.tab_label = wx.StaticText(self,  label='System Config Menu')
        self.pigrow_side_label = wx.StaticText(self,  label='Pigrow Software')
        self.system_side_label = wx.StaticText(self,  label='System')
        self.boot_label = wx.StaticText(self,  label='Boot config')
        self.picam_label = wx.StaticText(self,  label='Picam')

        #buttons
        # info panel refresh info boxes
        self.SetFont(shared_data.button_font)
        self.read_system_btn = wx.Button(self, label='Read System Info')
        self.read_system_btn.Bind(wx.EVT_BUTTON, self.read_system_click)
        # pigrow software install and upgrade buttons
        self.install_pigrow_btn = wx.Button(self, label='pigrow install')
        self.install_pigrow_btn.Bind(wx.EVT_BUTTON, self.install_click)
        self.update_pigrow_btn = wx.Button(self, label='update pigrow')
        self.update_pigrow_btn.Bind(wx.EVT_BUTTON, self.update_pigrow_click)
        # pi power control
        self.reboot_pigrow_btn = wx.Button(self, label='reboot pi')
        self.reboot_pigrow_btn.Bind(wx.EVT_BUTTON, self.reboot_pigrow_click)
        self.shutdown_pi_btn = wx.Button(self, label='shutdown pi')
        self.shutdown_pi_btn.Bind(wx.EVT_BUTTON, self.shutdown_pi_click)
        # run command on pi button
        self.run_cmd_on_pi_btn = wx.Button(self, label='Run Command On Pi')
        self.run_cmd_on_pi_btn.Bind(wx.EVT_BUTTON, self.run_cmd_on_pi_click)
        #edit boot conf file
        self.edit_boot_config_btn = wx.Button(self, label='Edit /boot/config.txt')
        self.edit_boot_config_btn.Bind(wx.EVT_BUTTON, self.edit_boot_config_click)
        # pi gpio overlay control
        self.i2c_baudrate_btn = wx.Button(self, label='i2c baudrate')
        self.i2c_baudrate_btn.Bind(wx.EVT_BUTTON, self.set_i2c_baudrate)
        # w1 config control
        self.edit_1wire_btn = wx.Button(self, label='1wire config')
        self.edit_1wire_btn.Bind(wx.EVT_BUTTON, self.edit_1wire)
        # Enable / Disable Camera
        self.enable_cam_btn = wx.Button(self, label='Enable')
        self.enable_cam_btn.Bind(wx.EVT_BUTTON, self.enable_cam_click)
        self.disable_cam_btn = wx.Button(self, label='Disable')
        self.disable_cam_btn.Bind(wx.EVT_BUTTON, self.disable_cam_click)
        # gui settings
        self.gui_settings_btn = wx.Button(self, label='GUI Settings')
        self.gui_settings_btn.Bind(wx.EVT_BUTTON, self.gui_settings_click)
        self.info_layout_btn = wx.Button(self, label='Set info layout')
        self.info_layout_btn.Bind(wx.EVT_BUTTON, self.info_layout_click)

        # Sizers
        power_sizer = wx.BoxSizer(wx.HORIZONTAL)
        power_sizer.Add(self.reboot_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        power_sizer.Add(self.shutdown_pi_btn, 0, wx.ALL|wx.EXPAND, 3)

        bootconf_sizer = wx.BoxSizer(wx.VERTICAL)
        bootconf_sizer.Add(self.boot_label, 0, wx.ALL|wx.EXPAND, 3)
        bootconf_sizer.Add(self.edit_boot_config_btn, 0, wx.ALL|wx.EXPAND, 3)
        bootconf_sizer.Add(self.i2c_baudrate_btn, 0, wx.ALL|wx.EXPAND, 3)
        bootconf_sizer.Add(self.edit_1wire_btn, 0, wx.ALL|wx.EXPAND, 3)

        picam_sizer = wx.BoxSizer(wx.HORIZONTAL)
        picam_sizer.Add(self.enable_cam_btn, 0, wx.ALL|wx.EXPAND, 3)
        picam_sizer.Add(self.disable_cam_btn, 0, wx.ALL|wx.EXPAND, 3)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.tab_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.read_system_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.pigrow_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.install_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.update_pigrow_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.system_side_label, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(self.run_cmd_on_pi_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(power_sizer, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(bootconf_sizer, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.picam_label, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(picam_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.gui_settings_btn, 0, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(self.info_layout_btn, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def gui_settings_click(self, e):
        dbox = self.parent.shared_data.settings_dialog( self.parent )
        dbox.ShowModal()
        dbox.Destroy()

    def info_layout_click(self, e):
        dbox = info_layout_dialog(self, self.parent)
        dbox.ShowModal()
        dbox.Destroy()

    def enable_cam_click(self, e):
        out, error = self.parent.link_pnl.run_on_pi("sudo raspi-config nonint do_camera 0")
        print("Picam module enabled")
        self.reboot_pigrow_click(None)

    def disable_cam_click(self, e):
        out, error = self.parent.link_pnl.run_on_pi("sudo raspi-config nonint do_camera 1")
        print("Picam module disabled.")

    # 1Wire - ds18b20
    def edit_1wire(self, e):
        edit_1wire_dbox = one_wire_change_pin_dbox(self, self.parent)
        edit_1wire_dbox.ShowModal()

    def update_boot_config(self, config_text):
        question_text = "Are you sure you want to change the pi's /boot/config.txt file?"
        dbox = wx.MessageDialog(self, question_text, "update pigrow /boot/config.txt?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            config_path = '/boot/config.txt'
            self.parent.link_pnl.update_config_file_on_pi(config_text, config_path)
            print(" Written config to " + config_path)

    # I2C
    def set_i2c_baudrate(self, e):
        new_i2c_baudrate = "30000"
        # ask the user what baudrate they want to set
        baud_dbox = wx.TextEntryDialog(self, 'Set i2c baudrate in /boot/config.txt to', 'Change i2c baudrate', new_i2c_baudrate)
        if baud_dbox.ShowModal() == wx.ID_OK:
            new_i2c_baudrate = baud_dbox.GetValue()
        else:
            return "cancelled"
        baud_dbox.Destroy()
        #
        print("changing the i2c baudrate")
        out, error = self.parent.link_pnl.run_on_pi("cat /boot/config.txt")
        raspberry_config = out.splitlines()
        # put it together again chaning settings line
        config_text = ""
        changed = False
        for line in raspberry_config:
            if "dtparam=i2c_baudrate=" in line:
                line = "dtparam=i2c_baudrate=" + new_i2c_baudrate
                print ("i2c set baudrate changing /boot/config.txt line to " + line)
                changed = True
            config_text = config_text + line + "\n"
        if changed == False:
            print("/boot/config.txt did not have 'dtparam=12c_baudrate=' so adding it")
            config_text = config_text + "dtparam=i2c_baudrate=" + new_i2c_baudrate + "\n"
        self.update_boot_config(config_text)

    # power controls
    def reboot_pigrow_click(self, e):
        dbox = wx.MessageDialog(self, "Are you sure you want to reboot the pigrow?", "reboot pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = self.parent.link_pnl.run_on_pi("sudo reboot now")
            self.parent.link_pnl.link_with_pi_btn_click("e")

    def shutdown_pi_click(self, e):
        dbox = wx.MessageDialog(self, "Are you sure you want to shutdown the pi?", "Shutdown Pi?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            out, error = self.parent.link_pnl.run_on_pi("sudo shutdown now")
            self.parent.link_pnl.link_with_pi_btn_click("e")


    # system checks
    #  -- currently not used but does something the info module can't --
    #def get_pi_time_diff(self):
    #    # just asks the pi the data at the same time grabs local datetime
    #    # returns to the user as strings
    #    out, error = self.link_pnl.run_on_pi("date")
    #    local_time = datetime.datetime.now()
    #    local_time_text = local_time.strftime("%a %d %b %X") + " " + str(time.tzname[0]) + " " + local_time.strftime("%Y")
    #    pi_time = out.strip()
    #    return local_time_text, pi_time


    def read_system_click(self, e):
        '''
        Refreshes all info boxes
        '''
        I_pnl = self.parent.dict_I_pnl['system_pnl']
        for key, value in list(I_pnl.info_box_dict.items()):
            I_pnl.read_and_update_info(key, value)

    def install_click(self, e):
        print(" Install is not yet enabled in the test version, use original gui instead")
        install_dbox = install_dialog(self, self.parent)
        install_dbox.ShowModal()
        install_dbox.Destroy()

    def update_pigrow_click(self, e):
        update_dbox = upgrade_pigrow_dialog(self, self.parent, title='Update Pigrow on Raspberry Pi')
        update_dbox.ShowModal()
        update_dbox.Destroy()

    def run_cmd_on_pi_click(self, e):
        msg = 'Input command to run on pi\n\n This will run the command and wait for it to finish before\ngiving results and resuming the gui'
        generic = 'ls ~/Pigrow/'
        run_cmd_dbox = wx.TextEntryDialog(self, msg, "Run command on pi", generic)
        if run_cmd_dbox.ShowModal() == wx.ID_OK:
            cmd_to_run = run_cmd_dbox.GetValue()
        else:
            return "cancelled"
        run_cmd_dbox.Destroy()
        # run command on the pi
        print("Running command; " + str(cmd_to_run))
        out, error = self.parent.link_pnl.run_on_pi(cmd_to_run)
        print(out, error)
        # tell user about it with a dialog boxes
        dbox = self.parent.shared_data.scroll_text_dialog(None, str(out) + str(error), "Output of " + str(cmd_to_run), False)
        dbox.ShowModal()
        dbox.Destroy()

    def edit_boot_config_click(self ,e):
        boot_conf = edit_boot_config_dialog(self, self.parent)
        boot_conf.ShowModal()
        boot_conf.Destroy()

class info_pnl(wx.Panel):
    '''
    #    This displays the system info
    #   controlled by the system ctrl pnl
    '''
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        ## Draw UI elements
        # Tab Title
        self.SetFont(shared_data.title_font)
        title_l = wx.StaticText(self,  label='System Control Panel')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Configure the raspberry pi on which the pigrow code runs')

        # Sizers
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        pnl_lists = shared_data.system_info_layout

        self.info_box_dict = {}
        big_pnl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        big_pnl_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(5, -1), style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)
        for info_list in pnl_lists:
            pnl_sizer = wx.BoxSizer(wx.VERTICAL)
            for item in info_list:
                self.SetFont(shared_data.item_title_font)
                title_box = wx.StaticText(self, label=item.replace("_", " "))
                title_box.Bind(wx.EVT_LEFT_DCLICK, self.doubleclick_pnl)
                self.SetFont(shared_data.info_font)
                info_box = wx.StaticText(self, label=" -- ")
                info_box.Bind(wx.EVT_LEFT_DCLICK, self.doubleclick_pnl)
                self.info_box_dict[item] = info_box
                pnl_sizer.Add(title_box, 0, wx.ALL|wx.EXPAND, 7)
                pnl_sizer.Add(info_box, 0, wx.LEFT|wx.EXPAND, 35)
            big_pnl_sizer.Add(pnl_sizer, 0, wx.ALL, 3)
            big_pnl_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(5, -1), style=wx.LI_VERTICAL), 0, wx.ALL|wx.EXPAND, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(big_pnl_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.Layout()

    def read_info_boxes(self, e=""):
        for key, value in list(self.info_box_dict.items()):
            self.read_and_update_info(key, value)

    def read_and_update_info(self, title, textbox):
        rpp = self.parent.shared_data.remote_pigrow_path
        info_cmd = rpp + "scripts/gui/info_modules/info_" + title + ".py"
        out, error = self.parent.link_pnl.run_on_pi(info_cmd)
        print(info_cmd, out, error, sep="\n")
        textbox.SetLabel(out)
        self.Layout()

    def doubleclick_pnl(self, e):
        print("Double clicked, ")
        eobject  = e.GetEventObject()
        label = eobject.GetLabel()
        label = label.strip().replace(" ", "_")
        print(label)
        if label in self.info_box_dict:
            self.read_and_update_info(label, self.info_box_dict[label])
        else:
            for item in self.info_box_dict:
                if self.info_box_dict[item] == eobject:
                    item = item.strip().replace(" ", "_")
                    if item in self.info_box_dict:
                        self.read_and_update_info(item, self.info_box_dict[item])


# Dialogue boxs

class edit_boot_config_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(edit_boot_config_dialog, self).__init__(*args, **kw)
        self.parent = parent
        self.InitUI(parent)
        self.SetSize((600, 600))
        self.SetTitle("Edit /boot/config.txt")
    def InitUI(self, parent):
        self.boot_config_original, error = parent.parent.link_pnl.run_on_pi("cat /boot/config.txt")
        header_text = "This file is an integral part of the the Raspbery Pi's system\n"
        header_text += " settings loaded here take effect right at the start of the boot procedure\n"
        header_text += " so even minor errors can cause serious problems."
        header_text += "\n Please read the offical documentation carefully; https://www.raspberrypi.org/documentation/configuration/config-txt/ "
        header = wx.StaticText(self, label=header_text)
        self.config_text = wx.TextCtrl(self, -1, self.boot_config_original, size=(800,600), style=wx.TE_MULTILINE)
        post_text = "Changes made won't take effect until you reboot your pi"
        post_text += "\n \nWarning : Mistakes editing this file may cause your Pi to fail to boot"
        post = wx.StaticText(self, label=post_text)
        #
        ok_btn = wx.Button(self, label='OK', size=(175, 30))
        ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        cancel_btn = wx.Button(self, wx.ID_CANCEL)

        # sizers
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer.AddStretchSpacer(1)
        btnsizer.Add(ok_btn, 0, wx.ALL, 5)
        btnsizer.AddStretchSpacer(1)
        btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
        btnsizer.AddStretchSpacer(1)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(self.config_text, 0, wx.EXPAND|wx.ALL, 6)
        main_sizer.Add(post, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 3)
        main_sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)
        self.SetSizerAndFit(main_sizer)

    def ok_click(self, e):
        config_text = self.config_text.GetValue()
        if not config_text == self.boot_config_original:
            self.parent.update_boot_config(config_text)
        self.Destroy()

class one_wire_change_pin_dbox(wx.Dialog):
    '''
    This opens a dialog box whixh allows you to change the gpio pin associated with
    the one wire devices, it only works with lines that include a ,gpiopin= entry and
    should not be called when there are complications in the file such as dtparam=gpiopin=
    being used to change the pin number on a subsiquent line.
    This is designed to work only with lines added by us or the offical raspi_conf tools,
    the button for it should be disabled if any complications are in the files
    '''
    def __init__(self, parent, *args, **kw):
        super(one_wire_change_pin_dbox, self).__init__(*args, **kw)
        self.InitUI(parent)
        self.SetSize((600, 350))
        self.SetTitle("Change 1Wire Overlay Pin")
    def InitUI(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        self.updated_conf = None
        #
        def pin_list_from_info():
            pigrow_path = "/home/" + shared_data.gui_set_dict['username'] + "/Pigrow"
            info_path = pigrow_path + "/scripts/gui/info_modules/info_1wire.py"
            cmd = info_path + " |grep '1wire overlay enabled on'"
            out, error = parent.parent.link_pnl.run_on_pi(cmd)
            pins = []
            if not out == "":
                out = out.split("enabled on")[1].strip().split(" ")[1:]
                for item in out:
                    print (item)
                    item=item.replace(",", "").replace("\n", "")
                    print (item)
                    pins.append(item)
                print(pins)
                return pins
            return []


        # draw the pannel and text
        pnl = wx.Panel(self)

        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Change 1wire Pin')
        self.SetFont(shared_data.sub_title_font)
        sub_text = wx.StaticText(self,  label="Editing the /boot/config.txt file's dtoverlay=w1-gpio,gpiopin= lines")
        # add drop down box with list of 1wire overlay gpio pins
        tochange_gpiopin_l = wx.StaticText(self, label='current 1wire gpio pin -')

        self.pin_list = pin_list_from_info()
        self.tochange_gpiopin_cb = wx.ComboBox(self, choices = self.pin_list, size=(110, 25))
        if len(self.pin_list) > 0:
            self.tochange_gpiopin_cb.SetValue(self.pin_list[0])
        #
        new_gpiopin_l = wx.StaticText(self, label='Change to GPIO pin -')
        self.SetFont(shared_data.button_font)
        self.new_gpiopin_tc = wx.TextCtrl(self, size=(110, 25)) # new number
        self.new_gpiopin_tc.Bind(wx.EVT_TEXT, self.make_config_line)
        line_l = wx.StaticText(self, label="/boot/config/txt line")
        self.line_t = wx.StaticText(self, label="")
        # add remove buttons
        self.add_btn = wx.Button(self, label='Add', size=(175, 30))
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_click)
        self.rem_btn = wx.Button(self, label='Remove', size=(175, 30))
        self.rem_btn.Bind(wx.EVT_BUTTON, self.rem_click)
        self.change_btn = wx.Button(self, label='Change', size=(175, 30))
        self.change_btn.Bind(wx.EVT_BUTTON, self.change_click)
        # ok and cancel Buttons
        self.ok_btn = wx.Button(self, label='OK', size=(175, 30))
        self.ok_btn.Bind(wx.EVT_BUTTON, self.ok_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        # sizers
        old_gpio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        old_gpio_sizer.Add(tochange_gpiopin_l, 0, wx.ALL, 2)
        old_gpio_sizer.Add(self.tochange_gpiopin_cb, 0, wx.ALL, 2)
        new_gpio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        new_gpio_sizer.Add(new_gpiopin_l, 0, wx.ALL, 2)
        new_gpio_sizer.Add(self.new_gpiopin_tc, 0, wx.ALL, 2)
        action_buttons_sizer  = wx.BoxSizer(wx.HORIZONTAL)
        action_buttons_sizer.Add(self.add_btn, 0, wx.ALL, 2)
        action_buttons_sizer.Add(self.rem_btn, 0, wx.ALL, 2)
        action_buttons_sizer.Add(self.change_btn, 0, wx.ALL, 2)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.ok_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_text, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(old_gpio_sizer, 0, wx.ALL, 3)
        main_sizer.Add(new_gpio_sizer, 0, wx.ALL, 3)
        main_sizer.Add(action_buttons_sizer, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(line_l, 0, wx.ALL, 3)
        main_sizer.Add(self.line_t, 0, wx.ALL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def make_config_line(self, e):
        gpiopin = self.new_gpiopin_tc.GetValue()
        # check pin valid and disable ok button if not, maybe paint box red
        self.line_t.SetLabel("dtoverlay=w1-gpio,gpiopin=" + gpiopin + "\n")
    #    if is_a_valid_and_free_gpio(gpiopin):
    # add this function to shared_data or core tools
        if True:
            print(" Not checking validity of gpio pin, need code added to shared_data")
            self.line_t.SetBackgroundColour((250,250,250))
            self.ok_btn.Enable()
        else:
            self.line_t.SetBackgroundColour((230, 100, 100))
            self.ok_btn.Disable()

    def make_old_line(self):
        old_pin =  self.tochange_gpiopin_cb.GetValue()
        old_line = "dtoverlay=w1-gpio,gpiopin=" + old_pin
        if old_pin == "default (4)":
            old_line = "dtoverlay=w1-gpio"
        return old_line

    # action buttons
    def add_click(self, e):
        print("adding")
        self.pin_list.append(self.new_gpiopin_tc.GetValue())
        self.modify_config_line("", self.line_t.GetLabel())

    def rem_click(self, e):
        print("removing")
        self.pin_list.remove(self.tochange_gpiopin_cb.GetValue())
        self.modify_config_line(self.make_old_line(), "")

    def change_click(self, e):
        print("changing")
        self.pin_list.remove(self.tochange_gpiopin_cb.GetValue())
        self.pin_list.append(self.new_gpiopin_tc.GetValue())
        self.modify_config_line(self.make_old_line(), self.line_t.GetLabel())

    def modify_config_line(self, old, new):
        #
        out, error = self.parent.parent.link_pnl.run_on_pi("cat /boot/config.txt")
        config_lines = out.splitlines()
        new_config_text = ""
        for line in config_lines:
            if not old == "":
                if old in line:
                    print("--Changing " + line + " to " + new)
                    line = new
            new_config_text = new_config_text + line + "\n"
        # when adding new layout
        if old == "":
                new_config_text = new_config_text + new
        self.updated_conf = new_config_text
        # refresh gui
        self.tochange_gpiopin_cb.Clear()
        self.tochange_gpiopin_cb.Append(self.pin_list)
        if len(self.pin_list) > 0:
            if not self.tochange_gpiopin_cb.GetValue() in self.pin_list:
                self.tochange_gpiopin_cb.SetValue(self.pin_list[0])
        else:
            self.tochange_gpiopin_cb.SetValue("")

    def ok_click(self, e):
        if not self.updated_conf == None:
            self.parent.update_boot_config(self.updated_conf)
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class upgrade_pigrow_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, parent, *args, **kw):
        super(upgrade_pigrow_dialog, self).__init__(*args, **kw)
        self.parent = parent
        self.InitUI()
        self.SetSize((600, 675))
        self.SetTitle("Upgrade Pigrow")
    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # draw the pannel and text
        pnl = wx.Panel(self)
        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Upgrade Pigrow')
        self.SetFont(shared_data.sub_title_font)
        sub_title = wx.StaticText(self,  label='Use Git to update the Pigrow to the newest version.')
        local_l = wx.StaticText(self,  label='Local;')
        repo_l = wx.StaticText(self,  label='Repo;')
        pigrow_status = wx.StaticText(self,  label='Pigrow Status;')

        self.SetFont(shared_data.info_font)
        # get info
        status_text, local_text, remote_text = self.read_changes()
        # changes which have been made locally to tracked files
        local_changes_tc = wx.TextCtrl(self, -1, local_text, size=(500,200), style=wx.TE_MULTILINE)
        # Changes which have been made on the remote repo (i.e. online repo)
        remote_changes_tc = wx.TextCtrl(self, -1, remote_text, size=(500,200), style=wx.TE_MULTILINE)

        # upgrade type
        upgrade_type_tb = wx.StaticText(self,  label=status_text)

        self.SetFont(shared_data.button_font)
        # upgrade and cancel buttons
        self.upgrade_btn = wx.Button(self, label='Upgrade', size=(175, 30))
        self.upgrade_btn.Bind(wx.EVT_BUTTON, self.upgrade_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        #Sizers
        upgrade_type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        upgrade_type_sizer.Add(pigrow_status, 0, wx.ALL, 4)
        upgrade_type_sizer.Add(upgrade_type_tb, 0, wx.ALL, 4)
        local_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_sizer.Add(local_l, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        local_sizer.Add(local_changes_tc, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        remote_sizer = wx.BoxSizer(wx.HORIZONTAL)
        remote_sizer.Add(repo_l, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        remote_sizer.Add(remote_changes_tc, 0, wx.ALIGN_LEFT|wx.ALL, 4)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upgrade_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(upgrade_type_sizer, 0, wx.TOP, 15)
        main_sizer.Add(remote_sizer, 0, wx.TOP, 25)
        main_sizer.Add(local_sizer, 0, wx.TOP, 10)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def read_changes(self):
        pigrow_path = "/home/" + self.parent.parent.shared_data.gui_set_dict['username'] + "/Pigrow"
        info_path = pigrow_path + "/scripts/gui/info_modules/info_git_update.py"
        out, error = self.parent.parent.link_pnl.run_on_pi(info_path)
        print (out, error)
        if "Status;" in out and "Local;" in out and "Remote;" in out:
            status_text = out.split("Status;")[1].split("Remote;")[0].strip()
            remote_text = out.split("Remote;")[1].split("Local;")[0].strip()
            local_text  = out.split("Local;")[1].strip()
        else:
            status_text = "Error"
            remote_text = out
            local_text  = error

        return status_text, local_text, remote_text

    def cancel_click(self, e):
        self.Destroy()

    def upgrade_click(self, e):

        # we could also use "git checkout ." before "git pull" if we want to ignore any changes we've made
        # set do_upgrade flag to true, changes to false if git makes it confusing
        do_upgrade = True
        # check to determine best git merge stratergy
#        update_type = MainApp.system_ctrl_pannel.check_git()
        update_type = "clean"
        if update_type == "clean":
            git_command = "git -C ~/Pigrow/ pull"
        elif update_type == "merge":
            print("WARNING WARNING _ THIS CODE IS VERY MUCH IN THE TESTING PHASE")
            print("if you're doing odd things it's very likely to mess up!")
            #this can cause odd confusions which requires use of 'git rebase'
            #reokace command line question with dialog box
            #question = raw_input("merge using default, ours or theirs?")
            question = "theirs"
            if question == "ours":
                git_command = "git -C ~/Pigrow/ pull --strategy=ours" #if we've changed a file it ignores the remote updated one
            elif question == "theirs":
                #often needs to commit or stash changes before working
                git_command = "git -C ~/Pigrow/ pull -s recursive -X theirs" #removes any changes made locally and replaces file with remote updated one
            elif question == "default":
                git_command = "git -C ~/Pigrow/ pull"
            else:
                print("not an option, calling the whole thing off...")
                do_upgrade = False
        #runs the git pull command using the selected stratergy
        if do_upgrade == True:
            dbox = wx.MessageDialog(self, "Are you sure you want to upgrade this pigrow?", "update pigrow?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = dbox.ShowModal()
            dbox.Destroy()
            #if user said ok then upload file to pi
            if (answer == wx.ID_OK):
                out, error = self.parent.parent.link_pnl.run_on_pi(git_command)
                responce = out.strip()
                print (responce)
                if len(error) > 0:
                    print(('error:' + str(error)))
#                    MainApp.system_info_pannel.sys_pigrow_update.SetLabel("--UPDATE ERROR--\n" + error)
#                else:
#                    MainApp.system_info_pannel.sys_pigrow_update.SetLabel("--UPDATED--")
                self.Destroy()

class info_layout_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, parent, *args, **kw):
        super(info_layout_dialog, self).__init__(*args, **kw)
        self.parent = parent
        self.InitUI()
        self.SetSize((600, 800))
        self.SetTitle("Info Box Layout")
    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # draw the pannel and text
        pnl = wx.Panel(self)
        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Set up info layout')
        self.SetFont(shared_data.sub_title_font)
        sub_title = wx.StaticText(self,  label='Select which info boxes will be displayed')

        # info script selection type
        info_scripts_label = wx.StaticText(self,  label='Info script;')
        opts = self.get_info_box_list()
        self.info_script = wx.ComboBox(self, choices = opts)
        info_cb_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_cb_sizer.Add(info_scripts_label, 0, wx.ALL, 4)
        info_cb_sizer.Add(self.info_script, 0, wx.ALL, 4)
        # info script test
        self.SetFont(shared_data.button_font)

        add_col_btn = wx.Button(self, label='Add Col')
        add_col_btn.Bind(wx.EVT_BUTTON, self.add_col_click)
        up_btn = wx.Button(self, label='Move Up')
        up_btn.Bind(wx.EVT_BUTTON, self.move_up_click)
        down_btn = wx.Button(self, label='Move Down')
        down_btn.Bind(wx.EVT_BUTTON, self.move_down_click)
        pos_butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pos_butt_sizer.Add(add_col_btn, 0, wx.ALL, 4)
        pos_butt_sizer.Add(up_btn, 0, wx.ALL, 4)
        pos_butt_sizer.Add(down_btn, 0, wx.ALL, 4)

        test_script_btn = wx.Button(self, label='Read info', size=(175, 30))
        test_script_btn.Bind(wx.EVT_BUTTON, self.test_script_click)
        add_info_btn = wx.Button(self, label='Add', size=(175, 30))
        add_info_btn.Bind(wx.EVT_BUTTON, self.add_click)
        info_butt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        info_butt_sizer.Add(test_script_btn, 0, wx.ALL, 4)
        info_butt_sizer.Add(add_info_btn, 0, wx.ALL, 4)

        self.info_output = wx.StaticText(self,  label=' -- ')
        info_scripts_sizer = wx.BoxSizer(wx.VERTICAL)
        info_scripts_sizer.Add(info_cb_sizer, 0, wx.ALL, 4)
        info_scripts_sizer.Add(info_butt_sizer, 0, wx.ALL|wx.ALIGN_RIGHT, 4)
        info_scripts_sizer.Add(self.info_output, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 4)

        # layout
        self.scroll_box = self.scroll_area(self)

        # save and cancel buttons
        self.save_btn = wx.Button(self, label='Ok', size=(175, 30))
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.save_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(info_scripts_sizer, 0, wx.TOP, 15)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.scroll_box, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(pos_butt_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def add_col_click(self, e):
        print("wants to add col")
        col = ['-none-']
        self.scroll_box.cols_sizer.Add(self.scroll_box.make_col(col), 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.Layout()

    def move_up_click(self, e):
        info_box = self.info_script.GetValue()
        item_list = self.scroll_box.cols_sizer.GetChildren()
        for item in item_list:
            item = item.GetWindow()
            if item.GetSelectedItemCount() == 1:
                s_index = item.GetFirstSelected()
                item_label = item.GetItem(s_index, 0).GetText()
                if not s_index == -1 and not s_index == 0:
                    item.Select(s_index, on=0)
                    item.InsertItem(s_index -1, item_label)
                    item.Select(s_index - 1, on=1)
                    item.DeleteItem(s_index + 1)

    def move_down_click(self, e):
        info_box = self.info_script.GetValue()
        item_list = self.scroll_box.cols_sizer.GetChildren()
        for item in item_list:
            item = item.GetWindow()
            if item.GetSelectedItemCount() == 1:
                s_index = item.GetFirstSelected()
                item_label = item.GetItem(s_index, 0).GetText()
                if not s_index == -1 and not s_index == item.GetItemCount()-1:
                    item.Select(s_index, on=0)
                    item.InsertItem(s_index + 2, item_label)
                    item.Select(s_index + 2, on=1)
                    item.DeleteItem(s_index)

    def get_info_box_list(self):
        rpp = self.parent.parent.shared_data.remote_pigrow_path
        info_mod_path = rpp + "scripts/gui/info_modules"
        cmd = "ls " + info_mod_path
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        module_list = out.splitlines()
        opts_list = []
        for item in module_list:
            if item[:5] == "info_":
                if item[-3:] == ".py":
                    opts_list.append(item[5:].replace(".py", ""))
        return opts_list

    def test_script_click(self, e):
        label = self.info_script.GetValue()
        if label == "":
            return None
        script = "info_" + label.strip() + ".py"
        print("Reading info script;", script)
        rpp = self.parent.parent.shared_data.remote_pigrow_path
        script_path = rpp + "scripts/gui/info_modules/" + script
        out, error = self.parent.parent.link_pnl.run_on_pi(script_path)
        print(out)
        self.info_output.SetLabel(out.strip())
        self.Layout()

    def add_click(self, e):
        info_box = self.info_script.GetValue()
        item_list = self.scroll_box.cols_sizer.GetChildren()
        for item in item_list:
            item = item.GetWindow()
            if item.GetSelectedItemCount() == 1:
                s_index = item.GetFirstSelected()
                if not s_index == -1:
                    item.InsertItem(s_index+1, info_box)
                    if item.GetItem(0, 0).GetText() == "-none-":
                        item.DeleteItem(0)

    def cancel_click(self, e):
        self.Destroy()

    def save_click(self, e):
        info_box = self.info_script.GetValue()
        item_list = self.scroll_box.cols_sizer.GetChildren()
        cols = []
        for item in item_list:
            col = []
            item = item.GetWindow()
            count = item.GetItemCount()
            for i in range(0, count):
                name = item.GetItem(i, 0).GetText()
                if not name == "-none-" and not name == "":
                    col.append(name)
            if not len(col) == 0:
                cols.append(col)



        #clear existing from gui settings
        i = 0
        while True:
            pnl_key = "syspnl_col_" + str(i)
            if pnl_key in self.parent.parent.shared_data.gui_set_dict:
                del self.parent.parent.shared_data.gui_set_dict[pnl_key]
                i += 1
            else:
                break
        # make and store lists in gui_config
        i = 0
        for col in cols:
            pnl_key = "syspnl_col_" + str(i)
            i += 1
            txt = ""
            for item in col:
                txt += item + ","
            if txt[-1:] == ",":
                txt = txt[:-1]
            self.parent.parent.shared_data.gui_set_dict[pnl_key] = txt
        self.parent.parent.shared_data.save_gui_settings()
        self.Destroy()

    class scroll_area(scrolled.ScrolledPanel):
        def __init__(self, parent):
            self.parent = parent
            scrolled.ScrolledPanel.__init__(self, parent, -1, size=(600,400))

            layout_box_sizer = wx.BoxSizer(wx.VERTICAL)
            self.cols_sizer = self.make_cols_sizer()
            layout_box_sizer.Add(self.cols_sizer, 0, wx.ALIGN_LEFT | wx.ALL, 5)

            self.SetSizer(layout_box_sizer)
            self.SetupScrolling()

        def make_cols_sizer(self):
            layout_list = self.parent.parent.parent.shared_data.system_info_layout
            cols_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
            for col in layout_list:
                cols_box_sizer.Add(self.make_col(col), 0, wx.ALIGN_LEFT | wx.ALL, 5)
            return cols_box_sizer

        def make_col(self, col):
            self.SetFont(self.parent.parent.parent.shared_data.info_font)
            col_lc = self.col_info_list(self, 1)
            #col_lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_col)
            col_lc.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
            col_lc.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.col_got_focus)
            col.reverse()
            for item in col:
                col_lc.InsertItem(0, str(item))
            return col_lc

        def del_item(self, e):
            keycode = e.GetKeyCode()
            if keycode == wx.WXK_DELETE:
                item_list = self.cols_sizer.GetChildren()
                for item in item_list:
                    item = item.GetWindow()
                    print(item.GetSelectedItemCount())
                    if item.GetSelectedItemCount() == 1:
                        focus_index = item.GetFirstSelected()
                        if not focus_index == -1:
                            item.DeleteItem(focus_index)
                            if item.GetItemCount() == 0:
                                item.InsertItem(0, "-none-")


        def col_got_focus(self, e):
            event_object = e.GetEventObject()
            item_list = self.cols_sizer.GetChildren()
            for item in item_list:
                item = item.GetWindow()
                if not item == event_object:
                    focus_index = item.GetFirstSelected()
                    item.Select(focus_index, on=0)

        class col_info_list(wx.ListCtrl):
            def __init__(self, parent, id, pos=(5,10), size=(200,400)):
                wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
                self.InsertColumn(0, '')
                self.SetColumnWidth(0, 200)


class install_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, parent, *args, **kw):
        super(install_dialog, self).__init__(*args, **kw)
        self.parent = parent
        self.InitUI()
        self.SetSize((600, 800))
        self.SetTitle("Install On Pi")
    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # draw the pannel and text
        pnl = wx.Panel(self)
        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Install Pigrow on Pi')
        self.SetFont(shared_data.sub_title_font)
        sub_title = wx.StaticText(self,  label='Remotely manage pigrow scripts and dependences')
        core_l = wx.StaticText(self,  label='Core Dependencies')
        opti_l = wx.StaticText(self,  label='Optional Dependencies')

        #  note
        note = wx.StaticText(self,  label='This feature is not yet coded')

        self.core_list = self.core_listctrl(self)
        self.core_list.add_core()

        # optional install catagory text & drop down
        self.filter_txt = wx.TextCtrl(self, size=(265, 30))
        self.filter_txt.Bind(wx.EVT_TEXT, self.update_filter)

        cat_opts = []
        self.cat_cb = wx.ComboBox(self, choices = cat_opts, size=(265, 30))
        self.cat_cb.Bind(wx.EVT_COMBOBOX, self.cat_combo_go)

        cat_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cat_sizer.Add(self.filter_txt, 0, wx.ALL, 2)
        cat_sizer.Add(self.cat_cb, 0, wx.ALL, 2)

        # optional install list ctrl
        self.opti_list = self.opti_listctrl(self)
        self.opti_list.set_opts()

        # save and cancel buttons
        self.install_btn = wx.Button(self, label='install', size=(175, 30))
        self.install_btn.Bind(wx.EVT_BUTTON, self.install_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.install_btn, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0, wx.ALL, 2)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(note, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(core_l, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.core_list, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(cat_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(opti_l, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.opti_list, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def update_filter(self, event):
        filter_text = self.filter_txt.GetValue()
        self.opti_list.set_filter(filter_text)

    def cat_combo_go(self, e):
        selection = self.cat_cb.GetValue()
        self.opti_list.set_opts(cat=selection)


    def install_click(self, e):
        to_install = []
        core_items = 'not coded core item selection for install list'
        for item in self.opti_list.full_list:
            if item[0] == "Y":
                to_install.append(item)
        #
        #print(" Want's to install;")
        #for item in to_install:
        #    print(item[1])
        print("CORE ITEMS INSTALL IS CURRENTLY NOT CODED FOR THE TEST GUI")
        #
        dlg = InstallProgressDialog(self, to_install)
        if dlg.ShowModal() == wx.ID_CANCEL:
            print("Install finished")
        dlg.Destroy()
        self.Destroy()

    def cancel_click(self, e):
        self.Destroy()

    def is_git_repository_installed(self, name, package):
        username = self.parent.parent.shared_data.gui_set_dict['username']
        path = "/home/" + username + "/" + name + "/"
        # check if path existst on remote pi
        cmd = "ls " + path
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print(cmd, ":", out, error)
        if "No such file or directory" in out + error:
            return False

        cmd = "git --git-dir " + path + ".git/ log"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if "Not a git repository" in out + error:
            return "error, not a git repository"
        return True

    def is_py3_installed(self, import_n):
        if import_n == None:
            return "no install"
        cmd = self.parent.parent.shared_data.remote_pigrow_path
        cmd += "/scripts/build_test/test_py3_module.py module=" + import_n
        print (cmd)

        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)
        if out.strip() == "True":
            return True
        elif out.strip() == "False":
            return False
        else:
            return "error; " + out + error

    def is_apt_installed(self, import_n):
        cmd = "which " + import_n
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if import_n in out:
            return True
        else:
            return False

    def is_file_installed(self, import_n):
        cmd = "ls " + import_n
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if "No such file or directory" in out + error:
            return False
        else:
            return True


    def check_installed(self, name, method, package, test, import_n, opt=False):
        if test == 'git':
            installed = self.is_git_repository_installed(name, package)
        elif test == "import":
            installed = self.is_py3_installed(import_n)
        elif test == "file":
            installed = self.is_file_installed(import_n)
        elif test == "apt":
            installed = self.is_apt_installed(import_n)
        else:
            to_install = ""
            status = "no test"
            return to_install, status

        # set status labels
        if installed == True:
            to_install = ""
            status = "Installed"
        elif installed == False:
            if opt == False:
                to_install = "Y"
            else:
                to_install = ""
            status = "Not Present"
        else:
            to_install = "---"
            status = installed
        return to_install, status


    class core_listctrl(wx.ListCtrl):
        def __init__(self, parent):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, -1, size=(-1,150), style=wx.LC_REPORT | wx.SUNKEN_BORDER)
            self.InsertColumn(0, "Install", width=100,  format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(1, "Name",    width=200, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(2, "Status",  width=150, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(3, "Method",  width=150, format=wx.LIST_FORMAT_CENTER)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCheckBox)

        def add_core(self):
            core_items = [["Pigrow Base", "git", "Pigrow", "it's path", "git", "None"],
                          ["test bad", "git", "testbadfolder", "the path", "git", "None"]]

            core_items.reverse()
            for item in core_items:
                to_install, status = self.parent.check_installed(item[3], item[1], item[2], item[4], item[3])
                self.InsertItem(0, to_install)
                self.SetItem(0, 1, item[0])
                self.SetItem(0, 2, status)
                self.SetItem(0, 3, item[1])

        def OnCheckBox(self, event):
            index = event.GetIndex()
            self.CheckItem(index)

        def CheckItem(self, index):
            check = self.GetItem(index, 0).GetText()
            if check == "":
                self.SetItem(index, 0, "Y")
            elif check == "Y":
                self.SetItem(index, 0, "")

    class opti_listctrl(wx.ListCtrl):
        def __init__(self, parent):
            wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
            self.InsertColumn(0, "Install", width=75,  format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(1, "Name",    width=200, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(2, "Group",   width=125, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(3, "Status",  width=100, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(4, "Method",  width=100, format=wx.LIST_FORMAT_CENTER)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCheckBox)

            self.full_list, cats = self.find_install_files()
            self.Parent.cat_cb.Set(cats)

        def find_install_files(self):
            '''
            This function searches for and processes '_install.txt' files in the 'installer'
            folder and its subdirectories. For each '_install.txt' file, it extracts the file
            prefix (text before '_install.txt'), the install_method, package_name, and import
            values from the file content. It also keeps track of the unique subdirectories
            encountered. The function returns a list of found_install_files, where each entry
            is a list containing the file prefix, subdirectory, install_method, package_name,
            and import value. It also returns a list of unique sub_folders found during the search.
            '''
            folder_path = "installer"
            found_install_files = []
            sub_folders = []
            for subdir, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith('_install.txt'):
                        file_prefix = file[:-12]
                        with open(os.path.join(subdir, file), 'r') as f:
                            file_content = f.read()

                        # read from lines
                        lines = file_content.splitlines()
                        install_method = package_name = test_method = import_name= None
                        for line in lines:
                            if line.startswith('install_method='):
                                install_method = line.split('=', 1)[1].strip()
                            elif line.startswith('package_name='):
                                package_name = line.split('=', 1)[1].strip()
                            elif line.startswith('test='):
                                test_method = line.split('=', 1)[1].strip()
                            elif line.startswith('import='):
                                import_name = line.split('=', 1)[1].strip()
                        # Create a list with the required information
                        tidy_subdir = subdir.replace(folder_path, "").replace("/", "").strip()
                        if not tidy_subdir in sub_folders and not tidy_subdir == "":
                            sub_folders.append(tidy_subdir)
                        install_file_info = [file_prefix, tidy_subdir, install_method, package_name, test_method, import_name]
                        # Append the list to the found_install_files list
                        found_install_files.append(install_file_info)

            checked_install_files = self.check_list_installed(found_install_files)
            return checked_install_files, sub_folders

        def set_filter(self, o_filter):
            self.DeleteAllItems()
            unfiltered = self.opts_items

            if o_filter == "":
                filtered = unfiltered
            else:
                filtered = []
                for item in unfiltered:
                    if o_filter in item[1]:
                        filtered.append(item)
            self.fill_table(filtered)

        def set_opts(self, cat='all'):
            self.opts_items = []
            if cat == 'all':
                self.opts_items = self.full_list
            else:
                for item in self.full_list:
                    if item[2] == cat:
                        self.opts_items.append(item)

            self.opts_items.reverse()
            self.set_filter(self.Parent.filter_txt.GetValue())

        def fill_table(self, items):
            for item in items:

                self.InsertItem(0, item[0]) # Install y/n
                self.SetItem(0, 1, item[1]) # Name
                self.SetItem(0, 2, item[2]) # Group
                self.SetItem(0, 3, item[3]) # Status
                self.SetItem(0, 4, item[4]) # Method

        def check_list_installed(self, found_list):
            checked = []
            for item in found_list:
                name     = item[0]
                group    = item[1]
                method   = item[2]
                package  = item[3]
                test     = item[4]
                import_n = item[5]
                to_install, status = self.Parent.check_installed(name, method, package, test, import_n, opt=True)
                checked.append([to_install, name, group, status, method, package])
            return checked


        def OnCheckBox(self, event):
            index = event.GetIndex()
            self.CheckItem(index)

        def CheckItem(self, index):
            check = self.GetItem(index, 0).GetText()
            name = self.GetItem(index, 1).GetText()
            for item in self.full_list:
                if item[1] == name:
                    if check == "":
                        item[0] = "Y"
                        self.SetItem(index, 0, "Y")

                    elif check == "Y":
                        item[0] = ""
                        self.SetItem(index, 0, "")

class InstallProgressDialog(wx.Dialog):
    '''
    Get's handed a list with [to_install, name, group, status, method, package]
    '''
    def __init__(self, parent, item_list):
        super().__init__(parent, title="Install Progress", size=(500, 350))
        self.parent = parent
        shared_data = self.parent.parent.parent.shared_data

        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Installing')
        self.SetFont(shared_data.sub_title_font)

        self.action_list = self.make_action_list(item_list)

        self.static_text = wx.StaticText(self, label="--")

        self.progress_bar = wx.Gauge(self, range=len(self.action_list), size=(-1, 25))

        self.cancel_button = wx.Button(self, label="Cancel")
        self.cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 10)
        main_sizer.Add(self.static_text, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER, 10)
        main_sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.SetSizer(main_sizer)

        self.should_continue = True
        self.run_process()

    def make_action_list(self, item_list):
        install_dict = {}
        for item in item_list:
            install_info = [item[1], item[5]]
            if not item[4] in install_dict:
                install_dict[item[4]] = [install_info]
            else:
                install_dict[item[4]].append(install_info)

        action_list = []
        for item in install_dict:
            action_list.append(["Preparing " + item, item])
            for install_item in install_dict[item]:
                action_list.append(["Installing " + install_item[0], install_item])

        return action_list


    def process_item(self, item):
        time.sleep(2)
        set_up_actions = {'pip':self.setup_pip,
                          'apt':self.setup_apt}

        if isinstance(item[1], str):
            if item[1] in set_up_actions:
                set_up_actions[item[1]]()
        else:
            print("Pretending to install", item)

    def setup_pip(self):
        print("setting up pip (not really)")
        cmd = "pip install -U pip"

    def setup_apt(self):
        print("setting up apt (not really)")
        cmd = "sudo apt update"

    def on_cancel(self, event):
        if self.cancel_button.GetLabel() == "Close":
            self.Destroy()
        else:
            self.should_continue = False
            print("Cancelling")
            self.cancel_button.Disable()

    def update_action_text(self, label):
        self.static_text.SetLabel(label)

    def increment_progress_bar(self):
        value = self.progress_bar.GetValue()
        self.progress_bar.SetValue(value + 1)

    def run_process(self):
        def process_items():
            for item in self.action_list:
                if not self.should_continue:
                    #self.Destroy()
                    break

                self.process_item(item)
                wx.CallAfter(self.update_action_text, item[0])
                wx.CallAfter(self.increment_progress_bar)

            wx.CallAfter(self.cancel_button.SetLabel, "Close")
            wx.CallAfter(self.cancel_button.Enable)
        threading.Thread(target=process_items).start()


#######

class old_install_dialog(wx.Dialog):
    #Dialog box for installing pigrow software on a raspberry pi remotely
    def __init__(self, *args, **kw):
        super(install_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 800))
        self.SetTitle("Install Pigrow")
    def InitUI(self):
        pnl = wx.Panel(self)
        # Header
        header_title = wx.StaticText(self,  label='Install Pigrow')
        header_sub = wx.StaticText(self,  label='Tool for installing pigrow code and dependencies')
        header_title.SetFont(shared_data.title_font)
        header_sub.SetFont(shared_data.sub_title_font)
        # Installed components
        # Core
        label_core = wx.StaticText(self,  label='Core components;')
        label_core.SetFont(shared_data.sub_title_font)
        self.pigrow_base_check = wx.CheckBox(self,  label='Pigrow base')
        self.pigrow_dirlocs_check = wx.CheckBox(self,  label='Locations File')
        self.config_wiz_check = wx.CheckBox(self,  label='Set-up Wizard')
        self.cron_check = wx.CheckBox(self,  label='python crontab')
        # sensors
        label_sensors = wx.StaticText(self,  label='Sensors;')
        label_sensors.SetFont(shared_data.sub_title_font)
        self.adaDHT_check = wx.CheckBox(self,  label='Adafruit_DHT (old py2)')
        self.ada1115_check = wx.CheckBox(self,  label='Adafruit ADS1115')
        # Camera
        label_camera = wx.StaticText(self,  label='Camera;')
        label_camera.SetFont(shared_data.sub_title_font)
        self.uvccapture_check = wx.CheckBox(self,  label='uvccapture')
        # Visualisation
        label_visualisation = wx.StaticText(self,  label='Visualisation;')
        label_visualisation.SetFont(shared_data.sub_title_font)
        self.matplotlib_check = wx.CheckBox(self,  label='Matplotlib py2')
        self.matplotlib3_check = wx.CheckBox(self,  label='Matplotlib py3')
        self.mpv_check = wx.CheckBox(self,  label='mpv')
        # Networking
        label_networking = wx.StaticText(self,  label='Networking;')
        label_networking.SetFont(shared_data.sub_title_font)
        self.praw_check = wx.CheckBox(self,  label='praw')
        self.sshpass_check = wx.CheckBox(self,  label='sshpass')
        self.pexpect_check = wx.CheckBox(self,  label='pexpect')
        #status text
        self.currently_doing_l = wx.StaticText(self,  label="Currently:")
        self.currently_doing = wx.StaticText(self,  label='...')
        self.progress = wx.StaticText(self,  label='...')
        # right hand side - module list
        self.module_list_l = wx.StaticText(self,  label="Install Modules:")
        self.install_module_list = wx.ListCtrl(self, size=(-1,200), style=wx.LC_REPORT|wx.BORDER_SUNKEN)
        self.install_module_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_install_module_opt)
        self.install_module_list.InsertColumn(0, 'Install')
        self.install_module_list.InsertColumn(1, 'Module')
        self.discover_folder_modules()

        #ok and cancel buttons
        self.start_btn = wx.Button(self, label='Start', size=(175, 30))
        self.start_btn.Bind(wx.EVT_BUTTON, self.start_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)

        # sizers
        header_sizer = wx.BoxSizer(wx.VERTICAL)
        header_sizer.Add(header_title, 0, wx.ALL, 3)
        header_sizer.Add(header_sub, 0, wx.ALL, 3)
        # left hand side - hardcoded install tools
        base_sizer = wx.BoxSizer(wx.VERTICAL)
        base_sizer.Add(label_core, 0, wx.EXPAND|wx.ALL, 3)
        base_sizer.Add(self.pigrow_base_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.pigrow_dirlocs_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.config_wiz_check, 0, wx.EXPAND|wx.LEFT, 30)
        base_sizer.Add(self.cron_check, 0, wx.EXPAND|wx.LEFT, 30)
        sensor_sizer = wx.BoxSizer(wx.VERTICAL)
        sensor_sizer.Add(label_sensors, 0, wx.EXPAND|wx.ALL, 3)
        sensor_sizer.Add(self.adaDHT_check, 0, wx.EXPAND|wx.LEFT, 30)
        sensor_sizer.Add(self.ada1115_check, 0, wx.EXPAND|wx.LEFT, 30)
        camera_sizer = wx.BoxSizer(wx.VERTICAL)
        camera_sizer.Add(label_camera, 0, wx.EXPAND|wx.ALL, 3)
        camera_sizer.Add(self.uvccapture_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer = wx.BoxSizer(wx.VERTICAL)
        visualisation_sizer.Add(label_visualisation, 0, wx.EXPAND|wx.ALL, 3)
        visualisation_sizer.Add(self.matplotlib_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer.Add(self.matplotlib3_check, 0, wx.EXPAND|wx.LEFT, 30)
        visualisation_sizer.Add(self.mpv_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer = wx.BoxSizer(wx.VERTICAL)
        networking_sizer.Add(label_networking, 0, wx.EXPAND|wx.ALL, 3)
        networking_sizer.Add(self.praw_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.sshpass_check, 0, wx.EXPAND|wx.LEFT, 30)
        networking_sizer.Add(self.pexpect_check, 0, wx.EXPAND|wx.LEFT, 30)
        # right hand side - folder modules
        folder_modules_sizer = wx.BoxSizer(wx.VERTICAL)
        folder_modules_sizer.Add(self.module_list_l, 0, wx.EXPAND, 30)
        folder_modules_sizer.Add(self.install_module_list, 0, wx.EXPAND, 30)

        status_text_sizer = wx.BoxSizer(wx.VERTICAL)
        status_text_sizer.Add(self.currently_doing_l, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.currently_doing, 0, wx.EXPAND|wx.ALL, 3)
        status_text_sizer.Add(self.progress, 0, wx.EXPAND|wx.ALL, 3)

        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.start_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)

        left_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        left_bar_sizer.Add(base_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(sensor_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(camera_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(visualisation_sizer, 0, wx.ALL|wx.EXPAND, 2)
        left_bar_sizer.Add(networking_sizer, 0, wx.ALL|wx.EXPAND, 2)
        right_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        right_bar_sizer.Add(folder_modules_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options = wx.BoxSizer(wx.HORIZONTAL)
        middle_options.AddStretchSpacer(1)
        middle_options.Add(left_bar_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options.AddStretchSpacer(1)
        middle_options.Add(right_bar_sizer, 0, wx.ALL|wx.EXPAND, 2)
        middle_options.AddStretchSpacer(1)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(middle_options, 0, wx.ALL|wx.EXPAND, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(status_text_sizer, 0, wx.ALL, 2)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(main_sizer)





        #run initial checks
        wx.GetApp().Yield() #update screen to show changes

        self.check_for_pigrow_base()
        self.check_dirlocs()
        self.check_config()
        self.check_python_dependencies()
        self.check_python3_dependencies()
        wx.GetApp().Yield() #update screen to show changes
        self.check_program_dependencies()
        self.check_module_dependencies()

    def discover_folder_modules(self):
        # Read sensor modules folder and list install presets
        install_modules_files = os.listdir(shared_data.sensor_modules_path)
        label_text = ""
        self.install_module_list.DeleteAllItems()
        index = 0
        for file in install_modules_files:
            if "_install.txt" in file:
                module = file.split("_install")[0]
                self.install_module_list.InsertItem(index, "False")
                self.install_module_list.SetItem(index, 1, module)
                index = index + 1

    def onDoubleClick_install_module_opt(self, e):
        index =  e.GetIndex()
        to_install = self.install_module_list.GetItem(index, 0).GetText()
        module_name = self.install_module_list.GetItem(index, 1).GetText()
        if to_install == "True":
            self.install_module_list.SetItem(index, 0, "False")
        else:
            self.install_module_list.SetItem(index, 0, "True")

    def check_dirlocs(self):
        print(" Checking for existence and validity of dirlocs.txt")
        dirlocs_path = "/home/" + pi_link_pnl.target_user + "/Pigrow/config/dirlocs.txt"
        locs_file, error = self.link_pnl.run_on_pi("cat " + dirlocs_path)
        if not 'No such file or directory' in locs_file:
            locs_file = locs_file.splitlines()
            for line in locs_file:
                if line[0:5] == "path=":
                    listed_path = line.split("path=")[1]
                    if not listed_path == "/home/" + pi_link_pnl.target_user + "/Pigrow/":
                        print("!!! Error in dirlocs, path does not match current path")
                    else:
                        print("   valid path found in dirlocs.txt", line)
                        self.pigrow_dirlocs_check.SetForegroundColour((75,200,75))
                        return True
        self.pigrow_dirlocs_check.SetForegroundColour((200,75,75))
        self.pigrow_dirlocs_check.SetValue(True)
        return False

    def check_for_pigrow_base(self):
        print("Checking for pigrow code on raspberry pi")
        out, error = self.link_pnl.run_on_pi("ls /home/" + pi_link_pnl.target_user + "/Pigrow/")
        print(out, error)
        if not len(out.splitlines()) < 1:
            self.pigrow_base_check.SetForegroundColour((75,200,75))
        else:
            self.pigrow_base_check.SetForegroundColour((255,75,75))
            self.pigrow_base_check.SetValue(True)

    def check_config(self):
        print("Checking config file contains box name")
        if not pi_link_pnl.get_box_name() == None:
            self.config_wiz_check.SetForegroundColour((75,200,75))
        else:
            self.config_wiz_check.SetForegroundColour((255,75,75))
            self.config_wiz_check.SetValue(True)

    def config_wizard(self):
        # set box name
        msg = "Select a name for your pigrow."
        msg += "\n\n This will be used to identify your pigrow and to name the local folder in which\n "
        msg += "files from or associated with the pigrow will be stored. \n\n "
        msg += "Ideally choose a simple and descriptive name, like Veg, Flowering, Bedroom, or Greenhouse"
        pi_link_pnl.boxname = "blank"
        MainApp.config_ctrl_pannel.update_pigrow_setup_pannel_information_click("e")
        valid_name = False
        while valid_name == False:
            name_box_dbox = wx.TextEntryDialog(self, msg, "Name your Pigrow")
            if name_box_dbox.ShowModal() == wx.ID_OK:
                box_name = name_box_dbox.GetValue()
                if not box_name == "":
                    MainApp.config_ctrl_pannel.config_dict["box_name"] = box_name
                    pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
                    MainApp.pi_link_pnl.link_status_text.SetLabel("linked with - " + box_name)
                    MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")
                    valid_name = True
                else:
                    w_msg = "You must select a name for your pigrow"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
            else:
                print ("User decided not to set the box name")
                valid_name = True
        ## Selflog
        self.add_selflog()
        ## Sensors, Relay devices and triggers
        msg = "Configure Sensors, Relay Devices and Triggers\n\n"
        msg += "To control devices you need to add relay devices and sensors, "
        #msg += "The relays are used to control the power to your devices, they turn on the lights, heater and etc."
        msg += "\n\n options to configure relays and sensors during install will be added here soon, for now add and configure them in the pigrow config tab and sensor tab."
        dbox = wx.MessageDialog(self, msg, "Relay Devices", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("wants to config relays and sensors but that feature isn't written yet")

    def set_control_sensor_to_dht22(self):
        #
        #
        # THIS IS NO LONGER USED - remove when modular sensor system adoption is complete.
        #
        #
        # gpio pin
        msg = "Set DHT22 GPIO pin\n\n"
        msg += "Input the GPIO number of which you connected the DHT22 data pin to."
        valid_gpio = False
        while valid_gpio == False:
            dht22_gpio_dbox = wx.TextEntryDialog(self, msg, "DHT22 GPIO")
            if dht22_gpio_dbox.ShowModal() == wx.ID_OK:
                DHT22_GPIO = dht22_gpio_dbox.GetValue()
                if not DHT22_GPIO== "" and DHT22_GPIO.isdigit() == True:
                    MainApp.config_ctrl_pannel.gpio_dict["dht22sensor"] = DHT22_GPIO
                    valid_gpio = True
                else:
                    w_msg = "You must select a valid GPIO number"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
                    if not (answer == wx.ID_OK):
                        print("User cancelled dht22 set up")
                        return "cancelled"
        # log frequency
        msg = "Set log frequency\n\n"
        msg += "Select how frequently to log the dht22 temp and humid data, this also determines how"
        msg += "frequently it will check temperature and humidity values to decide when to turn on and"
        msg += "turn off devices.\n\n"
        msg += "A value between 60 seconds and 1800 seconds (half an hour) is ideal."
        valid_freq = False
        while valid_freq == False:
            dht22_freq_dbox = wx.TextEntryDialog(self, msg, "DHT22 Logging Frequency")
            if dht22_freq_dbox.ShowModal() == wx.ID_OK:
                DHT22_freq = dht22_freq_dbox.GetValue()
                if not DHT22_freq== "" and DHT22_freq.isdigit() == True:
                    MainApp.config_ctrl_pannel.gpio_dict["log_frequency"] = DHT22_freq
                    valid_freq = True
                else:
                    w_msg = "You must input a time in seconds for how often you want to read the control sensor."
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
                    if not (answer == wx.ID_OK):
                        print("User cancelled dht22 set up")
                        return "cancelled"
        # test dht22 and ask user if they want to add to cron
        args = "gpio=" + DHT22_GPIO + " sensor=dht22"
        out, error = self.link_pnl.run_on_pi("/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/build_test/test_dht.py " + args)
        out = out.strip()
        if "temp" in out:
            out = out.split(" ")
            temp = out[0].split("=")[1]
            humid = out[1].split("=")[1]
        elif "failed" in out:
            temp = "failed"
            humid = "failed"
        else:
            temp = "error"
            humid = "error"
        msg = "Control sensor set to dht22 on GPIO pin " + DHT22_GPIO + " reading every " + DHT22_freq + " seconds.\n\n"
        msg += " Sensor readings\n            Temp: " + temp + "\n            Humid: " + humid + "\n\n"
        msg += "You can change these settings and configure switching behaviour in the config dht dialog box found in the Pigrow Setup tab.\n\n"
        cron_dht_exists, cron_dht_enabled, cron_dht_index = self.check_for_control_script(scriptname="checkDHT.py")
        if cron_dht_exists == False:
            msg += "To enable the sensor's logging and device switching the script checkDHT.py must be running on the pigrow, this is called at "
            msg += "start-up by Cron the pi's task scheduling tool."
            msg += "\n\n, Press ok to add checkDHT.py to crons startup list, or cancel to skip this step."
        else:
            msg += "checkDHT.py is already in the start up cron list, possibly from a prior install. "
            if cron_dht_enabled == False:
                msg += " But is currently disabled."
            msg +=  "\n\n Press ok to remove all instances of checkDHT.py from the cron startup list and add it again, "
            msg += "or press cancel to skip this step."
        dbox = wx.MessageDialog(self, msg, "Control Sensor Config", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("Cleaning cron of old checkdht22.py calls...")
            while cron_dht_exists:
                print("Removing " + str(cron_dht_index))
                #cron_list_pnl.startup_cron.DeleteItem(cron_dht_index)
                cron_list_pnl.startup_cron.SetItem(cron_dht_index, 0, "deleted")
                cron_dht_exists, cron_dht_enabled, cron_dht_index = self.check_for_control_script(scriptname="checkDHT.py")
            print("Adding a new checkDHT.py script to cron")
            checkDHT_path = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/scripts/autorun/checkDHT.py"
            cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', "True", checkDHT_path, "", "")
            MainApp.cron_info_pannel.update_cron_click("e")
        # save settings
        MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

    def set_temp_and_humid_ranges(self):
        # Low Temp
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "The control sensor is used to turn on and off climate control devices, at the moment \n"
        msg += "the only option is simple switching which uses threashold values to determine if devices should\n"
        msg += "be turned on or off, but again other options will be added as the pigrow continues to grow.\n"
        msg += "\n All Temperatures are in C, I'll add the option of using american units soon."
        msg += "\n\n Set the low temp, if it falls below this temperature the heater will turn on. "
        valid_temp = False
        while valid_temp == False:
            lowtemp_dbox = wx.TextEntryDialog(self, msg, "Set Low Temp in degrees C", "15")
            if lowtemp_dbox.ShowModal() == wx.ID_OK:
                lowtemp = lowtemp_dbox.GetValue()
                if lowtemp.isdigit():
                    print("Valid Low Temp of - ", lowtemp)
                    valid_temp = True
                else:
                    w_msg = "You must select a temperature in C"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # Low Temp
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "All Temperatures are in C, I'll add the option of using american units soon."
        msg += "\n\n Set the High temp, if it rises above this temperature the cooling system will engage.\n\n"
        msg += "This is generally an extra fan which sucks air out the top of your growspace but can \n"
        msg += "also be an air chiller, an inlet letting colder outside air in or similar."
        valid_temp = False
        while valid_temp == False:
            hightemp_dbox = wx.TextEntryDialog(self, msg, "Set High Temp in degrees C", "25")
            if hightemp_dbox.ShowModal() == wx.ID_OK:
                hightemp = hightemp_dbox.GetValue()
                if hightemp.isdigit():
                    print("Valid High Temp of - ", hightemp)
                    valid_temp = True
                else:
                    w_msg = "You must select a temperature in C"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # low humidity
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "Relative Humidity is measured as a percentage\n\n"
        msg += "Set the Low Humidity threashold, if the humidity falls bellow this point it will\n"
        msg += "turn on the humidifier until the humidity rises above this point again. \n"
        valid_humid = False
        while valid_humid == False:
            lowhum_dbox = wx.TextEntryDialog(self, msg, "Set Low Humidity", "35")
            if lowhum_dbox.ShowModal() == wx.ID_OK:
                lowhum = lowhum_dbox.GetValue()
                lowhum = lowhum.replace("%", "")
                if lowhum.isdigit():
                    print("Valid Low Humidity of - ", lowhum)
                    valid_humid = True
                else:
                    w_msg = "You must input a number for the low humidity value"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        # high humidity
        msg = "Temp and Humid Control Sensor - Value Ranges\n\n"
        msg += "Relative Humidity is measured as a percentage\n\n"
        msg += "Set the High Humidity threashold, if the humidity rises above this point it will\n"
        msg += "turn on the dehumidifier until the humidity falls below this point again. \n"
        valid_humid = False
        while valid_humid == False:
            highhum_dbox = wx.TextEntryDialog(self, msg, "Set High Humidity", "70")
            if highhum_dbox.ShowModal() == wx.ID_OK:
                highhum = highhum_dbox.GetValue()
                highhum = highhum.replace("%", "")
                if highhum.isdigit():
                    print("Valid High Humidity of - ", highhum)
                    valid_humid = True
                else:
                    w_msg = "You must input a number for the high humidity value"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
        print("Completed threashold set-up, saving to pi")
        MainApp.config_ctrl_pannel.config_dict["heater_templow"] = lowtemp
        MainApp.config_ctrl_pannel.config_dict["heater_temphigh"] = hightemp
        MainApp.config_ctrl_pannel.config_dict["humid_low"] = lowhum
        MainApp.config_ctrl_pannel.config_dict["humid_high"] = highhum
        MainApp.config_ctrl_pannel.update_setting_file_on_pi_click("e")

    def check_for_control_script(self, scriptname):
        last_index = cron_list_pnl.startup_cron.GetItemCount()
        script_has_cronjob_already = False
        script_enabled = False
        script_startupcron_index = None
        if not last_index == 0:
            for index in range(0, last_index):
                name = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
                if scriptname in name:
                    if not cron_list_pnl.startup_cron.GetItem(index, 0).GetText() == "deleted":
                        script_enabled = cron_list_pnl.startup_cron.GetItem(index, 1).GetText()
                        script_startupcron_index = index
                        script_has_cronjob_already = True
        return script_has_cronjob_already, script_enabled, script_startupcron_index

    def add_selflog(self):
        msg = "Enable Selflog\n\n"
        msg += "The selflog is a simple python script which is called periodically by cron to log various system \n"
        msg += "conditions including the Raspberry Pi's cpu temperature, it's available memory and disk space."
        msg += "\n\n"
        msg += "These logs can be downloaded and graphed using presets found in the local graphing tools."
        cron_selflog_exists, cron_selflog_enabled, cron_selflog_index = self.check_for_selflog_script()
        if cron_selflog_exists == False:
            msg += "\n\n, Press ok to add selflog.py to cron repeating every fifteen min, or cancel to skip this step."
        else:
            msg += "\n\nselflog.py is already in cron's repeating list, possibly from a prior install. "
            if cron_selflog_enabled == False:
                msg += " But is currently disabled."
            msg +=  "\n\n Press ok to remove all instances of selflog.py from the cron repeating list and add it again, "
            msg += "or press cancel to skip this step."
        dbox = wx.MessageDialog(self, msg, "Self Log Config", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("Cleaning cron of old selflog.py calls...")
            while cron_selflog_exists:
                print("Removing " + str(cron_selflog_index))
                cron_list_pnl.repeat_cron.DeleteItem(cron_selflog_index)
                cron_selflog_exists, cron_selflog_enabled, cron_selflog_index = self.check_for_selflog_script()
            print("Adding a new selflog.py script to cron")
            selflog_path = "/home/" + str(pi_link_pnl.target_user) +  "/Pigrow/scripts/cron/selflog.py"
            cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', "True", "*/15 * * * *", selflog_path, "", "")
            MainApp.cron_info_pannel.update_cron_click("e")

    def check_for_selflog_script(self):
        last_index = cron_list_pnl.repeat_cron.GetItemCount()
        has_cron_got_selflog_already = False
        selflog_enabled = False
        selflog_index = None
        if not last_index == 0:
            for index in range(0, last_index):
                name = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
                if "selflog.py" in name:
                    selflog_enabled = cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()
                    selflog_index = index
                    has_cron_got_selflog_already = True
        return has_cron_got_selflog_already, selflog_enabled, selflog_index

    def install_pigrow(self):
        print(" Cloning git repo onto pi")
        # download pigrow scripts from git
        self.currently_doing.SetLabel("using git to clone (download) pigrow code")
        wx.GetApp().Yield()
        out, error = self.link_pnl.run_on_pi("git clone https://github.com/Pragmatismo/Pigrow ~/Pigrow/")
        print(out, error)
        self.progress_install_bar()

        # create empty folders
        self.currently_doing.SetLabel("creating empty folders")
        out, error = self.link_pnl.run_on_pi("mkdir ~/Pigrow/caps/")
        out, error = self.link_pnl.run_on_pi("mkdir ~/Pigrow/graphs/")
        out, error = self.link_pnl.run_on_pi("mkdir ~/Pigrow/logs/")
        self.progress_install_bar()

    def create_dirlocs_from_template(self):
        print("Creting dirlocs.txt from template")
        self.currently_doing.SetLabel("Creating dirlocs from template")
        # grab template from pi and swap wildcards for username
        dirlocs_template, error = self.link_pnl.run_on_pi("cat ~/Pigrow/config/templates/dirlocs_temp.txt")
        dirlocs_text = dirlocs_template.replace("**", str("/home/" + pi_link_pnl.target_user))
        # Create a local version of dirloc.txt to upload onto pi
        if localfiles_info_pnl.local_path == "":
            localfiles_info_pnl.local_path = os.path.join(MainApp.localfiles_path, str(pi_link_pnl.boxname))
        local_temp_path = os.path.join(localfiles_info_pnl.local_path, "temp")
        local_temp_dirlocs_path =  os.path.join(local_temp_path, "dirlocs.txt")
        #print(local_temp_path)
        #print(local_temp_dirlocs_path)
        if not os.path.isdir(local_temp_path):
            os.makedirs(local_temp_path)
        with open(local_temp_dirlocs_path, "w") as temp_local:
            temp_local.write(dirlocs_text)
        MainApp.localfiles_ctrl_pannel.upload_file_to_folder(local_temp_dirlocs_path, "/home/" + pi_link_pnl.target_user + "/Pigrow/config/dirlocs.txt")
        self.progress_install_bar()
        print(" - uploaded new dirlocs to pigrow config folder")

    def update_pip(self):
        # update pip the python package manager
        print(" - updating pip2")
        self.currently_doing.SetLabel("Updating PIP2 the python2 install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        print(" - install running command; sudo pip2 install -U pip")
        out, error = self.link_pnl.run_on_pi("sudo pip2 install -U pip")
        print (out)

    def install_pip2_package(self, pip2_package):
        pip2_command = "sudo pip2 install " + pip2_package
        self.currently_doing.SetLabel("Using pip2 to install " + pip2_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip2_command)
        out, error = self.link_pnl.run_on_pi(pip2_command)
        print("   -- Finished " + pip2_package + " install attempt;")
        print (out, error)

    def update_pip2_package(self, pip2_package):
        # this is not yet used
        pip2_command = "sudo pip2 install -U"
        self.currently_doing.SetLabel("Upgrading pip2 package " + pip2_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip2_command)
        out, error = self.link_pnl.run_on_pi(pip2_command)
        print("   -- Finished " + pip2_package + " upgrade attempt;")
        print (out, error)

    def update_pip3(self):
        # update pip the python package manager
        print(" - updating pip3")
        self.currently_doing.SetLabel("Updating PIP3 the python3 install manager")
        self.progress.SetLabel("#########~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()
        print(" - install running command; sudo pip3 install -U pip")
        out, error = self.link_pnl.run_on_pi("sudo pip3 install -U pip")
        print (out)

    def install_pip3_package(self, pip3_package):
        pip3_command = "sudo pip3 install " + pip3_package
        self.currently_doing.SetLabel("Using pip3 to install " + pip3_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip3_command)
        out, error = self.link_pnl.run_on_pi(pip3_command)
        print("   -- Finished " + pip3_package + " install attempt;")
        print (out, error)

    def update_pip3_package(self, pip3_package):
        # this is not yet used
        pip3_command = "sudo pip3 install -U"
        self.currently_doing.SetLabel("Upgrading pip3 package " + pip3_package)
        wx.GetApp().Yield()
        print(" - install running command; " + pip3_command)
        out, error = self.link_pnl.run_on_pi(pip3_command)
        print("   -- Finished " + pip3_package + " upgrade attempt;")
        print (out, error)

    def update_apt(self):
        print(" - updating apt")
        self.currently_doing.SetLabel("updating apt the system package manager on the raspberry pi")
        wx.GetApp().Yield()
        out, error = self.link_pnl.run_on_pi("sudo apt-get update --yes")
        print (out, error)

    def install_apt_package(self, apt_package):
        apt_command= "sudo apt-get --yes install " + apt_package
        self.currently_doing.SetLabel("Using apt to install " + apt_package)
        wx.GetApp().Yield()
        print(" - install running command; " + apt_command)
        out, error = self.link_pnl.run_on_pi(apt_command)
        print("   -- Finished " + apt_package + " install attempt;")
        print (out, error)

    def install_wget_package(self, package_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_file_name = os.path.split(package_name)[1]
        install_p = sensor_module_folder + install_file_name
        self.currently_doing.SetLabel("Using wget to download " + package_name)
        command = "wget " + package_name + " -O " + install_p
        print(" - install running command; " + command)
        wx.GetApp().Yield()
        out, error = self.link_pnl.run_on_pi(command)
        print("   -- Finished " + package_name + " install attempt;")
        print(out, error)

    def install_git_package(self, package_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_folder = os.path.split(package_name)[1].replace(".git", "")
        install_p = sensor_module_folder + install_folder
        self.currently_doing.SetLabel("Using git to download " + package_name)
        command = "git clone " + package_name + " " + install_p
        print(" - install running command; " + command)
        wx.GetApp().Yield()
        out, error = self.link_pnl.run_on_pi(command)
        print("   -- Finished " + package_name + " install attempt;")
        print(out, error)

    def check_module_dependencies(self):
        print(" Testing dependencies from install module files")
        for module_index in range(0, self.install_module_list.GetItemCount()):
            module_name = self.install_module_list.GetItem(module_index, 1).GetText()
            module_name = module_name + "_install.txt"
            install_module_path = os.path.join(shared_data.sensor_modules_path, module_name)
            with open(install_module_path, "r") as install_text:
                install_module_file = install_text.read().splitlines()
            install_method = ""
            package_name = ""
            import_name = ""
            for line in install_module_file:
                if "install_method=" in line:
                    install_method = line.split("=")[1]
                elif "package_name=" in line:
                    package_name =  line.split("=")[1]
                elif "import=" in line:
                    import_name =  line.split("=")[1]
            is_installed = False
            if not install_method == "" and not package_name == "":
                if install_method == "pip2":
                    if "True" in self.test_py_module(package_name):
                        is_installed = True
                elif install_method == 'pip3':
                    if not import_name == "":
                        if "True" in self.test_py3_module(import_name):
                            is_installed = True
                    else:
                        if "True" in self.test_py3_module(package_name):
                            is_installed = True
                elif install_method == "apt":
                    is_installed = self.test_apt_package(package_name)
                elif install_method == "wget":
                    is_installed = self.test_wget_file(package_name)
                elif install_method == "git":
                    # The same test procedure as wget
                    is_installed = self.test_git_file(package_name, import_name)

            if is_installed == True:
                self.install_module_list.SetItemTextColour(module_index, wx.Colour(90,180,90))
                print(" -- " + package_name + " is already installed")
            else:
                self.install_module_list.SetItemTextColour(module_index, wx.RED)
                print(" -- " + package_name + " is not installed")


    def test_apt_package(self, package_name):
        out, error = self.link_pnl.run_on_pi("apt-cache policy " + package_name + " |grep Installed")
        if "Installed" in out:
            if not "(none)" in out:
                return True
            else:
                return False
        else:
            return False

    def test_wget_file(self, package_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_file_name = os.path.split(package_name)[1]
        install_p = sensor_module_folder + install_file_name
        out, error = self.link_pnl.run_on_pi("ls " + install_p)
        if install_p == out.strip():
            return True
        else:
            return False

    def test_git_file(self, package_name, import_name):
        sensor_module_folder = "/home/" + pi_link_pnl.target_user + "/Pigrow/scripts/gui/sensor_modules/"
        install_p = sensor_module_folder + import_name
        out, error = self.link_pnl.run_on_pi("ls " + install_p)
        if install_p == out.strip():
            return True
        else:
            return False


    def check_program_dependencies(self):
        program_dependencies = ["sshpass", "uvccapture", "mpv"]
        working_programs = []
        nonworking_programs = []
        for program in program_dependencies:
            out, error = self.link_pnl.run_on_pi("apt-cache policy "+program+" |grep Installed")
            if "Installed" in out:
                if not "(none)" in out:
                    working_programs.append(program)
                else:
                    nonworking_programs.append(program)
            else:
                nonworking_programs.append(program)
        #colour ui
        if "uvccapture" in working_programs:
            self.uvccapture_check.SetForegroundColour((75,200,75))
        else:
            self.uvccapture_check.SetForegroundColour((255,75,75))
            self.uvccapture_check.SetValue(True)
        if "mpv" in working_programs:
            self.mpv_check.SetForegroundColour((75,200,75))
        else:
            self.mpv_check.SetForegroundColour((255,75,75))
            self.mpv_check.SetValue(True)
        if "sshpass" in working_programs:
            self.sshpass_check.SetForegroundColour((75,200,75))
        else:
            self.sshpass_check.SetForegroundColour((255,75,75))
            self.sshpass_check.SetValue(True)

    def check_python3_dependencies(self):
        # Dependencies for ADS1115
        ads1115_working = True
        if "True" in self.test_py3_module("board"):
            print("Adafruit board module installed")
        else:
            ads1115_working = False
            print("Adafruit board module is NOT installed - this is required for the ads1115")
        if "True" in self.test_py3_module("busio"):
            print("Adafruit busio module installed")
        else:
            ads1115_working = False
            print("Adafruit board module is NOT installed - this is required for the ads1115")
        if "True" in self.test_py3_module("adafruit_ads1x15"):
            print("Adafruit ADS1x15 module installed")
        else:
            ads1115_working = False
            print("Adafruit ads1x15 module is NOT installed - this is required for the ads1115")
        if ads1115_working == True:
            self.ada1115_check.SetForegroundColour((75,200,75))
        else:
            self.ada1115_check.SetForegroundColour((255,75,75))
            self.ada1115_check.SetValue(True)
        # Praw - the reddit bot module
        if "True" in self.test_py3_module("praw"):
            self.praw_check.SetForegroundColour((75,200,75))
        else:
            self.praw_check.SetForegroundColour((255,75,75))
            self.praw_check.SetValue(True)
        # matplotlib
        if "True" in self.test_py3_module("matplotlib"):
            self.matplotlib3_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib3_check.SetForegroundColour((255,75,75))
            self.matplotlib3_check.SetValue(True)

    def check_python_dependencies(self):
        python_dependencies = ["matplotlib", "Adafruit_DHT", "pexpect", "crontab"]
        working_modules = []
        nonworking_modules = []
        for module in python_dependencies:
            #print module
            out = self.test_py_module(module)
            if "True" in out:
                working_modules.append(module)
            else:
                nonworking_modules.append(module)
        MainApp.status.write_bar("")
        # colour UI
        if "matplotlib" in working_modules:
            self.matplotlib_check.SetForegroundColour((75,200,75))
        else:
            self.matplotlib_check.SetForegroundColour((255,75,75))
            self.matplotlib_check.SetValue(True)
        wx.GetApp().Yield()
        if "Adafruit_DHT" in working_modules:
            self.adaDHT_check.SetForegroundColour((75,200,75))
        else:
            self.adaDHT_check.SetForegroundColour((255,75,75))
            self.adaDHT_check.SetValue(True)
        if "crontab" in working_modules:
            self.cron_check.SetForegroundColour((75,200,75))
        else:
            self.cron_check.SetForegroundColour((255,75,75))
            self.cron_check.SetValue(True)
        if "pexpect" in working_modules:
            self.pexpect_check.SetForegroundColour((75,200,75))
        else:
            self.pexpect_check.SetForegroundColour((255,75,75))
            self.pexpect_check.SetValue(True)

    def progress_install_bar(self):
        current_label = self.progress.GetLabel()
        extra_hashes = "#" * self.hash_per_item
        pos = current_label.find("~")
        hashes = current_label[:pos]
        tilda = current_label[pos:]
        if len(tilda) > self.hash_per_item:
            tilda = tilda[:-self.hash_per_item]
        else:
            tilda = ""
        hashes = hashes + extra_hashes
        print (current_label, extra_hashes, pos, hashes, tilda)
        self.progress.SetLabel(hashes + tilda)
        #self.currently_doing.SetLabel("-")
        wx.GetApp().Yield()

    def start_click(self, e):
        print("(Upgraded) Install process started;")
        self.progress.SetLabel("#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        wx.GetApp().Yield()


        # hardcoded controlls -
        #                     -  Remove this when these are added to generated list control
        # installed using pip2
        pip2_package_list = []
        if self.pexpect_check.GetValue() == True:
            pip2_package_list.append('pexpect')
        if self.adaDHT_check.GetValue() == True:
            pip2_package_list.append('Adafruit_DHT')

        # installed using pip3
        pip3_package_list = []
        if self.ada1115_check.GetValue() == True:
            #self.install_adafruit_ads1115()
            #pip3_package_list.append('RPI.GPIO')
            #pip3_package_list.append('adafruit-blinka')
            pip3_package_list.append('adafruit-circuitpython-ads1x15')
        if self.praw_check.GetValue() == True:
            #self.install_praw()
            pip3_package_list.append('praw')
        if self.matplotlib3_check.GetValue() == True:
            #self.install_matplotlib3()
            pip3_package_list.append('matplotlib')

        # Dependencies installed using apt
        apt_package_list = []
        if self.uvccapture_check.GetValue() == True:
            #self.install_uvccaptre()
            apt_package_list.append('uvccapture')
        if self.mpv_check.GetValue() == True:
            #self.install_mpv()
            apt_package_list.append('mpv')
        if self.sshpass_check.GetValue() == True:
            #self.install_sshpass()
            apt_package_list.append('sshpass')
        if self.matplotlib_check.GetValue() == True:
            #self.install_python_matplotlib()
            apt_package_list.append('python-matplotlib')
        if self.cron_check.GetValue() == True:
            #self.install_python_crontab()
            apt_package_list.append('python-crontab')
        # Add modular sensors to list from table
        wget_package_list = []
        git_package_list = []
        for module_index in range(0, self.install_module_list.GetItemCount()):
            if self.install_module_list.GetItem(module_index, 0).GetText() == "True":
                module_name = self.install_module_list.GetItem(module_index, 1).GetText()
                module_name = module_name + "_install.txt"
                install_module_path = os.path.join(shared_data.sensor_modules_path, module_name)
                with open(install_module_path, "r") as install_text:
                    install_module_file = install_text.read().splitlines()
                for line in install_module_file:
                    if "install_method=" in line:
                        install_method = line.split("=")[1]
                    if "package_name=" in line:
                        package_name =  line.split("=")[1]
                if not install_method == "" and not package_name == "":
                    if install_method == "pip2":
                        pip2_package_list.append(package_name)
                    elif install_method == 'pip3':
                        pip3_package_list.append(package_name)
                    elif install_method == "apt":
                        apt_package_list.append(package_name)
                    elif install_method == "wget":
                        wget_package_list.append(package_name)
                    elif install_method == "git":
                        git_package_list.append(package_name)

        # counting items for progress bar
        item_count = len(pip3_package_list) + len(pip3_package_list) + len(apt_package_list) + len(wget_package_list) + len(git_package_list)
        if self.pigrow_base_check.GetValue() == True:
            item_count += 1
        if self.pigrow_dirlocs_check.GetValue() == True:
            item_count += 1
        if self.config_wiz_check.GetValue() == True:
            item_count += 1
        total_spaces =  30
        if item_count == 0:
            item_count = 1
        self.hash_per_item = int(total_spaces / item_count)

        # Base installed via Git Clone
        if self.pigrow_base_check.GetValue() == True:
            self.install_pigrow()
            self.progress_install_bar()
        # make dirlocs with pi's username
        if self.pigrow_dirlocs_check.GetValue() == True:
            self.create_dirlocs_from_template()
            self.progress_install_bar()
        # Install packages
        # Cycle through list install all pip2 packages
        if len(pip2_package_list) > 0:
            self.update_pip()
            for pip2_package in pip2_package_list:
                self.install_pip2_package(pip2_package)
                self.progress_install_bar()
        # cycle through and install all pip3 packages
        if len(pip3_package_list) > 0:
            self.update_pip3()
            for pip3_package in pip3_package_list:
                self.install_pip3_package(pip3_package)
                self.progress_install_bar()
        # cycle through all and install all apt packages
        if len(apt_package_list) > 0:
            self.update_apt()
            for apt_package in apt_package_list:
                self.install_apt_package(apt_package)
                self.progress_install_bar()
        # download all files using wget
        for wget_package in wget_package_list:
            self.install_wget_package(wget_package)
            self.progress_install_bar()
        # download all files using git
        for git_package in git_package_list:
            self.install_git_package(git_package)
            self.progress_install_bar()
        # run the setup wizard
        if self.config_wiz_check.GetValue() == True:
            self.currently_doing.SetLabel(" Config Wizard")
            self.progress.SetLabel("##############################~")
            wx.GetApp().Yield()
            self.config_wizard()

        # Announce finished
        print("(Upgraded) Install process finished;")
        self.progress.SetLabel("####### INSTALL COMPLETE ######")
        self.currently_doing.SetLabel(" -- ")
        self.start_btn.Disable()
        self.cancel_btn.SetLabel("OK")
        wx.GetApp().Yield()


    def cancel_click(self, e):
        self.Destroy()

    def test_py_module(self, module):
        msg = "  - Testing; " + module
        MainApp.status.write_bar(msg)
        print(msg)
        module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
        out, error = self.link_pnl.run_on_pi("python -c " + module_question)
        return out

    def test_py3_module(self, module):
        module_question = """\
"try:
    import """ + module + """
    print('True')
except:
    print('False')" """
        out, error = self.link_pnl.run_on_pi("python3 -c " + module_question)
        return out
