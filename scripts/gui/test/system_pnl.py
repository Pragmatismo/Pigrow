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
        print(" NOTE: pigrow gui needs to be restarted for layout changes to take effect")
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
        self.SetSize((650, 800))
        self.SetTitle("Install On Pi")
    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # draw the pannel and text
        pnl = wx.Panel(self)
        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Install Pigrow on Pi')
        self.SetFont(shared_data.sub_title_font)
        sub_title = wx.StaticText(self,  label='Remotely manage pigrow scripts and dependences')
        opti_l = wx.StaticText(self,  label='Install Selection')

        ##  note
        #note = wx.StaticText(self,  label='')

        # initial install buttons
        self.wizard_btn = wx.Button(self, label='Set-up Wizard', size=(175, 30))
        self.wizard_btn.Bind(wx.EVT_BUTTON, self.wizard_click)

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
        #main_sizer.AddStretchSpacer(1)
        #main_sizer.Add(note, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.wizard_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(cat_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(opti_l, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.opti_list, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def wizard_click(self, e):
        # install core components
        to_install = []
        new_install = False
        for item in self.opti_list.full_list:
            if item[2] == "core" and item[3] == "Not Found":
                to_install.append(item)
                if "Pigrow" in item[1]:
                    new_install = True
        print("core dependencies to install;", to_install)

        dlg = InstallProgressDialog(self, to_install)
        if dlg.ShowModal() == wx.ID_CANCEL:
            print("Core components installed")
        dlg.Destroy()

        # make folders
        make_folders = ['~/Pigrow/caps/', '~/Pigrow/graphs/', '~/Pigrow/logs/']
        for folder in make_folders:
            out, error = self.parent.parent.link_pnl.run_on_pi("mkdir " + folder)

        # clear config dict
        if new_install == True:
            self.parent.parent.shared_data.config_dict = {}
        else:
            message = ("Do you want to clear pigrow_config.txt and start with a fresh setup?\n\n"
                   "Warning - this will remove any sensors, gpio devices or similar that have "
                   "already been configured, ensure you have backups of any config files you "
                   "may want to keep.")
            dlg = wx.MessageDialog(self, message, "Clear Config?", wx.YES_NO | wx.ICON_WARNING)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                print("Wants to clear config")
                self.parent.parent.shared_data.config_dict = {}
            else:
                print("Keep existing")
                self.parent.parent.shared_data.read_pigrow_settings_file()
            dlg.Destroy()

        # wizard
        self.name_pigrow()
        self.enable_trigger_watcher()
        self.enable_selflog_script()

    def name_pigrow(self):
        if not 'box_name' in self.parent.parent.shared_data.config_dict:
            self.parent.parent.shared_data.config_dict["box_name"] = "new"
        box_name = self.parent.parent.shared_data.config_dict["box_name"]
        valid_name = False
        while valid_name == False:
            msg = "Select a name for your pigrow."
            msg += "\n\n This will be used to identify your pigrow and to name the local folder in which\n "
            msg += "files from or associated with the pigrow will be stored. \n\n "
            msg += "Ideally choose a simple and descriptive name, like Veg, Flower, Bedroom, or Greenhouse"
            name_box_dbox = wx.TextEntryDialog(self, msg, "Name your Pigrow")
            if name_box_dbox.ShowModal() == wx.ID_OK:
                box_name = name_box_dbox.GetValue()
                if not box_name == "":
                    box_name = box_name.strip().replace(" ", "_")
                    print("not actually setting box name at this time", box_name)
                    self.parent.parent.shared_data.config_dict["box_name"] = box_name
                    self.parent.parent.shared_data.update_pigrow_config_file_on_pi()
                    valid_name = True
                else:
                    w_msg = "You must select a name for your pigrow"
                    dbox = wx.MessageDialog(self, w_msg, "Error", wx.OK | wx.ICON_ERROR)
                    answer = dbox.ShowModal()
                    dbox.Destroy()
            else:
                print ("User decided not to set the box name")
                valid_name = True

        self.parent.parent.link_pnl.set_link_pi_text(True, box_name)
        self.parent.parent.link_pnl.set_shared_info_on_connect(box_name)

    def enable_trigger_watcher(self):
        cron_i_pnl  = self.parent.parent.dict_I_pnl['cron_pnl']
        cron_c_pnl  = self.parent.parent.dict_C_pnl['cron_pnl']
        shared_data = self.parent.parent.shared_data
        # check_for_control_scripts
        control_script = "trigger_watcher.py"
        full_cs_path   = shared_data.remote_pigrow_path + "scripts/autorun/" + control_script

        control_script_exists = cron_c_pnl.check_if_script_in_startup(control_script)

        message = ("trigger_watcher.py\n\n"
                   "When using the pigrow to control devices the script trigger_watcher.py "
                   "must be enabled on boot, this enables the log based triggers and ensures gpio "
                   "devices (such as relay controlled lamps) are reset after a reboot. ")
        dlg = wx.MessageDialog(self, message, "Enable trigger_watcher?", wx.YES_NO | wx.ICON_WARNING)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            print("Adding trigger_watcher.py to cron")
            script_path = shared_data.remote_pigrow_path + "scripts/autorun/trigger_watcher.py"
            startup_list_instance = cron_i_pnl.startup_cron
            cron_c_pnl.add_to_startup_list(startup_list_instance, "new", "True", full_cs_path, cron_extra_args='')
            cron_c_pnl.update_cron_click()

            # test if it's running (it won't be because there's no trigger_watcher)
        else:
            print("not enabling trigger_watcher")
        dlg.Destroy()

    def enable_selflog_script(self):
        selflog_exists     = False
        selflog_adv_exists = False

        # check_for_selflog_script
        cmd = "crontab -l |grep selflog.py"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if "selflog.py" in out:
            if not out.strip().startswith("#"):
                selflog_exists = True
            else:
                selflog_exists = "disabled"

        cmd = "crontab -l |grep selflog_adv.py"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if "selflog_adv.py" in out:
            if not out.strip().startswith("#"):
                selflog_adv_exists = True
            else:
                selflog_adv_exists = "disabled"

        if selflog_exists and selflog_adv_exists:
            print("- warning - selflog and selflog_adv both in cron")
            if selflog_exists == "disabled" and selflog_adv_exists == "disabled":
                print("but both are disabled")
            elif selflog_exists == "disabled":
                print("but only selflog_adv is active")
            elif selflog_adv_exists == "disabled":
                print("but only selflog is active")

        if selflog_exists or selflog_adv_exists:
            print("self logging found in cron")
        else:
            print("no self logging in cron")
            # if not self_log_script add selflog dialogue
            dialog = SelfLogDialog(self, "Selflog")
            dialog.ShowModal()
            dialog.Destroy()

        print("selflog script wizard not written")

    def update_filter(self, event):
        filter_text = self.filter_txt.GetValue()
        self.opti_list.set_filter(filter_text)

    def cat_combo_go(self, e):
        selection = self.cat_cb.GetValue()
        self.opti_list.set_opts(cat=selection)


    def install_click(self, e):
        to_install = []
        for item in self.opti_list.full_list:
            if item[0] == "Y":
                to_install.append(item)
        #
        dlg = InstallProgressDialog(self, to_install)
        if dlg.ShowModal() == wx.ID_CANCEL:
            print("Install finished")
        dlg.Destroy()
        self.Destroy()

    def cancel_click(self, e):
        self.Destroy()

    def is_git_repository_installed(self, name, package, i_path):
        home_dir = self.parent.parent.shared_data.remote_pigrow_path
        home_dir = home_dir.replace("Pigrow/", "")

        if i_path == None or i_path == "":
            print("No install path, installing to home directory")
            i_path = home_dir

        else:
            i_path = home_dir + i_path
        print("install path;", i_path)

        #install_folder = os.path.split(package)[1].replace(".git", "")
        install_folder = package.split("/")[-1].replace(".git", "")
        path = i_path + install_folder

        # check if path existst on remote pi
        cmd = "ls " + path
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print(cmd, ":", out, error)
        if "No such file or directory" in out + error:
            return False

        cmd = "git --git-dir " + path + "/.git/ log"
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
        home_dir = self.parent.parent.shared_data.remote_pigrow_path
        home_dir = home_dir.replace("Pigrow/", "")

        cmd = "ls " + home_dir + import_n
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if "No such file or directory" in out + error:
            return False
        else:
            return True


    def check_installed(self, name, method, package, i_path, test, import_n, opt=False):
        if test == 'git':
            installed = self.is_git_repository_installed(name, package, i_path)
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
            status = "Not Found"
        else:
            to_install = "---"
            status = installed
        return to_install, status

    class opti_listctrl(wx.ListCtrl):
        def __init__(self, parent):
            wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
            #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
            self.InsertColumn(0, "Install", width=75,  format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(1, "Name",    width=200, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(2, "Group",   width=125, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(3, "Status",  width=100, format=wx.LIST_FORMAT_CENTER)
            self.InsertColumn(4, "Method",  width=100, format=wx.LIST_FORMAT_CENTER)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnCheckBox)

            self.full_list, cats = self.find_install_files()
            self.Parent.cat_cb.Set(cats)

        #def OnColClick(self, event):
        #    print("CLICKED")
        #    col = event.GetColumn()
        #    self.SortItems(lambda item1, item2: self.CompareItems(item1, item2, col))
        #    self.DeleteAllItems()
            # read all items in reordered list, create new list and update


        #def CompareItems(self, item1, item2, col):
        #    item1_value = self.GetItem(item1, col).GetText().lower()
        #    item2_value = self.GetItem(item2, col).GetText().lower()
        #    return (item1_value > item2_value) - (item1_value < item2_value)


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
                        install_method = package_name = install_path = test_method = import_name = None
                        for line in lines:
                            if line.startswith('install_method='):
                                install_method = line.split('=', 1)[1].strip()
                            elif line.startswith('package_name='):
                                package_name = line.split('=', 1)[1].strip()
                            elif line.startswith('install_path='):
                                install_path = line.split('=', 1)[1].strip()
                            elif line.startswith('test='):
                                test_method = line.split('=', 1)[1].strip()
                            elif line.startswith('import='):
                                import_name = line.split('=', 1)[1].strip()
                        # Create a list with the required information
                        tidy_subdir = subdir.replace(folder_path, "").replace("/", "").replace("\\", "").strip()
                        if not tidy_subdir in sub_folders and not tidy_subdir == "":
                            sub_folders.append(tidy_subdir)
                        install_file_info = [file_prefix, tidy_subdir, install_method, package_name, install_path, test_method, import_name]
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
                i_path   = item[4]
                test     = item[5]
                import_n = item[6]
                to_install, status = self.Parent.check_installed(name, method, package, i_path, test, import_n, opt=True)
                checked.append([to_install, name, group, status, method, package, import_n, i_path])
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

class SelfLogDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(SelfLogDialog, self).__init__(parent, title=title, size=(500, 350))
        self.parent = parent

        self.InitUI()

    def InitUI(self):

        text = ("The selflog is a simple python script which is called periodically by cron to log "
                "various system conditions including the Raspberry Pi's cpu temperature, it's available "
                "memory and disk space. These logs can be graphed, incorporated into datawalls, "
                "or used to trigger system warnings such a low storage capacity.\n\n"
                "There's also a more detailed version selflog_adv which collects more information, "
                "this can be useful to developers but is probably excessive for general users.")
        label = wx.StaticText(self, label=text, size=(500, 200))

        choices = ['15 min', '30 min', '1 hour', '3 hour']
        self.dropdown = wx.Choice(self, choices=choices)
        self.dropdown.SetSelection(0)

        enable_selflog_button = wx.Button(self, label='Enable selflog')
        enable_selflog_button.Bind(wx.EVT_BUTTON, self.on_enable_selflog)
        enable_selflog_adv_button = wx.Button(self, label='Enable selflog_adv')
        enable_selflog_adv_button.Bind(wx.EVT_BUTTON, self.on_enable_selflog_adv)
        none_button = wx.Button(self, label='None')
        none_button.Bind(wx.EVT_BUTTON, self.on_none)

        # sizers

        time_select = wx.BoxSizer(wx.HORIZONTAL)
        time_select.Add(wx.StaticText(self, label="Record log every:"), flag=wx.RIGHT, border=10)
        time_select.Add(self.dropdown)

        hbox_buttons = wx.BoxSizer(wx.HORIZONTAL)
        hbox_buttons.Add(enable_selflog_button)
        hbox_buttons.Add(enable_selflog_adv_button)
        hbox_buttons.Add(none_button)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(time_select, flag=wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        main_sizer.Add(hbox_buttons, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        self.SetSizer(main_sizer)

    def on_enable_selflog(self, event):
        interval = self.dropdown.GetString(self.dropdown.GetSelection())
        new_cron_num, new_cron_txt = interval.split(" ")
        shared_data = self.parent.parent.parent.shared_data
        script_path = shared_data.remote_pigrow_path + "scripts/cron/selflog.py"
        print(f"Enabling selflog every {interval}")
        cron_i_pnl  = self.parent.parent.parent.dict_I_pnl['cron_pnl']
        cron_i_pnl.edit_repeat_job_by_name(script_path, None, None, new_cron_txt, new_cron_num, use_name=False)
        self.Destroy()

    def on_enable_selflog_adv(self, event):
        interval = self.dropdown.GetString(self.dropdown.GetSelection())
        new_cron_num, new_cron_txt = interval.split(" ")
        shared_data = self.parent.parent.parent.shared_data
        script_path = shared_data.remote_pigrow_path + "scripts/cron/selflog_adv.py"
        print(f"Enabling the adv selflog every {interval}")
        cron_i_pnl  = self.parent.parent.parent.dict_I_pnl['cron_pnl']
        cron_i_pnl.edit_repeat_job_by_name(script_path, None, None, new_cron_txt, new_cron_num, use_name=False)
        self.Destroy()

    def on_none(self, event):
        self.Close()

class InstallProgressDialog(wx.Dialog):
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
        main_sizer.Add(title, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        main_sizer.Add(self.static_text, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        main_sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 10)
        main_sizer.Add(self.cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.SetSizer(main_sizer)
        self.should_continue = True
        self.run_process()

    def make_action_list(self, item_list):
        '''
        item_list contans a list of [to_install,path name, group, status, method, package, import_n, i_path]
        '''
        install_dict = {}
        for item in item_list:
            install_info = [item[1], item[5], item[7], item[4]]
            #              name, package, install_path, method
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

        install_actions = {'pip':self.install_pip,
                           'apt':self.install_apt,
                           'wget':self.install_wget,
                           'git':self.install_git}

        if isinstance(item[1], str):
            if item[1] in set_up_actions:
                set_up_actions[item[1]]()
        else:
            if item[1][3] in install_actions:
                print("Installing", item)
                install_actions[item[1][3]](item[1])

    def install_pip(self, item):
        cmd = "pip install " + item[1]
        print("running;", cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)

    def install_apt(self, item):
        cmd = "sudo apt --yes install " + item[1]
        print("running;", cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)

    def install_wget(self, item):
        package_name = item[1]
        install_path = item[2]

        home_dir = self.parent.parent.parent.shared_data.remote_pigrow_path
        home_dir = home_dir.replace("Pigrow/", "")

        if install_path == None:
            print("No install path, installing to home directory")
            install_path = home_dir
        else:
            install_path = home_dir + install_path
        print("install path;", install_path)

        install_file_name = os.path.split(item[1])[1]
        install_p = install_path + install_file_name

        cmd = "wget " + package_name + " -O " + install_p
        print("running;", cmd)
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)

    def install_git(self, item):
        package_name = item[1]
        install_path = item[2]
        home_dir = self.parent.parent.parent.shared_data.remote_pigrow_path
        home_dir = home_dir.replace("Pigrow/", "")

        if install_path == None:
            print("No install path, installing to home directory")
            install_path = home_dir
        else:
            install_path = home_dir + install_path

        install_folder = os.path.split(package_name)[1].replace(".git", "")
        install_p = install_path + install_folder
        print("install path;", install_p)

        cmd = "git clone " + package_name + " " + install_p
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out, error)


    def setup_pip(self):
        print("setting up pip")
        cmd = "pip install -U pip"
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out,error)

    def setup_apt(self):
        print("setting up apt")
        cmd = "sudo apt update"
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        print(out,error)

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

                wx.CallAfter(self.update_action_text, item[0])
                self.process_item(item)
                wx.CallAfter(self.increment_progress_bar)

            wx.CallAfter(self.update_action_text, "Done")
            wx.CallAfter(self.cancel_button.SetLabel, "Close")
            wx.CallAfter(self.cancel_button.Enable)
        threading.Thread(target=process_items).start()
