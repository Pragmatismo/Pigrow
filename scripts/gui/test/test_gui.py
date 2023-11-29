#!/usr/bin/python3
import sys
import wx

import shared_data
import link_pnl as link_pnl

list_of_panels = ['start_pnl',  'system_pnl', 'cron_pnl', 'camera_pnl', 'timelapse_pnl', 'localfiles_pnl', 'sensors_pnl', 'power_pnl', 'watering_pnl', 'display_pnl', 'userlog_pnl']
for x in list_of_panels:
    import_cmd = "import " + x
    exec(import_cmd)

class view_pnl(wx.Panel):
    '''
     Creates the little pannel with the navigation tabs
     small and simple, it changes which pannels are visible
    '''
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((230,200,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        self.current_display = 'start_pnl'
        #Showing only completed tabs
        self.view_cb = wx.ComboBox(self, choices = list_of_panels)
        self.view_cb.SetFont(MainApp.shared_data.button_font)
        self.view_cb.Bind(wx.EVT_TEXT, self.view_combo_go)
        # sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.view_cb, 0, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def view_combo_go(self, e):
        display = self.view_cb.GetValue()
        MainFrame.dict_I_pnl[self.current_display].Hide()
        MainFrame.dict_C_pnl[self.current_display].Hide()
        self.current_display = display
        MainFrame.dict_I_pnl[display].Show()
        MainFrame.dict_C_pnl[display].Show()
        MainFrame.window.Layout()

class MainFrame(wx.Frame):
    def __init__(self, parent):
        # Settings
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Pigrow Remote Interface", pos = wx.DefaultPosition, style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.Bind(wx.EVT_SIZE, self.resize_window)

        # load link panel
        self.link_pnl = link_pnl.link_pnl(self, MainApp.shared_data)
        self.view_pnl = view_pnl(self)

        # create dictionaries of initiated panels
        MainFrame.dict_C_pnl = {}
        MainFrame.dict_I_pnl = {}
        pnl_args = "(self)"
        for x in list_of_panels:
            # ctrl panel dict
            try:
                create_cmd = "MainFrame.dict_C_pnl['"+x+"']= " + x + ".ctrl_pnl" + pnl_args
                exec(create_cmd)
            except:
                raise
                create_cmd = "MainFrame.dict_C_pnl['"+x+"']= blank_pnl.ctrl_pnl " + pnl_args
                exec(create_cmd)
            # info panel dict
            try:
                # if pannel has no info panel use blank (can be used for showing images, writing to directly, etc)
                create_cmd = "MainFrame.dict_I_pnl['"+x+"']= " + x + ".info_pnl" + pnl_args
                exec(create_cmd)
            except:
                raise
                create_cmd = "MainFrame.dict_I_pnl['"+x+"']= blank_pnl.info_pnl" + pnl_args
                exec(create_cmd)

        # add panels to sizer
        # make left bar with ctrl panels
        side_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        side_bar_sizer.Add(self.link_pnl, 0, wx.ALL|wx.EXPAND, 0)
        side_bar_sizer.Add(self.view_pnl, 0, wx.ALL|wx.EXPAND, 0)
        for pnl in list_of_panels:
            MainFrame.dict_C_pnl[pnl].SetMinSize((-1,800))
            side_bar_sizer.Add(MainFrame.dict_C_pnl[pnl], 0, wx.ALL|wx.EXPAND, 0)
        # add info panels
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(side_bar_sizer, 0, wx.ALL|wx.EXPAND, 0)
        for pnl in list_of_panels:
            main_sizer.Add(MainFrame.dict_I_pnl[pnl], 0, wx.ALL|wx.EXPAND, 0)
        #hide all, then show start screen
        for key, value in MainFrame.dict_C_pnl.items():
            value.Hide()
        for key, value in MainFrame.dict_I_pnl.items():
            value.Hide()
        MainFrame.dict_I_pnl['start_pnl'].Show()
        MainFrame.dict_C_pnl['start_pnl'].Show()

        # setup the window layout
        main_sizer.Fit(self)
        self.SetSizer(main_sizer)
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.Layout()
        self.Centre(wx.BOTH)

        #memory use before connection / data loading
    #    from guppy import hpy
    #    h = hpy()
    #    print (h.heap())

    def tell_pnls_connected(self):
        print("Connected to a pigrow - this is where we'd tell the pnls")
        for key, value in MainFrame.dict_C_pnl.items():
            try:
                value.connect_to_pigrow()
            except Exception as E:
                print(key, "doesn't have connect_to_pigrow")
                #print(E)

    def tell_pnls_updated_config(self):
        print("       Telling all pnls that the config file has been updated")
        for key, value in MainFrame.dict_C_pnl.items():
            try:
                value.updated_config()
            except Exception as E:
                print(key, " - doesn't have updated_config function, no problem it probably doens't need it")



    def resize_window(self, e):
        '''
        Imposes sizes on the panels
        '''
        left_bar_size = 100
        status_bar_height = 175
        win_width = e.GetSize()[0]
        win_height = e.GetSize()[1]
        w_space_left = win_width - left_bar_size
        size = wx.Size(win_width, win_height - status_bar_height)
        for pnl in MainFrame.dict_I_pnl:
            MainFrame.dict_I_pnl[pnl].SetMinSize(size)
            try:
                pnl.SetupScrolling()
            except:
                pass

        try:
            MainFrame.window.Layout()
        except:
            pass #to avoid the error on first init
        #MainApp.graphing_info_pannel.SetupScrolling()


class MainApp(MainFrame):
    def __init__(self, parent):
        # intiate shared data
        MainApp.shared_data = shared_data.shared_data(self)
        # Initiate frame
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, e):
        #Closes SSH connection even on quit
        # need to add 'ya sure?' question if there's unsaved data
        print("Closing SSH connection")
        self.link_pnl.ssh.close()
        sys.exit(0)

def main():
    app = wx.App()
    MainFrame.window = MainApp(None)
    MainFrame.window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    #gui_set = gui_settings()
    try:
        # if run from a desktop icon or something
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    main()
