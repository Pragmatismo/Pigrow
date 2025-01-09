import wx
import wx.grid as gridlib
import wx.adv
import wx.lib.scrolledpanel as scrolled
import importlib
import os
import json
import datetime
import time
import sys



class ctrl_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.loaded_datasets = []

        # Initialize ScrolledPanel instead of Panel
        scrolled.ScrolledPanel.__init__(self, parent, id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the label 'Loaded Datasets' above the table
        label = wx.StaticText(self, label="Datawall")
        self.main_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.load_datawall_btn = wx.Button(self, label="Load Datawall")
        self.load_datawall_btn.Bind(wx.EVT_BUTTON, self.on_load_datawall)
        self.main_sizer.Add(self.load_datawall_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        # Set the sizer
        self.SetSizer(self.main_sizer)

        # Setup scrolling
        self.SetupScrolling(scroll_x=False, scroll_y=True)

    def on_load_datawall(self, e):
        print("Sorry that's not a thing this does.")


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['datawall_pnl']
        w = 1000
        wx.Panel.__init__(self, parent, size=(w, -1), id=wx.ID_ANY, style=wx.TAB_TRAVERSAL)

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self, label='Datawall')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This is in progress and doesn't do anything useful yet"
        page_sub_title = wx.StaticText(self, label=sub_title_text)

        # Main Sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(self.main_sizer)
        self.SetupScrolling()



