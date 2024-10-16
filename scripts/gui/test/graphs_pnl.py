import wx
import wx.lib.scrolledpanel as scrolled


class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )


        ## Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        #main_sizer.AddStretchSpacer(1)

        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def connect_to_pigrow(self):
        self.refresh_list_click(None)


class info_pnl(scrolled.ScrolledPanel):
    def __init__( self, parent ):
        self.parent = parent
        self.shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['graphs_pnl']
        w = 1000
        wx.Panel.__init__ ( self, parent, size = (w,-1), id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )

        # Tab Title
        self.SetFont(self.shared_data.title_font)
        title_l = wx.StaticText(self,  label='Graphs')
        self.SetFont(self.shared_data.sub_title_font)
        sub_title_text = "This will be where graphs are made, at the moment you still need to use the older gui. "
        page_sub_title =  wx.StaticText(self,  label=sub_title_text)



        # Main Sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)
        self.SetupScrolling()
