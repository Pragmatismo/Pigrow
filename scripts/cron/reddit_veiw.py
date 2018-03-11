#!/usr/bin/python
import datetime
import praw           #pip install praw
import os
import sys
from PIL import Image, ImageDraw, ImageFont
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
script = 'selflog_graph.py'
loc_locs = homedir + '/Pigrow/config/dirlocs.txt'


#sizes
photo_basewidth = 600
graph_basewidth = 400

#print(" if you're me -    python update_reddit.py loc_locs=/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt ")
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

#
# load location information and reddir log in details
#
def load_settings(loc_locs):
    loc_dic = pigrow_defs.load_locs(loc_locs)
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'])
    graph_path = loc_dic['graph_path']
    caps_path = loc_dic['caps_path']
    if 'loc_dht_log' in loc_dic:
        loc_switchlog = loc_dic['loc_dht_log']
    return loc_dic, set_dic, graph_path, caps_path, loc_dht_log

loc_dic, set_dic, graph_path, caps_path, loc_dht_log = load_settings(loc_locs)

if 'loc_settings' in loc_dic: loc_settings = loc_dic['loc_settings']
if 'err_log' in loc_dic: err_log = loc_dic['err_log']
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


print("")
print("        #############################################")
print("      ##       Automatic Reddit Grow Info Updater    ##")
print("")


print("logging in")
reddit = praw.Reddit(user_agent=my_user_agent,
                     client_id=my_client_id,
                     client_secret=my_client_secret,
                     username=my_username,
                     password=my_password)
subreddit = reddit.subreddit(subreddit)
print(subreddit.title)


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
                print('THERE WAS NO DOT THAT WAS THE PROBLEM YOU SEE')
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

page_text = '#Pigrow Live Updated Grow Tracker \n\n'
page_text += '**' + set_dic['box_name'] + '** at ' + str(datetime.datetime.now()).split(".")[0][:-3] + '  \n'
page_text += "Most recent sensor data; "
if date == -1:
    page_text += "No Sensor data has been collected  \n"
else:
    page_text += "Temp:"+str(temp)+" ^o C Humid:"+str(hum)+"%  Date:" + str(date) + " UTC  \n"
    page_text += " which was " + str(datetime.datetime.now() - date) + " ago.  \n"
page_text += '  \n'
page_text += '##Most Recent Photo  \n'


filelist = []
file_type = "jpg"
resize = True
for filefound in os.listdir(caps_path):
    if filefound.endswith(file_type):
        filelist.append(filefound)
filelist.sort()
if len(filelist) >= 1:
    img_photo = str(caps_path+filelist[-1])
    page_text += "Most recent image; "+filelist[-1]+"  \n  \n"
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
    page_text += '![most recent photo](%%photo%%)  \n  \n'
else:
    img_photo = None
    page_text += "There were no " + file_type + " images in the folder " + caps_path + "  \n  \n"

### Graphs
page_text += '##Graphs \n  \n'

graph_file_type = "png"
resize = False
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
        page_text += "#####"+graph_file+"  \n"
        page_text += '![' + g_name + '](%%'+ g_name +'%%)  \n'
    else:
        subreddit.stylesheet.upload(g_name, graph_path + graph_file)
        page_text += "#####"+graph_file+"  \n"
        page_text += '![' + g_name + '](%%'+ g_name +'%%)  \n'
    num = num + 1

if len(g_filelist) == 0:
    page_text += "No graphs found in " + str(graph_path)

  #REDDIT STYLE SHEET TURNS GIFS INTO PNG WITH NO ANIMATION
#page_text += '  \n  \n#Animated Gifs  \n'
#gif_filelist = []
#for filefound in os.listdir(graph_path):
#    if filefound.endswith('gif'):
#        gif_filelist.append(filefound)
#num = 1
#for gif_file in gif_filelist:
#    gif_name = 'gif' + str(num)
#    subreddit.stylesheet.upload(gif_name, graph_path + gif_file)
#    page_text += "#####"+gif_file+"  \n"
#    page_text += '![' + gif_name + '](%%'+ gif_name +'%%)  \n'
#    num = num + 1

praw.models.WikiPage(reddit, subreddit, live_wiki_title).edit(page_text)
print("Updated " + str(subreddit) + " " + str(live_wiki_title))
print("https://www.reddit.com/r/" + str(subreddit) + "/wiki/" + str(live_wiki_title))
