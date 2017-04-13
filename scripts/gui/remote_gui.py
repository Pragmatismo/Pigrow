#!/usr/bin/python
import os, sys
import wx
import datetime
import paramiko # pip install paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#target_address = "pi@192.168.1.11"
#target_pass    = "raspberry"

caps_files = "/caps/" #useful to change when using more than one cam
target_cap_files   = "/home/pi/Pigrow" + caps_files  #can add *.jpg to limit
target_graph_path  = "/home/pi/Pigrow/graphs/"
target_log_path    = "/home/pi/Pigrow/logs/"
target_config_path = "/home/pi/Pigrow/config/"
#target_crontab_path = "/var/spool/cron/crontabs/pi"
cap_type = "jpg"

if sys.platform == 'win32':
    operating_system = 'win'
    basepath = "c:/MinGW/msys/1.0/bin/"
    print(" This is a windows system, how exciting!")
elif sys.platform == 'linux2':
#elif sys.platform.startswith('linux'):
    print(" This is a linux system, great news! best choice!")
    userhome = os.path.expanduser('~')
    basepath = userhome + "/frompigrow/"
    operating_system = 'linux'
else:
    print(" i have no idea what this is?!")
    print sys.platform
    print("hack the system and see if it works as other OS's if you like")
    print("edit the code and add OS = 'linux' or 'win' after this bit of text")
#here. put the os = 'linux' / 'win' here if you want to ignore the auto detect

boxname = "Flower"

def setfilepaths(boxname):
    global capsdir, logsdir, graphdir, configdir
    global dht_log, self_log, switch_log, err_log, conf_file
    capsdir   = basepath + boxname + caps_files
    logsdir   = basepath + boxname + "/logs/"
    graphdir  = basepath + boxname + "/graph/"
    configdir = basepath + boxname + "/config/"
    if not os.path.exists(capsdir):
        os.makedirs(capsdir)
    if not os.path.exists(logsdir):
        os.makedirs(logsdir)
    if not os.path.exists(graphdir):
        os.makedirs(graphdir)
    if not os.path.exists(configdir):
        os.makedirs(configdir)

    dht_log    = logsdir + 'dht22_log.txt'
    self_log   = logsdir + 'selflog.txt'
    switch_log = logsdir + 'switch_log.txt'
    err_log    = logsdir + 'err_log.txt'
    conf_file  = configdir + 'pigrow_config.txt'
setfilepaths(boxname)

def count_caps():
    cap_files = []
    for filefound in os.listdir(capsdir):
        if filefound.endswith(cap_type):
            cap_files.append(filefound)
    return cap_files

def get_box_name(target_ip, target_user, target_pass):
    boxname = None
    found_login = False
    try:
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        found_login = True
        stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
        boxname = stdout.read().strip().split("=")[1]
        print "Pigrow Found; " + boxname
        ssh.close()
    except:
        print("dang - can't connect to pigrow")
        ssh.close()
    return found_login, boxname

def clear_pis_caps(target_ip, target_user, target_pass, theboxname):
    try:
        port = 22
        ssh_tran = paramiko.Transport((target_ip, port))
        print("  - linking transport pipe... " + target_ip + " port:" + str(port))
        ssh_tran.connect(username=target_user, password=target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        listofcaps_onpi = sftp.listdir(target_cap_files)
        print("It has " + str(len(listofcaps_onpi)) + " in it's caps folder " + target_cap_files)
        listofcaps_local = os.listdir(capsdir)
        print("We have " + str(len(listofcaps_local)) + " in it's local folder " + capsdir)
        print("-- Though they might not all be the same rememmber --")
        newcaps = []
        print("Clearing the pi of all images we've already downlaoded...")
        for capfile in listofcaps_onpi:
            if capfile in listofcaps_local:
                filepath  = target_cap_files + capfile
                localpath = capsdir + capfile
                sftp.remove(filepath)
        sftp.close()
        ssh_tran.close()
    except:
        print("ooops sorrys brokes")
        raise
    print("SSH REMOVE loop finished")

def download_caps(target_ip, target_user, target_pass, theboxname):
    rmfrompi = False
    #note this ignores existing files
    if os.path.exists(capsdir) == False:
        os.makedirs(capsdir)
    target_address = target_user + "@" + target_ip
    download_method = 'ssh'
    if download_method == 'ssh':
        try:
            port = 22
            ssh_tran = paramiko.Transport((target_ip, port))
            print("  - connecting transport pipe... " + target_ip + " port:" + str(port))
            ssh_tran.connect(username=target_user, password=target_pass)
            sftp = paramiko.SFTPClient.from_transport(ssh_tran)
            listofcaps_onpi = sftp.listdir(target_cap_files)
            print("It has " + str(len(listofcaps_onpi)) + " in it's caps folder " + target_cap_files)
            listofcaps_local = os.listdir(capsdir)
            print("We have " + str(len(listofcaps_local)) + " in it's local folder " + capsdir)
            extrapics = len(listofcaps_onpi) - len(listofcaps_local)
            print("So there's " + str(extrapics) + " more on the pi")
            print("-- Though they might not all be the same rememmber --")
            newcaps = []
            limitbreak = 0
            ticktocken = 0
            limitbreaklimit = -1 #currently used for testing only.
            print("Downloading all files we don't have, this might takea while...")
            for capfile in listofcaps_onpi:
                if capfile not in listofcaps_local:
                    limitbreak += 1
                    ticktocken += 1
                    if ticktocken > 100:
                        print("..got a hundred more")
                        ticktocken = 0
                    newcaps.append(capfile)
                    filepath = target_cap_files + capfile
                    localpath = capsdir + capfile
                    #print filepath, localpath
                    sftp.get(filepath, localpath)
                    if rmfrompi == True:
                        sftp.remove(filepath)
                if limitbreak == limitbreaklimit:
                    break
            print("Found " + str(len(newcaps)) + " caps files on pi we didn't have")
            listofcaps_after = os.listdir(capsdir)
            print("We now have " + str(len(listofcaps_after)) + " in it's local folder " + capsdir)
            extrapics = len(listofcaps_after) - len(listofcaps_local)
            print("So we grabbed " + str(extrapics) + " more pictures")
            sftp.close()
            ssh_tran.close()
        except:
            print("DANG MESSSED UP")
            raise
        print("SSH copy loop finished")
        #sys.exit()



    elif operating_system == 'linux' and download_method == 'rsync':
        try:
            print("Copying files...   (this may time some time)")
            os.system("rsync --ignore-existing -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass+" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_cap_files+" "+capsdir)
            print("Files Grabbed")
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    elif operating_system == 'win':
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

tdht_log = "dht22_log.txt"
tself_log = "selflog.txt"
terr_log = "err_log.txt"
tswitch_log = "switch_log.txt"

def log_times():
    dht_ff = False
    sl_ff = False
    err_ff = False
    switch_ff = False
    for filefound in os.listdir(logsdir):
        print filefound
        if filefound == tdht_log:
            dht_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == tself_log:
            sl_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == terr_log:
            err_ff = os.path.getmtime(logsdir+filefound)
        elif filefound == tswitch_log:
            switch_ff = os.path.getmtime(logsdir+filefound)
    return dht_ff, sl_ff, err_ff, switch_ff

def download_logs(target_ip, target_user, target_pass, theboxname):
    #note this overwrites existing local files
    target_address = target_user + "@" + target_ip
 #get last edit times for files
    dht_ff, sl_ff, err_ff, switch_ff  = log_times()
 #downloads the files
    logsdir = basepath + theboxname + "/logs/"
    if os.path.exists(logsdir) == False:
        os.makedirs(logsdir)
    if operating_system == 'linux':
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
    elif operating_system == 'win':
        try:
            print("Copying files...")
            os.chdir(winrsyncpath)
            rsync_cmd = "rsync.exe " + target_address +":"+ target_log_path + " logs"
            print rsync_cmd
            os.system(rsync_cmd)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
  #get file tiems again and check if they've changed
    dht_fa, sl_fa, err_fa, switch_fa  = log_times()
    if dht_ff == dht_fa:
        message = "  DHT log not updated, \n"
    else:
        message = "  DHT log which is " + str(round(dht_fa - dht_ff)) + " sec newer \n"
    if sl_ff == sl_fa:
        message += "  Self log not updated, \n"
    else:
        message += "  Self log which is " + str(round(sl_fa - sl_ff)) + " min newer \n"
    if switch_ff == switch_fa:
        message += "  Switch log not updated, \n"
    else:
        message += "  Switch log which is " + str(round(switch_fa - switch_ff)) + " min newer \n"
    if err_ff == err_fa:
        message += "  Error log not updated, \n"
    else:
        message += "  Error log which is " + str(round(err_fa - err_ff)) + " min newer \n"
    return message

def download_graphs(target_ip, target_user, target_pass, theboxname):
    #note this overwrites existing local files
    graphdir = basepath + theboxname + "/graph/"
    target_address = target_user + "@" + target_ip
    if operating_system == 'linux':
        try:
            print("Grabbing graphs, this may take a short while...")
            cmd = "rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass
            cmd +=" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "+target_address+":"+target_graph_path+" "+graphdir
            os.system(cmd)
            print("local graphs updated as " + graphdir)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    elif operating_system == 'win':
        try:
            print("Copying graphs...")
            os.chdir(winrsyncpath)
            rsync_cmd = "rsync.exe " + target_address +":"+ target_graph_path + " graphs"
            print rsync_cmd
            os.system(rsync_cmd)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

def download_config(target_ip, target_user, target_pass, theboxname):
    #note this overwrites existing local files
    configdir = basepath + theboxname + "/config/"
    target_address = target_user + "@" + target_ip
    if operating_system == 'linux':
        try:
            print("Grabbing config, this may take a short while...")
            cmd = "rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass
            cmd +=" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "
            cmd += target_address +":"+ target_config_path +" "+ configdir
            os.system(cmd)
            #cmd = "rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_pass
            #cmd +=" ssh -o StrictHostKeyChecking=no -l "+target_address+"\" "
            #cmd += target_address +":"+ target_crontab_path +" "+ configdir
            #os.system(cmd)
               #The above fails becayse of file permissions on the pi...
            print("local pi config files updated at " + configdir)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    elif operating_system == 'win':
        try:
            print("Copying config...")
            os.chdir(winrsyncpath)
            rsync_cmd = "rsync.exe " + target_address +":"+ target_config_path + " config"
            print rsync_cmd
            os.system(rsync_cmd)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
    print("Config files download")

def load_dhtlog(retdate=False, limit_days=False, limit_num=False):
    print("Loading dht log")
    if os.path.exists(dht_log):
        dht_dates = []
        dht_temps = []
        dht_humids = []
        #hours_to_show = 999999 #currently not used
        thetime = datetime.datetime.now()
        with open(dht_log, "r") as f:
            logitem = f.read()
            logitem = logitem.split("\n")
        print('Log contains ' + str(len(logitem)) + ' readings.')
        if limit_days != False:
            oldest_allowed_date = thetime - datetime.timedelta(hours=limit_days)
        curr_line = len(logitem) - 1
        limit_line = curr_line - limit_num
        while curr_line >= 0:
            try:
                item = logitem[curr_line]
                item = item.split(">")
                date = item[2].split(".")
                date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
                if limit_num != False:
                    if curr_line <= limit_line:
                        break
                if limit_days != False:
                    if date < oldest_allowed_date:
                        break
                if retdate == True:
                    print(" - found date of last log entry...")
                    return date
                hum  = float(item[1])
                temp = float(item[0])
                dht_humids.append(hum)
                dht_temps.append(temp)
                dht_dates.append(date)
                curr_line = curr_line - 1
            except:
                print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
                curr_line = curr_line - 1
        if retdate == True:
            print(" - log empty, no date to return...")
            return 'none'

        dht_humids.reverse()
        dht_temps.reverse()
        dht_dates.reverse()
        if len(dht_humids) > 0:
            return dht_humids, dht_temps, dht_dates
        else:
            print("nothing found in dht file? maybe it's bad?")
            return "none"
    else:
        return "none"

def load_selflog(retdate=False):
    log_dic = {}    # Reused for every line of the log file
                         ## Lists used to make graphs.
    dates = []      # Used for all the graphs
    cpu_a1 = []    #
    cpu_a5 = []    #  cpu load average for one min, five min, fifteen min
    cpu_a15 = []   #
    mem_a = []      #
    mem_f = []      #  mem avail, full, total
    mem_t = []      #
    disk_p = []    #
    disk_f = []    #  Disk Percent, Full, total, used
    disk_t = []    #
    disk_u = []    #
    up = []         # uptime
    if os.path.exists(self_log):
        print("Loading Selflog")
        with open(self_log, "r") as f:
            for line in f:
                try:
                    line = line.split('>')
                    for item in line:
                        item = item.split("=")
                        if len(item) == 1:
                            break
                        name = item[0].strip()
                        value = item[1].strip()
                        log_dic[name]=value
                #time and date
                    date = log_dic['timenow'].split('.')[0]
                    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    if retdate == True:
                        return date
                    dates.append(date)
                #CPU LOAD AVE
                    load_ave1 = log_dic['load_ave1']
                    load_ave5 = log_dic['load_ave5']
                    load_ave15 = log_dic['load_ave15']
                    cpu_a1.append(load_ave1)
                    cpu_a5.append(load_ave5)
                    cpu_a15.append(load_ave15)
                #mem space
                    mem_avail = int(log_dic['memavail'].split(" ")[0])/1024
                    mem_free = int(log_dic['memfree'].split(" ")[0])/1024
                    mem_total = int(log_dic['memtotal'].split(" ")[0])/1024
                    mem_a.append(mem_avail)
                    mem_f.append(mem_free)
                    mem_t.append(mem_total)
                #Disk fullness
                    disk_percent = log_dic['disk_percent']
                    disk_free = int(log_dic['disk_free'])/1024/1024
                    disk_total = int(log_dic['disk_total'])/1024/1024
                    disk_used = int(log_dic['disk_used'])/1024/1024
                    disk_p.append(disk_percent)
                    disk_f.append(disk_free)
                    disk_t.append(disk_total)
                    disk_u.append(disk_used)
                #uptime
                    uptime = log_dic['uptime_sec']
                    up.append(uptime)
                except:
                    print("didn't parse" + str(item))
        return "none" #THIS NEEDS TO CHANGE WHEN THE LOG GETS USED FOR GRAPHS
    else:
        print("no selflog")
        return "none"


def load_switchlog(retdate=False, limit_days=False, limit_num=False, thelog=switch_log):
    print("loading " + str(thelog))
    switchlog = []
    if os.path.exists(thelog):
        print("  -log found")
        with open(thelog, "r") as f:
            logitem = f.read()
            logitem = logitem.split("\n")
        print('Adding ' + str(len(logitem)) + ' readings from log.')
        if limit_days != False:
            oldest_allowed_date = thetime - datetime.timedelta(hours=limit_days)
        curr_line = len(logitem) - 1
        limit_line = curr_line - limit_num
        gotdate = False
        while curr_line >= 0:
            try:
                item = logitem[curr_line]
                #print item
                item = item.split("@")
                date = item[1].split(".")[0]
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                gotdate = True
                switch_script = item[0]
                switch_message = item[2]
                if limit_num != False:
                    if curr_line <= limit_line:
                        break
                if limit_days != False:
                    if date < oldest_allowed_date:
                        break
                if retdate == True:
                    if gotdate == True:
                        return date
                    else:
                        print("No valid entries in the log, bad log maybe?")
                        return 'none'
                switch_list = [switch_script, date, switch_message]
                switchlog.append(switch_list)
                curr_line = curr_line - 1
            except:
                #print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
                curr_line = curr_line - 1
        print("Returning switch log")
        if retdate == True:
            return "none" #it's here because it didn't find one
        if len(switchlog) == 0:
            return "none"
        else:
            return switchlog
    else:
        print("no " + str(thelog))
        return 'none'

def load_settings(sets=conf_file):
    sets_dic = {}
    try:
        with open(sets, "r") as f:
            for line in f:
                s_item = line.split("=")
                sets_dic[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary
        return sets_dic
    except:
        print("could get info from settings file")
        sets_dic = {'none':none}
        return sets_dic

class Pigrow(wx.Frame):
    def __init__(self, *args, **kw):
        super(Pigrow, self).__init__(*args, **kw)
        self.InitUI()

    def InitUI(self):

     #menu bar
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        self.menu_seek = fileMenu.Append(wx.ID_ANY, 'Seek next Pi', 'Search the local network for the next pi')
        self.menu_settings = fileMenu.Append(wx.ID_ANY, 'Pi settings', 'Edit and update pigrow config files')
        self.Bind(wx.EVT_MENU, self.seek_pi, self.menu_seek)
        fileMenu.AppendSeparator()
        imp = wx.Menu()
        import_set = imp.Append(wx.ID_ANY, 'soon-Import settings')
        import_dht = imp.Append(wx.ID_ANY, 'Import sensor log')
        import_swi = imp.Append(wx.ID_ANY, 'soon-Import switch log')
        import_cap = imp.Append(wx.ID_ANY, 'Import caps folder')
        fileMenu.AppendMenu(wx.ID_ANY, 'Import', imp)
        menu_upload_settings = fileMenu.Append(wx.ID_ANY, 'soon -Upload Settings', 'Upload settings to selected pi')
        menu_exit = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        menubar.Append(fileMenu, '&File')
        self.Bind(wx.EVT_MENU, self.imp_dht, import_dht)
        self.Bind(wx.EVT_MENU, self.imp_caps, import_cap)
        self.Bind(wx.EVT_MENU, self.OnClose, menu_exit)
        renderMenu = wx.Menu()
        menu_render_timelapse = renderMenu.Append(wx.ID_ANY, 'Timelapse')
        menu_render_capsgraph = renderMenu.Append(wx.ID_ANY, 'soon- Caps Graph')
        menu_render_dhtgraph = renderMenu.Append(wx.ID_ANY, 'DHT Graph')
        menu_render_selfgraph = renderMenu.Append(wx.ID_ANY, 'soon- Selflog Graph')
        menu_render_report = renderMenu.Append(wx.ID_ANY, 'soon - Report')
        self.Bind(wx.EVT_MENU, self.render_timelapse, menu_render_timelapse)
        self.Bind(wx.EVT_MENU, self.render_dht, menu_render_dhtgraph)
        menubar.Append(renderMenu, '&Render')
        downMenu = wx.Menu()
        menu_download = downMenu.Append(wx.ID_ANY, 'Download from Pi')
        menu_clear_got = downMenu.Append(wx.ID_ANY, 'clear got images from pi')
        self.Bind(wx.EVT_MENU, self.download, menu_download)
        self.Bind(wx.EVT_MENU, self.clear_got, menu_clear_got)
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
        self.v_scale = visMenu.Append(wx.ID_ANY, 'Resize', 'Toggle Image Resize', kind=wx.ITEM_CHECK)
        visMenu.AppendSeparator()
        self.v_cap = visMenu.Append(wx.ID_ANY, 'Most Recent cap', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_hourA = visMenu.Append(wx.ID_ANY, 'Last Hour Gif', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_dayA = visMenu.Append(wx.ID_ANY, 'Last Day Gif', 'Shows most recent image', kind=wx.ITEM_RADIO)
        self.v_capgr = visMenu.Append(wx.ID_ANY, 'Caps Graphs', 'Self log graphs', kind=wx.ITEM_RADIO)
        self.v_selfgr = visMenu.Append(wx.ID_ANY, 'Self Graphs', 'Self log graphs', kind=wx.ITEM_RADIO)

        #self.Bind(wx.EVT_MENU, self.checkbox_big, self.v_cap)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files),  self.v_scale)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files),  self.v_cap)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files), self.v_hourA)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files), self.v_dayA)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files), self.v_capgr)
        self.Bind(wx.EVT_MENU, lambda event: self.checkbox_big(event, cap_files), self.v_selfgr)
        menubar.Append(visMenu, 'Show')

        self.SetMenuBar(menubar)

     #connect pannel
        pnl = wx.Panel(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        font_big = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        font_small = wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        heading = wx.StaticText(self, label='Pigrow Control', pos=(300, 15))
        heading.SetFont(font_big)

        wx.StaticText(self,  label='address', pos=(10, 20))
        self.tb_ip = wx.TextCtrl(self, pos=(125, 25), size=(150, 25))
        self.tb_ip.SetValue("192.168.1.0")

        wx.StaticText(self,  label='Username', pos=(10, 60))
        self.tb_user = wx.TextCtrl(self, pos=(125, 60), size=(150, 25))
        self.tb_user.SetValue("pi")

        wx.StaticText(self,  label='Password', pos=(10, 95))
        self.tb_pass = wx.TextCtrl(self, pos=(125, 95), size=(150, 25))
        self.tb_pass.SetValue("raspberry")

        self.last_acc = wx.StaticText(self,  label='Last Accessed; ', pos=(10, 140))
     #local storage
        wx.StaticText(self,  label='Name; ', pos=(10, 180))
        self.boxname_text = wx.StaticText(self,  label='boxname ', pos=(90, 180))
        self.update_boxname(boxname)
        self.cap_thumb = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(150, 150), pos=(85, 210))
        self.cap_thumb.Bind(wx.EVT_LEFT_DOWN, self.clickgraph)
        wx.StaticText(self,  label='Caps ; ', pos=(5, 210))
        self.cap_len_text = wx.StaticText(self,  label='Caps ; ', pos=(20, 235))
        self.cap_lf_text = wx.StaticText(self,  label=' ', pos=(10, 315))
        self.cap_ff_text = wx.StaticText(self, label=' ', pos=(10, 340))
        cap_files = self.update_caps(capsgraph=False)
    # large image
        self.bigpic = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(500, 500), pos=(300, 0))
        self.update_bigpic(cap_files)
    # DHT log
        self.last_DHT_text = wx.StaticText(self,  label='Last DHT; ', pos=(5, 380))
        self.update_dht()
        self.last_self_text = wx.StaticText(self,  label='Last Self; ', pos=(5, 405))
        self.update_selflog()
        self.last_switch_text = wx.StaticText(self,  label='Last Switch; ', pos=(5, 430))
        self.update_switch()
        self.last_err_text = wx.StaticText(self,  label='Last Err; ', pos=(5, 455))
        self.update_err()
    #read pigrow settings file
        self.conf_boxname_text = wx.StaticText(self,  label='Box Name ', pos=(5, 490))
        self.relay1_btn = wx.Button(self, label='Relay 1', pos=(100, 500))
        self.relay2_btn = wx.Button(self, label='Relay 2', pos=(100, 540))
        self.relay3_btn = wx.Button(self, label='Relay 3', pos=(100, 580))
        self.relay4_btn = wx.Button(self, label='Relay 4', pos=(100, 620))
        self.relay1_btn.Bind(wx.EVT_BUTTON, self.relay1_btn_click)
        self.relay2_btn.Bind(wx.EVT_BUTTON, self.relay2_btn_click)
        self.relay3_btn.Bind(wx.EVT_BUTTON, self.relay3_btn_click)
        self.relay4_btn.Bind(wx.EVT_BUTTON, self.relay4_btn_click)
        #and the off buttons
        self.relay1_btn_off = wx.Button(self, label='Off', pos=(200, 500))
        self.relay2_btn_off = wx.Button(self, label='Off', pos=(200, 540))
        self.relay3_btn_off = wx.Button(self, label='Off', pos=(200, 580))
        self.relay4_btn_off = wx.Button(self, label='Off', pos=(200, 620))
        self.relay1_btn_off.Bind(wx.EVT_BUTTON, self.relay1_btn_off_click)
        self.relay2_btn_off.Bind(wx.EVT_BUTTON, self.relay2_btn_off_click)
        self.relay3_btn_off.Bind(wx.EVT_BUTTON, self.relay3_btn_off_click)
        self.relay4_btn_off.Bind(wx.EVT_BUTTON, self.relay4_btn_off_click)
        #pointless text
        self.relay1_text = wx.StaticText(self,  label='Relay 1; ', pos=(5, 515))
        self.relay2_text = wx.StaticText(self,  label='Relay 2; ', pos=(5, 550))
        self.relay3_text = wx.StaticText(self,  label='Relay 3; ', pos=(5, 585))
        self.relay4_text = wx.StaticText(self,  label='Relay 4; ', pos=(5, 120))
        self.update_gpiotext()




     #Opening the window
        self.SetSize((1000, 900))
        self.SetTitle('Pigrow Control')
        self.Centre()
        self.Show(True)

    def throw_switch(self, relay_device, direction):
        print("USER Want's to flip the " + relay_device)
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        ssh.connect(target_ip, username=target_user, password=target_pass, timeout=3)
        print "Connected to " + target_ip
        if direction == 'on':
            print("Turning " + relay_device + " on...")
            stdin, stdout, stderr = ssh.exec_command("/home/pi/Pigrow/scripts/switches/" + relay_device + "_on.py")
        elif direction == 'off':
            print("Turning " + relay_device + " off...")
            stdin, stdout, stderr = ssh.exec_command("/home/pi/Pigrow/scripts/switches/" + relay_device + "_off.py")
        else:
            print("OI! YOU CODED THIS WRONG! YOU NEED TO TELL IT WHICH WAY TO FLIP!")
        print stdout.read().strip()
        ssh.close()


    def relay1_btn_click(self, e):
        text = self.relay1_btn.GetLabel()
        self.throw_switch(text, 'on')

    def relay2_btn_click(self, e):
        text = self.relay2_btn.GetLabel()
        self.throw_switch(text, 'on')

    def relay3_btn_click(self, e):
        text = self.relay3_btn.GetLabel()
        self.throw_switch(text, 'on')

    def relay4_btn_click(self, e):
        text = self.relay4_btn.GetLabel()
        self.throw_switch(text, 'on')

#off buttons
    def relay1_btn_off_click(self, e):
        text = self.relay1_btn.GetLabel()
        self.throw_switch(text, 'off')

    def relay2_btn_off_click(self, e):
        text = self.relay2_btn.GetLabel()
        self.throw_switch(text, 'off')

    def relay3_btn_off_click(self, e):
        text = self.relay3_btn.GetLabel()
        self.throw_switch(text, 'off')

    def relay4_btn_off_click(self, e):
        text = self.relay4_btn.GetLabel()
        self.throw_switch(text, 'off')

    def askpi_filenums(self, host, target_user, target_pass):
        port = 22
        ssh_tran = paramiko.Transport((host, port))
        print("  - connecting transport pipe... " + host + " port:" + str(port))
        ssh_tran.connect(username=target_user, password=target_pass)
        sftp = paramiko.SFTPClient.from_transport(ssh_tran)
        listofcaps_onpi = sftp.listdir(target_cap_files)
        print("It has " + str(len(listofcaps_onpi)) + " in it's caps folder " + target_cap_files)
        if os.path.exists(capsdir):
            listofcaps_local = os.listdir(capsdir)
            print("We have " + str(len(listofcaps_local)) + " in it's local folder " + capsdir)
            print("-- Though they might not all be the same rememmber --")
        else:
            print("No local information, download to get some..")
        sftp.close()
        ssh_tran.close()
        return listofcaps_onpi, listofcaps_local



    def seek_pi(self, e):
        target_ip = self.tb_ip.GetValue()
        start_from = int(target_ip.split('.')[3]) + 1
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        print("seeking pi...")
        lastdigits = len(str(start_from))
        hostrange = target_ip[:-lastdigits]
        for testloc in range(start_from,255):
            host = hostrange + str(testloc)
            ctry = 1
            while True:
                print("Trying to connect to " + host)
                try:
                    ssh.connect(host, username=target_user, password=target_pass, timeout=3)
                    print "Connected to " + host
                    self.tb_ip.SetValue(host)
                    stdin, stdout, stderr = ssh.exec_command("cat /home/pi/Pigrow/config/pigrow_config.txt | grep box_name")
                    boxname = stdout.read().strip().split("=")[1]
                    print "Pigrow Found; " + boxname
                    #print stdin, stdout, stderr
                    ssh.close()
                    setfilepaths(boxname)
                    listofcaps_onpi, listofcaps_local = self.askpi_filenums(host, target_user, target_pass)
                    print("Pi located, disconnected ssh session")
                    self.update_boxname(boxname)
                    return host, boxname #doens't return it to anyone at the mo
                except paramiko.AuthenticationException:
                    print "Authentication failed when connecting to " + str(host)
                    pass
                except:
                    print "Could not SSH to " + host + ", waiting for it to start"
                    #raise  #this for testing only
                    ctry += 1


           # If we could not connect within time limit
                if ctry == 3:
                    print "Could not connect to " + host + " Giving up"
                    break


    def update_gpiotext(self):
        self.relay1_btn.Disable()
        self.relay2_btn.Disable()
        self.relay3_btn.Disable()
        self.relay4_btn.Disable()
        self.relay1_btn_off.Disable()
        self.relay2_btn_off.Disable()
        self.relay3_btn_off.Disable()
        self.relay4_btn_off.Disable()
        setdic = load_settings(sets=conf_file)
        if len(setdic) > 1:
            self.conf_boxname_text.SetLabel(setdic['box_name']) #this is now pointless
            gpiodevices = []
            for key, value in setdic.iteritems():
                if key[0:4] == 'gpio':
                    if len(key.split('_')) == 2:
                        if value != '':
                            if key == 'gpio_dht22sensor':
                                pass
                            else:
                                gpiodevices.append(key.split('_')[1])
                            print key, value

            if len(gpiodevices) >= 1:
                self.relay1_text.SetLabel(gpiodevices[0])
                self.relay1_btn.SetLabel(gpiodevices[0])
                self.relay1_btn.Enable()
                self.relay1_btn_off.Enable()
            if len(gpiodevices) >= 2:
                self.relay2_text.SetLabel(gpiodevices[1])
                self.relay2_btn.SetLabel(gpiodevices[1])
                self.relay2_btn.Enable()
                self.relay2_btn_off.Enable()
            if len(gpiodevices) >= 3:
                self.relay3_text.SetLabel(gpiodevices[2])
                self.relay3_btn.SetLabel(gpiodevices[2])
                self.relay3_btn.Enable()
                self.relay3_btn_off.Enable()
            if len(gpiodevices) >= 4:
                self.relay4_text.SetLabel(gpiodevices[3])
                self.relay4_btn.SetLabel(gpiodevices[3])
                self.relay4_btn.Enable()
                self.relay4_btn_off.Enable()


        else:
            self.boxname_text.SetLabel('No settings file')
            self.relay1_text.SetLabel('No Settings file')

    def update_err(self):
        self_date = load_switchlog(retdate=True, thelog=err_log)
        if self_date != "none":
            self_ago = datetime.datetime.now() - self_date
            self.last_err_text.SetLabel('Last Error; ' + str(self_ago).split(".")[0])
        else:
            self.last_err_text.SetLabel('No Error log')

    def update_switch(self):
        self_date = load_switchlog(retdate=True, thelog=switch_log)
        print self_date
        if self_date != "none":
            self_ago = datetime.datetime.now() - self_date
            self.last_switch_text.SetLabel('Last switch; ' + str(self_ago).split(".")[0])
        else:
            self.last_switch_text.SetLabel('No switch log')

    def update_selflog(self):
        self_date = load_selflog(retdate=True)
        if self_date != "none":
            self_ago = datetime.datetime.now() - self_date
            self.last_self_text.SetLabel('Last selflog; ' + str(self_ago).split(".")[0])
        else:
            self.last_self_text.SetLabel('No self log')

    def update_dht(self):
        dht_date = load_dhtlog(retdate=True)
        if dht_date != 'none':
            dht_ago = datetime.datetime.now() - dht_date
        else:
            dht_ago = 'No DHT log'
        self.last_DHT_text.SetLabel('Last DHT; ' + str(dht_ago).split(".")[0])

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.DrawLine(10, 170, 275, 170)

    def imp_caps(self, e):
        global capsdir
        openFileDialog = wx.FileDialog(self, "Select caps folder", "", "", "JPG files (*.jpg)|*.jpg", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.SetMessage("Select an image from the caps folder you want to import")
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return
        new_cap_path = openFileDialog.GetPath()
        capsdir = os.path.split(new_cap_path)
        print capsdir
        capsdir = capsdir[0]
        cap_files = self.update_caps()
        print capsdir

    def imp_dht(self, e):
        openFileDialog = wx.FileDialog(self, "Select DHT Log file", "", "", "TXT files (*.txt)|*.txt", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openFileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed idea...
        new_dht_log = openFileDialog.GetPath()

    def OnClose(self, e):
        print("Bye!")
        self.Close(True)

    def render_timelapse(self, e):

        print("This should call the module which makes the timelapse gui")
        #cmd = '../visualisation/timelapse_assemble.py caps=' + capsdir + " of=" + graphdir
        #cmd += 'guimade.mp4 ow=r dc=day3'
        #cmd += 'guimade.gif ow=r dc=hour1'
        #print cmd
        #os.system(cmd)
        #playcmd = 'vlc ' + graphdir + 'guimade.mp4'
        #print playcmd
        #os.system(playcmd)

    def render_dht(self, e):
        print("This should call the module which makes the dht graph gui")
        print("for now it just runs the pigrow script with arguments")
        cmd = "../visualisation/temp_graph.py log=" + dht_log
        cmd += " out=" + graphdir + "dht_temp_graph.png"
        print cmd
        os.system(cmd)
        cmd = "../visualisation/humid_graph.py log=" + dht_log
        cmd += " out=" + graphdir + "dht_humid_graph.png"
        print cmd
        os.system(cmd)
        os.system("gpicview " + graphdir + "dht_temp_graph.png")



    def clickgraph(self, e):
        cap_s_path = graphdir + 'caps_filesize_graph.png'
        cap_size_graph = wx.Image(cap_s_path, wx.BITMAP_TYPE_ANY)
        cap_d_path = graphdir + 'caps_timediff_graph.png'
        cap_dif_graph = wx.Image(cap_d_path, wx.BITMAP_TYPE_ANY)
        hpos = cap_size_graph.GetWidth() + 5
        self.capgraph = wx.Frame(None, title='Cap Graph', size=(hpos*2, cap_size_graph.GetHeight()))
        self.cappic = wx.Panel(self.capgraph)
        self.cap_top = wx.StaticBitmap(self.capgraph, bitmap=wx.EmptyBitmap(150, 150), pos=(5, 5))
        self.cap_bot = wx.StaticBitmap(self.capgraph, bitmap=wx.EmptyBitmap(150, 150), pos=(hpos, 5))
        self.cap_top.SetBitmap(wx.BitmapFromImage(cap_size_graph))
        self.cap_bot.SetBitmap(wx.BitmapFromImage(cap_dif_graph))
        self.capgraph.Show()

    def update_boxname(self, boxname):
        self.boxname_text.SetLabel(str(boxname))


    def update_caps(self, capsgraph=True):
        cap_files = []
        for filefound in os.listdir(capsdir):
            if filefound.endswith(cap_type):
                cap_files.append(filefound)
        if len(cap_files) > 1:
            self.cap_len_text.SetLabel(' ' + str(len(cap_files)))
            cap_files.sort()
            lastcapdate = float(cap_files[-1].split(".")[0].split("_")[-1])
            firstcapdate = float(cap_files[0].split(".")[0].split("_")[-1])
            capdur = datetime.datetime.fromtimestamp(lastcapdate) - datetime.datetime.fromtimestamp(firstcapdate)
            lastcapdate = datetime.datetime.now() - datetime.datetime.fromtimestamp(lastcapdate)
            lastcapdate = str(lastcapdate).split(".")[0]
            self.cap_lf_text.SetLabel("last; " + str(lastcapdate) + " ago")
            capdur = str(capdur).split(".")[0]
            self.cap_ff_text.SetLabel('duration; ' + capdur)
        else:
            self.cap_len_text.SetLabel('Empty')
            self.cap_lf_text.SetLabel("last; --")
            self.cap_ff_text.SetLabel('duration; --')

        if len(cap_files) > 0 and capsgraph == True:
            print("make caps graph")
            if operating_system == "linux":
                print("Yay linux")
                os.system("../visualisation/caps_graph.py caps="+capsdir+" out="+graphdir)
            elif operating_system == 'win':
                print("oh, windows, i prefer linux but no worries...")
                os.system("python ../visualisation/caps_graph.py caps="+capsdir+" out="+graphdir)
        else:
            print("skipping graphing caps - disabled or no caps to make graphs with")
        if os.path.exists(graphdir+'caps_filesize_graph.png'):
            cap_size_graph = wx.Image(graphdir+'caps_filesize_graph.png', wx.BITMAP_TYPE_ANY)
            scale_size_graph = cap_size_graph.Scale(200, 100)
            self.cap_thumb.SetBitmap(wx.BitmapFromImage(scale_size_graph))
        else:
            print("NO CAPS GRAPH SO USING BLANK THUMB")
            blankimg = wx.EmptyImage(width=200, height=100, clear=True)
            self.cap_thumb.SetBitmap(wx.BitmapFromImage(blankimg))
        return cap_files

    def checkbox_big(self, e, cap_files):
        self.update_bigpic(cap_files)

    def update_bigpic(self, cap_files):
        if self.v_cap.IsChecked():
            if len(cap_files) > 0:
                pictoload = str(capsdir + cap_files[-1])
            else:
                pictoload = 'none'
        elif self.v_hourA.IsChecked():
            pictoload = str(capsdir + cap_files[0])
        elif self.v_dayA.IsChecked():
            pictoload = str(capsdir + cap_files[1])
        elif self.v_capgr.IsChecked():
            pictoload = str(graphdir+'caps_filesize_graph.png')
        elif self.v_selfgr.IsChecked():
            pictoload = str(graphdir+'caps_timediff_graph.png')
    #load and scale image
        print("Showing -" + pictoload)
        if os.path.exists(pictoload):
            bigpic = wx.Image(pictoload, wx.BITMAP_TYPE_ANY)
            pic_hight = bigpic.GetHeight()
            pic_choice = bigpic
            if self.v_scale.IsChecked():
                if pic_hight > 800:
                    pic_width = bigpic.GetWidth()
                    new_hight = 800
                    sizeratio = (pic_hight / new_hight)
                    new_width = (pic_width / sizeratio)
                    scale_bigpic = bigpic.Scale(new_width, new_hight)
                    pic_choice = scale_bigpic
            self.bigpic.SetBitmap(wx.BitmapFromImage(pic_choice))
        else:
            self.bigpic.SetBitmap(wx.EmptyBitmap(10,10))

    def clear_got(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
        foundpi, boxname = get_box_name(target_ip, target_user, target_pass)
        if not boxname == None:
            self.tb_ip.SetValue(target_ip)
            setfilepaths(boxname)
            clear_pis_caps(target_ip, target_user, target_pass, boxname)


    def download(self, e):
        target_ip = self.tb_ip.GetValue()
        target_user = self.tb_user.GetValue()
        target_pass = self.tb_pass.GetValue()
      #ssh into the pigrow to discover it's name
        foundpi, boxname = get_box_name(target_ip, target_user, target_pass)
        setfilepaths(boxname)
        self.update_boxname(boxname)
    #SHOULD ASK USER FOR INPUT here

        msg_text = "Found; \n"
        if self.d_con.IsChecked():
            download_config(target_ip, target_user, target_pass, boxname)
        if self.d_log.IsChecked():
            message = download_logs(target_ip, target_user, target_pass, boxname)
            msg_text += message
        if self.d_cap.IsChecked():
            cap_files = self.update_caps(capsgraph=False)
            startnum = len(cap_files)
            num = download_caps(target_ip, target_user, target_pass, boxname)
            cap_files = self.update_caps()
            capsnow = len(cap_files)
            capsdown = startnum - capsnow
            msg_text += str(capsdown) + " caps images. \n"
        if self.d_gra.IsChecked():
            download_graphs(target_ip, target_user, target_pass, boxname)
            gcount = len(os.listdir(graphdir))
            if gcount == 0:
                mes_text += 'no graphs'
            else:
                msg_text += "\n -plus some of the ("+ str(gcount)  +") files in graphs might have been refreshed  \n"
        if msg_text == "Found; \n":
            msg_text = "Nothing selected for download"
        wx.MessageBox(msg_text, 'Files Downloaded', wx.OK | wx.ICON_INFORMATION)
        lastaccess = str(datetime.datetime.now()).split(".")[0].split(" ")[1]
        self.update_dht()
        self.update_selflog()
        self.update_switch()
        self.last_acc.SetLabel("Last Accessed; " + str(lastaccess))
        self.update_bigpic(cap_files)
        self.update_gpiotext()





def main():
    app = wx.App()
    Pigrow(None)
    app.MainLoop()


if __name__ == '__main__':
    main()
