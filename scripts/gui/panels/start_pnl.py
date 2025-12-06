import os
import wx
import sys
import importlib


class ctrl_pnl(wx.Panel):
    '''
    The controls for the start panel
    '''

    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        super().__init__(parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour((100, 150, 170))

        # Create Datawall checkbox
        self.cbCreateDatawall = wx.CheckBox(self, label="Create Datawall")
        init_val = self.shared_data.gui_set_dict.get('start_datawall', "False")
        if str(init_val).lower() == 'true':
            self.cbCreateDatawall.SetValue(1)
        self.cbCreateDatawall.Bind(wx.EVT_CHECKBOX, self.onToggleCreateDatawall)

        # Select Preset button
        self.btnSelectPreset = wx.Button(self, label="Select Datawall Preset")
        self.btnSelectPreset.Bind(wx.EVT_BUTTON, self.onSelectPreset)

        # Refresh Datawall button
        self.btnRefreshDatawall = wx.Button(self, label="Refresh Datawall")
        self.btnRefreshDatawall.Bind(wx.EVT_BUTTON, self.onRefreshDatawall)

        # Datawall status / error note
        self.datawall_note = wx.StaticText(self, label="")
        self.datawall_note.Wrap(250)

        # Layout: center controls vertically & horizontally
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.cbCreateDatawall, 0, wx.ALIGN_CENTER_HORIZONTAL)
        sizer.Add(self.btnSelectPreset, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 10)
        sizer.Add(self.btnRefreshDatawall, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 10)
        sizer.Add(self.datawall_note, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 10)
        sizer.AddStretchSpacer(1)
        self.SetSizer(sizer)

    def onToggleCreateDatawall(self, event):
        val = self.cbCreateDatawall.GetValue()
        self.shared_data.gui_set_dict['start_datawall'] = str(val)

    def onSelectPreset(self, event):
        dlg = DatawallPresetDialog(self, self.shared_data)
        if dlg.ShowModal() == wx.ID_OK:
            # preset stored in gui_set_dict inside dialog
            pass
        dlg.Destroy()

    def onRefreshDatawall(self, event):
        '''User-requested rebuild of the datawall.'''
        self.connect_to_pigrow()

    def connect_to_pigrow(self):
        '''
        Called whenever a connection to a PiGrow is made.
        If Datawall creation is enabled, build it using the stored preset.
        '''
        # Only proceed if user enabled datawall
        if not self.shared_data.gui_set_dict.get('start_datawall', "False") == "True":
            return

        # Clear previous note
        self.datawall_note.SetLabel("")

        # Retrieve chosen preset
        preset = self.shared_data.config_dict.get('gui_datawall', '')
        if not preset:
            preset = self.shared_data.gui_set_dict.get('default_datawall', '')
        if not preset:
            preset = self.shared_data.gui_set_dict.get('start_datawall_preset', '')

        # If no preset, nothing to build
        if not preset:
            return

        print(f"Wants to create datawall using preset: {preset}")

        # Load preset file lines
        preset_path = os.path.join("./datawall_presets", f"datawall_{preset}.txt")
        if not os.path.isfile(preset_path):
            print(f"Preset file not found: {preset_path}")
            return
        with open(preset_path, encoding="utf-8") as f:
            preset_lines = f.read().splitlines()

        # Build the data package
        error_notes = []
        data_pkg = self.parent.dict_C_pnl['datawall_pnl'].create_datawall_data(
            preset_lines, show_dialog=False, error_collector=error_notes
        )

        if error_notes:
            note = "Error creating datawall; " + ", ".join(error_notes)
            self.datawall_note.SetLabel(note)
            self.Layout()

        # Extract module name from preset
        module_name = None
        for line in preset_lines:
            if line.startswith("module="):
                module_name = line.split("=", 1)[1].strip()
                print("creaing dtawallwith with ", module_name)
                break
        if not module_name:
            print("No 'module=' entry in preset; cannot import datawall module.")
            return
        # Import and run the datawall module
        full_mod = f"datawall_{module_name}"
        mod_path = os.path.abspath("./datawall_modules")
        if mod_path not in sys.path:
            sys.path.insert(0, mod_path)
        try:
            if full_mod in sys.modules:
                importlib.reload(sys.modules[full_mod])
                m = sys.modules[full_mod]
            else:
                m = importlib.import_module(full_mod)
            # Run make_datawall; no extra settings
            output = m.make_datawall(data_pkg, opts={})
            print(f"Datawall created at: {output}")
            dw_i_pnl = self.parent.dict_I_pnl['start_pnl']
            dw_i_pnl.display_image = output
            dw_i_pnl.Refresh()
            dw_i_pnl.Update()
            if error_notes:
                note = "Error creating datawall; " + ", ".join(error_notes)
                self.datawall_note.SetLabel(note)
                self.Layout()
        except Exception as e:
            print(f"Error creating datawall module '{full_mod}': {e}")
            if error_notes:
                note = "Error creating datawall; " + ", ".join(error_notes)
                self.datawall_note.SetLabel(note)
                self.Layout()



    def _get_presets(self):
        """
        Scan ./datawall_presets for files named datawall_*.txt, return names without prefix/suffix
        """
        presets_dir = "./datawall_presets"
        presets = []
        if not os.path.isdir(presets_dir):
            return presets
        for fn in os.listdir(presets_dir):
            if fn.startswith("datawall_") and fn.endswith(".txt"):
                name = fn[len("datawall_"):-4]
                presets.append(name)
        return sorted(presets)


class DatawallPresetDialog(wx.Dialog):
    def __init__(self, parent, shared_data):
        super().__init__(parent, title="Select Datawall Preset")
        self.shared_data = shared_data

        # Dropdown of all presets
        presets = parent._get_presets()
        self.choicePreset = wx.Choice(self, choices=presets)
        if presets:
            current_preset = shared_data.config_dict.get(
                'gui_datawall',
                shared_data.gui_set_dict.get('default_datawall', "")
            )
            try:
                self.choicePreset.SetStringSelection(current_preset)
            except wx.wxAssertionError:
                self.choicePreset.SetSelection(0)

        # Checkbox: set as global default
        self.cbSetAll = wx.CheckBox(self, label="Set as global default")
        self.cbSetAll.SetValue(True)

        # Set & Cancel buttons
        btnOk     = wx.Button(self, wx.ID_OK,     label="Set")
        btnCancel = wx.Button(self, wx.ID_CANCEL, label="Cancel")
        btnOk.Bind(wx.EVT_BUTTON,     self.onOk)
        btnCancel.Bind(wx.EVT_BUTTON, self.onCancel)

        # Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.choicePreset, 0, wx.EXPAND|wx.ALL, 10)
        main_sizer.Add(self.cbSetAll,     0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddStretchSpacer(1)
        btn_sizer.Add(btnOk,     0, wx.ALL, 5)
        btn_sizer.Add(btnCancel, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 10)

        self.SetSizerAndFit(main_sizer)

    def onOk(self, event):
        sel = self.choicePreset.GetStringSelection()
        self.shared_data.gui_set_dict['start_datawall_preset'] = sel
        self.shared_data.config_dict['gui_datawall'] = sel

        if self.cbSetAll.GetValue():
            prev_default = self.shared_data.gui_set_dict.get('default_datawall', "")
            self.shared_data.gui_set_dict['default_datawall'] = sel
            if sel != prev_default:
                self.shared_data.save_gui_settings()

        if getattr(self.shared_data, 'remote_pigrow_path', ""):
            self.shared_data.update_pigrow_config_file_on_pi()
        self.EndModal(wx.ID_OK)

    def onCancel(self, event):
        self.EndModal(wx.ID_CANCEL)


class info_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.display_image = "./ui_images/splash.png"
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170))
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    def OnEraseBackground(self, evt):
            dc = evt.GetDC()
            if not dc:
                dc = wx.ClientDC(self)
                rect = self.GetUpdateRegion().GetBox()
                dc.SetClippingRect(rect)

            dc.Clear()
            img = wx.Image(self.display_image, wx.BITMAP_TYPE_ANY)
            img = img.Scale(self.GetSize().GetWidth(), self.GetSize().GetHeight(), wx.IMAGE_QUALITY_HIGH)
            bmp = img.ConvertToBitmap()
            dc.DrawBitmap(bmp, 0, 0)
