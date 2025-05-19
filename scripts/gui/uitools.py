import wx
import os
import re

class RunCmdDialog(wx.Dialog):
    def __init__(self, parent, cancel_button=False, start_text=None):
        super().__init__(parent, title="Run Command on Pi", size=(700, 500))
        self.parent = parent
        self._orig_cmd = ""
        self._use_ok_cancel = cancel_button
        self._start_text = start_text or ''
        # dict to hold parsed k=v args from start_text
        self._start_args = {}
        # parsed base command without k=v args
        self._parsed_base = ''
        self.InitUI()

    def _apply_start_text(self, text):
        """
        Extract k=v pairs from self._start_text into self._start_args,
        and set self._parsed_base to the remainder (script path + other flags).
        """
        args = {}
        # regex: key = value where value is quoted or unquoted
        pattern = re.compile(r"(\w+)=('.*?'|\".*?\"|\S+)")
        # find all key=value pairs
        for match in pattern.finditer(text):
            key = match.group(1)
            val = match.group(2)
            # strip quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            args[key] = val
        # remove args (and leading spaces) from text
        cleaned = re.sub(r"\s*(\w+=(?:'.*?'|\".*?\"|\S+))", "", text)
        self._start_args = args
        self._parsed_base = cleaned.strip()
        # set orig for later use
        self._orig_cmd = self._parsed_base
        return self._parsed_base, args

    def InitUI(self):
        # Top row: [command_text] [Browse] [Run]
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.command_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        # pre-fill text control
        if self._start_text:
            self.command_text.SetValue(self._start_text)
        self.command_text.Bind(wx.EVT_TEXT, self.OnCommandTextChanged)

        self.browse_btn = wx.Button(self, label="…", size=(30, -1))
        self.browse_btn.Bind(wx.EVT_BUTTON, self.OnBrowse)

        self.run_btn = wx.Button(self, label="Run")
        self.run_btn.Bind(wx.EVT_BUTTON, self.OnRun)

        top_sizer.Add(self.command_text, 1, wx.ALL | wx.EXPAND, 5)
        top_sizer.Add(self.browse_btn, 0, wx.ALL, 5)
        top_sizer.Add(self.run_btn, 0, wx.ALL, 5)

        # Buttons for Read Settings / Make Args
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.read_btn = wx.Button(self, label="Read Settings")
        self.read_btn.Bind(wx.EVT_BUTTON, self.OnRead)
        self.make_args_btn = wx.Button(self, label="Make Args")
        self.make_args_btn.Bind(wx.EVT_BUTTON, self.OnMakeArgs)
        buttons_sizer.Add(self.read_btn, 0, wx.EXPAND | wx.ALL, 5)
        buttons_sizer.Add(self.make_args_btn, 0, wx.EXPAND | wx.ALL, 5)

        # Script configuration panel
        self.script_config = ScriptConfigTool(self)

        # Output text area (read-only, multiline)
        self.output_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # OK / Cancel or Done button
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        if self._use_ok_cancel:
            ok_btn = wx.Button(self, wx.ID_OK, label="OK")
            cancel_btn = wx.Button(self, wx.ID_CANCEL, label="Cancel")
            btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
            btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        else:
            done_btn = wx.Button(self, label="Done")
            done_btn.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
            btn_sizer.Add(done_btn, 0, wx.ALL, 5)

        # Layout
        main_v = wx.BoxSizer(wx.VERTICAL)
        main_v.Add(top_sizer, 0, wx.EXPAND | wx.ALL, 5)
        main_v.Add(buttons_sizer, 0, wx.ALL, 5)
        main_v.Add(self.script_config, 1, wx.EXPAND | wx.ALL, 5)
        main_v.Add(self.output_text, 1, wx.EXPAND | wx.ALL, 5)
        main_v.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(main_v)

    def OnBrowse(self, event):
        selected_files, selected_folders = self.parent.parent.link_pnl.select_files_on_pi()
        if selected_files:
            remote_path = selected_files[0][0]
            ext = os.path.splitext(remote_path)[1].lower()
            cmd = "cat " + remote_path if ext == ".txt" else remote_path
            self.command_text.SetValue(cmd)

    def OnRead(self, event):
        cmd = self.command_text.GetValue().strip()
        if not cmd:
            wx.MessageBox("Enter or browse a command first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        base_cmd, args = self._apply_start_text(cmd)
        self._orig_cmd = base_cmd
        self.script_config.update_command(base_cmd, args)

    def OnMakeArgs(self, event):
        cmd_str = self.script_config.get_command_string()
        self.command_text.SetValue(cmd_str)

    def OnCommandTextChanged(self, event):
        current = self.command_text.GetValue()
        base_cmd, args = self._apply_start_text(current)
        self.script_config.Enable(base_cmd == self._orig_cmd)
        event.Skip()

    def OnRun(self, event):
        cmd = self.command_text.GetValue().strip()
        if not cmd:
            wx.MessageBox("Enter or browse a command first.", "Error", wx.OK | wx.ICON_ERROR)
            return
        # Execute the command on Pi and display output
        out, err = self.parent.parent.link_pnl.run_on_pi(cmd)
        result = (out or '') + (('\n' + err) if err else '')
        self.output_text.SetValue(result)

    def GetCommand(self):
        return self.command_text.GetValue()


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

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.opts_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.Enable(False)

    def update_command(self, cmd, args):
        """Re-introspect script for flags and defaults, rebuild controls, prefill from args."""
        self._original_cmd = cmd
        self._order.clear()
        self.flags.clear()
        self.defaults.clear()
        self.opts_sizer.Clear(True)
        self.controls.clear()

        raw_flags = self._run(f"{cmd} -flags")
        for line in raw_flags.splitlines():
            if '=' in line:
                key, val = line.split('=', 1)
                self.flags[key] = val
                self._order.append(key)

        raw_defs = self._run(f"{cmd} -defaults")
        for line in raw_defs.splitlines():
            if '=' in line:
                key, val = line.split('=', 1)
                self.defaults[key] = val

        for key in self._order:
            flag_val = self.flags.get(key, '')
            def_val = self.defaults.get(key, '')

            row = wx.BoxSizer(wx.HORIZONTAL)
            lbl = wx.StaticText(self, label=key)
            row.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)

            ctrl = None
            if flag_val.startswith('[<') and flag_val.endswith('>]'):
                tag = flag_val[2:-2]
                items = self.special_lists.get(tag, lambda: [])()
                ctrl = wx.ComboBox(self, choices=items)
                row.Add(ctrl, 1, wx.EXPAND)
            elif flag_val.startswith('[') and flag_val.endswith(']'):
                items = [i.strip() for i in flag_val[1:-1].split(',') if i.strip()]
                ctrl = wx.ComboBox(self, choices=items)
                row.Add(ctrl, 1, wx.EXPAND)
            elif flag_val.startswith('<') and flag_val.endswith('>'):
                tag = flag_val[1:-1]
                creator = self.special_commands.get(tag)
                if creator:
                    sizer, widget = creator()
                    ctrl = widget
                    row.Add(sizer, 1, wx.EXPAND)
            else:
                ctrl = wx.TextCtrl(self, value='')
                row.Add(ctrl, 1, wx.EXPAND)

            if ctrl:
                has_default = key in self.defaults
                raw_def = self.defaults.get(key, '')
                def_str = raw_def.strip().strip('"').strip("'")
                # initial set from default
                if has_default and def_str:
                    ctrl.SetValue(def_str)
                    ctrl.SetBackgroundColour(wx.NullColour)
                elif has_default and not def_str:
                    ctrl.SetValue('')
                    ctrl.SetBackgroundColour(wx.Colour(255, 200, 200))
                else:
                    ctrl.SetValue('')

                # override from start args if present
                if key in args:
                    ctrl.SetValue(args[key])
                    ctrl.SetBackgroundColour(wx.NullColour)

                ctrl.Bind(wx.EVT_TEXT, lambda evt, k=key: self._on_value_change(k))
                self.controls[key] = ctrl

            self.opts_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 2)

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
