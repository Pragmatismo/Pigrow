import wx

from panels.camera_controls import controls_grid, load_settings, serialize_settings


class picam_sets_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent, style=wx.TAB_TRAVERSAL)
        label = wx.StaticText(self, label="PiCamera settings")
        label.SetFont(parent.parent.shared_data.button_font)
        camera_res_v1 = ['1920x1080', '2592x1944', '1296x972', '1296x730', '640x480']
        camera_res_v2 = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        camera_res = list(dict.fromkeys(camera_res_v2 + camera_res_v1))
        self.default_settings_dict = {"resolution"            : [camera_res[0], camera_res],
                         "brightness"            : ["50", (0, 100)],
                         "contrast"              : ["0", (-100, 100)],
                         "saturation"            : ["0", (-100, 100)],
                         "iso"                   : ["0", ['0', '100', '200', '320', '400', '500', '640', '800']],
                         "sharpness"             : ["0", (-100, 100)],
                         "zoom"                  : ["(0.0, 0.0, 1.0, 1.0)", ""],
                         "drc_strength"          : ["", ['off', 'low', 'medium', 'high']],
                         "exposure_compensation" : ["0", (-25, 25)],
                         "exposure_mode"         : ["", ['off', 'auto', 'night', 'nightpreview', 'backlight', 'spotlight', 'sports', 'snow',
                                                         'beach', 'verylong', 'fixedfps', 'antishake', 'fireworks']],
                         "exposure_speed"        : ["", "0 (auto), shutter speed in microseconds"],
                         "hflip"                 : ["", ["True", "False"]],
                         "vflip"                 : ["", ["True", "False"]],
                         "rotation"              : ["", ['0', '90', '180', '270']],
                         "meter_mode"            : ["", ['average', 'spot', 'backlit', 'matrix']],
                         "image_denoise"         : ["", ["True", "False"]],
                         "image_effect"          : ["", ['none', 'negative', 'solarize', 'sketch', 'denoise', 'emboss', 'oilpaint', 'hatch', 'gpen', 'pastel', 'watercolor', 'film', 'blur',
                                                         'saturation', 'colorswap', 'washedout', 'posterise', 'colorpoint', 'colorbalance', 'cartoon', 'deinterlace1', 'deinterlace2']],
                         "image_effect_params"   : ["", ""],
                         "awb_mode"              : ["", ['off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon']]
                         }
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = controls_grid(self, self.default_settings_dict)
        self.setting_crtl_dict["resolution"].SetToolTip("Image dimensions in pixels; select a preset or type WIDTHxHEIGHT.")
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.BOTTOM, 8)
        main_sizer.Add(self.c_sets_sizer, 0, wx.EXPAND)
        self.SetSizer(main_sizer)

    def make_conf_text(self, setting_dict):
        return serialize_settings(self, setting_dict)

    def text_into_ui(self, set_text):
        load_settings(self, set_text)

    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/picamcap.py caps=' + outpath + ' set=' + settings_file
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        # check for text output listing save location
        if "Saving image to:" in combined_output:
            path = combined_output.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + combined_output
        return path, combined_output

    def take_default(self, outpath):
        print(" Taking default image using raspistill ")
        cam_cmd = "raspistill -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return outpath, "raspistill", (out + error).strip()
