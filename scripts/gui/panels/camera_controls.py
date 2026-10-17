"""Compact, editable camera settings widgets shared by the capture panels."""

import math
from decimal import Decimal, InvalidOperation
import wx


_LABELS = {
    "fs_delay": "Capture delay (s)",
    "fs_fskip": "Skip frames",
    "fs_jpg_q": "JPEG quality",
    "fs_banner": "Show date banner",
    "iso": "ISO sensitivity",
    "ev": "Exposure compensation",
    "awb": "White balance",
    "awb_mode": "White balance",
    "awbgains": "White balance gains",
    "roi": "Crop region",
    "hflip": "Flip horizontally",
    "vflip": "Flip vertically",
    "drc_strength": "Dynamic range",
    "exposure_speed": "Shutter speed (µs)",
    "shutter": "Shutter speed (µs)",
    "lens-position": "Lens position",
    "hdr": "HDR",
}


def readable_label(setting):
    return _LABELS.get(setting, setting.replace("_", " ").replace("-", " ").capitalize())


class NumericControl(wx.Panel):
    """A slider with a precise, immediately applied editable numeric value.

    The slider's range is a suggestion, rather than a restriction on values read
    from a config file. This keeps camera-specific and future ranges usable.
    """

    def __init__(self, parent, setting, value, minimum, maximum, integer=True):
        super().__init__(parent)
        self.SetLabel(setting)
        self.is_integer = integer
        self.minimum = minimum
        self.maximum = maximum
        self._last_value = ""
        self._tooltip = ""
        self._direct = integer and -2147483648 <= minimum < maximum <= 2147483647
        slider_min, slider_max = (int(minimum), int(maximum)) if self._direct else (0, 1000)
        self.slider = wx.Slider(self, minValue=slider_min, maxValue=slider_max)
        self.slider.SetMinSize((90, -1))
        self.text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self._normal_background = self.text.GetBackgroundColour()
        self.text.SetMinSize((76, -1))
        self.text.SetMaxSize((110, -1))
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.slider, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        row.Add(self.text, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(row)
        self.slider.Bind(wx.EVT_SLIDER, self._on_slider)
        self.text.Bind(wx.EVT_TEXT, self._on_text)
        self.text.Bind(wx.EVT_TEXT_ENTER, self._on_commit)
        self.text.Bind(wx.EVT_KILL_FOCUS, self._on_commit)
        self.SetValue(value)

    def GetMin(self):
        return self.minimum

    def GetMax(self):
        return self.maximum

    def _number(self, value):
        if str(value).strip() == "":
            return ""
        if self.is_integer:
            try:
                number = Decimal(str(value))
                if not number.is_finite() or number != int(number):
                    raise ValueError("Enter a whole number")
            except (InvalidOperation, OverflowError) as error:
                raise ValueError("Enter a whole number") from error
            return int(number)
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Invalid numeric value")
        return number

    def _mark_invalid(self, invalid):
        self.text.SetBackgroundColour(wx.Colour(255, 226, 226) if invalid else self._normal_background)
        expected = "a whole number" if self.is_integer else "a number"
        self.text.SetToolTip(("Enter %s, or leave blank.\n" % expected if invalid else "") + self._tooltip)
        self.text.Refresh()

    def _sync_slider(self, value):
        if value == "":
            return
        value = max(self.minimum, min(self.maximum, value))
        if self._direct:
            position = int(value)
        elif self.maximum == self.minimum:
            position = 0
        else:
            position = round((value - self.minimum) / (self.maximum - self.minimum) * 1000)
        self.slider.SetValue(position)

    def SetValue(self, value):
        # Keep the original text (and precision) when loading a configuration.
        self.text.ChangeValue(str(value))
        try:
            number = self._number(value)
        except (ValueError, OverflowError):
            self._mark_invalid(True)
            return
        self._last_value = str(value)
        self._mark_invalid(False)
        self._sync_slider(number)

    def GetValue(self):
        try:
            number = self._number(self.text.GetValue())
        except (ValueError, OverflowError):
            self.text.ChangeValue(self._last_value)
            number = self._number(self._last_value)
        self._mark_invalid(False)
        self._last_value = self.text.GetValue()
        return number

    def SetToolTip(self, tip):
        self._tooltip = str(tip) + "\nSuggested range: %s to %s. You can type camera-specific values." % (self.minimum, self.maximum)
        super().SetToolTip(self._tooltip)
        self.slider.SetToolTip(self._tooltip)
        self.text.SetToolTip(self._tooltip)

    def _on_slider(self, event):
        position = self.slider.GetValue()
        if self._direct:
            value = position
        else:
            value = self.minimum + (self.maximum - self.minimum) * position / 1000
            value = round(value) if self.is_integer else round(value, 6)
        self.SetValue(value)

    def _on_text(self, event):
        try:
            number = self._number(self.text.GetValue())
        except (ValueError, OverflowError):
            self._mark_invalid(True)
            event.Skip()
            return
        self._mark_invalid(False)
        self._last_value = self.text.GetValue()
        self._sync_slider(number)
        event.Skip()

    def _on_commit(self, event):
        self.GetValue()
        event.Skip()


class SettingsGrid(wx.FlexGridSizer):
    """Two aligned columns without a permanently empty third notes column."""

    def __init__(self, parent):
        super().__init__(cols=2, vgap=5, hgap=12)
        self.parent = parent
        self.AddGrowableCol(1, 1)

    def add_setting(self, setting, control, auxiliary=None, tooltip=""):
        label = wx.StaticText(self.parent, label=readable_label(setting))
        tip = setting + ("\n" + tooltip if tooltip else "")
        label.SetToolTip(tip)
        control.SetToolTip(tip)
        self.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
        if auxiliary is None:
            self.Add(control, 1, wx.EXPAND)
        else:
            row = wx.BoxSizer(wx.HORIZONTAL)
            row.Add(control, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
            row.Add(auxiliary, 0, wx.ALIGN_CENTER_VERTICAL)
            self.Add(row, 1, wx.EXPAND)
        return label


def create_setting(parent, setting, value, options, tooltip=""):
    if isinstance(options, list):
        control = wx.ComboBox(parent, value=str(value), choices=[str(item) for item in options])
    elif isinstance(options, tuple):
        minimum, maximum = options
        integer = all(isinstance(item, int) for item in options)
        control = NumericControl(parent, setting, value, minimum, maximum, integer=integer)
    else:
        control = wx.TextCtrl(parent, value=str(value))
        if tooltip or options:
            control.SetHint(tooltip or str(options))
    control.SetMinSize((200, -1))
    label = wx.StaticText(parent, label=readable_label(setting))
    tip = setting + ("\n" + tooltip if tooltip else "")
    label.SetToolTip(tip)
    control.SetToolTip(tip)
    return label, control, None


def controls_grid(parent, settings):
    grid = SettingsGrid(parent)
    controls, auxiliary = {}, {}
    for setting, spec in settings.items():
        value, options = spec[:2]
        tooltip = spec[2] if len(spec) > 2 else (options if isinstance(options, str) else "")
        label, control, extra = create_setting(parent, setting, value, options, tooltip)
        grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
        grid.Add(control, 1, wx.EXPAND)
        controls[setting] = control
        auxiliary[setting] = extra
    return grid, controls, auxiliary


def parse_settings(text):
    settings = {}
    for line in text.splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings


def load_settings(panel, text, aliases=True):
    settings = parse_settings(text)
    panel.camera_settings_dict = settings
    if aliases:
        if "resolution" not in settings and "x_dim" in settings and "y_dim" in settings:
            settings["resolution"] = settings["x_dim"] + "x" + settings["y_dim"]
        for old, new in (("b_val", "brightness"), ("c_val", "contrast"),
                         ("s_val", "saturation"), ("g_val", "iso")):
            if old in settings and new not in settings:
                settings[new] = settings[old]
    for key, value in settings.items():
        if key in panel.setting_crtl_dict:
            panel.setting_crtl_dict[key].SetValue(value)
    return settings


def serialize_settings(panel, controls, transforms=None):
    # Preserve settings not represented by this version of the UI. Camera and
    # tool selection are written separately by camera_pnl, from their controls.
    values = {key: value for key, value in getattr(panel, "camera_settings_dict", {}).items()
              if key not in controls and key not in ("cam_num", "cam_opt")}
    for key, control in controls.items():
        value = control.GetValue()
        if value != "":
            values[key] = value
    # A deliberately cleared modern control also clears its legacy fallback.
    # Otherwise old aliases silently restore a value at capture time.
    for modern, legacy in (("resolution", ("x_dim", "y_dim")),
                           ("Resolution", ("x_dim", "y_dim")),
                           ("brightness", ("b_val",)), ("contrast", ("c_val",)),
                           ("saturation", ("s_val",)), ("gain", ("g_val",)),
                           ("iso", ("g_val",))):
        if modern in controls and modern not in values:
            for key in legacy:
                values.pop(key, None)
    if transforms is not None:
        values = transforms(values)
    return "".join(str(key) + "=" + str(value) + "\n" for key, value in values.items())
