"""Camera photo previews and their fixed navigation bar."""

import wx


class PhotoView(wx.Panel):
    def __init__(self, parent, record, on_open):
        super().__init__(parent)
        self.panel = self
        self.record = record
        self.label = wx.StaticText(self)
        self.bitmap = wx.StaticBitmap(self, bitmap=record.get_bitmap())
        self.bitmap.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.bitmap.SetToolTip('Open this photograph')
        self.bitmap.Bind(wx.EVT_LEFT_DOWN, lambda event: on_open(record))
        self._render_width = record.width
        self._caption = record.label
        self._label_width = None
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.label, 0, wx.BOTTOM, 6)
        layout.Add(self.bitmap, 0)
        self.SetSizer(layout)

    def set_number(self, number):
        self._caption = '{} · {}'.format(number, self.record.label)
        self._label_width = None

    def render(self, width=None):
        width = self.record.width if width is None else max(1, int(width))
        changed = False
        if self._label_width != width:
            self.label.SetLabel(self._caption)
            self.label.Wrap(width)
            self._label_width = width
            changed = True
        if width != self._render_width:
            self.bitmap.SetBitmap(self.record.get_bitmap(width))
            self._render_width = width
            changed = True
        if changed:
            self.InvalidateBestSize()
            self.Layout()


class PhotoToolbar(wx.Panel):
    """Small thumbnail shortcuts and actions, separate from scrolling content."""

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.nav_buttons = []
        window = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        face = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        channels = [(window[index] + face[index]) // 2 for index in range(3)]
        if sum(abs(channels[index] - window[index]) for index in range(3)) < 12:
            delta = -10 if sum(channels) > 384 else 10
            channels = [max(0, min(255, channel + delta)) for channel in channels]
        self.SetBackgroundColour(wx.Colour(*channels))
        self.clear_btn = wx.Button(self, label='Clear photos')
        self.clear_btn.Disable()
        self.clear_btn.Bind(wx.EVT_BUTTON, owner.clear_pics_click)
        self.show_last_btn = wx.Button(self, label='Show last photo')
        self.show_last_btn.Disable()
        self.show_last_btn.Bind(wx.EVT_BUTTON, owner.show_last_click)
        self.scale_cb = wx.CheckBox(self, label='Scale to fit')
        self.scale_cb.SetBackgroundColour(self.GetBackgroundColour())
        self.scale_cb.SetToolTip('Fit photo width to the available space. Turn off to view full-size pixels.')
        self.scale_cb.Bind(wx.EVT_CHECKBOX, owner.scale_photos_click)
        row = wx.WrapSizer(wx.HORIZONTAL)
        self.row_sizer = row
        row.Add(self.clear_btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 6)
        row.Add(self.show_last_btn, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 12)
        row.Add(self.scale_cb, 0, wx.ALIGN_CENTER_VERTICAL)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(wx.StaticLine(self), 0, wx.EXPAND)
        layout.Add(row, 1, wx.ALL | wx.EXPAND, 8)
        self.SetSizer(layout)

    def _thumbnail(self, record, label):
        bitmap = wx.Bitmap(44, 30)
        dc = wx.MemoryDC(bitmap)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        thumbnail = record.thumbnail(44, 30)
        dc.DrawBitmap(thumbnail, (44 - thumbnail.GetWidth()) // 2,
                      (30 - thumbnail.GetHeight()) // 2, True)
        font = self.GetFont()
        font.SetPointSize(max(7, font.GetPointSize() - 2))
        dc.SetFont(font)
        text_width, text_height = dc.GetTextExtent(label)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(42, 45, 48)))
        dc.DrawRectangle(0, 30 - text_height - 2, text_width + 6, text_height + 2)
        dc.SetTextForeground(wx.WHITE)
        dc.DrawText(label, 3, 30 - text_height - 1)
        dc.SelectObject(wx.NullBitmap)
        return bitmap

    def set_photos(self, records):
        for button in self.nav_buttons:
            self.row_sizer.Detach(button)
            button.Destroy()
        self.nav_buttons = []
        shortcuts = [(str(index + 1), record) for index, record in enumerate(records[:5])]
        if len(records) > 5:
            shortcuts.append(('Last', records[-1]))
        for label, record in shortcuts:
            button = wx.BitmapButton(self, bitmap=self._thumbnail(record, label),
                                     style=wx.BU_EXACTFIT)
            button.SetName('Photo ' + label)
            button.SetLabel(label)
            button.photo_record_id = record.record_id
            button.SetToolTip('{} · {}'.format(label, record.label))
            button.Bind(wx.EVT_BUTTON,
                        lambda event, record_id=record.record_id: self.owner.scroll_to_photo(record_id))
            self.row_sizer.Insert(len(self.nav_buttons), button, 0,
                                  wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 4)
            self.nav_buttons.append(button)
        self.clear_btn.Enable(bool(records))
        self.InvalidateBestSize()
        self.Layout()
