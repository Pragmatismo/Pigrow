#!/usr/bin/python
import os

print("##################################")
print("##   Pigrow Setup Utility       ##")
print("")

config_path = "/home/pi/Pigrow/config/"
loc_locs    = "/home/pi/Pigrow/config/dirlocs.txt"


# Defaults

loc_settings    = "/home/pi/Pigrow/config/pigrow_config.txt"
loc_switchlog   = "/home/pi/Pigrow/logs/switch_log.txt"
loc_dht_log     = "/home/pi/Pigrow/logs/dht22_log.txt"
err_log         = "/home/pi/Pigrow/logs/err_log.txt"
caps_path    = "/home/pi/Pigrow/caps/"
graph_path   = "/home/pi/Pigrow/graphs/"
log_path     = "/home/pi/Pigrow/logs/"
my_client_id      = ""
my_client_secret  = ""
my_username       = ""
my_password       = ""
subreddit       = "Pigrow"
wiki_title      = "livegrow_test_settings"
live_wiki_title = "livegrow_test"

loc_dic = {}
def load_locs():
    print("Loading location details")
    with open(loc_locs, "r") as f:
        for line in f:
            s_item = line.split("=")
            loc_dic[s_item[0]]=s_item[1].rstrip('\n') #adds each setting to dictionary

config_path = "/home/pragmo/pigitgrow/Pigrow/config/"
loc_locs    = "/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt"


if not os.path.exists(loc_locs):
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    print("Locations and passes file not found, creating default one...")
                     #
                     #          THIS LINE ONLY FOR TESTING PHASE ONLY REPLACE ONCE EVERYTHING IS FINAL WITH A SENSIBLE AND TIDY LINE
    default_settings = "loc_settings=/home/pi/Pigrow/config/pigrow_config.txt\nloc_switchlog=/home/pi/Pigrow/logs/switch_log.txt\nloc_dht_log=/home/pi/Pigrow/log/dht22_log.txt\nerr_log=/home/pi/Pigrow/log/err_log.txt/\ncaps_path=/home/pi/Pigrow/caps/\ngraph_path=/home/pi/Pigrow/graphs/\nmy_client_id=\nmy_client_secret=\nmy_username=Pigrow_salad\nmy_password=\nsubreddit=Pigrow\nwiki_title=livegrow_test_settings\nloc_dht_log=/home/pi/Pigrow/logs/dht22_log.txt\ngraph_path=/home/pi/Pigrow/graphs/\nlog_path=/home/pi/Pigrow/logs/"
                     #
                     #
    with open(loc_locs, "w") as f:
        f.write(default_settings)
else:
    load_locs()
    loc_settings    = loc_dic['loc_settings']
    loc_switchlog   = loc_dic['loc_switchlog']
    loc_dht_log     = loc_dic['loc_dht_log']
    err_log         = loc_dic['err_log']
    caps_path    = loc_dic['caps_path']
    graph_path   = loc_dic['graph_path']
    log_path     = loc_dic['log_path']
    my_client_id     = loc_dic['my_client_id']
    my_client_secret = loc_dic['my_client_secret']
    my_username      = loc_dic['my_username']
    my_password      = loc_dic['my_password']
    subreddit       = loc_dic['subreddit']
    wiki_title      = loc_dic['wiki_title']
    live_wiki_title = loc_dic['live_wiki_title']

pi_set={}
with open(loc_settings, "r") as f:
    for line in f:
        s_item = line.split("=")
        pi_set[s_item[0]]=s_item[1].rstrip('\n')

def save_settings():
    print("Saving Settings...")
    try:
        with open(loc_settings, "w") as f:
            for a,b in pi_set.iteritems():
                s_line = str(a) +"="+ str(b) +"\n"
                f.write(s_line)
    except:
        print("Settings not saved!")
        raise

def show_settings():
    for a,b in pi_set.iteritems():
        print str(a) +"  = "+ str(b)

def make_dirs():
    if not os.path.exists(caps_path):
        os.makedirs(caps_path)
        print("Created; " + caps_path)
    if not os.path.exists(graph_path):
        os.makedirs(graph_path)
        print("Created; " + graph_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
        print("Created; " + log_path)

def guided_setup():
    print("\n\nAye, that'd be a lovely feature to add!   --I imagine it'll import the cam_config script and that sort of magic too...")
    print("I've started writing it, you won't get too far tho...")
    print("checking directories")
    make_dirs()

    print("That's as far as we've got with that.... yeah, not that impressive so far... ")
def show_gpio_menu():
    used_gpio=[]
    print("")
    print("   ##############################################")
    print("   ####          GPIO SETTINGS               ####")
    print("   ####                                      ####")
    for a,b in pi_set.iteritems():
        asplit = str(a).split("_")
        if asplit[0] == 'gpio':
            if len(asplit) == 2:
                #print("   ####   " + asplit[1])
                used_gpio.append([a,b])
    print("   #### Currently Used gpio pins; ")
    print("   ####    GPIO     DEVICE")
    for x in range(0,len(used_gpio)):
        if not str(used_gpio[x][1]) == "":
            print("   ####     " +str(used_gpio[x][1])+"        " + str(used_gpio[x][0].split("_")[1] + "  "))
    print("   ####                                      ####")
    print("   ####   1  - Add new device                ####")
    print("   ####                                      ####")
    print("   ####   2  - Remove device                 ####")
    print("   ####                                      ####")
    print("   ####   3  - Test device                   ####")
    print("   ####                                      ####")
    option = raw_input("Type the number and press return;")
    if option == "1":
        show_gpio_menu()
    elif option == "2":
        print(" ")
        print(" Choose Device to remove;")
        for x in range(0,len(used_gpio)):
            if not str(used_gpio[x][1]) == "":
                print("   ####     " + str(x) + "        " + str(used_gpio[x][0].split("_")[1] + "  "))
        option = raw_input("Type the number and press return;")
        try:
            setting = used_gpio[int(option)]
            print setting
            pi_set[setting[0]] = ''
            save_settings()
            show_gpio_menu()
        except:
            print("meh")
            raise
        #show_gpio_menu()
    elif option == "3":
        show_gpio_menu()
        #show_gpio_menu()

def show_start_script_menu():
    print("\n\nhahahahahahahahahaahaha NO.")
def show_cron_menu():
    print("\n\nuse crontab you bum")
def show_reddit_menu():
    print("\n\nnah - text file it.")
def show_restore_default_menu():
    print("\n\nnope if you've messed up that bad just rm it all")

def show_main_menu():
    print("")
    print("   ##############################################")
    print("   ####                                      ####")
    print("   ####     Pigrow Setup                     ####")
    print("   ####                                      ####")
    print("   ####        1 - Guided Set up             ####")
    print("   ####                                      ####")
    print("   ####        2 - GPIO set up               ####")
    print("   ####                                      ####")
    print("   ####        3 - Start-up scripts          ####")
    print("   ####                                      ####")
    print("   ####        4 - Cron run scripts          ####")
    print("   ####                                      ####")
    print("   ####        5 - Reddit login              ####")
    print("   ####                                      ####")
    print("   ####        6 - Restore Default           ####")
    print("   ####                    s - show settings ####")
    print("   ####                    q - to quit       ####")
    print("   ##############################################")

    option = raw_input("Type the number and press return;")
    if option == "1":
        guided_setup()
        show_main_menu()
    elif option == "2":
        show_gpio_menu()
        #show_main_menu()
    elif option == "3":
        show_start_script_menu()
        show_main_menu()
    elif option == "4":
        show_cron_menu()
        show_main_menu()
    elif option == "5":
        show_reddit_menu()
        show_main_menu()
    elif option == "6":
        show_restore_default_menu()
        show_main_menu()
    elif option == "q":
        exit()
    elif option == "s":
        show_settings()
        option = raw_input("return to continue;")
        show_main_menu()


show_main_menu()
