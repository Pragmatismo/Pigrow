import wx

class motion_sets_pnl(wx.Panel):
    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        self.label = wx.StaticText(self,  label='Motion Settings')
        self.label.SetFont(shared_data.button_font)
        self.mcf_label = wx.StaticText(self,  label='Motion Config File')
        #self.mcf_label.SetFont(shared_data.button_font)

        # control buttons
        self.make_status_sizer()
        self.control_buttons()

        self.generic_settings_dict = {"config_path"            : ["", ""],
                                      "log_path"               : ["", ""],
                                      "log_level"              : ["6", (1, 9)]}

        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_settings_sizer(self.generic_settings_dict)

        self.make_sizer()

    def control_buttons(self):
        self.start_motion_btn = wx.Button(self, label='Start Motion')
        self.start_motion_btn.Bind(wx.EVT_BUTTON, self.start_motion_click)
        self.start_detect_btn = wx.Button(self, label='Start Detection')
        self.start_detect_btn.Bind(wx.EVT_BUTTON, self.start_detect_click)
        self.pause_motion_btn = wx.Button(self, label='Pause Detection')
        self.pause_motion_btn.Bind(wx.EVT_BUTTON, self.pause_motion_click)
        self.quit_motion_btn = wx.Button(self, label='Stop motion')
        self.quit_motion_btn.Bind(wx.EVT_BUTTON, self.quit_motion_click)

        self.start_pause_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.start_pause_sizer.Add(self.start_motion_btn, 0, wx.ALL, 0)
        self.start_pause_sizer.Add(self.start_detect_btn, 0, wx.ALL, 0)
        self.start_pause_sizer.Add(self.pause_motion_btn, 0, wx.ALL, 0)
        self.start_pause_sizer.Add(self.quit_motion_btn, 0, wx.ALL, 0)


    def make_status_sizer(self):
        self.check_status_btn = wx.Button(self, label='check status')
        self.check_status_btn.Bind(wx.EVT_BUTTON, self.check_status_click)

        self.staus_label = wx.StaticText(self,  label='Motion status:')
        self.staus = wx.StaticText(self,  label='')
        self.status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status_sizer.Add(self.check_status_btn, 0, wx.ALL, 0)
        self.status_sizer.Add(self.staus_label, 0, wx.ALL, 0)
        self.status_sizer.Add(self.staus, 0, wx.ALL, 0)

    def make_motion_conf_sizer(self):
        self.show_motion_config_btn = wx.Button(self, label='Show saved\nmotion config')
        self.show_motion_config_btn.Bind(wx.EVT_BUTTON, self.show_motion_config_click)

        self.get_res_btn = wx.Button(self, label='get resolutions')
        #self.get_res_btn.SetFont(shared_data.button_font)
        self.get_res_btn.Bind(wx.EVT_BUTTON, self.get_resolutions_click)
        self.get_opts_btn = wx.Button(self, label='get opt list ')
        #self.get_opts_btn.SetFont(shared_data.button_font)
        self.get_opts_btn.Bind(wx.EVT_BUTTON, self.get_opt_list)

        self.get_opts_btn.Disable()
        self.get_res_btn.Disable()

        self.motion_conf_sizer = wx.BoxSizer(wx.VERTICAL)
        self.motion_conf_sizer.Add(self.show_motion_config_btn, 0, wx.ALL, 0)
        self.motion_conf_sizer.Add(self.get_res_btn, 0, wx.ALL, 0)
        self.motion_conf_sizer.Add(self.get_opts_btn, 0, wx.ALL, 0)


    def make_sizer(self):
        self.make_motion_conf_sizer()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        self.main_sizer.Add(self.status_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.start_pause_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.c_sets_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.mcf_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        self.main_sizer.Add(self.motion_conf_sizer, 0, wx.ALL, 0)
        self.SetSizer(self.main_sizer)

    def create_settings_sizer(self, settings_dict):
        c_settings_sizer = wx.FlexGridSizer(3, 0, 5)
        settings_dict = {**self.generic_settings_dict, **settings_dict}
        setting_crtl_dict = {}
        setting_t_dict = {}
        for setting in settings_dict.keys():
            label, box, box_t = self.create_ui_element(setting, settings_dict[setting])
            if not label == None:
                setting_crtl_dict[setting] = box
                setting_t_dict[setting] = box_t
                c_settings_sizer.Add(label, 0, wx.TOP|wx.EXPAND|wx.ALIGN_RIGHT, 2)
                c_settings_sizer.Add(box, 0, wx.TOP|wx.EXPAND, 2)
                c_settings_sizer.Add(box_t, 0, wx.TOP|wx.EXPAND, 2)
        return c_settings_sizer, setting_crtl_dict, setting_t_dict

    def create_ui_element(self, setting, vals):
        label     = wx.StaticText(self,  label=setting)
        input_box_t = wx.StaticText(self,  label="")
        if isinstance(vals[1], list):
            input_box = wx.ComboBox(self, choices=vals[1], value=vals[0])
        elif isinstance(vals[1], str):
            input_box = wx.TextCtrl(self, value=vals[0])
        elif isinstance(vals[1], tuple):
            min_val, max_val = vals[1]
            default_val = int(vals[0])
            #print(min_val, max_val, default_val)
            input_box_t = wx.TextCtrl(self, value=str(default_val), style=wx.TE_PROCESS_ENTER)
            input_box_t.SetLabel(setting)
            input_box_t.Bind(wx.EVT_TEXT_ENTER, self.slider_text_change)
            input_box = wx.Slider(self, id=wx.ID_ANY, value=default_val, minValue=int(min_val), maxValue=int(max_val))
            input_box.SetLabel(setting)
            input_box.Bind(wx.EVT_SLIDER, self.slider_move)
        else:
            print (" Error - motion_set create_ui_element - Not set up to undertand ", type(vals[1]), " as options type")
            input_box = wx.TextCtrl(self, value="")
        return label, input_box, input_box_t

    def start_motion_click(self, e):
        rpp = self.parent.parent.shared_data.remote_pigrow_path
        set_loc = self.parent.camconf_path_tc.GetValue()
        cmd = rpp + "/scripts/autorun/motion_start.py set=" + set_loc
        print(" RUNNING - " + cmd)
        print(" ")
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print("out, error =", out, error)

    def start_detect_click(self, e):
        port = "8080"
        cmd_base = "curl http://localhost:" + port + "/0/"
        check_status = self.check_status()
        if "PAUSE" in check_status:
            cmd = "detection/start"
        else:
            cmd = "action/restart"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
        text = self.read_motion_output(out)
        print (text)
        self.check_status_click("e")

    def pause_motion_click(self, e):
        port = "8080"
        cmd_base = "curl http://localhost:" + port + "/0/"
        cmd = "detection/pause"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
        text = self.read_motion_output(out)
        print (text)
        self.check_status_click("e")

    def quit_motion_click(self, e):
        port = "8080"
        cmd_base = "curl http://localhost:" + port + "/0/"
        cmd = "action/quit"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
        text = self.read_motion_output(out)
        print (text)
        self.check_status_click("e")

    # check - installed, running, paused
    def check_status_click(self, e):

        # check if active
        text, installed = self.check_motion_install()
        self.start_motion_btn.Disable()
        self.start_detect_btn.Disable()
        self.pause_motion_btn.Disable()
        self.quit_motion_btn.Disable()
        #
        if installed == True:
            # check if running
            out, error = self.parent.parent.link_pnl.run_on_pi("pidof motion")
            if out.strip() == "":
                running = False
                text = text + "\n" + "motion - Not running"
                self.start_motion_btn.Enable()
            else:
                motion_pid = out.strip()
                running = True
                text = text + "\n" + "motion - Running"
                self.start_detect_btn.Enable()
                self.pause_motion_btn.Enable()
                self.quit_motion_btn.Enable()

            if running == True:
                # {IP}:{port}/{camid}/detection/status
                status_text = self.check_status()


                # IP}:{port}/{camid}/detection/
                port = "8080"
                cmd_base = "curl http://localhost:" + port + "/0/"
                cmd = "detection/connection"
                out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
                if out == "":
                    connect_text = ""
                else:
                    print("!!!!!!!!"+out+"!!!!!!!!!!!")
                    connect_text = self.read_motion_output(out)
                text = text + "\n" + status_text +  "\n" + connect_text
        self.staus.SetLabel(text)
        self.parent.Layout()


    def check_status(self):
        port = "8080"
        cmd_base = "curl http://localhost:" + port + "/0/"
        cmd = "detection/status"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
        if out == "":
            status_text = "HTTP connection not responding"
        else:
            #print("======="+out+"=========")
            status_text = self.read_motion_output(out)
        return status_text

    def read_motion_output(self, text):
        print (text)
        text = text.split("<body>")[1]
        text = text.split("</body>")[0]
        if "</b>" in text:
            text = text.split("</b>")[1]
        if "<br>" in text:
            text = text.replace("<br>", "")
        return text.strip()


    def reread_motion_conf(self):
        #
        #    THIS CODE IS CURRENTLY NOT USED
        #
        out, error = self.parent.parent.link_pnl.run_on_pi("kill -s SIGHUP")

    # install motion functions
    def check_motion_install(self):
        # check for and install
        status = self.check_installed()
        re_check = False
        if status == "none":
            self.install_motion()
            re_check = True
        elif status == "updatable":
            self.update_motion()
            re_check = True
        # re check if installed attempt made
        if re_check == True:
            status = self.check_installed()
        # set label text
        installed = True
        if status == "none":
            text = " Motion - NOT INSTALLED"
            installed = False
        elif status == "updatable":
            text = " Motion - using older version"
        else:
            text = " Motion - installed "
        return text, installed

    def install_motion(self):
        # msg box
        i_msg = "Motion isn't installed on the pigrow, would you like to install it?"
        dbox = wx.MessageDialog(self, i_msg, "install Motion?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("installing Motion on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get install motion --force-yes -y")
            print(out, error)
        else:
            print("installing motion cancelled")

    def update_motion(self):
        # msg box
        i_msg = "motion version installed on the pigrow is an older version than available, would you like to update it?"
        dbox = wx.MessageDialog(self, i_msg, "install motion?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("updating motion on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get install motion --force-yes -y")
            print(out, error)
        else:
            print("updating motion cancelled")

    def check_installed(self):
        cmd = "apt-cache policy motion"
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        version, candidate = None, None
        for line in out.splitlines():
            if "Installed" in line:
                if "(none)" in line:
                    return "none"
                else:
                    version = line.split(":")[1].strip()
            elif "Candidate" in line:
                candidate = line.split(":")[1].strip()
        if not version == None and candidate == None:
            if version == candidate:
                return "current"
            else:
                return "updatable"

    # special controls
    def show_motion_config_click(self, e):
        print("Showing motion config ")
        motion_conf_path = self.setting_crtl_dict['config_path'].GetValue()
        cmd = "cat " + motion_conf_path
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print (out)



    def get_resolutions_click(self, e):
        # Other option if this doesn't work
        #       ffmpeg -f video4linux2 -list_formats all -i /dev/video0
        cmd = 'v4l2-ctl --list-formats-ext'
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if not error == "":
            print ("Error - ", error, "\n")
            print("  Ensure v412-crl is installed correctly on the raspberry pi")
            print("              sudo apt-get install v4l-utils")
        res_opts = []
        for line in out.splitlines():
            if "Size:" in line:
                if 'with' in line:
                    res = line.split("-")[1].split("with")[0].strip()
                    if not res in res_opts:
                        res_opts.append(res)
                elif 'x' in line:
                    items = line.split(" ")
                    for item in items:
                        if "x" in item:
                            x, y = item.strip().split("x")
                            if x.isdigit() and y.isdigit():
                                res = item.strip()
                                if not res in res_opts:
                                    res_opts.append(res)

    #    self.setting_crtl_dict['resolution'].Clear()
    #    res_opts.sort(key = lambda x: int(x.split("x")[0]))
    #    self.setting_crtl_dict['resolution'].Append(res_opts)




    def make_line_dict(self, line):
        line_opts = line.strip().split(":")[1].split(" ")
        line_dict = {}
        for item in line_opts:
            if "=" in item:
                key, value = item.strip().split("=")
                line_dict[key]=value
        return line_dict

    def get_opt_list(self, e):
        print("Getting opt list")
        opt_list = []
        #
        cmd = 'v4l2-ctl --list-ctrls-menus'
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if not error.strip() == "":
            print ("Error - ", error, "\n")
            print("  Ensure v412-crl is installed correctly on the raspberry pi")
            print("              sudo apt-get install v4l-utils")
        lines = out.splitlines()
        new_sets_dict = {}
        for i in range(0, len(lines)-1):
            if ":" in lines[i] and "=" in lines[i]:
                crtl_name = lines[i].strip().split(" ")[0]
                line_dict = self.make_line_dict(lines[i])
                if "(int)" in lines[i]:
                    if "min" in line_dict and "max" in line_dict and "value" in line_dict:
                        # add new control to dict for sliders - a list containing the current value and a tuple of min and max
                        new_sets_dict[crtl_name] = [ line_dict['value'], (int(line_dict['min']), int(line_dict['max'])) ]
                elif "(bool)" in lines[i]:
                    if "value" in line_dict:
                        val = line_dict['value']
                        if val == "0":
                            val = "False"
                        else:
                            val = "True"
                        new_sets_dict[crtl_name] = [ val, ["True", "False"] ]
                    else:
                        new_sets_dict[crtl_name] = [ "", ["True", "False"] ]
                elif "(menu)" in lines[i] or "(intmenu)" in lines[i]:
                    menu_list = []
                    for ii in range( i+1, i+int(line_dict['max'])+2 ):
                        if not ii > len(lines)-1:
                            if ":" in lines[ii]:
                                line = lines[ii].strip().split(":")
                                if line[0].isdigit():
                                    menu_list.append(line[1])
                        new_sets_dict[crtl_name] = [ '', menu_list ]
        #print (new_sets_dict)
        self.c_sets_sizer.Clear(True)
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_settings_sizer(new_sets_dict)
        self.make_sizer()
        C_pnl = self.parent.parent.dict_C_pnl['camera_pnl']
        C_pnl.camcap_combo_go("e")
        self.parent.SetupScrolling()
        self.parent.Layout()

        #

    # controls
    def slider_move(self, e):
        setting_name = e.GetEventObject().GetLabel()
        slider_val = e.GetEventObject().GetValue()
        self.setting_t_dict[setting_name].SetValue(str(slider_val))

    def slider_text_change(self, e):
        setting_name = e.GetEventObject().GetLabel()
        box_val = e.GetEventObject().GetValue()
        self.setting_crtl_dict[setting_name].SetValue(int(box_val))

    # conf
    def make_conf_text(self, setting_dict):
        settings_text = ""
        for item in setting_dict.keys():
            value = str(setting_dict[item].GetValue())
            if not value == "":
                if not item == "resolution":
                    #settings_text += ' --set "' + item + '"="' + str(value) + '"'
                    settings_text += item + "=" + str(value) + '\n'
                else:
                    res = value
        #res_text = "resolution=" + res + "\n"
        #return res_text + settings_text
        return settings_text

    def text_into_ui(self, set_text):
        cam_settings = set_text.splitlines()
        self.camera_settings_dict = {}
        for line in cam_settings:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos+1:]
                self.camera_settings_dict[key] = value
        # put into ui items
        csd = self.camera_settings_dict
        for key in csd.keys():
            if key in self.setting_crtl_dict:
                if type(self.setting_crtl_dict[key]) == wx._core.Slider:
                    self.setting_t_dict[key].SetValue(csd[key])
                    csd[key] = int(csd[key])
                self.setting_crtl_dict[key].SetValue(csd[key])

    #capture

    def take_image(self, settings_file, outpath):
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        port = "8080"
        cmd = "wget http://localhost:" + port + "/0/action/snapshot > /dev/null"
        print(" Taking a picture using ", cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)

        # check for text output listing save location
        if "‘snapshot’ saved [255]" in out:
            print(" NOTE NOTE NOTE - TAKEN THE SNAPSHOP CORRECTLY")
        # determining path of most recent saved image
        motion_save_folder = "/home/pi/images/motion/"
        print(" USING A TOTALLY ARBIRATY SAVE LOCATION WHICH MUST BE FIXED BEFORE RELEASE")
        symlink_path = motion_save_folder + 'lastsnap.jpg'
        cmd = "realpath " + symlink_path
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        path = out.strip()
        # return path
        print(path)
        return path

    def take_default(self, outpath):
        print("Motion does not support taking default images")
