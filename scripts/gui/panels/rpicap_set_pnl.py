import wx

from panels.camera_controls import controls_grid, load_settings, serialize_settings

from panels.image_region import (
    EVT_ROI_CHANGED, ROIChangedEvent, SetAFROIDialog, create_region_button,
    edit_region, parse_roi,
)


class rpicap_sets_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent, style=wx.TAB_TRAVERSAL)
        label = wx.StaticText(self, label="Rpicam settings")
        label.SetFont(parent.parent.shared_data.button_font)
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_empty_settings_sizer()
        self.refresh_settings_sizer()

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(label, 0, wx.BOTTOM, 8)
        self.main_sizer.Add(self.c_sets_sizer, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def set_afroi_click(self, event):
        edit_region(self, "autofocus-window", "autofocus")

    def set_roi_click(self, event):
        edit_region(self, "roi", "crop")

    def make_control_dict(self):
        # -t [ --timeout ] arg (=5sec) -- Time for which program runs. If no units are provided default to ms.
        control_dict = {"brightness":[(-1.0, 1.0), 0.0],
                        "contrast":[(0.0, 32.0), 1.0],
                        "saturation":[(0.0, 32.0), 1.0],
                        "sharpness":[(0.0, 16.0), 1.0],
                        "hflip":[["True", "False"], "False"],
                        "vflip":[["True", "False"], "False"],
                        "roi":["0,0,1,1", "0,0,1,1", "X, Y, w, h - in decimal 0.0 to 1.0"],
                        "rotation":[(0, 180), 0],
                        "shutter":["0", "0", "Shutter speed in microseconds; 0 selects automatic exposure"],
                        "gain":["0", "0"],
                        "ev":[(-10.0, 10.0), 0.0, "exposure value compensation of the image in stops"],

                        "exposure":[["normal",
                                     "sport"], "normal"],
                        "metering":[["centre",
                                     "spot",
                                     "average",
                                     "custom"], "centre"],
                         #"flicker-period":[(0, 50000), 0],
                         "awb":[["auto",
                                 "incandescent",
                                 "tungsten",
                                 "fluorescent",
                                 "indoor",
                                 "daylight",
                                 "cloudy",
                                 "custom"], "auto", "Auto White Balance"],
                        "awbgains":["0,0", "0,0", "Explicit red and blue white balance gains, separated by a comma"],
                        "denoise":[["auto",
                                   "off",
                                   "cdn_off",
                                   "cdn_fast",
                                   "cdn_hq"], "auto"],
                        "autofocus-mode":[["manual",
                                           "auto",
                                           "continuous"], "auto"],
                        "autofocus-range":[["normal",
                                            "macro",
                                            "full"], "normal"],
                        "autofocus-speed":[["normal",
                                            "fast"], "normal"],
                        "autofocus-window":["0.33,0.33,0.33,0.33", "0.33,0.33,0.33,0.33", "X, Y, w, h - in decimal 0.0 to 1.0"],
                        "lens-position":[(0.0, 32.0), 0.0],
                        "hdr":[["off",
                               "auto",
                               "sensor",
                               "single-exp"], "off"],
                        "encoding":[["jpg",
                                     "png",
                                     "bmp",
                                     "rgb",
                                     "yuv420"], "jpg"],
                        "raw":[["True", "False"], "False"],
                        "metadata":[["off",
                                    "each",
                                    "$path",
                                    "-"], "off"],
                        "tuning-file":["", "", "Path to camera tuning file"],
                        "post-process-file":["", "", "Path to post-processing configuration file"],
                        "quality":[(1, 100), "", "JPEG quality (1–100); leave blank for the camera default"],
                        "timeout":["", "", "Camera warm-up time, e.g. 5s or 2000ms; blank uses the tool default"],
                        "framerate":["", "", "Frame rate; lower values allow longer exposures"]}

        return control_dict

    def create_empty_settings_sizer(self):
        return wx.BoxSizer(wx.VERTICAL), {}, {}

    def refresh_settings_sizer(self):
        previous = {key: control.GetValue() for key, control in self.setting_crtl_dict.items()}
        preset_res = ['4608x2592 "picam v3"', '4056x3040 "picam HQ"',
                      '3280x2464 "picam v2"', '3840x2160 "4K UHD"',
                      '2592x1944 "picam v1"', '1920x1080 "Full HD (1080p)"',
                      '1280x720 "HD (720p)"', '640x480 "VGA"', '320x240 "QVGA"']
        specs = {"Resolution": [preset_res[0], preset_res,
                                "Image dimensions in pixels; select a preset or type WIDTHxHEIGHT."]}
        # This backend's original schema is [options, default, optional hint].
        for key, spec in self.make_control_dict().items():
            specs[key] = [spec[1], spec[0]] + spec[2:]
        self.c_sets_sizer.Clear(delete_windows=True)
        grid, self.setting_crtl_dict, self.setting_t_dict = controls_grid(
            self, specs, auxiliary_factories={
                "autofocus-window": lambda control: create_region_button(self, "autofocus-window", "autofocus"),
                "roi": lambda control: create_region_button(self, "roi"),
            })
        self.c_sets_sizer.Add(grid, 0, wx.EXPAND)
        for key, value in previous.items():
            if key in self.setting_crtl_dict:
                self.setting_crtl_dict[key].SetValue(value)
        self.Layout()
        self.parent.Layout()

    def make_conf_text(self, setting_dict):
        return serialize_settings(self, setting_dict, self.set_for_text)

    def set_for_text(self, settings):
        if "Resolution" in settings:
            settings["Resolution"] = str(settings["Resolution"]).split()[0]
        return settings

    def text_into_ui(self, set_text):
        load_settings(self, set_text, aliases=False)

    # Image capture
    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/rpicap.py caps=' + outpath + ' set=' + settings_file
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        print(out, error)
        # check for text output listing save location
        if "Saving image to:" in combined_output:
            path = combined_output.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + combined_output
        return path, combined_output

    def take_default(self, outpath):
        print(" Taking default image using rpicam-still ")
        metapath = outpath.split(".")[0] + ".json"
        print("saving metadata to", metapath)
        cam_cmd = "rpicam-still --nopreview --metadata " + metapath + " -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return outpath, "rpicam-still", (out + error).strip()
