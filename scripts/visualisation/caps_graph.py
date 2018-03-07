#!/usr/bin/python
import os, sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
homedir = os.getenv("HOME")

try:
    sys.path.append(homedir + '/Pigrow/scripts/')
    import pigrow_defs
    script = 'caps_graph.py'
    loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
    loc_dic = pigrow_defs.load_locs(loc_locs)
    capsdir = loc_dic['caps_path']
    graph_path = loc_dic['graph_path']
except:
    print("Pigrow config not detected, using defaults")
    capsdir = "./"
    graph_path = "./"
#user settings
cap_type = "jpg"
#graph_path = "/home/"

for argu in sys.argv[1:]:
    if "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if  thearg == 'caps':
            capsdir = theval
        elif thearg == 'graph' or thearg == 'out':
            graph_path = theval
    elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
        print("")
        print("  caps=DIR          - folder containing the caps images")
        print("  out=DIR/NAME.png  - folder to make graphs in, can use ./ ")
        sys.exit()
    elif argu == '-flags':
        print("log=" + capsdir)
        print("out=" + graph_path)
        sys.exit()
    else:
        print(" No idea what you mean by; " + str(argu))

if capsdir[-1] == '/':
    pass
else:
    capsdir = capsdir + '/'
if graph_path[-1] == '/':
    pass
else:
    graph_path = graph_path + '/'

def count_folder(capsdir="./", cap_type="jpg"):
    filelist = []
    facounter = 0
    fsize_log = []
    #facounter_log = []
    datelist = []
    for filefound in os.listdir(capsdir):
        if filefound.endswith(cap_type):
            filelist.append(filefound)
    filelist.sort()
    for thefile in filelist:
        try:
            datelist.append(int(str(thefile).split(".")[0].split('_')[-1]))
            thefile = os.stat(capsdir + thefile)
            fsize = thefile.st_size
            facounter = facounter + 1
            fsize_log.append(fsize)
            #facounter_log.append(facounter)
        except:
            print("File name didn't parse, ignoring it")
    print "found; " + str(facounter)
    print "with ; " + str(len(fsize_log)) + " file sizes's"
    print "and  ; " + str(len(datelist)) + " dates taken from the filename's"
    return fsize_log, datelist

#optional file size of captured image graph
#images taken in darkness have a significantly lower filesize than full images
def file_size_graph(datelst, fsize_log, graph_path="./"):
    fcounter_log = []
    gname = graph_path+"caps_filesize_graph.png"
    for x in range(0,len(fsize_log)):
        fcounter_log.append(x)
    plt.figure(1)
    ax = plt.subplot()
    #ax.plot(fcounter_log, fsize_log, color='darkblue', lw=3)
    ax.bar(fcounter_log, fsize_log, width=0.1, color='green')
    #ax.plot_date(fsize_log, datelist)
    plt.title("filesize")
    plt.ylabel("filesize")
    plt.xlabel("file number")
    #plt.show() #hash this line out to stop it shoinw the plot, unhash tp show plot
    plt.savefig(gname) #will be blank if plt.show is active
    print("Graph saved to "+gname)
    return gname


#optional time difference between captured image graph
def image_time_diff_graph(datelist, graph_path="/."):
    gname = graph_path+"caps_timediff_graph.png"
    pic_dif_log = []
    fcounter_log = []
    print("Gathering data for time diff graph")
    for x in range(1, len(datelist)):
        cur_pic = datelist[x]
        las_pic = datelist[x-1]
        pic_dif = cur_pic - las_pic
        pic_dif_log.append(pic_dif)
        fcounter_log.append(x)
    print('We now have ' + str(len(pic_dif_log)) + ' up time differnces from the pictures to work with.')
    plt.figure(2)
    ax = plt.subplot()
    #ax.plot(fcounter_log, fsize_log, color='darkblue', lw=3)
    ax.bar(fcounter_log, pic_dif_log, width=0.1, color='green')
    plt.title("Time Diff Between Images")
    plt.ylabel("seconds between images")
    plt.xlabel("file number")
    #plt.show() #hash this line out to stop it shoinw the plot, unhash to show plot
    plt.savefig(gname) #will be blank if plt.show is active
    print("Graph saved to "+gname)
    return gname

#optionally updates the ububtu background with the most recent script.
def update_ubuntu_background():
    #import subprocess
    print("Updating background image with most recent file...")
    newstbk = capsdir + filelist[-1]
    print newstbk

    cmd = "sudo -u "+user_name+" DISPLAY=:0 GSETTINGS_BACKEND=dconf gsettings set org.gnome.desktop.background picture-uri file://" + newstbk
    print cmd
    os.system(cmd)

#but a hash [#] before the following to stop them happening;
fsize_log, datelist = count_folder(capsdir, cap_type)
td_gname = image_time_diff_graph(datelist, graph_path)
fs_gname = file_size_graph(datelist, fsize_log, graph_path)
#update_ubuntu_background() use the cron script instead it works better.
