#!/usr/bin/python

import matplotlib as mpl
mpl.use('Agg')

import os
import sys
import matplotlib.pyplot as plt
import datetime
import numpy as np



#This sctipt downloads all the images and the most recent log files and creates graphs from the data

errorlog = '/home/pragmo/TESTAFILEAOUTPUTSEE.txt'
tolog = False #verbose and annoying, use only for testing
if tolog == True:
    with open(errorlog, "a") as f:
        line = '\n  - download_logs.py - started a run for '+str(os.getlogin())+' - '
        f.write(line)

#humid
dangerlow = 30
toolow = 40
toohigh = 70
dangerhigh = 80
#temp
dangercold = 15
toocold = 23
toohot = 30
dangerhot = 36

graph_length_h = 24*7*52 #time in hours to show on graphs
hours_to_show_pitime = 24*6
loc_pi_list = "/home/pragmo/pigitgrow/Pigrow/config/pi_list.txt"

print("------ Pigrow -------")
print("  --Log Downloader--")
print("   --Graph Maker--")

#username = 'USERNAME'
user_name = str(os.getlogin())  #hash this line out if it causes problem, autograbs username replace with username = "magimo" (or whatever)
                                #it will cause problems if for any reason you run this script via cron for example
from_pipath = "/home/" + user_name + "/pigitgrow/Pigrow/frompi/" #obviously remove the pigitgrow folder if you're not me ;)
pieye_logs = "/home/" + user_name + "/pigitgrow/Pigrow/logs/"    #or are me using this on a different computer...

pi_list = []
with open(loc_pi_list, "r") as f:
    pi_settings = f.read()
    pi_settings = pi_settings.split("\n")
    for line in pi_settings[0:-1]:
        line = line.split(">")
        hostname = (line[0].split("="))[1]
        username = (line[1].split("="))[1]
        password = (line[2].split("="))[1]
        pi_list.append([hostname, username, password])

def download_images(target_hostname, target_password):
    if not os.path.exists(from_pipath+target_hostname+"/caps/"):
        if tolog == True:
            with open(errorlog, "a") as f:
                line = '\n...Caps folder doesn\'t exist, attempting to create it... '
                f.write(line)
        os.makedirs(from_pipath+target_hostname+"/caps/")

    try:
        if tolog == True:
            with open('/home/pragmo/TESTAFILEAOUTPUTSEE.txt', "a") as f:
                line = 'seeking out caps files... '
                f.write(line)
        target_files = "/home/pi/cam_caps/text_*.jpg"
        capsdir = from_pipath+target_hostname+"/caps/"
        print("Grabbing files, this might take some time...")
        os.system("rsync --ignore-existing -ratlz --rsh=\"/usr/bin/sshpass -p "+target_password+" ssh -o StrictHostKeyChecking=no -l "+target_hostname+"\" "+target_hostname+":"+target_files+" "+capsdir)
        print("Files Grabbed")
    except exception as e:
        if tolog == True:
            with open(errorlog, "a") as f:
                line = '...FAIL CAPS NOT GRABBED- '+str(e)+'... '
                f.write(line)
        print("Files not grabbed!")
        pass

def download_logs(target_hostname, target_password):
    if tolog == True:
        with open('/home/pragmo/TESTAFILEAOUTPUTSEE.txt', "a") as f:
            line = 'seeking out log files for '+str(target_hostname)+'... '
            f.write(line)
    if not os.path.exists(from_pipath+target_hostname+"/log/"):
        os.makedirs(from_pipath+target_hostname+"/log/")
    try:
        target_files = "/home/pi/logs/*.txt"
        #temporary hax to fix dev work in progress
        #if target_hostname == "pi@192.168.1.12":
        #    target_files = "/home/pi/pigrow3/logs/*.txt"
        #elif target_hostname == "pi@192.168.1.6":
        #    target_files = "/glog4.txt"
        logdir = from_pipath+target_hostname+"/log/"
        print("Grabbing logs, this shouldn't take as long...")
        os.system("rsync -ratlz --rsh=\"/usr/bin/sshpass -p "+target_password+" ssh -o StrictHostKeyChecking=no -l "+target_hostname+"\" "+target_hostname+":"+target_files+" "+logdir)
        print("local logs updated")
    except exception as e:
        if tolog == True:
            with open(errorlog, "a") as f:
                line = '...FAIL LOGS NOT GRABBED - '+str(e)+'... '
                f.write(line)
        print("Files not grabbed!")
        raise



def make_dht_graph(target_hostname, hours_to_show):
    if not os.path.exists(from_pipath+target_hostname+"/graphs/"):
        os.makedirs(from_pipath+target_hostname+"/graphs/")
    log_location = from_pipath+target_hostname+"/log/dht22_log.txt"
    log_humid = []
    log_temp = []
    log_date = []
    cut_list_date = []
    with open(log_location, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print('Adding ' + str(len(logitem)) + ' readings from dht log.')
    oldest_allowed_date = datetime.datetime.now() - datetime.timedelta(hours=hours_to_show)
    curr_line = len(logitem) - 2
    while curr_line >= 0:
        try:
            item = logitem[curr_line]
            item = item.split(">")
            date = item[2].split(".")
            date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            if date < oldest_allowed_date:
                break
            humid_val = float(item[1])  #these are split up so if it fails on the temp conversion
            temp_val = float(item[0])   #then it doesn't mess up the entire list.
            log_humid.append(humid_val)
            log_temp.append(temp_val)
            log_date.append(date)
            curr_line = curr_line - 1
        except:
            #print("-log item "+str(item)+" failed to parse, ignoring it..." + logitem[curr_line]) #ugly output when filewrite error
            curr_line = curr_line - 1
    log_humid.reverse()
    log_date.reverse()
    if tolog == True:
        with open(errorlog, "a") as f:
            line = '\n...LOGS UNDERSTOOD - We have '+str(len(log_temp))+' temp and '+str(len(log_humid))+' humidity readings, plus '+str(len(log_date))+' to work with.'
            f.write(line)
    print('We have '+str(len(log_temp))+' temp and '+str(len(log_humid))+' humidity readings, plus '+str(len(log_date))+' to work with.')
    #print('Log starts - ' + str(log_date[0].strftime("%b-%d %H:%M")) + ' to ' + str(log_date[-1].strftime("%b-%d %H:%M")))
##
### Make Humidity Graphs
##
    plt.figure(1)
    ax = plt.subplot()
  #  ax.bar(log_date, log_humid, width=0.01, color='k', linewidth = 0)
    ax.plot(log_date, log_humid, color='darkblue', lw=3)
    ave = 0
    for x in log_humid:
        ave = ave + x
    av = ave / len(log_humid)
    log_humid = np.array(log_humid)
    ax.fill_between(log_date, log_humid, 0,where=log_humid < dangerlow, alpha=0.6, color='darkblue')
    ax.fill_between(log_date, log_humid, 0,where=log_humid > dangerlow, alpha=0.6, color='blue')
    ax.fill_between(log_date, log_humid, 0,where=log_humid > toolow, alpha=0.6, color='green')
    ax.fill_between(log_date, log_humid, 0,where=log_humid > toohigh, alpha=0.6, color='red')
    ax.fill_between(log_date, log_humid, 0,where=log_humid > dangerhigh, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title(target_hostname+" Time Perod; " + str(log_date[0].strftime("%b-%d %H:%M")) + " to " + str(log_date[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("Humidity")
    fig = plt.gcf()
    fig.canvas.set_window_title(str('created' + str(datetime.datetime.now()))) #can remove this line when removing plt.show
    maxh = log_humid
    fig.autofmt_xdate()
    #plt.show()
    plt.savefig(from_pipath+target_hostname+"/graphs/Humidity.png")
    plt.close()
    print(" Created; "+from_pipath+target_hostname+ "/graphs/Humidity.png")
##
### Make Temp Graphs
##
    plt.figure(2)
    ax = plt.subplot()
 #   ax.bar(log_date, log_temp, width=0.01, color='green', linewidth = 0)
    ax.plot(log_date, log_temp, color='darkblue', lw=3)
    ave = 0
    for x in log_temp:
        ave = ave + x
    av = ave / len(log_temp)
    log_temp = np.array(log_temp)
    ax.fill_between(log_date, log_temp, 0,where=log_temp < dangercold, alpha=0.6, color='darkblue')
    ax.fill_between(log_date, log_temp, 0,where=log_temp > dangercold, alpha=0.6, color='blue')
    ax.fill_between(log_date, log_temp, 0,where=log_temp > toocold, alpha=0.6, color='green')
    ax.fill_between(log_date, log_temp, 0,where=log_temp > toohot, alpha=0.6, color='red')
    ax.fill_between(log_date, log_temp, 0,where=log_temp > dangerhot, alpha=0.6, color='darkred')
    ax.xaxis_date()
    plt.title(target_hostname+" Time Perod; " + str(log_date[0].strftime("%b-%d %H:%M")) + " to " + str(log_date[-1].strftime("%b-%d %H:%M")) + " UTC")
    plt.ylabel("Temperature C")
    fig = plt.gcf()
    fig.autofmt_xdate()
    maxh = log_temp
    plt.savefig(from_pipath+target_hostname+"/graphs/Temperature.png")
    plt.close()
    print("-- Created; "+from_pipath+target_hostname+"/graphs/Temperature.png")

##
### finds most recent image and creates image data graphs
##

def make_photo_graph(target_hostname):
    filelist = []         #Sorted list of all the files in the capsfolder
    facounter = 0         #file number used to make facounter_log list
    fsize_log = []        #file size list
    facounter_log = []    #file number list used in graphing
    datelist = []         #list of datetime objects parsed from filepaths

    for filefound in os.listdir(from_pipath+target_hostname+"/caps/"):
        if filefound.endswith("jpg"):
            filelist.append(filefound)
    filelist.sort()
    if len(filelist) > 0:
        for thefile in filelist:
            try:
                datelist.append(int(str(thefile).split(".")[0].split('_')[2]))
                thefile = os.stat(from_pipath+target_hostname+"/caps/" + thefile)
                fsize = thefile.st_size
                facounter = facounter + 1
                fsize_log.append(fsize)
                facounter_log.append(facounter)
            except:
                print("--"+thefile+" --Failed to parse")
                pass

#file size of captured image graph
#                images taken in darkness have a significantly
#                lower filesize than images in lightimages

        plt.figure(1)
        ax = plt.subplot()
        #ax.plot(facounter_log, fsize_log, color='darkblue', lw=3)
        ax.bar(facounter_log, fsize_log, width=0.1, color='green')
        plt.title("filesize of captured images")
        plt.ylabel("filesize")
        plt.xlabel("file number")
        #plt.show() #hash this line out to stop it shoinw the plot, unhash tp show plot
        plt.savefig (from_pipath+target_hostname+"/graphs/file_size_graph.png") #will be blank if plt.show is active
        plt.close()
        print("-- Created; " + from_pipath+target_hostname+"/graphs/file_size_graph.png")
# time difference between captured image graph
        pic_dif_log = []
        #print("Gathering data for time diff graph")
        for x in range(1, len(datelist)):
            cur_pic = datelist[x]
            las_pic = datelist[x-1]
            pic_dif = cur_pic - las_pic
            pic_dif_log.append(pic_dif)
        #print('We now have ' + str(len(pic_dif_log)) + ' up time differnces from the pictures to work with.')
        #print('most recent date: ' + str(datelist[-1]))
        plt.figure(2)
        ax = plt.subplot()
        #ax.plot(facounter_log, fsize_log, color='darkblue', lw=3)
        ax.bar(facounter_log[1:], pic_dif_log, width=0.1, color='green')
        plt.title("Time Diff Between Images")
        plt.ylabel("seconds between images")
        plt.xlabel("file number")
        #plt.show() #hash this line out to stop it shoinw the plot, unhash to show plot
        plt.savefig (from_pipath+target_hostname+"/graphs/file_time_diff_graph.png") #will be blank if plt.show is active
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/file_time_diff_graph.png")
    else:
        print("No images in "+from_pipath+target_hostname+"/caps/ folder, skipping these graphs..")



###
####  Creates Pi_Eye graphs if log available
##

def make_pieye_graph(target_hostname):
    piaddno = target_hostname.split(".")[-1]
    pi_eye_log = pieye_logs+"pieye_log_"+piaddno+".txt"
    graph_path = from_pipath +target_hostname+ "/graphs/"
    log_date = []
    log_cm_date = []
    log_comp_diff = []
    log_diff_pitime = []
    log_up_date = []
    log_up_date_ago = []
    uptim_diff_log = []
    counter = []
    pi_time_epoc = []
 # Loading log file for pi if it exits...

    with open(pi_eye_log, "r") as f:
        logitem = f.read()
        logitem = logitem.split("\n")
    print("found " + str(len(logitem)) + " lines in "+pi_eye_log+" log.")

######
####
##

    oldest_allowed_date = datetime.datetime.now() - datetime.timedelta(hours=hours_to_show_pitime)
    curr_line = len(logitem) - 1
    while curr_line >= 0:
        item = logitem[curr_line].split(">")
        try:
            pi_date = item[1] #output of date command on pi
            pi_eye_log_date = pi_date.split("=")[1]
            pi_eye_log_date = datetime.datetime.strptime(pi_eye_log_date, '%Y-%m-%d %H:%M:%S')
            cm_date = item[2] #output of this computer's date output
            cm_log_date = cm_date.split("=")[1]
            cm_log_date = datetime.datetime.strptime(cm_log_date, '%Y-%m-%d %H:%M:%S')
            up_date = item[5] #output of uptime on pi
            up_log_date = up_date.split("=")[1]
            up_log_date = datetime.datetime.strptime(up_log_date, '%Y-%m-%d %H:%M:%S')
            curr_line = curr_line - 1
            if cm_log_date < oldest_allowed_date:
                curr_line = -1
            log_date.append(pi_eye_log_date)
            log_cm_date.append(cm_log_date)
            log_up_date.append(up_log_date)
        except:
            print("- - - - log item "+str(curr_line)+" failed to parse, ignoring it..." + str(item))
            curr_line = curr_line - 1

    log_cm_date.reverse()
    log_date.reverse()
    log_up_date.reverse()

    print(' - We now have ' + str(len(log_date)) + ' date readings from the pi to work with.')
    print(' - We now have ' + str(len(log_up_date)) + ' up time readings from the pi to work with.')

    try:
        print('   -  From ' + str(log_date[0]) + ' to ' + str(log_date[-1]))
        for x in range(0, len(log_date)):
         #make list of diffs for pi reported dates from log
            diff = log_date[x] - log_date[0]
            diff = diff.total_seconds()
            log_diff_pitime.append(diff)
            counter.append(x)
            pi_time_epoc.append(int(log_date[x].strftime('%s')))
         #make list of reported uptime in seconds
            up_ago = log_date[x] - log_up_date[x]
            up_ago = int(up_ago.total_seconds())
            log_up_date_ago.append(up_ago)
         #make list of differing times between both computers
            comps_time_diff = log_cm_date[x] - log_date[x] #to account for bst# - datetime.timedelta(hours=1)
            comps_time_diff = int(comps_time_diff.total_seconds())
            log_comp_diff.append(comps_time_diff)
      #make list of uptime differences between each log entry
        for x in range(1, len(log_up_date_ago)):
            cur_upt = log_up_date_ago[x]
            las_upt = log_up_date_ago[x-1]
            uptim_diff = cur_upt - las_upt
            uptim_diff_log.append(uptim_diff)
        print('    We now have ' + str(len(uptim_diff_log)) + ' up time differnces from the pi to work with.')

    ###The Graph Making Routines
    # time as reported by pi

        plt.figure(1)
        ax = plt.subplot()
        ax.plot(counter, pi_time_epoc, color='darkblue', lw=3)
        plt.title("Seconds past since 1970 according to pi")
        plt.ylabel("seconds since the epoch")
        plt.xlabel("log entry number")
        plt.savefig (graph_path + "consecutive_pi_time_graph.png")
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/consecutive_pi_time_graph.png")

    # time diff of most recent and first entry in log as reported by pi

        plt.figure(2)
        ax = plt.subplot()
        ax.bar(log_date, log_diff_pitime, width=0.001, color='green', linewidth = 0.05)
        plt.title("Time from start of log")
        plt.ylabel("seconds")
        plt.gcf().autofmt_xdate()
        plt.savefig (graph_path + "step_graph.png")
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/step_graph.png")

    # uptime of pi in seconds

        plt.figure(3)
        ax = plt.subplot()
        ax.bar(log_date, log_up_date_ago, width=0.001, color='green', linewidth = 0)
        #ax.plot(log_date, log_up_date_ago, color='red', lw=1) #optional
        plt.title("Announced Uptime")
        plt.ylabel("seconds")
        plt.gcf().autofmt_xdate()
        plt.savefig(graph_path + "sec_since_up_graph.png")
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/sec_since_up_graph.png")

    # time between each logged uptime

        plt.figure(4)
        ax = plt.subplot()
        ax.plot(log_date[1:], uptim_diff_log, color='darkblue', lw=3)
        plt.title("Time between each logged uptime")
        plt.ylabel("seconds")
        plt.gcf().autofmt_xdate()
        plt.savefig(graph_path + "sec_between_up_graph.png")
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/sec_between_up_graph.png")

    # time between both computers time

        plt.figure(5)
        ax = plt.subplot()
        ax.plot(log_date, log_comp_diff, color='darkblue', lw=3) #choice of this, below line or both.
        ax.bar(log_date, log_comp_diff, width=0.001, color='green', linewidth = 0.05) #optional
        plt.title("Time difference between both computers")
        plt.ylabel("seconds")
        plt.gcf().autofmt_xdate()
        plt.savefig(graph_path + "sec_between_comps_graph.png")
        plt.close()
        print("-- Created " + from_pipath+target_hostname+"/graphs/sec_between_comps_graph.png")
    except:
        print("Problem making pieye graphs, probably due no recent data...")
        pass


##
###  Loops through the list of pis in the config file and does everything...
#####



try:
    for pi in pi_list:
        print("\n")
        print(" ------- Working on;")
        print("    ----------" + pi[0])
        download_images(pi[0],pi[2])
        download_logs(pi[0],pi[2])
        try:
             make_dht_graph(pi[0], graph_length_h)
        except Exception as e:
            print("Skipping graphing photos due to error, probably none there")
            print("Exception is " + str(e)+ " if that helps")
            #with open('/home/pragmo/TESTAFILEAOUTPUTSEE.txt', "a") as f:
            #    line = 'I dun a run and this happen... '+str(e)+'\n'
            #    f.write(line)
        try:
            make_photo_graph(pi[0])
        except Exception as e:
            print("Skipping graphing photos due to error, probably none there")
            print("Exception is " + str(e)+ " if that helps")
        try:
            make_pieye_graph(pi[0])
        except Exception as e:
            print("Pi eye log for "+pi[0]+" not found or broken")
            print("Exception is ---"+str(e)+"---- if that helps.")
            pass
except Exception as e:
    print("Exception is ---"+str(e)+"---- so there's that.")
    raise
print(" All tasks complete, images and graphs ready for use")
