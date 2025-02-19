import wx
import wx.grid as gridlib
import wx.adv
import wx.lib.scrolledpanel as scrolled
import importlib
import os
import json
import datetime
import time
import sys



class ctrl_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.loaded_datasets = []
        self.datawall_data = {}

        # Initialize ScrolledPanel instead of Panel
        scrolled.ScrolledPanel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, label="Datawall")
        self.main_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        # Preset
        opts = self.get_datawall_presets()
        self.preset_choice = wx.Choice(self, choices=opts)
        self.load_preset_btn = wx.Button(self, label="Load Datawall Preset")
        self.load_preset_btn.Bind(wx.EVT_BUTTON, self.on_load_preset)
        self.main_sizer.Add(self.preset_choice, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.main_sizer.Add(self.load_preset_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Datawall Module
        module_opts = self.get_datawall_module_list()
        self.module_choice = wx.Choice(self, choices=module_opts)
        self.run_module_btn = wx.Button(self, label="Run Datawall Module")
        self.run_module_btn.Bind(wx.EVT_BUTTON, self.on_run_datawall_module)
        self.main_sizer.Add(wx.StaticText(self, label="Select Datawall Module:"),
                            0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.main_sizer.Add(self.module_choice, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.main_sizer.Add(self.run_module_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Set the sizer
        self.SetSizer(self.main_sizer)

        # Setup scrolling
        self.SetupScrolling(scroll_x=False, scroll_y=True)

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

    def on_load_preset(self, e):
        choice = self.preset_choice.GetStringSelection()
        filename = 'datawall_' + choice + ".txt"
        preset_path = os.path.join('./datawall_presets', filename)

        data_for_datawall = {
            "info": {},
            "images": {},
            "data": {},
            "graphs": {}
        }

        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                datawall_preset_file = f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found in datawall_presets folder.")
            return
        except Exception as ex:
            print(f"Error reading {filename}: {ex}")
            return

        for line in datawall_preset_file.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == 'info_read':
                    info = self.read_info_module(value)
                    data_for_datawall["info"][value] = info
                elif key == 'picture_path':
                    data_for_datawall["images"][value] = self.get_image(value)
                elif key == "graph_preset":
                    graph_path = self.parent.dict_C_pnl['graphs_pnl'].create_graph_by_preset(value)
                    if graph_path:
                        data_for_datawall["graphs"][graph_path] = graph_path
                elif key == 'log_preset':
                    # Instead of creating a graph, load the datasets used to create it.
                    dataset = self.parent.dict_C_pnl['graphs_pnl'].graph_preset.load_dataset_preset(
                        self.parent.dict_C_pnl['graphs_pnl'], value)
                    if dataset:
                        data_for_datawall["data"][value] = dataset

        self.datawall_data = data_for_datawall

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
            print(f"Copying image for datawall from {remote_path} to {img_fold + "/" + img_filename}")
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
            output = module.make_datawall(self.datawall_data)
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
        sub_title_text = "This is in progress and doesn't do anything useful yet"
        page_sub_title = wx.StaticText(self, label=sub_title_text)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
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


