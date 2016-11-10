#!/usr/bin/python
from crontab import CronTab   #  pip install python-crontab
import os

### USER SETTINGS

#script_path = '/home/pragmo/pigitgrow/Pigrow/scripts/cron/'
script_path = '/home/pi/Pigrow/scripts/cron/'
cappath = "/home/pi/cam_caps/"
cron = CronTab('root')  #generally leave user as 'root' but 'pi' or whatever will work also if that user can run the camcap sctipt

#### PROGRAM

print("  ############################################")
print("  ##                                        ##")
print("  ##     Pigrow2 Cron Camera Management     ##")
print("  ##                                        ##")

print("  ##  Checking cron...")
camcap_list = []
for job in cron:
    if str(job).find('camcap') >= 0:
        camcap_list.append(job)
if len(camcap_list) >= 1:
    print("         -Found " + str(len(camcap_list))+" camcap scripts running...")
else:
    print('         -No currently running camcap jobs in cron')
print("  ##  Checking folders;")

filelist = []
if not os.path.exists(cappath):
    os.makedirs(cappath)
    print("         -created empty folder")
else:
    for filefound in os.listdir(cappath):
        filelist.append(filefound)
    print("         -"+cappath+" contains "+str(len(filelist))+" files")

def show_camcap():
    print("")
    print("")
    print("All camcap sctipt jobs currently running on cron;")
    for j in camcap_list:
        print("  - "+ str(j))
    print("")

def clear_camcap():
    print("")
    if len(camcap_list) >= 1:
        print("")
        print(" Select camcap cron job to remove;")
        for j in range(0, len(camcap_list)):
            print("  "+str(j)+" - "+ str(camcap_list[j]))
        option = raw_input("select job to delete or type ALL to clear all camcap jobs;")
        if option == ("ALL"):
            for j in camcap_list:
                cron.remove(j)
                cron.write()
                print("Jobs Cleared...")
        elif option == "":
            print("  -Nothing Changed")
            show_cron_menu()
        else:
            try:
                cron.remove(camcap_list[int(option)])
                cron.write()
                print("Job Removed...")
            except:
                print("didn't understand your input, try again;")
                clear_camcap()
    else:
        print(" No camcap jobs to remove")
        print("")
        show_cron_menu()

def add_job():
    print("")
    print("")
    print(" Select camcap script to enable;")
    print("")
    print("  Webcam;")
    print("    1 - camcap.py                   Basic image only webacm capture script")
    print("    2 - camcap_text_simple.py       Captures Image from webcam and add temp, humid and date ")
    print("    3 - camcap_text_colour.py       =soon-Same as above but with colour coding")
    print("  Pi Cam;")
    print("    4 - picamcap.py                 Basic image only capture script")
    print("    5 - picamcap_text_simple.py     -soon-Captures picam image and adds text")
    print("    6 - picamcap_text_colour.py     -soon-Same as above with colour coding")
    print("")
    asker = True
    asking = True
    while asker == True:
        option = raw_input("Type the number and press return;")
        if option == "1":
            cam_script = "python "+script_path+"camcap.py"
            asker = False
        elif option == "2":
            cam_script = "python "+script_path+"camcap_text_simple.py"
            asker = False
        elif option == "3":
            cam_script = "python "+script_path+"camcap_text_colour.py"
            asker = False
        elif option == "4":
            cam_script = "python "+script_path+"picamcap.py"
            asker = False
        elif option == "5":
            cam_script = "python "+script_path+"picamcap_text_simple.py"
            asker = False
        elif option == "6":
            cam_script = "python "+script_path+"picamcap_text_colour.py"
            asker = False
        elif option == "":
            print("")
            break
        else:
            print("")
            print(" Not a valid option, pick a number between 1 and 6...")
            print("")
    while asking == True:
        try:
            time_step = raw_input("How frequently in min do you want it to capture images? input value between 1 and 59;")
            time_step = int(time_step)
            asking = False
        except:
            print("not a valid answer")
    try:
        print("  ##  Adding Cron Job " + cam_script + " to run every " + str(time_step) + " min")
        cron_job = cron.new(command=cam_script,comment='added by timelapse_config')
        cron_job.minute.every(time_step)
        cron_job.enable()
        if cron_job.is_valid() == True:
            cron.write()
            print("         -Validity test passed, Job written")
        else:
            print(" ! ! ! ! -Validity test FAILED - very rare that is...?")
            raise
    except:
        print("")
        print(" _ Writing job failed  ")
        raise
        print("")
        show_cron_menu()
    if not cron.render():
        print "cron error, something is wrong!"

def job_mod():
    print("")
    if len(camcap_list) >= 1:
        print("")
        print(" Select camcap cron job to modify;")
        for j in range(0, len(camcap_list)):
            print("  "+str(j)+" - "+ str(camcap_list[j]))
        option = raw_input("select job to modify;")
        try:
            cron.remove(camcap_list[int(option)])
        except:
            print("")
            print("  - Input Error, try again;")
            job_mod()
        finally:
                #cron.write()
                add_job()
    else:
        print("No camcap jobs to modify")
        print("")
        show_cron_menu()


def show_all_cron():
    print("")
    print(" ## full cron list ## ")
    if len(cron) >= 1:
        for job in cron:
            print job
    else:
        print(" NO CRON JOBS RUNNING")
    print(" ####################")
    print("")

def show_cron_menu():
    print("  ####                                     ####")
    print("  ##                                         ##")
    print("  ##   1, show camcap jobs                   ##")
    print("  ##                                         ##")
    print("  ##   2, Modify camcap job                  ##")
    print("  ##                                         ##")
    print("  ##   3, Delete camcap job                  ##")
    print("  ##                                         ##")
    print("  ##   4, add new camcap job                 ##")
    print("  ##                                         ##")
    print("  ##   5, archive and clear camcap folders   ##")
    print("  ##                                         ##")
    print("  ##   6, show all cron jobs                 ##")
    print("  ##                                         ##")
    option = raw_input("Type the number and press return;")
    if option == "1":
        show_camcap()
        show_cron_menu()
    elif option == "2":
        job_mod()
        #show_cron_menu()
    elif option == "3":
        clear_camcap()
        #show_cron_menu()
    elif option == "4":
        add_job()
        #show_cron_menu()
    elif option == "5":
        print("NOT IMPLIMENTS! NOT IMPLEMENTS! YOU GO NOW!")
#        ()
#cappath = "/home/pi/cam_caps/"
#        show_cron_menu()
    elif option == "6":
        show_all_cron()
        show_cron_menu()

#show_camcap()
#add_job()
#show_all_cron()
show_cron_menu()
