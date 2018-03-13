#!/usr/bin/python
import datetime
import praw           #pip install praw
import os
import sys
from PIL import Image, ImageDraw, ImageFont

homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
try:
    import pigrow_defs
    script = 'selflog_graph.py'
except:
    print("pigrow_defs not found, can't survive without...")
    print("make sure pigrow software is installed correctly")
    sys.exit()
#
#       This script is designed to be either periodically called by cron
#       or triggered from a remote interface, especially the reddit ear listener
#       it can of course be run from command line or imported as modules.
#
#    This script looks in dirlocs.txt for the reddit user information
#    reads the most recent dht22 sensor data
#    finds the most recent image in the caps folder
#    uploads and lists all the image files in the graphs folder
#    posts everythign to the wiki
#


# Default locations
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'
#sizes
photo_basewidth = 600
graph_basewidth = 400

#
# Command line arguments
#
for argu in sys.argv:
    if argu == '-h' or argu == '--help':
        print(" Reddit Live View Update script")
        print(" ")
        print("This updates the reddit wiki with the most recent caps image,")
        print("plus al graphs and any other images in the graphs folder")
        print("")
        print("this script is best run at the end of a sh file which first")
        print("runs each graph making program in turn")
        print("")
        print(" this script is due a minor update, command line arguments coming soon")
        sys.exit(0)
    elif argu == "-flags":
        print("path_dirloc=" + str(loc_locs))
        sys.exit(0)
    elif "=" in argu:
        thearg = str(argu).split('=')[0]
        theval = str(argu).split('=')[1]
        if thearg == 'loc_locs' or thearg == "path_dirloc":
            loc_locs = theval


print("")
print("        #############################################")
print("      ##   Automatic Reddit Wiki Grow Info Updater   ##")
print("")

#
# load location information and reddit log in details
#
def load_settings(loc_locs):
    loc_dic = pigrow_defs.load_locs(loc_locs)
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'])
    if 'loc_dht_log' in loc_dic:
        loc_dht_log = loc_dic['loc_dht_log']
    else:
        print("!! DHT log not found !!")
    if 'err_log' in loc_dic:
        err_log = loc_dic['err_log']
    else:
        err_log = 'emergency_error_log.txt'
    return loc_dic, set_dic, loc_dht_log, err_log

def load_reddit_login(loc_dic):
    my_user_agent= 'Pigrow Periodic Wiki Updater V0.8 (by /u/The3rdWorld)'
    try:
        my_client_id = loc_dic['my_client_id']
        my_client_secret = loc_dic['my_client_secret']
        my_username = loc_dic['my_username']
        my_password = loc_dic['my_password']
        subreddit = loc_dic["subreddit"]
        live_wiki_title = loc_dic['live_wiki_title']
    except:
        print("REDDIT SETTINGS NOT SET - EDIT THE FILE " + str(loc_locs))
        raise
    return my_user_agent, my_client_id, my_client_secret, my_username, my_password, subreddit, live_wiki_title

def log_in_reddit(my_user_agent, my_client_id, my_client_secret, my_username, my_password, subreddit):
    print("logging in as " + str(my_username))
    reddit = praw.Reddit(user_agent=my_user_agent,
                         client_id=my_client_id,
                         client_secret=my_client_secret,
                         username=my_username,
                         password=my_password)
    print("linking to " + str(subreddit))
    subreddit = reddit.subreddit(subreddit)
    print("   " + subreddit.title)
    return reddit, subreddit

def post_page(page_text, reddit, subreddit, live_wiki_title):
    praw.models.WikiPage(reddit, subreddit, live_wiki_title).edit(page_text)
    print("Updated " + str(subreddit) + " " + str(live_wiki_title))
    print("https://www.reddit.com/r/" + str(subreddit) + "/wiki/" + str(live_wiki_title))

#
# construct page text
#
def read_dht_log_mostrecent(loc_dht_log):
    # Getting most recent temp and humid reading
    try:
        with open(loc_dht_log, "r") as f:
            logitem = f.read()
            logitem = logitem.split("\n")
        print('Adding ' + str(len(logitem)) + ' readings from log.')
        curr_line = len(logitem) - 1
        while curr_line >= 0:
            try:
                item = logitem[curr_line]
                item = item.split(">")
                try:
                    date = item[2].split(".")  #does this work, looks like it shouldn't check
                except:
                    date = item[2]
                    #print('THERE WAS NO DOT THAT WAS THE PROBLEM YOU SEE')
                date = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
                hum = float(item[1])
                temp = float(item[0])
                curr_line = -1
            except:
                print("-log item "+str(curr_line)+" failed to parse, ignoring it..." + logitem[curr_line])
                curr_line = curr_line - 1
    except:
        print("No log to load, or it didn't work proper")
        temp=-1
        hum=-1
        date=-1
        pass
    print("Temp:"+str(temp)+" Humid:"+str(hum)+" Date:" + str(date))
    return temp, hum, date

def make_identity_text(box_name):
    id_text = '#Pigrow Live Updated Grow Tracker \n\n'
    id_text += '**' + box_name + '** at ' + str(datetime.datetime.now()).split(".")[0][:-3] + '  \n'
    return id_text

def make_dht_text(temp, hum, date):
    if date == -1:
        dht_text = "No DHT sensor data has been collected or log not found.  \n"
    else:
        dht_text = "Temp:"+str(temp)+" ^o C Humid:"+str(hum)+"%  Date:" + str(date) + "  \n"
        dht_text += " which was " + str(datetime.datetime.now() - date) + " before wiki update.  \n"
    return dht_text

def show_most_recent(caps_path):
    # finds the most recent image in the folder and uploads it
    # can only be called once as will overwrite image on reddit wiki
    pic_text = '##Most Recent Photo  \n'
    filelist = []
    file_type = "jpg"
    resize = True
    for filefound in os.listdir(caps_path):
        if filefound.endswith(file_type):
            filelist.append(filefound)
    filelist.sort()
    if len(filelist) >= 1:
        img_photo = str(caps_path+filelist[-1])
        pic_text += "Most recent image; "+ filelist[-1] + "  \n"
        pic_text += "from folder; " + caps_path + "  \n   \n"
        if resize == True:
            res_photo='./resized_photo.png'
            photo = Image.open(img_photo)
            wpercent = (photo_basewidth/float(photo.size[0]))
            hsize = int((float(photo.size[1])*float(wpercent)))
            photo = photo.resize((photo_basewidth,hsize), Image.ANTIALIAS)
            photo.save(res_photo)
            photo_loc = subreddit.stylesheet.upload('photo', res_photo)
        else:
            photo_loc = subreddit.stylesheet.upload('photo', img_photo)
        pic_text += '![most recent photo](%%photo%%)  \n  \n'
    else:
        img_photo = None
        pic_text += "There were no " + file_type + " images in the folder " + caps_path + "  \n  \n"
    return pic_text

def show_all_graphs(graph_path, graph_file_type="png", resize=False):
    #posts all images in folder under the title graphs
    graph_text = '##Graphs \n  \n'
    g_filelist = []
    for filefound in os.listdir(graph_path):
        if filefound.endswith(graph_file_type):
            g_filelist.append(filefound)
    num = 1
    for graph_file in g_filelist:
        g_name = 'graph' + str(num)
        if resize == True:
            graph = Image.open(graph_path + graph_file)
            wpercent = (graph_basewidth/float(graph.size[0]))
            hsize = int((float(graph.size[1])*float(wpercent)))
            graph = graph.resize((graph_basewidth,hsize), Image.ANTIALIAS)
            resize_name = str(graph_file).split(".")[0] + "_resized.png"
            graph.save(graph_path + resize_name)
            subreddit.stylesheet.upload(g_name, graph_path + resize_name)
            os.remove(graph_path + resize_name)
            graph_text += "#####"+graph_file+"  \n"
            graph_text += '![' + g_name + '](%%'+ g_name +'%%)  \n'
        else:
            subreddit.stylesheet.upload(g_name, graph_path + graph_file)
            graph_text += "#####"+graph_file+"  \n"
            graph_text += '![' + g_name + '](%%'+ g_name +'%%)  \n'
        num = num + 1
    if len(g_filelist) == 0:
        graph_text += "No graphs found in " + str(graph_path)
    return graph_text

def show_gifs(graph_path):
    #
    #REDDIT STYLE SHEET TURNS GIFS INTO PNG WITH NO ANIMATION
    #
    page_text = '  \n  \n#Animated Gifs  \n'
    gif_filelist = []
    for filefound in os.listdir(graph_path):
        if filefound.endswith('gif'):
            gif_filelist.append(filefound)
    num = 1
    for gif_file in gif_filelist:
        gif_name = 'gif' + str(num)
        subreddit.stylesheet.upload(gif_name, graph_path + gif_file)
        page_text += "#####"+gif_file+"  \n"
        page_text += '![' + gif_name + '](%%'+ gif_name +'%%)  \n'
        num = num + 1

if __name__ == '__main__':
    ## Load logs and log on
    loc_dic, set_dic, loc_dht_log, err_log = load_settings(loc_locs)
    my_user_agent, my_client_id, my_client_secret, my_username, my_password, subreddit, live_wiki_title = load_reddit_login(loc_dic)
    reddit, subreddit = log_in_reddit(my_user_agent, my_client_id, my_client_secret, my_username, my_password, subreddit)
    ## construct page
    page_text = make_identity_text(set_dic['box_name'])
    page_text += "#Most recent sensor data  \n"
    temp, hum, date = read_dht_log_mostrecent(loc_dht_log)
    page_text += make_dht_text(temp, hum, date)
    make_identity_text(set_dic['box_name'])
    page_text += show_most_recent(loc_dic['caps_path'])
    page_text += show_all_graphs(loc_dic['graph_path'], graph_file_type="png", resize=False)
    # page_text += show_gifs(loc_dic['graph_path']) reddit doesn't do animated gifs anymore
    ## post the page on the wiki
    post_page(page_text, reddit, subreddit, live_wiki_title)
