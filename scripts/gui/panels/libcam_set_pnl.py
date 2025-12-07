import wx
import wx.lib.agw.floatspin as FS

class libcam_sets_pnl(wx.Panel):
    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        label = wx.StaticText(self,  label='libcam Settings')
        label.SetFont(shared_data.button_font)

        def create_settings_sizer():
            camera_res = get_camera_res()
            self.default_settings_dict = {"resolution"            : [camera_res[0], camera_res, "0x0 sets full-size default"],
                             "brightness"            : ["0", (-1.0, 1.0), "-1.0 to 1.0"],
                             "contrast"              : ["1", (0.0, 10.0), "1.0 = normal contrast"],
                             "saturation"            : ["1", (-0.0, 10.0), "1.0 = normal and 0.0 = greyscale"],
                             "sharpness"             : ["1", (-1.0, 10.0), "1.0 = normal sharpening"],
                             "gain"                  : ["0", (-100, 100), ""],
                             "shutter"               : ["0", "", "Shutter speed in microseconds"],
                             "roi"                   : ["0.0, 0.0, 1.0, 1.0", "", "Region Of Interest (digital zoom)"],
                            # "rotation"              : ["0", (0, 180), ""],
                             "vflip"                 : ["0", ["0", "1"], ""],
                             "hflip"                 : ["0", ["0", "1"], ""],
                             "metering"              : ["centre", ["centre", "spot", "average", "custom"], ""],
                             "exposure"              : ["normal", ["normal", "sport"], ""],
                             "ev"                    : ["0", (-10, 10), "EV exposure compensation, where 0 = no change"],
                             "awb"                   : ["auto", ["auto", "incandescent", "tungsten", "fluorescent", "indoor", "daylight", "cloudy", "custom"], ""],
                             "denoise"               : ["auto", ["auto", "off", "cdn_off", "cdn_fast", "cdn_hq"], ""],

                             "encoding"              : ["jpg", ["jpg", "png", "rgb", "bmp", "yuv420"], ""],
                             "quality"               : ["93", (1,100), "jpg quality"]
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
            camera_res_v2 = ['0x0', '1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
            return camera_res_v2

        def create_ui_element(setting, vals):
            label     = wx.StaticText(self,  label=setting)
            input_box_t = wx.StaticText(self,  label=vals[2])
            if isinstance(vals[1], list):
                input_box = wx.ComboBox(self, choices=vals[1], value=vals[0])
            elif isinstance(vals[1], str):
                input_box = wx.TextCtrl(self, value=vals[0])
            elif isinstance(vals[1], tuple):
                # set the size of the scroll step
                if isinstance(vals[1][1], int):
                    slidestep = 1
                else:
                    slidestep = 0.1
                # create spin control
                min_val, max_val = vals[1]
                default_val = float(vals[0])
                #print(min_val, max_val, default_val)
                input_box = FS.FloatSpin(self, -1, size=(200, 40), value=default_val, min_val=float(min_val), max_val=float(max_val), increment=slidestep, agwStyle=FS.FS_LEFT)
                input_box.SetDigits(2)
                #input_box.SetLabel(setting)
            else:
                print (" Error - libcam_set create_ui_element - Not set up to understand ", type(vals[1]), " as options type")
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
                if type(self.setting_crtl_dict[key]) == wx.lib.agw.floatspin.FloatSpin:
                    csd[key] = float(csd[key])
                self.setting_crtl_dict[key].SetValue(csd[key])

    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/libcam_cap.py caps=' + outpath + ' set=' + settings_file
        print(cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        # check for text output listing save location
        if "Saving image to:" in combined_output:
            path = combined_output.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + combined_output
        return path, combined_output

    def take_default(self, outpath):
        print(" Taking default image using libcamera-still ")
        cam_cmd = "libcamera-still -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return outpath, "libcam-still", (out + error).strip()
