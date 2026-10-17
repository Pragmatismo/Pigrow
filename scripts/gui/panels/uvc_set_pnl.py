"""Settings supported by camcap.py's uvccapture backend."""

import shlex

import wx

from panels.camera_controls import (
    NumericControl,
    SettingsGrid,
    load_settings,
    serialize_settings,
)


class uvc_sets_pnl(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.camera_settings_dict = {}

        self.label = wx.StaticText(self, label="UVCCapture settings")
        self.label.SetFont(parent.parent.shared_data.button_font)
        grid = SettingsGrid(self)
        self.setting_crtl_dict = {}
        self.setting_t_dict = {}

        resolution = wx.ComboBox(
            self,
            value="",
            choices=["", "1920x1080", "1280x720", "640x480", "320x240"],
        )
        resolution.SetMinSize((200, -1))
        resolution.SetHint("Camera default / width x height")
        grid.add_setting(
            "resolution", resolution,
            tooltip="Enter any supported width x height. Leave blank to use camcap's default maximum size.",
        )
        self.setting_crtl_dict["resolution"] = resolution
        self.setting_t_dict["resolution"] = None

        for key, label in (
            ("s_val", "Saturation"),
            ("c_val", "Contrast"),
            ("g_val", "Gain"),
            ("b_val", "Brightness"),
        ):
            control = NumericControl(self, key, "", 0, 255)
            control.text.SetHint("Default")
            tip = (
                "Leave blank for the camera default. The slider covers 0–255; "
                "enter other values directly if your camera uses a different range."
            )
            grid.add_setting(key, control, tooltip=tip).SetLabel(label)
            self.setting_crtl_dict[key] = control
            self.setting_t_dict[key] = None

        extra = wx.TextCtrl(self)
        extra.SetHint("Additional uvccapture arguments")
        grid.add_setting(
            "uvc_extra", extra,
            tooltip="Additional uvccapture arguments, passed through unchanged by camcap.py.",
        ).SetLabel("Extra arguments")
        self.setting_crtl_dict["uvc_extra"] = extra
        self.setting_t_dict["uvc_extra"] = None
        self.c_sets_sizer = grid

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.label, 0, wx.BOTTOM, 8)
        main_sizer.Add(grid, 0, wx.EXPAND)
        self.SetSizer(main_sizer)

    def text_into_ui(self, set_text):
        # Each loaded file starts from the backend's unset values, rather than
        # inheriting controls left over from the previously selected file.
        for control in self.setting_crtl_dict.values():
            control.SetValue("")
        load_settings(self, set_text, aliases=False)

        # camcap accepts both the legacy dimensions and resolution, processing
        # them in file order. Display the effective dimensions in either form,
        # including files which set just one dimension or mix the old/new keys.
        width, height = "100000", "100000"
        dimensions_set = False
        for line in set_text.splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            key, value = (item.strip() for item in line.split("=", 1))
            if key == "x_dim":
                width, dimensions_set = value, True
            elif key == "y_dim":
                height, dimensions_set = value, True
            elif key == "resolution" and value.count("x") == 1:
                width, height = value.split("x", 1)
                dimensions_set = True
        if dimensions_set:
            self.setting_crtl_dict["resolution"].SetValue(width + "x" + height)

    def make_conf_text(self, setting_dict):
        def resolution_last(values):
            resolution = values.pop("resolution", "")
            if resolution:
                # A new resolution must take precedence over legacy keys, even
                # when those keys appeared later in the loaded file.
                values["resolution"] = resolution
            else:
                # Clearing the resolution restores the backend defaults.
                values.pop("x_dim", None)
                values.pop("y_dim", None)
            return values

        return serialize_settings(self, setting_dict, transforms=resolution_last)

    def take_image(self, settings_file, outpath):
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = (
            shlex.quote(pigrow_path + "scripts/cron/camcap.py")
            + " " + shlex.quote("caps=" + outpath)
            + " " + shlex.quote("set=" + settings_file)
        )
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        path = "Error : Image path not given \n\n" + combined_output
        for line in combined_output.splitlines():
            for marker in ("Capture Finished, Image path :", "Saving image to:"):
                if marker in line:
                    path = line.split(marker, 1)[1].strip()
        return path, combined_output

    def take_default(self, outpath):
        camera = self.parent.parent.dict_C_pnl["camera_pnl"].cam_cb.GetValue()
        # Match camcap's maximum-size defaults without reading a settings file.
        cmd = "uvccapture -x100000 -y100000 -v -t0"
        if camera:
            cmd += " " + shlex.quote("-d" + camera)
        cmd += " " + shlex.quote("-o" + outpath)
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        return outpath, "uvccapture", (out + error).strip()
