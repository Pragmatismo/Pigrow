import wx
import os

class ctrl_pnl(wx.Panel):
    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL )
        self.SetFont(shared_data.sub_title_font)
        self.cron_label = wx.StaticText(self,  label='Cron Config Menu')
        self.cron_bkup_label = wx.StaticText(self,  label='backup;')
        self.SetFont(shared_data.button_font)

        self.read_cron_btn = wx.Button(self, label='Read Crontab', size=(175, 30))
        self.read_cron_btn.Bind(wx.EVT_BUTTON, self.read_cron_click)
        self.new_cron_btn = wx.Button(self, label='Add new job', size=(175, 30))
        self.new_cron_btn.Bind(wx.EVT_BUTTON, self.new_cron_click)
        self.update_cron_btn = wx.Button(self, label='Save Cron', size=(175, 30))
        self.update_cron_btn.Bind(wx.EVT_BUTTON, self.update_cron_click)
        self.help_cron_btn = wx.Button(self, label='Cron Help', size=(175, 30))
        self.help_cron_btn.Bind(wx.EVT_BUTTON, self.help_cron_click)

        self.cron_backup_btn = wx.Button(self, label='Backup Cron', size=(175, 30))
        self.cron_backup_btn.Bind(wx.EVT_BUTTON, self.cron_backup_click)
        self.cron_restore_btn = wx.Button(self, label='Restore backup', size=(175, 30))
        self.cron_restore_btn.Bind(wx.EVT_BUTTON, self.cron_restore_click)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.cron_label, 0, wx.ALL, 5)
        main_sizer.Add(self.read_cron_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.new_cron_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.update_cron_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        #
        main_sizer.Add(self.cron_bkup_label, 0, wx.ALL, 5)
        main_sizer.Add(self.cron_backup_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.cron_restore_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(wx.StaticLine(self, wx.ID_ANY, size=(20, -1), style=wx.LI_HORIZONTAL), 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.Add(self.help_cron_btn, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(main_sizer)

    def help_cron_click(self, e):
        self.parent.shared_data.show_help('cron_help.png')

    def start_running_script_in_background_on_pi(self, script_cmd):
        text_msg = "Script " + str(script_cmd) + " not currently running, "
        text_msg += "would you like to start it in the background on the pi?"
        dbox = wx.MessageDialog(self, text_msg, "Run on Pigrow?", wx.YES_NO | wx.ICON_QUESTION)
        answer = dbox.ShowModal()
        dbox.Destroy()
        if (answer == wx.ID_YES):
            print(("Running " + str(script_cmd)))
            self.parent.link_pnl.run_on_pi(script_cmd + " &")
                                                # the & at the end is so that it
                                                # doesn't ask for output and is non-blocking
                                                # this is absolutely vital!

    def update_cron_click(self, e="", no_starting=False):
        #
        self.startup_cron = self.parent.dict_I_pnl['cron_pnl'].startup_cron
        self.repeat_cron = self.parent.dict_I_pnl['cron_pnl'].repeat_cron
        self.timed_cron = self.parent.dict_I_pnl['cron_pnl'].timed_cron
        cron_line_dict = {}
        #make a text file of all the cron jobs
        num_new = 0
        startup_num = self.startup_cron.GetItemCount()
        for num in range(0, startup_num):
            line_num = self.startup_cron.GetItemText(num, 0)
            cron_line = ''
            if self.startup_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            script_cmd = self.startup_cron.GetItemText(num, 3) # cron task
            script_cmd += ' ' + self.startup_cron.GetItemText(num, 4) # cron_extra_args
            cron_line += '@reboot ' + script_cmd
            if not line_num.isdigit():
                line_num = line_num + str(num_new)
                num_new += 1
            cron_line_dict[line_num] = cron_line
            # ask if unrunning scripts should be started
            if not no_starting == True:
                is_running = self.test_if_script_running(self.startup_cron.GetItemText(num, 3), self.startup_cron.GetItemText(num, 4))
                enabled = self.startup_cron.GetItemText(num, 1)
                if is_running == False and enabled == 'True':
                    self.start_running_script_in_background_on_pi(script_cmd)
        # add repating jobs to cron list
        repeat_num = self.repeat_cron.GetItemCount()
        for num in range(0, repeat_num):
            cron_line = ''
            line_num = self.repeat_cron.GetItemText(num, 0)
            if self.repeat_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += self.repeat_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + self.repeat_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + self.repeat_cron.GetItemText(num, 4) # cron_extra_args
            if not line_num.isdigit():
                line_num = line_num + str(num_new)
                num_new += 1
            cron_line_dict[line_num] = cron_line
        onetime_num = self.timed_cron.GetItemCount()
        for num in range(0, onetime_num):
            cron_line = ''
            line_num = self.timed_cron.GetItemText(num, 0)
            if self.timed_cron.GetItemText(num, 1) == 'False':
                cron_line += '#'
            cron_line += self.timed_cron.GetItemText(num, 2).strip(' ')
            cron_line += ' ' + self.timed_cron.GetItemText(num, 3) # cron_task
            cron_line += ' ' + self.timed_cron.GetItemText(num, 4) # cron_extra_args
            if not line_num.isdigit():
                line_num = line_num + str(num_new)
                num_new += 1
            cron_line_dict[line_num] = cron_line
        # write cron in the correct order
        cron_text = ""
        for line_number in range(1,  len(cron_line_dict) + len(self.cron_extra_lines)):
            if str(line_number) in cron_line_dict:
                cron_text += cron_line_dict[str(line_number)].strip() + "\n"
            elif line_number in self.cron_extra_lines:
                if not self.cron_extra_lines[line_number].strip() == "":
                    cron_text += self.cron_extra_lines[line_number].strip() + "\n"
        for key, value in cron_line_dict.items():
            if not key.isdigit() and not value.strip() == "":
                if not "deleted" in key:
                    cron_text += value.strip() + "\n"

        # ask the user if they're sure
        msg_text = "Update cron to; \n\n" + cron_text
        mbox = wx.MessageDialog(None, msg_text, "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
        sure = mbox.ShowModal()
        #
        if sure == wx.ID_YES:
            print ("Updating remote cron")
            # save cron text onto pigrow as text file
            temppath = '/home/' + self.parent.link_pnl.target_user + '/Pigrow/temp/remotecron.txt'
            self.parent.link_pnl.write_textfile_to_pi( cron_text, temppath )
            # import file into cron
            out, error = self.parent.link_pnl.run_on_pi("crontab " + temppath)
            print("Cron tab : ", out, error)
            out, error = self.parent.link_pnl.run_on_pi("rm " + temppath)

        else:
            print("Updating cron cancelled")
        mbox.Destroy()
        #refresh cron list
        self.read_cron_click("event")

    def read_cron_click(self, event):
        #reads pi's crontab then puts jobs in correct table
        print("Reading cron information from pi")
        cron_text, error = self.parent.link_pnl.run_on_pi("crontab -l")
        cron_text = cron_text.split('\n')
        #select instance of list to use
        #
        startup_list_instance = self.parent.dict_I_pnl['cron_pnl'].startup_cron
        repeat_list_instance = self.parent.dict_I_pnl['cron_pnl'].repeat_cron
        onetime_list_instance = self.parent.dict_I_pnl['cron_pnl'].timed_cron
        #clear lists of prior data
        startup_list_instance.DeleteAllItems()
        repeat_list_instance.DeleteAllItems()
        onetime_list_instance.DeleteAllItems()
        #sort cron info into lists
        line_number = 0

        self.cron_extra_lines = {}
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
                # split cmd_string into task and extra args
                cron_task = cmd_string.split(' ')[0]
                cron_extra_args = ''
                for arg in cmd_string.split(' ')[1:]:
                    cron_extra_args += arg + ' '
                if real_job == True and not cmd_string == '':
                    #print job_enabled, timing_string, cron_jobtype, cron_task, cron_extra_args
                    if cron_jobtype == 'reboot':
                        self.add_to_startup_list(startup_list_instance, line_number, job_enabled, cron_task, cron_extra_args)
                    elif cron_jobtype == 'one time':
                        self.add_to_onetime_list(onetime_list_instance, line_number, job_enabled, timing_string, cron_task, cron_extra_args)
                    elif cron_jobtype == 'repeating':
                        self.add_to_repeat_list(repeat_list_instance, line_number, job_enabled, timing_string, cron_task, cron_extra_args)
                else:
                    if job_enabled == False:
                        cron_line = "#" + cron_line
                    if not cron_line == "":
                        self.cron_extra_lines[line_number]=cron_line
            else:
                self.cron_extra_lines[line_number]=cron_line
        print("cron information read and updated into tables.")
        # update table layouts
        startup_list_instance.autosizeme()
        repeat_list_instance.autosizeme()
        onetime_list_instance.autosizeme()

    def test_if_script_running(self, script, args):
        #cron_info_pnl.test_if_script_running(MainApp.cron_info_pannel, script)
        pid_text, error = self.parent.link_pnl.run_on_pi("pidof -x " + str(script))
        pid_text = pid_text.strip()
        # return false if none are running
        if pid_text == '':
            return False
        # convert output into list of pids
        if " " in pid_text:
            pids = pid_text.split(" ")
        else:
            pids = [pid_text]
        # cycle through and check for expected args
        for pid in pids:
            out, error = self.parent.link_pnl.run_on_pi("ps -fp " + pid)
            if args.strip() in out:
                return True
        # if it didn't find it return false
        return False

    def check_if_script_in_startup(self, script_name):
        print(" checking startup cron for " + script_name )
        startup_cron = self.parent.dict_I_pnl['cron_pnl'].startup_cron
        last_index = startup_cron.GetItemCount()

        script_status = "none"
        if not last_index == 0:
           for index in range(0, last_index):
                name = startup_cron.GetItem(index, 3).GetText()
                if script_name in name:
                    if not startup_cron.GetItem(index, 0).GetText() == "deleted":
                        script_enabled = startup_cron.GetItem(index, 1).GetText()
                        if script_enabled == 'True':
                            script_status = 'enabled'
                        else:
                            script_status = 'disabled'

        return script_status

    def add_to_startup_list(self, startup_list_instance, line_number, job_enabled, cron_task, cron_extra_args=''):
        is_running = self.test_if_script_running(cron_task, cron_extra_args)
        startup_list_instance.InsertItem(0, str(line_number))
        startup_list_instance.SetItem(0, 1, str(job_enabled))
        startup_list_instance.SetItem(0, 2, str(is_running))   #tests if script it currently running on pi
        startup_list_instance.SetItem(0, 3, cron_task)
        startup_list_instance.SetItem(0, 4, cron_extra_args)

    def add_to_repeat_list(self, repeat_list_instance, line_number, job_enabled, timing_string, cron_task, cron_extra_args=''):
        repeat_list_instance.InsertItem(0, str(line_number))
        repeat_list_instance.SetItem(0, 1, str(job_enabled))
        repeat_list_instance.SetItem(0, 2, timing_string)
        repeat_list_instance.SetItem(0, 3, cron_task)
        repeat_list_instance.SetItem(0, 4, cron_extra_args)

    def add_to_onetime_list(self, onetime_list_instance, line_number, job_enabled, timing_string, cron_task, cron_extra_args=''):
        onetime_list_instance.InsertItem(0, str(line_number))
        onetime_list_instance.SetItem(0, 1, str(job_enabled))
        onetime_list_instance.SetItem(0, 2, timing_string)
        onetime_list_instance.SetItem(0, 3, cron_task)
        onetime_list_instance.SetItem(0, 4, cron_extra_args)

    def make_repeating_cron_timestring(self, repeat, repeat_num):
        #assembles timing sting for cron
        # min (0 - 59) | hour (0 - 23) | day of month (1-31) | month (1 - 12) | day of week (0 - 6) (Sunday=0)
        # 1st postion - Minute 0-59
        if repeat == 'min':
            if int(repeat_num) in range(0,59):
                cron_time_string = '*/' + str(repeat_num)
            else:
                print("Cron string min wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string = '0'
        # 2nd Position - Hour 0-23
        if repeat == 'hour':
            if int(repeat_num) in range(0,23):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron string hour wrong, fix it before updating")
                return 'fail'
        else:
            if not repeat == "min":
                cron_time_string += ' 0'
            else:
                cron_time_string += ' *'
        # 3rd Position - Day of Month 1-31
        if repeat == 'day':
            if int(repeat_num) in range(1,31):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron string day wrong, fix it before updating")
                return 'fail'
        else:
            if not repeat in ['min', 'hour']:
                cron_time_string += ' 1'
            else:
                cron_time_string += ' *'
        # 4th Position - Month 1-12
        if repeat == 'month':
            if int(repeat_num) in range(1,12):
                cron_time_string += ' */' + str(repeat_num)
            else:
                print("Cron sting month wrong, fix it before updating")
                return 'fail'
        else:
            if not repeat in ['min', 'hour', 'day']:
                cron_time_string += ' 1'
            else:
                cron_time_string += ' *'
        # 5th Position - Day Of the Week 0-7 with 0&7 Sunday
        if repeat == 'dow':
            if int(repeat_num) in range(1,7):
                cron_time_string = '0 0 * * */' + str(repeat_num)
            else:
                print("Cron string dow wrong, fix it before updating")
                return 'fail'
        else:
            cron_time_string += ' *'
        return cron_time_string

    def make_onetime_cron_timestring(self, job_min, job_hour, job_day, job_month, job_dow):
        # 1st postion - Minute 0-59
        if job_min.isdigit():
            timing_string = str(job_min)
        else:
            timing_string = '0'
        # 2nd Position - Hour 0-23
        if job_hour.isdigit():
            timing_string += ' ' + str(job_hour)
        else:
            timing_string += ' 0'
        # 3rd Position - Day of Month 1-31
        if job_day.isdigit():
            timing_string += ' ' + str(job_day)
        else:
            if job_month.isdigit(): #if month is selected use first day of month
                timing_string += ' 1'
            else:
                timing_string += ' *'
        # 4th Position - Month 1-12
        if job_month.isdigit():
            timing_string += ' ' + str(job_month)
        else:
            timing_string += ' *'
        # 5th Position - Day Of the Week 0-7 with 0&7 Sunday
        if job_dow.isdigit():
            timing_string += ' ' + str(job_dow)
        else:
            timing_string += ' *'
        return timing_string

    def new_cron_click(self, e="", set_dict={}):
        #define blank fields and defaults for dialogue box to read
        pi_path = self.parent.shared_data.remote_pigrow_path + "scripts/cron/"
        cron_set_dict = {"path":pi_path,
                        "task":"input cron task here",
                        "args":"",
                        "type":"repeating",
                        "everystr":"min",
                        "everynum":"5",
                        "min":"30",
                        "hour":"8",
                        "day":"",
                        "month":"",
                        "dow":"",
                        "enabled":True}
        for item in set_dict:
            if item in cron_set_dict:
                cron_set_dict[item] = set_dict[item]
        # the following is until it gets updated to just pass the dict
        self.cron_path_toedit     = cron_set_dict["path"]
        self.cron_task_toedit     = cron_set_dict["task"]
        self.cron_args_toedit     = cron_set_dict["args"]
        self.cron_type_toedit     = cron_set_dict["type"]
        self.cron_everystr_toedit = cron_set_dict["everystr"]
        self.cron_everynum_toedit = cron_set_dict["everynum"]
        self.cron_min_toedit      = cron_set_dict["min"]
        self.cron_hour_toedit     = cron_set_dict["hour"]
        self.cron_day_toedit      = cron_set_dict["day"]
        self.cron_month_toedit    = cron_set_dict["month"]
        self.cron_dow_toedit      = cron_set_dict["dow"]
        self.cron_enabled_toedit  = cron_set_dict["enabled"]
        #make dialogue box
        cron_dbox = cron_job_dialog(self, self.parent)
        cron_dbox.ShowModal()
        #catch any changes made if ok was pressed, if cancel all == None
        cron_jobtype = cron_dbox.job_type
        job_path = cron_dbox.job_path
        job_script = cron_dbox.job_script
        cron_extra_args = cron_dbox.job_args
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
                self.add_to_startup_list(self.parent.dict_I_pnl['cron_pnl'].startup_cron ,'new', job_enabled, cron_task, cron_extra_args)
            elif cron_jobtype == 'one time':
                self.add_to_onetime_list(self.parent.dict_I_pnl['cron_pnl'].timed_cron ,'new', job_enabled, timing_string, cron_task, cron_extra_args)
            elif cron_jobtype == 'repeating':
                self.add_to_repeat_list(self.parent.dict_I_pnl['cron_pnl'].repeat_cron, 'new', job_enabled, timing_string, cron_task, cron_extra_args)

    def cron_backup_click(self, e):
        #
        # ask user to name conf - format 'cron_<NAME>.txt' default 'backup'
        msg = "Select name of cron backup"
        filename_dbox = wx.TextEntryDialog(self, msg, 'Cron backup', 'backup')
        if filename_dbox.ShowModal() == wx.ID_OK:
            cron_archive_name = filename_dbox.GetValue()
        else:
            return "cancelled"
        filename_dbox.Destroy()
        cron_archive_name = "cron_" + cron_archive_name + ".txt"
        #
        cron_save_path = os.path.join(self.parent.shared_data.frompi_path, "cron/")
        os.makedirs(cron_save_path, exist_ok = True)
        cron_save_path = os.path.join(cron_save_path, cron_archive_name)
        if os.path.isfile(cron_save_path):
            print(" FILE ALREADY EXISTS ASK THE USER IF THEY WANT TO OVERWRITE")
        # read cron
        cmd = "crontab -l"
        out, error = self.parent.link_pnl.run_on_pi(cmd)
        if out.strip() == "":
            print("Error reading cron, or it's totally blank.")
            return None
        # save to text file
        with open(cron_save_path, "w") as f:
            f.write(out)
        #
        print("Cron backup saved to; ", cron_save_path)

    def cron_restore_click(self ,e):
        print(" restore cron button has been pressed, what do you think of that, hu?")
        restore_dialog = restore_backup_dialog(self, self.parent)
        restore_dialog.ShowModal()
        self.read_cron_click("e")

    def connect_to_pigrow(self):
        self.read_cron_click('e')


class restore_backup_dialog(wx.Dialog):
    """
    For restoring backup cron files to raspberry pi
        """
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(restore_backup_dialog, self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((750, 750))
        self.SetTitle("Restore cron backup to raspberry pi")
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        shared_data = self.parent.parent.shared_data
        cron_save_path = os.path.join(self.parent.parent.shared_data.frompi_path, "cron/")
        list_of_cron_bks = os.listdir(cron_save_path)

        # panel
        pnl = wx.Panel(self)
        self.SetFont(shared_data.title_font)
        box_label = wx.StaticText(self,  label='Select backup to restore')
        self.SetFont(shared_data.info_font)
        self.logfile_cb = wx.ComboBox(self, choices = list_of_cron_bks, size=(265, 30))
        self.logfile_cb.Bind(wx.EVT_COMBOBOX, self.logfile_combo_go)
        self.crontext = wx.TextCtrl(self, -1, "", size=(700,500), style=wx.TE_MULTILINE)

        # ok and cancel Buttons
        self.SetFont(shared_data.button_font)
        self.restore_btn = wx.Button(self, label='Restore', size=(175, 30))
        self.restore_btn.Bind(wx.EVT_BUTTON, self.restore_click)
        self.cancel_btn = wx.Button(self, label='Close', size=(175, 30))
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.Add(self.restore_btn, 0,  wx.ALL, 3)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(self.cancel_btn, 0,  wx.ALL, 3)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(box_label, 0, wx.ALL|wx.EXPAND, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(self.logfile_cb, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(self.crontext, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)

    def logfile_combo_go(self, e):
        choice = self.logfile_cb.GetValue()
        cron_local_path = os.path.join(self.parent.parent.shared_data.frompi_path, "cron/", choice)
        with open(cron_local_path, "r") as f:
            cron_text = f.read()
        print(cron_text)
        self.crontext.SetValue(cron_text)

    def restore_click(self, e):
        # copy backup file to pi
        cron_text = self.crontext.GetValue()
        if cron_text.strip() == "":
            return None
        temp_cron_remote = self.parent.parent.shared_data.remote_pigrow_path + "temp/cron_bkup.txt"
        self.parent.parent.link_pnl.write_textfile_to_pi(cron_text, temp_cron_remote)

        # install into crontab
        cmd = "crontab " + temp_cron_remote
        out, error = self.parent.parent.link_pnl.run_on_pi(cmd)
        if not error == "":
            mbox = wx.MessageDialog(None, error, "Error writing cron", wx.OK|wx.ICON_ERROR)
            mbox.ShowModal()
            mbox.Destroy()
        print (out, error)
        self.Destroy()

    def OnClose(self, e):
        self.Destroy()

class info_pnl(wx.Panel):
    '''
    #  This displays the three different cron type lists on the big-pannel
    #  double click to edit one of the jobs
    #  other control buttons found on the cron control pannel
    '''

    class startup_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,10), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Active')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

    class repeating_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,245), size=(900,200)):
            wx.ListCtrl.__init__(self, parent, id, size=size, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'every')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

        def parse_cron_string(self, cron_rep_string):
            try:
                cron_stars = cron_rep_string.split(' ')
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
                    cron_rep = ""
                    cron_num = "fail"
                return cron_num, cron_rep
            except:
                return "", ""

    class timed_cron_list(wx.ListCtrl):
        def __init__(self, parent, id, pos=(5,530)):
            wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT, pos=pos)
            self.InsertColumn(0, 'Line')
            self.InsertColumn(1, 'Enabled')
            self.InsertColumn(2, 'Time')
            self.InsertColumn(3, 'Task')
            self.InsertColumn(4, 'extra args')
            self.autosizeme()

        def autosizeme(self):
            for i in range(0, self.GetColumnCount()):
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE)
                l = self.GetColumnWidth(i)
                self.SetColumnWidth(i, wx.LIST_AUTOSIZE_USEHEADER)
                h = self.GetColumnWidth(i)
                if l > h:
                    self.SetColumnWidth(i, wx.LIST_AUTOSIZE)

    def __init__( self, parent ):
        shared_data = parent.shared_data
        self.parent = parent
        wx.Panel.__init__(self, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL)
        # Tab Title
        self.SetFont(shared_data.title_font)
        title_l = wx.StaticText(self,  label='Cron Tab Control')
        self.SetFont(shared_data.sub_title_font)
        page_sub_title =  wx.StaticText(self,  label='Use cron on the pigrow to time events and trigger devices')
        # Info boxes
        cron_start_up_l = wx.StaticText(self,  label='Cron start up;')
        self.SetFont(shared_data.info_font)
        self.startup_cron = self.startup_cron_list(self, 1)
        self.startup_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_startup)
        self.startup_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        self.startup_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.startup_got_focus)
        self.SetFont(shared_data.sub_title_font)
        cron_repeat_l = wx.StaticText(self,  label='Repeating Jobs;')
        self.SetFont(shared_data.info_font)
        self.repeat_cron = self.repeating_cron_list(self, 1)
        self.repeat_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_repeat)
        self.repeat_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        self.repeat_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.repeat_got_focus)
        self.SetFont(shared_data.sub_title_font)
        cron_timed_l = wx.StaticText(self,  label='One time triggers;')
        self.SetFont(shared_data.info_font)
        self.timed_cron = self.timed_cron_list(self, 1)
        self.timed_cron.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick_timed)
        self.timed_cron.Bind(wx.EVT_LIST_KEY_DOWN, self.del_item)
        self.timed_cron.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.timed_got_focus)
        # sizers
        main_sizer =  wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title_l, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(page_sub_title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(cron_start_up_l, 0, wx.ALL, 3)
        main_sizer.Add(self.startup_cron, 1, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(cron_repeat_l, 0, wx.ALL, 3)
        main_sizer.Add(self.repeat_cron, 1, wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(cron_timed_l, 0, wx.ALL, 3)
        main_sizer.Add(self.timed_cron, 1, wx.ALL|wx.EXPAND, 3)
        self.SetSizer(main_sizer)

    def startup_got_focus(self, e):
        timed_focus = self.timed_cron.GetFocusedItem()
        self.timed_cron.Select(timed_focus, on=0)
        repeat_focus = self.repeat_cron.GetFocusedItem()
        self.repeat_cron.Select(repeat_focus, on=0)

    def repeat_got_focus(self, e):
        startup_focus = self.startup_cron.GetFocusedItem()
        self.startup_cron.Select(startup_focus, on=0)
        timed_focus = self.timed_cron.GetFocusedItem()
        self.timed_cron.Select(timed_focus, on=0)

    def timed_got_focus(self, e):
        startup_focus = self.startup_cron.GetFocusedItem()
        self.startup_cron.Select(startup_focus, on=0)
        repeat_focus = self.repeat_cron.GetFocusedItem()
        self.repeat_cron.Select(repeat_focus, on=0)

    def remove_by_name(self, script, name=None):
        #remove named script from repeat cron
        c_pnl = self.parent.dict_C_pnl['cron_pnl']
        print("removing " + script + " named " + str(name) + " if it's set")
        last_index = self.repeat_cron.GetItemCount()
        if not last_index == 0:
            for index in range(0, last_index):
                job_name  = self.repeat_cron.GetItem(index, 3).GetText()
                job_extra = self.repeat_cron.GetItem(index, 4).GetText()
                if script in job_name:
                    if "name=" + name in job_extra:
                        self.repeat_cron.DeleteItem(index)
                        print("REMOVED FROM CRON")
                        c_pnl.update_cron_click("e")
                        return "removed"

    def find_repeat_pos_by_name(self, script, name):
        script_index_repeating = -1
        if not name == "":
            for index in range(0, self.repeat_cron.GetItemCount()):
                cmd_path = self.repeat_cron.GetItem(index, 3).GetText()
                if script in cmd_path:
                    cmd_args = self.repeat_cron.GetItem(index, 4).GetText()
                    if  "name=" + name in cmd_args:
                        script_index_repeating = index
        return script_index_repeating

    def list_repeat_by_key(self, script, key, val):
        if script == "" or key == "" or val == "":
            return []
        # look for key=val in args
        found_jobs = []
        id_pair = str(key) + "=" + str(val) + " "
        for index in range(0, self.repeat_cron.GetItemCount()):
            cmd_path = self.repeat_cron.GetItem(index, 3).GetText()
            if script in cmd_path:
                cmd_args = self.repeat_cron.GetItem(index, 4).GetText()
                cmd_args_s = cmd_args.replace('"', "") + " "
                if  id_pair.replace('"', "") in cmd_args_s:
                    enabled = self.repeat_cron.GetItem(index, 1).GetText()
                    cron_time_string = self.repeat_cron.GetItem(index, 2).GetText()
                    freq_num, freq_text = self.repeat_cron.parse_cron_string(cron_time_string)
                    found_jobs.append([index, enabled, freq_num, freq_text, cmd_args])
        return found_jobs

    def list_timed_by_key(self, script, key, val):
        if script == "" or key == "" or val == "":
            return []
        # look for key=val in args
        found_jobs = []
        id_pair = str(key) + "=" + str(val) + " "
        for index in range(0, self.timed_cron.GetItemCount()):
            cmd_path = self.timed_cron.GetItem(index, 3).GetText()
            if script in cmd_path:
                cmd_args = self.timed_cron.GetItem(index, 4).GetText()
                cmd_args_s = cmd_args.replace('"', "") + " "
                if  id_pair.replace('"', "") in cmd_args_s:
                    enabled = self.timed_cron.GetItem(index, 1).GetText()
                    cron_time_string = self.timed_cron.GetItem(index, 2).GetText()
                    found_jobs.append([index, enabled, cron_time_string, cmd_args])
        return found_jobs

    def edit_repeat_job_by_name(self, script_path, start_name, new_name, new_cron_time_txt, new_cron_time_num):
    #    script_path = shared_data.remote_pigrow_path + "scripts/sensors/log_sensor_module.py"
        script = os.path.split(script_path)[1]
        print("Changing " + script + " with name " + start_name)
        c_pnl = self.parent.dict_C_pnl['cron_pnl']

        # check to find cron job for script and name=start_name
        script_index_repeating = self.find_repeat_pos_by_name(script, start_name)

        if not script_index_repeating == -1:
            print("    - found in cron, editing it...")
            cron_enabled  = self.repeat_cron.GetItem(script_index_repeating, 1).GetText()
            cron_args     = self.repeat_cron.GetItem(script_index_repeating, 4).GetText()
            cron_args = cron_args.replace("name=" + start_name, "name=" + new_name)
            # clear job ready to add new one using the same info
            self.repeat_cron.DeleteItem(script_index_repeating)
        else:
            print("    - Job not currently in cron, adding it...")
            cron_enabled  = "True"
            cron_args     = "name=" + new_name

        timing_string = c_pnl.make_repeating_cron_timestring(new_cron_time_txt, new_cron_time_num)
        print("   setting - Cron job; " + cron_enabled + " " + timing_string + " " + script_path + " " + cron_args)
        c_pnl.add_to_repeat_list(self.repeat_cron, 'new', cron_enabled, timing_string, script_path, cron_args)

        # offer to write cron to pi
        c_pnl.update_cron_click("e", no_starting=True)

    def time_text_from_name(self, script, name):
        script_index_repeating = self.find_repeat_pos_by_name(script, name)
        if not script_index_repeating == -1:
            cron_time_string = self.repeat_cron.GetItem(script_index_repeating, 2).GetText()
            freq_num, freq_text = self.repeat_cron.parse_cron_string(cron_time_string)
            return freq_num, freq_text
        else:
            return "not", "found"

    def del_item(self, e):
        keycode = e.GetKeyCode()
        if keycode == wx.WXK_DELETE:
                mbox = wx.MessageDialog(None, "Delete selected cron job?", "Are you sure?", wx.YES_NO|wx.ICON_QUESTION)
                sure = mbox.ShowModal()
                if sure == wx.ID_YES:
                    if self.startup_cron.GetSelectedItemCount() == 1:
                        #print(self.startup_cron.DeleteItem(self.startup_cron.GetFocusedItem()))
                        index = self.startup_cron.GetFocusedItem()
                        self.startup_cron.SetItem(index, 0, "deleted")
                    if self.repeat_cron.GetSelectedItemCount() == 1:
                        #print(self.repeat_cron.DeleteItem(self.repeat_cron.GetFocusedItem()))
                        index = self.repeat_cron.GetFocusedItem()
                        self.repeat_cron.SetItem(index, 0, "deleted")
                    if self.timed_cron.GetSelectedItemCount() == 1:
                        #print(self.timed_cron.DeleteItem(self.timed_cron.GetFocusedItem()))
                        index = self.timed_cron.GetFocusedItem()
                        self.timed_cron.SetItem(index, 0, "deleted")

    def onDoubleClick_timed(self, e):
        index =  e.GetIndex()
        # create dbox and update table when done
        self.set_toedit_for_box(index, "one time", self.timed_cron)
        self.create_job_box(index)

    def onDoubleClick_repeat(self, e):
        index =  e.GetIndex()
        # create dbox and update table when done
        self.set_toedit_for_box(index, "repeating", self.repeat_cron)
        self.create_job_box(index)

    def onDoubleClick_startup(self, e):
        index =  e.GetIndex()
        # create dbox and update table when done
        self.set_toedit_for_box(index, "startup", self.startup_cron)
        self.create_job_box(index)

    def set_toedit_for_box(self, index, type, table):
        # general settings
        self.cron_type_toedit    = type
        self.cron_args_toedit    = str(table.GetItem(index, 4).GetText())
        # path and filename info
        cmd_path = table.GetItem(index, 3).GetText()
        cmd = cmd_path.split('/')[-1]
        cmd_path = cmd_path[:-len(cmd)]
        self.cron_path_toedit = str(cmd_path)
        self.cron_task_toedit = str(cmd)
        if str(table.GetItem(index, 1).GetText()) == 'True':
            enabled = True
        else:
            enabled = False
        self.cron_enabled_toedit = enabled
        # type spesific settings
        if type == "startup":
            self.cron_everystr_toedit = 'min'
            self.cron_everynum_toedit = '5'
            self.cron_min_toedit = '0'
            self.cron_hour_toedit = '8'
            self.cron_day_toedit = '*'
            self.cron_month_toedit = '*'
            self.cron_dow_toedit = '*'
        elif type == "repeating":
            timing_string = table.GetItem(index, 2).GetText()
            cron_num, cron_rep = self.repeating_cron_list.parse_cron_string(self, timing_string)
            self.cron_everystr_toedit = cron_rep
            self.cron_everynum_toedit = cron_num
            self.cron_min_toedit = '0'
            self.cron_hour_toedit = '8'
            self.cron_day_toedit = '*'
            self.cron_month_toedit = '*'
            self.cron_dow_toedit = '*'
        elif type == "one time":
            timing_string = table.GetItem(index, 2).GetText()
            cron_stars = timing_string.split(' ')
            cron_min = cron_stars[0]
            cron_hour = cron_stars[1]
            cron_day = cron_stars[2]
            cron_month = cron_stars[3]
            cron_dow = cron_stars[4]
            self.cron_min_toedit = cron_min
            self.cron_hour_toedit = cron_hour
            self.cron_day_toedit = cron_day
            self.cron_month_toedit = cron_month
            self.cron_dow_toedit = cron_dow
            self.cron_everystr_toedit = 'min'
            self.cron_everynum_toedit = '5'

    def create_job_box(self, index):
        cron_dbox = cron_job_dialog(self, self.parent)
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
        job_enabled = cron_dbox.job_enabled
        job_repeat = cron_dbox.job_repeat
        job_repnum = cron_dbox.job_repnum
        job_min = cron_dbox.job_min
        job_hour = cron_dbox.job_hour
        job_day = cron_dbox.job_day
        job_month = cron_dbox.job_month
        job_dow = cron_dbox.job_dow
        # make timing_string from min:hour or repeat + repeat_num
        c_pnl = self.parent.dict_C_pnl['cron_pnl']
        if cron_jobtype == 'repeating':
            timing_string = c_pnl.make_repeating_cron_timestring(job_repeat, job_repnum)
        elif cron_jobtype == 'one time':
            timing_string = c_pnl.make_onetime_cron_timestring(job_min, job_hour, job_day, job_month, job_dow)
        # sort into the correct table
        if not job_script == None:
            # remove entry
            if self.cron_type_toedit == "startup":
                self.startup_cron.DeleteItem(index)
            elif self.cron_type_toedit == "one time":
                self.timed_cron.DeleteItem(index)
            elif self.cron_type_toedit == "repeating":
                self.repeat_cron.DeleteItem(index)
            #add new entry to correct table
            if cron_jobtype == 'startup':
                c_pnl.add_to_startup_list(self.startup_cron, 'new', job_enabled, cron_task, cron_extra_args)
            elif cron_jobtype == 'one time':
                c_pnl.add_to_onetime_list(self.timed_cron, 'new', job_enabled, timing_string, cron_task, cron_extra_args)
            elif cron_jobtype == 'repeating':
                c_pnl.add_to_repeat_list(self.repeat_cron, 'new', job_enabled, timing_string, cron_task, cron_extra_args)

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
    def __init__(self, parent, *args, **kw):
        self.parent = parent
        super(cron_job_dialog, self).__init__(*args, **kw)
        self.InitUI(parent)
        self.SetSize((850, 430))
        self.SetTitle("Cron Job Editor")
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def InitUI(self, parent):
        shared_data = self.parent.parent.shared_data
        #these need to be set before the dialog is created
        cron_path     = parent.cron_path_toedit
        cron_task     = parent.cron_task_toedit
        cron_args     = parent.cron_args_toedit
        cron_type     = parent.cron_type_toedit
        cron_everystr = parent.cron_everystr_toedit
        cron_everynum = parent.cron_everynum_toedit
        cron_enabled  = parent.cron_enabled_toedit
        cron_min      = parent.cron_min_toedit
        cron_hour     = parent.cron_hour_toedit
        cron_day      = parent.cron_day_toedit
        cron_month    = parent.cron_month_toedit
        cron_dow      = parent.cron_dow_toedit
        #draw the pannel
        pnl = wx.Panel(self)
        ## universal controls

        self.SetFont(shared_data.title_font)
        title = wx.StaticText(self,  label='Cron job editor')

        self.SetFont(shared_data.info_font)
        tm_label = wx.StaticText(self,  label='timing method;')
        cron_type_opts = ['startup', 'repeating', 'one time']
        self.cron_type_combo = wx.ComboBox(self, choices = cron_type_opts, size=(150, 30))
        self.cron_type_combo.Bind(wx.EVT_COMBOBOX, self.cron_type_combo_go)
        timing_m_sizer = wx.BoxSizer(wx.HORIZONTAL)
        timing_m_sizer.Add(tm_label, 0, wx.ALL, 2)
        timing_m_sizer.Add(self.cron_type_combo, 0, wx.ALL, 2)


        # folder path
        path_l = wx.StaticText(self,  label='path;')
        script_path = shared_data.remote_pigrow_path + "scripts"
        cron_path_opts = [script_path + "/cron/",
                          script_path + "/autorun/",
                          script_path + "/switches/",
                          script_path + "/sensors/",
                          script_path + "/visualisation/"]
        self.cron_path_combo = wx.ComboBox(self, style=wx.TE_PROCESS_ENTER, choices=cron_path_opts, size=(525, 30))
        self.cron_path_combo.Bind(wx.EVT_TEXT_ENTER, self.cron_path_combo_go)
        self.cron_path_combo.Bind(wx.EVT_COMBOBOX, self.cron_path_combo_go)
        path_sizer = wx.BoxSizer(wx.HORIZONTAL)
        path_sizer.Add(path_l, 0, wx.ALL, 2)
        path_sizer.Add(self.cron_path_combo, 0, wx.ALL, 2)

        # script name
        cron_script_opts = self.get_cronable_scripts(cron_path) #send the path of the folder get script list
        self.cron_script_cb = wx.ComboBox(self, choices=cron_script_opts, size=(600, 30))
        show_cat_butt = wx.Button(self, label='view script')
        show_cat_butt.Bind(wx.EVT_BUTTON, self.cat_script)
        script_sizer = wx.BoxSizer(wx.HORIZONTAL)
        script_sizer.Add(self.cron_script_cb, 0, wx.ALL, 2)
        script_sizer.Add(show_cat_butt, 0, wx.ALL, 2)

        # extra args
        args_l = wx.StaticText(self,  label='Extra args;', pos=(10, 110))
        self.cron_args_tc = wx.TextCtrl(self, pos=(100, 110), size=(525, 30))
        show_help_butt = wx.Button(self, label='show help', pos=(625, 110))
        show_help_butt.Bind(wx.EVT_BUTTON, self.show_help)
        args_sizer = wx.BoxSizer(wx.HORIZONTAL)
        args_sizer.Add(args_l, 0, wx.ALL, 2)
        args_sizer.Add(self.cron_args_tc, 0, wx.ALL, 2)
        args_sizer.Add(show_help_butt, 0, wx.ALL, 2)

        # cron job enabled
        self.cron_enabled_cb = wx.CheckBox(self,  label='Enabled')

        ### set universal controls data...
        self.cron_type_combo.SetValue(cron_type)
        self.cron_path_combo.SetValue(cron_path)
        self.cron_args_tc.SetValue(cron_args)
        self.cron_script_cb.SetValue(cron_task)
        self.cron_enabled_cb.SetValue(cron_enabled)


        # draw and hide optional option controlls
        ## for repeating cron jobs
        self.cron_rep_every = wx.StaticText(self,  label='Every ')
        self.cron_every_num_tc = wx.TextCtrl(self, size=(40, 30))  #box for number, name num only range set by repeat_opt
        self.cron_every_num_tc.Bind(wx.EVT_CHAR, self.onChar)
        cron_repeat_opts = ['min', 'hour', 'day', 'month', 'dow']
        self.cron_repeat_opts_cb = wx.ComboBox(self, choices = cron_repeat_opts, size=(100, 30))
        # set vals
        self.cron_rep_every.Hide()
        self.cron_every_num_tc.Hide()
        self.cron_repeat_opts_cb.Hide()
        self.cron_repeat_opts_cb.SetValue(cron_everystr)
        self.cron_every_num_tc.SetValue(cron_everynum)
        rep_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rep_sizer.Add(self.cron_rep_every, 0, wx.ALL, 2)
        rep_sizer.Add(self.cron_every_num_tc, 0, wx.ALL, 2)
        rep_sizer.Add(self.cron_repeat_opts_cb, 0, wx.ALL, 2)


        ## for one time cron jobs
        self.timed_txt = wx.StaticText(self,  label='Time; ')
        self.cron_timed_min_tc = wx.TextCtrl(self, size=(40, 30)) #limit to 0-23
        self.cron_timed_min_tc.SetValue(cron_min)
        self.cron_timed_min_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_hour_tc = wx.TextCtrl(self, size=(40, 30)) #limit to 0-59
        self.cron_timed_hour_tc.SetValue(cron_hour)
        self.cron_timed_hour_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_day_tc = wx.TextCtrl(self, size=(40, 30)) #limit to 0-59
        self.cron_timed_day_tc.SetValue(cron_day)
        self.cron_timed_day_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_month_tc = wx.TextCtrl(self, size=(40, 30)) #limit to 0-59
        self.cron_timed_month_tc.SetValue(cron_month)
        self.cron_timed_month_tc.Bind(wx.EVT_CHAR, self.onChar)
        self.cron_timed_dow_tc = wx.TextCtrl(self, size=(40, 30)) #limit to 0-59
        self.cron_timed_dow_tc.SetValue(cron_dow)
        self.cron_timed_dow_tc.Bind(wx.EVT_CHAR, self.onChar)

        time_sizer = wx.BoxSizer(wx.HORIZONTAL)
        time_sizer.Add(self.timed_txt, 0, wx.ALL, 2)
        time_sizer.Add(self.cron_timed_min_tc, 0, wx.ALL, 2)
        time_sizer.Add(self.cron_timed_hour_tc, 0, wx.ALL, 2)
        time_sizer.Add(self.cron_timed_day_tc, 0, wx.ALL, 2)
        time_sizer.Add(self.cron_timed_month_tc, 0, wx.ALL, 2)
        time_sizer.Add(self.cron_timed_dow_tc, 0, wx.ALL, 2)

        self.timed_txt2 = wx.StaticText(self,  label='[min : hour : day : month : day of the week]')

                #Bottom Row of Buttons
        self.SetFont(shared_data.button_font)
        okButton = wx.Button(self, label='Save')
        okButton.Bind(wx.EVT_BUTTON, self.do_upload)
        closeButton = wx.Button(self, label='Cancel')
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(okButton, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)
        buttons_sizer.Add(closeButton, 0, wx.ALL, 2)
        buttons_sizer.AddStretchSpacer(1)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        #main_sizer.AddStretchSpacer(1)
        main_sizer.Add(path_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(script_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(args_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.cron_enabled_cb, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(timing_m_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        main_sizer.Add(rep_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(time_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.Add(self.timed_txt2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        main_sizer.AddStretchSpacer(1)
        main_sizer.Add(buttons_sizer, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetSizer(main_sizer)
        self.set_control_visi()

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
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        if script_path == "" or script_name == "":
            return None
        # Run a cat command on the pi to read script
        script_to_ask = script_path + script_name
        script_text, error_text = self.parent.parent.link_pnl.run_on_pi("cat " + str(script_to_ask))
        if not error_text == '':
            msg_text =  "Error reading script " + script_to_ask + " \n\n"
            msg_text += str(error_text)
        else:
            msg_text = script_to_ask + '\n\n'
            msg_text += str(script_text)
        dbox = self.parent.parent.shared_data.scroll_text_dialog(None, msg_text, script_to_ask, False)
        dbox.ShowModal()
        dbox.Destroy()

    def get_cronable_scripts(self, script_path):
        #this reads the files in the path provided
        #then creates a list of all .py and .sh scripts in that folder
        cron_opts = []
        try:
            print("reading " + str(script_path))
            out, error_text = self.parent.parent.link_pnl.run_on_pi("ls " + str(script_path))
            cron_dir_list = out.split('\n')
            for filename in cron_dir_list:
                if filename.endswith("py") or filename.endswith('sh'):
                    cron_opts.append(filename)
        except Exception as e:
            print(("ERROR getting scripts! " + str(e)))
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
            self.timed_txt.Show()
            self.timed_txt2.Show()
            self.cron_timed_min_tc.Show()
            self.cron_timed_hour_tc.Show()
            self.cron_timed_day_tc.Show()
            self.cron_timed_month_tc.Show()
            self.cron_timed_dow_tc.Show()
        elif cron_type == 'repeating':
            self.cron_rep_every.Show()
            self.cron_every_num_tc.Show()
            self.cron_repeat_opts_cb.Show()
            self.timed_txt.Hide()
            self.timed_txt2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
        elif cron_type == 'startup':
            self.cron_rep_every.Hide()
            self.cron_every_num_tc.Hide()
            self.cron_repeat_opts_cb.Hide()
            self.timed_txt.Hide()
            self.timed_txt2.Hide()
            self.cron_timed_min_tc.Hide()
            self.cron_timed_hour_tc.Hide()
            self.cron_timed_day_tc.Hide()
            self.cron_timed_month_tc.Hide()
            self.cron_timed_dow_tc.Hide()
        self.Layout()

    def get_help_text(self, script_to_ask):
        #open an ssh pipe and runs the script with a -h argument
        #
        #WARNING
        #       If the script doesn't support -h args then it'll just run it
        #       this can cause switches to throw, photos to be taken or etc
        if script_to_ask.endswith('sh'):
            return ("Sorry, .sh files don't support help arguments, try viewing it instead.")
        out, error = self.parent.parent.link_pnl.run_on_pi(str(script_to_ask) + " -h")
        return out+error

    def show_help(self, e):
        script_path = self.cron_path_combo.GetValue()
        script_name = self.cron_script_cb.GetValue()
        helpfile = self.get_help_text(str(script_path + script_name))
        dbox = self.parent.parent.shared_data.scroll_text_dialog(None, helpfile, script_name + " help info", False)
        dbox.ShowModal()
        dbox.Destroy()

    def do_upload(self, e):
        #get data from boxes
        #   these are the exit variables, they're only set when ok is pushed
        #   this is to stop any dirty old data mixing in with the correct stuff
        self.job_type = self.cron_type_combo.GetValue()
        self.job_path = self.cron_path_combo.GetValue()
        self.job_script = self.cron_script_cb.GetValue()
        self.job_args = self.cron_args_tc.GetValue()
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
        self.job_enabled = None
        self.job_repeat = None
        self.job_repnum = None
        self.job_min = None
        self.job_hour = None
        self.job_day = None
        self.job_month = None
        self.job_dow = None
        self.Destroy()
