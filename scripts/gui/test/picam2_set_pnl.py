import wx

class picam2_sets_pnl(wx.Panel):

    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        label = wx.StaticText(self,  label='Picam Settings')
        label.SetFont(shared_data.button_font)

        self.getset_btn = wx.Button(self, label='Get Settings')
        self.getset_btn.Bind(wx.EVT_BUTTON, self.getset_click)
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_empty_settings_sizer()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        main_sizer.Add(self.getset_btn, 0, wx.ALL, 0)
        main_sizer.Add(self.c_sets_sizer, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    def getset_click(self, e):
        print("Getting settings from Raspberry Pi")
        self.refresh_settings_sizer()

    def make_control_dict(self):
        control_dict = {"AeConstraintMode":[["Normal",
                                             "Highlight",
                                             "Shadows",
                                             "Custom"], 0],
                        "AeEnable":[["True", "False"], 0],
                        "AeExposureMode":[["Normal",
                                           "Short",
                                           "Long",
                                           "Custom"], 0],
                        "AeFlickerMode":[["FlickerOff",
                                          "FlickerManual"], 0],
                        "AeFlickerPeriod":[(0, 50000), 10000],
                        "AeMeteringMode":[["CentreWeighted",
                                           "Spot",
                                           "Matrix",
                                           "Custom"], 0],
                        "AfMetering":[["Auto",
                                       "Windows"], 0],
                        "AfMode":[["Manual",
                                   "Auto",
                                   "Continuous"], 1],
                        "AfRange":[["Normal",
                                    "Macro",
                                    "Full"], 2],
                        "AfSpeed":[["Normal",
                                    "Fast"], 0],
                        #"AfWindows":[
                        #"AnalogueGain":[]
                        "AwbEnable":[["False", "True"], 1],
                        "AwbMode":[["Auto",
                                    "Tungsten",
                                    "Fluorescent",
                                    "Indoor",
                                    "Daylight",
                                    "Cloudy",
                                    "Custom"], 0],
                        "Brightness":[(-1.0, 1.0), 0.0],
                        #"ColourCorrectionMatrix"
                        #"ColourGains"
                        "Contrast":[(-1.0, 1.0), 0.0],
                        "Saturation":[(0.0, 32.0), 1.0],
                        "Sharpness":[(0.0, 16.0), 1.0],
                        #"ExposureTime":[]
                        "ExposureValue":[(-8.0, 8.0), 0.0],
                        #"FrameDurationLimits"
                        "HdrMode":[["Off",
                                    "SingleExposure",
                                    "MultiExposure",
                                    "Night",
                                    "MultiExposureUnmerged"], 0],
                        "LensPosition":[(0.0, 32.0), 5.0],
                        # LENS POS SHOULD BE use BY camera_controls property
                        "NoiseReductionMode":[["Off",
                                               "Fast",
                                               "HighQuality"], 0]}
                        #"ScalerCrop":(,,,,)

        return control_dict

    def read_set_from_pi(self):

        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/picam2cap.py --settings'
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        print("picam2 settings;")
        print(out)
        lines = out.splitlines()
        for line in lines:
            if "=" in line:
                name, vals = line.split("=")
                name = name.strip()
                vmin, vmax, vnow = vals.split("|")

                try:
                    vnow = float(vnow)
                    vmin = float(vmin)
                    vmax = float(vmax)
                    settings_dict[name] = [vnow, (vmin, vmax)]
                except:
                    #print("didn't work with", line)
                    pass


    def refresh_settings_sizer(self):
        self.c_sets_sizer.Clear(delete_windows=True)
        settings_dict = self.make_control_dict()

        # Get Resolution and camera sensor settings
        #camera_res_v1 = ['1920x1080', '2592x1944', '1296x972', '1296x730', '640x480']
        #camera_res_v2 = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        preset_res = ['4608x2592 "picam v3"',
                      '4056x3040 "picam HQ"',
                      '3280x2464 "picam v2"',
                      '3840x2160 "4K UHD"',
                      '2592x1944 "picam v1"',
                      '1920x1080 "Full HD (1080p)"',
                      '1280x720 "HD (720p)"',
                      '640x480 "VGA"',
                      '320x240 "QVGA"']
        #preset_res = limit_res_for_cam(preset_res)
        settings_dict["Resolution"] = [preset_res, preset_res[0]]



        # read settings
        # currently not reading setting from pi

        # make ui elements and reference dicts
        setting_crtl_dict = {}
        setting_t_dict = {}
        for setting in settings_dict.keys():
            print(" Making box for", setting)
            label, box, box_t = self.create_ui_element(setting, settings_dict[setting])
            if not label == None:
                self.setting_crtl_dict[setting] = box
                self.setting_t_dict[setting] = box_t
                self.c_sets_sizer.Add(label, 0, wx.TOP|wx.ALIGN_RIGHT, 2)
                self.c_sets_sizer.Add(box, 0, wx.TOP|wx.EXPAND, 2)
                self.c_sets_sizer.Add(box_t, 0, wx.TOP|wx.EXPAND, 2)

        self.parent.Layout()

    def create_ui_element(self, setting, vals):
        label     = wx.StaticText(self,  label=setting)
        input_box_t = wx.StaticText(self,  label="")
        if isinstance(vals[0], list):
            input_box = wx.ComboBox(self, choices=vals[0])
            if isinstance(vals[1], int):
                input_box.SetSelection(vals[1])
            else:
                input_box.SetValue(vals[1])
        elif isinstance(vals[0], str):
            input_box = wx.TextCtrl(self, value=vals[1])

        elif isinstance(vals[0], tuple) and isinstance(vals[1], int):
            min_val, max_val = vals[0]
            default_val = int(vals[1])
            #print(min_val, max_val, default_val)
            input_box_t = wx.TextCtrl(self, value=str(default_val), style=wx.TE_PROCESS_ENTER)
            input_box_t.SetLabel(setting)
            input_box_t.Bind(wx.EVT_TEXT_ENTER, self.slider_text_change)
            input_box = wx.Slider(self, id=wx.ID_ANY, value=default_val, minValue=int(min_val), maxValue=int(max_val))
            input_box.SetLabel(setting)
            input_box.Bind(wx.EVT_SLIDER, self.slider_move)
        elif isinstance(vals[0], tuple) and isinstance(vals[1], float):
            min_val, max_val = vals[0]
            step = 0.1
            c_val = float(vals[1])
            #
            slider_v = int((c_val - min_val) / (max_val - min_val) * 100)
            slider_m = int((max_val - min_val) / (max_val - min_val) * 100)

            #
            input_box = wx.SpinCtrlDouble(self, value=str(c_val), min=min_val, max=max_val, inc=step)
            input_box.SetLabel(setting)
            self.Bind(wx.EVT_SPINCTRLDOUBLE, self.onSpinCtrl, input_box)

            input_box_t = wx.Slider(self, value=slider_v, minValue=0, maxValue=slider_m, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
            input_box_t.SetTickFreq(10)
            input_box_t.SetLabel(setting)
            self.Bind(wx.EVT_SLIDER, self.onSlider, input_box_t)
            #

        else:
            print (" Error - picam2_set create_ui_element - Not set up to undertand ", type(vals[1]), " as options type")
            input_box = wx.TextCtrl(self, value="")
        return label, input_box, input_box_t

    def create_empty_settings_sizer(self):
        note = wx.StaticText(self,  label='Press Get Settings')

        #c_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        c_settings_sizer = wx.FlexGridSizer(3, 0, 5)
        c_settings_sizer.Add(note, 0, wx.ALL|wx.EXPAND, 3)

        setting_crtl_dict = {}
        setting_t_dict = {}
        return c_settings_sizer, setting_crtl_dict, setting_t_dict


    # int slider
    def slider_move(self, e):
        setting_name = e.GetEventObject().GetLabel()
        slider_val = e.GetEventObject().GetValue()
        self.setting_t_dict[setting_name].SetValue(str(slider_val))

    def slider_text_change(self, e):
        setting_name = e.GetEventObject().GetLabel()
        box_val = e.GetEventObject().GetValue()
        self.setting_crtl_dict[setting_name].SetValue(int(box_val))

    # float spin control
    def onSpinCtrl(self, event):
        spinCtrl = event.GetEventObject()
        setting_name = spinCtrl.GetLabel()
        spin_val = spinCtrl.GetValue()
        slider = self.setting_t_dict[setting_name]
        minValue = spinCtrl.GetMin()
        maxValue = spinCtrl.GetMax()
        slider.SetValue(int((spin_val - minValue) / (maxValue - minValue) * 100))

    def onSlider(self, event):
        slider = event.GetEventObject()
        setting_name = slider.GetLabel()
        slider_val = slider.GetValue()
        spinCtrl = self.setting_crtl_dict[setting_name]
        minValue = spinCtrl.GetMin()
        maxValue = spinCtrl.GetMax()
        spinCtrl.SetValue(float(minValue + (maxValue - minValue) * slider_val / 100))


    # config
    def make_conf_text(self, setting_dict):
        #print("handed settings_dict", setting_dict)
        set_for_txt_dict = {}
        for item in setting_dict.keys():
            #
            print(setting_dict[item])
            if isinstance(setting_dict[item], wx.ComboBox):
                index = setting_dict[item].GetSelection()
                if index != wx.NOT_FOUND:
                    print("Index of selected item:", index)
                    value = index
                else:
                    value = ""
                    print("No item selected.")
            else:
                value = setting_dict[item].GetValue()
            #
            if not value == "":
                set_for_txt_dict[item] = value
                print("Adding from setting_dict get value;", item, value)

        # switch dict
        set_for_txt_dict = self.set_for_text(set_for_txt_dict)

        settings_text = ""
        for item in set_for_txt_dict.keys():
            value = str(set_for_txt_dict[item]).strip()
            settings_text += item.strip() + "=" + value + "\n"

        print("picam2_set returning;", settings_text)
        return settings_text

    def set_for_text(self, set_dict):
        '''alters settings to match expected format'''
        if "Resolution" in set_dict:
            if " " in set_dict["Resolution"]:
                set_dict["Resolution"] = set_dict["Resolution"].split(" ")[0]

        return set_dict


    # def text_into_ui(self, set_text):
        # cam_settings = set_text.splitlines()
        # self.camera_settings_dict = {}
        # for line in cam_settings:
        #     if "=" in line:
        #         equals_pos = line.find("=")
        #         key = line[:equals_pos]
        #         value = line[equals_pos+1:]
        #         self.camera_settings_dict[key] = value
        # # make changes for old keys
        # csd = self.camera_settings_dict
        #
        # # put into ui items
        # for key in csd.keys():
        #     if key in self.setting_crtl_dict:
        #         if type(self.setting_crtl_dict[key]) == wx._core.Slider:
        #             self.setting_t_dict[key].SetValue(csd[key])
        #             csd[key] = int(csd[key])
        #         self.setting_crtl_dict[key].SetValue(csd[key])

    # image capture
    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/picam2cap.py caps=' + outpath + ' set=' + settings_file
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        # check for text output listing save location
        if "Saving image to:" in out:
            path = out.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + out + '\n' + error
        return path

    def take_default(self, outpath):
        print(" Taking default image using rpicam-still ")
        cam_cmd = "rpicam-still --nopreview -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return out + error, "rpicam-still"
