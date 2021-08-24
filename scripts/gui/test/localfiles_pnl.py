import os
import datetime
import wx
import wx.lib.scrolledpanel as scrolled

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # read / save cam config button
        self.read_btn = wx.Button(self, label='Read local files')
        self.read_btn.Bind(wx.EVT_BUTTON, self.read_click)
        self.download_btn = wx.Button(self, label='Download')
        self.download_btn.Bind(wx.EVT_BUTTON, self.download_click)
        self.upload_btn = wx.Button(self, label='Upload to pi')
        self.upload_btn.Bind(wx.EVT_BUTTON, self.upload_click)
        self.clear_downed_btn = wx.Button(self, label='clear downloaded caps')
        self.clear_downed_btn.Bind(wx.EVT_BUTTON, self.clear_downed_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.read_btn, 0, wx.ALL, 0)
        main_sizer.Add(self.download_btn, 0, wx.ALL, 0)
        main_sizer.Add(self.upload_btn, 0, wx.ALL, 0)
        main_sizer.Add(self.clear_downed_btn, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)

    def read_click(self, e):
        if self.parent.shared_data.frompi_path == "":
            print("No frompi folder set, check link to pi is active")
            return None
        config_folder = "config"
        logs_folder   = "logs"
        caps_folder   = 'caps'
        I_pnl = self.parent.dict_I_pnl['localfiles_pnl']
        I_pnl.config_file_list.read_configs(I_pnl.config_files, config_folder)
        I_pnl.log_file_list.read_logs(I_pnl.log_files, logs_folder)
        if I_pnl.r_folder_text.GetLabel().strip() == "caps":
            remote_caps = self.parent.shared_data.remote_pigrow_path + caps_folder
            I_pnl.r_folder_text.SetLabel(remote_caps)
        if I_pnl.folder_text.GetLabel().strip() == "caps":
            local_caps  = os.path.join(self.parent.shared_data.frompi_path, caps_folder)
            I_pnl.folder_text.SetLabel(local_caps)
        I_pnl.set_r_caps_text()
        I_pnl.read_caps_info()

    def download_click(self, e):
        file_dbox = file_download_dialog(self, self.parent)
        file_dbox.ShowModal()
        file_dbox.Destroy()
        self.read_click("e")

    def upload_click(self, e):
        file_dbox = file_upload_dialog(self, self.parent)
        file_dbox.ShowModal()
        file_dbox.Destroy()

    def connect_to_pigrow(self):
        print(" LOCALFILES KNOWS YOU JUST CONNECTED TO A PIGROW - WOOT")
        self.read_click("e")

    def clear_downed_click(self, e):
        # looks at local files an remote files removing any from the pigrows
        # that are already stored in the local caps folder for that pigrow
        print("clearing already downloaded images off pigrow")
        remote_caps_path = self.parent.dict_I_pnl['localfiles_pnl'].r_folder_text.GetLabel()
        local_caps_path = self.parent.dict_I_pnl['localfiles_pnl'].folder_text.GetLabel()
        caps_files = os.listdir(local_caps_path)
        print("---------")
        print(local_caps_path)
        print(len(caps_files))
        print("-----")
        caps_files.sort()
        print(str(len(caps_files)) + " files locally \n")
        #read pi's caps folder
        try:

            out, error = self.parent.link_pnl.run_on_pi("ls " + remote_caps_path)
            remote_caps = out.splitlines()
            print(len(remote_caps))
            print("-------------------")
        except Exception as e:
            print(("-- reading remote caps folder failed; " + str(e)))
            remote_caps = []
        count = 0
        for the_remote_file in remote_caps:
            if the_remote_file in caps_files:
                the_remote_file = remote_caps_path + "/" + the_remote_file
                #MainApp.status.write_bar("clearing - " + the_remote_file)
                print("clearing - " + the_remote_file)
                self.parent.link_pnl.run_on_pi("rm " + the_remote_file, False)
                #wx.GetApp().Yield()
                count = count + 1
            #MainApp.status.write_bar("Cleared " + str(count) + " files from the pigrow")
            print("Cleared " + str(count) + " files from the pigrow")
        # when done refreh the file info
        self.parent.dict_I_pnl['localfiles_pnl'].set_r_caps_text()

class file_upload_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.user_files_to_upload = []
        self.user_folders_to_upload = []
        super(file_upload_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 400))
        self.SetTitle("Upload files to Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # draw the pannel
        label = wx.StaticText(self,  label='Select elements to upload onto pi')

        # select files or folders to download
        self.select_file_btn = wx.Button(self, label='Select files', size=(175, 50))
        self.select_file_btn.Bind(wx.EVT_BUTTON, self.select_file_click)
        # select files
        self.cb_overwrite = wx.CheckBox(self, label='Overwrite existing')
        self.selected_files_l = wx.StaticText(self,  label='--')
        select_file_sizer = wx.BoxSizer(wx.VERTICAL)
        select_file_sizer.Add(self.select_file_btn, 0, wx.ALL|wx.EXPAND, 5)
        select_file_sizer.Add(self.cb_overwrite, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #

        self.selected_dest_folder_l = wx.StaticText(self,  label='--')
        self.select_upload_folder_btn = wx.Button(self, label='Select upload folder', size=(175, 50))
        self.select_upload_folder_btn.Bind(wx.EVT_BUTTON, self.select_upload_folder_click)
        select_dest_sizer = wx.BoxSizer(wx.HORIZONTAL)
        select_dest_sizer.Add(self.selected_dest_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        select_dest_sizer.Add(self.select_upload_folder_btn, 0, wx.ALL|wx.EXPAND, 5)

        #buttons
        self.upload_btn = wx.Button(self, label='Upload', size=(175, 50))
        self.upload_btn.Bind(wx.EVT_BUTTON, self.start_upload_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.upload_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(select_file_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(select_dest_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def select_file_click(self, e):
        dialog = wx.FileDialog(self, "Select files to upload to pi", style=wx.FD_MULTIPLE)
        if dialog.ShowModal() == wx.ID_OK:
            self.filelist = dialog.GetPaths()
        self.Layout()

    def select_upload_folder_click(self, e):
        self.parent.parent.link_pnl.select_files_on_pi(single_folder=True)
        selected_files = self.parent.parent.link_pnl.selected_files
        self.selected_folders = self.parent.parent.link_pnl.selected_folders
        self.selected_dest_folder_l.SetLabel(self.selected_folders[0])
        self.Layout()

    def start_upload_click(self, e):
        dest_fold = self.selected_folders[0]
        tocopy_files = self.filelist
        print("Wants to copy", len(tocopy_files), "to", dest_fold)
        copy_list = []
        for file in tocopy_files:
            dest = dest_fold + os.path.split(file)[1]
            copy_list.append([file, dest])
        print (copy_list)
        self.parent.parent.link_pnl.upload_files(copy_list)
        self.Layout()

    def OnClose(self, e):
        #closes the dialogue box
    #    self.user_files_to_upload = []
    #    self.user_folders_to_upload = []
        self.Destroy()

class file_download_dialog(wx.Dialog):
    #Dialog box for downloding files from pi to local storage folder
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        self.user_files_to_download = []
        self.user_folders_to_download = []
        super(file_download_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((700, 400))
        self.SetTitle("Download files from Pigrow")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        # draw the pannel
        label = wx.StaticText(self,  label='Select elements to download to local storage')
        # tick boxes for default folder select
        self.cb_conf = wx.CheckBox(self,  label='Config')
        self.cb_logs = wx.CheckBox(self,  label='Logs')
        self.cb_caps = wx.CheckBox(self,  label='Photos')
        self.cb_graph = wx.CheckBox(self, label='Graphs')
        tickbox_sizer = wx.BoxSizer(wx.VERTICAL)
        tickbox_sizer.Add(self.cb_conf, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_logs, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_caps, 0, wx.ALL|wx.EXPAND, 5)
        tickbox_sizer.Add(self.cb_graph, 0, wx.ALL|wx.EXPAND, 5)
        # select files or folders to download
        self.select_file_btn = wx.Button(self, label='Select Folder', size=(175, 50))
        self.select_file_btn.Bind(wx.EVT_BUTTON, self.select_file_click)
        self.cb_overwrite = wx.CheckBox(self, label='Overwrite existing')
        self.selected_files_l = wx.StaticText(self,  label='--')
        self.selected_folders_l = wx.StaticText(self,  label='--')
        select_file_sizer = wx.BoxSizer(wx.VERTICAL)
        select_file_sizer.Add(self.select_file_btn, 0, wx.ALL|wx.EXPAND, 5)
        select_file_sizer.Add(self.cb_overwrite, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        select_file_sizer.Add(self.selected_files_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        select_file_sizer.Add(self.selected_folders_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #buttons
        self.download_btn = wx.Button(self, label='Download', size=(175, 50))
        self.download_btn.Bind(wx.EVT_BUTTON, self.start_download_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.download_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # mid pnl
        mid_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mid_sizer.AddStretchSpacer(1)
        mid_sizer.Add(tickbox_sizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        mid_sizer.AddStretchSpacer(1)
        mid_sizer.Add(select_file_sizer, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        mid_sizer.AddStretchSpacer(1)
        # main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(mid_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def select_file_click(self, e):
        self.parent.parent.link_pnl.select_files_on_pi()
        selected_files = self.parent.parent.link_pnl.selected_files
        selected_folders = self.parent.parent.link_pnl.selected_folders
        if len(selected_files) == 0 and len(selected_folders) == 0:
            return None
        # folders
        if len(selected_folders) > 0:
            in_fold_list = self.selected_folders_l.GetLabel()
            for fold in selected_folders:
                in_fold_list += "\n" + fold
                self.user_folders_to_download.append(fold)
            in_fold_list = in_fold_list.replace("--\n", "")
            self.selected_folders_l.SetLabel(in_fold_list)

        # files
        file_list = self.user_files_to_download
        if len(selected_files) > 0:
            for s_file in selected_files:
                if not s_file in self.user_files_to_download:
                    self.user_files_to_download.append(s_file)
            # make text
            in_file_text = ""
            for item in self.user_files_to_download:
                in_file_text += item[0] + "\n"
            self.selected_files_l.SetLabel(in_file_text)
        self.Layout()


    def start_download_click(self, e):
        folders_overwrite = []
        folders_newonly   = []
        remote_path = self.parent.parent.shared_data.remote_pigrow_path
        if self.cb_conf.GetValue() == True:
            folders_overwrite.append(remote_path + "config")
        if self.cb_logs.GetValue() == True:
            folders_overwrite.append(remote_path + "logs")
        if self.cb_caps.GetValue() == True:
            remote_caps_path = self.parent.parent.dict_I_pnl['localfiles_pnl'].r_folder_text.GetLabel()
            print(" ---remote---- ", remote_caps_path, " --------- ")
            local_caps_path = self.parent.parent.dict_I_pnl['localfiles_pnl'].folder_text.GetLabel()
            print(" ---local---- ", local_caps_path, " --------- ")
            folders_newonly.append([remote_caps_path, local_caps_path])
        if self.cb_graph.GetValue() == True:
            folders_overwrite.append(remote_path + "graphs")
        # set if overwrite is ticked
        if self.cb_overwrite.GetValue() == True:
            print(" OVERWRITING FILES")
            folders_overwrite = folders_overwrite + self.user_folders_to_download
            extra_files_over = []
            extra_files = self.user_files_to_download
        else:
            print(" NOT OVERWRITING FILES")
            folders_newonly = folders_newonly + self.user_folders_to_download
            extra_files_over = self.user_files_to_download
            extra_files = []
        #
        if len(extra_files) > 0 or len(extra_files_over) > 0:
            print(" HAS USER FILES TO DOWNLOAD!!!! ")
        if len(self.user_folders_to_download) > 0:
            print(" HAS USER FOLDERS TO DOWNLOAD!!!! ")

        # only run if something to download
        if not len(folders_overwrite) == 0 or not len(extra_files_over) == 0:
            self.parent.parent.link_pnl.download_folder(folders_overwrite, overwrite=True, extra_files=extra_files_over)
        if not len(folders_newonly) == 0 or not len(extra_files) == 0:
            self.parent.parent.link_pnl.download_folder(folders_newonly, overwrite=False, extra_files=extra_files)

        #if not len(folders_overwrite) == 0 or not len(folders_newonly) == 0:
        self.user_files_to_download = []
        self.user_folders_to_download = []
        self.Destroy()

    def OnClose(self, e):
        #closes the dialogue box
        self.user_files_to_download = []
        self.user_folders_to_download = []
        self.Destroy()

#class info_pnl(wx.Panel):
class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['localfiles_pnl']
        w = 1000
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (w,-1))
        # Title and Subtitle
        page_title =  wx.StaticText(self,  label='Local Files')
        page_sub_title =  wx.StaticText(self,  label='Files downloaded from the pi and stored locally')
        page_title.SetFont(shared_data.title_font)
        page_sub_title.SetFont(shared_data.sub_title_font)
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Config Files
        config_l = wx.StaticText(self,  label='Config')
        config_l.SetFont(shared_data.item_title_font)
        self.config_files = self.config_file_list(self, 1)
        self.config_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.config_files.doubleclick_config)
        # Log Files
        log_l = wx.StaticText(self,  label='Log')
        log_l.SetFont(shared_data.item_title_font)
        self.log_files = self.log_file_list(self, 1)
        self.log_files.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.log_files.doubleclick_log)

        tables_sizer = wx.BoxSizer(wx.VERTICAL)
        tables_sizer.Add(config_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.config_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(log_l, 0, wx.ALL|wx.EXPAND, 3)
        tables_sizer.Add(self.log_files, 1, wx.ALL|wx.EXPAND, 3)
        tables_sizer.SetItemMinSize(self.config_files, (w, -1))
        tables_sizer.SetItemMinSize(self.log_files, (w, -1))

        #photos
        #local photo storage info
        photo_l = wx.StaticText(self,  label='Photos', size=(75,25))
        photo_l.SetFont(shared_data.item_title_font)
        # local caps folder
        caps_folder_l = wx.StaticText(self,  label='Local;')
        caps_folder = os.path.join(shared_data.frompi_path, 'caps')
        self.folder_text = wx.StaticText(self,  label=caps_folder)
        self.set_caps_folder_btn = wx.Button(self, label='...')
        self.set_caps_folder_btn.Bind(wx.EVT_BUTTON, self.set_caps_folder_click)
        caps_folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        caps_folder_sizer.Add(caps_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        caps_folder_sizer.Add(self.folder_text, 0, wx.ALL|wx.EXPAND, 5)
        caps_folder_sizer.Add(self.set_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 5)
        # remote caps folder
        r_caps_folder_l = wx.StaticText(self,  label='Remote;')
        r_caps_folder = shared_data.remote_pigrow_path + 'caps'
        self.r_folder_text = wx.StaticText(self,  label=r_caps_folder)
        self.set_r_caps_folder_btn = wx.Button(self, label='...')
        self.set_r_caps_folder_btn.Bind(wx.EVT_BUTTON, self.set_r_caps_folder_click)
        r_caps_folder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        r_caps_folder_sizer.Add(r_caps_folder_l, 0, wx.ALL|wx.EXPAND, 5)
        r_caps_folder_sizer.Add(self.r_folder_text, 0, wx.ALL|wx.EXPAND, 5)
        r_caps_folder_sizer.Add(self.set_r_caps_folder_btn, 0, wx.ALL|wx.EXPAND, 5)

        self.photo_first_text = wx.StaticText(self, label='--')
        self.photo_mid_text   = wx.StaticText(self, label='--', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.r_mid_text       = wx.StaticText(self, label='--', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.photo_last_text  = wx.StaticText(self, label='--')

        photo_dates_sizer = wx.BoxSizer(wx.HORIZONTAL)
        photo_dates_sizer.Add(self.photo_first_text, 0, wx.RIGHT, 5)
        photo_dates_sizer.AddStretchSpacer(1)
        photo_dates_sizer.Add(self.photo_last_text, 0, wx.LEFT, 5)
        photo_mid_sizer = wx.BoxSizer(wx.VERTICAL)
        photo_mid_sizer.Add(caps_folder_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_mid_sizer.Add(r_caps_folder_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_mid_sizer.Add(photo_dates_sizer, 0, wx.ALL|wx.EXPAND, 1)
        photo_mid_sizer.Add(self.photo_mid_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        photo_mid_sizer.Add(self.r_mid_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        blank_img = wx.Bitmap(255, 255)
        self.first_photo_title = wx.StaticText(self,  label='first image')
        self.photo_folder_first_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        self.photo_folder_first_pic.SetToolTip("none")
        self.photo_folder_first_pic.Bind(wx.EVT_BUTTON, self.img_click)
        self.last_photo_title = wx.StaticText(self,  label='last image')
        self.photo_folder_last_pic = wx.BitmapButton(self, -1, blank_img, size=(255, 255))
        self.photo_folder_last_pic.SetToolTip("none")
        self.photo_folder_last_pic.Bind(wx.EVT_BUTTON, self.img_click)
        first_pic_sizer = wx.BoxSizer(wx.VERTICAL)
        first_pic_sizer.Add(self.photo_folder_first_pic, 0, wx.ALL|wx.EXPAND, 5)
        first_pic_sizer.Add(self.first_photo_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        last_pic_sizer = wx.BoxSizer(wx.VERTICAL)
        last_pic_sizer.Add(self.photo_folder_last_pic, 0, wx.ALL|wx.EXPAND, 5)
        last_pic_sizer.Add(self.last_photo_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        photo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        photo_sizer.Add(first_pic_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_sizer.Add(photo_mid_sizer, 0, wx.ALL|wx.EXPAND, 5)
        photo_sizer.Add(last_pic_sizer, 0, wx.ALL|wx.EXPAND, 5)


        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(tables_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(photo_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)

    def set_r_caps_folder_click(self, e):
        print("pressed to open remote caps path")
        self.parent.link_pnl.select_files_on_pi(single_folder=True)
        selected_folders = self.parent.link_pnl.selected_folders
        self.r_folder_text.SetLabel(selected_folders[0])
        self.set_r_caps_text()
        self.Layout()

    def set_r_caps_text(self):
        r_path = self.r_folder_text.GetLabel()
        out, error = self.parent.link_pnl.run_on_pi("ls " + r_path)
        r_file_list = out.splitlines()
        text = "Remote folder " + str(len(r_file_list)) + " files"
        if len(r_file_list) > 1:
            f_pic_date = self.parent.shared_data.date_from_fn(r_file_list[0])
            l_pic_date = self.parent.shared_data.date_from_fn(r_file_list[-1])
            if f_pic_date == None or l_pic_date == None:
                text += "\nfilename dates not readable"

            else:
                time_delta = l_pic_date - f_pic_date
                text += "\n" + str(f_pic_date) + " - " + str(l_pic_date)
                text += "\nDuration " + str(time_delta)

        self.r_mid_text.SetLabel(text)


    def img_click(self, e):
        obj = e.GetEventObject()
        tip_path = obj.GetToolTipText()
        print (tip_path)
        if not tip_path == "none":
            dbox = self.parent.shared_data.show_image_dialog(None, tip_path, "First image")
            dbox.ShowModal()
            dbox.Destroy()

    def set_caps_folder_click(self, e):
        # get folder
        wildcard = "JPG and PNG files (*.jpg;*.png)|*.jpg;*.png|GIF files (*.gif)|*.gif"
        openFileDialog = wx.FileDialog(self, "Select caps folder", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()
        cap_dir = os.path.split(new_cap_path)[0]
        #
        self.folder_text.SetLabel(cap_dir)
        self.read_caps_info()
        self.Layout()

    def read_caps_info(self):
        caps_folder = self.folder_text.GetLabel()
        file_list = os.listdir(caps_folder)
        pic_list = []
        img_types = ['jpg', 'gif', 'png', 'bmp', 'raw']
        for item in file_list:
            if "." in item:
                img_type = item.split(".")[1]
                if img_type in img_types:
                    full_path = os.path.join(caps_folder, item)
                    pic_list.append(full_path)
        pic_list.sort()

        self.set_mid_text(pic_list)
        if len(pic_list) > 0:
            name = os.path.split(pic_list[0])[1]
            self.first_photo_title.SetLabel(name)
            self.set_image_preview(pic_list[0], 'first')
            self.photo_first_text.SetLabel(self.make_image_text(pic_list[0]))
            if len(pic_list) > 1:
                name = os.path.split(pic_list[-1])[1]
                self.last_photo_title.SetLabel(name)
                self.set_image_preview(pic_list[-1], 'last')
                self.photo_last_text.SetLabel(self.make_image_text(name))
            else:
                print(" only one image in caps folder")
        else:
            print(" No image files to load")

    def set_image_preview(self, img_path, place):
        #print("Loading -", img_path, "to", place)
        try:
            pic = wx.Image(img_path, wx.BITMAP_TYPE_ANY)
            pic = self.parent.shared_data.scale_pic(pic, 300)
            pic = pic.ConvertToBitmap()
            if place == 'first':
                self.photo_folder_first_pic.SetToolTip(img_path)
                self.photo_folder_first_pic.SetBitmap(pic)
            if place == 'last':
                self.photo_folder_last_pic.SetToolTip(img_path)
                self.photo_folder_last_pic.SetBitmap(pic)
        except:
            #raise
            print("!! image in local caps folder didn't work.", img_path)

    def make_image_text(self, pic_path):
        pic_date = self.parent.shared_data.date_from_fn(pic_path)
        pic_text = str(pic_date)
        return pic_text

    def set_mid_text(self, pic_list):
        mid_text = str(len(pic_list)) + " files locally"
        # length of image dates
        if len(pic_list) > 1:
            date_f = self.parent.shared_data.date_from_fn(pic_list[0])
            date_l = self.parent.shared_data.date_from_fn(pic_list[-1])
            if date_f == None or date_l == None:
                mid_text += "\ndates not readable"
            else:
                caps_delta = date_l - date_f
                mid_text += "\nDuration " + str(caps_delta)

        self.photo_mid_text.SetLabel(mid_text)
        self.Layout()


    class config_file_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.InsertColumn(3, 'updated?')
            self.autosizeme()

        def autosizeme(self):
            if self.GetItemCount() == 0:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(3, wx.LIST_AUTOSIZE_USEHEADER)
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(3, wx.LIST_AUTOSIZE)

        def add_to_config_list(self, name, mod_date, age, update_status):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))
            self.SetItem(0, 3, str(update_status))

        def read_configs(self, folder_name):
            self.DeleteAllItems()
            print("Loading content of config folder into listctrl")
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            config_files = os.listdir(full_path)
            for file in config_files:
                if file.endswith("txt"):
                    thing_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(thing_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    update_status = "unchecked"
                    self.add_to_config_list(file, modified, file_age, update_status)
            self.autosizeme()

        def doubleclick_config(self, e):
            shared_data = self.parent.parent.shared_data
            index =  e.GetIndex()
            filename = self.GetItem(index, 0).GetText()
            file_path = os.path.join(shared_data.frompi_path, "config", filename)
            with open(file_path, "r") as config_file:
                config_file_text = config_file.read()
            dbox = shared_data.scroll_text_dialog(None, config_file_text, "Editing " + filename, True, False)
            dbox.ShowModal()
            out_conf = dbox.text
            dbox.Destroy()
            if out_conf == None:
                #print("User aborted")
                return None
            else:
                if not out_conf == config_file_text:
                    question_text = "Save changes to config file?"
                    question_text += "\n\nNote: This will not change it on the pi until you upload it over writing the original."
                    dbox = wx.MessageDialog(self, question_text, "Save Changes?", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                    answer = dbox.ShowModal()
                    if (answer == wx.ID_OK):
                        with open(file_path, "w") as config_file:
                            config_file.write(out_conf)
                        print(" Config file " + filename + " changes saved")
                else:
                    #print("Config file unchanged")
                    return None

    class log_file_list(wx.ListCtrl):
        def __init__(self, parent, id):
            self.parent = parent
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT)
            self.InsertColumn(0, 'Filename')
            self.InsertColumn(1, 'date modified')
            self.InsertColumn(2, 'age')
            self.autosizeme()

        def doubleclick_log(self, e):
            shared_data = self.parent.parent.shared_data
            index =  e.GetIndex()
            filename = self.GetItem(index, 0).GetText()
            print(" not doing anything with the log at this momement")

        def autosizeme(self):
            if self.GetItemCount() == 0:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
            else:
                self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
                self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        def add_to_logs_list(self, name, mod_date, age):
            self.InsertItem(0, str(name))
            self.SetItem(0, 1, str(mod_date))
            self.SetItem(0, 2, str(age))

        def read_logs(self, folder_name):
            self.DeleteAllItems()
            full_path = os.path.join(self.parent.parent.shared_data.frompi_path, folder_name)
            logs_files = os.listdir(full_path)
            for file in logs_files:
                if file.endswith("txt"):
                    file_path = os.path.join(full_path, file)
                    modified = os.path.getmtime(file_path)
                    modified = datetime.datetime.fromtimestamp(modified)
                    file_age = datetime.datetime.now() - modified
                    modified = modified.strftime("%Y-%m-%d %H:%M")
                    file_age = str(file_age).split(".")[0]
                    self.add_to_logs_list(file, modified, file_age)
            self.autosizeme()
