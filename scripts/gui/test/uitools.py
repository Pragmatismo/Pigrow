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
    A panel that introspects a Python script for flags and defaults,
    generates controls, highlights required fields, and builds a command.
    """
    MAGIC_TAG = "#Flags output enabled"

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._original_cmd = ''
        self._order = []       # to remember flag order
        self.flags = {}        # key -> flag format value
        self.defaults = {}     # key -> default format value
        self.controls = {}     # key -> main wx.Control

        # special handlers
        self.special_lists = {"LED NAME": self.get_led_name}
        self.special_commands = {"PATH": self.path_ctrl}

        self.opts_sizer = wx.BoxSizer(wx.VERTICAL)
        self.raw_output = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SUNKEN
        )

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.opts_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.raw_output, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.Enable(False)

    def update_command(self, cmd):
        """Re-introspect script for flags and defaults, rebuild controls."""
        self._original_cmd = cmd
        self._order.clear()
        self.flags.clear()
        self.defaults.clear()

        # clear old controls
        self.opts_sizer.Clear(True)
        self.controls.clear()

        # fetch flags
        raw_flags = self._run(f"{cmd} -flags")
        for line in raw_flags.splitlines():
            if '=' in line:
                key, val = line.split('=', 1)
                self.flags[key] = val
                self._order.append(key)

        # fetch defaults
        raw_defs = self._run(f"{cmd} -defaults")
        for line in raw_defs.splitlines():
            if '=' in line:
                key, val = line.split('=', 1)
                self.defaults[key] = val

        # build rows
        for key in self._order:
            flag_val = self.flags.get(key, '')
            def_val  = self.defaults.get(key, '')

            row = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(self, label=key)
            row.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

            ctrl = None
            # [<TAG>] → special list
            if flag_val.startswith('[<') and flag_val.endswith('>]'):
                tag = flag_val[2:-2]
                items = self.special_lists.get(tag, lambda: [])()
                combo = wx.ComboBox(self, choices=items)
                row.Add(combo, 1, wx.EXPAND)
                ctrl = combo

            # [a,b,c] → dropdown
            elif flag_val.startswith('[') and flag_val.endswith(']'):
                items = [i.strip() for i in flag_val[1:-1].split(',') if i.strip()]
                combo = wx.ComboBox(self, choices=items)
                row.Add(combo, 1, wx.EXPAND)
                ctrl = combo

            # <TAG> → special command control
            elif flag_val.startswith('<') and flag_val.endswith('>'):
                tag = flag_val[1:-1]
                creator = self.special_commands.get(tag)
                if creator:
                    sizer, ctrl_widget = creator()
                    row.Add(sizer, 1, wx.EXPAND)
                    ctrl = ctrl_widget

            # free text
            else:
                txt = wx.TextCtrl(self, value='')
                row.Add(txt, 1, wx.EXPAND)
                ctrl = txt

            # initialize control value & style
            if ctrl:
                has_default = key in self.defaults
                raw_def = self.defaults.get(key, '')
                def_str = raw_def.strip().strip('"').strip("'")

                if has_default and def_str:
                    # optional argument with a non‐empty default
                    ctrl.SetValue(def_str)
                    ctrl.SetBackgroundColour(wx.NullColour)

                elif has_default and not def_str:
                    # required argument (explicitly in defaults but blank)
                    ctrl.SetValue('')
                    ctrl.SetBackgroundColour(wx.Colour(255, 200, 200))

                else:
                    # not mentioned in defaults at all → leave blank, normal style
                    ctrl.SetValue('')
                    ctrl.SetBackgroundColour(wx.NullColour)

                # bind change to clear red when filled
                ctrl.Bind(wx.EVT_TEXT, lambda evt, k=key: self._on_value_change(k))
                self.controls[key] = ctrl

            self.opts_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 2)

        # show raw flags & defaults
        self.raw_output.SetValue(
            f"Flags (`-flags`):\n{raw_flags}\n\nDefaults (`-defaults`):\n{raw_defs}"
        )

        self.Layout()
        self.Enable(True)

    def _run(self, cmd):
        """Helper to run via remote link_pnl; returns stdout or empty."""
        out, err = self.parent.parent.parent.link_pnl.run_on_pi(cmd)
        return out or ''

    def _on_value_change(self, key):
        ctrl = self.controls.get(key)
        if not ctrl:
            return
        current = ctrl.GetValue().strip()
        raw_def = self.defaults.get(key, None)
        # only for keys explicitly in defaults with empty default:
        if (raw_def is not None) and (raw_def.strip() == '') and current:
            ctrl.SetBackgroundColour(wx.NullColour)
            self.Refresh()

    def get_command_string(self):
        """Compose: original_cmd + only args that differ from default/nonblank."""
        parts = [self._original_cmd]
        for key in self._order:
            ctrl = self.controls.get(key)
            if not ctrl:
                continue
            val = ctrl.GetValue().strip()
            def_val = self.defaults.get(key, '').strip().strip('"').strip("'")
            # include if required (def_val=='') and filled, or optional but changed
            if val and val != def_val:
                # quote if contains space
                v = f"\"{val}\"" if ' ' in val else val
                parts.append(f"{key}={v}")
        return " ".join(parts)

    # --- example special handlers ---
    def get_led_name(self):
        return ['test 1', 'test 2', 'test 3']

    def path_ctrl(self):
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
