import os
import wx
import wx.lib.scrolledpanel as scrolled
import image_combine
import shutil
from picam_set_pnl import picam_sets_pnl
from fswebcam_set_pnl import fs_sets_pnl

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # read / save cam config button
        self.read_btn = wx.Button(self, label='read config')
        self.read_btn.Bind(wx.EVT_BUTTON, self.read_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.read_btn, 0, wx.ALL, 0)
        self.SetSizer(main_sizer)

    def read_click(self, e):
        print(" This button does nothing.")


#class info_pnl(wx.Panel):
class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        c_pnl = parent.dict_C_pnl['camera_pnl']
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (1000,1000))
        # config file choice
        label = wx.StaticText(self, label='Local files')

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(label, 0, wx.ALL, 0)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
