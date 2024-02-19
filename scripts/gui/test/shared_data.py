import wx
import os
from pathlib import Path
import sys
import platform
import datetime
import wx.lib.scrolledpanel as scrolled

class shared_data:
    def __init__(self, parent):
        self.parent = parent
        # Connection settings
        # defaults
        self.gui_set_dict = {}
        # connection settigns
        self.gui_set_dict['ssh_port'] = "22"
        self.gui_set_dict['default_address'] = "192.168.1."
        self.gui_set_dict['address_list'] = []
        self.gui_set_dict['username'] = "pi"
        self.gui_set_dict['password'] = "raspberry"
        self.gui_set_dict['save_ip'] = "True"
        # scale and units
        self.gui_set_dict['font_scale'] = "1"
        self.gui_set_dict['volume_unit'] = "ml"
        self.gui_set_dict['temp_unit'] = "c"



        # load from file
        self.load_gui_settings()
        #
        ## settings
        # system tab layout
        self.system_info_layout = self.load_sys_layout_info()
        if self.system_info_layout == []:
            self.system_info_layout = [['boxname','check_pigrow_folder','os_version','hardware_version','power_warnings','cpu_temp','diskusage'],
                                       ['camera','i2c','error_log','connected_network','datetime']]
        # setiings related to current connection
        self.frompi_base_path = self.set_local_path() # base path without box_name folder
        self.frompi_path = ""
        self.remote_pigrow_path = ""
        self.config_dict = {} # pigrow_config.txt
        #
        self.always_show_config_changes = False  # if true always show the 'upload to pigrow?' dialog box
        #
        ## paths
        #
        # gui system paths
        self.cwd = os.getcwd()
        self.ui_img_path = Path.cwd().parent / "ui_images"
        self.graph_modules_path = os.path.join(self.cwd, "graph_modules")
        self.sensor_modules_path = os.path.join(self.cwd, "sensor_modules")
        self.timelapse_modules_path = os.path.join(self.cwd, "timelapse_modules")
        sys.path.append(self.graph_modules_path)
        sys.path.append(self.sensor_modules_path)
        sys.path.append(self.timelapse_modules_path)
        self.graph_presets_path = os.path.join(self.cwd, "graph_presets")
        self.datawall_presets_path = os.path.join(self.cwd, "datawall_presets")
        #
        ## Temporarily Stored data
        #
        # graphing logs
        self.log_to_load = None
        self.list_of_datasets = [] # [[date, value, key], [set2_date, set2_value, set2_key], etc]
        #      [self.first_date_set, self.first_value_set, self.first_keys_set]
        self.first_value_set = []
        self.first_date_set = []
        self.first_keys_set = []
        self.first_valueset_name = ""
        # camconf info
        self.most_recent_camconf_image = ""
        self.camcomf_compare_image  = ""

        #
        ## Icon images
        #
        no_log_img_path = self.ui_img_path / "log_loaded_none.png"
        yes_log_img_path = self.ui_img_path / "log_loaded_true.png"
        warn_log_img_path = self.ui_img_path / "log_loaded_none.png"
        self.no_log_image = wx.Image(str(no_log_img_path), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.yes_log_image = wx.Image(str(yes_log_img_path), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.warn_log_image = wx.Image(str(warn_log_img_path), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        infobtn_img_path = self.ui_img_path / "Info_button.png"
        self.infobtn_image = wx.Image(str(infobtn_img_path), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        #
        ## Fonts
        #
        font_scale = float(self.gui_set_dict['font_scale'])
        self.title_font      = wx.Font(int(28 * font_scale), wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.sub_title_font  = wx.Font(int(15 * font_scale), wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.item_title_font = wx.Font(int(16 * font_scale), wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.info_font       = wx.Font(int(14 * font_scale), wx.MODERN, wx.ITALIC, wx.NORMAL)
        self.large_info_font = wx.Font(int(16 * font_scale), wx.MODERN, wx.ITALIC, wx.NORMAL)
        self.button_font       = wx.Font(int(14 * font_scale), wx.MODERN, wx.ITALIC, wx.NORMAL)

    def load_sys_layout_info(self):
        i = 0
        system_info_layout = []
        while True:
            pnl_key = "syspnl_col_" + str(i)
            if pnl_key in self.gui_set_dict:
                item_list = self.gui_set_dict[pnl_key]
                if "," in item_list:
                    item_list = item_list.split(",")
                else:
                    item_list = [item_list]
                system_info_layout.append(item_list)
                i += 1
            else:
                return system_info_layout

    def set_local_path(self):
        try:
            OStype =  platform.system()
            if OStype == "Linux":
                computer_username = os.getlogin()
                localpath = os.path.join("/home", computer_username)
                localpath = os.path.join(localpath, "frompigrow")
                return localpath
            else:
                localpath = os.getcwd()
                localpath = os.path.join(localpath, "frompigrow")
                return localpath
        except:
            localpath = os.getcwd()
            localpath = os.path.join(localpath, "frompigrow")
            return localpath

    def load_gui_settings(self):
        gui_settings_path = "gui_settings.txt"
        if os.path.isfile(gui_settings_path):
            with open(gui_settings_path, "r") as gui_set_text:
                gui_settings_list = gui_set_text.read().splitlines()
            for line in gui_settings_list:
                if "=" in line:
                    equals_pos = line.find("=")
                    setting = line[:equals_pos]
                    value = line[equals_pos+1:]
                    self.gui_set_dict[setting]=value
        else:
            print(" No gui settings file, using defaults")

    def save_gui_settings(self):
        gui_settings_path = "gui_settings.txt"
        settings_file_text = ""
        for key, value in self.gui_set_dict.items():
            settings_file_text += str(key) + "=" + str(value) + "\n"
        with open(gui_settings_path, "w") as gui_set_text:
            gui_set_text.write(settings_file_text)

    def show_help(self, img_path):
        # load image
        guide_path = os.path.join(self.ui_img_path, img_path)
        if os.path.isfile(guide_path):
            print( " Showing help file - ", guide_path )
            guide = wx.Image(guide_path, wx.BITMAP_TYPE_ANY)
            guide = guide.ConvertToBitmap()
            dbox = self.show_image_dialog(None, guide, "Cron Help")
            dbox.ShowModal()
            dbox.Destroy()
        else:
            print(" help file not found, check www.reddit.com/r/Pigrow/wiki for info.")
            print("     " + guide_path + " not found")

    def scale_pic(self, pic, target_size):
        pic_height = pic.GetHeight()
        pic_width = pic.GetWidth()
        # scale the image, preserving the aspect ratio
        if pic_width > pic_height:
            sizeratio = (pic_width / target_size)
            new_height = int(pic_height / sizeratio)
            scale_pic = pic.Scale(target_size, new_height, wx.IMAGE_QUALITY_HIGH)
            #print(pic_width, pic_height, sizeratio, target_size, new_height, scale_pic.GetWidth(), scale_pic.GetHeight())
        else:
            sizeratio = (pic_height / target_size)
            new_width = int(pic_width / sizeratio)
            scale_pic = pic.Scale(new_width, target_size, wx.IMAGE_QUALITY_HIGH)
            #print(pic_width, pic_height, sizeratio, new_width, target_size, scale_pic.GetWidth(), scale_pic.GetHeight())
        return scale_pic

    def date_from_fn(self, thefilename):
        if "." in thefilename and "_" in thefilename:
            fdate = thefilename.split(".")[0].split("_")[-1]
            if len(fdate) == 10 and fdate.isdigit():
                fdate = datetime.datetime.utcfromtimestamp(float(fdate))
            else:
                return None
            return fdate
        # for motion standard file name
        elif "-" in thefilename:
            try:
                date = thefilename.split("-")[1]
                # 10-2018 05 05 20 12 12-03
                file_datetime = datetime.datetime.strptime(date, '%Y%m%d%H%M%S')
                #text_date = file_datetime.strftime('%Y-%m-%d %H:%M')
                return file_datetime
            except:
                print("!! Tried to parse filename as Motion date but failed " + str(thefilename))
                return None #, None
        else:
            return None

    def get_module_options(self, module_prefix, m_folder="graph_modules"):
        list_of_modules = []
        modules_folder = os.path.join(os.getcwd(), m_folder)
        module_options = os.listdir(modules_folder)
        for file in module_options:
            if module_prefix in file:
                file = file.split(module_prefix)[1]
                if ".py" in file:
                    file = file.split(".py")[0]
                    list_of_modules.append(file)
        return list_of_modules

    def read_pigrow_settings_file(self):
        setfile_path = self.remote_pigrow_path + "config/pigrow_config.txt"
        out, error = self.parent.link_pnl.run_on_pi("cat " + setfile_path)
        #print(out, error)
        self.config_dict.clear()
        for line in out.splitlines():
            if "=" in line:
                e_pos    = line.find("=")
                s_value  = line[e_pos + 1:]
                s_name   = line[:e_pos]
                self.config_dict[s_name] = s_value
        print("  - Shared_data.config_dict set from pigrow_config.txt")

    def update_pigrow_config_file_on_pi(self, ask="yes"):
        setting_file_path = self.remote_pigrow_path + "config/pigrow_config.txt"

        config_text = ""
        for key, value in list(self.config_dict.items()):
            if not key == "":
                config_text += key + "=" + value + "\n"
        config_text = config_text.strip()

        # show user and ask user if they relly want to update
        if ask == "yes":
            dbox = shared_data.scroll_text_dialog(None, config_text, "Upload to Pigrow? ", cancel=True)
            dbox.ShowModal()
            out_conf = dbox.text
            dbox.Destroy()
            if out_conf == None:
                #print("User aborted")
                return None
            else:
                #self.parent.link_pnl.save_text_to_file_on_pi(setting_file_path, config_text)
                self.parent.link_pnl.update_config_file_on_pi(config_text, setting_file_path)
                self.parent.tell_pnls_updated_config()


    class settings_dialog(wx.Dialog):
        '''
        Dialog box for changing the gui settings
        #
        dbox = self.settings_dialog(None)
        dbox.ShowModal()
        dbox.Destroy()
        #
        '''
        def __init__(self, parent):
            self.gui_set_dict = parent.shared_data.gui_set_dict
            self.parent = parent
            wx.Dialog.__init__(self, parent, title="Remote Gui Settings")
            # Default connection address
            self.default_address_l = wx.StaticText(self, label='Default Address')
            self.default_address_tc = wx.TextCtrl(self, -1, self.gui_set_dict['default_address'], size=(250,30))
            # username and password
            self.default_username_l = wx.StaticText(self, label='Username')
            self.default_username_tc = wx.TextCtrl(self, -1, self.gui_set_dict['username'], size=(250,30))
            self.default_password_l = wx.StaticText(self, label='Password')
            self.default_password_tc = wx.TextCtrl(self, -1, self.gui_set_dict['password'], size=(250,30))
            # SSH Settings
            self.sshport_l = wx.StaticText(self, label='SSH Port')
            self.ssh_port_tc = wx.TextCtrl(self, -1, str(self.gui_set_dict['ssh_port']))
            # save ip on connect
            self.save_ip_l = wx.StaticText(self, label='Save on connect')
            self.save_ip_cb = wx.CheckBox(self, -1)
            if self.gui_set_dict['save_ip'] == "True":
                self.save_ip_cb.SetValue(True)
            else:
                self.save_ip_cb.SetValue(False)
            #list of stored ips


            # ui settings
            self.font_scale_l = wx.StaticText(self, label='Font Scale')
            self.font_scale = wx.TextCtrl(self, -1, str(self.gui_set_dict['font_scale']))
            # units
            self.temp_unit_l = wx.StaticText(self, label='Temp Unit')
            tunits = ['C', 'F']
            self.temp_unit_cb = wx.ComboBox(self, choices = tunits, size=(200, 40), style=wx.CB_READONLY, value=self.gui_set_dict['temp_unit'])
            self.vol_unit_l = wx.StaticText(self, label='Volume Unit')
            vunits = ['Litre', 'Gallon (US)']
            self.vol_unit_cb = wx.ComboBox(self, choices = vunits, size=(200, 40), style=wx.CB_READONLY, value=self.gui_set_dict['volume_unit'])
            # Buttons
            btn = wx.Button(self, wx.ID_OK)
            cancel_btn = wx.Button(self, wx.ID_CANCEL)
            btn.Bind(wx.EVT_BUTTON, self.ok_click)
            # Sizers
            conection_sizer = wx.FlexGridSizer(2, 0, 4)
            conection_sizer.AddMany( [(self.default_address_l, 0, wx.ALIGN_RIGHT),
                (self.default_address_tc, 0),
                (self.default_username_l, 0),
                (self.default_username_tc, 0, wx.ALIGN_RIGHT),
                (self.default_password_l, 0),
                (self.default_password_tc, 0, wx.ALIGN_RIGHT),
                (self.sshport_l, 0, wx.ALIGN_RIGHT),
                (self.ssh_port_tc, 0),
                (self.save_ip_l, 0),
                (self.save_ip_cb, 0),
                (self.font_scale_l, 0),
                (self.font_scale, 0),
                (self.temp_unit_l, 0),
                (self.temp_unit_cb, 0),
                (self.vol_unit_l, 0),
                (self.vol_unit_cb, 0)])
            btnsizer = wx.BoxSizer(wx.HORIZONTAL)
            btnsizer.Add(btn, 0, wx.ALL, 5)
            btnsizer.Add((5,-1), 0, wx.ALL, 5)
            btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(conection_sizer, 0, wx.EXPAND|wx.ALL, 5)
            main_sizer.Add(btnsizer, 0, wx.ALL, 5)
            self.SetSizerAndFit(main_sizer)
        def ok_click(self, e):
            self.gui_set_dict['ssh_port'] = self.ssh_port_tc.GetValue()
            self.gui_set_dict['default_address'] = self.default_address_tc.GetValue()
            self.gui_set_dict['username'] = self.default_username_tc.GetValue()
            self.gui_set_dict['password'] = self.default_password_tc.GetValue()
            self.gui_set_dict['save_ip'] = str(self.save_ip_cb.GetValue())
            self.gui_set_dict['font_scale'] = self.font_scale.GetValue()
            self.gui_set_dict['temp_unit'] = self.temp_unit_cb.GetValue()
            self.gui_set_dict['volume_unit'] = self.vol_unit_cb.GetValue()
            # save settings
            self.parent.shared_data.save_gui_settings()
            self.Destroy()

    class scroll_text_dialog(wx.Dialog):
        def __init__(self, parent,  text_to_show, title, cancel=True, readonly=True):
            wx.Dialog.__init__(self, parent, title=(title))
            self.text = None
            if readonly == True:
                self.text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE | wx.TE_READONLY)
            else:
                self.text = wx.TextCtrl(self, -1, text_to_show, size=(800,600), style=wx.TE_MULTILINE)
            sizer = wx.BoxSizer(wx.VERTICAL)
            btnsizer = wx.BoxSizer()
            btn = wx.Button(self, wx.ID_OK)
            btn.Bind(wx.EVT_BUTTON, self.ok_click)
            btnsizer.Add(btn, 0, wx.ALL, 5)
            btnsizer.Add((5,-1), 0, wx.ALL, 5)
            if cancel==True:
                cancel_btn = wx.Button(self, wx.ID_CANCEL)
                cancel_btn.Bind(wx.EVT_BUTTON, self.cancel_click)
                btnsizer.Add(cancel_btn, 0, wx.ALL, 5)
            sizer.Add(self.text, 0, wx.EXPAND|wx.ALL, 5)
            sizer.Add(btnsizer, 0, wx.ALL, 5)
            self.SetSizerAndFit(sizer)
        def ok_click(self, e):
            self.text = self.text.GetValue()
            self.Destroy()
        def cancel_click(self, e):
            self.text = None
            self.Destroy()

    class show_image_dialog(wx.Dialog):
        def __init__(self, parent, image_to_show, title):
            wx.Dialog.__init__(self, parent, title=title)
            self.title = title
            self.zoom_factor = 1.0  # Initial zoom factor

            if type(image_to_show) == type("str"):
                print("Displaying Image; ", image_to_show)
                image_to_show = wx.Image(image_to_show, wx.BITMAP_TYPE_ANY)
                image_to_show = image_to_show.ConvertToBitmap()
            else:
                print(type(image_to_show))

            self.original_image = image_to_show  # Save the original image for reference

            width, height = wx.GetDisplaySize()
            im_width, im_height = image_to_show.GetSize()

            if im_height > height:
                im_height = height
            if im_width > width:
                im_width = width

            display_panel = scrolled.ScrolledPanel(self, size=(im_width, im_height), style=wx.HSCROLL | wx.VSCROLL)
            display_panel.SetupScrolling()
            self.pic = wx.StaticBitmap(display_panel, -1, image_to_show)
            self.pic.Bind(wx.EVT_LEFT_DOWN, self.on_left_click)
            self.pic.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

            panel_sizer = wx.BoxSizer(wx.VERTICAL)
            panel_sizer.Add(self.pic)
            display_panel.SetSizer(panel_sizer)

            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(display_panel)
            self.SetSizerAndFit(sizer)

        def on_left_click(self, event):
            click_point = event.GetPosition()
            self.zoom_factor *= 1.1  # You can adjust the zoom factor as needed
            self.update_image(click_point)
            self.update_title()

        def on_right_click(self, event):
            click_point = event.GetPosition()
            self.zoom_factor /= 1.1  # You can adjust the zoom factor as needed
            self.update_image(click_point)
            self.update_title()

        def update_image(self, click_point):
            # Update the image size based on the current zoom factor
            image_to_show = self.original_image.ConvertToImage()
            new_width = int(image_to_show.GetWidth() * self.zoom_factor)
            new_height = int(image_to_show.GetHeight() * self.zoom_factor)
            image_to_show = image_to_show.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

            # Center the clicked point in the image box
            scroll_pos = self.pic.GetParent().GetViewStart()
            offset_x = int((click_point.x + scroll_pos[0]) * self.zoom_factor - click_point.x)
            offset_y = int((click_point.y + scroll_pos[1]) * self.zoom_factor - click_point.y)

            # Update the bitmap within the scrolled panel
            self.pic.SetBitmap(wx.Bitmap(image_to_show))
            # Resize the display_panel to match the new image size
            self.pic.GetParent().SetVirtualSize((new_width, new_height))
            self.pic.GetParent().Layout()
            # Scroll to the new position
            self.pic.GetParent().Scroll(offset_x, offset_y)

        def update_title(self):
            # Update the dialog box title with the current zoom level
            self.SetTitle(f"{self.title} - Zoom: {round(self.zoom_factor, 2) * 100}")
