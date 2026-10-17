import re
import shlex

import wx

from panels.camera_controls import controls_grid, load_settings, parse_settings, serialize_settings


class fs_sets_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent, style=wx.TAB_TRAVERSAL)
        self.label = wx.StaticText(self, label="Fswebcam settings")
        self.label.SetFont(parent.parent.shared_data.button_font)
        camera_res = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        self.generic_settings_dict = {
            "resolution": [camera_res[0], camera_res, "Select a preset or type custom WIDTHxHEIGHT dimensions."],
            "fs_delay": ["2", (0, 15), "Delay before capture in seconds."],
            "fs_fskip": ["5", (0, 25), "Discard this many frames before capturing the photo."],
            "fs_jpg_q": ["90", (0, 100), "JPEG image quality."],
            "fs_banner": ["True", ["True", "False"], "Include the date banner on the image."],
        }
        self.device_settings_dict = {}
        self.c_sets_sizer = wx.BoxSizer(wx.VERTICAL)
        self.setting_crtl_dict = {}
        self.setting_t_dict = {}
        self.make_sizer()
        self._rebuild_settings()

    def make_sizer(self):
        self.test_btn = wx.Button(self, label="Find resolutions")
        self.test_btn.SetToolTip("Read supported resolutions from the selected camera. Custom dimensions remain editable.")
        self.test_btn.Bind(wx.EVT_BUTTON, self.get_resolutions_click)
        self.testr_btn = wx.Button(self, label="Find camera controls")
        self.testr_btn.SetToolTip("Read the selected camera's controls; keep your current values.")
        self.testr_btn.Bind(wx.EVT_BUTTON, self.get_opt_list)
        tools = wx.BoxSizer(wx.HORIZONTAL)
        tools.Add(self.test_btn, 0, wx.RIGHT, 6)
        tools.Add(self.testr_btn, 0)
        self.status_label = wx.StaticText(self, label="")
        self.status_label.Wrap(410)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.label, 0, wx.BOTTOM, 8)
        self.main_sizer.Add(tools, 0, wx.BOTTOM, 6)
        self.main_sizer.Add(self.status_label, 0, wx.BOTTOM | wx.EXPAND, 4)
        self.status_label.Hide()
        self.main_sizer.Add(self.c_sets_sizer, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def create_settings_sizer(self, settings):
        return controls_grid(self, {**self.generic_settings_dict, **settings})

    def _rebuild_settings(self, values=None):
        if values is None:
            values = {key: control.GetValue() for key, control in self.setting_crtl_dict.items()}
        self.c_sets_sizer.Clear(delete_windows=True)
        grid, self.setting_crtl_dict, self.setting_t_dict = self.create_settings_sizer(self.device_settings_dict)
        self.c_sets_sizer.Add(grid, 0, wx.EXPAND)
        for key, value in values.items():
            if key in self.setting_crtl_dict:
                self.setting_crtl_dict[key].SetValue(value)
        self._layout_controls()

    def _layout_controls(self):
        self.Layout()
        self.parent.Layout()
        if hasattr(self.parent, "SetupScrolling"):
            self.parent.SetupScrolling(scrollToTop=False)

    def _show_status(self, message):
        self.status_label.SetLabel(message)
        self.status_label.Wrap(410)
        self.status_label.Show(bool(message))
        self._layout_controls()

    def _device_command(self, arguments):
        controls = self.parent.parent.dict_C_pnl.get("camera_pnl")
        device = controls.cam_cb.GetValue().strip() if controls is not None else ""
        # v4l2-ctl can target /dev/videoN or a numeric device identifier.
        suffix = " --device " + shlex.quote(device) if device else ""
        return "v4l2-ctl " + arguments + suffix

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
            out, error = self.parent.parent.link_pnl.run_on_pi("sudo apt-get install fswebcam --force-yes -y")
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
            out, error = self.parent.parent.link_pnl.run_on_pi("sudo apt-get install fswebcam --force-yes -y")
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
        if version is not None and candidate is not None:
            if version == candidate:
                return "current"
            else:
                return "updatable"

    def get_resolutions_click(self, event):
        out, error = self.parent.parent.link_pnl.run_on_pi(self._device_command("--list-formats-ext"))
        resolutions = []
        for line in out.splitlines():
            if "Size:" not in line:
                continue
            # Both discrete sizes and endpoints of continuous/stepwise ranges.
            for width, height in re.findall(r"(\d+)\s*x\s*(\d+)", line):
                resolution = width + "x" + height
                if resolution not in resolutions:
                    resolutions.append(resolution)
        if not resolutions:
            self._show_status("No resolutions returned. Check the selected camera and that v4l-utils is installed.")
            return
        control = self.setting_crtl_dict["resolution"]
        current = control.GetValue()
        resolutions.sort(key=lambda item: tuple(int(number) for number in item.split("x")), reverse=True)
        control.SetItems(resolutions)
        control.SetValue(current)
        self._show_status("Found %d resolutions. You can also type custom dimensions." % len(resolutions))

    def make_line_dict(self, line):
        return dict(re.findall(r"(\w+)=([^\s]+)", line))

    def parse_device_controls(self, output):
        settings = {}
        lines = output.splitlines()
        for index, line in enumerate(lines):
            match = re.match(r"\s*(\S+)\s+0x[0-9a-fA-F]+\s+\(([^)]+)\)\s*:", line)
            if match is None:
                continue
            setting, kind = match.groups()
            metadata = self.make_line_dict(line)
            if "read-only" in line or "read_only" in line:
                continue
            value = metadata.get("value", metadata.get("default", ""))
            hint = "Camera control: " + setting
            if kind in ("int", "int64") and "min" in metadata and "max" in metadata:
                try:
                    minimum, maximum = int(metadata["min"]), int(metadata["max"])
                    if minimum >= maximum:
                        continue
                    settings[setting] = [value, (minimum, maximum), hint]
                except ValueError:
                    continue
            elif kind == "bool":
                value = "False" if value == "0" else "True" if value else ""
                settings[setting] = [value, ["True", "False"], hint]
            elif kind in ("menu", "intmenu"):
                choices, numbered = [], {}
                for menu_line in lines[index + 1:]:
                    menu = re.match(r"\s*(\d+)\s*:\s*(.+)", menu_line)
                    if menu is None:
                        if menu_line.strip():
                            break
                        continue
                    number, name = menu.groups()
                    name = re.sub(r"\s+\(0x[0-9a-fA-F]+\)$", "", name).strip()
                    numbered[number] = name
                    choices.append(name)
                settings[setting] = [numbered.get(value, value), choices, hint]
            elif kind in ("str", "string", "bitmask"):
                settings[setting] = [value, "", hint]
        return settings

    def get_opt_list(self, event):
        out, error = self.parent.parent.link_pnl.run_on_pi(self._device_command("--list-ctrls-menus"))
        discovered = self.parse_device_controls(out)
        if not discovered:
            self._show_status("No editable controls returned. Check the selected camera and that v4l-utils is installed.")
            return
        self.device_settings_dict.update(discovered)
        self._rebuild_settings()
        self._show_status("Found %d camera controls. Your current settings have been kept." % len(discovered))
        controls = self.parent.parent.dict_C_pnl.get("camera_pnl")
        if controls is not None:
            controls.camcap_combo_go(None)

    def make_conf_text(self, setting_dict):
        return serialize_settings(self, setting_dict, self._sync_legacy_extra)

    def old_make_conf_text(self, setting_dict):
        return self.make_conf_text(setting_dict)

    @staticmethod
    def _legacy_extra_assignments(extra):
        # Keep source spans so changing a legacy --set value does not rewrite
        # unrelated options, shell quoting, or whitespace in fsw_extra.
        word_pattern = r'''(?:[^\s"'\\]|\\.|"(?:\\.|[^"\\])*"|'[^']*')+'''
        words = list(re.finditer(word_pattern, extra))
        tokens = []
        for word in words:
            try:
                tokens.append(shlex.split(word.group(), comments=False)[0])
            except (ValueError, IndexError):
                tokens.append(None)
        assignments = []
        for index, word in enumerate(words[:-1]):
            if tokens[index] != "--set":
                continue
            end_index = index + 1
            while end_index + 1 < len(words):
                next_token = tokens[end_index + 1]
                if next_token is None or re.match(r"--?[A-Za-z]", next_token):
                    break
                end_index += 1
            argument = " ".join(token for token in tokens[index + 1:end_index + 1] if token is not None)
            if "=" in argument:
                key, value = argument.split("=", 1)
                assignments.append((key.strip(), value.strip(), word.start(), words[end_index].end(), words[index + 1].start()))
        return assignments

    def _sync_legacy_extra(self, values):
        extra = str(values.get("fsw_extra", ""))
        aliases = {"b_val": "brightness", "c_val": "contrast", "s_val": "saturation",
                   "g_val": "gain", "x_dim": "resolution", "y_dim": "resolution"}
        for key, old_value, start, end, argument_start in reversed(self._legacy_extra_assignments(extra)):
            if key in values:
                value = str(values[key])
                if value != old_value:
                    argument = shlex.quote(key) + "=" + shlex.quote(value)
                    extra = extra[:argument_start] + argument + extra[end:]
            elif key in self.setting_crtl_dict:
                # A cleared control should be omitted from both config forms.
                extra = extra[:start] + extra[end:]
            elif aliases.get(key) in self.setting_crtl_dict and aliases[key] not in values:
                extra = extra[:start] + extra[end:]
        if "fsw_extra" in values:
            values["fsw_extra"] = extra
        return values

    def text_into_ui(self, set_text):
        settings = parse_settings(set_text)
        # Legacy extra settings take precedence in camcap.fs_sets_trim. Expose
        # their effective values so editing the modern control still works.
        for key, value, *_ in self._legacy_extra_assignments(settings.get("fsw_extra", "")):
            settings[key] = value
        aliases = {"b_val": "brightness", "s_val": "saturation", "c_val": "contrast", "g_val": "gain"}
        for old, new in aliases.items():
            if old in settings and new not in settings:
                settings[new] = settings[old]
        if "resolution" not in settings and "x_dim" in settings and "y_dim" in settings:
            settings["resolution"] = settings["x_dim"] + "x" + settings["y_dim"]
        legacy = {"cam_num", "cam_opt", "x_dim", "y_dim", "b_val", "c_val", "s_val", "g_val", "fsw_extra", "uvc_extra"}
        for key, value in settings.items():
            if key not in self.generic_settings_dict and key not in self.device_settings_dict and key not in legacy:
                self.device_settings_dict[key] = [value, "", "Camera-specific setting from this configuration."]
        previous = {key: control.GetValue() for key, control in self.setting_crtl_dict.items()}
        self._rebuild_settings(previous)
        load_settings(self, set_text, aliases=False)
        for key, value in settings.items():
            if key in self.setting_crtl_dict:
                self.setting_crtl_dict[key].SetValue(value)

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
