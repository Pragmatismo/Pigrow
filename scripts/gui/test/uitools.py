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



class ScriptConfigTool(wx.Panel):
    """
    A panel that introspects a Python script for flags and dynamically generates controls,
    including support for special lists and commands.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._original_cmd = ''
        # mappings for special handlers
        self.special_lists = {"LED NAME": self.get_led_name}
        self.special_commands = {"PATH": self.path_ctrl}
        # dict to store main controls
        self.controls = {}

        # sizer for dynamic option rows
        self.opts_sizer = wx.BoxSizer(wx.VERTICAL)
        # placeholder for raw flags output
        self.placeholder = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN
        )

        # assemble main layout
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.opts_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.placeholder, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(self.main_sizer)

        self.Enable(False)

    def update_command(self, cmd):
        self._original_cmd = cmd
        # clear existing controls
        self.opts_sizer.Clear(True)
        for k in list(self.controls):
            del self.controls[k]

        raw = ''
        opts = {}
        if self.has_flags_flag(cmd):
            raw = self.get_script_flags(cmd)
            for line in raw.splitlines():
                if '=' in line:
                    key, val = line.split('=', 1)
                    opts[key.strip()] = val.strip()

        # build a row for each option
        for key, val in opts.items():
            row = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(self, label=key)
            row.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
            ctrl_main = None
            # special list: [<TAG>]
            if val.startswith('[<') and val.endswith('>]'):
                tag = val[2:-2]
                if tag in self.special_lists:
                    items = self.special_lists[tag]()
                    combo = wx.ComboBox(self, choices=items)
                    if items:
                        combo.SetStringSelection(items[0])
                    row.Add(combo, 1, wx.EXPAND)
                    ctrl_main = combo
            # normal list: [a, b, c]
            elif val.startswith('[') and val.endswith(']'):
                items = [i.strip() for i in val[1:-1].split(',')]
                combo = wx.ComboBox(self, choices=items)
                if items:
                    combo.SetStringSelection(items[0])
                row.Add(combo, 1, wx.EXPAND)
                ctrl_main = combo
            # special command: <TAG>
            elif val.startswith('<') and val.endswith('>'):
                tag = val[1:-1]
                if tag in self.special_commands:
                    ctrl_sizer, ctrl = self.special_commands[tag]()
                    row.Add(ctrl_sizer, 1, wx.EXPAND)
                    ctrl_main = ctrl
            # free text
            else:
                txt = wx.TextCtrl(self, value=val)
                row.Add(txt, 1, wx.EXPAND)
                ctrl_main = txt

            if ctrl_main:
                self.controls[key] = ctrl_main
            self.opts_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 2)

        # update raw flags placeholder
        if raw:
            self.placeholder.SetValue(f"Flags for `{cmd}`:\n\n{raw}")
        else:
            self.placeholder.SetValue("No flag‐introspection tag found, automatic options not supported.")
        self.Layout()
        self.Enable(True)

    def get_script_flags(self, cmd):
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(f"{cmd} -flags")
        return out

    def has_flags_flag(self, cmd):
        out, error = self.parent.parent.parent.link_pnl.run_on_pi(f"cat {cmd}")
        for line in out.splitlines():
            if line.strip() == "#Flags output enabled":
                return True
        return False

    def reset(self):
        self._original_cmd = ''
        self.controls.clear()
        self.opts_sizer.Clear(True)
        self.placeholder.Clear()
        self.Enable(False)

    def is_unchanged(self, current_cmd):
        return current_cmd == self._original_cmd

    # example special handlers
    def get_led_name(self):
        return ['test 1', 'test 2', 'test 3']

    def path_ctrl(self):
        """
        Returns a sizer and a text control for file path selection.
        """
        hs = wx.BoxSizer(wx.HORIZONTAL)
        txt = wx.TextCtrl(self)
        btn = wx.Button(self, label="...")
        def on_browse(evt):
            dlg = wx.FileDialog(self, message="Select file")
            if dlg.ShowModal() == wx.ID_OK:
                txt.SetValue(dlg.GetPath())
            dlg.Destroy()
        btn.Bind(wx.EVT_BUTTON, on_browse)
        hs.Add(txt, 1, wx.EXPAND | wx.RIGHT, 5)
        hs.Add(btn, 0)
        return hs, txt