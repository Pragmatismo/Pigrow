import wx
import os
import sys
import datetime


class ctrl_pnl(wx.Panel):
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        ## image set
        path_l = wx.StaticText(self,  label='Image Path')
        #path_l.SetFont(shared_data.sub_title_font)
        open_caps_folder_btn = wx.Button(self, label='Open Caps Folder')
        open_caps_folder_btn.Bind(wx.EVT_BUTTON, self.open_caps_folder_click)
        select_set_btn = wx.Button(self, label='Select\nCaps Set')
        select_set_btn.Bind(wx.EVT_BUTTON, self.select_caps_set_click)
        select_folder_btn = wx.Button(self, label='Select\nCaps Folder')
        select_folder_btn.Bind(wx.EVT_BUTTON, self.select_caps_folder_click)
        p_sel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        p_sel_sizer.Add(select_set_btn, 0, wx.ALL, 3)
        p_sel_sizer.Add(select_folder_btn, 0, wx.ALL, 3)
        ##
        framese_l = wx.StaticText(self,  label='Frame Select')
        frame_sel_sizer = self.make_frame_select_sizer()
        vid_set_sizer   = self.make_vid_set_sizer()
        ## Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(path_l, 0, wx.ALL, 5)
        main_sizer.Add(open_caps_folder_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(p_sel_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(framese_l, 0, wx.ALL, 5)
        main_sizer.Add(frame_sel_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(vid_set_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def make_frame_select_sizer(self):
        # use every nth frame
        use_every_l = wx.StaticText(self,  label='Use every')
        self.use_every_tc = wx.TextCtrl(self)
        use_e_sizer = wx.BoxSizer(wx.HORIZONTAL)
        use_e_sizer.Add(use_every_l, 0, wx.ALL, 5)
        use_e_sizer.Add(self.use_every_tc, 0, wx.ALL, 5)
        # selection method
        sel_mode_opts = self.get_sel_mode_opts()
        self.sel_mode_cb = wx.ComboBox(self, choices = sel_mode_opts)
        self.sel_mode_cb.SetValue("strict")
        #self.sel_mode_cb.Bind(wx.EVT_COMBOBOX, self.)
        # last n time period selection
        time_lim_l = wx.StaticText(self,  label='laat')
        self.time_lim_tc = wx.TextCtrl(self)
        time_limit_opts = ["all", "hours", "days", "weeks", "months" ]
        self.time_lim_cb = wx.ComboBox(self, choices = time_limit_opts)
        time_lim_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_lim_sizer.Add(time_lim_l, 0, wx.ALL, 5)
        time_lim_sizer.Add(self.time_lim_tc, 0, wx.ALL, 5)
        time_lim_sizer.Add(self.time_lim_cb, 0, wx.ALL, 5)
        # min file size
        min_size_l = wx.StaticText(self,  label='Min file size')
        self.min_size_tc = wx.TextCtrl(self)
        min_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_sizer.Add(min_size_l, 0, wx.ALL, 5)
        min_sizer.Add(self.min_size_tc, 0, wx.ALL, 5)

        max_size_l = wx.StaticText(self,  label='Max file size')
        self.max_size_tc = wx.TextCtrl(self)
        max_sizer = wx.BoxSizer(wx.HORIZONTAL)
        max_sizer.Add(max_size_l, 0, wx.ALL, 5)
        max_sizer.Add(self.max_size_tc, 0, wx.ALL, 5)
        # calc frames button
        calc_frames_btn = wx.Button(self, label='Calculate Frames')
        calc_frames_btn.Bind(wx.EVT_BUTTON, self.calc_frames_click)

        # frame select sizer
        frame_sel_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sel_sizer.Add(use_e_sizer, 0, wx.ALL, 5)
        frame_sel_sizer.Add(self.sel_mode_cb, 0, wx.ALIGN_RIGHT, 5)
        frame_sel_sizer.Add(time_lim_sizer, 0, wx.ALL, 5)
        frame_sel_sizer.Add(min_sizer, 0, wx.ALL, 1)
        frame_sel_sizer.Add(max_sizer, 0, wx.ALL, 1)
        frame_sel_sizer.Add(calc_frames_btn, 0, wx.ALIGN_RIGHT, 5)

        return frame_sel_sizer

    def get_sel_mode_opts(self):
        sel_mode_opts = self.parent.shared_data.get_module_options("selmode_", "timelapse_modules")
        return sel_mode_opts

    def make_vid_set_sizer(self):
        vid_set_l = wx.StaticText(self,  label='Video Settings')
        # audio
        # credits

        vid_set_sizer = wx.BoxSizer(wx.VERTICAL)
        vid_set_sizer.Add(vid_set_l, 0, wx.ALL, 5)

        return vid_set_sizer

    # caps folder
    def open_caps_folder_click(self, e):
        # opens the caps folder and finds all images
        frompi_path = self.parent.shared_data.frompi_path
        cap_dir = os.path.join(frompi_path, 'caps')
        self.open_caps_folder(cap_dir)

    def open_caps_folder(self, cap_dir, cap_type="jpg", cap_set=None):
        self.cap_file_paths = []
        for filefound in os.listdir(cap_dir):
            if filefound.endswith(cap_type):
                file_path = os.path.join(cap_dir, filefound)
                if not cap_set == None:
                    if filefound.split("_")[0] == cap_set:
                        self.cap_file_paths.append(file_path)
                else: #when using all images in the folder regardless of the set
                    self.cap_file_paths.append(file_path)
        self.cap_file_paths.sort()
        if not len(self.cap_file_paths) > 0:
            print("No caps files found in ", cap_dir)
        else:
            print("Found; ", len(self.cap_file_paths), " image files, starting at ", self.cap_file_paths[0])

            # # fill the infomation boxes
            i_pnl = self.parent.dict_I_pnl['timelapse_pnl']

            # # set first and last images
            i_pnl.first_frame_no.ChangeValue("0")
            i_pnl.set_first_image(0)

            l_img_num = len(self.cap_file_paths) - 1
            i_pnl.last_frame_no.ChangeValue(str(l_img_num))
            i_pnl.set_last_image(l_img_num)


        ### info box and frame calculation
        i_pnl.set_img_box()

    def select_caps_set_click(self, e):
        new_cap_path = self.caps_file_dialog()

        cap_dir = os.path.split(new_cap_path)
        cap_set = cap_dir[1].split("_")[0]  # Used to select set if more than one are present
        cap_type = cap_dir[1].split('.')[1]
        cap_dir = cap_dir[0]
        print(" Selected " + cap_dir + " with capset; " + cap_set + " filetype; " + cap_type)
        self.open_caps_folder(cap_dir, cap_type, cap_set)

    def select_caps_folder_click(self, e):
        new_cap_path = self.caps_file_dialog()

        cap_dir = os.path.split(new_cap_path)
        cap_type = cap_dir[1].split('.')[1]
        cap_dir = cap_dir[0]
        print(" Selected " + cap_dir + " filetype; " + cap_type)
        self.open_caps_folder(cap_dir, cap_type, cap_set=None)

    def caps_file_dialog(self):
        wildcard = "JPG and PNG files (*.jpg;*.png)|*.jpg;*.png|GIF files (*.gif)|*.gif"
        defdir = self.parent.shared_data.frompi_path
        openFileDialog = wx.FileDialog(self, "Select caps folder", defaultDir=defdir, wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the set you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()
        return new_cap_path

    # frame select

    def calc_frames_click(self, e):
        new_list = self.cap_file_paths.copy()

        new_list = self.trim_nth(new_list)
        print("new frame list length;", len(new_list))


    def trim_nth(self, cap_list):
        use_every = self.use_every_tc.GetValue()
        try:
            use_every = int(use_every)
        except:
            if not use_every == "":
                print("Frame selection - Use Every value must be a number")
            return cap_list
        sel_mode = self.sel_mode_cb.GetValue()
        module_name = "selmode_" + sel_mode
        self.import_module(module_name, "selmode_tool")
        new_list = selmode_tool.trim_list(cap_list, use_every)
        return new_list


    # module tools
    def import_module(self, module_name, import_name):
        print(" Importing module; " + module_name)
        if module_name in sys.modules:
            del sys.modules[module_name]
        exec('import ' + module_name + ' as ' + import_name, globals())

class info_pnl(wx.Panel):
    #
        def __init__( self, parent ):
            self.parent = parent
            self.shared_data = parent.shared_data
            self.c_pnl = parent.dict_C_pnl['timelapse_pnl']
            w = 1000
            self.pic_size = 500
            wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

            # Tab Title
            self.SetFont(self.shared_data.title_font)
            title_l = wx.StaticText(self,  label='Timelapse \n coming soon - use the one in the old gui for now')
            self.SetFont(self.shared_data.sub_title_font)
            page_sub_title = wx.StaticText(self,  label='Assemble timelapse from captured images')

            image_box_sizer = self.make_image_box_sizer()
            info_sizer = self.make_info_sizer()
            graph_sizer = self.make_graph_sizer()

            lower_sizer = wx.BoxSizer(wx.HORIZONTAL)
            lower_sizer.AddStretchSpacer(1)
            lower_sizer.Add(info_sizer, 0, wx.ALL| wx.ALIGN_CENTER_VERTICAL, 5)
            lower_sizer.AddStretchSpacer(1)
            lower_sizer.Add(graph_sizer, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            lower_sizer.AddStretchSpacer(1)

            # Main Sizer
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.AddStretchSpacer(1)
            main_sizer.Add(image_box_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.AddStretchSpacer(1)
            main_sizer.Add(lower_sizer, 0, wx.EXPAND, 5)
            main_sizer.AddStretchSpacer(1)
            self.SetSizer(main_sizer)

        def make_graph_sizer(self):
            self.SetFont(self.shared_data.sub_title_font)
            graph_l = wx.StaticText(self,  label='Graph goes here')

            graph_sizer = wx.BoxSizer(wx.VERTICAL)
            graph_sizer.Add(graph_l, 0, wx.ALL |  wx.ALIGN_CENTER_HORIZONTAL, 5)
            return graph_sizer


        def make_info_sizer(self):
            # image set info
            self.SetFont(self.shared_data.sub_title_font)
            img_set_l = wx.StaticText(self,  label='Image Set Info')

            self.SetFont(self.shared_data.item_title_font)
            set_count_l = wx.StaticText(self,  label='Images found ')
            self.SetFont(self.shared_data.info_font)
            self.set_count_t = wx.StaticText(self,  label='')
            set_panel_sizer = wx.GridSizer(2, 2, 2, 2)
            set_panel_sizer.AddMany([(set_count_l, 0, wx.ALL),
                (self.set_count_t, 0, wx.EXPAND)])

            # animation info
            ani_info_l = wx.StaticText(self,  label='Animation Info')
            self.SetFont(self.shared_data.item_title_font)
            frame_count_l = wx.StaticText(self,  label='Frame Count  ')
            self.SetFont(self.shared_data.info_font)
            self.frame_count_t = wx.StaticText(self,  label='')
            self.SetFont(self.shared_data.item_title_font)
            duration_l = wx.StaticText(self,  label='Duration  ')
            self.SetFont(self.shared_data.info_font)
            self.duration_t = wx.StaticText(self,  label='')

            ani_panel_sizer = wx.GridSizer(3, 2, 2, 2)
            ani_panel_sizer.AddMany([(frame_count_l, 0, wx.ALL),
                (self.frame_count_t, 0, wx.EXPAND),
                (duration_l, 0, wx.ALL),
                (self.duration_t, 0, wx.EXPAND),])

            info_sizer = wx.BoxSizer(wx.VERTICAL)
            info_sizer.AddStretchSpacer(1)
            info_sizer.Add(img_set_l, 0, wx.BOTTOM, 10)
            info_sizer.Add(set_panel_sizer, 0, wx.LEFT | wx.EXPAND, 25)
            info_sizer.AddStretchSpacer(1)
            info_sizer.Add(ani_info_l, 0, wx.BOTTOM, 10)
            info_sizer.Add(ani_panel_sizer, 0, wx.LEFT | wx.EXPAND, 25)
            info_sizer.AddStretchSpacer(1)
            return info_sizer

        def make_image_box_sizer(self):
            blank_img = wx.Bitmap(self.pic_size, self.pic_size)
            # first image box
            self.first_img_l = wx.StaticText(self,  label='-first image- \n(date)')
            self.first_image = wx.BitmapButton(self, -1, blank_img, size=(self.pic_size, self.pic_size))
            self.first_image.Bind(wx.EVT_BUTTON, self.first_image_click)
            first_prev_btn = wx.Button(self, label='<')
            first_prev_btn.Bind(wx.EVT_BUTTON, self.first_prev_click)
            self.first_frame_no = wx.TextCtrl(self, style=wx.TE_CENTRE)
            self.first_frame_no.Bind(wx.EVT_TEXT, self.first_frame_change)
            first_next_btn = wx.Button(self, label='>')
            first_next_btn.Bind(wx.EVT_BUTTON, self.first_next_click)

            first_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
            first_ctrl_sizer.Add(first_prev_btn, 0, wx.ALL, 5)
            first_ctrl_sizer.Add(self.first_frame_no, 0, wx.ALL, 5)
            first_ctrl_sizer.Add(first_next_btn, 0, wx.ALL, 5)

            first_img_sizer = wx.BoxSizer(wx.VERTICAL)
            first_img_sizer.Add(self.first_img_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            first_img_sizer.Add(self.first_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            first_img_sizer.Add(first_ctrl_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

            # last image box
            self.last_img_l = wx.StaticText(self,  label='-last image- \n(date)')
            self.last_image = wx.BitmapButton(self, -1, blank_img, size=(self.pic_size, self.pic_size))
            self.last_image.Bind(wx.EVT_BUTTON, self.last_image_click)
            last_prev_btn = wx.Button(self, label='<')
            last_prev_btn.Bind(wx.EVT_BUTTON, self.last_prev_click)
            self.last_frame_no = wx.TextCtrl(self, style=wx.TE_CENTRE)
            self.last_frame_no.Bind(wx.EVT_TEXT, self.last_frame_change)
            last_next_btn = wx.Button(self, label='>')
            last_next_btn.Bind(wx.EVT_BUTTON, self.last_next_click)

            last_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
            last_ctrl_sizer.Add(last_prev_btn, 0, wx.ALL, 5)
            last_ctrl_sizer.Add(self.last_frame_no, 0, wx.ALL, 5)
            last_ctrl_sizer.Add(last_next_btn, 0, wx.ALL, 5)

            last_img_sizer = wx.BoxSizer(wx.VERTICAL)
            last_img_sizer.Add(self.last_img_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            last_img_sizer.Add(self.last_image, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            last_img_sizer.Add(last_ctrl_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

            # image box sizer
            img_box_sizer = wx.BoxSizer(wx.HORIZONTAL)
            img_box_sizer.Add(first_img_sizer, 0, wx.ALL, 5)
            img_box_sizer.Add(last_img_sizer, 0, wx.ALL, 5)
            return img_box_sizer

        # info box controls
        def set_img_box(self):
            # image set info
            set_count = len(self.c_pnl.cap_file_paths)
            self.set_count_t.SetLabel(str(set_count))

            #ani info
            ani_frame_count = "not coded"
            duration = "not coded"
            self.frame_count_t.SetLabel(str(ani_frame_count))
            self.duration_t.SetLabel(str(duration))

            self.Layout()


        # first image box controls
        def set_first_image(self, frame):
            image_path = self.c_pnl.cap_file_paths[frame]
            filename, date = self.date_from_filename(image_path)
            image_title = filename + "\n" + date.strftime('%Y-%m-%d %H:%M:%S')
            self.first_img_l.SetLabel(image_title)

            try:
                self.first_ani_pic = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                first = self.shared_data.scale_pic(self.first_ani_pic, self.pic_size)
                first = first.ConvertToBitmap()
                self.first_image.SetBitmap(first)
            except:
                print("!! First frame didn't work for timelapse tab.", filename)

        def first_image_click(self, e):
            frame_num = self.first_frame_no.GetValue()
            try:
                frame_num = int(frame_num)
            except:
                return None

            image_path = self.c_pnl.cap_file_paths[frame_num]
            title = self.first_img_l.GetLabel()
            dbox = self.shared_data.show_image_dialog(None, image_path, title)
            dbox.ShowModal()
            dbox.Destroy()

        def first_prev_click(self, e):
            number = int(self.first_frame_no.GetValue())
            if number > 0:
                number = number - 1
            self.first_frame_no.SetValue(str(number))

        def first_next_click(self, e):
            number = int(self.first_frame_no.GetValue())
            total_images = len(self.c_pnl.cap_file_paths) - 1
            if number < total_images:
                number = number + 1
            self.first_frame_no.SetValue(str(number))

        def first_frame_change(self, e):
            frame_num = self.first_frame_no.GetValue()
            try:
                frame_num = int(frame_num)
            except:
                return None

            max_num = len(self.c_pnl.cap_file_paths) - 1
            if frame_num > max_num:
                self.first_frame_no.SetValue(str(max_num))
                frame_num = max_num
            self.set_first_image(frame_num)


        # last image box controls
        def set_last_image(self, frame):
            image_path = self.c_pnl.cap_file_paths[frame]
            filename, date = self.date_from_filename(image_path)
            image_title = filename + "\n" + date.strftime('%Y-%m-%d %H:%M:%S')
            self.last_img_l.SetLabel(image_title)

            try:
                self.last_ani_pic = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                first = self.shared_data.scale_pic(self.last_ani_pic, self.pic_size)
                first = first.ConvertToBitmap()
                self.last_image.SetBitmap(first)
            except:
                print("!! Last frame didn't work for timelapse tab.", filename)

        def last_image_click(self, e):
            frame_num = self.last_frame_no.GetValue()
            try:
                frame_num = int(frame_num)
            except:
                return None

            image_path = self.c_pnl.cap_file_paths[frame_num]
            title = self.first_img_l.GetLabel()
            dbox = self.shared_data.show_image_dialog(None, image_path, title)
            dbox.ShowModal()
            dbox.Destroy()

        def last_prev_click(self, e):
            number = int(self.last_frame_no.GetValue())
            if number > 0:
                number = number - 1
            self.last_frame_no.SetValue(str(number))

        def last_next_click(self, e):
            try:
                number = int(self.last_frame_no.GetValue())
            except:
                return None
            total_images = len(self.c_pnl.cap_file_paths) - 1
            if number < total_images:
                number = number + 1
            self.last_frame_no.SetValue(str(number))

        def last_frame_change(self, e):
            frame_num = self.last_frame_no.GetValue()
            try:
                frame_num = int(frame_num)
            except:
                return None

            max_num = len(self.c_pnl.cap_file_paths) - 1
            if frame_num > max_num:
                self.last_frame_no.SetValue(str(max_num))
                frame_num = max_num
            self.set_last_image(frame_num)

        # filename tools
        def date_from_filename(self, image_path):
            # Extract the file name without extension and folders
            s_file_name, file_extension = os.path.splitext(os.path.basename(image_path))
            file_name = s_file_name + file_extension

            # Check if the file name contains an underscore
            if '_' in file_name:
                # Extract the last section after the final underscore
                last_section = s_file_name.rsplit('_', 1)[-1]

                # Try to parse the last section as a Linux epoch
                try:
                    epoch_time = int(last_section)
                    date = datetime.datetime.utcfromtimestamp(epoch_time)
                    return file_name, date
                except ValueError:
                    pass

                # Try to parse the last section as a common date string
                try:
                    date = datetime.datetime.strptime(last_section, '%Y%m%d%H%M%S')
                    return file_name, date
                except ValueError:
                    pass

            return file_name, 'undetermined'