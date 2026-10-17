import math
import os

import wx
import wx.lib.newevent

from panels.camera_controls import controls_grid, load_settings, serialize_settings

ROIChangedEvent, EVT_ROI_CHANGED = wx.lib.newevent.NewEvent()


class rpicap_sets_pnl(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent, style=wx.TAB_TRAVERSAL)
        label = wx.StaticText(self, label="Rpicam settings")
        label.SetFont(parent.parent.shared_data.button_font)
        self.c_sets_sizer, self.setting_crtl_dict, self.setting_t_dict = self.create_empty_settings_sizer()
        self.refresh_settings_sizer()

        set_afroi_button = wx.Button(self, label="Set autofocus region…")
        set_afroi_button.SetToolTip("Select the focus area on the latest photo, or enter normalized coordinates.")
        set_afroi_button.Bind(wx.EVT_BUTTON, self.set_afroi_click)
        heading = wx.BoxSizer(wx.HORIZONTAL)
        heading.Add(label, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        heading.Add(set_afroi_button, 0)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(heading, 0, wx.EXPAND | wx.BOTTOM, 8)
        self.main_sizer.Add(self.c_sets_sizer, 0, wx.EXPAND)
        self.SetSizer(self.main_sizer)

    def set_afroi_click(self, event):
        setting = self.setting_crtl_dict.get("autofocus-window")
        if setting is None:
            wx.MessageBox("This camera does not provide an autofocus-window setting.", "Autofocus region", wx.OK | wx.ICON_INFORMATION)
            return
        try:
            initial_roi = parse_roi(setting.GetValue())
        except (ValueError, TypeError):
            initial_roi = (0.33, 0.33, 0.33, 0.33)
        shared_data = self.parent.parent.shared_data
        image_path = getattr(shared_data, "most_recent_camera_capture", "") or getattr(shared_data, "most_recent_camconf_image", "")
        if not image_path or not os.path.isfile(image_path):
            image_path = "./test.jpg" if os.path.isfile("./test.jpg") else None
        dialog = SetAFROIDialog(self, image_path, initial_roi)
        try:
            if dialog.ShowModal() == wx.ID_OK:
                setting.SetValue(dialog.get_roi())
        finally:
            dialog.Destroy()

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
                        "shutter":["0", "0", "Shutter speed in microseconds; 0 selects automatic exposure"],
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
                        "awbgains":["0,0", "0,0", "Explicit red and blue white balance gains, separated by a comma"],
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
                        "post-process-file":["", "", "Path to post-processing configuration file"],
                        "quality":[(1, 100), "", "JPEG quality (1–100); leave blank for the camera default"],
                        "timeout":["", "", "Camera warm-up time, e.g. 5s or 2000ms; blank uses the tool default"],
                        "framerate":["", "", "Frame rate; lower values allow longer exposures"]}

        return control_dict

    def create_empty_settings_sizer(self):
        return wx.BoxSizer(wx.VERTICAL), {}, {}

    def refresh_settings_sizer(self):
        previous = {key: control.GetValue() for key, control in self.setting_crtl_dict.items()}
        preset_res = ['4608x2592 "picam v3"', '4056x3040 "picam HQ"',
                      '3280x2464 "picam v2"', '3840x2160 "4K UHD"',
                      '2592x1944 "picam v1"', '1920x1080 "Full HD (1080p)"',
                      '1280x720 "HD (720p)"', '640x480 "VGA"', '320x240 "QVGA"']
        specs = {"Resolution": [preset_res[0], preset_res,
                                "Image dimensions in pixels; select a preset or type WIDTHxHEIGHT."]}
        # This backend's original schema is [options, default, optional hint].
        for key, spec in self.make_control_dict().items():
            specs[key] = [spec[1], spec[0]] + spec[2:]
        self.c_sets_sizer.Clear(delete_windows=True)
        grid, self.setting_crtl_dict, self.setting_t_dict = controls_grid(self, specs)
        self.c_sets_sizer.Add(grid, 0, wx.EXPAND)
        for key, value in previous.items():
            if key in self.setting_crtl_dict:
                self.setting_crtl_dict[key].SetValue(value)
        self.Layout()
        self.parent.Layout()

    def make_conf_text(self, setting_dict):
        return serialize_settings(self, setting_dict, self.set_for_text)

    def set_for_text(self, settings):
        if "Resolution" in settings:
            settings["Resolution"] = str(settings["Resolution"]).split()[0]
        return settings

    def text_into_ui(self, set_text):
        load_settings(self, set_text, aliases=False)

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


def parse_roi(value):
    """Validate normalized x,y,width,height without clipping a user's input."""
    if isinstance(value, str):
        value = value.split(",")
    values = tuple(float(item) for item in value)
    if len(values) != 4 or not all(math.isfinite(item) for item in values):
        raise ValueError("Enter four finite numbers: x, y, width, height.")
    x, y, width, height = values
    if (x < 0 or y < 0 or width <= 0 or height <= 0
            or x + width > 1.0000001 or y + height > 1.0000001):
        raise ValueError("Use coordinates from 0 to 1, with a positive width and height inside the image.")
    return values


class SetAFROIDialog(wx.Dialog):
    """A scaled image selector that also works before the first photo exists."""

    def __init__(self, parent, image_path=None, initial_roi=None):
        display_width, display_height = wx.GetClientDisplayRect().GetSize()
        super().__init__(parent, title="Set autofocus region",
                         size=(min(780, display_width - 40), min(600, display_height - 60)),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.image = None
        self.bitmap = None
        self._image_rect = (0, 0, 1, 1)
        self._drag_start = None
        self._roi = parse_roi(initial_roi or (0.33, 0.33, 0.33, 0.33))
        self.image_panel = wx.Panel(self, style=wx.FULL_REPAINT_ON_RESIZE)
        self.image_panel.SetMinSize((280, 180))
        self.image_panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.image_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.image_panel.Bind(wx.EVT_SIZE, self.on_resize)
        self.image_panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.image_panel.Bind(wx.EVT_MOTION, self.on_mouse_drag)
        self.image_panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.image_panel.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.on_capture_lost)

        instruction = wx.StaticText(self, label="Drag on the image to select a focus area, or enter coordinates from 0 to 1.")
        coordinates = wx.FlexGridSizer(cols=8, hgap=6, vgap=4)
        self.roi_fields = []
        for index, name in enumerate(("X", "Y", "Width", "Height")):
            coordinates.Add(wx.StaticText(self, label=name), 0, wx.ALIGN_CENTER_VERTICAL)
            field = wx.TextCtrl(self, value=str(self._roi[index]), style=wx.TE_PROCESS_ENTER)
            field.SetMinSize((65, -1))
            field.Bind(wx.EVT_TEXT, self.on_coordinate_change)
            field.Bind(wx.EVT_TEXT_ENTER, self.on_coordinate_change)
            self.roi_fields.append(field)
            coordinates.Add(field, 1, wx.EXPAND)
            coordinates.AddGrowableCol(index * 2 + 1, 1)
        self.x_text, self.y_text, self.w_text, self.h_text = self.roi_fields

        choose_button = wx.Button(self, label="Choose image…")
        choose_button.Bind(wx.EVT_BUTTON, self.on_choose_image)
        reset_button = wx.Button(self, label="Full image")
        reset_button.Bind(wx.EVT_BUTTON, lambda event: self.set_roi((0, 0, 1, 1)))
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(choose_button, 0, wx.RIGHT, 6)
        buttons.Add(reset_button, 0)
        buttons.AddStretchSpacer()
        standard_buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        buttons.Add(standard_buttons, 0)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(instruction, 0, wx.ALL | wx.EXPAND, 10)
        layout.Add(self.image_panel, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        layout.Add(coordinates, 0, wx.ALL | wx.EXPAND, 10)
        layout.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(layout)
        self.SetMinSize((580, 380))
        if image_path:
            self.load_image(image_path)
        self.CentreOnParent()

    def load_image(self, image_path):
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        if not image.IsOk():
            return False
        self.image = image
        self.bitmap = None
        self.image_panel.Refresh()
        return True

    def on_choose_image(self, event):
        with wx.FileDialog(self, "Choose a reference photo", wildcard="Images|*.jpg;*.jpeg;*.png;*.bmp;*.JPG;*.JPEG;*.PNG|All files|*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dialog:
            if dialog.ShowModal() == wx.ID_OK and not self.load_image(dialog.GetPath()):
                wx.MessageBox("The selected file could not be opened as an image.", "Reference photo", wx.OK | wx.ICON_ERROR)

    def _layout_image(self):
        width, height = self.image_panel.GetClientSize()
        width, height = max(1, width), max(1, height)
        if self.image is None:
            self._image_rect = (0, 0, width, height)
            return
        scale = min(width / self.image.GetWidth(), height / self.image.GetHeight())
        image_width = max(1, int(self.image.GetWidth() * scale))
        image_height = max(1, int(self.image.GetHeight() * scale))
        self._image_rect = ((width - image_width) // 2, (height - image_height) // 2,
                            image_width, image_height)
        if self.bitmap is None or self.bitmap.GetSize() != (image_width, image_height):
            self.bitmap = wx.Bitmap(self.image.Scale(image_width, image_height, wx.IMAGE_QUALITY_HIGH))

    def on_resize(self, event):
        self.bitmap = None
        self.image_panel.Refresh()
        event.Skip()

    def on_paint(self, event):
        self._layout_image()
        dc = wx.AutoBufferedPaintDC(self.image_panel)
        dc.SetBackground(wx.Brush(wx.Colour(40, 43, 48)))
        dc.Clear()
        left, top, width, height = self._image_rect
        if self.bitmap is not None:
            dc.DrawBitmap(self.bitmap, left, top)
        else:
            dc.SetTextForeground(wx.Colour(225, 225, 225))
            dc.DrawText("Take a photo or choose an image for a reference.", 14, 14)
        x, y, roi_width, roi_height = self._roi
        dc.SetPen(wx.Pen(wx.Colour(40, 210, 255), 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(left + round(x * width), top + round(y * height),
                         max(1, round(roi_width * width)), max(1, round(roi_height * height)))

    def _normalized_position(self, position):
        self._layout_image()
        left, top, width, height = self._image_rect
        return (max(0, min(1, (position.x - left) / width)),
                max(0, min(1, (position.y - top) / height)))

    def on_left_down(self, event):
        self._drag_start = self._normalized_position(event.GetPosition())
        self.image_panel.CaptureMouse()

    def _update_drag(self, event):
        if self._drag_start is None:
            return
        x, y = self._drag_start
        end_x, end_y = self._normalized_position(event.GetPosition())
        if x != end_x and y != end_y:
            self.set_roi((min(x, end_x), min(y, end_y), abs(end_x - x), abs(end_y - y)))

    def on_mouse_drag(self, event):
        if event.Dragging() and event.LeftIsDown():
            self._update_drag(event)

    def on_left_up(self, event):
        self._update_drag(event)
        self._drag_start = None
        if self.image_panel.HasCapture():
            self.image_panel.ReleaseMouse()
        wx.PostEvent(self, ROIChangedEvent())

    def on_capture_lost(self, event):
        self._drag_start = None

    def set_roi(self, roi):
        self._roi = parse_roi(roi)
        for field, value in zip(self.roi_fields, self._roi):
            field.ChangeValue(str(value))
        self.image_panel.Refresh()

    def on_coordinate_change(self, event):
        try:
            self._roi = parse_roi([field.GetValue() for field in self.roi_fields])
        except (ValueError, TypeError):
            return
        self.image_panel.Refresh()

    def get_roi(self):
        return ",".join(field.GetValue().strip() for field in self.roi_fields)

    def on_ok(self, event):
        try:
            parse_roi(self.get_roi())
        except (ValueError, TypeError) as error:
            wx.MessageBox(str(error), "Autofocus region", wx.OK | wx.ICON_WARNING)
            return
        self.EndModal(wx.ID_OK)
