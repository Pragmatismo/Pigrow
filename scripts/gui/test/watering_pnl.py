import wx


class ctrl_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170))


        self.add_tank_btn = wx.Button(self, label='Add Tank')
        self.add_tank_btn.Bind(wx.EVT_BUTTON, self.add_tank_click)

        # main sizer
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.add_tank_btn, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        self.SetSizer(main_sizer)

    def add_tank_click(self, e):
        #i_pnl = self.parent.dict_I_pnl['watering_pnl']
        # load config from file and fill tables so there are no conflicts
    #    self.fill_tables_click("e")
        # set blanks for dialog box
        # call dialog box
        tank_dialog.s_name = "lol"
        tank_dialog.s_volume = ""
        tank_dialog.s_mode = ""
        add_dlb = tank_dialog(self, self.parent)
        add_dlb.ShowModal()
    #    self.fill_tables_click("e")

    def connect_to_pigrow(self):
        '''
        This is called every time a connection to a pigrow is made
        '''
        # Set values from config for set
        #if '---setting name goes here------' in shared_data.gui_set_dict:
        #self.tank_size_tc.SetValue(shared_data.gui_set_dict['---setting name goes here------'])


        pass

class info_pnl(wx.Panel):
    #
    #
    def __init__( self, parent ):
        self.parent = parent
        shared_data = parent.shared_data
        self.c_pnl = parent.dict_C_pnl['watering_pnl']
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        #self.SetBackgroundColour((50,50,50))

        # Tab Title
        title_l = wx.StaticText(self,  label='Watering Control Panel', size=(500,40))
        title_l.SetFont(shared_data.title_font)
        page_sub_title =  wx.StaticText(self,  label='Self Watering System Control', size=(550,30))
        page_sub_title.SetFont(shared_data.sub_title_font)

        # Tank Size Panel
        tank_size_title =  wx.StaticText(self,  label='Tank Size Calculations')
        self.tank_size_st = wx.StaticText(self, label='Tank Size in mL')
        self.tank_size_tc = wx.TextCtrl(self)
        t_size_sizer = wx.BoxSizer(wx.HORIZONTAL)
        t_size_sizer.Add(self.tank_size_st, 1, wx.ALL, 3)
        t_size_sizer.Add(self.tank_size_tc, 1, wx.ALL, 3)

        tank_size_sizer = wx.BoxSizer(wx.VERTICAL)
        tank_size_sizer.Add(tank_size_title, 1, wx.ALL|wx.EXPAND, 3)
        tank_size_sizer.Add(t_size_sizer, 1, wx.ALL, 3)


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(tank_size_sizer, 1, wx.ALL, 3)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)


class tank_dialog(wx.Dialog):
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(tank_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 450))
        self.SetTitle("Water Tank Setup")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        # panel
        pnl = wx.Panel(self)

        # Header
        box_label = wx.StaticText(self,  label='Water Tank Config')
        box_label.SetFont(shared_data.title_font)
        # Show guide button
        show_guide_btn = wx.Button(self, label='Guide', size=(175, 30))
        show_guide_btn.Bind(wx.EVT_BUTTON, self.show_guide_click)
        header_sizer =  wx.BoxSizer(wx.HORIZONTAL)
        header_sizer.Add(box_label, 0, wx.ALL, 5)
        header_sizer.AddStretchSpacer(1)
        header_sizer.Add(show_guide_btn, 0, wx.ALL, 5)

        # buttons_
        self.save_btn = wx.Button(self, label='Save', size=(175, 30))
        self.save_btn.Bind(wx.EVT_BUTTON, self.save_click)
        self.cancel_btn = wx.Button(self, label='Cancel', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.save_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)

        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(header_sizer, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        #main_sizer.Add(name_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.Add(volume_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.Add(mode_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(main_sizer)

    def show_guide_click(self, e):
        self.parent.parent.shared_data.show_help('wtank_help.png')

    def save_click(self, e):
        print("Saving is not yet enabled, sorry about that")    

    def OnClose(self, e):
        self.s_name  = ""
        self.s_volume = ""
        self.s_mode = ""
        self.Destroy()
