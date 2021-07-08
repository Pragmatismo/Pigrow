import os
import wx
import wx.lib.scrolledpanel as scrolled
import image_combine
import shutil
from picam_set_pnl import picam_sets_pnl
from fswebcam_set_pnl import fs_sets_pnl

class ctrl_pnl(scrolled.ScrolledPanel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # read / save cam config button
        self.read_cam_config_btn = wx.Button(self, label='read config')
        self.read_cam_config_btn.Bind(wx.EVT_BUTTON, self.read_cam_config_click)
        self.save_cam_config_btn = wx.Button(self, label='save to pi')
        self.save_cam_config_btn.Bind(wx.EVT_BUTTON, self.save_cam_config_click)
        #camera options
        self.cam_select_l = wx.StaticText(self,  label='Camera selection;')
        self.list_cams_btn = wx.Button(self, label='find', size=(30, 30))
        self.list_cams_btn.Bind(wx.EVT_BUTTON, self.list_cams_click)
        cam_opts = [""]
        self.cam_cb = wx.ComboBox(self, choices = cam_opts, size=(225, 30))
        #
        self.cap_tool_l = wx.StaticText(self,  label='Capture tool;')
        webcam_opts = ['uvccapture', 'fswebcam', 'picamcap']
        self.captool_cb = wx.ComboBox(self, choices = webcam_opts, size=(265, 30))
        self.captool_cb.Bind(wx.EVT_COMBOBOX, self.camcap_combo_go)

        # Buttons
        self.take_unset_btn = wx.Button(self, label='Take using\ncam default')
        self.take_unset_btn.Bind(wx.EVT_BUTTON, self.take_unset_click)
        self.take_set_btn = wx.Button(self, label='Take using\nlocal settings')
        self.take_set_btn.Bind(wx.EVT_BUTTON, self.take_set_click)
        self.take_s_set_btn = wx.Button(self, label='Take using\nsaved settings')
        self.take_s_set_btn.Bind(wx.EVT_BUTTON, self.take_saved_set_click)
        # Take Range altering a single setting
        self.range_combo = wx.ComboBox(self, choices = [])
        self.range_combo.Bind(wx.EVT_COMBOBOX, self.range_combo_go)
        # start point, end point, increment every x - text control, label, default settings
        self.range_start_tc = wx.TextCtrl(self)
        self.range_end_tc = wx.TextCtrl(self)
        self.range_every_tc = wx.TextCtrl(self)
        self.range_start_l = wx.StaticText(self,  label='start;')
        self.range_end_l = wx.StaticText(self,  label='end;')
        self.range_every_l = wx.StaticText(self,  label='every;')
        self.range_start_tc.SetValue("0")
        self.range_end_tc.SetValue("255")
        self.range_every_tc.SetValue("20")
        # take range button
        self.take_range_btn = wx.Button(self, label='Take\nrange', size=(50,-1))
        self.take_range_btn.Bind(wx.EVT_BUTTON, self.range_btn_click)
        # compare
        self.onscreen_compare_l = wx.StaticText(self,  label='Compare Images;')
        self.set_as_compare_btn = wx.Button(self, label='Set as compare image')
        self.set_as_compare_btn.Bind(wx.EVT_BUTTON, self.set_as_compare_click)
        self.use_compare = wx.CheckBox(self, label='Enable')
        compare_opts = image_combine.config.styles
        self.compare_style_cb = wx.ComboBox(self, choices = compare_opts, value=compare_opts[0], size=(265, 30))
        # show noise - image set analasis
        self.anal_tools_l = wx.StaticText(self,  label='Analasis Tools;')
        self.cap_stack_btn = wx.Button(self, label='Capture Stack')
        self.cap_stack_btn.Bind(wx.EVT_BUTTON, self.cap_stack_click)
        self.capture_stack_count = wx.TextCtrl(self, value="5")
        self.use_range_combine = wx.CheckBox(self, label='Combine Range')
        combine_opts = image_combine.config.combine_styles
        self.set_style_cb = wx.ComboBox(self, choices = combine_opts, value=combine_opts[0], size=(265, 30))


        # Sizers
        load_save_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        load_save_btn_sizer.Add(self.read_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        load_save_btn_sizer.Add(self.save_cam_config_btn, 1, wx.ALL|wx.EXPAND, 0)
        find_select_cam_sizer = wx.BoxSizer(wx.HORIZONTAL)
        find_select_cam_sizer.Add(self.list_cams_btn, 0, wx.ALL, 0)
        find_select_cam_sizer.Add(self.cam_cb, 0, wx.ALL|wx.EXPAND, 0)
        take_single_photo_btns_sizer = wx.BoxSizer(wx.HORIZONTAL)
        take_single_photo_btns_sizer.Add(self.take_unset_btn, 0, wx.ALL, 0)
        take_single_photo_btns_sizer.Add(self.take_s_set_btn, 0, wx.ALL, 0)
        range_options_btn_sizer = wx.GridSizer(3, 2, 0, 0)
        range_options_btn_sizer.AddMany( [(self.range_start_l, 0, wx.EXPAND),
            (self.range_start_tc, 0, wx.EXPAND),
            (self.range_end_l, 0, wx.EXPAND),
            (self.range_end_tc, 0, wx.EXPAND),
            (self.range_every_l, 0, wx.EXPAND),
            (self.range_every_tc, 0, wx.EXPAND) ])
        range_options_sizer = wx.BoxSizer(wx.VERTICAL)
        range_options_sizer.Add(self.range_combo, 0, wx.ALL|wx.EXPAND, 0)
        range_options_sizer.Add(range_options_btn_sizer, 0, wx.ALL|wx.EXPAND, 0)
        range_sizer = wx.BoxSizer(wx.HORIZONTAL)
        range_sizer.Add(self.take_range_btn, 0, wx.ALL|wx.EXPAND, 0)
        range_sizer.Add(range_options_sizer, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer = wx.BoxSizer(wx.VERTICAL)
        compare_sizer.Add(self.onscreen_compare_l, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.set_as_compare_btn, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.use_compare, 0, wx.ALL|wx.EXPAND, 0)
        compare_sizer.Add(self.compare_style_cb, 0, wx.ALL|wx.EXPAND, 0)
        stack_cap_sizer = wx.BoxSizer(wx.HORIZONTAL)
        stack_cap_sizer.Add(self.cap_stack_btn, 0, wx.ALL|wx.EXPAND, 0)
        stack_cap_sizer.Add(self.capture_stack_count, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer = wx.BoxSizer(wx.VERTICAL)
        anal_sizer.Add(self.anal_tools_l, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer.Add(stack_cap_sizer, 0, wx.ALL|wx.EXPAND, 0)
        anal_sizer.Add(self.set_style_cb, 0, wx.ALL|wx.EXPAND, 0)

        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(load_save_btn_sizer, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.cam_select_l, 0, wx.ALL, 0)
        main_sizer.Add(find_select_cam_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.cap_tool_l, 0, wx.ALL, 0)
        main_sizer.Add(self.captool_cb, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.take_set_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(take_single_photo_btns_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(range_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.use_range_combine, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(compare_sizer, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(anal_sizer, 0, wx.ALL, 0)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(main_sizer)

    # Load / Save Config

    def seek_cam_configs(self):
        conf_folder = self.parent.shared_data.remote_pigrow_path + "config/"
        out, error = self.parent.link_pnl.run_on_pi("ls " + str(conf_folder))
        config_list = out.splitlines()
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        I_pnl.camconf_path_tc.Clear()
        cam_config_list = []
        for file in config_list:
            file_name = conf_folder + file.strip()
            grep_cmd = "grep cam_num= " + file_name
            out, error = self.parent.link_pnl.run_on_pi(grep_cmd)
            if not out.strip() == "":
                I_pnl.camconf_path_tc.Append(file_name)

    def save_cam_config_click(self, e):
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        sets_text = I_pnl.sets_pnl.make_conf_text(I_pnl.sets_pnl.setting_crtl_dict)
        cam_opt = self.cam_cb.GetValue()
        cap_opt = self.captool_cb.GetValue()
        conf_text = "cam_num=" + cam_opt + "\n"
        conf_text += "cam_opt=" + cap_opt + "\n"
        conf_text += sets_text
        # Ask filename to save to
        c_sets_path = I_pnl.camconf_path_tc.GetValue()
        if c_sets_path == "":
            if cap_opt == "picamcap":
                rpp = self.parent.shared_data.remote_pigrow_path
                c_sets_path = rpp + "config/picam_config.txt"
            else:
                c_sets_path = rpp + "config/camera_config.txt"
        remote_path = os.path.dirname(c_sets_path)
        config_file_name = os.path.basename(c_sets_path)
        filename_dbox = wx.TextEntryDialog(self, 'Upload config file with name, \n\n(Change when using more than one camera)', 'Upload config to Pi?', config_file_name)
        if filename_dbox.ShowModal() == wx.ID_OK:
            cam_config_file_name = filename_dbox.GetValue()
        else:
            return "cancelled"
        filename_dbox.Destroy()
        # Write config file to pi
        c_save_path = remote_path+"/"+cam_config_file_name
        self.parent.link_pnl.update_config_file_on_pi(conf_text, c_save_path)
        print(" Saved ", c_save_path, " to pi")

    def read_cam_config_click(self, e):
        self.seek_cam_configs()
        conf_path = self.parent.dict_I_pnl['camera_pnl'].camconf_path_tc.GetValue()
        if conf_path == "":
            print(" - No camera config file selected")
            return None
        out, error = self.parent.link_pnl.run_on_pi("cat " + conf_path)
        if out == "":
            print("Unable to read settings file -" + conf_path)
            return None
        # Set cam num and capture opt
        cam_num = ""
        cam_opt = ""
        for line in out.split("\n"):
            if "cam_num=" in line:
                cam_num = line.split("=")[1]
            if "cam_opt=" in line:
                cam_opt = line.split("=")[1]
        self.cam_cb.SetValue(cam_num)
        self.captool_cb.SetValue(cam_opt)
        self.camcap_combo_go("e")
        # load captool spesific settings into
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        I_pnl.sets_pnl.text_into_ui(out)

    # Controlls - camera select and capture tool

    def list_cams_click(self, e):
        # find picams
        out, error = self.parent.link_pnl.run_on_pi("vcgencmd get_camera")
        if "detected=" in out:
            out = out.split('detected=')[1].strip()
            if out == "0":
                print(' - No Picam detected')
                picam_list = []
            elif out == "1":
                print(' - 1 Picam Detected')
                picam_list = ['picam 0']
            elif out == "2":
                print(' - Dual Picams Detected')
                picam_list = ['picam 0', 'picam 1']
            else:
                print(' - Multipul Picams detected - only using first two: ' + out)
                picam_list = ['picam 0', 'picam 1']
        # find webcams
        out, error = self.parent.link_pnl.run_on_pi("ls /dev/video*")
        cam_list = out.strip().split("\n")
        # add cams to list box
        self.cam_cb.Clear()
        cam_list = picam_list + cam_list
        for cam in cam_list:
            if "video" in cam:
                if not int(cam.split("video")[1].strip()) > 9:
                    self.cam_cb.Append(cam)

    def camcap_combo_go(self, e):
        print ( " changing ")
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        if self.captool_cb.GetValue() == 'fswebcam':
            I_pnl.show_fswebcam_control()
        elif self.captool_cb.GetValue() == 'uvccapture':
            I_pnl.show_uvc_control()
        elif self.captool_cb.GetValue() == 'picamcap':
            I_pnl.show_picamcap_control()
        # add rangeable items to range_combo box
        self.range_combo.Clear()
        scd = I_pnl.sets_pnl.setting_crtl_dict
        for key in scd.keys():
            #print(type(scd[key]))
            if type(scd[key]) == wx._core.Slider or type(scd[key]) == wx._core.ComboBox:
                self.range_combo.Append(key)

    def range_combo_go(self, e):
        key = self.range_combo.GetValue()
        scd = self.parent.dict_I_pnl['camera_pnl'].sets_pnl.setting_crtl_dict
        if type(scd[key]) == wx._core.Slider:
            print(" slider ")
            self.range_start_tc.Show()
            self.range_end_tc.Show()
            self.range_every_tc.Show()
            self.range_start_l.Show()
            self.range_end_l.Show()
            self.range_every_l.Show()
            self.range_start_tc.SetValue(str(scd[key].GetMin()))
            self.range_end_tc.SetValue(str(scd[key].GetMax()))
        if type(scd[key]) == wx._core.ComboBox:
            print(" combo ")
            self.range_start_tc.Hide()
            self.range_end_tc.Hide()
            self.range_every_tc.Hide()
            self.range_start_l.Hide()
            self.range_end_l.Hide()
            self.range_every_l.Hide()
        self.parent.Layout()

     # Image Area Display
     #     now in I_pnl

#    def clear_picture_area(self):
#        children = MainApp.camconf_info_pannel.picture_sizer.GetChildren()
#        for child in children:
#            item = child.GetWindow()
#            item.Destroy()

    # Take Image

    def download_and_show_picture(self, path, label, combine=False):
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        if "errror" in path.lower():
            msg_text = "Photo was not taken, \n\n" + path
            dbox = wx.MessageDialog(self, msg_text, "Error", wx.OK | wx.ICON_ERROR)
            dbox.ShowModal()
            dbox.Destroy()
        else:
            # check the claimed image actually exists on the pi
            cmd = "ls " + path
            out, error = self.parent.link_pnl.run_on_pi(cmd)
            if out.strip() == path:
                # download photo
                local_temp_img_path = os.path.join("temp", os.path.basename(path))
                img_path = self.parent.link_pnl.download_file_to_folder(path, local_temp_img_path)
                # display on screen
                if combine == True:
                    self.local_img_paths.append(img_path)
                else:
                    I_pnl.show_image_onscreen(img_path, label)


    # Take image buttons
    def take_saved_set_click(self, e):
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        settings_file = I_pnl.camconf_path_tc.GetValue()
        if settings_file.strip() == "":
            print(" - No config file selected, skipping taking picture.")
        # Take photo using module
        outpath = self.parent.shared_data.remote_pigrow_path + 'temp/'
        path = I_pnl.sets_pnl.take_image(settings_file, outpath)
        # download and show
        label = "Taken with settings stored on the Pigrow"
        self.download_and_show_picture(path, label)

    def take_set_click(self, e, filename="test_settings.jpg"):
        # create a temp settings file on the pi
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        sets_text = I_pnl.sets_pnl.make_conf_text(I_pnl.sets_pnl.setting_crtl_dict)
        cam_opt = self.cam_cb.GetValue()
        cap_opt = self.captool_cb.GetValue()
        conf_text = "cam_num=" + cam_opt + "\n"
        conf_text += "cam_opt=" + cap_opt + "\n"
        conf_text += sets_text
        rpp = self.parent.shared_data.remote_pigrow_path
        temp_set_path = rpp + "temp/temp_camconf.txt"
        print(" - Writing temp settings file to " + temp_set_path)
        self.parent.link_pnl.write_textfile_to_pi(conf_text, temp_set_path)
        # call camera's take photo command
        outpath = rpp + 'temp/'
        path = I_pnl.sets_pnl.take_image(temp_set_path, outpath)
        # show on the screen
        label = "Taken with gui settings"
        self.download_and_show_picture(path, label)

    def take_unset_click(self, e):
        print("taking unset image ")
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        outpath = self.parent.shared_data.remote_pigrow_path + 'temp/default_image.jpg'
        output, tool = I_pnl.sets_pnl.take_default(outpath)
        label = "Taken using " + tool + " default settings."
        self.download_and_show_picture(outpath, label)

    def range_btn_click(self, e):
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        # create config files with range of settings
        key = self.range_combo.GetValue()
        basic_sets = I_pnl.sets_pnl.setting_crtl_dict
        basic_sets = I_pnl.sets_pnl.make_conf_text(basic_sets)
        cam_opt = self.cam_cb.GetValue()
        cap_opt = self.captool_cb.GetValue()
        conf_text = "cam_num=" + cam_opt + "\n"
        conf_text += "cam_opt=" + cap_opt + "\n"
        conf_text += basic_sets
        scd = I_pnl.sets_pnl.setting_crtl_dict
        if type(scd[key]) == wx._core.Slider:
            range_start = self.range_start_tc.GetValue()
            range_end =self.range_end_tc.GetValue()
            range_every = self.range_every_tc.GetValue()
            opt_list = range(int(range_start), int(range_end)+1, int(range_every))
        if type(scd[key]) == wx._core.ComboBox:
            opt_list = I_pnl.sets_pnl.setting_crtl_dict[key].GetItems()
        # create selection of settings texts
        sets_texts = []
        for opt_n in opt_list:
            is_set = False
            temp_sets = ""
            for line in conf_text.splitlines():
                if "key" in line:
                    line = key + "=" + str(opt_n)
                    is_set = True
                temp_sets += line + "\n"
            if is_set == False:
                temp_sets += key + "=" + str(opt_n)
            sets_texts.append(temp_sets)
        # create config files and save to pi
        rpp = self.parent.shared_data.remote_pigrow_path
        i = 0
        settings_paths = []
        for sets_text in sets_texts:
            i = i + 1
            temp_set_path = rpp + "temp/temp_camconf_" + str(i) + ".txt"
            print(" - Writing temp settings file to " + temp_set_path)
            self.parent.link_pnl.write_textfile_to_pi(sets_text, temp_set_path)
            settings_paths.append(temp_set_path)
        # take all the images
        img_paths = []
        outpath = rpp + 'temp/'
        for set_path in settings_paths:
            path = I_pnl.sets_pnl.take_image(set_path, outpath)
            img_paths.append(path)
        # download images
        self.local_img_paths = []
        for i in range(0, len(img_paths)):
            path = img_paths[i]
            val = opt_list[i]
            label = "Range - " + key + " " + str(val)
            print(label, path)
            if not self.use_range_combine.GetValue() == True:
                self.download_and_show_picture(path, label)
            else:
                # if combine range
                self.download_and_show_picture(path, label, combine=True)
        if self.use_range_combine.GetValue() == True:
            style = self.set_style_cb.GetValue()
            output_path = os.path.join(self.parent.shared_data.frompi_path, "temp/combined.jpg")
            img_to_show = image_combine.multi_combine(self.local_img_paths, style, output_path)
            I_pnl.show_image_onscreen(img_to_show, "Combined Image")

    def cap_stack_click(self, e):
        # Make temp settings
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        rpp = self.parent.shared_data.remote_pigrow_path
        sets_text = I_pnl.sets_pnl.make_conf_text(I_pnl.sets_pnl.setting_crtl_dict)
        cam_opt = self.cam_cb.GetValue()
        cap_opt = self.captool_cb.GetValue()
        conf_text = "cam_num=" + cam_opt + "\n"
        conf_text += "cam_opt=" + cap_opt + "\n"
        conf_text += sets_text
        temp_set_path = rpp + "temp/test_noise.txt"
        self.parent.link_pnl.write_textfile_to_pi(conf_text, temp_set_path)
        # take range of settings
        pic_amount = int(self.capture_stack_count.GetValue())
        filename_list = []
        for i in range(0, pic_amount):
            path = I_pnl.sets_pnl.take_image(temp_set_path, rpp + "temp/")
            filename_list.append(path)
        # download
        self.local_img_paths = []
        for file in filename_list:
            self.download_and_show_picture(file, "Noise test", combine=True)
        # combine list of images
        style = self.set_style_cb.GetValue()
        output_path = os.path.join(self.parent.shared_data.frompi_path, "temp/combined.jpg")
        img_to_show = image_combine.multi_combine(self.local_img_paths, style, output_path)
        I_pnl.show_image_onscreen(img_to_show, style)


    def set_as_compare_click(self, e):
        file_to_set = self.parent.shared_data.most_recent_camconf_image
        print(" - Setting " + file_to_set + " as compare image.")
        without_filename = os.path.split(file_to_set)[0]
        filetype = os.path.split(file_to_set)[1].split(".")[1]
        compare_path = os.path.join(without_filename, "compare_image." + filetype)
        shutil.copy(file_to_set, compare_path)
        self.parent.shared_data.camcomf_compare_image = compare_path



#class info_pnl(wx.Panel):
class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['camera_pnl']
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (1000,1000))
        # config file choice
        ccf_label = wx.StaticText(self,  label='Camera Config file', size=(150,30))
        self.camconf_path_tc = wx.ComboBox(self, choices = [], size=(400, 30))

        #intiate settings pnls
        self.picam_set_pnl = picam_sets_pnl(self)
        self.fs_set_pnl = fs_sets_pnl(self)

        self.sets_pnl = None #self.picam_set_pnl
        cam_conf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cam_conf_sizer.Add(ccf_label, 0, wx.ALL, 5)
        cam_conf_sizer.Add(self.camconf_path_tc , 0, wx.ALL, 5)

        self.picture_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(cam_conf_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.picam_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.fs_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.picture_sizer , 0, wx.ALL, 5)


        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
        self.picam_set_pnl.Hide()
        self.fs_set_pnl.Hide()

    def show_image_onscreen(self, img_path, label):
        #
        C_pnl = self.parent.dict_C_pnl['camera_pnl']

        #
        shared_data = self.parent.shared_data
        if C_pnl.use_compare.GetValue():
            if shared_data.camcomf_compare_image == "":
                print(" - No compare image, using this one")
                shared_data.most_recent_camconf_image = img_path
                C_pnl.set_as_compare_click("e")
                img_to_show = img_path
                text_label  = label + " set as compare image"
            else:
                print("COMPARING!!!!!")
                style = C_pnl.compare_style_cb.GetValue()
                img_to_show = image_combine.combine([shared_data.camcomf_compare_image, img_path], style)
                text_label  = label + " compared with " + os.path.split(shared_data.camcomf_compare_image)[1]
        else:
            img_to_show = img_path
            text_label  = label
        #
        self.picture_sizer.Add(wx.StaticText(self,  label=text_label), 0, wx.ALL, 2)
        self.picture_sizer.Add(wx.StaticBitmap(self, -1, wx.Image(img_to_show, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        shared_data.most_recent_camconf_image = img_to_show
        self.parent.Layout()


    def clear_picture_area(self):
        children = self.picture_sizer.GetChildren()
        for child in children:
            item = child.GetWindow()
            item.Destroy()


    def show_picamcap_control(self):
        print(" Showing picam ctrl")
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.picam_set_pnl
        self.sets_pnl.Show()
        self.Layout()

    def show_fswebcam_control(self):
        print(" Showing fswebcam ctrl")
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.fs_set_pnl
        self.fs_set_pnl.Show()
        self.Layout()

    def show_uvc_control(self):
        print(" UVC CONTROL NOT YET CODED ! ! !")
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = None
        # self.fs_set_pnl.Show()
        self.Layout()
