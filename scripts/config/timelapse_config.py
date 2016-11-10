#!/usr/bin/python
from crontab import CronTab   #  pip install python-crontab

#script_path = '/home/pragmo/pigitgrow/Pigrow/scripts/cron/'
script_path = '/home/pi/Pigrow/scripts/cron/'
cappath = "/home/pi/cam_caps/"

cron = CronTab('root')  #generally leave user as 'root' but 'pi' or whatever will work also
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
    print("  Webcam;")
    print("    1 - camcap.py                   Basic image only webacm capture script")
    print("    2 - camcap_text_simple.py       Captures Image from webcam and add temp, humid and date ")
    print(" soon   3 - camcap_text_colour.py       Same as above but with colour coding on temp and humid values")
    print("  Pi Cam;")
    print("    4 - picamcap.py                 Basic image only capture script")
    print(" soon   5 - picamcap_text_simple.py     Captures picam image and adds text")
    print(" soon   6 - picamcap_text_colour.py     Same as above with colour coding on temp and humid")
    print("")
    option = raw_input("Type the number and press return;")
    if option == "1":
        cam_script = "python "+script_path+"camcap.py"
    elif option == "2":
        cam_script = "python "+script_path+"camcap_text_simple.py"
    elif option == "3":
        cam_script = "python "+script_path+"camcap_text_colour.py"
    elif option == "4":
        cam_script = "python "+script_path+"picamcap.py"
    elif option == "5":
        cam_script = "python "+script_path+"picamcap_text_simple.py"
    elif option == "6":
        cam_script = "python "+script_path+"picamcap_text_colour.py"
    time_step = raw_input("How frequently in min do you want it to capture images? input value between 1 and 59;")
    print("  ##  Adding Cron Job " + cam_script + " to run every " + str(time_step) + " min")
    cron_job = cron.new(command=cam_script,comment='added by timelapse_config')
    cron_job.minute.every(time_step)
    cron_job.enable()
    if cron_job.is_valid() == True:
        cron.write()
        print("         -Validity test passed, Job written")
    else:
        print(" ! ! ! ! -Validity test FAILED - maybe you typed the number wrong?")
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
            cron.write()
            add_job()
        except:
            print("")
            print("  - Input Error, try again;")
            job_mod()
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
