import os
import wx
import wx.lib.scrolledpanel as scrolled
import image_combine
import shutil
from picam_set_pnl import picam_sets_pnl
from fswebcam_set_pnl import fs_sets_pnl
from motion_set_pnl import motion_sets_pnl
from libcam_set_pnl import libcam_sets_pnl
import wx.lib.delayedresult as delayedresult

import time

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
        webcam_opts = ['uvccapture', 'fswebcam', 'picamcap', 'libcamera', 'motion']
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

        # record timelapse button
        quick_timelapse_btn = wx.Button(self, label='Quick Timelapse')
        quick_timelapse_btn.Bind(wx.EVT_BUTTON, self.quick_timelapse_click)

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
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(self.cam_select_l, 0, wx.ALL, 0)
        main_sizer.Add(find_select_cam_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.cap_tool_l, 0, wx.ALL, 0)
        main_sizer.Add(self.captool_cb, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(self.take_set_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(take_single_photo_btns_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(range_sizer, 0, wx.ALL, 0)
        main_sizer.Add(self.use_range_combine, 0, wx.ALL|wx.EXPAND, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(compare_sizer, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(anal_sizer, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 10)
        main_sizer.Add(quick_timelapse_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(main_sizer)

    def connect_to_pigrow(self):
        self.list_cams_click('e')
        self.seek_cam_configs()

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
            rpp = self.parent.shared_data.remote_pigrow_path
            if cap_opt == "picamcap":
                c_sets_path = rpp + "config/picam_config.txt"
            elif cap_opt == "motion":
                c_sets_path = rpp + "config/motion_config.txt"
            elif cap_opt == "libcamera":
                c_sets_path = rpp + "config/libcam_settings.txt"
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

    def read_cam_config_click(self, e, select=False):
        if select==False:
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
        I_pnl = self.parent.dict_I_pnl['camera_pnl']
        option = self.captool_cb.GetValue()
        if option == 'fswebcam':
            I_pnl.show_fswebcam_control()
        elif option == 'uvccapture':
            I_pnl.show_uvc_control()
        elif option == 'picamcap':
            I_pnl.show_picamcap_control()
        elif option == 'motion':
            I_pnl.show_motion_control()
        elif option == 'libcamera':
            I_pnl.show_libcam_control()
        # add rangeable items to range_combo box
        self.range_combo.Clear()
        scd = I_pnl.sets_pnl.setting_crtl_dict
        for key in scd.keys():
            if type(scd[key]) == wx._core.Slider or type(scd[key]) == wx._core.ComboBox:
                self.range_combo.Append(key)

    def range_combo_go(self, e):
        key = self.range_combo.GetValue()
        scd = self.parent.dict_I_pnl['camera_pnl'].sets_pnl.setting_crtl_dict
        if type(scd[key]) == wx._core.Slider:
            self.range_start_tc.Show()
            self.range_end_tc.Show()
            self.range_every_tc.Show()
            self.range_start_l.Show()
            self.range_end_l.Show()
            self.range_every_l.Show()
            self.range_start_tc.SetValue(str(scd[key].GetMin()))
            self.range_end_tc.SetValue(str(scd[key].GetMax()))
        if type(scd[key]) == wx._core.ComboBox:
            self.range_start_tc.Hide()
            self.range_end_tc.Hide()
            self.range_every_tc.Hide()
            self.range_start_l.Hide()
            self.range_end_l.Hide()
            self.range_every_l.Hide()
        self.parent.Layout()

     # Image Area Display
     #     now in I_pnl

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

    # Quick Timelapse
    def quick_timelapse_click(self, e):
        self.style_dbox = quicktl_dialog(self, self.parent)
        self.style_dbox.ShowModal()
        if self.style_dbox:
            if not self.style_dbox.IsBeingDeleted():
                self.style_dbox.Destroy()


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['camera_pnl']
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (1000,1000))
        # config file choice
        ccf_label = wx.StaticText(self,  label='Camera Config file', size=(150,30))
        self.camconf_path_tc = wx.ComboBox(self, choices = [], size=(400, 30))
        self.camconf_path_tc.Bind(wx.EVT_COMBOBOX, self.camconf_select)

        #intiate settings pnls
        self.picam_set_pnl = picam_sets_pnl(self)
        self.fs_set_pnl = fs_sets_pnl(self)
        self.motion_set_pnl = motion_sets_pnl(self)
        self.libcam_set_pnl = libcam_sets_pnl(self)

        self.sets_pnl = None #self.picam_set_pnl
        cam_conf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cam_conf_sizer.Add(ccf_label, 0, wx.ALL, 5)
        cam_conf_sizer.Add(self.camconf_path_tc , 0, wx.ALL, 5)

        # picture sizer and buttons
        self.clear_pics_btn = wx.Button(self, label='Clear pics')
        self.clear_pics_btn.Bind(wx.EVT_BUTTON, self.clear_pics_click)
        self.show_last_btn = wx.Button(self, label='show last pic')
        self.show_last_btn.Bind(wx.EVT_BUTTON, self.show_last_click)
        self.pic_buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pic_buttons_sizer.Add(self.clear_pics_btn, 0, wx.ALL, 5)
        self.pic_buttons_sizer.Add(self.show_last_btn, 0, wx.ALL, 5)

        self.picture_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(cam_conf_sizer, 0, wx.ALL, 0)
        self.main_sizer.Add(self.picam_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.fs_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.motion_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.libcam_set_pnl , 0, wx.ALL, 5)
        self.main_sizer.Add(self.pic_buttons_sizer , 0, wx.ALL, 5)
        self.main_sizer.Add(self.picture_sizer , 0, wx.ALL, 5)


        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
        self.picam_set_pnl.Hide()
        self.fs_set_pnl.Hide()
        self.motion_set_pnl.Hide()
        self.libcam_set_pnl.Hide()

    def camconf_select(self, e):
        c_pnl = self.parent.dict_C_pnl['camera_pnl']
        c_pnl.read_cam_config_click(None, select=True)

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
                style = C_pnl.compare_style_cb.GetValue()
                img_to_show = image_combine.combine([shared_data.camcomf_compare_image, img_path], style)
                text_label  = label + " compared with " + os.path.split(shared_data.camcomf_compare_image)[1]
        else:
            img_to_show = img_path
            text_label  = label
        #
        pic = wx.StaticBitmap(self, -1, wx.Image(img_to_show, wx.BITMAP_TYPE_ANY).ConvertToBitmap())
        pic.SetLabel(img_to_show)
        pic.Bind(wx.EVT_LEFT_DOWN, self.pic_click)

        self.picture_sizer.Add(wx.StaticText(self,  label=text_label), 0, wx.ALL, 2)
        self.picture_sizer.Add(pic, 0, wx.ALL, 2)
        shared_data.most_recent_camconf_image = img_to_show
        self.parent.Layout()

    def pic_click(self, e):
        bitmap = e.GetEventObject()
        path_label = bitmap.GetLabel()
        try:
            dbox = self.parent.shared_data.show_image_dialog(None, path_label, path_label)
            dbox.ShowModal()
            dbox.Destroy()
        except:
            pass

    def show_last_click(self, e):
        shared_data = self.parent.shared_data
        path = shared_data.most_recent_camconf_image
        try:
            dbox = self.parent.shared_data.show_image_dialog(None, path, path)
            dbox.ShowModal()
            dbox.Destroy()
        except:
            pass



    def clear_pics_click(self, e): # was; clear_picture_area(self):
        children = self.picture_sizer.GetChildren()
        for child in children:
            item = child.GetWindow()
            item.Destroy()


    def show_picamcap_control(self):
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.picam_set_pnl
        self.sets_pnl.Show()
        self.Layout()

    def show_fswebcam_control(self):
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.fs_set_pnl
        self.fs_set_pnl.Show()
        self.Layout()

    def show_motion_control(self):
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.motion_set_pnl
        self.sets_pnl.Show()
        self.Layout()

    def show_libcam_control(self):
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = self.libcam_set_pnl
        self.sets_pnl.Show()
        self.Layout()

    def show_uvc_control(self):
        print(" UVC CONTROL NOT YET CODED ! ! !")
        if not self.sets_pnl == None:
            self.sets_pnl.Hide()
        self.sets_pnl = None
        # self.fs_set_pnl.Show()
        self.Layout()


class quicktl_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        super(quicktl_dialog, self).__init__(*args, **kw)
        self.parent = parent
        self.link_pnl = self.parent.parent.link_pnl

        self.ScriptReadEvent, self.EVT_SCRIPT_READ = wx.lib.newevent.NewEvent()
        self.Bind(self.EVT_SCRIPT_READ, self.script_output)

        self.pipe_inst = self.init_script()
        self.InitUI()
        self.SetSize((700, 650))
        self.SetTitle("Quick Timelapse Recorder")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.set_camconf_file()

    def set_camconf_file(self):
        I_pnl = self.parent.parent.dict_I_pnl['camera_pnl']
        camconf_path = I_pnl.camconf_path_tc.GetValue()
        if camconf_path == "":
            print("ERRROR no cam conf ")
            wx.MessageBox("No camera configuration file has been selected.", "Error - no camconf", wx.OK | wx.ICON_WARNING)
            self.OnClose(None)
        else:
            time.sleep(0.5)
            self.pipe_inst.send(f"set_camset {camconf_path}\n")

    def post_output_event(self, output):
        wx.PostEvent(self, self.ScriptReadEvent(output=output))

    def InitUI(self):
        # Header Labels
        self.SetFont(self.parent.parent.shared_data.title_font)
        title = wx.StaticText(self,  label='Record Short Timelapse')
        self.SetFont(self.parent.parent.shared_data.sub_title_font)
        sub_msg = "This tool loops camera capture on the pigrow"
        sub_label = wx.StaticText(self,  label=sub_msg)

        # Buttons
        self.toggle_btn = wx.Button(self, label='Show Display')
        self.toggle_btn.Bind(wx.EVT_BUTTON, self.toggle_click)
        self.go_btn = wx.Button(self, label='Start') #, size=(175, 50))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Done') #, size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.toggle_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.go_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)

        # Switching panels control and output display
        self.ctrl_sizer = self.make_control_sizer()
        self.disp_sizer = self.make_display_sizer()
        self.disp_sizer.Hide()

        # Main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.Add(sub_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(self.ctrl_sizer, 1, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(self.disp_sizer, 1, wx.ALL|wx.EXPAND, 5)

        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)

    def toggle_click(self, e):
        if self.ctrl_sizer.IsShown():
            self.ctrl_sizer.Hide()
            self.disp_sizer.Show()
        else:
            self.ctrl_sizer.Show()
            self.disp_sizer.Hide()

        self.Layout()
        self.adjust_output_tc_size()

    def adjust_output_tc_size(self):
        # Calculate available height
        total_height = self.main_sizer.GetSize()[1]
        occupied_height = sum(item.GetSize()[1] for item in self.main_sizer.GetChildren())
        available_height = total_height - occupied_height

        # Set minimum height for output_tc
        min_height = max(available_height, 600)  # Minimum height, adjust as needed
        self.output_tc.SetMinSize((-1, min_height))


    def make_display_sizer(self):
        display_panel = wx.Panel(self)
        self.output_tc = wx.TextCtrl(display_panel, -1, "", style=wx.TE_MULTILINE | wx.TE_READONLY)

        display_sizer = wx.BoxSizer(wx.VERTICAL)
        display_sizer.Add(self.output_tc, 0, wx.EXPAND)

        display_panel.SetSizer(display_sizer)
        return display_panel

    def make_control_sizer(self):
        # Create a panel to hold the controls
        control_panel = wx.Panel(self)

        #camera tool
        camera_tool_label = wx.StaticText(control_panel, label="Camera Tool:")
        camera_tool_choices = ["picam", "fswebcam"]
        self.camera_tool_dropdown = wx.ComboBox(control_panel, choices=camera_tool_choices, style=wx.CB_READONLY)
        self.set_camtool()
        camera_tool_sizer = wx.BoxSizer(wx.HORIZONTAL)
        camera_tool_sizer.Add(camera_tool_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        camera_tool_sizer.Add(self.camera_tool_dropdown, 1, wx.ALL|wx.EXPAND, 5)

        # Outfolder line
        outfolder_label = wx.StaticText(control_panel, label="Outfolder:")
        self.outfolder_textctrl = wx.TextCtrl(control_panel)
        out_folder = self.parent.parent.shared_data.remote_pigrow_path + "caps/"
        self.outfolder_textctrl.SetValue(out_folder)
        outfolder_button = wx.Button(control_panel, label="...")
        outfolder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outfolder_sizer.Add(outfolder_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        outfolder_sizer.Add(self.outfolder_textctrl, 1, wx.ALL|wx.EXPAND, 5)
        outfolder_sizer.Add(outfolder_button, 0, wx.ALL, 5)

        # Set name line
        setname_label = wx.StaticText(control_panel, label="Set Name:")
        self.setname_textctrl = wx.TextCtrl(control_panel)
        self.setname_textctrl.SetValue("quick")
        setname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        setname_sizer.Add(setname_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        setname_sizer.Add(self.setname_textctrl, 1, wx.ALL|wx.EXPAND, 5)

        # Delay line
        delay_label = wx.StaticText(control_panel, label="Delay between frames:")
        self.delay_spin = wx.SpinCtrl(control_panel, value='5', min=0, max=1000)
        delay_sizer = wx.BoxSizer(wx.HORIZONTAL)
        delay_sizer.Add(delay_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        delay_sizer.Add(self.delay_spin, 1, wx.ALL|wx.EXPAND, 5)

        # Frame limit line
        framelimit_label = wx.StaticText(control_panel, label="Frame Limit:")
        self.framelimit_spin = wx.SpinCtrl(control_panel, value='-1', min=-1, max=60*5)
        framelimit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        framelimit_sizer.Add(framelimit_label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        framelimit_sizer.Add(self.framelimit_spin, 1, wx.ALL|wx.EXPAND, 5)

        self.set_btn = wx.Button(control_panel, label='Send Options')
        self.set_btn.Bind(wx.EVT_BUTTON, self.set_click)

        controls_sizer = wx.BoxSizer(wx.VERTICAL)
        controls_sizer.Add(camera_tool_sizer, 0, wx.EXPAND)
        controls_sizer.Add(outfolder_sizer, 0, wx.EXPAND)
        controls_sizer.Add(setname_sizer, 0, wx.EXPAND)
        controls_sizer.Add(delay_sizer, 0, wx.EXPAND)
        controls_sizer.Add(framelimit_sizer, 0, wx.EXPAND)
        controls_sizer.Add(self.set_btn, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 7)

        control_panel.SetSizer(controls_sizer)
        return control_panel

    def set_camtool(self):
        currently_supported = ["fswebcam"]
        camopt = self.parent.captool_cb.GetValue()
        if camopt in currently_supported:
            self.camera_tool_dropdown.SetValue(camopt)
        else:
            print("Using", camopt, "currently not supported in quick timelapse, defaulting to fswebcam")
            self.camera_tool_dropdown.SetValue("fswebcam")

    # Script tools
    def init_script(self):
        path_camtrig = self.parent.parent.shared_data.remote_pigrow_path + "scripts/build_test/remote_cam_loop.py"
        pipe_inst = self.link_pnl.RemoteScriptPipes(self, path_camtrig, self.link_pnl)
        return pipe_inst

    def go_click(self, e):
        if self.go_btn.GetLabel() == "Start":
            self.pipe_inst.send("start\n")
            self.go_btn.SetLabel("Stop")
            self.ctrl_sizer.Hide()
            self.disp_sizer.Show()
            self.adjust_output_tc_size()
        else:
            self.pipe_inst.send("stop\n")
            self.go_btn.SetLabel("Start")
            self.ctrl_sizer.Show()
            self.disp_sizer.Hide()
        self.Layout()

    def script_output(self, e):
        output = e.output.strip()
        current = self.output_tc.GetValue()
        updated = current + "\n" + output
        self.output_tc.SetValue(updated)
        self.output_tc.SetInsertionPointEnd()
        #print("Quick Timelapse Recieved; ", output)

    def set_click(self, e):
        self.set_settings()

    def set_settings(self):
        ctool       = self.camera_tool_dropdown.GetValue()
        if ctool == 'picam':
            self.pipe_inst.send("use_picam\n")
        elif ctool == 'fswebcam':
            self.pipe_inst.send("use_fsw\n")
        #
        outfolder   = self.outfolder_textctrl.GetValue()
        self.pipe_inst.send(f"set_outfolder {outfolder}\n")

        setname     = self.setname_textctrl.GetValue()
        self.pipe_inst.send(f"set_name {setname}\n")

        delay       = self.delay_spin.GetValue()
        self.pipe_inst.send(f"set_delay {delay}\n")

        frame_limit = self.framelimit_spin.GetValue()
        self.pipe_inst.send(f"set_flimit {frame_limit}\n")

    def OnClose(self, e):
        self.pipe_inst.close_pipe()
        self.Destroy()
