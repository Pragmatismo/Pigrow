#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import wx
import datetime
target_address = "pi@192.168.1.11"
target_pass    = "raspberry"
target_cap_files   = "/home/pi/Pigrow/caps/*.jpg"
target_log_path = "/home/pi/logs/"
cap_type = "jpg"

if sys.platform == 'win32':
    OS = 'win'
    winrsyncpath = "c:\MinGW\msys\\1.0\\bin\\"
    logsdir = winrsyncpath + "logs\\"
    capsdir = winrsyncpath + "caps\\"
    print(" This IS a windows 32 system, how exciting!")
elif sys.platform == 'linux2':
#elif sys.platform.startswith('linux'):
    print(" This is a linux system, great news! best choice!")
    logsdir = "/home/pragmo/frompigrow/logs/"
    capsdir = "/home/pragmo/frompigrow/caps/"
    OS = 'linux'
else:
    print(" i have no idea what this is?!")
    print sys.platform
    print("hack the system and see if it works as other OS's if you like")
    print("edit the code and add OS = 'linux' or 'win' after this bit of text")
#here. put the os = 'linux' / 'win' here if you want to ignore the auto detect

dht_log    = logsdir + 'dht22_log.txt'
self_log   = logsdir + 'selflog.txt'
switch_log = logsdir + 'switch_log.txt'
err_log    = logsdir + 'err_log.txt'

cap_files = []

def count_caps():
    cap_files = []
    for filefound in os.listdir(capsdir):
        if filefound.endswith(cap_type):
            cap_files.append(filefound)
    return cap_files

def download_caps():
    #note this ignores existing files
    if OS == 'linux':
        try:
            print("Copying files...   (this may time some time)")
            os.system("rsync --ignore-existing -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass+" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_cap_files+" "+capsdir)
            print("Files Grabbed")
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    elif OS == 'win':
        try:
            print("Copying files...")
            os.chdir(winrsyncpath)
            rsync_cmd = "rsync.exe --ignore-existing "+target_address+":"+target_cap_files + " caps"
            print rsync_cmd
            os.system(rsync_cmd)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

dht_log = "dht22_log.txt"
self_log = "selflog.txt"
err_log = "err_log.txt"
switch_log = "switch_log.txt"

def log_times():
    dht_ff = False
    sl_ff = False
    err_ff = False
    switch_ff = False
    for filefound in os.listdir(logsdir):
        if filefound == dht_log:
            dht_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == self_log:
            sl_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == err_log:
            err_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == switch_log:
            switch_ff = os.path.getmtime(logsdir+filefound)
    return dht_ff, sl_ff, err_ff, switch_ff

def download_logs():
    #note this overwrites existing files
 #get last edit times for files
    dht_ff, sl_ff, err_ff, switch_ff  = log_times()
 #downloads the files
    if OS == 'linux':
        try:
            print("Grabbing logs, this may take a short while...")
            cmd = "rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass
            cmd +=" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_log_path+" "+logsdir
            os.system(cmd)
            print("local logs updated as " + logsdir)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    elif OS == 'win':
        try:
            print("Grabbing logs, this may take a while.")
        except:
            print("dang, that fucked up")
            raise
    dht_fa, sl_fa, err_fa, switch_fa  = log_times()
    if dht_ff == dht_fa:
        message = " DHT log not updated, \n"
    else:
        message = " DHT log which is " + str(round(dht_fa - dht_ff)) + " sec newer \n"
    if sl_ff == sl_fa:
        message += " Self log not updated, \n"
    else:
        message += " Self log which is " + str(round(sl_fa - sl_ff)) + " min newer \n"
    if switch_ff == switch_fa:
        message += " Switch log not updated, \n"
    else:
        message += " Switch log which is " + str(round(switch_fa - switch_ff)) + " min newer \n"
    if err_ff == err_fa:
        message += " Error log not updated, \n"
    else:
        message += " Error log which is " + str(round(err_fa - err_ff)) + " min newer \n"
    return message

def load_dhtlog():
    dht_dates = []
    dht_temps = []
    dht_humids = []
    hours_to_show = 999999 #currently not used
    thetime = datetime.datetime.now()
    with open(dht_log, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Adding ' + str(len(logitem)) + ' readings from log.')
    oldest_allowed_date = thetime - datetime.timedelta(hours=hours_to_show)
    curr_line = len(logitem) - 1
    while curr_line >= 0:
        try:
            item = logitem[curr_line]
            item = item.split(">")
            date = item[2].split(".")
            date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            #if date < oldest_allowed_date:
            #    break
            hum  = float(item[1])
            temp = float(item[0])
            dht_humids.append(hum)
            dht_temps.append(temp)
            dht_dates.append(date)
            curr_line = curr_line - 1
        except:
            print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
            curr_line = curr_line - 1

    dht_humids.reverse()
    dht_temps.reverse()
    dht_dates.reverse()
    return dht_humids, dht_temps, dht_dates


class Pigrow(wx.Frame):
    def __init__(self, *args, **kw):
        super(Pigrow, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)
        font_big = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font_small = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading = wx.StaticText(self, label='Pigrow Control', pos=(130, 15))
        heading.SetFont(font_big)

     #menu bar
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()


        menu_seek = fileMenu.Append(wx.ID_ANY, 'Seek for Pi', 'Search the local network for a pi')
        menu_settings = fileMenu.Append(wx.ID_ANY, 'Pi settings', 'Edit and update pigrow config files')
        fileMenu.AppendSeparator()
        imp = wx.Menu()
        import_set = imp.Append(wx.ID_ANY, 'Import settings')
        import_dht = imp.Append(wx.ID_ANY, 'Import sensor log')
        import_swi = imp.Append(wx.ID_ANY, 'Import switch log')
        import_cap = imp.Append(wx.ID_ANY, 'Import caps folder')
        fileMenu.AppendMenu(wx.ID_ANY, 'I&mport', imp)
        menu_exit = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.Bind(wx.EVT_MENU, self.imp_dht, import_dht)
        self.Bind(wx.EVT_MENU, self.imp_caps, import_cap)
        self.Bind(wx.EVT_MENU, self.OnClose, menu_exit)
        downMenu = wx.Menu()
        menu_download = downMenu.Append(wx.ID_ANY, 'Download from Pi')
        self.Bind(wx.EVT_MENU, self.download, menu_download)
        downMenu.AppendSeparator()
        self.d_cap = downMenu.Append(wx.ID_ANY, 'Caps', 'Captured Images from pigrow camera', kind=wx.ITEM_CHECK)
        self.d_log = downMenu.Append(wx.ID_ANY, 'Logs', 'Pigrow Logs', kind=wx.ITEM_CHECK)
        self.d_gra = downMenu.Append(wx.ID_ANY, 'Graphs', 'Pigrow Graphs', kind=wx.ITEM_CHECK)
        self.d_con = downMenu.Append(wx.ID_ANY, 'Config', 'Pigrow Config', kind=wx.ITEM_CHECK)
        self.d_cap.Check()
        self.d_log.Check()
        self.d_con.Check()
        menubar.Append(downMenu, '&Download')
        visMenu = wx.Menu()
        self.v_cap = visMenu.Append(wx.ID_ANY, 'Most Recent cap', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_hourA = visMenu.Append(wx.ID_ANY, 'Last Hour Gif', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_dayA = visMenu.Append(wx.ID_ANY, 'Last Day Gif', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_cap = visMenu.Append(wx.ID_ANY, 'Self Graphs', 'Self log graphs', kind=wx.ITEM_RADIO)
        menubar.Append(visMenu, 'Show')

        self.SetMenuBar(menubar)

     #caps
        self.cap_len_text = wx.StaticText(self,  label='Files in caps ; ', pos=(25, 75))
        self.cap_ff_text = wx.StaticText(self, label='First file ; ', pos=(25, 100))
        self.cap_lf_text = wx.StaticText(self,  label='Last file  ; ', pos=(25, 125))
        cap_files = self.update_caps()

     #Opening the window
        self.SetSize((800, 600))
        self.SetTitle('Pigrow Control')
        self.Centre()
        self.Show(True)

    def imp_caps(self, e):
        openFileDialog = wx.FileDialog(self, "Select caps folder", "", "", "JPG files (*.jpg)|*.jpg", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        new_cap_path = openFileDialog.GetPath()
        print new_cap_path

    def imp_dht(self, e):
        openFileDialog = wx.FileDialog(self, "Select DHT Log file", "", "", "TXT files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...
        new_dht_log = openFileDialog.GetPath()

    def OnClose(self, e):
        print("Bye!")
        self.Close(True)

    def update_caps(self):
        cap_files = []
        for filefound in os.listdir(capsdir):
            if filefound.endswith(cap_type):
                cap_files.append(filefound)
        if len(cap_files) > 1:
            self.cap_len_text.SetLabel('Files in caps; ' + str(len(cap_files)))
            self.cap_ff_text.SetLabel('Files in caps; ' + str(cap_files[1]))
            self.cap_lf_text.SetLabel('Files in caps; ' + str(cap_files[-1]))
        else:
            self.cap_len_text.SetLabel('Caps folder is empty')
            self.cap_ff_text.SetLabel('')
        return cap_files

    def download(self, e):
        msg_text = "Found; "
        if self.d_log.IsChecked():
            message = download_logs()
            msg_text += message
        if self.d_gra.IsChecked():
            #download_graphs()
            print("graph download not enabled yet")
        if self.d_con.IsChecked():
            print("download config not enabled yet")
        if self.d_cap.IsChecked():
            cap_files = self.update_caps()
            startnum = len(cap_files)
            num = download_caps()
            cap_files = self.update_caps()
            capsnow = len(cap_files)
            capsdown = startnum - capsnow
            msg_text += str(capsdown) + " images. "
        if msg_text == "Found; ":
            msg_text = "Nothing selected for download"
        wx.MessageBox(msg_text, 'Files Downloaded', wx.OK | wx.ICON_INFORMATION)





def main():
    app = wx.App()
    Pigrow(None)
    app.MainLoop()


if __name__ == '__main__':
    main()
