import wx
import os
import re
import sys
import datetime
import wx.lib.delayedresult as delayedresult
from PIL import Image, ImageDraw, ImageEnhance

class ctrl_pnl(wx.Panel):
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        self.trimmed_frame_list = []
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
        vid_set_l = wx.StaticText(self,  label='Video Settings')
        vid_set_sizer   = self.make_vid_set_sizer()
        render_l = wx.StaticText(self,  label='Render')
        render_sizer    = self.make_render_sizer()
        imgset_l = wx.StaticText(self,  label='Create Image Set')
        imgset_sizer    = self.make_imgset_sizer()
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
        main_sizer.Add(vid_set_l, 0, wx.ALL, 5)
        main_sizer.Add(vid_set_sizer, 0, wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(render_l, 0, wx.ALL, 5)
        main_sizer.Add(render_sizer, 0, wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(imgset_l, 0, wx.ALL, 5)
        main_sizer.Add(imgset_sizer, 0, wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def style_set_go(self, e):
        print("style set event triggered mean the style set creation is complete")
        print("created set in", e.out_folder)
        print("result output =". e.msg)

    def make_render_sizer(self):
        fps_l = wx.StaticText(self,  label='FPS')
        self.fps_tc = wx.TextCtrl(self)
        self.fps_tc.SetValue("25")
        self.Bind(wx.EVT_TEXT, self.list_val_changed, self.fps_tc)
        fps_sizer = wx.BoxSizer(wx.HORIZONTAL)
        fps_sizer.Add(fps_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        fps_sizer.Add(self.fps_tc, 0, wx.ALL, 2)

        outfile_l = wx.StaticText(self,  label='Outfile')
        default_path = os.path.join(self.parent.shared_data.frompi_base_path, "timelapse.mp4")
        self.outfile_tc = wx.TextCtrl(self)
        self.outfile_tc.SetValue(default_path)
        set_outfile_btn = wx.Button(self, label='...', size=(35,29))
        set_outfile_btn.Bind(wx.EVT_BUTTON, self.set_outfile_click)
        outfile_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outfile_sizer.Add(outfile_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        outfile_sizer.Add(self.outfile_tc, 40, wx.EXPAND, 2)
        outfile_sizer.Add(set_outfile_btn, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        render_btn = wx.Button(self, label='Render')
        render_btn.Bind(wx.EVT_BUTTON, self.render_click)
        play_btn = wx.Button(self, label='Play')
        play_btn.Bind(wx.EVT_BUTTON, self.play_click)
        butts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        butts_sizer.Add(render_btn, 4, wx.EXPAND, 2)
        butts_sizer.Add(play_btn, 0, wx.ALL, 2)

        render_sizer = wx.BoxSizer(wx.VERTICAL)
        render_sizer.Add(fps_sizer, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)
        render_sizer.Add(outfile_sizer, 0, wx.ALL | wx.EXPAND, 2)
        render_sizer.Add(butts_sizer, 0, wx.ALL | wx.EXPAND, 2)

        return render_sizer

    def make_frame_select_sizer(self):
        # use every nth frame
        use_every_l = wx.StaticText(self,  label='Use every')

        self.use_every_tc = wx.TextCtrl(self)
        self.Bind(wx.EVT_TEXT, self.list_val_changed, self.use_every_tc)
        use_e_sizer = wx.BoxSizer(wx.HORIZONTAL)
        use_e_sizer.Add(use_every_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        use_e_sizer.Add(self.use_every_tc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        # selection method
        sel_mode_opts = self.get_sel_mode_opts()
        self.sel_mode_cb = wx.ComboBox(self, choices = sel_mode_opts)
        self.Bind(wx.EVT_COMBOBOX, self.list_val_changed, self.sel_mode_cb)
        self.sel_mode_cb.SetValue("strict")
        #self.sel_mode_cb.Bind(wx.EVT_COMBOBOX, self.)
        # last n time period selection
        time_lim_l = wx.StaticText(self,  label='last')
        self.time_lim_tc = wx.TextCtrl(self)
        self.Bind(wx.EVT_TEXT, self.list_val_changed, self.time_lim_tc)
        time_limit_opts = ["all", "hours", "days", "weeks", "months"]
        self.time_lim_cb = wx.ComboBox(self, choices = time_limit_opts)
        self.Bind(wx.EVT_COMBOBOX, self.list_val_changed, self.time_lim_cb)
        self.time_lim_cb.SetValue("all")
        time_lim_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_lim_sizer.Add(time_lim_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        time_lim_sizer.Add(self.time_lim_tc, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        time_lim_sizer.Add(self.time_lim_cb, 0, wx.ALL, 5)
        # min file size
        min_size_l = wx.StaticText(self,  label='Min file size')
        self.min_size_tc = wx.TextCtrl(self)
        self.Bind(wx.EVT_TEXT, self.list_val_changed, self.min_size_tc)
        min_sizer = wx.BoxSizer(wx.HORIZONTAL)
        min_sizer.Add(min_size_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        min_sizer.Add(self.min_size_tc, 0, wx.ALL, 5)

        # calc frames button
        calc_frames_btn = wx.Button(self, label='Calculate Frames')
        calc_frames_btn.Bind(wx.EVT_BUTTON, self.calc_frames_click)
        self.calc_cb = wx.CheckBox(self, label='')
        self.calc_cb.SetValue(True)
        calc_sizer = wx.BoxSizer(wx.HORIZONTAL)
        calc_sizer.Add(calc_frames_btn, 0, wx.ALL, 2)
        calc_sizer.Add(self.calc_cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        # frame select sizer
        frame_sel_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sel_sizer.Add(use_e_sizer, 0, wx.ALL, 5)
        frame_sel_sizer.Add(self.sel_mode_cb, 0, wx.ALIGN_RIGHT, 5)
        frame_sel_sizer.Add(time_lim_sizer, 0, wx.ALL, 5)
        frame_sel_sizer.Add(min_sizer, 0, wx.ALL, 1)
        frame_sel_sizer.Add(calc_sizer, 0, wx.ALIGN_RIGHT, 5)

        return frame_sel_sizer

    def list_val_changed(self, e=None):
        # Debounce the function by delaying its execution
        if self.calc_cb.GetValue() == True:
            wx.CallAfter(self.calc_frames_click)

    def get_sel_mode_opts(self):
        sel_mode_opts = self.parent.shared_data.get_module_options("selmode_", "timelapse_modules")
        return sel_mode_opts

    def get_credit_opts(self):
        sel_credit_opts = self.parent.shared_data.get_module_options("credits_", "timelapse_modules")

        return sel_credit_opts

    def make_vid_set_sizer(self):
        # audio
        audio_l = wx.StaticText(self,  label='Audio')
        self.audio_tc = wx.TextCtrl(self)
        audio_btn = wx.Button(self, label='...', size=(35,29))
        audio_btn.Bind(wx.EVT_BUTTON, self.audio_click)
        audio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        audio_sizer.Add(audio_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        audio_sizer.Add(self.audio_tc, 40, wx.EXPAND, 2)
        audio_sizer.Add(audio_btn, 0, wx.ALL, 2)

        # credits
        credits_l = wx.StaticText(self,  label='Credits')
        credits_opts = ["none", "freeze"] + self.get_credit_opts()
        self.credits_cb = wx.ComboBox(self, choices = credits_opts)
        self.credits_cb.SetValue("none")
        self.Bind(wx.EVT_COMBOBOX, self.list_val_changed, self.credits_cb)
        self.credit_num_cb = wx.TextCtrl(self, size=(50, 29))
        self.credit_num_cb.SetValue("2")
        self.Bind(wx.EVT_TEXT, self.list_val_changed, self.credit_num_cb)
        credits_sizer = wx.BoxSizer(wx.HORIZONTAL)
        credits_sizer.Add(credits_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        credits_sizer.Add(self.credits_cb, 0, wx.ALL | wx.EXPAND, 5)
        credits_sizer.Add(self.credit_num_cb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # sizer
        vid_set_sizer = wx.BoxSizer(wx.VERTICAL)
        vid_set_sizer.Add(audio_sizer, 0, wx.EXPAND, 5)
        vid_set_sizer.Add(credits_sizer, 0, wx.ALL, 5)

        return vid_set_sizer

    def make_imgset_sizer(self):

        log_overlay_btn = wx.Button(self, label='Overlay Log')
        log_overlay_btn.Bind(wx.EVT_BUTTON, self.log_overlay_click)

        imgset_overlay_btn = wx.Button(self, label='Overlay Image Set')
        imgset_overlay_btn.Bind(wx.EVT_BUTTON, self.imgset_overlay_click)

        stylized_btn = wx.Button(self, label='Stylized Set')
        stylized_btn.Bind(wx.EVT_BUTTON, self.stylized_click)

        # sizer
        imgset_sizer = wx.BoxSizer(wx.VERTICAL)
        imgset_sizer.Add(log_overlay_btn, 0, wx.EXPAND, 5)
        imgset_sizer.Add(imgset_overlay_btn, 0, wx.EXPAND, 5)
        imgset_sizer.Add(stylized_btn, 0, wx.EXPAND, 5)

        return imgset_sizer


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
            i_pnl.set_first_image(0, resize=True)

            l_img_num = len(self.cap_file_paths) - 1
            i_pnl.last_frame_no.ChangeValue(str(l_img_num))
            i_pnl.set_last_image(l_img_num, resize=True)


        ### info box and frame calculation
        if self.calc_cb.GetValue() == True:
            self.calc_frames_click(None)

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
        if defdir == "":
            defdir = self.parent.shared_data.frompi_base_path
        openFileDialog = wx.FileDialog(self, "Select caps folder", defaultDir=defdir, wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the set you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()
        return new_cap_path

    # frame select

    def calc_frames_click(self, e=None):
        i_pnl = self.parent.dict_I_pnl['timelapse_pnl']
        try:
            start = int(i_pnl.first_frame_no.GetValue())
            stop = int(i_pnl.last_frame_no.GetValue())
        except:
            print("Error - Timelapse - First and Last frame numbers not numbers!")
            raise
            return None

        new_list = self.cap_file_paths[start:stop].copy()

        new_list = self.limit_to_date(new_list)
        new_list = self.limit_to_size(new_list)
        new_list = self.trim_nth(new_list)
        self.trimmed_frame_list = new_list
        i_pnl.set_img_box()

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

    def limit_to_date(self, cap_list):
        lim_num = self.time_lim_tc.GetValue()
        lim_txt = self.time_lim_cb.GetValue()
        if lim_txt == "all":
            return cap_list
        if lim_num == "":
            lim_num = 1
            self.time_lim_tc.SetValue("1")

        try:
            lim_num = int(lim_num)
        except:
            return cap_list

        # Set cutoff datetime
        if lim_txt == "days":
            datecheck = datetime.timedelta(days=lim_num)
        elif lim_txt == "hours":
            datecheck=datetime.timedelta(hours=lim_num)
        elif lim_txt == "weeks":
            datecheck=datetime.timedelta(weeks=lim_num)
        elif lim_txt == "months":
            datecheck=datetime.timedelta(weeks=lim_num*4)
        else:
            print(" !!!! Error in trim list by date checkbox, unknown value selected")
            return cap_list
        start_point_cutoff = datetime.datetime.now() - datecheck
        print("Cut off time for animation set to -", start_point_cutoff)

        # trim list to after start point
        i_pnl = self.parent.dict_I_pnl['timelapse_pnl']
        list_trimmed_by_startpoint = []
        for item in cap_list:
            filename, pic_time = i_pnl.date_from_filename(item)
            if pic_time >= start_point_cutoff:
                list_trimmed_by_startpoint.append(item)

        #print("date trimmed list; list now " + str(len(list_trimmed_by_startpoint)) + " frames long")
        return list_trimmed_by_startpoint

    def limit_to_size(self, cap_list):
        min_size = self.min_size_tc.GetValue()
        try:
            min_size = int(min_size)
        except:
            if not min_size == "":
                print("Frame selection - Min Size value must be a number")
            return cap_list

        newly_trimmed_list = []
        for file in cap_list:
            filesize = os.path.getsize(file)
            if filesize > int(min_size):
                newly_trimmed_list.append(file)
        #print("Timelapse min filesize trimmed list to:", len(newly_trimmed_list))
        return newly_trimmed_list

    # video options

    def audio_click(self, e):
        audiofile = self.select_audiofile()
        if not audiofile == "none":
            self.audio_tc.SetValue(audiofile)

    def select_audiofile(self):
        audio_formats = "*.mp3;*.ogg;*.aac;*.flac;*.wav"
        wildcard = f"Audio files ({audio_formats})|{audio_formats}|All files (*.*)|*.*"

        local_path = self.parent.shared_data.frompi_path
        if local_path == "":
            local_path = self.parent.shared_data.frompi_base_path

        openFileDialog = wx.FileDialog(self, "Select audio file", "", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select the audio file for the video")

        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        outfile = openFileDialog.GetPath()
        return outfile


    # renderer

    def set_outfile_click(self, e):
        outfile = self.select_outfile()
        if not outfile == "none":
            self.outfile_tc.SetValue(outfile)

    def select_outfile(self):
        wildcard = "Video files (*.mp4;*.avi;*.mkv;*.flv;*.mov;*.webm)|*.mp4;*.avi;*.mkv;*.flv;*.mov;*.webm|All files (*.*)|*.*"
        local_path = self.parent.shared_data.frompi_path
        if local_path == "":
            local_path = self.parent.shared_data.frompi_base_path
        default_path = os.path.join(local_path, "timelapse.mp4")
        openFileDialog = wx.FileDialog(self, "Select output file", "", default_path, wildcard, wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        openFileDialog.SetMessage("Select the outfile for the video file")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        outfile = openFileDialog.GetPath()
        return outfile

    def render_click(self, e):
        if self.calc_cb.GetValue() == True:
            self.calc_frames_click

        fps = self.fps_tc.GetValue()
        outfile = self.outfile_tc.GetValue()
        audiofile = self.audio_tc.GetValue()

        listfile, frame_count = self.make_frame_list()
        print("Created", listfile)

        extra_commands = ""
        if not audiofile == "":
            #frame_count = len(self.trimmed_frame_list) + freeze_num
            extra_commands += " --audiofile=\"" + audiofile + "\" --frames=" + str(frame_count)

        print (" Making timelapse video...")
        cmd = "mpv mf://@"+listfile+" --mf-fps="+str(fps)
        cmd += " -o "+outfile+" " + extra_commands

        print(" Running - " + cmd)
        os.system(cmd)
        print(" --- "+ outfile +" Done ---")

    def make_frame_list(self, credit_style=""):
        ''' write text file with a list of frames to use '''
        credit_style = self.credits_cb.GetValue()
        credit_num = int(self.credit_num_cb.GetValue())
        fps = self.fps_tc.GetValue()
        local_path = self.parent.shared_data.frompi_path
        if local_path == "":
            local_path = self.parent.shared_data.frompi_base_path

        temp_folder = os.path.join(local_path, "temp")
        if not os.path.isdir(temp_folder):
            os.makedirs(temp_folder)

        frame_count = 0
        listfile = os.path.join(temp_folder, "frame_list.txt")
        frame_list_text_file = open(listfile, "w")
        for cap_file in self.trimmed_frame_list:
            frame_list_text_file.write(cap_file + "\n")
            frame_count += 1

        # credits
        if credit_style == "freeze":
            freeze_num = int(fps) * int(credit_num)
            for x in range(0, freeze_num):
                frame_list_text_file.write(self.trimmed_frame_list[-1] + "\n")
                frame_count += 1
        elif not credit_style == "none":
            credits_path_list = self.make_credits_from_module(credit_style, credit_num, self.trimmed_frame_list, fps, temp_folder)
            for frame_path in credits_path_list:
                frame_list_text_file.write(frame_path + "\n")
                frame_count += 1

        frame_list_text_file.close()

        return listfile, frame_count

    def make_credits_from_module(self, credit_style, credit_num, ani_frame_list, fps, temp_folder):
        #credit_style, credit_num, self.trimmed_frame_list, fps, temp_folder
        module_name = "credits_" + credit_style
        self.import_module(module_name, "credits_tool")
        credits_path_list = credits_tool.make_credits(credit_num, ani_frame_list, fps, temp_folder)
        return credits_path_list

    def play_click(self, e):
        outfile = self.outfile_tc.GetValue()
        if not os.path.isfile(outfile):
            print("File ", outfile, "not found.")
            return None
        cmd = "mpv " + outfile
        os.system(cmd)

    # overlay

    def log_overlay_click(self, e):
        print("LOG OVERLAY DOES NOT EXIST YET")

    def imgset_overlay_click(self, e):
        if len(self.trimmed_frame_list) > 0:
            self.imgset_dbox = imgset_overlay_dialog(self, self.parent)
            self.imgset_dbox.ShowModal()
            if self.imgset_dbox:
                if not self.imgset_dbox.IsBeingDeleted():
                    self.imgset_dbox.Destroy()
        else:
            print("Image set has zero length, can't overlay on nothing")

    def stylized_click(self, e):
        if len(self.trimmed_frame_list) > 0:
            self.style_dbox = stylized_dialog(self, self.parent)
            self.style_dbox.ShowModal()
            if self.style_dbox:
                if not self.style_dbox.IsBeingDeleted():
                    self.style_dbox.Destroy()
        else:
            print("Image set has zero length, can't overlay on nothing")

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
            self.Bind(wx.EVT_SIZE, self.on_size)
            # Tab Title
            self.SetFont(self.shared_data.title_font)
            title_l = wx.StaticText(self,  label='Timelapse')
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

        def on_size(self, e):
            new_size = self.GetSize()
            self.pic_size = int((new_size[0] / 2))

            f_frame = self.first_frame_no.GetValue()
            try:
                f_frame = int(f_frame)
                self.set_first_image(f_frame, resize=True)
            except:
                pass

            l_frame = self.last_frame_no.GetValue()
            try:
                l_frame = int(l_frame)
                self.set_last_image(l_frame, resize=True)
            except:
                pass

            e.Skip()  # Allow the event to propagate

        def make_graph_sizer(self):
            self.SetFont(self.shared_data.sub_title_font)
            graph_l = wx.StaticText(self,  label='Image Set Analyse')

            analyse_opts = self.get_analyse_opts()
            self.analyse_cb = wx.ComboBox(self, choices = analyse_opts)
            self.analyse_cb.SetValue(analyse_opts[0])
            do_analyse_btn = wx.Button(self, label='Go')
            do_analyse_btn.Bind(wx.EVT_BUTTON, self.do_analyse_click)

            analyse_select_sizer = wx.BoxSizer(wx.HORIZONTAL)
            analyse_select_sizer.Add(self.analyse_cb, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 5)
            analyse_select_sizer.Add(do_analyse_btn, 0, wx.ALL |  wx.ALIGN_CENTER_VERTICAL, 5)

            graph_sizer = wx.BoxSizer(wx.VERTICAL)
            graph_sizer.Add(graph_l, 0, wx.ALL |  wx.ALIGN_CENTER_HORIZONTAL, 5)
            graph_sizer.Add(analyse_select_sizer, 0, wx.ALL |  wx.ALIGN_CENTER_HORIZONTAL, 5)
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
            # frame count
            frame_count_l = wx.StaticText(self,  label='Frame Count  ')
            self.SetFont(self.shared_data.info_font)
            self.frame_count_t = wx.StaticText(self,  label='')
            # duration
            self.SetFont(self.shared_data.item_title_font)
            duration_l = wx.StaticText(self,  label='Duration  ')
            self.SetFont(self.shared_data.info_font)
            self.duration_t = wx.StaticText(self,  label='')
            # time period
            self.SetFont(self.shared_data.item_title_font)
            period_l = wx.StaticText(self,  label='Time period  ')
            self.SetFont(self.shared_data.info_font)
            self.period_t = wx.StaticText(self,  label='')
            # ave interval
            self.SetFont(self.shared_data.item_title_font)
            interval_l = wx.StaticText(self,  label='Ave Interval  ')
            self.SetFont(self.shared_data.info_font)
            self.interval_t = wx.StaticText(self,  label='')
            # speed factor
            self.SetFont(self.shared_data.item_title_font)
            speed_l = wx.StaticText(self,  label='Speed X  ')
            self.SetFont(self.shared_data.info_font)
            self.speed_t = wx.StaticText(self,  label='')

            ani_panel_sizer = wx.GridSizer(5, 2, 2, 2)
            ani_panel_sizer.AddMany([(frame_count_l, 0, wx.ALL),
                (self.frame_count_t, 0, wx.EXPAND),
                (duration_l, 0, wx.ALL),
                (self.duration_t, 0, wx.EXPAND),
                (period_l, 0, wx.ALL),
                (self.period_t, 0, wx.EXPAND),
                (interval_l, 0, wx.ALL),
                (self.interval_t, 0, wx.EXPAND),
                (speed_l, 0, wx.ALL),
                (self.speed_t, 0, wx.EXPAND),])

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

        # graph sizer

        def get_analyse_opts(self):
            analyse_opts = self.parent.shared_data.get_module_options("analyse_", "timelapse_modules")

            return analyse_opts

        def do_analyse_click(self, e):
            module_opt = self.analyse_cb.GetValue()
            if module_opt == "" or module_opt == "none":
                return None

            local_path = self.parent.shared_data.frompi_path
            if local_path == "":
                local_path = self.parent.shared_data.frompi_base_path

            temp_folder = os.path.join(local_path, "temp")
            if not os.path.isdir(temp_folder):
                os.makedirs(temp_folder)

            ani_frame_list = self.c_pnl.trimmed_frame_list

            module_name = "analyse_" + module_opt
            self.c_pnl.import_module(module_name, "analyse_tool")
            analysis_img_path = analyse_tool.analyse_set(ani_frame_list, temp_folder)
            print("analysis output;", analysis_img_path)
            return analysis_img_path

        # info box controls
        def set_img_box(self):
            # image set info
            set_count = len(self.c_pnl.cap_file_paths)
            self.set_count_t.SetLabel(str(set_count))

            # ani info
            trimmed_count = len(self.c_pnl.trimmed_frame_list)
            credit_style = self.c_pnl.credits_cb.GetValue()
            fps = self.c_pnl.fps_tc.GetValue()
            try:
                fps = int(fps)
            except:
                print("FPS not set, can't calcuate video length")
                credit_style = ""
                fps = 0

            # add credit length to duration

            credit_style = self.c_pnl.credits_cb.GetValue()
            if credit_style == "none" or credit_style == "":
                credit_num = 0
            else:
                credit_num = self.c_pnl.credit_num_cb.GetValue()
                try:
                    credit_num = int(credit_num)
                except:
                    credit_num = 0

            credit_frame_count = (fps * credit_num)
            full_frame_count = trimmed_count + credit_frame_count

            # set duration label
            if full_frame_count == 0 or fps == 0:
                ani_length_sec = 0
            else:
                ani_length_sec = full_frame_count / fps
            duration = str(datetime.timedelta(seconds=ani_length_sec))
            if "." in duration:
                duration = duration.split(".")[0]
            self.duration_t.SetLabel(duration)

            # set frame count
            frame_count_str = str(trimmed_count)
            if credit_frame_count > 0:
                frame_count_str += "  +" + str(credit_frame_count)
            self.frame_count_t.SetLabel(frame_count_str)

            # set time period of trimmed caps
            if len(self.c_pnl.trimmed_frame_list) > 1:
                f_image_path = self.c_pnl.trimmed_frame_list[0]
                f_filename, f_date = self.date_from_filename(f_image_path)

                l_image_path = self.c_pnl.trimmed_frame_list[-1]
                l_filename, l_date = self.date_from_filename(l_image_path)

                if not l_date == 'undetermined' and not f_date == 'undetermined':
                    period_d = l_date - f_date
                    period = str(period_d)
                else:
                    period = 'undetermined'
                if "." in period:
                    period = period.split(".")[0]
            else:
                period = "0"

            self.period_t.SetLabel(str(period))

            # average Interval lengh
            if len(self.c_pnl.trimmed_frame_list) > 1:
                t_period = l_date - f_date
                t_per = t_period.total_seconds() / trimmed_count
                t_per = str(datetime.timedelta(seconds=t_per))
                if "." in t_per:
                    duration = t_per.split(".")[0]

                # playback rate
                if trimmed_count == 0 or fps == 0:
                    trim_length_sec = 0
                else:
                    trim_length_sec = trimmed_count / fps
                real_capture_seconds     = period_d.total_seconds()
                playback_outfile_seconds = trim_length_sec
                playback_rate = round(real_capture_seconds / playback_outfile_seconds, 3)
            else:
                playback_rate = "0"
                t_per = "0"

            self.interval_t.SetLabel(t_per)
            self.speed_t.SetLabel(str(playback_rate))

            # refresh layout
            self.Layout()

        # first image box controls
        def set_first_image(self, frame, resize=False):
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

            if resize == True:
                self.first_image.SetMinSize(first.GetSize())
                self.first_image.Layout()

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

            self.c_pnl.list_val_changed()

        def first_next_click(self, e):
            number = int(self.first_frame_no.GetValue())
            total_images = len(self.c_pnl.cap_file_paths) - 1
            if number < total_images:
                number = number + 1
            self.first_frame_no.SetValue(str(number))

            self.c_pnl.list_val_changed()

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

            self.c_pnl.list_val_changed()

        # last image box controls
        def set_last_image(self, frame, resize=False):
            image_path = self.c_pnl.cap_file_paths[frame]
            filename, date = self.date_from_filename(image_path)
            image_title = filename + "\n" + date.strftime('%Y-%m-%d %H:%M:%S')
            self.last_img_l.SetLabel(image_title)

            try:
                self.last_ani_pic = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
                last = self.shared_data.scale_pic(self.last_ani_pic, self.pic_size)
                last = last.ConvertToBitmap()
                self.last_image.SetBitmap(last)
            except:
                print("!! Last frame didn't work for timelapse tab.", filename)

            if resize == True:
                self.last_image.SetMinSize(last.GetSize())
                self.last_image.Layout()

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

            self.c_pnl.list_val_changed()

        def last_next_click(self, e):
            try:
                number = int(self.last_frame_no.GetValue())
            except:
                return None
            total_images = len(self.c_pnl.cap_file_paths) - 1
            if number < total_images:
                number = number + 1
            self.last_frame_no.SetValue(str(number))

            self.c_pnl.list_val_changed()

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

            self.c_pnl.list_val_changed()

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

class stylized_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(stylized_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((600, 400))
        self.SetTitle("Create Stylized Set")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        # draw the pannel
        self.SetFont(self.parent.parent.shared_data.title_font)
        title = wx.StaticText(self,  label='Create Stylized Image Set')
        self.SetFont(self.parent.parent.shared_data.sub_title_font)
        sub_msg = "This will create a new image set\nby modifying the selected images"
        sub_label = wx.StaticText(self,  label=sub_msg)

        # module select
        self.SetFont(self.parent.parent.shared_data.item_title_font)
        self.module_l = wx.StaticText(self,  label='Stylizer Module')
        module_opts = self.get_module_opts()
        self.module_cb = wx.ComboBox(self, choices = module_opts)
        self.module_cb.SetValue(module_opts[0])
        module_sizer = wx.BoxSizer(wx.HORIZONTAL)
        module_sizer.Add(self.module_l, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        module_sizer.Add(self.module_cb, 2, wx.EXPAND, 2)

        # out folder select
        self.outfolder_l = wx.StaticText(self,  label='Output folder')
        default_path = os.path.join(self.parent.parent.shared_data.frompi_base_path, "newset/")
        self.outfolder_tc = wx.TextCtrl(self)
        self.outfolder_tc.SetValue(default_path)
        self.set_outfolder_btn = wx.Button(self, label='...', size=(35,29))
        self.set_outfolder_btn.Bind(wx.EVT_BUTTON, self.set_outfolder_click)
        outfolder_sizer = wx.BoxSizer(wx.HORIZONTAL)
        outfolder_sizer.Add(self.outfolder_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        outfolder_sizer.Add(self.outfolder_tc, 40, wx.EXPAND, 2)
        outfolder_sizer.Add(self.set_outfolder_btn, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)

        # set name
        self.setname_l = wx.StaticText(self,  label='img set name  ')
        self.setname_tc = wx.TextCtrl(self)
        self.setname_tc.SetValue('stylized')
        setname_sizer = wx.BoxSizer(wx.HORIZONTAL)
        setname_sizer.Add(self.setname_l, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2)
        setname_sizer.Add(self.setname_tc, 40, wx.EXPAND, 2)

        # message while creating files
        self.create_l = wx.StaticText(self,  label='Creating Image Set in Progress...\nThis may take some time, please wait')
        self.create_l.Hide()

        #buttons
        self.go_btn = wx.Button(self, label='Create') #, size=(175, 50))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Cancel') #, size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.go_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.Add(sub_label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(self.create_l, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 6)
        self.main_sizer.Add(module_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 6)
        self.main_sizer.Add(outfolder_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 6)
        self.main_sizer.Add(setname_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 6)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)

    def get_module_opts(self):
        module_opts = self.parent.parent.shared_data.get_module_options("stylize_", "timelapse_modules")
        return module_opts

    def set_outfolder_click(self, e):
        outfolder = self.select_image_folder()
        if not outfolder == "none":
            self.outfolder_tc.SetValue(outfolder)

    def select_image_folder(self):
        default_folder = self.parent.parent.shared_data.frompi_path
        if default_folder == "":
            default_folder = self.parent.parent.shared_data.frompi_base_path

        dirDialog = wx.DirDialog(self, "Select image folder", defaultPath=default_folder, style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)

        if dirDialog.ShowModal() == wx.ID_CANCEL:
            dirDialog.Destroy()
            return 'none'

        selected_folder = dirDialog.GetPath()
        dirDialog.Destroy()
        return selected_folder

    def go_click(self, e):
        module_name = self.module_cb.GetValue()
        module_name = "stylize_" + module_name
        try:
            self.parent.import_module(module_name, "stylize_tool")
        except Exception as e:
            print("Failed to import module", module_name, "because", e)
            return None

        ani_frame_list = self.parent.trimmed_frame_list
        out_folder = self.outfolder_tc.GetValue()

        if not os.path.exists(out_folder):
            try:
                os.makedirs(out_folder)
                print(f"Folder '{out_folder}' not found, created.")
            except OSError as e:
                print(f"Error creating folder '{out_folder}': {e}")
                return None

        set_name = self.setname_tc.GetValue()
        if set_name == "":
            return None
        set_name = re.sub(r'\W+', '', set_name)
        set_name = set_name.replace("_", "")

        self.outfolder_l.Hide()
        self.outfolder_tc.Hide()
        self.set_outfolder_btn.Hide()
        self.module_l.Hide()
        self.module_cb.Hide()
        self.setname_l.Hide()
        self.setname_tc.Hide()
        self.go_btn.Hide()
        self.cancel_btn.SetLabel("Run In Background")
        self.create_l.Show()
        self.Layout()

        file_name, file_extension = os.path.splitext(ani_frame_list[0])
        delayedresult.startWorker(stylize_class._on_result,
                            self._run_stylize_set,
                            wargs=(ani_frame_list, out_folder, set_name, file_extension),
                            jobID=0)


    def _run_stylize_set(self, ani_frame_list, out_folder, set_name, img_type):
        stylize_output, out_folder, set_name, img_type = stylize_tool.stylize_set(ani_frame_list, out_folder, set_name, img_type)
        print(stylize_output)
        return [stylize_output, out_folder, set_name, img_type, self]

    def _on_cancel(self):
        print("CAAANNCCCEELLL REQUEST !!!!!!!!!!!!!!!!!!!!!!!!!!(does nothing)!!!!!!!!!!!!!!!!!!!!!!!!!")

    def OnClose(self, e):
        self.Destroy()

class stylize_class:

    def _on_result(result):
        '''Triggers once the stylized output tool is done'''
        output, out_folder, set_name, img_type, dlbox = result.get()

        set_o_name = set_name + "_<DATE>." + img_type
        set_o_name = os.path.join(out_folder, set_o_name)

        dlog_msg = "Image set creation completed\n\n" + str(set_o_name)
        dlog_msg += "\n\nDo you want to switch to the new set?"
        confirm_dialog = wx.MessageDialog(None, dlog_msg, "Confirmation", wx.YES_NO | wx.ICON_QUESTION)
        if confirm_dialog.ShowModal() == wx.ID_YES:
            c_pnl = dlbox.parent.parent.dict_C_pnl['timelapse_pnl']
            c_pnl.open_caps_folder(out_folder, img_type, set_name)
        confirm_dialog.Destroy()

        if dlbox:
            if not dlbox.IsBeingDeleted():
                dlbox.Destroy()

class imgset_overlay_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(imgset_overlay_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((800, 850))
        self.SetTitle("Create Stylized Set")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        self.image_list = self.parent.trimmed_frame_list
        self.ref_overlay_image = None
        self.overlay_img_set = []
        # draw the pannel
        self.SetFont(self.parent.parent.shared_data.title_font)
        title = wx.StaticText(self,  label='Overlay Image Set')
        self.SetFont(self.parent.parent.shared_data.sub_title_font)
        sub_msg = "This will create a new picture in picture image set"
        sub_msg += "\nOverlay graphs, dials, or other camera views."
        sub_msg += "\nAdded set will be synced using filename timestamps."
        sub_label = wx.StaticText(self,  label=sub_msg, style=wx.ALIGN_CENTRE_HORIZONTAL)

        # log select
        self.SetFont(self.parent.parent.shared_data.item_title_font)
        self.imgset_btn = wx.Button(self, label='Select Image Set')
        self.imgset_btn.Bind(wx.EVT_BUTTON, self.imgset_click)
        self.SetFont(self.parent.parent.shared_data.info_font)
        self.imgset_l = wx.StaticText(self,  label='none')
        imgset_sizer = wx.BoxSizer(wx.HORIZONTAL)
        imgset_sizer.Add(self.imgset_btn, 0,  wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 7)
        imgset_sizer.Add(self.imgset_l, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)

        # placement
        self.SetFont(self.parent.parent.shared_data.item_title_font)
        pos_x_l = wx.StaticText(self,  label='X')
        pos_y_l = wx.StaticText(self,  label='Y')
        self.SetFont(self.parent.parent.shared_data.button_font)
        self.setpos_btn = wx.Button(self, label='Set Position')
        self.setpos_btn.Bind(wx.EVT_BUTTON, self.setpos_click)
        self.SetFont(self.parent.parent.shared_data.info_font)
        self.pos_x_tc = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.pos_x_tc.Bind(wx.EVT_TEXT_ENTER, self.ref_frame_tc_enter)
        self.pos_x_tc.SetValue('10')
        self.pos_y_tc = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.pos_y_tc.Bind(wx.EVT_TEXT_ENTER, self.ref_frame_tc_enter)
        self.pos_y_tc.SetValue('10')
        setpos_sizer = wx.BoxSizer(wx.HORIZONTAL)
        setpos_sizer.Add(self.setpos_btn, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        setpos_sizer.Add(pos_x_l, 0,  wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 7)
        setpos_sizer.Add(self.pos_x_tc, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        setpos_sizer.Add(pos_y_l, 0,  wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 7)
        setpos_sizer.Add(self.pos_y_tc, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)

        # scale & opacity
        self.SetFont(self.parent.parent.shared_data.item_title_font)
        scale_l = wx.StaticText(self,  label='Scale %')
        opacity_l = wx.StaticText(self,  label='Opacity %')
        self.SetFont(self.parent.parent.shared_data.info_font)
        self.scale_tc = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.scale_tc.SetValue('100')
        self.scale_tc.Bind(wx.EVT_TEXT_ENTER, self.ref_frame_tc_enter)
        self.opacity_tc = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.opacity_tc.SetValue('100')
        self.opacity_tc.Bind(wx.EVT_TEXT_ENTER, self.ref_frame_tc_enter)
        scale_opacity_sizer = wx.BoxSizer(wx.HORIZONTAL)
        scale_opacity_sizer.Add(scale_l, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        scale_opacity_sizer.Add(self.scale_tc, 0,  wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 3)
        scale_opacity_sizer.Add(opacity_l, 0,  wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 15)
        scale_opacity_sizer.Add(self.opacity_tc, 0,  wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)

        # chromakey - select colour and tollerance to turn that color transparent

        # scaled img display
        #representative frame number (sets reference image, not used in calculations)
        self.current_image_index = 0
        ref_background_image = self.image_list[0]
        self.preview_panel = PreviewPanel(self, ref_background_image, self.ref_overlay_image)

        self.ref_frame_tc = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.ref_frame_tc.SetValue(str(self.current_image_index))
        self.ref_frame_tc.Bind(wx.EVT_TEXT_ENTER, self.ref_frame_tc_enter)

        image_box_sizer = wx.BoxSizer(wx.VERTICAL)
        image_box_sizer.Add(self.preview_panel, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        image_box_sizer.Add(self.ref_frame_tc, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        #buttons
        self.go_btn = wx.Button(self, label='Create') #, size=(175, 50))
        self.go_btn.Bind(wx.EVT_BUTTON, self.go_click)
        self.cancel_btn = wx.Button(self, label='Cancel') #, size=(175, 50))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.go_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        # main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 2)
        self.main_sizer.Add(sub_label, 0, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 4)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(imgset_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.Add(setpos_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.Add(scale_opacity_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.main_sizer.Add(image_box_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL |wx.ALL, 5)
        self.main_sizer.AddStretchSpacer(1)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(self.main_sizer)


    def go_click(self, e):
        print("GO!!!!!!!!!!!!!!!!!!!! (thats all you get for pressing go)")
        # get control values
        pos_x = int(self.pos_x_tc.GetValue())
        pos_y = int(self.pos_y_tc.GetValue())
        try:
            scale = float(self.scale_tc.GetValue()) / 100.0
            opacity = float(self.opacity_tc.GetValue()) / 100.0
        except:
            print("Timelapse Img Overlay - Scale and Opacity must be numbers")
            return None
        #


    def imgset_click(self, e):
        # select folder
        wildcard = "JPG and PNG files (*.jpg;*.png)|*.jpg;*.png|GIF files (*.gif)|*.gif"
        defdir = self.parent.parent.shared_data.frompi_path
        if defdir == "":
            defdir = self.parent.parent.shared_data.frompi_base_path
        openFileDialog = wx.FileDialog(self, "Select image set", defaultDir=defdir, wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the set you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()

        #
        cap_dir = os.path.split(new_cap_path)
        cap_set = cap_dir[1].split("_")[0]  # Used to select set if more than one are present
        cap_type = cap_dir[1].split('.')[1]
        cap_dir = cap_dir[0]
        print(" Selected " + cap_dir + " with capset; " + cap_set + " filetype; " + cap_type)
        self.open_imgset(cap_dir, cap_type, cap_set)

        imgset_str = os.path.basename(cap_dir) + "/" + cap_set + "_..."
        self.imgset_l.SetLabel(imgset_str)
        self.ref_frame_tc_enter()

    def open_imgset(self, cap_dir, cap_type="jpg", cap_set=None):
        self.overlay_img_set = []
        for filefound in os.listdir(cap_dir):
            if filefound.endswith(cap_type):
                file_path = os.path.join(cap_dir, filefound)
                if not cap_set == None:
                    if filefound.split("_")[0] == cap_set:
                        self.overlay_img_set.append(file_path)
                else: #when using all images in the folder regardless of the set
                    self.overlay_img_set.append(file_path)
        self.overlay_img_set.sort()
        if not len(self.overlay_img_set) > 0:
            print("No images found in ", cap_dir)
        else:
            print("Found; ", len(self.overlay_img_set), " image files, starting at ", self.overlay_img_set[0])

        self.ref_overlay_image = self.overlay_img_set[0]


    def setpos_click(self, e):
        print("no one is setting the position of the text for you lol")

    def OnClose(self, e):
        self.Destroy()


    def ref_frame_tc_enter(self, event=None):
        try:
            index = int(self.ref_frame_tc.GetValue())
            if 0 <= index < len(self.image_list):
                self.current_image_index = index
                self.update_image_display()
        except ValueError:
            pass

    def update_image_display(self):
        ref_background_image = self.image_list[self.current_image_index]
        #ref_overlay_image = self.parent.ref_overlay_image

        self.preview_panel.update_preview(ref_background_image, self.ref_overlay_image)


class PreviewPanel(wx.Panel):
    def __init__(self, parent, ref_background_image, ref_overlay_image):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.SetMinSize(wx.Size(790, 400))  # Set a minimum size
        self.ref_background_image = wx.Image(ref_background_image, wx.BITMAP_TYPE_ANY)
        self.ref_overlay_image = ref_overlay_image
        self.static_bitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap())
        self.Bind(wx.EVT_PAINT, self.on_paint)

        # Schedule the initial update after the layout is complete
        wx.CallAfter(self.update_preview, ref_background_image, ref_overlay_image)


    def update_preview(self, ref_background_image, ref_overlay_image):
        #print(ref_background_image, ref_overlay_image)
        if ref_overlay_image is None:
            bg_image = wx.Image(ref_background_image, wx.BITMAP_TYPE_ANY)
            self.draw_scaled_image(bg_image)
        else:
            # Draw the overlay on top of the background image
            pos_x = int(self.parent.pos_x_tc.GetValue())
            pos_y = int(self.parent.pos_y_tc.GetValue())
            try:
                scale = float(self.parent.scale_tc.GetValue()) / 100.0  # Convert to a scale factor (0-1)
                opacity = float(self.parent.opacity_tc.GetValue()) / 100.0  # Convert to an opacity factor (0-1)
            except:
                print("Timelapse Img Overlay - Scale and Opacity must be numbers")
                return None

            # Load images
            bg_img = Image.open(ref_background_image).convert("RGBA")
            overlay_image = Image.open(ref_overlay_image).convert("RGBA")

            # Resize overlay image
            overlay_image = overlay_image.resize(
                (int(overlay_image.width * scale), int(overlay_image.height * scale)))
            # set transparency
            overlay_image.putalpha(int(opacity * 255))
            # overlay onto background
            bg_img.alpha_composite(overlay_image, (pos_x, pos_y))

            # convert to wx image
            result_wx = wx.Bitmap.FromBufferRGBA(bg_img.width, bg_img.height, bg_img.tobytes())
            result_wx = result_wx.ConvertToImage()
            # display to screen
            self.draw_scaled_image(result_wx)

    def on_paint(self, event):
        pass  # No need for painting, as the image is drawn using wx.StaticBitmap

    def draw_scaled_image(self, bg_img):
        # Determine the maximum available screen space
        #max_width, max_height = wx.GetDisplaySize()

        # Assuming self.GetParent() returns the parent panel
        #max_width, max_height = self.GetParent()
        max_width, max_height = self.GetSize()

        # Get the aspect ratio of the original image
        aspect_ratio = bg_img.GetWidth() / bg_img.GetHeight()

        # Calculate the maximum size that fits the screen, maintaining the aspect ratio
        new_width = min(bg_img.GetWidth(), max_width)
        new_height = int(new_width / aspect_ratio)

        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)

        # Resize the image
        resized_image = bg_img.Scale(new_width, new_height, wx.IMAGE_QUALITY_HIGH)

        # Set the resized image to the StaticBitmap
        self.static_bitmap.SetBitmap(wx.Bitmap(resized_image))
        #self.static_bitmap

        # Resize the panel to match the resized image
        self.SetSize((new_width, new_height))

            # Get the parent sizer
        parent_sizer = self.GetContainingSizer()

        # Update the size and layout of the parent sizer
        if parent_sizer:
            parent_sizer.SetItemMinSize(self, (new_width, new_height))
            parent_sizer.Layout()
