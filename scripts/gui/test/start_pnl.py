import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        #self.SetBackgroundColour((100,150,170))
        #self.l_ip = wx.StaticText(self,  label=' Start \n'*5)

class info_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

    # def OnEraseBackground(self, evt):
    #     # yanked from ColourDB.py #then from https://www.blog.pythonlibrary.org/2010/03/18/wxpython-putting-a-background-image-on-a-panel/
    #     dc = evt.GetDC()
    #     if not dc:
    #         dc = wx.ClientDC(self)
    #         rect = self.GetUpdateRegion().GetBox()
    #         dc.SetClippingRect(rect)
    #     dc.Clear()
    #     bmp = wx.Bitmap("./ui_images/splash.png")
    #     dc.DrawBitmap(bmp, 0, 0)

    def OnEraseBackground(self, evt):
            dc = evt.GetDC()
            if not dc:
                dc = wx.ClientDC(self)
                rect = self.GetUpdateRegion().GetBox()
                dc.SetClippingRect(rect)

            dc.Clear()
            img = wx.Image("./ui_images/splash.png", wx.BITMAP_TYPE_ANY)
            img = img.Scale(self.GetSize().GetWidth(), self.GetSize().GetHeight(), wx.IMAGE_QUALITY_HIGH)
            bmp = img.ConvertToBitmap()
            dc.DrawBitmap(bmp, 0, 0)
