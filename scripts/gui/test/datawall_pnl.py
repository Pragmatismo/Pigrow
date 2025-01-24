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
        # Construct the filename based on the selection
        filename = 'datawall_' + choice + ".txt"
        preset_path = os.path.join('./datawall_presets', filename)

        # Prepare the data structure
        data_for_datawall = {
            "info": {},
            "images": {},
            "data": {}
        }

        # Attempt to open and read the preset file
        try:
            with open(preset_path, 'r', encoding='utf-8') as f:
                datawall_preset_file = f.read()
        except FileNotFoundError:
            print(f"Error: {filename} not found in datawall_presets folder.")
            return
        except Exception as ex:
            print(f"Error reading {filename}: {ex}")
            return

        # Split the file content into lines and process each line
        for line in datawall_preset_file.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                if key == 'info_read':
                    info = self.read_info_module(value)
                    data_for_datawall["info"][value] = info
                if key == 'picture_path':
                    data_for_datawall["images"][value] = self.get_image(value)
                elif key == 'graph_name':
                    # Handle creating a new graph settings
                    pass

        # Show for debugging
        print(data_for_datawall)

        print("Sorry this is not yet complete.")

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
        return out.strip()

    def get_image(self, value):
        # find the image path
        info_o = self.read_info_module(value, "picture_")
        print("!!!!", info_o)
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


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['datawall_pnl']
        w = 1000
        wx.Panel.__init__(self, parent, size=(w, -1), id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

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

        self.SetSizer(self.main_sizer)
        self.SetupScrolling()



