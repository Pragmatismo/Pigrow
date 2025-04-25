import wx

class MakeDynamicOptPnl(wx.Panel):
    """
    A panel that dynamically constructs controls based on a provided options dictionary.

    Usage:
        panel = MakeDynamicOptPnl(parent)
        panel.build(options_dict)
        # ... add panel to sizer/layout ...
        settings = panel.get_settings()
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.controls = {}
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

    def build(self, options_dict):
        print("making table thing")
        """
        Construct controls for each key/value in options_dict.
        Clears any existing controls.
        """
        # Clear existing controls from sizer
        self.main_sizer.Clear(True)
        self.controls.clear()

        # Create a grid sizer: two columns (label + control)
        grid = wx.FlexGridSizer(rows=len(options_dict), cols=2, hgap=5, vgap=5)
        grid.AddGrowableCol(1, 1)

        for key, value in options_dict.items():
            # Label
            label = wx.StaticText(self, label=key)
            grid.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)

            # Determine control type
            ctrl = self._make_control_for_value(value)
            grid.Add(ctrl, 1, wx.EXPAND | wx.ALL, 2)

            # Store control
            self.controls[key] = ctrl

        # Add grid to main sizer and refresh layout
        self.main_sizer.Add(grid, 1, wx.EXPAND | wx.ALL, 5)
        self.Layout()

    def _make_control_for_value(self, value):
        # Boolean -> CheckBox
        if isinstance(value, str) and value.lower() in ('true', 'false'):
            cb = wx.CheckBox(self)
            cb.SetValue(value.lower() == 'true')
            return cb
        # List or tuple -> ComboBox
        elif isinstance(value, (list, tuple)):
            combo = wx.ComboBox(self, choices=[str(v) for v in value])
            if value:
                combo.SetStringSelection(str(value[0]))
            return combo
        # Default -> TextCtrl
        else:
            return wx.TextCtrl(self, value=str(value))

    def get_settings(self):
        """
        Read current values from controls and return as a dict.
        """
        settings = {}
        for key, ctrl in self.controls.items():
            if isinstance(ctrl, wx.CheckBox):
                settings[key] = 'true' if ctrl.GetValue() else 'false'
            elif isinstance(ctrl, wx.ComboBox):
                settings[key] = ctrl.GetValue()
            elif isinstance(ctrl, wx.TextCtrl):
                settings[key] = ctrl.GetValue()
            else:
                # Unknown control type
                settings[key] = None
        return settings
