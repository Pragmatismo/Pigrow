import wx

import wx.lib.newevent
try:
    import cv2
    use_cv2 = True
except:
    print("Not using opencv as it's not installed.")
    use_cv2 = False
import numpy as np
ROIChangedEvent, EVT_ROI_CHANGED = wx.lib.newevent.NewEvent()

class rpicap_sets_pnl(wx.Panel):

    def __init__(self, parent):
        shared_data = parent.parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        label = wx.StaticText(self,  label='Rpi cam Settings')
        label.SetFont(shared_data.button_font)

        #self.getset_btn = wx.Button(self, label='Get Settings')
        #self.getset_btn.Bind(wx.EVT_BUTTON, self.getset_click)
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_empty_settings_sizer()
        self.refresh_settings_sizer()

        # tool buttons
        set_afroi_butt = wx.Button(self, label='Set AutoFocus\nRegion')
        set_afroi_butt.Bind(wx.EVT_BUTTON, self.set_afroi_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 7)
        #main_sizer.Add(self.getset_btn, 0, wx.ALL, 0)
        main_sizer.Add(set_afroi_butt, 0, wx.ALL, 0)
        main_sizer.Add(self.c_sets_sizer, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(main_sizer)

    def set_afroi_click(self, e):
        print("Setting Autofocus Region of Interest")
        setting_name = "autofocus-window"

        if setting_name in self.setting_crtl_dict:
            initial_roi = self.setting_crtl_dict[setting_name].GetValue()
            x,y,w,h = initial_roi.split(",")
            initial_roi = float(x), float(y), float(w), float(h)
        else:
            wx.MessageBox("Error - autofocus-range not in options, can't set it", "Error", wx.OK | wx.ICON_ERROR)


        image_path = "./test.jpg"

        dialog = SetAFROIDialog(None, image_path, initial_roi)
        result = dialog.ShowModal()

        if result == wx.ID_OK:
            # If the user clicked OK, retrieve the ROI information
            new_roi = dialog.get_roi()
            if setting_name in self.setting_crtl_dict:
                self.setting_crtl_dict[setting_name].SetValue(new_roi)
            print(f"Final ROI coordinates: {new_roi}")
        else:
            # Handle case where user clicked Cancel or closed the dialog
            new_roi = None

        dialog.Destroy()

    # def getset_click(self, e):
    #     #print("Getting settings from Raspberry Pi")
    #     self.refresh_settings_sizer()

    def make_control_dict(self):
        # -t [ --timeout ] arg (=5sec) -- Time for which program runs. If no units are provided default to ms.
        control_dict = {"brightness":[(-1.0, 1.0), 0.0],
                        "contrast":[(0.0, 32.0), 1.0],
                        "saturation":[(0.0, 32.0), 1.0],
                        "sharpness":[(0.0, 16.0), 1.0],
                        "hflip":[["True", "False"], "False"],
                        "vflip":[["True", "False"], "False"],
                        "roi":["0,0,1,1", "0,0,1,1", "X, Y, w, h - in decimal 0.0 to 1.0"],
                        "rotation":[(0, 180), 0],
                        "shutter":["0", "0", "sutter speed in microseconds"],
                        "gain":["0", "0"],
                        "ev":[(-10.0, 10.0), 0.0, "exposure value compensation of the image in stops"],

                        "exposure":[["normal",
                                     "sport"], "normal"],
                        "metering":[["centre",
                                     "spot",
                                     "average",
                                     "custom"], "centre"],
                         #"flicker-period":[(0, 50000), 0],
                         "awb":[["auto",
                                 "incandescent",
                                 "tungsten",
                                 "fluorescent",
                                 "indoor",
                                 "daylight",
                                 "cloudy",
                                 "custom"], "auto", "Auto White Balance"],
                        "awbgains":["0,0", "0,0", "explict red and blue white balance gains"],
                        "denoise":[["auto",
                                   "off",
                                   "cdn_off",
                                   "cdn_fast",
                                   "cdn_hq"], "auto"],
                        "autofocus-mode":[["manual",
                                           "auto",
                                           "continuous"], "auto"],
                        "autofocus-range":[["normal",
                                            "macro",
                                            "full"], "normal"],
                        "autofocus-speed":[["normal",
                                            "fast"], "normal"],
                        "autofocus-window":["0.33,0.33,0.33,0.33", "0.33,0.33,0.33,0.33", "X, Y, w, h - in decimal 0.0 to 1.0"],
                        "lens-position":[(0.0, 32.0), 0.0],
                        "hdr":[["off",
                               "auto",
                               "sensor",
                               "single-exp"], "off"],
                        "encoding":[["jpg",
                                     "png",
                                     "bmp",
                                     "rgb",
                                     "yuv420"], "jpg"],
                        "raw":[["True", "False"], "False"],
                        "metadata":[["off",
                                    "each",
                                    "$path",
                                    "-"], "off"],
                        "tuning-file":["", "", "Path to camera tuning file"],
                        "post-process-file":["", "", "Path to file"]}

        return control_dict

    # def read_set_from_pi(self):
    #     pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
    #     cmd = pigrow_path + 'scripts/cron/picam2cap.py --settings'
    #     out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
    #     print("picam2 settings;")
    #     print(out)
    #     lines = out.splitlines()
    #     for line in lines:
    #         if "=" in line:
    #             name, vals = line.split("=")
    #             name = name.strip()
    #             vmin, vmax, vnow = vals.split("|")
    #
    #             try:
    #                 vnow = float(vnow)
    #                 vmin = float(vmin)
    #                 vmax = float(vmax)
    #                 settings_dict[name] = [vnow, (vmin, vmax)]
    #             except:
    #                 #print("didn't work with", line)
    #                 pass


    def refresh_settings_sizer(self):
        self.c_sets_sizer.Clear(delete_windows=True)
        settings_dict = self.make_control_dict()

        # Get Resolution and camera sensor settings
        #camera_res_v1 = ['1920x1080', '2592x1944', '1296x972', '1296x730', '640x480']
        #camera_res_v2 = ['1920x1080', '3280x2464', '1640x1232', '1640x922', '1280x720', '640x480']
        preset_res = ['4608x2592 "picam v3"',
                      '4056x3040 "picam HQ"',
                      '3280x2464 "picam v2"',
                      '3840x2160 "4K UHD"',
                      '2592x1944 "picam v1"',
                      '1920x1080 "Full HD (1080p)"',
                      '1280x720 "HD (720p)"',
                      '640x480 "VGA"',
                      '320x240 "QVGA"']
        #preset_res = limit_res_for_cam(preset_res)
        settings_dict = {**{"Resolution":[preset_res, preset_res[0]]}, **settings_dict}

        # read settings
        # currently not reading setting from pi

        # make ui elements and reference dicts
        setting_crtl_dict = {}
        setting_t_dict = {}
        for setting in settings_dict.keys():
            label, box, box_t = self.create_ui_element(setting, settings_dict[setting])
            if not label == None:
                self.setting_crtl_dict[setting] = box
                self.setting_t_dict[setting] = box_t
                self.c_sets_sizer.Add(label, 0, wx.TOP|wx.ALIGN_RIGHT, 2)
                self.c_sets_sizer.Add(box, 0, wx.TOP|wx.EXPAND, 2)
                self.c_sets_sizer.Add(box_t, 0, wx.TOP|wx.EXPAND, 2)

        self.parent.Layout()

    def create_ui_element(self, setting, vals):
        label     = wx.StaticText(self,  label=setting)
        # Use 3rd box for note about setting if provided.
        input_box_t = wx.StaticText(self,  label="")
        try:
            input_box_t.SetLabel(vals[2])
        except:
            pass

        # list boxes
        if isinstance(vals[0], list):
            input_box = wx.ComboBox(self, choices=vals[0])
            if isinstance(vals[1], int):
                input_box.SetSelection(vals[1])
            else:
                input_box.SetValue(vals[1])
        # For string based settings
        elif isinstance(vals[0], str):
            input_box = wx.TextCtrl(self, value=vals[1])
        # int numbers
        elif isinstance(vals[0], tuple) and isinstance(vals[1], int):
            min_val, max_val = vals[0]
            default_val = int(vals[1])
            #print(min_val, max_val, default_val)
            input_box_t = wx.TextCtrl(self, value=str(default_val), style=wx.TE_PROCESS_ENTER)
            input_box_t.SetLabel(setting)
            input_box_t.Bind(wx.EVT_TEXT_ENTER, self.slider_text_change)
            input_box = wx.Slider(self, id=wx.ID_ANY, value=default_val, minValue=int(min_val), maxValue=int(max_val))
            input_box.SetLabel(setting)
            input_box.Bind(wx.EVT_SLIDER, self.slider_move)
        # float numbers
        elif isinstance(vals[0], tuple) and isinstance(vals[1], float):
            min_val, max_val = vals[0]
            step = 0.1
            c_val = float(vals[1])
            #
            slider_v = int((c_val - min_val) / (max_val - min_val) * 100)
            slider_m = int((max_val - min_val) / (max_val - min_val) * 100)

            #
            input_box = wx.SpinCtrlDouble(self, value=str(c_val), min=min_val, max=max_val, inc=step)
            input_box.SetLabel(setting)
            self.Bind(wx.EVT_SPINCTRLDOUBLE, self.onSpinCtrl, input_box)

            input_box_t = wx.Slider(self, value=slider_v, minValue=0, maxValue=slider_m, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
            input_box_t.SetTickFreq(10)
            input_box_t.SetLabel(setting)
            self.Bind(wx.EVT_SLIDER, self.onSlider, input_box_t)
            #

        else:
            print (" Error - picam2_set create_ui_element - Not set up to undertand ", type(vals[1]), " as options type")
            input_box = wx.TextCtrl(self, value="")
        return label, input_box, input_box_t

    def create_empty_settings_sizer(self):
        note = wx.StaticText(self,  label='Press Get Settings')

        #c_settings_sizer = wx.BoxSizer(wx.VERTICAL)
        c_settings_sizer = wx.FlexGridSizer(3, 0, 5)
        c_settings_sizer.Add(note, 0, wx.ALL|wx.EXPAND, 3)

        setting_crtl_dict = {}
        setting_t_dict = {}
        return c_settings_sizer, setting_crtl_dict, setting_t_dict


    # int slider
    def slider_move(self, e):
        setting_name = e.GetEventObject().GetLabel()
        slider_val = e.GetEventObject().GetValue()
        self.setting_t_dict[setting_name].SetValue(str(slider_val))

    def slider_text_change(self, e):
        setting_name = e.GetEventObject().GetLabel()
        box_val = e.GetEventObject().GetValue()
        self.setting_crtl_dict[setting_name].SetValue(int(box_val))

    # float spin control
    def onSpinCtrl(self, event):
        spinCtrl = event.GetEventObject()
        setting_name = spinCtrl.GetLabel()
        spin_val = spinCtrl.GetValue()
        slider = self.setting_t_dict[setting_name]
        minValue = spinCtrl.GetMin()
        maxValue = spinCtrl.GetMax()
        slider.SetValue(int((spin_val - minValue) / (maxValue - minValue) * 100))

    def onSlider(self, event):
        slider = event.GetEventObject()
        setting_name = slider.GetLabel()
        slider_val = slider.GetValue()
        spinCtrl = self.setting_crtl_dict[setting_name]
        minValue = spinCtrl.GetMin()
        maxValue = spinCtrl.GetMax()
        spinCtrl.SetValue(float(minValue + (maxValue - minValue) * slider_val / 100))


    # config
    def make_conf_text(self, setting_dict):
        #print("handed settings_dict", setting_dict)
        set_for_txt_dict = {}
        for item in setting_dict.keys():
            #print(setting_dict[item])
            value = setting_dict[item].GetValue()
            if not value == "":
                set_for_txt_dict[item] = value

        # switch dict
        set_for_txt_dict = self.set_for_text(set_for_txt_dict)

        settings_text = ""
        for item in set_for_txt_dict.keys():
            value = str(set_for_txt_dict[item]).strip()
            settings_text += item.strip() + "=" + value + "\n"

        return settings_text

    def set_for_text(self, set_dict):
        '''alters settings to match expected format'''
        if "Resolution" in set_dict:
            res_text = self.setting_crtl_dict["Resolution"].GetValue()
            #print("res_text", res_text)
            if " " in res_text:
                set_dict["Resolution"] = res_text.split(" ")[0]
            else:
                set_dict["Resolution"] = res_text

        return set_dict


    def text_into_ui(self, set_text):
        cam_settings = set_text.splitlines()
        self.camera_settings_dict = {}
        for line in cam_settings:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos+1:]
                self.camera_settings_dict[key] = value
        # make changes for old keys
        csd = self.camera_settings_dict

        # put into ui items
        for key in csd.keys():
            if key in self.setting_crtl_dict:
                if type(self.setting_crtl_dict[key]) == wx._core.Slider:
                    self.setting_t_dict[key].SetValue(csd[key])
                    csd[key] = int(csd[key])

                self.setting_crtl_dict[key].SetValue(csd[key])

    # Image capture
    def take_image(self, settings_file, outpath):
        print(" Taking a picture using ", settings_file, outpath)
        pigrow_path = self.parent.parent.shared_data.remote_pigrow_path
        cmd = pigrow_path + 'scripts/cron/rpicap.py caps=' + outpath + ' set=' + settings_file
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        combined_output = (out + error).strip()
        print(out, error)
        # check for text output listing save location
        if "Saving image to:" in combined_output:
            path = combined_output.split("Saving image to:")[1].split("\n")[0].strip()
        else:
            path = "Error : Image path not given \n\n" + combined_output
        return path, combined_output

    def take_default(self, outpath):
        print(" Taking default image using rpicam-still ")
        metapath = outpath.split(".")[0] + ".json"
        print("saving metadata to", metapath)
        cam_cmd = "rpicam-still --nopreview --metadata " + metapath + " -o " + outpath
        out, error = self.parent.parent.link_pnl.run_on_pi(cam_cmd)
        return outpath, "rpicam-still", (out + error).strip()

class SetAFROIDialog(wx.Dialog):
    def __init__(self, parent, image_path, initial_roi=None):
        if use_cv2 == False:
            print("Unable to complete as cv2 is ot installed")
        self.image = cv2.imread(image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.image_height, self.image_width = self.image.shape[:2]
        display_size = wx.DisplaySize()

        # Determine initial dialog size based on the image size and screen size
        dialog_width = min(self.image_width + 20, display_size[0] - 100)
        dialog_height = min(self.image_height + 150, display_size[1] - 100)

        super(SetAFROIDialog, self).__init__(parent, title="Set ROI", size=(dialog_width, dialog_height))

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.header = wx.StaticText(self.panel, label="Drag to select a region")
        self.vbox.Add(self.header, 0, wx.ALL | wx.CENTER, 5)

        self.image_panel = wx.Panel(self.panel, size=(self.image_width, self.image_height))
        self.image_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.image_panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.image_panel.Bind(wx.EVT_MOTION, self.on_mouse_drag)
        self.image_panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.image_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.vbox.Add(self.image_panel, 1, wx.EXPAND | wx.ALL, 5)

        self.coord_sizer = wx.GridSizer(1, 8, 5, 5)
        self.coord_sizer.Add(wx.StaticText(self.panel, label="x:"))
        self.x_text = wx.TextCtrl(self.panel)
        self.coord_sizer.Add(self.x_text)
        self.coord_sizer.Add(wx.StaticText(self.panel, label="y:"))
        self.y_text = wx.TextCtrl(self.panel)
        self.coord_sizer.Add(self.y_text)
        self.coord_sizer.Add(wx.StaticText(self.panel, label="w:"))
        self.w_text = wx.TextCtrl(self.panel)
        self.coord_sizer.Add(self.w_text)
        self.coord_sizer.Add(wx.StaticText(self.panel, label="h:"))
        self.h_text = wx.TextCtrl(self.panel)
        self.coord_sizer.Add(self.h_text)

        self.vbox.Add(self.coord_sizer, 0, wx.ALL | wx.CENTER, 5)

        self.ok_button = wx.Button(self.panel, label="OK")
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_ok)
        self.vbox.Add(self.ok_button, 0, wx.ALL | wx.CENTER, 5)

        self.panel.SetSizer(self.vbox)

        self.start_pos = None
        self.end_pos = None
        self.bmp = wx.Bitmap.FromBuffer(self.image_width, self.image_height, self.image)
        self.resized_image = self.image
        self.resized_image_offset = (0, 0)

        # Set initial ROI
        if initial_roi is None:
            self.set_default_roi()
        else:
            self.set_roi(initial_roi)

    def get_roi(self):
        # This method should return the final ROI coordinates
        x = self.x_text.GetValue()
        y = self.y_text.GetValue()
        w = self.w_text.GetValue()
        h = self.h_text.GetValue()
        roi = f"{x},{y},{w},{h}"
        return roi

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self.image_panel)
        dc.Clear()
        dc.DrawBitmap(self.bmp, 0, 0)

        if self.start_pos and self.end_pos:
            dc.SetPen(wx.Pen(wx.Colour(255, 0, 0), 2))
            brush = wx.Brush(wx.Colour(255, 255, 255, 191))  # 75% transparent white
            dc.SetBrush(brush)
            start_x, start_y = self.start_pos
            end_x, end_y = self.end_pos
            dc.DrawRectangle(start_x, start_y, end_x - start_x, end_y - start_y)

    def on_left_down(self, event):
        self.start_pos = event.GetPosition()
        self.end_pos = None
        self.Refresh()

    def on_mouse_drag(self, event):
        if event.Dragging() and event.LeftIsDown() and self.start_pos:
            self.end_pos = event.GetPosition()
            self.Refresh()

    def on_left_up(self, event):
        if self.start_pos and self.end_pos:
            self.end_pos = event.GetPosition()
            self.update_roi_text_boxes()
            wx.PostEvent(self, ROIChangedEvent())
            self.Refresh()

    def update_roi_text_boxes(self):
        x1, y1 = self.start_pos
        x2, y2 = self.end_pos

        x = min(x1, x2)
        y = min(y1, y2)
        w = abs(x2 - x1)
        h = abs(y2 - y1)


        normalized_x = x / self.resized_image.shape[1]
        normalized_y = y / self.resized_image.shape[0]
        normalized_w = w / self.resized_image.shape[1]
        normalized_h = h / self.resized_image.shape[0]

        if normalized_w > 1:
            normalized_w = 1
        if normalized_h > 1:
            normalized_h = 1

        self.x_text.SetValue(f"{normalized_x:.4f}")
        self.y_text.SetValue(f"{normalized_y:.4f}")
        self.w_text.SetValue(f"{normalized_w:.4f}")
        self.h_text.SetValue(f"{normalized_h:.4f}")

    def set_default_roi(self):
        """Set the default ROI to the middle third of the image dimensions."""
        self.start_pos = (int(self.resized_image.shape[1] * 1/3), int(self.resized_image.shape[0] * 1/3))
        self.end_pos = (int(self.resized_image.shape[1] * 2/3), int(self.resized_image.shape[0] * 2/3))
        self.update_roi_text_boxes()
        self.Refresh()

    def set_roi(self, roi):
        """Set the ROI based on provided normalized coordinates (x, y, w, h)."""
        normalized_x, normalized_y, normalized_w, normalized_h = roi
        self.start_pos = (int(normalized_x * self.resized_image.shape[1]), int(normalized_y * self.resized_image.shape[0]))
        self.end_pos = (int((normalized_x + normalized_w) * self.resized_image.shape[1]), int((normalized_y + normalized_h) * self.resized_image.shape[0]))
        self.update_roi_text_boxes()
        self.Refresh()

    def on_ok(self, event):
        x = float(self.x_text.GetValue())
        y = float(self.y_text.GetValue())
        w = float(self.w_text.GetValue())
        h = float(self.h_text.GetValue())

        #print(f"Final ROI coordinates: x={x}, y={y}, w={w}, h={h}")
        self.EndModal(wx.ID_OK)
