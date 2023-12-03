import wx
import os
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

        ## Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(path_l, 0, wx.ALL, 5)
        main_sizer.Add(open_caps_folder_btn, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(p_sel_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

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
            i_pnl.first_frame_no.ChangeValue("1")
            i_pnl.set_first_image(1)

            l_img_num = len(self.cap_file_paths) - 1
            i_pnl.last_frame_no.ChangeValue(str(l_img_num))
            i_pnl.set_last_image(l_img_num)

        # filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[0]
        # MainApp.timelapse_info_pannel.set_first_image(filename)
        # filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[-1]
        # MainApp.timelapse_info_pannel.set_last_image(filename)
        # MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")


        # MainApp.timelapse_info_pannel.images_found_info.SetLabel(str(len(MainApp.timelapse_ctrl_pannel.cap_file_paths)))

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

class info_pnl(wx.Panel):
    #
        def __init__( self, parent ):
            self.parent = parent
            shared_data = parent.shared_data
            self.c_pnl = parent.dict_C_pnl['timelapse_pnl']
            w = 1000
            wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

            # Tab Title
            self.SetFont(shared_data.title_font)
            title_l = wx.StaticText(self,  label='Timelapse')
            self.SetFont(shared_data.sub_title_font)
            page_sub_title = wx.StaticText(self,  label='Assemble timelapse from captured images \n coming soon - use the one in the old gui for now')

            image_box_sizer = self.make_image_box_sizer()
            # Main Sizer
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.AddStretchSpacer(1)
            main_sizer.Add(image_box_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.AddStretchSpacer(1)
            self.SetSizer(main_sizer)

        def make_image_box_sizer(self):
            blank_img = wx.Bitmap(400, 400)
            # first image box
            self.first_img_l = wx.StaticText(self,  label='-first image- \n(date)')
            self.first_image = wx.BitmapButton(self, -1, blank_img, size=(400, 400))
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
            self.last_image = wx.BitmapButton(self, -1, blank_img, size=(400, 400))
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

        def set_first_image(self, frame):
            image_path = self.c_pnl.cap_file_paths[frame]
            filename, date = self.date_from_filename(image_path)
            image_title = filename + "\n" + date.strftime('%Y-%m-%d %H:%M:%S')
            self.first_img_l.SetLabel(image_title)


        def first_image_click(self, e):
            print("not coded to load image yet so will fail with unable to open")
            title = self.first_img_l.GetLabel()
            image_to_show = ""
            self.parent.shared_data.show_image_dialog(self, image_to_show, title)

        def first_prev_click(self, e):
            print("does nothing")

        def first_next_click(self, e):
            print("does nothing")

        def first_frame_change(self, e):
            print("does nothing")

        def set_last_image(self, frame):
            image_path = self.c_pnl.cap_file_paths[frame]
            filename, date = self.date_from_filename(image_path)
            image_title = filename + "\n" + date.strftime('%Y-%m-%d %H:%M:%S')
            self.last_img_l.SetLabel(image_title)

        def last_image_click(self, e):
            print("not coded to load image yet so will fail with unable to open")
            title = self.last_img_l.GetLabel()
            image_to_show = ""
            self.parent.shared_data.show_image_dialog(self, image_to_show, title)

        def last_prev_click(self, e):
            print("does nothing")

        def last_next_click(self, e):
            print("does nothing")

        def last_frame_change(self, e):
            print("does nothing")

        def date_from_filename(self, image_path):
            # Extract the file name without extension and folders
            s_file_name, file_extension = os.path.splitext(os.path.basename(image_path))
            file_name = s_file_name + "." + file_extension

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
