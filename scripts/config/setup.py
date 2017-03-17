#!/usr/bin/python

"""
Module for guided user setup of PiGrow2
"""

from __future__ import print_function

import os
import socket
import sys
from subprocess import check_output

import praw

try:
    from crontab import CronTab  # pip install python-crontab
    # can be user+True, 'yourusername' or 'root' all work.
    CRON = CronTab(user=True)
except Exception as e:
    print("Crontab not installed, run guided setup. Error: " + str(e))

print("##################################")
print("##     Pigrow Setup Utility     ##")
print("##################################")

CONFIG_PATH = "/home/pi/Pigrow/config/"
LOC_LOCS = "/home/pi/Pigrow/config/dirlocs.txt"

# These folders are checked for scripts to add to cron
# TODO: Deduce folders to check based on username

AUTORUN_PATH = "/home/pi/Pigrow/scripts/autorun/"  # reboot scripts'
CRON_PATH = "/home/pi/Pigrow/scripts/cron/"  # repeting scripts
SWITCH_PATH = "/home/pi/Pigrow/scripts/switches/"  # timed scripts

# Test reboot scripts
# AUTORUN_PATH = "/home/pragmo/pigitgrow/Pigrow/scripts/autorun/"

# Test repeating scripts
# CRON_PATH    = "/home/pragmo/pigitgrow/Pigrow/scripts/cron/"

# Test timed scripts
# SWITCH_PATH  = "/home/pragmo/pigitgrow/Pigrow/scripts/switches/"

VALID_GPIO = [2, 3, 4, 17, 27, 22, 10, 9, 11, 0, 5, 6, 13,
              19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 1, 12, 16, 20, 21]
USED_GPIO_NUM = []

# LOC Defaults
LOC_SETTINGS = "/home/pi/Pigrow/config/pigrow_config.txt"
LOC_SWITCHLOG = "/home/pi/Pigrow/logs/switch_log.txt"
LOC_DHT_LOG = "/home/pi/Pigrow/logs/dht22_log.txt"
ERR_LOG = "/home/pi/Pigrow/logs/err_log.txt"
CAPS_PATH = "/home/pi/Pigrow/caps/"
GRAPH_PATH = "/home/pi/Pigrow/graphs/"
LOG_PATH = "/home/pi/Pigrow/logs/"
CLIENT_ID = " "
CLIENT_SECRET = " "
USERNAME = " "
PASSWORD = " "
SUBREDDIT = "Pigrow"
WIKI_TITLE = "livegrow_test_settings"
LIVE_WIKI_TITLE = "livegrow_test"
WATCHER_NAME = ' '

LOC_DIC = {}


def load_locs():
    print("Loading location details")
    with open(LOC_LOCS, "r") as f:
        for line in f:
            s_item = line.split("=")
            LOC_DIC[s_item[0]] = s_item[1].rstrip(
                '\n')  # adds each setting to dictionary


for arg in sys.argv:
    thearg = str(arg).split('=')[0]
    if thearg == 'locs':
        LOC_LOCS = str(arg).split('=')[1]
    elif thearg == '-pragmo':
        LOC_LOCS = "/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt"


def write_loclocs():
    with open(LOC_LOCS, "w") as f:
        for a, b in LOC_DIC.iteritems():
            try:
                s_line = str(a) + "=" + str(b) + "\n"
                f.write(s_line)
            except Exception:
                print("ERROR SETTINGS FILE ERROR SETTING NOT SAVED _ SERIOUS FAULT!")


def set_locs_and_passes():
    global WATCHER_NAME, LOC_SETTINGS, LOC_SWITCHLOG, LOC_DHT_LOG, ERR_LOG, CAPS_PATH, GRAPH_PATH, LOG_PATH, CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD, SUBREDDIT, WIKI_TITLE, LIVE_WIKI_TITLE

    try:
        load_locs()
    except Exception as error:
        print(" Couldn't load the logs: " + str(error))

    try:
        LOC_SETTINGS = LOC_DIC['loc_settings']
    except Exception:
        print(
            "IMPORTANT - Location of Settings File not included in file, adding default - " +
            LOC_SETTINGS)
        LOC_DIC['loc_settings'] = LOC_SETTINGS

    try:
        LOC_SWITCHLOG = LOC_DIC['loc_switchlog']
    except Exception:
        print(
            "IMPORTANT - Location of switch log not included in file, adding default - " +
            LOC_SWITCHLOG)
        LOC_DIC['loc_switchlog'] = LOC_SWITCHLOG

    try:
        LOC_DHT_LOG = LOC_DIC['loc_dht_log']
    except Exception:
        print(
            "IMPORTANT - Location of DHT log not included in file, adding default - " +
            LOC_DHT_LOG)
        LOC_DIC['loc_dht_log'] = LOC_DHT_LOG

    try:
        ERR_LOG = LOC_DIC['err_log']
    except Exception:
        print(
            "IMPORTANT - Location of Error log not included in file, adding default - " +
            ERR_LOG)
        LOC_DIC['err_log'] = ERR_LOG

    try:
        CAPS_PATH = LOC_DIC['caps_path']
    except Exception:
        print(
            "IMPORTANT - Location of caps path not included in file, adding default - " +
            CAPS_PATH)
        LOC_DIC['caps_path'] = CAPS_PATH

    try:
        GRAPH_PATH = LOC_DIC['graph_path']
    except Exception:
        print(
            "IMPORTANT - Location of Graph path not included in file, adding default - " +
            GRAPH_PATH)
        LOC_DIC['graph_path'] = GRAPH_PATH

    try:
        LOG_PATH = LOC_DIC['log_path']
    except Exception:
        print(
            "IMPORTANT - Location of log path not included in file, adding default - " +
            LOG_PATH)
        LOC_DIC['log_path'] = LOG_PATH

    try:
        CLIENT_ID = LOC_DIC['my_client_id']
        CLIENT_SECRET = LOC_DIC['my_client_secret']
        USERNAME = LOC_DIC['my_username']
        PASSWORD = LOC_DIC['my_password']
    except Exception:
        print(" Reddit Login details NOT SET set them if you want to use them...")
        CLIENT_ID = ' '
        CLIENT_SECRET = ' '
        USERNAME = ' '
        PASSWORD = ' '

    try:
        SUBREDDIT = LOC_DIC['subreddit']
        WIKI_TITLE = LOC_DIC['wiki_title']
        LIVE_WIKI_TITLE = LOC_DIC['live_wiki_title']
    except Exception:
        print("Subreddit details not set, leaving blank")
        SUBREDDIT = ' '
        WIKI_TITLE = ' '
        LIVE_WIKI_TITLE = ' '

    try:
        WATCHER_NAME = LOC_DIC['watcher_name']
    except Exception:
        print("No Reddit user set to recieve mail and issue commands")
        WATCHER_NAME = ' '

    if not os.path.exists(LOC_LOCS):
        print("Locations and passes file not found, creating default one...")
        write_loclocs()
        print(" - Settings saved to file - " + str(LOC_LOCS))

set_locs_and_passes()

PI_SET = {}
with open(LOC_SETTINGS, "r") as f:
    for line in f:
        s_item = line.split("=")
        PI_SET[s_item[0]] = s_item[1].rstrip('\n')


def save_settings():
    """
    Save settings from setup.py execution
    """
    print("Saving Settings...")
    try:
        with open(LOC_SETTINGS, "w") as f:
            for a, b in PI_SET.iteritems():
                s_line = str(a) + "=" + str(b) + "\n"
                f.write(s_line)
    except Exception:
        print("Settings not saved!")
        raise


def show_settings():
    for a, b in PI_SET.iteritems():
        print(str(a) + "  = " + str(b))


def make_dirs():
    """
    Check for directories, create if not extant.
    """
    if not os.path.exists(CAPS_PATH):
        os.makedirs(CAPS_PATH)
        print("Created: " + CAPS_PATH)
    if not os.path.exists(GRAPH_PATH):
        os.makedirs(GRAPH_PATH)
        print("Created: " + GRAPH_PATH)
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
        print("Created: " + LOG_PATH)


def guided_setup():
    """
    Execute guided setup for installing dependencies and creating directories
    """
    print("\n\n Pigrow dependencies Install ")
    print("")
    print("checking directories")
    make_dirs()
    os.system("/home/pi/Pigrow/scripts/config/install.py")
    print("")
    sys.exit()  # needs to be roloaded now the settings are in place
    raw_input("Press return to continue:")


def bind_realy(device):
    setting = raw_input("Select GPIO pin to use:")
    if setting in USED_GPIO_NUM:
        print("")
        print("That GPIO pin is already in use!")
    else:
        if int(setting) in VALID_GPIO:
            print("Setting " + device + " to use GPIO " + setting)
            print("")
            print(" Select Normal State:")
            print("    type 0, L or low  --OR--   1, H, or high")
            print(
                " This relates to if current can flow through the relay when it's powered down ")
            print(
                "  -- It's perfectly safe to get this wrong as long as you're using he right GPIO number --")
            print(
                "           --- if you've got it backwards turningi on will instead turn it off..  ---")
            direction = raw_input("Input option:")
            if direction.lower() in ["0", "l", "low", "down", "off"]:
                print("Direction set to LOW")
                PI_SET[device + "_on"] = "low"
                PI_SET[device] = setting
                save_settings()
            elif direction.lower() in ["1", "h", "high", "up", "on"]:
                print("Direction set to HIGH")
                PI_SET[device + "_on"] = 'high'
                PI_SET[device] = setting
                save_settings()
                print(
                    "Set " +
                    device +
                    " to " +
                    setting +
                    " with it's normal state as " +
                    direction)
            else:
                print("All those options and you still messaed up...")


def show_gpio_menu():
    used_gpio = []
    used_gpio_num = []
    print("")
    print("   ##############################################")
    print("   ####          GPIO SETTINGS               ####")
    print("   ####                                      ####")
    for a, b in PI_SET.iteritems():
        asplit = str(a).split("_")
        if asplit[0] == 'gpio':
            if len(asplit) == 2:
                # print("   ####   " + asplit[1])
                used_gpio.append([a, b])
                used_gpio_num.append(b)
    print("   #### Currently Used gpio pins: ")
    print("   ####    GPIO     DEVICE")
    for x in range(0, len(used_gpio)):
        if not str(used_gpio[x][1]) == "":
            print("   ####     " +
                  str(used_gpio[x][1]) +
                  "        " +
                  str(used_gpio[x][0].split("_")[1] +
                      "  "))
    print("   ####                                      ####")
    print("   ####   1  - Add new device                ####")
    print("   ####                                      ####")
    print("   ####   2  - Remove device                 ####")
    print("   ####                                      ####")
    print("   ####   3  - Test device                   ####")
    print("   ####                        m - main menu ####")
    print("   ####                        q - quit      ####")
    option = raw_input("Type the number and press return:")
    if option == "1":
        print("Select device to add:")
        print("   Sensors:")
        print("  1   - DHT22 Temp and Humidity")
        print("")
        print("   Relay Bindings:")
        print(" 2 - Lamp")
        print(" 3 - Heater")
        print(" 4 - Fans")
        print(" 5 - Humid")
        print(" 6 - Dehumid")
        print(" 7 - Co2")
        print(" 8 - Fan out")
        print(" 9 - Fan in")
        print("")
        option = raw_input("Type the number and press return: ")
        if option == "1":
            setting = raw_input("Select GPIO pin to use: ")
            try:
                setting = int(setting)
            except Exception:
                print("Should use a number")

            print(used_gpio_num)
            if setting in used_gpio_num:
                print("")
                print("That GPIO pin is already in use!")
            else:
                if setting in VALID_GPIO:
                    print("")
                    print("Setting DHT22 Sensor on pin " + str(setting))
                    PI_SET['gpio_dht22sensor'] = setting
                    save_settings()
                else:
                    print("Sorry that doesn't seem to be a valid pin... ")
        elif option == "2":
            bind_realy('gpio_lamp')
        elif option == "3":
            bind_realy('gpio_heater')
        elif option == "4":
            bind_realy('gpio_fans')
        elif option == "5":
            bind_realy('gpio_humid')
        elif option == "6":
            bind_realy('gpio_dehumid')
        elif option == "7":
            bind_realy('gpio_CO2')
        elif option == "8":
            bind_realy('gpio_fanout')
        elif option == "9":
            bind_realy('gpio_fanin')
        show_gpio_menu()

    elif option == "2":
        print(" ")
        print(" Choose Device to remove:")
        for x in range(0, len(used_gpio)):
            if not str(used_gpio[x][1]) == "":
                print("   ####     " + str(x) + "        " +
                      str(used_gpio[x][0].split("_")[1] + "  "))
        option = raw_input("Type the number and press return:")
        try:
            option = int(option)
            setting = used_gpio[int(option)]
            print(setting)
            PI_SET[setting[0]] = ''
            used_gpio = []
            used_gpio_num = []
            save_settings()
            show_gpio_menu()
            # show_gpio_menu()
        except Exception:
            print("Should use numbers for this,,,")
            show_gpio_menu()
            exit()
    elif option == "3":
        print("Select device to test:")
        count = 0
        for x in os.listdir(SWITCH_PATH):
            if x.endswith("py"):
                print("   #### " + str(count) + " - " + x)
            count = count + 1
        print("   ####   ")
        choice = raw_input("Select device to test:")
        os.system(SWITCH_PATH + os.listdir(SWITCH_PATH)[int(choice)])
        show_gpio_menu()
        exit()
        # show_gpio_menu()
    elif option == "m":
        show_main_menu()
    elif option == "q":
        exit()
    else:
        show_gpio_menu()
        exit()


def show_start_script_menu():
    print("\n\nhahahahahahahahahaahaha NO.")
    print("             ok, coming soon....")


def show_cron_menu():
    print("   ##############################################")
    print("   ####  Cron Scripts                        ####")
    print("   ####     1  -  Add start up script        ####")
    print("   ####                                      ####")
    print("   ####     2  -  Add Timed Switch           ####")
    print("   ####                                      ####")
    print("   ####     3  -  Add Repeating script       ####")
    print("   ####                                      ####")
    print("   ####     4  -  Remove job from Cron       ####")
    print("   ####                        s = show cron ####")
    print("   ####                        m = main menu ####")
    option = raw_input("Select option and press return:")
    if option == "1":
        print("   #### Choose script to run on start up,")
        print("   ####    -NOTE: This should be considered an alternative way")
        print("   ####            it's not as robust as starting a service")
        print("   #### ")
        count = -1
        for x in os.listdir(AUTORUN_PATH):
            count = count + 1
            print("   #### " + str(count) + " - " + x)
        option = raw_input("Select script to add:")
        try:
            job = AUTORUN_PATH + os.listdir(AUTORUN_PATH)[int(option)]
        except Exception:
            print("Sorry, that doesn't seem to have been a valid option")
            show_cron_menu()
            exit()
        job = CRON.new(command=job, comment='Pigrow')
        job.every_reboot()
        CRON.write()

    elif option == "2":
        print("   #### Choose script you want to trigger at a set time")
        count = 0
        for x in os.listdir(SWITCH_PATH):
            count = count + 1
            print("   #### " + str(count) + " - " + x)
        print("   ####   ")
        option = raw_input("Select script to add: ")
        hour = raw_input("Input hour to trigger (0-23): ")
        minpast = raw_input("How man min past the hour? (0-59): ")
        try:
            job = SWITCH_PATH + os.listdir(SWITCH_PATH)[int(option) - 1]
            hour = int(hour)
            minpast = int(minpast)
        except Exception:
            print("")
            print(" those needed to both be numbers...")
            show_cron_menu()
            exit()
        job = CRON.new(command=job, comment='Pigrow')
        job.hour.on(hour)
        job.minute.on(minpast)
        CRON.write()
        show_cron_menu()

    elif option == "3":
        count = -1
        print("")
        print("   #### Choose script you want to trigger periodically")
        for x in os.listdir(CRON_PATH):
            count = count + 1
            print("   #### " + str(count) + " - " + x)
        print("   ####   ")
        option = raw_input("Select script to add:")
        job = CRON_PATH + os.listdir(CRON_PATH)[int(option)]
        job = CRON.new(command=job, comment='Pigrow')
        print("")
        print(" Set frequency in,")
        print("  1 - minute")
        print("  2 - hour")
        print("  3 - day")
        print("  4 - week")
        print("  5 - month")
        freqin = raw_input(" : ")
        freq = raw_input("How frequently do you want it to trigger")
        freq = int(freq)
        if freqin == "1":
            job.minute.every(freq)
        elif freqin == "2":
            job.hour.every(freq)
        elif freqin == "3":
            job.day.every(freq)
        elif freqin == "4":
            job.week.every(freq)
        elif freqin == "5":
            job.month.every(freq)
        CRON.write()
        print("   -----------")
        print(" -- Job added --")
        show_cron_menu()

    elif option == "4":
        print(" Choose script to remove:")
        count = 0
        for job in CRON:
            print("  " + str(count) + "  - " + str(job))
            count = count + 1
        torem = raw_input("Type number and press return:")
        try:
            torem = int(torem)
        except Exception:
            print("\n\n THAT WAS NOT A NUMBER \n\n")
            show_cron_menu()
        print("Removing --" + str(CRON[torem]))
        print("")
        CRON.remove(CRON[torem])
        CRON.write()
        show_cron_menu()

    elif option == "s":
        print("   ###########")
        for line in CRON:
            # if job.command=="Pigrow":
            print("   #### " + str(line))  # s.command)
        raw_input("hit return to continue...")
        show_cron_menu()
    elif option == "m":
        print("   #################")
        show_main_menu()


def show_reddit_menu():
    global WATCHER_NAME, CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD, SUBREDDIT, WIKI_TITLE, LIVE_WIKI_TITLE

    print("\n\n")
    print("   ##############################################")
    print("   ####                                      ####")
    print("   ####    Reddit passwords and stuff        ####")
    print("   ####        bot: " + USERNAME)
    print("   ####        sub: " + SUBREDDIT)
    print("   ####       user: " + WATCHER_NAME)
    print("   ####  Settings:                           ####")
    print("   ####      1  -  Bot Login Info            ####")
    print("   ####      2  -  Wiki Details              ####")
    print("   ####      3  -  User to recieve messages  ####")
    print("   ####  Test:                               ####")
    print("   ####      4  -  Send test message         ####")
    print("   ####      5  -  Start Reddit settings ear ####")
    print("   ####                                      ####")
    print("   ####              s - Show Reddit Details ####")
    print("   ####                                      ####")

    option = raw_input("Selection option:")
    if option == "1":
        print(" These are the login details of your bot account, not your main reddit account...")
        print("                    -- best not to use the same for both, it'd mess up your messages")
        print("              ")
        print("leave blank to keep seetings or input a single space ' ' to blank them:")
        i_my_username = raw_input("Input the reddit username of your bot: ")
        i_my_password = raw_input("Input reddit password: ")
        i_my_client_id = raw_input("Input Client Id (the Shorter gibberish): ")
        i_my_client_secret = raw_input(
            "Input Client secret code (the longer gibberish): ")

        if i_my_username == '':
            print("Leaving username set to: " + USERNAME)
        else:
            LOC_DIC['my_username'] = i_my_username
            USERNAME = i_my_username

        if i_my_password == '':
            print("Leaving password set to: " + PASSWORD)
        else:
            LOC_DIC['my_password'] = i_my_password
            PASSWORD = i_my_password

        if i_my_client_id == '':
            print("Leaving Client ID set to: " + CLIENT_ID)
        else:
            LOC_DIC['my_client_id'] = i_my_client_id
            CLIENT_ID = i_my_client_id

        if i_my_client_secret == '':
            print(
                "Leaving Client Secret set to: " +
                CLIENT_SECRET +
                " yeah, means nothing to me either...")
        else:
            LOC_DIC['my_client_secret'] = i_my_client_secret
            CLIENT_SECRET == i_my_client_secret

        write_loclocs()
        print("")
        print(" Login Details Saved:")
        show_reddit_menu()
    elif option == "2":
        print("")
        SUBREDDIT = raw_input("Input name of subreddit: ")
        WIKI_TITLE = raw_input("Input name of wiki page for settings: ")
        LIVE_WIKI_TITLE = raw_input(
            "Input name wiki to use for live updates: ")
        LOC_DIC['subreddit'] = SUBREDDIT
        LOC_DIC['wiki_title'] = WIKI_TITLE
        LOC_DIC['live_wiki_title'] = LIVE_WIKI_TITLE
        write_loclocs()
        print("Subreddit Details Saved,")
        show_reddit_menu()
    elif option == "3":
        print(" Input the name of the account you want to be in control of your Pigrow")
        print("       - this user will be able to alter settings and recieve updates.")
        i_watcher_name = raw_input(
            "Input just he username, press return to leave it the same or add a space to blank it: ")
        print("")
        if i_watcher_name == '':
            print("No change made")
        else:
            LOC_DIC['watcher_name'] = i_watcher_name
            WATCHER_NAME = i_watcher_name
            write_loclocs()
            print("Watcher Username set and saved.")
        show_reddit_menu()

    elif option == "4":
        print("Attempting to send a message to" + LOC_DIC['watcher_name'])
        try:
            CLIENT_ID = LOC_DIC['my_client_id']
            CLIENT_SECRET = LOC_DIC['my_client_secret']
            USERNAME = LOC_DIC['my_username']
            PASSWORD = LOC_DIC['my_password']
            WATCHER_NAME = LOC_DIC['watcher_name']
        except Exception:
            print(
                "You need to set reddit login details and a trusted user to receive mail first")
            exit()
        try:
            reddit = praw.Reddit(user_agent="pigrow config script test message",
                                 client_id=CLIENT_ID,
                                 client_secret=CLIENT_SECRET,
                                 username=USERNAME,
                                 password=PASSWORD)
        except Exception:
            print("Couldn't log into Reddit.")
            raise
            try:
                print(" - Checking conneciton..")
                host = socket.gethostbyname("www.reddit.com")
                s = socket.create_connection((host, 80), 2)
                print(" -- Connected to the internet and reddit is up.")
                print("check you login details")
            except Exception:
                print(
                    "We don't appear to be able to connect to reddit, check your connection and try again...")
            exit()
        print(
            "Logged into reddit, trying to send message to " +
            str(WATCHER_NAME))
        try:
            whereto = praw.models.Redditor(reddit, name=WATCHER_NAME)
            whereto.message(
                'Test message from setup.py',
                "Congratulations, you have a working pigrow!")
            print(
                "The message has been sent, it should appear in your inbox any second...")
            print(
                " If you don't get the message check your login details and reddit settings")
            print(
                "   -also it might be worth checking you can send messages from the bot account")
            print("    log into it from reddit and send your main account a hello")
        except Exception as e:
            print("Sorry it didn't work this time, check your login details and username")
            print("The exception was: " + str(e))
            print("")
            print(
                "A 403 means bad login details or reddit issues, 404 means connection issues or reddit issues")
            print(
                "If everything seems correct then check you can post on reddit from the bot account normally")
        print("")
        raw_input("Press return to continue...")

    elif option == "5":
        print("Reddit Settings Ear is the program that listens for reddit messages,")
        print(" -use the cron start-up script menu to enable it on boot up")
        print("")
        print("Checking it's not already running..")

        try:
            script = AUTORUN_PATH + "reddit_settings_ear.py"
            script_test = map(int, check_output(
                ["pidof", script, "-x"]).split())
            print(" Found " + str(len(script_test)) + " running versions.")
            killorignore = raw_input(
                "Do you want to kill these and restart the script? Y/n")
            if killorignore == "y" or killorignore == "Y":
                os.system("pkill reddit_set")
                print("Old scripts killed")
                os.system("nohup " + AUTORUN_PATH + "reddit_settings_ear.py &")
                print("new script started.")
        except Exception:
            print("reddit_settings_ear.py doesn't appear to be running...")
            print(AUTORUN_PATH + "reddit_settings_ear.py")
            os.system("nohup " + AUTORUN_PATH + "reddit_settings_ear.py &")

        print(" ")
        print(" Press return to continue")
        raw_input("...")
        show_reddit_menu()

    elif option == 's' or option == 'S':
        print("  Reddit Log in details:")
        print("      ")
        print("Pigrow Bot Account: ")
        print("   Username: " + USERNAME)
        print("   Password: " + PASSWORD)
        print("  Client id: " + CLIENT_ID)
        print("  Secret id: " + CLIENT_SECRET)
        print("")
        print("Wiki Information:")
        print("     Subreddit: " + SUBREDDIT)
        print(" Settings Wiki: " + WIKI_TITLE)
        print("     Live Wiki: " + LIVE_WIKI_TITLE)
        print("")
        print("Person who is in control,")
        print("  Watcher/Commander: " + WATCHER_NAME)
        print("")
        raw_input("Press return to continue...")
        show_reddit_menu()


def show_restore_default_menu():
    """
    Erase settings and restore to default menu.
    """
    print("\n\nThis will erase all settings and reset to default values")
    print("                          .")
    if raw_input("Type yes to continue") == "yes":
        set_loc_defaults()
        save_settings()
        print("Location settings and passes have been set to defaults")
    if raw_input(
            "Do you want to empty [delete] the default directories? type yes") == "yes":
        os.system("sudo rm /home/pi/Pigrow/logs/*.*")
        os.system("sudo rm /home/pi/Pigrow/graphs/*.*")
        os.system("sudo rm /home/pi/Pigrow/caps/*.*")
    print("NOTE: I need to add default settings for other settings file..")


def show_main_menu():
    """
    Print main menu to terminal
    """
    print("")
    print("   ##############################################")
    print("   ####                                      ####")
    print("   ####     Pigrow Setup                     ####")
    print("   ####                                      ####")
    print("   ####        1 - Install Dependencies      ####")
    print("   ####                                      ####")
    print("   ####        2 - GPIO set up               ####")
    # print("   ####                  -change to view settings                    ####")
    # print("   ####        3 - Start-up services         ####")
    print("   ####                                      ####")
    print("   ####        4 - Cron run scripts          ####")
    print("   ####                                      ####")
    print("   ####        5 - Reddit login              ####")
    print("   ####                                      ####")
    print("   ####        6 - Restore Default           ####")
    print("   ####                    s - show settings ####")
    print("   ####                    q - to quit       ####")
    print("   ##############################################")

    option = raw_input("Type the number and press return:")
    if option == "1":
        guided_setup()
        show_main_menu()
    elif option == "2":
        show_gpio_menu()
        # show_main_menu()
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
        option = raw_input("return to continue:")
        show_main_menu()


show_main_menu()
