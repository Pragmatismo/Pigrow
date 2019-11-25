#!/usr/bin/python3

import os
import sys
import time
import datetime
import wx

class shared_data:
    def __init__(self):
        #This is a temporary fudge soon to be cleaned and used more widely
        #
        ## paths
        #
        # gui system paths
        shared_data.cwd = os.getcwd()
        shared_data.ui_img_path = os.path.join(shared_data.cwd, "ui_images")
        shared_data.graph_modules_path = os.path.join(shared_data.cwd, "graph_modules")
        sys.path.append(shared_data.graph_modules_path)
        shared_data.graph_presets_path = os.path.join(shared_data.cwd, "graph_presets")
        localpath = str(os.getcwd()).split("/scripts")[0]
        print (localpath)
        shared_data.local_logs_path = os.path.join(localpath, "logs")
        local_graphs_path = os.path.join(localpath, "graphs")
        shared_data.local_graph_path = os.path.join(local_graphs_path, "live_rolling.png")
        #shared_data.local_graph_path = "/home/pragmo/frompigrow/carputer/graphs/live_rolling.png"
        #
        ## Fonts
        #
        shared_data.title_font = wx.Font(28, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.sub_title_font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.item_title_font = wx.Font(16, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        shared_data.info_font = wx.Font(14, wx.MODERN, wx.ITALIC, wx.NORMAL)
        shared_data.large_info_font = wx.Font(16, wx.MODERN, wx.ITALIC, wx.NORMAL)
        #
        ## Options
        #
        graph_data_option = "DHT22_Temp.txt"
        shared_data.graph_data_preset_choice = os.path.join(shared_data.graph_presets_path, graph_data_option)
        show_duration = 2 #hours
        #
        ## Data
        #
        shared_data.list_of_datasets = []





class display_pnl(wx.Panel):
    """
    This panel displays the most recent information from the selected graph module or datawall
    """
    #
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        # timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        # Tab Title
        title_l = wx.StaticText(self,  label='Live Display', size=(-1,40))
        title_l.SetBackgroundColour((50,250,250))
        title_l.SetFont(shared_data.title_font)
        self.toggleBtn = wx.Button(self, wx.ID_ANY, "Start")
        self.toggleBtn.Bind(wx.EVT_BUTTON, self.onToggle)
        bitmap = wx.Bitmap(1, 1)
        #bitmap.LoadFile(pic_one, wx.BITMAP_TYPE_ANY)
        size = bitmap.GetSize()
        self.img_bmp_box = wx.StaticBitmap(self, -1, bitmap, size=(size[0], size[1]))


        # sizers
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.image_sizer.Add(self.img_bmp_box, 0, wx.EXPAND, 3)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.toggleBtn, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.image_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def load_log_from_preset(self, preset_path):
        # create dictionary of preset settings
        with open(shared_data.graph_data_preset_choice) as f:
            graph_presets = f.read()
        graph_presets = graph_presets.splitlines()
        preset_settings = {}
        for line in graph_presets:
            if "=" in line:
                equals_pos = line.find("=")
                key = line[:equals_pos]
                value = line[equals_pos + 1:]
                preset_settings[key]=value
        # Setting basic values
        try:
            log_to_load = preset_settings['log_path']
            split_chr = preset_settings['split_chr']
            date_pos = int(preset_settings['date_pos'])
            value_pos = int(preset_settings['value_pos'])
            key_pos = preset_settings['key_pos']
        except:
            print("Split_chr, Date, Value, Key position not set for reading data, can't continue")
            return [[], [], []]
        if not key_pos.isdigit():
            key_pos = ""
        else:
            key_pos = int(key_pos)
        #
        try:
            date_split = preset_settings['date_split']
            date_split_pos = preset_settings['date_split_pos']
        except:
            date_split = ""
            date_split_pos = ""
        #
        try:
            value_split = preset_settings['value_split']
            value_split_pos = preset_settings['value_split_pos']
        except:
            value_split = ""
            value_split_pos = ""
        try:
            key_split = preset_settings['key_split']
            key_split_pos = preset_settings['key_split_pos']
        except:
            key_split = ""
            key_split_pos = ""
        #
        if "value_rem" in preset_settings:
            value_rem = preset_settings['value_rem']
        else:
            value_rem = ""
        if "key_match" in preset_settings:
            key_match = preset_settings['key_match']
        else:
            key_match = ""
        if "key_manual" in preset_settings:
            key_manual = preset_settings['key_manual']
        else:
            key_manual = ""
        ##
        #    Hige and Low values are currently ignored - this should be added in here
        ##
        #
        ## Load data from the log
        #

        log_path = os.path.join(shared_data.local_logs_path, log_to_load)
        #log_path = "/home/pragmo/frompigrow/carputer/logs/dht22_log.txt"
        print("  -- Reading log from file " + log_path)
        with open(log_path) as f:
            log_to_parse = f.read()
        log_to_parse = log_to_parse.splitlines()
        if len(log_to_parse) == 0:
            print("  --- Log file is empty")
        else:
            print("  --- Log contains " + str(len(log_to_parse)) + " lines")
        #
        ##
        #
        numbers_only = True
        limit_by_date = False
        # define lists to fill
        date_list = []
        value_list = []
        key_list = []
        # cycle through each line and fill the lists
        for line in log_to_parse:
            line_items = line.split(split_chr)
            # get date for this log entry
            date = line_items[date_pos]
            if not date_split == "":
                date = date.split(date_split)[date_split_pos]
            if "." in date:
                date = date.split(".")[0]
            # Check date is valid and ignore if not
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if limit_by_date == True:
                    if date > last_datetime or date < first_datetime:
                        date = ""
            except:
                #raise
                print("date not valid -" + str(date))
                date = ""

            # get value for this log entry
            value = line_items[value_pos]
            if not value_split == "":
                value = line_items[value_pos]
                value = value.split(value_split)[value_split_pos]
            # remove from value
            if not value_rem == "":
                value = value.replace(value_rem, "")
            # perform checks for numbers only when selected
            if numbers_only == True:
                try:
                    value = float(value)
                except:
                    print('value not valid -' + str(value))
                    raise
                    value = ""

            # get key for this log entry
            if not key_pos == "":
                key = line_items[key_pos]
                if not key_split == "":
                    key = key.split(key_split)[key_pos_split]
                # if key matching is selected
                if not key_match == "":
                    if not key_match in key:
                        key = False
            # if manual key is selected
            elif not key_manual == "":
                key = key_manual
            elif key_pos == "" and key_manual == "":
                key = ""

            # add to lists
            if not date == "" and not value == "" and not key == False:
                date_list.append(date)
                value_list.append(value)
                key_list.append(key)
        # end of loop - return appropriate lists
        if len(date_list) == 0:
            print("  --- No valid data found")
        else:
            print("  --- Found " + str(len(date_list)) + " valid data points")
        return [date_list, value_list, key_list]



    def make_image_using_module(self):
        # loag log
        log_data = self.load_log_from_preset(shared_data.graph_data_preset_choice)
        shared_data.list_of_datasets.append(log_data)
        # set graph settings
        ymax = ""
        ymin = ""
        dangercold = ""
        toocold = ""
        toohot = ""
        dangerhot = ""
        size_h, size_v = (7, 12)
        module_name = "line"
        module_name = "graph_" + module_name
        file_name = module_name + "_graph.png"
        graph_path = shared_data.local_graph_path
        #
        if module_name in sys.modules:
            del sys.modules[module_name]
        # import the make_graph function as a module
        exec("from " + module_name + " import make_graph", globals())
        # creaty the graph using the imported module
        extra = ""  #this is temporary testing
        make_graph(shared_data.list_of_datasets, graph_path, ymax, ymin, size_h, size_v, dangerhot, toohot, toocold, dangercold, extra)

        return graph_path

    def display_image(self, path_to_image):
        #img_bmp = wx.StaticBitmap(self, -1, wx.Image(path_to_image, wx.BITMAP_TYPE_ANY).ConvertToBitmap()), 0, wx.ALL, 2)
        bitmap = wx.Bitmap(1, 1)
        bitmap.LoadFile(path_to_image, wx.BITMAP_TYPE_ANY)
        self.img_bmp_box.SetBitmap(bitmap)
        MainApp.window_self.Layout()




    def onToggle(self, event):
        refresh_time_seconds = 1000 * 60
        btnLabel = self.toggleBtn.GetLabel()
        if btnLabel == "Start":
            path_to_image = self.make_image_using_module()
            self.display_image(path_to_image)
            self.timer.Start(refresh_time_seconds)
            self.toggleBtn.SetLabel("Stop")
        else:
            self.timer.Stop()
            self.toggleBtn.SetLabel("Start")

    def update(self, event):
        shared_data.list_of_datasets = []
        path_to_image = self.make_image_using_module()
        self.display_image(path_to_image)
        print (time.ctime(), path_to_image)

class MainFrame ( wx.Frame ):
    def __init__( self, parent ):
        # Settings
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = "Pigrow Data Display", pos = wx.DefaultPosition, style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.Bind(wx.EVT_SIZE, self.resize_window)
        MainApp.display_panel = display_pnl(self)

        # Sizers
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(MainApp.display_panel, 0, wx.EXPAND)
        MainApp.window_sizer = wx.BoxSizer(wx.VERTICAL)
        MainApp.window_sizer.Add(main_sizer, 0, wx.EXPAND)
        #MainApp.window_sizer.Fit(self)
        self.SetSizer(MainApp.window_sizer)
        MainApp.window_self = self
        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.Layout()
        self.Centre( wx.BOTH )

    def resize_window(self, e):
        win_width = e.GetSize()[0]
        win_height = e.GetSize()[1]
        size = wx.Size(win_width, win_height)
        #self.SetMinSize(size)
        MainApp.display_panel.SetMinSize(size)
        try:
            MainApp.window_self.Layout()
        except:
            pass #to avoid the error on first init

class MainApp(MainFrame):
    def __init__(self, parent):
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, e):
        print(" -- Exiting --")
        sys.exit(0)

def main():
    app = wx.App()
    shared_data()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    try:
        # if run from a desktop icon or something
        os.chdir(os.path.dirname(sys.argv[0]))
    except:
        pass
    main()
