"""Shared normalized crop and autofocus selectors for camera settings panels."""

import math
import os

import wx
import wx.lib.newevent

ROIChangedEvent, EVT_ROI_CHANGED = wx.lib.newevent.NewEvent()


def parse_roi(value):
    """Validate normalized x,y,width,height without clipping a user's input."""
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("(") and value.endswith(")"):
            value = value[1:-1]
        value = value.split(",")
    values = tuple(float(item) for item in value)
    if len(values) != 4 or not all(math.isfinite(item) for item in values):
        raise ValueError("Enter four finite numbers: x, y, width, height.")
    x, y, width, height = values
    if (x < 0 or y < 0 or width <= 0 or height <= 0
            or x + width > 1.0000001 or y + height > 1.0000001):
        raise ValueError("Use coordinates from 0 to 1, with a positive width and height inside the image.")
    return values


class ImageRegionDialog(wx.Dialog):
    """A scaled image selector that also works before the first photo exists."""

    def __init__(self, parent, image_path=None, initial_roi=None, *,
                 region_kind="autofocus", image=None, reference_roi=None):
        display_width, display_height = wx.GetClientDisplayRect().GetSize()
        self.region_title = "Autofocus region" if region_kind == "autofocus" else "Crop region"
        self.region_kind = region_kind
        self.reference_roi = parse_roi(reference_roi or (0, 0, 1, 1))
        super().__init__(parent, title="Set " + self.region_title.lower(),
                         size=(min(780, display_width - 40), min(600, display_height - 60)),
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.image = None
        self.bitmap = None
        self._image_rect = (0, 0, 1, 1)
        self._drag_start = None
        default_roi = (0.33, 0.33, 0.33, 0.33) if region_kind == "autofocus" else (0, 0, 1, 1)
        self._roi = parse_roi(initial_roi or default_roi)
        self.image_panel = wx.Panel(self, style=wx.FULL_REPAINT_ON_RESIZE)
        self.image_panel.SetMinSize((280, 180))
        self.image_panel.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.image_panel.Bind(wx.EVT_PAINT, self.on_paint)
        self.image_panel.Bind(wx.EVT_SIZE, self.on_resize)
        self.image_panel.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.image_panel.Bind(wx.EVT_MOTION, self.on_mouse_drag)
        self.image_panel.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.image_panel.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.on_capture_lost)

        area = "focus area" if region_kind == "autofocus" else "crop area"
        self.instruction_text = "Drag on the image to select a %s, or enter coordinates from 0 to 1." % area
        self.instruction = wx.StaticText(self)
        self.instruction.SetMinSize((0, -1))
        self._update_instruction()
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
        layout.Add(self.instruction, 0, wx.ALL | wx.EXPAND, 10)
        layout.Add(self.image_panel, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
        layout.Add(coordinates, 0, wx.ALL | wx.EXPAND, 10)
        layout.Add(buttons, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        self.SetSizer(layout)
        self.SetMinSize((min(580, display_width - 40), min(380, display_height - 60)))
        self.Bind(wx.EVT_SIZE, self.on_dialog_resize)
        if image is not None and image.IsOk():
            self.image = image.Copy()
        elif image_path:
            self.load_image(image_path, reset_reference=False)
        self.CentreOnParent()

    def _update_instruction(self):
        text = self.instruction_text
        if self.reference_roi != (0, 0, 1, 1):
            text += " The reference photo is already cropped; coordinates still refer to the full camera image."
        self.instruction.SetLabel(text)
        self.instruction.Wrap(max(200, self.GetClientSize().width - 20))

    def on_dialog_resize(self, event):
        self._update_instruction()
        self.Layout()
        event.Skip()

    def load_image(self, image_path, reset_reference=True):
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        if not image.IsOk():
            return False
        self.image = image
        if reset_reference:
            self.reference_roi = (0, 0, 1, 1)
            self._update_instruction()
            self.Layout()
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
        ref_x, ref_y, ref_width, ref_height = self.reference_roi
        x, y = (x - ref_x) / ref_width, (y - ref_y) / ref_height
        roi_width, roi_height = roi_width / ref_width, roi_height / ref_height
        dc.SetClippingRegion(left, top, width, height)
        dc.SetPen(wx.Pen(wx.Colour(40, 210, 255), 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(left + round(x * width), top + round(y * height),
                         max(1, round(roi_width * width)), max(1, round(roi_height * height)))

    def _normalized_position(self, position):
        self._layout_image()
        left, top, width, height = self._image_rect
        ref_x, ref_y, ref_width, ref_height = self.reference_roi
        return (ref_x + ref_width * max(0, min(1, (position.x - left) / width)),
                ref_y + ref_height * max(0, min(1, (position.y - top) / height)))

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
            wx.MessageBox(str(error), self.region_title, wx.OK | wx.ICON_WARNING)
            return
        self.EndModal(wx.ID_OK)


# Keep the original dialog import available for callers and saved UI workflows.
SetAFROIDialog = ImageRegionDialog


def edit_region(panel, setting, region_kind="crop", tuple_format=False):
    """Only commit a validated selection; opening or cancelling keeps text intact."""
    control = panel.setting_crtl_dict.get(setting)
    if control is None:
        return
    try:
        initial_roi = parse_roi(control.GetValue())
    except (ValueError, TypeError):
        initial_roi = (0.33, 0.33, 0.33, 0.33) if region_kind == "autofocus" else (0, 0, 1, 1)
    image = None
    reference_roi = None
    reference_provider = getattr(panel.parent, "get_region_reference_image", None)
    if reference_provider:
        image = reference_provider()
        roi_provider = getattr(panel.parent, "get_region_reference_roi", None)
        if image is not None and roi_provider:
            try:
                reference_roi = parse_roi(roi_provider())
            except (ValueError, TypeError):
                pass
    shared_data = panel.parent.parent.shared_data
    image_path = getattr(shared_data, "most_recent_camera_capture", "") or getattr(shared_data, "most_recent_camconf_image", "")
    if not image_path or not os.path.isfile(image_path):
        image_path = "./test.jpg" if os.path.isfile("./test.jpg") else None
    dialog = ImageRegionDialog(panel, image_path, initial_roi, region_kind=region_kind,
                               image=image, reference_roi=reference_roi)
    try:
        if dialog.ShowModal() == wx.ID_OK:
            value = dialog.get_roi()
            control.SetValue("(" + value + ")" if tuple_format else value)
    finally:
        dialog.Destroy()


def create_region_button(panel, setting, region_kind="crop", tuple_format=False):
    button = wx.Button(panel, label="Set region", style=wx.BU_EXACTFIT)
    button.SetToolTip("Select a %s region on the latest camera photo, or enter normalized coordinates." % region_kind)
    button.Bind(wx.EVT_BUTTON, lambda event: edit_region(panel, setting, region_kind, tuple_format))
    return button
