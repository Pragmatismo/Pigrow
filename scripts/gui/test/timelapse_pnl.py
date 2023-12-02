import wx
import os


class ctrl_pnl(wx.Panel):
    #
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
        select_set_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_set_click)
        select_folder_btn = wx.Button(self, label='Select\nCaps Folder')
        select_folder_btn.Bind(wx.EVT_BUTTON, self.select_new_caps_folder_click)
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
        print("does nothing")
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
        if len(self.cap_file_paths) > 0:
            print("Found; ", len(self.cap_file_paths), " image files, starting at ", self.cap_file_paths[0])
        else:
            print("No caps files found in ", cap_dir)

        # # fill the infomation boxes
        # MainApp.timelapse_info_pannel.images_found_info.SetLabel(str(len(MainApp.timelapse_ctrl_pannel.cap_file_paths)))
        # # set first and last images
        # MainApp.timelapse_info_pannel.first_frame_no.ChangeValue("1")
        # MainApp.timelapse_info_pannel.last_frame_no.ChangeValue(str(len(MainApp.timelapse_ctrl_pannel.cap_file_paths)))
        # filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[0]
        # MainApp.timelapse_info_pannel.set_first_image(filename)
        # filename = MainApp.timelapse_ctrl_pannel.cap_file_paths[-1]
        # MainApp.timelapse_info_pannel.set_last_image(filename)
        # MainApp.timelapse_ctrl_pannel.calculate_frames_click("e")

    def select_new_caps_set_click(self, e):
        print("does nothing")

    def select_new_caps_folder_click(self, e):
        print("does nothing")

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
            page_sub_title =  wx.StaticText(self,  label='Assemble timelapse from captured images \n coming soon - use the one in the old gui for now')

            # Main Sizer
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
            #main_sizer.AddStretchSpacer(1)
            self.SetSizer(main_sizer)
