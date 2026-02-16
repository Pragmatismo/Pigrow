import wx
#import wx.grid as gridlib
import wx.adv
import wx.lib.scrolledpanel as scrolled
import importlib
import os
import sys
from uitools import MakeDynamicOptPnl

class ctrl_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.parent = parent
        self.shared_data = parent.shared_data
        self.loaded_datasets = []
        self.datawall_data = {}

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Datawall")
        self.main_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # module selector
        self.module_choice = wx.Choice(self, choices=self.get_datawall_module_list())
        self.module_choice.Bind(wx.EVT_CHOICE, self.on_module_choice)
        h = wx.BoxSizer(wx.HORIZONTAL)
        h.Add(wx.StaticText(self, label="Module:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        h.Add(self.module_choice, 1, wx.EXPAND)
        self.main_sizer.Add(h, 0, wx.EXPAND | wx.ALL, 5)

        # preset panel (owns its own dropdown + save + dynamic controls)
        self.preset_options_panel = PresetOptionsPanel(self)
        self.main_sizer.Add(self.preset_options_panel, 0, wx.EXPAND | wx.ALL, 5)

        # Import / Create buttons
        self.import_btn = wx.Button(self, label="Import Data")
        self.import_btn.Bind(wx.EVT_BUTTON, self.on_import_data)

        self.create_btn = wx.Button(self, label="Create Datawall")
        self.create_btn.Disable()
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_run_datawall_module)

        btn_s = wx.BoxSizer(wx.HORIZONTAL)
        btn_s.Add(self.import_btn, 0, wx.RIGHT, 10)
        btn_s.Add(self.create_btn, 0)
        self.main_sizer.Add(btn_s, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # options area (unchanged)
        self.options_panel = MakeDynamicOptPnl(self)
        self.main_sizer.Add(self.options_panel, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.SetupScrolling(scroll_x=False, scroll_y=True)


    def on_module_choice(self, event):
        """When the user picks a datawall module, reload its options."""
        sel = self.module_choice.GetStringSelection()
        if not sel:
            return

        module_name = f"datawall_{sel}"
        module_dir = os.path.abspath("./datawall_modules")
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)

        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                m = sys.modules[module_name]
            else:
                m = importlib.import_module(module_name)
        except Exception as e:
            wx.MessageBox(f"Failed to load {module_name}:\n{e}",
                          "Error", wx.OK | wx.ICON_ERROR)
            return

        if hasattr(m, "read_datawall_options"):
            opts, preset_req = m.read_datawall_options()
            self.preset_options_panel.update_preset_panel(preset_req)
        else:
            opts, preset_req = {}, {}
            self.preset_options_panel.update_preset_panel(preset_req)
            self.options_panel.build(opts)
            self.create_btn.Disable()
            self.Layout()

        # rebuild the controls
        print("preest_req =", preset_req)
        self.options_panel.build(opts)
        self.Layout()

    def on_import_data(self, event):

        text = self.preset_options_panel.get_text()
        data = self.create_datawall_data(text)

        self.datawall_data = data
        self.create_btn.Enable()

    def create_datawall_data(self, text_lines, show_dialog=True, error_collector=None):
        """
        Given a list of preset lines (key=val strings),
        build and return the full data package.
        """
        data = {"info": {}, "images": {}, "data": {}, "graphs": {}}
        for line in text_lines:
            if "=" not in line:
                continue
            key, val = (s.strip() for s in line.split("=", 1))

            if key == "info_read":
                info = self.read_info_module(val)
                data["info"][val] = info

            elif key.startswith("picture_path"):
                data["images"][key[len("picture_path:"):]] = self.get_image(val)

            elif key.startswith("graph_preset"):
                gp = self.parent.dict_C_pnl['graphs_pnl'].create_graph_by_preset(val)
                data["graphs"][key[len("graph_preset:"):]] = gp or None

            elif key.startswith("log_preset"):
                ds = self.parent.dict_C_pnl['graphs_pnl'].graph_preset.load_dataset_preset(
                    self.parent.dict_C_pnl['graphs_pnl'], val, show_dialog=show_dialog, error_collector=error_collector
                )
                data["data"][key[len("log_preset:"):]] = ds or None

        return data


    def on_refresh(self, event):
        """Refresh both presets and modules lists."""
        # re-fetch options
        preset_opts = self.get_datawall_presets()
        module_opts = self.get_datawall_module_list()

        # update preset_choice
        self.preset_choice.Clear()
        if preset_opts:
            self.preset_choice.Append(preset_opts)
        else:
            # leave empty if none found
            pass

        # update module_choice
        self.module_choice.Clear()
        if module_opts:
            self.module_choice.Append(module_opts)

    def get_datawall_presets(self):
        print("NOTE: preset does not yet check for log availability")
        options = []
        directory = './datawall_presets'
        # check dir exists
        if not os.path.isdir(directory):
            print("Datawall Presets not found")
            return options
        # find datawall preset files
        for filename in os.listdir(directory):
            if filename.startswith('datawall_') and filename.endswith('.txt'):
                name = filename[9:-4]
                options.append(name)
        return options

    def read_info_module(self, module, prefix="info_"):
        args = ""
        if " " in module:
            e_pos = module.find(" ")
            args = module[e_pos:]
            module = module[:e_pos]
        # check name is in module format
        info_modules_path = self.shared_data.remote_pigrow_path + "scripts/gui/info_modules/"
        if not prefix in module:
            module = prefix + module
        if not ".py" in module:
            module += ".py"
        # module
        out, error = self.parent.link_pnl.run_on_pi(info_modules_path + module + args)
        print (out, error)
        return out.strip()

    def get_image(self, value):
        # find the image path
        info_o = self.read_info_module(value, "picture_")
        if info_o.lower().strip() == "none":
            print("No image found")
            return info_o
        # copy locally if required
        remote_path = info_o
        img_filename = info_o.split("/")[-1]
        img_fold = info_o.split("/")[-2]
        caps_path = os.path.join(self.shared_data.frompi_path, img_fold)
        local_img_path = os.path.join(caps_path, img_filename)

        if os.path.isfile(local_img_path):
            print("Image already exists locally")
        else:
            print("image not yet downloaaded locally")
            path_text = img_fold + "/" + img_filename
            print(f"Copying image for datawall from {remote_path} to {path_text}")
            self.parent.link_pnl.download_file_to_folder(remote_path,
                                                         img_fold + "/" + img_filename)

        return local_img_path

    def get_datawall_module_list(self):
        modules = []
        module_path = "./datawall_modules/"
        if os.path.isdir(module_path):
            for filename in os.listdir(module_path):
                if filename.startswith("datawall_") and filename.endswith(".py"):
                    name = filename[len("datawall_"):-3]
                    modules.append(name)
        return modules

    def on_run_datawall_module(self, event):
        selected = self.module_choice.GetStringSelection()
        if not selected:
            wx.MessageBox("Please select a datawall module.", "Error", wx.OK | wx.ICON_ERROR)
            return
        module_name = f"datawall_{selected}"
        module_path = os.path.abspath("./datawall_modules")
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        try:
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                module = sys.modules[module_name]
            else:
                module = importlib.import_module(module_name)
            # Call the module’s make_datawall() function, handing it the preset data.
            settings = self.options_panel.get_settings()
            output = module.make_datawall(self.datawall_data, opts=settings)
            print(f"Datawall module output: {output}")
            #
            if os.path.isfile(output):
                self.parent.dict_I_pnl['datawall_pnl'].display_image(output)
            else:
                wx.MessageBox(f"Datawall module output: {output}", "Info", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Error running datawall module: {e}", "Error", wx.OK | wx.ICON_ERROR)



class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['datawall_pnl']
        w = 1000
        # Initialize as a ScrolledPanel so that if the image is large the user can scroll.
        scrolled.ScrolledPanel.__init__(self, parent, size=(w, -1), id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self, label='Datawall')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This is in progress and subject to change."
        page_sub_title = wx.StaticText(self, label=sub_title_text)

        guide_btn = wx.Button(self, label='Guide')
        guide_btn.Bind(wx.EVT_BUTTON, self.show_guide)

        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(title_l, 0, wx.ALIGN_CENTER_VERTICAL)
        title_sizer.AddStretchSpacer(1)
        title_sizer.Add(guide_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Create an image box (using wx.StaticBitmap)
        self.image_box = wx.StaticBitmap(self, bitmap=wx.NullBitmap)
        # Initially, no image is loaded.
        self.main_sizer.Add(self.image_box, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.SetupScrolling()

    def display_image(self, image_path):
        """Load the image from image_path and display it in the image_box.
        The box is resized to fit the new image."""
        if not os.path.isfile(image_path):
            wx.MessageBox(f"Image file not found: {image_path}", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            # Load the image. The BITMAP_TYPE_ANY flag lets wxPython decide the type.
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        except Exception as e:
            wx.MessageBox(f"Failed to load image: {e}", "Error", wx.OK | wx.ICON_ERROR)
            return

        # (Optional) If you want to ensure the image is not too large, you can scale it here.
        # For example:
        # max_width, max_height = 800, 600
        # if img.GetWidth() > max_width or img.GetHeight() > max_height:
        #     img = img.Scale(max_width, max_height, wx.IMAGE_QUALITY_HIGH)

        bmp = wx.Bitmap(img)
        self.image_box.SetBitmap(bmp)
        # Resize the image box to match the bitmap dimensions.
        self.image_box.SetSize(bmp.GetWidth(), bmp.GetHeight())
        # Re-layout the panel to account for the new image size.
        self.main_sizer.Layout()

    def show_guide(self, event):
        self.shared_data.show_help('datawall_help.png')

class PresetOptionsPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(300, -1))
        self.parent = parent
        self.SetBackgroundColour(wx.Colour(230, 230, 230))

        # — Preset selector —
        self.preset_choice = wx.Choice(self)
        lbl = wx.StaticText(self, label="Select Preset:")
        ps = wx.BoxSizer(wx.HORIZONTAL)
        ps.Add(lbl, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        ps.Add(self.preset_choice, 1, wx.EXPAND)
        self.save_btn = wx.Button(self, label="Save")
        self.save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        ps.Add(self.save_btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # bind selection
        self.preset_choice.Bind(wx.EVT_CHOICE, self.on_preset_select)

        # dynamic controls
        self.graph_controls   = {}
        self.log_controls     = {}
        self.picture_controls = {}
        self.info_modules     = []

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)

        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(ps,               0, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(self.content_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_sizer)

    def _preset_filepath(self, name):
        return os.path.join("./datawall_presets", f"datawall_{name}.txt")

    def on_preset_select(self, event):
        preset = self.preset_choice.GetStringSelection()
        if not preset:
            return
        path = self._preset_filepath(preset)
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except Exception:
            wx.MessageBox(f"Could not load preset file:\n{path}",
                          "Error", wx.OK | wx.ICON_ERROR)
            return

        # parse into dict: { ("graph", name): value, ... }
        settings = {}
        for line in lines:
            if "=" not in line:
                continue
            left, val = line.split("=", 1)
            val = val.strip()
            if left.startswith("graph_preset:"):
                _, name = left.split(":", 1)
                settings[("graph", name)] = val
            elif left.startswith("log_preset:"):
                _, name = left.split(":", 1)
                settings[("log", name)] = val
            elif left.startswith("picture_path:"):
                _, name = left.split(":", 1)
                settings[("picture", name)] = val

        # apply to each section
        for name, ctrl in self.graph_controls.items():
            self.apply_setting(ctrl, settings.get(("graph", name)))

        for name, ctrl in self.log_controls.items():
            self.apply_setting(ctrl, settings.get(("log", name)))

        for name, ctrl in self.picture_controls.items():
            self.apply_setting(ctrl, settings.get(("picture", name)))

        self.content_sizer.Fit(self)
        self.Layout()
        if hasattr(self.parent, "SetupScrolling"):
            self.parent.SetupScrolling(scroll_x=False, scroll_y=True)
        self.parent.Layout()

    def apply_setting(self, ctrl: wx.ComboBox, value: str):
        """Set ctrl to value; color red if invalid, black if valid."""
        if value is None:
            return
        choices = list(ctrl.GetItems())
        ctrl.SetValue(value)
        print(value, choices)
        if value in choices:
            ctrl.SetForegroundColour(wx.Colour(0, 0, 0))
        else:
            ctrl.SetForegroundColour(wx.Colour(255, 0, 0))
        ctrl.Refresh()

    def set_col(self, event):
        ctrl = event.GetEventObject()
        val = ctrl.GetValue()
        # GetItems() returns the list of valid choices
        if val in ctrl.GetItems():
            ctrl.SetForegroundColour(wx.Colour(0, 0, 0))  # valid → black
        else:
            ctrl.SetForegroundColour(wx.Colour(255, 0, 0))  # invalid → red
        ctrl.Refresh()
        event.Skip()

    def _get_presets_for_module(self, module_name):
        """Scan ./datawall_presets for files that contain module=<module_name>."""
        presets = []
        d = "./datawall_presets"
        if not os.path.isdir(d):
            return presets
        for fn in os.listdir(d):
            if not (fn.startswith("datawall_") and fn.endswith(".txt")):
                continue
            name = fn[len("datawall_"):-4]
            path = os.path.join(d, fn)
            with open(path, encoding="utf-8") as f:
                for line in f:
                    if line.strip() == f"module={module_name}":
                        presets.append(name)
                        break
        return sorted(presets)

    def update_preset_panel(self, preset_req):
        """Rebuild everything under the dropdown (graphs/logs/pics),
           AND refresh the preset_choice list to only those matching."""
        # 1) Refresh the preset dropdown
        module = self.parent.module_choice.GetStringSelection()
        print("update for", module)
        self.preset_choice.Clear()
        self.preset_choice.Append(self._get_presets_for_module(module))

        # 2) clear old dynamic controls
        for d in (self.graph_controls, self.log_controls, self.picture_controls):
            d.clear()
        self.content_sizer.Clear(True)

        # 3) load info_read
        self.info_modules = preset_req.get("info_read", [])

        # 4) graph presets list
        graph_dir = "./graph_presets"
        graph_presets = []
        if os.path.isdir(graph_dir):
            graph_presets = sorted(p[:-5]  # strip “.json”
                                   for p in os.listdir(graph_dir)
                                   if p.endswith(".json"))

        # 5) build sections
        for title, key, ctrl_dict in [
            ("Graphs",   "graphs",   self.graph_controls),
            ("Logs",     "logs",     self.log_controls),
            ("Pictures", "pictures", self.picture_controls)
        ]:
            items = preset_req.get(key, [])
            if not items:
                continue

            self.content_sizer.Add(wx.StaticText(self, label=title),
                                   0, wx.TOP|wx.CENTER, 5)

            for name, default in items:
                row = wx.BoxSizer(wx.HORIZONTAL)
                row.Add(wx.StaticText(self, label=name),
                        0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)

                choices = graph_presets if key != "pictures" else ["recent"]
                ctrl = wx.ComboBox(self, choices=choices)
                ctrl.SetValue(default)
                ctrl.Bind(wx.EVT_COMBOBOX, self.set_col)
                ctrl.Bind(wx.EVT_TEXT, self.set_col)
                ctrl_dict[name] = ctrl

                row.Add(ctrl, 1, wx.EXPAND)
                self.content_sizer.Add(row, 0, wx.EXPAND|wx.ALL, 5)

        # 6) resize to fit content
        self.content_sizer.Fit(self)
        self.Layout()

        # 7) let parent re‐layout (it’s a ScrolledPanel)
        if hasattr(self.parent, "SetupScrolling"):
            self.parent.SetupScrolling(scroll_x=False, scroll_y=True)
        self.parent.Layout()

    def on_save(self, event):
        name = wx.GetTextFromUser("Enter preset name:", "Save Datawall Preset")
        if not name:
            return

        lines = self.get_text()

        os.makedirs("./datawall_presets", exist_ok=True)
        fn = os.path.join("./datawall_presets", f"datawall_{name}.txt")
        try:
            with open(fn, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            wx.MessageBox(f"Preset saved to {fn}", "Success",
                          wx.OK|wx.ICON_INFORMATION)

            # refresh the list for future updates
            module = self.parent.module_choice.GetStringSelection()
            new_list = self._get_presets_for_module(module)
            self.preset_choice.Clear()
            self.preset_choice.Append(new_list)
            if name in new_list:
                self.preset_choice.SetStringSelection(name)

        except Exception as e:
            wx.MessageBox(f"Error saving preset:\n{e}", "Error", wx.OK|wx.ICON_ERROR)

    def get_text(self):
        lines = []
        # always include module line
        module = self.parent.module_choice.GetStringSelection()
        lines.append(f"module={module}")

        for g, c in self.graph_controls.items():
            lines.append(f"graph_preset:{g}={c.GetValue()}")
        for l, c in self.log_controls.items():
            lines.append(f"log_preset:{l}={c.GetValue()}")
        for p, c in self.picture_controls.items():
            lines.append(f"picture_path:{p}={c.GetValue()}")
        for info in self.info_modules:
            lines.append(f"info_read={info}")

        return lines