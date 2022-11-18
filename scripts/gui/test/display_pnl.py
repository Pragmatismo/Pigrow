import os
import datetime
import wx
import wx.lib.scrolledpanel as scrolled

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent

        wx.Panel.__init__ (self, parent, id=wx.ID_ANY, size=(100,-1), style=wx.TAB_TRAVERSAL)
        # button to refresh pnl information
        self.refresh_btn = wx.Button(self, label='Refresh Info')
        self.refresh_btn.Bind(wx.EVT_BUTTON, self.refresh_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.refresh_btn, 0, wx.ALL, 0)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def connect_to_pigrow(self):
        print("display pannel connected to pigrow and doing nothing with it :D lol")

    def refresh_click(self, e):
        print("You pressed a button and all it does is show this text")


class info_pnl(scrolled.ScrolledPanel):
    def __init__(self, parent):
        shared_data = parent.shared_data
        self.parent = parent
        #c_pnl = parent.dict_C_pnl['display_pnl']
        w = 1000
        wx.Panel.__init__ (self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL, size = (w,-1))

        # Title and Subtitle
        self.SetFont(shared_data.title_font)
        page_title =  wx.StaticText(self,  label='Display')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Show output from the pigrow via local displays')
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        title_sizer.Add(page_title, 1,wx.ALIGN_CENTER_HORIZONTAL, 5)
        title_sizer.Add(page_sub_title, 1, wx.ALIGN_CENTER_HORIZONTAL, 5)

        # LED
        led_title =  wx.StaticText(self,  label='LED')
        led_sizer = wx.BoxSizer(wx.VERTICAL)
        led_sizer.Add(led_title, 1,wx.ALL, 5)


        # Datawall
        datawall_title =  wx.StaticText(self,  label='Datawall')
        # datawall - hdmi
        # datawall - remote upload
        #                 - modular using script
        datawall_sizer = wx.BoxSizer(wx.VERTICAL)
        datawall_sizer.Add(datawall_title, 1,wx.ALL, 5)


        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(title_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(led_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(datawall_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.SetSizer(self.main_sizer)
