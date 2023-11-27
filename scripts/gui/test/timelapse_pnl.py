import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((100,150,170))
        self.l_ip = wx.StaticText(self,  label=' Timelapse \n'*5)

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
