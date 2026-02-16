import wx

'''
 other fs webcam settings


    -R, --read
        Use read() to capture images. This can be slower but more stable with some devices.
        Default is to use mmap(), falling back on read() if mmap() is unavailable.

    --no-banner      remove the bottom red/blue bar with date

    --top-banner     Position the banner at the top of the image.

    --banner-colour <#AARRGGBB>
                    Set the colour of the banner. Uses the web-style hexadecimal format (#RRGGBB) to describe the colour, and can support an alpha channel (#AARRGGBB). Examples:
                    "#FF0000" is pure red.

                    "#80000000" is semi-transparent black.

                    "#FF000000" is invisible (alpha channel is at maximum).

                    Default is "#40263A93".

    --line-colour <#AARRGGBB>      Set the colour of the divider line.

    --text-colour <#AARRGGBB>     Set the colour of the text.

    --font <[file or font name]:[font size]>
                            Set the font used in the banner. If no path is specified the path in the
                            GDFONTPATH environment variable is searched for the font. Fontconfig names may
                            also be used if the GD library has support.

    --no-shadow           Disable the text shadow

    --title <text>        Set the main text, located in the top left of the banner.

    --subtitle <text>     Set the sub-title text, located in the bottom left of the banner.

    --timestamp <text>
                        Set the timestamp text, located in the top right of the banner.
                        This string is formatted by strftime.
                            Default is "%Y-%m-%d %H:%M (%Z)".

    --info <text>
                        Set the info text, located in the bottom right of the banner.

    --underlay <filename>
                        Load a PNG image and overlay it on the image, below the banner.
                        The image is aligned to the top left.

    --overlay <filename>
                        Load a PNG image and overlay on the image, above the banner.
                        The image is aligned to the top left.


'''

class fs_sets_pnl(wx.Panel):
    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        self.label = wx.StaticText(self,  label='Fswebcam Settings')
        self.label.SetFont(shared_data.button_font)

        camera_res = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        camera_res = camera_res
        self.generic_settings_dict = {"resolution"            : [camera_res[0], camera_res],
                                 "fs_delay"            : ["2", (0, 15)],
                                 "fs_fskip"            : ["5", (0, 25)],
                                 "fs_jpg_q"            : ["90", (0, 100)],
                                 "fs_banner"           : ["True", ["True", "False"]]
                                 }

        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_settings_sizer(self.generic_settings_dict)
        self.make_sizer()

    def make_sizer(self):
        self.test_btn = wx.Button(self, label='get resolutions')
        #self.test_btn.SetFont(shared_data.button_font)
        self.test_btn.Bind(wx.EVT_BUTTON, self.get_resolutions_click)
        self.testr_btn = wx.Button(self, label='get opt list ')
        #self.testr_btn.SetFont(shared_data.button_font)
        self.testr_btn.Bind(wx.EVT_BUTTON, self.get_opt_list)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        self.main_sizer.Add(self.test_btn, 0, wx.ALL, 0)
        self.main_sizer.Add(self.testr_btn, 0, wx.ALL, 0)
        self.main_sizer.Add(self.c_sets_sizer, 0, wx.ALL, 0)
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
            print (" Error - picam_set create_ui_element - Not set up to undertand ", type(vals[1]), " as options type")
            input_box = wx.TextCtrl(self, value="")
        return label, input_box, input_box_t

    # install fs functions
    def check_fs(self):
        # check for and install
        status = self.check_fs_installed()
        re_check = False
        if status == "none":
            self.install_fswebcam()
            re_check = True
        elif status == "updatable":
            self.update_fswebcam()
            re_check = True
        # re check if installed attempt made
        if re_check == True:
            status = self.check_fs_installed()
        # set label text
        if status == "none":
            text = " Fswebcam - NOT INSTALLED"
        elif status == "updatable":
            text = " Fswebcam - using older version"
        else:
            text = " Fswebcam - installed "
        self.label.SetLabel(text)

    def install_fswebcam(self):
        # msg box
        i_msg = "fswebcam isn't installed on the pigrow, would you like to install it?"
        dbox = wx.MessageDialog(self, i_msg, "install fswebcam?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("installing fswebcam on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get install fswebcam --force-yes -y")
            print(out, error)
        else:
            print("installing fswebcam cancelled")

    def update_fswebcam(self):
        # msg box
        i_msg = "fswebcam version installed on the pigrow is an older version than available, would you like to update it?"
        dbox = wx.MessageDialog(self, i_msg, "install fswebcam?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_OK):
            print("updating fswebcam on pigrow")
            out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("sudo apt-get install fswebcam --force-yes -y")
            print(out, error)
        else:
            print("updating fswebcam cancelled")

    def check_fs_installed(self):
        cmd = "apt-cache policy fswebcam"
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

        self.setting_crtl_dict['resolution'].Clear()
        res_opts.sort(key = lambda x: int(x.split("x")[0]))
        self.setting_crtl_dict['resolution'].Append(res_opts)

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
        res_text = "resolution=" + res + "\n"
        return res_text + settings_text

    def old_make_conf_text(self, setting_dict):
        settings_text = ""
        for item in setting_dict.keys():
            value = str(setting_dict[item].GetValue())
            if not value == "":
                settings_text += item + "=" + value + "\n"
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
        # make changes for old keys
        csd = self.camera_settings_dict
        if "x_dim" in csd and "y_dim" in csd:
            if not "resolution" in csd:
                csd['resolution'] = csd['x_dim'] + "x" + csd['y_dim']
        if "b_val" in csd and not "brightness" in csd:
            csd['brightness'] = csd['b_val']
        if "s_val" in csd and not "saturation" in csd:
            csd['saturation'] = csd['s_val']
        if "c_val" in csd and not "contrast" in csd:
            csd['contrast'] = csd['c_val']
        if "g_val" in csd and not "iso" in csd:
            csd['iso'] = csd['g_val']
        # put into ui items
        for key in csd.keys():
            if key in self.setting_crtl_dict:
                if type(self.setting_crtl_dict[key]) == wx._core.Slider:
                    self.setting_t_dict[key].SetValue(csd[key])
                    csd[key] = int(csd[key])
                self.setting_crtl_dict[key].SetValue(csd[key])

    #capture

    def take_image(self, settings_file, outpath):
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/camcap.py caps=' + outpath + ' set=' + settings_file
        print(" Taking a picture using ", cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        # check for text output listing save location
        if "Saving image to:" in combined_output:
            path = combined_output.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + combined_output
            self.check_fs()
        print(path)
        return path, combined_output

    def take_default(self, outpath):
        print(" Taking default image using fswebcam")
        cam_select = self.parent.parent.dict_C_pnl['camera_pnl'].cam_cb.GetValue()
        cam_cmd  = "fswebcam -r " + self.setting_crtl_dict['resolution'].GetValue()
        if not cam_select == "":
            cam_cmd += " --device=" + cam_select
        cam_cmd += " -D 2"      #the delay in seconds before taking photo
        cam_cmd += " -S 5"      #number of frames to skip before taking image
        cam_cmd += " --jpeg 90" #jpeg quality
        cam_cmd += " " + outpath  #output filename'
        print("---Doing: " + cam_cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return outpath, "fswebcam", (out + error).strip()
