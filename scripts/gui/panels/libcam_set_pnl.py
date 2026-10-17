import re

import wx

from panels.camera_controls import (
    SettingsGrid, create_setting, load_settings, parse_settings,
    serialize_settings,
)
from panels.image_region import create_region_button


class libcam_sets_pnl(wx.Panel):
    # These settings are optional because older libcamera-still releases do not
    # support all of them. Empty values never change the capture command.
    optional_settings = {
        "timeout": ["", "", "Preview / settling time, e.g. 5000 (milliseconds) or 5sec"],
        "autofocus-mode": ["", ["", "manual", "auto", "continuous"], "Autofocus mode; leave empty to keep the capture script default"],
        "autofocus-range": ["", ["", "normal", "macro", "full"], "Autofocus search range, on cameras with a focus motor"],
        "autofocus-speed": ["", ["", "normal", "fast"], "Autofocus search speed"],
        "autofocus-window": ["", "", "Focus region: x,y,width,height, each from 0 to 1"],
        "lens-position": ["", "", "Manual lens position in dioptres; 0 means infinity. Use manual autofocus mode."],
        "awbgains": ["", "", "Manual red,blue white balance gains, e.g. 1.5,1.2"],
    }

    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        label = wx.StaticText(self, label='libcamera Settings')
        label.SetFont(shared_data.button_font)
        camera_res = ['0x0', '1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        self.default_settings_dict = {
            "resolution": [camera_res[0], camera_res, "Width x height; 0x0 uses the full-size camera default. Custom sizes may be typed."],
            "brightness": ["0", (-1.0, 1.0), "Brightness: -1.0 to 1.0"],
            "contrast": ["1", (0.0, 10.0), "1.0 = normal contrast"],
            "saturation": ["1", (0.0, 10.0), "1.0 = normal; 0.0 = greyscale"],
            "sharpness": ["1", (-1.0, 10.0), "1.0 = normal sharpening"],
            "gain": ["0", (-100.0, 100.0), "Camera analogue gain; 0 uses automatic gain"],
            "shutter": ["0", "", "Shutter speed in microseconds; 0 uses automatic exposure"],
            "roi": ["0.0, 0.0, 1.0, 1.0", "", "Digital zoom region: x,y,width,height, each from 0 to 1"],
            "vflip": ["0", ["0", "1"], "Vertical flip (existing 0/1 config values are retained)"],
            "hflip": ["0", ["0", "1"], "Horizontal flip (existing 0/1 config values are retained)"],
            "metering": ["centre", ["centre", "spot", "average", "custom"], "Exposure metering region"],
            "exposure": ["normal", ["normal", "sport"], "Exposure profile"],
            "ev": ["0", (-10.0, 10.0), "Exposure compensation in stops; 0 = no change"],
            "awb": ["auto", ["auto", "incandescent", "tungsten", "fluorescent", "indoor", "daylight", "cloudy", "custom"], "Automatic white balance profile"],
            "denoise": ["auto", ["auto", "off", "cdn_off", "cdn_fast", "cdn_hq"], "Noise reduction mode"],
            "encoding": ["jpg", ["jpg", "png", "rgb", "bmp", "yuv420"], "Output image encoding"],
            "quality": ["93", (1.0, 100.0), "JPEG quality, 1 to 100"],
        }
        self.setting_crtl_dict = {}
        self.setting_t_dict = {}
        self.c_settings_sizer = SettingsGrid(self)
        self._append_settings(self.default_settings_dict)

        self.extra_options_btn = wx.Button(self, label='Find extra options')
        self.extra_options_btn.SetToolTip('Check the installed libcamera-still version for optional focus, white balance and capture-time controls.')
        self.extra_options_btn.Bind(wx.EVT_BUTTON, self.find_extra_options)
        self.extra_options_status = wx.StaticText(self, label='')
        extra_sizer = wx.WrapSizer(wx.HORIZONTAL)
        extra_sizer.Add(self.extra_options_btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 8)
        extra_sizer.Add(self.extra_options_status, 0, wx.ALIGN_CENTER_VERTICAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL, 6)
        main_sizer.Add(self.c_settings_sizer, 0, wx.ALL | wx.EXPAND, 6)
        main_sizer.Add(extra_sizer, 0, wx.ALL | wx.EXPAND, 6)
        self.SetSizer(main_sizer)

    def _append_settings(self, specs):
        for setting, values in specs.items():
            if setting in self.setting_crtl_dict:
                continue
            label, control, auxiliary = create_setting(self, setting, values[0], values[1], values[2])
            if setting in ("roi", "autofocus-window"):
                kind = "autofocus" if setting == "autofocus-window" else "crop"
                auxiliary = create_region_button(self, setting, kind)
            self.setting_crtl_dict[setting] = control
            self.setting_t_dict[setting] = auxiliary
            label.Destroy()
            self.c_settings_sizer.add_setting(setting, control, auxiliary, values[2])

    def find_extra_options(self, event):
        # Match the exact binary used by libcam_cap.py rather than a different
        # installation that happens to be first on PATH.
        out, error = self.parent.parent.link_pnl.run_on_pi('/usr/local/bin/libcamera-still --help 2>&1')
        supported = set(re.findall(r'--([a-z][a-z0-9-]*)\b', out + error))
        found = {key: values for key, values in self.optional_settings.items() if key in supported}
        self._append_settings(found)
        if found:
            self.extra_options_status.SetLabel('{} extra options available'.format(len(found)))
        else:
            self.extra_options_status.SetLabel('No extra options reported')
        self.extra_options_status.SetToolTip((out + error).strip() if not found else 'Leave optional fields empty to keep the existing capture behaviour.')
        self.Layout()
        self.parent.Layout()

    def make_conf_text(self, setting_dict):
        return serialize_settings(self, setting_dict)

    def text_into_ui(self, set_text):
        loaded = parse_settings(set_text)
        self._append_settings({key: values for key, values in self.optional_settings.items() if key in loaded})
        # Loading an older config must not inherit an optional override from the
        # previously viewed config (in particular manual focus or a timeout).
        for key in self.optional_settings:
            if key in self.setting_crtl_dict and key not in loaded:
                self.setting_crtl_dict[key].SetValue('')
        load_settings(self, set_text, aliases=False)
        self.Layout()
        self.parent.Layout()

    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/libcam_cap.py caps=' + outpath + ' set=' + settings_file
        print(cmd)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
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
