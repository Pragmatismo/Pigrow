import os, sys
import datetime
import wx

capsdir = 'none'
graphdir = 'none'
outfile = '../guitest.mp4'

class Make_TL(wx.Frame):
    def __init__(self, *args, **kw):
        super(Make_TL, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):
        global capsdir, graphdir, outfile
        capsdir = '/home/pragmo/frompigrow/Flower/caps/'
        if capsdir == 'none':
            capsdir, capset, cap_type = self.select_caps_folder()
        else:
            firstfile = os.listdir(capsdir)[0]
            capset   = firstfile.split(".")[0][0:-10]  # Used to select set if more than one are present
            cap_type = firstfile.split('.')[1]
        graphdir = capsdir[:-5] #this is a hacky way of taking 'caps/' out of the filepath
        print graphdir
        graphdir += "graph/"
        print graphdir
        cap_files = self.count_caps(capsdir, cap_type)
        print("We've got " + str(len(cap_files)))
      #Big Pictures
        self.fpic_text = wx.StaticText(self,  label='first pic', pos=(10, 15))
        self.lpic_text = wx.StaticText(self,  label='last pic', pos=(530, 15))
        self.first_pic = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(500, 500), pos=(10, 50))
        self.last_pic = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(500, 500), pos=(520, 50))
      #graph
        self.cap_thumb = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(300, 300), pos=(500, 600))
      #lower left info
        wx.StaticText(self,  label='Caps Folder', pos=(25, 610))
        self.capsfolder_box = wx.TextCtrl(self, pos=(200, 610), size=(250, 30))
        self.capsfolder_box.SetValue(str(capsdir))
        wx.StaticText(self,  label='Outfile', pos=(25, 650))
        self.outfile_box = wx.TextCtrl(self, pos=(200, 650), size=(250, 30))
        self.outfile_box.SetValue(str(outfile))
        wx.StaticText(self,  label='FPS (in)', pos=(25, 690))
        self.fps_in_box = wx.TextCtrl(self, pos=(200, 690), size=(100, 30))
        self.fps_in_box.SetValue("10")
        wx.StaticText(self,  label='FPS (out)', pos=(25, 730))
        self.fps_out_box = wx.TextCtrl(self, pos=(200, 730), size=(100, 30))
        self.fps_out_box.SetValue("10")
        wx.StaticText(self,  label='Dark Threashold', pos=(25, 770))
        self.darksize_box = wx.TextCtrl(self, pos=(200, 770), size=(100, 30))
        self.darksize_box.SetValue("10000")
        wx.StaticText(self,  label='Limit to last', pos=(25, 810))
        date_opts = ['none', 'day', 'week', 'month']
        self.datecheck_combo = wx.ComboBox(self, choices = date_opts, pos=(200,810), size=(125, 30))
        self.datecheck_combo.Bind(wx.EVT_COMBOBOX, self.datecheck_combo_go)
        self.datecheck_box = wx.TextCtrl(self, pos=(330, 810), size=(100, 30))
        self.datecheck_box.SetValue("1")
        self.datecheck_box.Disable()
        wx.StaticText(self,  label='Timeskip', pos=(25, 850))
        self.timeskip_box = wx.TextCtrl(self, pos=(200, 850), size=(100, 30))
        self.timeskip_box.SetValue("0")


      #Buttons
        self.btn_1 = wx.Button(self, label='1', pos=(50, 550))
        self.btn_2 = wx.Button(self, label=' 2', pos=(400, 550))
        self.btn_3 = wx.Button(self, label='3', pos=(550, 550))
        self.btn_4 = wx.Button(self, label='4', pos=(900, 550))
        self.btn_1.Bind(wx.EVT_BUTTON, self.btn_1_click)
        self.btn_2.Bind(wx.EVT_BUTTON, self.btn_2_click)
        self.btn_3.Bind(wx.EVT_BUTTON, self.btn_3_click)
        self.btn_4.Bind(wx.EVT_BUTTON, self.btn_4_click)
        self.btn_ren = wx.Button(self, label=' Render ', pos=(250, 600), size=(50, 50))
        self.btn_ren.Bind(wx.EVT_BUTTON, self.btn_ren_click)

        self.updateUI(capsdir, cap_files)
        self.SetSize((1030, 900))
        self.SetTitle('Pigrow Control')
        self.Centre()
        self.Show(True)

    def datecheck_combo_go(self, e):
        if self.datecheck_combo.GetValue() == 'none':
            print("Want's to see all of it, no datecheck")
            self.datecheck_box.Disable()
        elif self.datecheck_combo.GetValue() == 'day':
            print("Want's to see only a number of days,")
            self.datecheck_box.Enable()
        elif self.datecheck_combo.GetValue() == 'week':
            print("Want's to see only a number of weeks,")
            self.datecheck_box.Enable()
        elif self.datecheck_combo.GetValue() == 'month':
            print("Want's to see only a number of months,")
            self.datecheck_box.Enable()


    def scale_pic(self, pic, hnum):
        pic_hight = pic.GetHeight()
        if pic_hight > hnum:
            pic_width = pic.GetWidth()
            new_hight = hnum
            sizeratio = (pic_hight / new_hight)
            new_width = (pic_width / sizeratio)
            scale_pic = pic.Scale(new_width, new_hight)
            return scale_pic

    def updateUI(self, capsdir, cap_files):
        print("---UPDATING USER INTERFACE ---")
        fframe = 0
        lframe = len(cap_files) - 1
        last_pic  = str(capsdir + cap_files[lframe])
        first_pic = str(capsdir + cap_files[fframe])
        if os.path.exists(last_pic):
            last_pic = wx.Image(last_pic, wx.BITMAP_TYPE_ANY)
            last_pic = self.scale_pic(last_pic, 500)
            self.last_pic.SetBitmap(wx.BitmapFromImage(last_pic))
            lpicdate = self.date_from_fn(cap_files[lframe])
            self.lpic_text.SetLabel('Frame ' + str(lframe) + '  -  ' + str(lpicdate))
        else:
            self.last_pic.SetBitmap(wx.EmptyBitmap(10,10))
            self.fpic_text.SetLabel('end')
        if os.path.exists(first_pic):
            first_pic = wx.Image(first_pic, wx.BITMAP_TYPE_ANY)
            first_pic = self.scale_pic(first_pic, 500)
            fpicdate = self.date_from_fn(cap_files[fframe])
            self.fpic_text.SetLabel('Frame ' + str(fframe) + '  -  ' + str(fpicdate))
            self.first_pic.SetBitmap(wx.BitmapFromImage(first_pic))
        else:
            self.first_pic.SetBitmap(wx.EmptyBitmap(10,10))
            self.fpic_text.SetLabel('start')
     #Cap graph
        cap_size_graph = self.graph_caps(cap_files, graphdir)
        scale_size_graph = first_pic = self.scale_pic(cap_size_graph, 300)
        self.cap_thumb.SetBitmap(wx.BitmapFromImage(scale_size_graph))

    def date_from_fn(self, thefilename):
        fdate = float(thefilename.split(".")[0].split("_")[-1])
        fdate = datetime.datetime.utcfromtimestamp(fdate)
        return fdate

    def btn_ren_click(self, e):
        print("old make timelapse menu option")
        cmd = '../visualisation/timelapse_assemble.py caps=' + capsdir + " of=" + graphdir
        cmd += 'guimade.mp4 ow=r dc=day3'
        #cmd += 'guimade.gif ow=r dc=hour1'
        print cmd
        os.system(cmd)
        playcmd = 'vlc ' + graphdir + 'guimade.mp4'
        print playcmd
        os.system(playcmd)

    def btn_1_click(self, e):
        print("Button pressed")

    def btn_2_click(self, e):
        print("Button pressed")

    def btn_3_click(self, e):
        print("Button pressed")

    def btn_4_click(self, e):
        print("Button pressed")

    def select_caps_folder(self):
        openFileDialog = wx.FileDialog(self, "Select caps folder", "", "", "JPG files (*.jpg)|*.jpg", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return 'none'
        new_cap_path = openFileDialog.GetPath()

        capsdir = os.path.split(new_cap_path)
        capset   = capsdir[1].split(".")[0][0:-10]  # Used to select set if more than one are present
        cap_type = capsdir[1].split('.')[1]
        capsdir = capsdir[0] + '/'
        print(" Selected " + capsdir + " with capset; " + capset + " filetype; " + cap_type)
        return capsdir, capset, cap_type

    def count_caps(self, capsdir, cap_type):
        cap_files = []
        for filefound in os.listdir(capsdir):
            if filefound.endswith(cap_type):
                cap_files.append(filefound)
        cap_files.sort()
        return cap_files

    def graph_caps(self, cap_files, graphdir):
        OS = "linux"
        if len(cap_files) > 1:
            print("make caps graph")
            if OS == "linux":
                print("Yay linux")
                os.system("../visualisation/caps_graph.py caps="+capsdir+" out="+graphdir)
            elif OS == 'win':
                print("oh, windows, i prefer linux but no worries...")
                os.system("python ../visualisation/caps_graph.py caps="+capsdir+" out="+graphdir)
        else:
            print("skipping graphing caps - disabled or no caps to make graphs with")
        if os.path.exists(graphdir+'caps_filesize_graph.png'):
            cap_size_graph_path = wx.Image(graphdir+'caps_filesize_graph.png', wx.BITMAP_TYPE_ANY)
            return cap_size_graph_path
        else:
            print("NOT ENOUGH CAPS GRAPH SO USING BLANK THUMB")
            blankimg = wx.EmptyImage(width=100, height=100, clear=True)
            return blankimg







def main():
    app = wx.App()
    Make_TL(None)
    app.MainLoop()


if __name__ == '__main__':
    main()
