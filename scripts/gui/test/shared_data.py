import wx
import os
import sys
import platform
import datetime
import wx.lib.scrolledpanel as scrolled

class shared_data:
    def __init__(self):
        # Connection settings
        # defaults
        self.gui_set_dict = {}
        self.gui_set_dict['ssh_port'] = "22"
        self.gui_set_dict['default_address'] = "192.168.1."
        self.gui_set_dict['address_list'] = ["192.168.1.5", "192.168.1.10"]
        self.gui_set_dict['username'] = "pi"
        self.gui_set_dict['password'] = "raspberry"
        self.gui_set_dict['font_scale'] = "1"
        # load from file
        self.load_gui_settings()
        #
        ## settings
        # setiings related to current connection
        self.frompi_base_path = self.set_local_path()
        self.frompi_path = ""
        self.remote_pigrow_path = ""
        #
        self.always_show_config_changes = False  # if true always show the 'upload to pigrow?' dialog box
        #
        ## paths
        #
        # gui system paths
        self.cwd = os.getcwd()
        self.ui_img_path = os.path.join(self.cwd, "ui_images")
        self.graph_modules_path = os.path.join(self.cwd, "graph_modules")
        self.sensor_modules_path = os.path.join(self.cwd, "sensor_modules")
        sys.path.append(self.graph_modules_path)
        sys.path.append(self.sensor_modules_path)
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
        no_log_img_path = os.path.join(self.ui_img_path, "log_loaded_none.png")
        yes_log_img_path = os.path.join(self.ui_img_path, "log_loaded_true.png")
        warn_log_img_path = os.path.join(self.ui_img_path, "log_loaded_none.png")
        self.no_log_image = wx.Image(no_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.yes_log_image = wx.Image(yes_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.warn_log_image = wx.Image(warn_log_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        infobtn_img_path = os.path.join(self.ui_img_path, "Info_button.png")
        self.infobtn_image = wx.Image(infobtn_img_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
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
            # ui settings
            self.font_scale_l = wx.StaticText(self, label='Font Scale')
            self.font_scale = wx.TextCtrl(self, -1, str(self.gui_set_dict['font_scale']))
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
                (self.font_scale_l, 0),
                (self.font_scale, 0)])
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
            self.gui_set_dict['font_scale'] = self.font_scale.GetValue()
            # save settings
            gui_settings_path = "gui_settings.txt"
            settings_file_text = ""
            for key, value in self.gui_set_dict.items():
                settings_file_text += str(key) + "=" + str(value) + "\n"
            with open(gui_settings_path, "w") as gui_set_text:
                gui_set_text.write(settings_file_text)
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
        def __init__(self, parent,  image_to_show, title):
            wx.Dialog.__init__(self, parent, title=(title))
            # if path load image
            if type(image_to_show) == type("str"):
                print("LOADING IMAGE ", image_to_show)
                image_to_show = wx.Image(image_to_show, wx.BITMAP_TYPE_ANY)
                image_to_show = image_to_show.ConvertToBitmap()
            else:
                print( type(image_to_show))
            # limit size to screen
            width, height = wx.GetDisplaySize()
            im_width, im_height = image_to_show.GetSize()
            #print(" W: ", width, im_width )
            #print(" H: ", height, im_height)
            if im_height > height:
                im_height = height
            if im_width > width:
                im_width = width
            # create scroll panel
            display_panel = scrolled.ScrolledPanel(self, size=(im_width, im_height), style = wx.HSCROLL|wx.VSCROLL)
            display_panel.SetupScrolling()
            pic = wx.StaticBitmap(display_panel, -1, image_to_show)
            # panel sizer
            panel_sizer = wx.BoxSizer(wx.VERTICAL)
            panel_sizer.Add(pic)
            display_panel.SetSizer(panel_sizer)
            # main sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(display_panel)
            self.SetSizerAndFit(sizer)
