#!/usr/bin/python

#
#   WORK IN PROGRESS
#
# Classes already created;
#    pi_link_pnl        - top-left connection box with ip, username, pass
#    view_pnl           - allows you to select which options to view
#    cron_list_pnl      - shows the 3 cron type lists on the right of the window
#    cron_info_pnl      - shows the buttons that control the cron_list_pnl
#    cron_job_dialog    - dialogue box for edit cron job
#
#
#
#

print("")
print(" THIS IS A WORK IN PROGRESS SCRIPT (ain't they all)")
print("     At the moment it does almost nothing at all ")
print("     beside define some dialog boxes and pannels")
print("  it's fuckin' sweet as tho, aye?")
print("")

try:
    import wx
    import wx.lib.scrolledpanel
except:
    print(" You don't have WX Python installed, this makes the gui")
    print(" google 'installing wx python' for your operating system")
    print("on ubuntu try the command;")
    print("   sudo apt install python-wxgtk3.0 ")
    sys.exit(1)
try:
    import paramiko
except:
    print("  You don't have paramiko installed, this is what connects to the pi")
    print(" google 'installing paramiko python' for your operating system")
    print(" on ubuntu;")
    print(" use the command ' pip install paramiko ' to install.")
    sys.exit(1)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

class system_ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        wx.StaticText(self,  label='System Config Menu', pos=(25, 10))
        self.read_system_btn = wx.Button(self, label='Read System Info', pos=(10, 70), size=(175, 30))
        self.read_system_btn.Bind(wx.EVT_BUTTON, self.read_system_click)

    def read_system_click(self, e):
        system_info_pnl.sys_hdd_info.SetLabel("lol not even tried to check it")

class system_info_pnl(wx.Panel):
    #
    #  This displays the system info
    # controlled by the system_ctrl_pnl
    #
    def __init__( self, parent ):
        #find size
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )
        wx.StaticText(self,  label='System infiormation;', pos=(5, 10))
        system_info_pnl.sys_hdd_info = wx.StaticText(self,  label='Disk Space;', pos=(25, 60))

class cron_info_pnl(wx.Panel):
    def __init__( self, parent ):
        win_height = parent.GetSize()[1]
        height_of_pannels_above = 230
        space_left = win_height - height_of_pannels_above

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, height_of_pannels_above), size = wx.Size(285, space_left), style = wx.TAB_TRAVERSAL )
        wx.StaticText(self,  label='Cron Config Menu', pos=(25, 10))
        self.read_cron_btn = wx.Button(self, label='Read Crontab', pos=(10, 40), size=(175, 30))
        self.read_cron_btn.Bind(wx.EVT_BUTTON, self.read_cron_click)
        self.new_cron_btn = wx.Button(self, label='New cron job', pos=(10, 80), size=(175, 30))
        self.new_cron_btn.Bind(wx.EVT_BUTTON, self.new_cron_click)
        self.update_cron_btn = wx.Button(self, label='Update Cron', pos=(10, 120), size=(175, 30))
        self.update_cron_btn.Bind(wx.EVT_BUTTON, self.update_cron_click)
        self.SetBackgroundColour('sea green') #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS

        bSizer = wx.BoxSizer(wx.VERTICAL)
        bSizer.Add(self.read_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.new_cron_btn, 0, wx.ALL, 5)
        bSizer.Add(self.update_cron_btn, 0, wx.ALL, 5)
        self.SetSizer(bSizer)

    def update_cron_click(self, e):
        #make a text file of all the cron jobs
        cron_text = ''
        startup_num = cron_list_pnl.startup_cron.GetItemCount()
        for num in range(0, startup_num):
            cron_line = ''
            if cron_list_pnl.startup_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += '@reboot ' + cron_list_pnl.startup_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.startup_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        repeat_num = cron_list_pnl.repeat_cron.GetItemCount()
        for num in range(0, repeat_num):
            cron_line = ''
            if cron_list_pnl.repeat_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.repeat_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.repeat_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        onetime_num = cron_list_pnl.timed_cron.GetItemCount()
        for num in range(0, onetime_num):
            cron_line = ''
            if cron_list_pnl.timed_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += cron_list_pnl.timed_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += ' ' + cron_list_pnl.timed_cron.GetItemText(num, 5) # cron_comment
            cron_text += cron_line + '\n'
        # ask the user if they're sure
        msg_text = "Update cron to; \n\n" + cron_text
        mbox = wx.MessageDialog(None, msg_text, "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        if sure == wx.ID_YES:
            print "Updating remote cron"
            # save cron text onto pigrow as text file then import into cron
            sftp = ssh.open_sftp()
            try:
                tempfolder = '/home/pi/Pigrow/temp'
                sftp.mkdir(tempfolder)
            except IOError:
                pass
            f = sftp.open(tempfolder + '/remotecron.txt', 'w')
            f.write(cron_text)
            f.close()
            try:
                stdin, stdout, stderr = ssh.exec_command("crontab " + tempfolder + '/remotecron.txt')
                responce = stdout.read()
                error = stderr.read()
                print responce, error
            except Exception as e:
                print("this ain't right, it just ain't right! " + str(e))
        else:
            print("Updating cron cancelled")
        mbox.Destroy()
        #refresh cron list
        self.read_cron_click("event")


    def read_cron_click(self, event):
        #reads pi's crontab then puts jobs in correct table
        try:
            stdin, stdout, stderr = ssh.exec_command("crontab -l")
            cron_text = stdout.read().split('\n')
        except Exception as e:
            print("oh - that didn't work! " + str(e))
        #select instance of list to use
        startup_list_instance = cron_list_pnl.startup_cron
        repeat_list_instance = cron_list_pnl.repeat_cron
        onetime_list_instance = cron_list_pnl.timed_cron
        #clear lists of prior data
        startup_list_instance.DeleteAllItems()
        repeat_list_instance.DeleteAllItems()
        onetime_list_instance.DeleteAllItems()
        #sort cron info into lists
        line_number = 0

        for cron_line in cron_text:
            line_number = line_number + 1
            real_job = True
            if len(cron_line) > 5:
                cron_line.strip()
                #determine if enabled or disabled with hash
                if cron_line[0] == '#':
                    job_enabled = False
                    cron_line = cron_line[1:].strip(' ')
                else:
                    job_enabled = True
                # sort for job type, split into timing string and cmd sting
                if cron_line.find('@reboot') > -1:
                    cron_jobtype = 'reboot'
                    timing_string = '@reboot'
                    cmd_string = cron_line[8:]
                else:
                    split_cron = cron_line.split(' ')
                    timing_string = ''
                    for star in split_cron[0:5]:
                        if not star.find('*') > -1 and not star.isdigit():
                            real_job = False
                        timing_string += star + ' '
                    cmd_string = ''

                    for cmd in split_cron[5:]:
                        cmd_string += cmd + ' '
                    if timing_string.find('/') > -1:
                        cron_jobtype = 'repeating'
                    else:
                        cron_jobtype = 'one time'
                # split cmd_string into cmd_string and comment
                cron_comment_pos = cmd_string.find('#')
                if cron_comment_pos > -1:
                    cron_comment = cmd_string[cron_comment_pos:].strip(' ')
                    cmd_string = cmd_string[:cron_comment_pos].strip(' ')
                else:
                    cron_comment = ''
                # split cmd_string into task and extra args
                cron_task = cmd_string.split(' ')[0]
                cron_extra_args = ''
                for arg in cmd_string.split(' ')[1:]:
                    cron_extra_args += arg + ' '
                if real_job == True and not cmd_string == '':
                    print job_enabled, timing_string, cron_jobtype, cron_task, cron_extra_args, cron_comment
                    if cron_jobtype == 'reboot':
                        self.add_to_startup_list(line_number, job_enabled, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'one time':
                        self.add_to_onetime_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
                    elif cron_jobtype == 'repeating':
                        self.add_to_repeat_list(line_number, job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def test_if_script_running(self, script):
        stdin, stdout, stderr = ssh.exec_command("pidof -x " + str(script))
        script_text = stdout.read().strip()
        #error_text = stderr.read().strip()
        if script_text == '':
            return False
        else:
            #print 'pid of = ' + str(script_text)
            return True

    def add_to_startup_list(self, line_number, job_enabled, cron_task, cron_extra_args='', cron_comment=''):
        is_running = self.test_if_script_running(cron_task)
        cron_list_pnl.startup_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.startup_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.startup_cron.SetStringItem(0, 2, str(is_running))   #should test if script it currently running on pi
        cron_list_pnl.startup_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.startup_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.startup_cron.SetStringItem(0, 5, cron_comment)

    def add_to_repeat_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.repeat_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.repeat_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.repeat_cron.SetStringItem(0, 2, timing_string)   #should test if script it currently running on pi
        cron_list_pnl.repeat_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.repeat_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.repeat_cron.SetStringItem(0, 5, cron_comment)

    def add_to_onetime_list(self, line_number, job_enabled, timing_string, cron_task, cron_extra_args='', cron_comment=''):
        cron_list_pnl.timed_cron.InsertStringItem(0, str(line_number))
        cron_list_pnl.timed_cron.SetStringItem(0, 1, str(job_enabled))
        cron_list_pnl.timed_cron.SetStringItem(0, 2, timing_string)   #should test if script it currently running on pi
        cron_list_pnl.timed_cron.SetStringItem(0, 3, cron_task)
        cron_list_pnl.timed_cron.SetStringItem(0, 4, cron_extra_args)
        cron_list_pnl.timed_cron.SetStringItem(0, 5, cron_comment)

    def make_repeating_cron_timestring(self, repeat, repeat_num):
        #assembles timing sting for cron
        # min (0 - 59) | hour (0 - 23) | day of month (1-31) | month (1 - 12) | day of week (0 - 6) (Sunday=0)
        if repeat == 'min':
            if int(repeat_num) in range(0,59):
                cron_time_string = '*/' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string = '*'
        if repeat == 'hour':
            if int(repeat_num) in range(0,23):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'day':
            if int(repeat_num) in range(1,31):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'month':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        if repeat == 'dow':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        return cron_time_string

    def make_onetime_cron_timestring(self, job_min, job_hour, job_day, job_month, job_dow):
        # timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        if job_min.isdigit():
            timing_string = str(job_min)
        else:
            timing_string = '*'
        if job_hour.isdigit():
            timing_string += ' ' + str(job_hour)
        else:
            timing_string += ' *'
        if job_day.isdigit():
            timing_string += ' ' + str(job_day)
        else:
            timing_string += ' *'
        if job_month.isdigit():
            timing_string += ' ' + str(job_month)
        else:
            timing_string += ' *'
        if job_dow.isdigit():
            timing_string += ' ' + str(job_dow)
        else:
            timing_string += ' *'
        return timing_string

    def new_cron_click(self, e):
        #define blank fields and defaults for dialogue box to read
        cron_info_pnl.cron_path_toedit = '/home/pi/Pigrow/scripts/cron/'
        cron_info_pnl.cron_task_toedit = 'input cron task here'
        cron_info_pnl.cron_args_toedit = ''
        cron_info_pnl.cron_comment_toedit = ''
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '30'
        cron_info_pnl.cron_hour_toedit = '8'
        cron_info_pnl.cron_day_toedit = ''
        cron_info_pnl.cron_month_toedit = ''
        cron_info_pnl.cron_dow_toedit = ''
        cron_info_pnl.cron_enabled_toedit = True
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = self.make_onetime_cron_timestring(job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None or not job_script == '':
            cron_task = job_path + job_script
            if cron_jobtype == 'startup':
                self.add_to_startup_list('new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                self.add_to_onetime_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                self.add_to_repeat_list('new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

class cron_list_pnl(wx.Panel):
    #
    #  This displays the three different cron type lists on the big-pannel
    #  double click to edit one of the jobs (not yet written)
    #  ohter control buttons found on the cron control pannel
    #

    #none of these resize or anything at the moment
    #consider putting into a sizer or autosizing with math
    #--to screen size tho not to size of cronlist that'd be super messy...
    class startup_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,10), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Active')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 100)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 75)
            self.SetColumnWidth(3, 650)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    class repeating_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,245), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'every')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 75)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    class other_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,530), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Time')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.InsertColumn(5, 'comment')
            self.SetColumnWidth(0, 75)
            self.SetColumnWidth(1, 75)
            self.SetColumnWidth(2, 100)
            self.SetColumnWidth(3, 500)
            self.SetColumnWidth(4, 500)
            self.SetColumnWidth(5, -1)

    def __init__( self, parent ):
        #find size
        win_height = parent.GetSize()[1]
        win_width = parent.GetSize()[0]
        w_space_left = win_width - 285

        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size(w_space_left , 800), style = wx.TAB_TRAVERSAL )

        wx.StaticText(self,  label='Cron start up;', pos=(5, 10))
        cron_list_pnl.startup_cron = self.startup_cron_list(self, 1, pos=(5, 40), size=(w_space_left-10, 200))
        cron_list_pnl.startup_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_startup)
        wx.StaticText(self,  label='Repeating Jobs;', pos=(5,245))
        cron_list_pnl.repeat_cron = self.repeating_cron_list(self, 1, pos=(5, 280), size=(w_space_left-10, 200))
        cron_list_pnl.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        wx.StaticText(self,  label='One time triggers;', pos=(5,500))
        cron_list_pnl.timed_cron = self.other_cron_list(self, 1, pos=(5, 530), size=(w_space_left-10, 200))
        cron_list_pnl.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)

    # TESTING CODE WHILE SCRIPT WRITING IS IN PROGRESS
        self.SetBackgroundColour('sea green')  ###THIS IS JUST TO TEST SIZE REMOVE TO STOP THE UGLY

    def onDoubleClick_timed(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.timed_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.timed_cron.GetItem(index, 2).GetText()
        cron_stars = timing_string.split(' ')
        cron_min = cron_stars[0]
        cron_hour = cron_stars[1]
        cron_day = cron_stars[2]
        cron_month = cron_stars[3]
        cron_dow = cron_stars[4]

        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.timed_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'one time'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = cron_min
        cron_info_pnl.cron_hour_toedit = cron_hour
        cron_info_pnl.cron_day_toedit = cron_day
        cron_info_pnl.cron_month_toedit = cron_month
        cron_info_pnl.cron_dow_toedit = cron_dow
        if str(cron_list_pnl.timed_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = cron_info_pnl.make_onetime_cron_timestring(MainApp.cron_info_pannel, job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.timed_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_repeat(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.repeat_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        timing_string = cron_list_pnl.repeat_cron.GetItem(index, 2).GetText()
        cron_stars = timing_string.split(' ')
        if not timing_string == 'fail':
            if '/' in cron_stars[0]:
                cron_rep = 'min'
                cron_num = cron_stars[0].split('/')[-1]
            elif '/' in cron_stars[1]:
                cron_rep = 'hour'
                cron_num = cron_stars[1].split('/')[-1]
            elif '/' in cron_stars[2]:
                cron_rep = 'day'
                cron_num = cron_stars[2].split('/')[-1]
            elif '/' in cron_stars[3]:
                cron_rep = 'month'
                cron_num = cron_stars[3].split('/')[-1]
            elif '/' in cron_stars[4]:
                cron_rep = 'dow'
                cron_num = cron_stars[4].split('/')[-1]
        else:
            cron_rep = 'min'
            cron_num = '5'


        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.repeat_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'repeating'
        cron_info_pnl.cron_everystr_toedit = cron_rep
        cron_info_pnl.cron_everynum_toedit = cron_num
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        if str(cron_list_pnl.repeat_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = cron_info_pnl.make_repeating_cron_timestring(MainApp.cron_info_pannel, job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.repeat_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)

    def onDoubleClick_startup(self, e):
        index =  e.GetIndex()
        #define blank fields and defaults for dialogue box to read
        cmd_path = cron_list_pnl.startup_cron.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        cron_info_pnl.cron_path_toedit = str(cmd_path)
        cron_info_pnl.cron_task_toedit = str(cmd)
        cron_info_pnl.cron_args_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 4).GetText())
        cron_info_pnl.cron_comment_toedit = str(cron_list_pnl.startup_cron.GetItem(index, 5).GetText())
        cron_info_pnl.cron_type_toedit = 'startup'
        cron_info_pnl.cron_everystr_toedit = 'min'
        cron_info_pnl.cron_everynum_toedit = '5'
        cron_info_pnl.cron_min_toedit = '0'
        cron_info_pnl.cron_hour_toedit = '8'
        if str(cron_list_pnl.startup_cron.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        cron_info_pnl.cron_enabled_toedit = enabled
        #make dialogue box
        cron_dbox = cron_job_dialog(None, title='Cron Job Editor')
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        if not job_path == None:
            cron_task = job_path + job_script
        else:
            cron_task = None
        cron_extra_args = cron_dbox.job_args
        cron_comment = cron_dbox.job_comment
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        # make timing_string from min:hour or repeat + repeat_num
        if cron_jobtype == 'repeating':
            timing_string = self.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = str(job_min) + ' ' + str(job_hour) + ' * * *'
        # sort into the correct table
        if not job_script == None:
            # remove entry
            cron_list_pnl.startup_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                cron_info_pnl.add_to_startup_list(MainApp.cron_info_pannel, 'new', job_enabled, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'one time':
                cron_info_pnl.add_to_onetime_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)
            elif cron_jobtype == 'repeating':
                cron_info_pnl.add_to_repeat_list(MainApp.cron_info_pannel, 'new', job_enabled, timing_string, cron_task, cron_extra_args, cron_comment)


class cron_job_dialog(wx.Dialog):
    #Dialog box for creating or editing cron scripts
    #   takes ten variables from cron_info_pnl
    #   which need to be set before it's called
    #   then it creates ten outgonig variables to
    #   be grabbed after it closes to be stored in
    #   whatever table they belong in
    #    - cat_script displays text of currently selected script
    #            this is useful for sh scripts with no -h option.
    #    - get_cronable_scripts(script_path) takes path and
    #            returns a list of py or sh scripts in that folder.
    #    - get_help_text(script_to_ask) which takes script location and
    #            returns the helpfile text from the -h output of the script.
    def __init__(self, *args, **kw):
        super(cron_job_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((750, 300))
        self.SetTitle("Cron Job Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self):
        #these need to be set before the dialog is created
        cron_path = cron_info_pnl.cron_path_toedit
        cron_task = cron_info_pnl.cron_task_toedit
        cron_args = cron_info_pnl.cron_args_toedit
        cron_comment = cron_info_pnl.cron_comment_toedit
        cron_type = cron_info_pnl.cron_type_toedit
        cron_everystr = cron_info_pnl.cron_everystr_toedit
        cron_everynum = cron_info_pnl.cron_everynum_toedit
        cron_enabled = cron_info_pnl.cron_enabled_toedit
        cron_min = cron_info_pnl.cron_min_toedit
        cron_hour = cron_info_pnl.cron_hour_toedit
        cron_day = cron_info_pnl.cron_day_toedit
        cron_month = cron_info_pnl.cron_month_toedit
        cron_dow = cron_info_pnl.cron_dow_toedit
        #draw the pannel
         ## universal controls
        pnl = wx.Panel(self)
        wx.StaticText(self,  label='Cron job editor', pos=(20, 10))
        cron_type_opts = ['startup', 'repeating', 'one time']
        wx.StaticText(self,  label='cron type;', pos=(165, 10))
        self.cron_type_combo = wx.ComboBox(self, choices = cron_type_opts, pos=(260,10), size=(125, 25))
        self.cron_type_combo.Bind(wx.EVT_COMBOBOX, self.cron_type_combo_go)
        wx.StaticText(self,  label='path;', pos=(10, 50))
        cron_path_opts = ['/home/pi/Pigrow/scripts/cron/', '/home/pi/Pigrow/scripts/autorun/', '/home/pi/Pigrow/scripts/switches/']
        self.cron_path_combo = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER, choices = cron_path_opts, pos=(100,45), size=(525, 30))
        self.cron_path_combo.Bind(wx.EVT_TEXT_ENTER, self.cron_path_combo_go)
        self.cron_path_combo.Bind(wx.EVT_COMBOBOX, self.cron_path_combo_go)
        show_cat_butt = wx.Button(self, label='view script', pos=(625, 75))
        show_cat_butt.Bind(wx.EVT_BUTTON, self.cat_script)
        wx.StaticText(self,  label='Extra args;', pos=(10, 110))
        self.cron_args_tc = wx.TextCtrl(self, pos=(100, 110), size=(525, 25))
        show_help_butt = wx.Button(self, label='show help', pos=(625, 110))
        show_help_butt.Bind(wx.EVT_BUTTON, self.show_help)
        wx.StaticText(self,  label='comment;', pos=(10, 140))
        self.cron_comment_tc = wx.TextCtrl(self, pos=(100, 140), size=(525, 25))
        self.cron_enabled_cb = wx.CheckBox(self,  label='Enabled', pos=(400, 190))
        ### set universal controls data...
        self.cron_type_combo.SetValue(cron_type)
        self.cron_path_combo.SetValue(cron_path)
        self.cron_args_tc.SetValue(cron_args)
        self.cron_comment_tc.SetValue(cron_comment)
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb = wx.ComboBox(self, choices = cron_script_opts, pos=(25,80), size=(600, 25))
        self.cron_script_cb.SetValue(cron_task)
        self.cron_enabled_cb.SetValue(cron_enabled)
        # draw and hide optional option controlls
        ## for repeating cron jobs
        self.cron_rep_every = wx.StaticText(self,  label='Every ', pos=(60, 190))
        self.cron_every_num_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25))  #box for number, name num only range set by repeat_opt
        self.cron_every_num_tc.Bind(wx.EVT_CHAR, self.onChar)
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.cron_repeat_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, pos=(170,190), size=(100, 30))
        self.cron_rep_every.Hide()
        self.cron_every_num_tc.Hide()
        self.cron_repeat_opts_cb.Hide()
        self.cron_repeat_opts_cb.SetValue(cron_everystr)
        self.cron_every_num_tc.SetValue(cron_everynum)
        ## for one time cron jobs
        self.cron_switch = wx.StaticText(self,  label='Time; ', pos=(60, 190))
        self.cron_switch2 = wx.StaticText(self,  label='[min : hour : day : month : day of the week]', pos=(110, 220))
        self.cron_timed_min_tc = wx.TextCtrl(self, pos=(115, 190), size=(40, 25)) #limit to 0-23
        self.cron_timed_min_tc.SetValue(cron_min)
        self.cron_timed_min_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_hour_tc = wx.TextCtrl(self, pos=(160, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_hour_tc.SetValue(cron_hour)
        self.cron_timed_hour_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_day_tc = wx.TextCtrl(self, pos=(205, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_day_tc.SetValue(cron_day)
        self.cron_timed_day_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_month_tc = wx.TextCtrl(self, pos=(250, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_month_tc.SetValue(cron_month)
        self.cron_timed_month_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_dow_tc = wx.TextCtrl(self, pos=(295, 190), size=(40, 25)) #limit to 0-59
        self.cron_timed_dow_tc.SetValue(cron_dow)
        self.cron_timed_dow_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_switch.Hide()
        self.cron_switch2.Hide()
        self.cron_timed_min_tc.Hide()
        self.cron_timed_hour_tc.Hide()
        self.cron_timed_day_tc.Hide()
        self.cron_timed_month_tc.Hide()
        self.cron_timed_dow_tc.Hide()
        self.set_control_visi() #set's the visibility of optional controls
        #Buttom Row of Buttons
        okButton = wx.Button(self, label='Ok', pos=(200, 250))
        closeButton = wx.Button(self, label='Cancel', pos=(300, 250))
        okButton.Bind(wx.EVT_BUTTON, self.do_upload)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def onChar(self, event):
        #this inhibits any non-numeric keys
        key = event.GetKeyCode()
        try: character = chr(key)
        except ValueError: character = "" # arrow keys will throw this error
        acceptable_characters = "1234567890"
        if character in acceptable_characters or key == 13 or key == 314 or key == 316 or key == 8 or key == 127: # 13 = enter, 314 & 316 = arrows, 8 = backspace, 127 = del
            event.Skip()
            return
        else:
            return False

    def cat_script(self, e):
        #opens an ssh pipe and runs a cat command to get the text of the script
        target_ip = pi_link_pnl.target_ip
        target_user = pi_link_pnl.target_user
        target_pass = pi_link_pnl.target_pass
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        script_to_ask = script_path + script_name
        try:
        #    ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
            print "Connected to " + target_ip
            print("running; cat " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command("cat " + str(script_to_ask))
            script_text = stdout.read().strip()
            error_text = stderr.read().strip()
            if not error_text == '':
                msg_text =  'Error reading script \n\n'
                msg_text += str(error_text)
            else:
                msg_text = script_to_ask + '\n\n'
                msg_text += str(script_text)
            wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            print("oh bother, this seems wrong... " + str(e))

    def get_cronable_scripts(self, script_path):
        #this opens an ssh channel and reads the files in the path provided
        #then creates a list of all .py and .sh scripts in that folder
        cron_opts = []
        try:
            print("reading " + str(script_path))
            stdin, stdout, stderr = ssh.exec_command("ls " + str(script_path))
            cron_dir_list = stdout.read().split('\n')
            for filename in cron_dir_list:
                if filename.endswith("py") or filename.endswith('sh'):
                    cron_opts.append(filename)
        except Exception as e:
            print("aggghhhhh cap'ain something ain't right! " + str(e))
        return cron_opts
    def cron_path_combo_go(self, e):
        cron_path = self.cron_path_combo.GetValue()
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb.Clear()
        for x in cron_script_opts:
            self.cron_script_cb.Append(x)
    def cron_type_combo_go(self, e):
        self.set_control_visi()
    def set_control_visi(self):
        #checks which type of cron job is set in combobox and shows or hides
        #which ever UI elemetns are required - doesn't lose or change the data.
        cron_type = self.cron_type_combo.GetValue()
        if cron_type == 'one time':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Show()
            self.cron_switch2.Show()
            self.cron_timed_min_tc.Show()
            self.cron_timed_hour_tc.Show()
            self.cron_timed_day_tc.Show()
            self.cron_timed_month_tc.Show()
            self.cron_timed_dow_tc.Show()
        elif cron_type == 'repeating':
            self.cron_rep_every.Show()
            self.cron_every_num_tc.Show()
            self.cron_repeat_opts_cb.Show()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
        elif cron_type == 'startup':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.cron_switch.Hide()
            self.cron_switch2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
    def get_help_text(self, script_to_ask):
        #open an ssh pipe and runs the script with a -h argument
        #
        #WARNING
        #       If the script doesn't support -h args then it'll just run it
        #       this can cause switches to throw, photos to be taken or etc
        if script_to_ask.endswith('sh'):
            return ("Sorry, .sh files don't support help arguments, try viewing it instead.")
        try:
            print("reading " + str(script_to_ask))
            stdin, stdout, stderr = ssh.exec_command(str(script_to_ask) + " -h")
            helpfile = stdout.read().strip()
        except Exception as e:
            print("sheee-it something ain't right! " + str(e))
        return helpfile
    def show_help(self, e):
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        helpfile = self.get_help_text(str(script_path + script_name))
        msg_text =  script_name + ' \n \n'
        msg_text += str(helpfile)
        wx.MessageBox(msg_text, 'Info', wx.OK | wx.ICON_INFORMATION)
    def do_upload(self, e):
        #get data from boxes
        #   these are the exit variables, they're only set when ok is pushed
        #   this is to stop any dirty old data mixing in with the correct stuff
        self.job_type = self.cron_type_combo.GetValue()
        self.job_path = self.cron_path_combo.GetValue()
        self.job_script = self.cron_script_cb.GetValue()
        self.job_args = self.cron_args_tc.GetValue()
        self.job_comment = self.cron_comment_tc.GetValue()
        self.job_enabled = self.cron_enabled_cb.GetValue()
        self.job_repeat = self.cron_repeat_opts_cb.GetValue()
        self.job_repnum = self.cron_every_num_tc.GetValue()
        self.job_min = self.cron_timed_min_tc.GetValue()
        self.job_hour = self.cron_timed_hour_tc.GetValue()
        self.job_day = self.cron_timed_day_tc.GetValue()
        self.job_month = self.cron_timed_month_tc.GetValue()
        self.job_dow = self.cron_timed_dow_tc.GetValue()
        self.Destroy()
    def OnClose(self, e):
        #set all post-creation flags to zero
        #   this is so that it doesn't ever somehow confuse old dirty data
        #   with new correct data, stuff comes in one side and leaves the other.
        self.job_type = None
        self.job_path = None
        self.job_script = None
        self.job_args = None
        self.job_comment = None
        self.job_enabled = None
        self.job_repeat = None
        self.job_repnum = None
        self.job_min = None
        self.job_hour = None
        self.job_day = None
        self.job_month = None
        self.job_dow = None
        self.Destroy()

class pi_link_pnl(wx.Panel):
    #
    # Creates the pannel with the raspberry pi data in it
    # and connects ssh to the pi when button is pressed
    # or allows seeking
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0,0), size = wx.Size( 285,190 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,230,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        pi_link_pnl.target_ip = ''
        pi_link_pnl.target_user = ''
        pi_link_pnl.target_pass = ''
        pi_link_pnl.config_location_on_pi = '/home/pi/Pigrow/config/pigrow_config.txt'
     ## the three boxes for pi's connection details, IP, Username and Password
        self.l_ip = wx.StaticText(self,  label='address', pos=(10, 20))
        self.tb_ip = wx.TextCtrl(self, pos=(125, 25), size=(150, 25))
        self.tb_ip.SetValue("192.168.1.")
        self.l_user = wx.StaticText(self,  label='Username', pos=(10, 60))
        self.tb_user = wx.TextCtrl(self, pos=(125, 60), size=(150, 25))
        self.tb_user.SetValue("pi")
        self.l_pass = wx.StaticText(self,  label='Password', pos=(10, 95))
        self.tb_pass = wx.TextCtrl(self, pos=(125, 95), size=(150, 25))
        self.tb_pass.SetValue("raspberry")
     ## link with pi button
        self.link_with_pi_btn = wx.Button(self, label='Link to Pi', pos=(10, 125), size=(175, 30))
        self.link_with_pi_btn.Bind(wx.EVT_BUTTON, self.link_with_pi_btn_click)
        self.link_status_text = wx.StaticText(self,  label='-- no link --', pos=(25, 160))
     ## seek next pi button
        self.seek_for_pigrows_btn = wx.Button(self, label='Seek next', pos=(190,125))
        self.seek_for_pigrows_btn.Bind(wx.EVT_BUTTON, self.seek_for_pigrows_click)
    def __del__(self):
        print("psssst it did that thing, the _del_ one you like so much...")
        pass

    def seek_for_pigrows_click(self, e):
        print("seeking for pigrows...")
        number_of_tries_per_host = 1
        pi_link_pnl.target_ip = self.tb_ip.GetValue()
        pi_link_pnl.target_user = self.tb_user.GetValue()
        pi_link_pnl.target_pass = self.tb_pass.GetValue()
        if pi_link_pnl.target_ip.split(".")[3] == '':
            pi_link_pnl.target_ip = pi_link_pnl.target_ip + '0'
        start_from = pi_link_pnl.target_ip.split(".")[3]
        lastdigits = len(str(start_from))
        hostrange = pi_link_pnl.target_ip[:-lastdigits]
        #Iterate through the ip_to_test and stop when  pigrow is found
        for ip_to_test in range(int(start_from)+1,255):
            host = hostrange + str(ip_to_test)
            pi_link_pnl.target_ip = self.tb_ip.SetValue(host)
            seek_attempt = 1
            log_on_test = False
            while True:
                print("Trying to connect to " + host)
                try:
                    ssh.connect(host, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                    print("Connected to " + host)
                    log_on_test = True
                    stdin, stdout, stderr = ssh.exec_command("cat " + pi_link_pnl.config_location_on_pi  + " | grep box_name")
                    box_name = stdout.read().strip().split("=")[1]
                    print("Pigrow Found; " + box_name)
                    self.set_link_pi_text(log_on_test, box_name)
                    return box_name #this just exits the loop
                except paramiko.AuthenticationException:
                    print("Authentication failed when connecting to " + str(host))
                except Exception as e:
                    print("Could not SSH to " + host + " because:" + str(e))
                    seek_attempt += 1
                if seek_attempt == number_of_tries_per_host + 1:
                    print("Could not connect to " + host + " Giving up")
                    break #end while loop and look at next host

    def link_with_pi_btn_click(self, e):
        log_on_test = False
        if self.link_with_pi_btn.GetLabel() == 'Disconnect':
            print("breaking ssh connection")
            ssh.close()
            self.link_with_pi_btn.SetLabel('Link to Pi')
            self.tb_ip.Enable()
            self.tb_user.Enable()
            self.tb_pass.Enable()
            self.link_status_text.SetLabel("-- Disconnected --")
            self.seek_for_pigrows_btn.Enable()
            MainApp.welcome_pannel.Show()
        else:
            #clear_temp_folder()
            pi_link_pnl.target_ip = self.tb_ip.GetValue()
            pi_link_pnl.target_user = self.tb_user.GetValue()
            pi_link_pnl.target_pass = self.tb_pass.GetValue()
            try:
                ssh.connect(pi_link_pnl.target_ip, username=pi_link_pnl.target_user, password=pi_link_pnl.target_pass, timeout=3)
                print("Connected to " + pi_link_pnl.target_ip)
                log_on_test = True
            except Exception as e:
                print("Failed to log on due to; " + str(e))
            if log_on_test == True:
                box_name = self.get_box_name()
            else:
                box_name = None
            self.set_link_pi_text(log_on_test, box_name)

    def set_link_pi_text(self, log_on_test, box_name):
        pi_link_pnl.boxname = box_name  #to maintain persistance if needed elsewhere later
        if not box_name == None:
            self.link_status_text.SetLabel("linked with - " + str(pi_link_pnl.boxname))
            MainApp.welcome_pannel.Hide()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()
        elif log_on_test == False:
            self.link_status_text.SetLabel("unable to connect")
            ssh.close()
        if log_on_test == True and box_name == None:
            self.link_status_text.SetLabel("Found raspberry pi, but not pigrow")
            MainApp.welcome_pannel.Hide()
            self.link_with_pi_btn.SetLabel('Disconnect')
            self.tb_ip.Disable()
            self.tb_user.Disable()
            self.tb_pass.Disable()
            self.seek_for_pigrows_btn.Disable()

    def get_box_name(self):
        boxname = None
        try:
            stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
            boxname = stdout.read().strip().split("=")[1]
            print "Pigrow Found; " + boxname
        except Exception as e:
            print("dang - can't connect to pigrow! " + str(e))
        if boxname == '':
            boxname = None
        return boxname

class welcome_pnl(wx.Panel):
    #
    #  This displays the welcome message on start up
    #     this explains how to get started
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (285, 0), size = wx.Size( 910,800 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((150,210,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        png = wx.Image('./splash.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth(), png.GetHeight()))


class view_pnl(wx.Panel):
    #
    # Creates the pannel with the navigation tabs
    # small and simple, it changes which pannels are visible
    #
    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = (0, 190), size = wx.Size( 285,35 ), style = wx.TAB_TRAVERSAL )
        self.SetBackgroundColour((230,200,170)) #TESTING ONLY REMOVE WHEN SIZING IS DONE AND ALL THAT BUSINESS
        view_opts = ['System Config', 'Pigrow Setup', 'Camera Config', 'Cron Timing', 'multi-script', 'Local Files', 'Timelapse', 'Graphs', 'Live View', 'pieye watcher']
        self.view_cb = wx.ComboBox(self, choices = view_opts, pos=(10,2), size=(265, 30))
        self.view_cb.Bind(wx.EVT_COMBOBOX, self.view_combo_go)
    def view_combo_go(self, e):
        display = self.view_cb.GetValue()
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.welcome_pannel.Hide()
        if display == 'System Config':
            MainApp.system_ctrl_pannel.Show()
            MainApp.system_info_pannel.Show()
        elif display == 'Pigrow Setup':
            print("changing window display like i'm Mr Polly on meth")
        elif display == 'Camera Config':
            print("changing window display like i'm Mr Polly on weed")
        elif display == 'Cron Timing':
            MainApp.cron_list_pannel.Show()
            MainApp.cron_info_pannel.Show()
        elif display == 'Multi-script':
            print("changing window display like i'm Mr Polly on coke")
        elif display == 'Local Files':
            print("changing window display like i'm Mr Polly on heroin")
        elif display == 'Timelapse':
            print("changing window display like i'm Mr Polly on crack")
        elif display == 'Graphs':
            print("changing window display like i'm Mr Polly on speed")
        elif display == 'Live View':
            print("changing window display like i'm Mr Polly on LSD")
        elif display == 'pieye watcher':
            print("changing window display like i'm Mr Polly in a daydream")
        else:
            print("!!! Option not recognised, this is a programming error! sorry")
            print("          message me and tell me about it and i'll be very thankful")





#
#
#  The main bit of the program
#           EXCITING HU?!!!?
#

class MainFrame ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 1200,800 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
    #    bSizer1 = wx.BoxSizer( wx.VERTICAL )
    #    self.SetSizer( bSizer1 )
        self.Layout()
        self.Centre( wx.BOTH )
    def __del__( self ):
        pass

class MainApp(MainFrame):
    def __init__(self, parent):
        MainFrame.__init__(self, parent)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.pi_link_pnl = pi_link_pnl(self)
        self.view_pnl = view_pnl(self)
        #
        # switch this up so it shows based on tabs and shit, yo!
        #
        MainApp.welcome_pannel = welcome_pnl(self)
        MainApp.system_ctrl_pannel = system_ctrl_pnl(self)
        MainApp.system_info_pannel = system_info_pnl(self)
        MainApp.cron_list_pannel = cron_list_pnl(self)
        MainApp.cron_info_pannel = cron_info_pnl(self)
        MainApp.cron_list_pannel.Hide()
        MainApp.cron_info_pannel.Hide()
        MainApp.system_ctrl_pannel.Hide()
        MainApp.system_info_pannel.Hide()
        #self.pi_link_pnl.Hide()

    def OnClose(self, e):
        #Closes SSH connection even on quit
        # Add 'ya sure?' question if there's unsaved data
        print("Closing SSH connection")
        ssh.close()
        exit(0)


def main():
    app = wx.App()
    window = MainApp(None)
    window.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()
