import wx

class libcam_sets_pnl(wx.Panel):
    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        label = wx.StaticText(self,  label='libcam Settings')
        label.SetFont(shared_data.button_font)

        def create_settings_sizer():
            camera_res = get_camera_res()
            self.default_settings_dict = {"resolution"            : [camera_res[0], camera_res],
                             "brightness"            : ["50", (-1, 1)],
                             "contrast"              : ["0", (-1.0, 1.0)],
                             "saturation"            : ["0", (-0.0, 1.0)],
                             #"iso"                   : ["0", ['0', '100', '200', '320', '400', '500', '640', '800']],
                             "sharpness"             : ["0", (-100, 100)],
                             "rot"                   : ["(0.0, 0.0, 1.0, 1.0)", ""],
                             "awb"                   : ["auto", "incandescent", "tungsten", "fluorescent", "indoor", "daylight", "cloudy", "custom"],
                             "encoding"              : ["jpg", "png", "rgb", "bmp", "yuv420"]
                             }
            settings_dict = self.default_settings_dict
            c_settings_sizer = wx.FlexGridSizer(3, 0, 5)
            setting_crtl_dict = {}
            setting_t_dict = {}
            for setting in settings_dict.keys():
                label, box, box_t = create_ui_element(setting, settings_dict[setting])
                if not label == None:
                    setting_crtl_dict[setting] = box
                    setting_t_dict[setting] = box_t
                    c_settings_sizer.Add(label, 0, wx.TOP|wx.ALIGN_RIGHT, 2)
                    c_settings_sizer.Add(box, 0, wx.TOP|wx.EXPAND, 2)
                    c_settings_sizer.Add(box_t, 0, wx.TOP|wx.EXPAND, 2)
            return c_settings_sizer, setting_crtl_dict, setting_t_dict

        def get_camera_res():
            camera_res_v1 = ['1920x1080', '2592x1944', '1296x972', '1296x730', '640x480']
            camera_res_v2 = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
            return camera_res_v2

        def create_ui_element(setting, vals):
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
                print (" Error - libcam_set create_ui_element - Not set up to undertand ", type(vals[1]), " as options type")
                input_box = wx.TextCtrl(self, value="")
            return label, input_box, input_box_t

        c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = create_settings_sizer()

        #    self.test_btn = wx.Button(self, label='test defult')
        #    self.test_btn.SetFont(shared_data.button_font)
        #    self.test_btn.Bind(wx.EVT_BUTTON, self.defult)
        #    self.testr_btn = wx.Button(self, label='test read')
        #    self.testr_btn.SetFont(shared_data.button_font)
        #    self.testr_btn.Bind(wx.EVT_BUTTON, self.read_settings_file)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        #    main_sizer.Add(self.test_btn, 0, wx.ALL, 0)
        #    main_sizer.Add(self.testr_btn, 0, wx.ALL, 0)
        main_sizer.Add(c_sets_sizer, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)


    def slider_move(self, e):
        setting_name = e.GetEventObject().GetLabel()
        slider_val = e.GetEventObject().GetValue()
        self.setting_t_dict[setting_name].SetValue(str(slider_val))

    def slider_text_change(self, e):
        setting_name = e.GetEventObject().GetLabel()
        box_val = e.GetEventObject().GetValue()
        self.setting_crtl_dict[setting_name].SetValue(int(box_val))


    def make_conf_text(self, setting_dict):
        settings_text = ""
        for item in setting_dict.keys():
            value = str(setting_dict[item].GetValue())
            if not value == "":
                settings_text += item + "=" + value + "\n"
        return settings_text

    def text_into_ui(self, set_text):
        # convert config file into dictionary
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

    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/libcam_cap.py caps=' + outpath + ' set=' + settings_file
        print(cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        # check for text output listing save location
        if "Saving image to:" in out:
            path = out.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + out + '\n' + error
        return path

    def take_default(self, outpath):
        print(" Taking default image using libcamera-still ")
        cam_cmd = "libcamera-still -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return out + error, "libcam-still"
