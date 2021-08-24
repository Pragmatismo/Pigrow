import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170))
        self.l = wx.StaticText(self,  label=((' CTRL '*5)+"\n")*10)

    def connect_to_pigrow(self):
        '''
        This is called every time a connection to a pigrow is made
        '''
        pass

class info_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((50,50,50))
        self.l = wx.StaticText(self,  label=((' INFO '*50) + "\n") * 50)
