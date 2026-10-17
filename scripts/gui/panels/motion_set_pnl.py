import shlex
import wx

from panels.camera_controls import parse_settings, serialize_settings

class motion_sets_pnl(wx.Panel):
    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        self.label = wx.StaticText(self,  label='Motion Settings')
        self.label.SetFont(shared_data.button_font)
        self.help_btn = wx.Button(self, label='Help')
        self.help_btn.Bind(wx.EVT_BUTTON, self.help_click)
        self.mcf_label = wx.StaticText(self,  label='Motion Config File')
        #self.mcf_label.SetFont(shared_data.button_font)

        # control buttons
        self.make_status_sizer()
        self.control_buttons()
        self.make_capture_settings_ui()

        #conf_default = shared_data.remote_pigrow_path + "config/motion.conf"
        self.generic_settings_dict = {}

    #    self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_settings_sizer(self.generic_settings_dict)
        self.setting_crtl_dict = {}
        self.c_sets_sizer = {}
        self.setting_t_dict = {}

        self.make_sizer()

    def make_capture_settings_ui(self):
        self.conf_path_l = wx.StaticText(self, label='Motion config')
        self.conf_path_tc = wx.TextCtrl(self, value='')
        self.conf_path_tc.SetMinSize((200, -1))
        self.conf_path_tc.SetToolTip('Path to the motion.conf file on the Pi.')
        self.set_m_conf_btn = wx.Button(self, label='Browse…')
        self.set_m_conf_btn.Bind(wx.EVT_BUTTON, self.set_m_conf_click)
        self.log_path_l = wx.StaticText(self, label='Log file')
        self.log_path_tc = wx.TextCtrl(self, value='')
        self.log_path_tc.SetMinSize((200, -1))
        self.log_path_tc.SetToolTip('Optional Motion log file on the Pi. Leave empty to use Motion defaults.')
        self.set_m_log_btn = wx.Button(self, label='Browse…')
        self.set_m_log_btn.Bind(wx.EVT_BUTTON, self.set_m_log_click)
        self.log_lev_l = wx.StaticText(self, label='Log level')
        self.log_lev_tc = wx.ComboBox(self, value='6', choices=[str(level) for level in range(1, 10)])
        self.log_lev_tc.SetToolTip('1: emergency; 2: alert; 3: critical; 4: error; 5: warning; 6: notice; 7: info; 8: debug; 9: all. Used when a log file is set.')
        self.cap_sets_sizer = wx.FlexGridSizer(cols=3, vgap=5, hgap=8)
        self.cap_sets_sizer.AddGrowableCol(1, 1)
        for label, control, button in ((self.conf_path_l, self.conf_path_tc, self.set_m_conf_btn),
                                       (self.log_path_l, self.log_path_tc, self.set_m_log_btn),
                                       (self.log_lev_l, self.log_lev_tc, None)):
            self.cap_sets_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            self.cap_sets_sizer.Add(control, 1, wx.EXPAND)
            if button is None:
                self.cap_sets_sizer.Add((0, 0))
            else:
                self.cap_sets_sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL)
        self._launcher_controls = {'config_path': self.conf_path_tc,
                                   'log_path': self.log_path_tc,
                                   'log_level': self.log_lev_tc}

    def help_click(self, e):
        self.parent.parent.shared_data.show_help('motion_help.png')


    def set_m_conf_click(self, e):
        conf_path = self.conf_path_tc.GetValue()
        if conf_path == "":
            conf_path = self.parent.parent.shared_data.remote_pigrow_path + "config/"
        selected_files, selected_folders = self.parent.parent.link_pnl.select_files_on_pi(create_file=True, default_path=conf_path)
        if not selected_files == []:
            self.conf_path_tc.SetValue(selected_files[0])

    def set_m_log_click(self, e):
        log_path = self.log_path_tc.GetValue()
        if log_path == "":
            log_path = self.parent.parent.shared_data.remote_pigrow_path + "logs/"
        selected_files, selected_folders = self.parent.parent.link_pnl.select_files_on_pi(create_file=True, default_path=log_path)
        if not selected_files == []:
            self.log_path_tc.SetValue(selected_files[0])

    def control_buttons(self):
        self.start_motion_btn = wx.Button(self, label='Start Motion')
        self.start_motion_btn.Bind(wx.EVT_BUTTON, self.start_motion_click)
        self.start_detect_btn = wx.Button(self, label='Start Detection')
        self.start_detect_btn.Bind(wx.EVT_BUTTON, self.start_detect_click)
        self.pause_motion_btn = wx.Button(self, label='Pause Detection')
        self.pause_motion_btn.Bind(wx.EVT_BUTTON, self.pause_motion_click)
        self.quit_motion_btn = wx.Button(self, label='Stop motion')
        self.quit_motion_btn.Bind(wx.EVT_BUTTON, self.quit_motion_click)

        self.start_pause_sizer = wx.WrapSizer(wx.HORIZONTAL)
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
        self.show_motion_config_btn = wx.Button(self, label='Edit saved config')
        self.show_motion_config_btn.Bind(wx.EVT_BUTTON, self.show_motion_config_click)
        self.new_motion_config_btn = wx.Button(self, label='Create config')
        self.new_motion_config_btn.Bind(wx.EVT_BUTTON, self.new_motion_config_click)
        self.reload_motion_config_btn = wx.Button(self, label='Reload config')
        self.reload_motion_config_btn.Bind(wx.EVT_BUTTON, self.reload_motion_config_click)

        self.conf_butt_sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.conf_butt_sizer.Add(self.show_motion_config_btn, 0, wx.ALL, 0)
        self.conf_butt_sizer.Add(self.new_motion_config_btn, 0, wx.ALL, 0)
        self.conf_butt_sizer.Add(self.reload_motion_config_btn, 0, wx.ALL, 0)

        self.get_res_btn = wx.Button(self, label='Show camera resolutions')
        #self.get_res_btn.SetFont(shared_data.button_font)
        self.get_res_btn.Bind(wx.EVT_BUTTON, self.get_resolutions_click)
#        self.get_opts_btn = wx.Button(self, label='get opt list ')
        #self.get_opts_btn.SetFont(shared_data.button_font)
#        self.get_opts_btn.Bind(wx.EVT_BUTTON, self.get_opt_list)

#        self.get_opts_btn.Disable()
        self.get_res_btn.SetToolTip("List available camera resolutions as a reference when editing motion.conf.")

        self.motion_conf_sizer = wx.BoxSizer(wx.VERTICAL)
        self.motion_conf_sizer.Add(self.conf_butt_sizer, 0, wx.ALL, 0)
        self.motion_conf_sizer.Add(self.get_res_btn, 0, wx.ALL, 0)
#        self.motion_conf_sizer.Add(self.get_opts_btn, 0, wx.ALL, 0)


    def make_sizer(self):
        self.make_motion_conf_sizer()
        heading = wx.BoxSizer(wx.HORIZONTAL)
        heading.Add(self.label, 1, wx.ALIGN_CENTER_VERTICAL)
        heading.Add(self.help_btn, 0, wx.LEFT, 8)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(heading, 0, wx.ALL | wx.EXPAND, 6)
        self.main_sizer.Add(self.status_sizer, 0, wx.ALL | wx.EXPAND, 6)
        self.main_sizer.Add(self.start_pause_sizer, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 6)
        self.main_sizer.Add(self.cap_sets_sizer, 0, wx.ALL | wx.EXPAND, 6)
        self.main_sizer.Add(self.mcf_label, 0, wx.LEFT | wx.TOP, 6)
        self.main_sizer.Add(self.motion_conf_sizer, 0, wx.ALL | wx.EXPAND, 6)
        self.SetSizer(self.main_sizer)

    def start_motion_click(self, e):
        rpp = self.parent.parent.shared_data.remote_pigrow_path
        set_loc = self.parent.camconf_path_tc.GetValue()
        cmd = rpp + "scripts/autorun/motion_start.py set=" + set_loc
        #print(" Running command - " + cmd)
        #print(" ")
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        #print("out, error =", out, error)

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

                # IP}:{port}/{camid}/detection/connection
                port = "8080"
                cmd_base = "curl http://localhost:" + port + "/0/"
                cmd = "detection/connection"
                out, error = self.parent.parent.link_pnl.run_on_pi(cmd_base + cmd)
                if out == "":
                    connect_text = ""
                else:
                    #print("!!!!!!!!"+out+"!!!!!!!!!!!")
                    connect_text = self.read_motion_output(out)
                text = text + "\n" + status_text +  "\n" + connect_text
        self.staus.SetLabel(text)
        self.Layout()
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
        '''
        This is a quick and dirty way of stripping the http tags,
        it works on the motion output but will create confused output
        with pretty much anything else.
        '''
        #print (text)
        if "<body>" in text:
            text = text.split("<body>")[1]
        if "</body>" in text:
            text = text.split("</body>")[0]
        if "</b>" in text:
            text = text.split("</b>")[1]
        if "<br>" in text:
            text = text.replace("<br>", "")
        return text.strip()


    def reload_motion_config_click(self, e=""):
        out, error = self.parent.parent.link_pnl.run_on_pi("pidof motion")
        if out.strip() == "":
            print("  - Motion not running")
        else:
            motion_pid = out.strip()
            out, error = self.parent.parent.link_pnl.run_on_pi("kill -s SIGHUP " + motion_pid)

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
            out, error = self.parent.parent.link_pnl.run_on_pi("sudo apt-get install motion --force-yes -y")
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
            out, error = self.parent.parent.link_pnl.run_on_pi("sudo apt-get install motion --force-yes -y")
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
                    version = line.split(":", 1)[1].strip()
            elif "Candidate" in line:
                candidate = line.split(":", 1)[1].strip()
        if version is not None and candidate is not None:
            if version == candidate or candidate == '(none)':
                return 'current'
            return 'updatable'
        return 'unknown'

    # special controls
    def show_motion_config_click(self, e):
        shared_data = self.parent.parent.shared_data
        motion_conf_path = self.conf_path_tc.GetValue().strip()
        if not motion_conf_path:
            wx.MessageBox('Choose a Motion config file first.', 'Motion config', wx.OK | wx.ICON_INFORMATION)
            return
        out, error = self.parent.parent.link_pnl.run_on_pi('cat -- ' + shlex.quote(motion_conf_path))
        if not out and error:
            wx.MessageBox(error, 'Unable to read Motion config', wx.OK | wx.ICON_ERROR)
            return
        dbox = shared_data.scroll_text_dialog(None, out, 'Editing ' + motion_conf_path, True, False)
        dbox.ShowModal()
        out_conf = dbox.text
        if dbox and not dbox.IsBeingDeleted():
            dbox.Destroy()
        if out_conf is not None and out_conf != out:
            question = wx.MessageDialog(self, 'Save changes to config file?', 'Save Changes?', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
            answer = question.ShowModal()
            question.Destroy()
            if answer == wx.ID_OK:
                self.parent.parent.link_pnl.write_textfile_to_pi(out_conf, motion_conf_path)

    def new_motion_config_click(self, e):
        shared_data = self.parent.parent.shared_data
        link = self.parent.parent.link_pnl
        # Use the installed program's template so directives match its version.
        template, error = link.run_on_pi('cat -- /etc/motion/motion.conf')
        if not template:
            wx.MessageBox('Unable to read /etc/motion/motion.conf. Install Motion or choose an existing configuration to edit.\n\n' + error,
                          'Motion config template unavailable', wx.OK | wx.ICON_ERROR)
            return
        dbox = shared_data.scroll_text_dialog(None, template, 'Create Motion config', True, False)
        dbox.ShowModal()
        config = dbox.text
        if dbox and not dbox.IsBeingDeleted():
            dbox.Destroy()
        if config is None:
            return
        default_path = shared_data.remote_pigrow_path + 'config/motion.conf'
        files, folders = link.select_files_on_pi(create_file=True, default_path=default_path)
        if not files:
            return
        path = files[0]
        # The file picker may select an existing file; make the write explicit.
        question = wx.MessageDialog(self, 'Save Motion config to ' + path + '?\nAn existing file at this path will be replaced.',
                                    'Save Motion config?', wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = question.ShowModal()
        question.Destroy()
        if answer == wx.ID_OK:
            link.write_textfile_to_pi(config, path)
            self.conf_path_tc.SetValue(path)

    def get_resolutions_click(self, e):
        camera = self.parent.parent.dict_C_pnl['camera_pnl'].cam_cb.GetValue()
        cmd = 'v4l2-ctl --list-formats-ext'
        if camera.startswith('/dev/video'):
            cmd += ' --device=' + shlex.quote(camera)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        text = out.strip()
        if not text:
            text = 'No camera formats were reported. Check the camera and install v4l-utils on the Pi.\n\n' + error
        dialog = self.parent.parent.shared_data.scroll_text_dialog(None, text, 'Available camera formats', True, True)
        dialog.ShowModal()
        if dialog and not dialog.IsBeingDeleted():
            dialog.Destroy()

    # conf
    def make_conf_text(self, setting_dict):
        def keep_launcher_semantics(values):
            # motion_start.py applies a log level only when a log path is set.
            if not self.log_path_tc.GetValue():
                values.pop('log_level', None)
            return values
        return serialize_settings(self, self._launcher_controls, transforms=keep_launcher_semantics)

    def text_into_ui(self, set_text):
        self.camera_settings_dict = parse_settings(set_text)
        for key, control in self._launcher_controls.items():
            if key in self.camera_settings_dict:
                control.SetValue(self.camera_settings_dict[key])

    #capture
    def take_image(self, settings_file, outpath):
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        port = "8080"
        cmd = "wget http://localhost:" + port + "/0/action/snapshot > /dev/null"
        print(" Taking a picture using ", cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()

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
        return path, combined_output

    def take_default(self, outpath):
        print("Motion does not support taking default images")
        return outpath, "motion", "Motion does not support taking default images"
