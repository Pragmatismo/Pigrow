#!/usr/bin/python
import datetime
import praw           #pip install praw
import OAuth2Util     #pip install praw-oauth2util
import os
from PIL import Image, ImageDraw, ImageFont
print("")
print("        #############################################")
print("      ##       Automatic Reddit Grow Info Updater    ##")
print("")
#print reddit.read_only

## REMEMBER TO REMOVE PASSWORD IF SHARING THE CODE!!!!

#sizes
photo_basewidth = 600
graph_basewidth = 400
#logs
link_dht_log = '/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/log/dht22_log.txt'
#caps
caps_path = "/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/caps/"
#graphs
img_graph2 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs//Humidity.png"
img_graph3 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/Temperature.png"
#sys graphs
img_graph4 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/sec_since_up_graph.png"
img_graph5 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs//step_graph.png"
img_graph6 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs//sec_between_up_graph.png"
img_graph7 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs//sec_between_comps_graph.png"
#cam graphs
img_graph1 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs//file_size_graph.png"
img_graph8 ="/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/file_time_diff_graph.png"


###     DON'T UPLOAD TO GITHUB WITH ALL THE SECRET CODES IN!
##       THESE WILL BE STORED AS A CONFIG FILE OR SOMETHING
#           in plaintext becaues no one givees a damn about stoopid reddit



print("logging in")
reddit = praw.Reddit(user_agent=my_user_agent,
                     client_id=my_client_id,
                     client_secret=my_client_secret,
                     username=my_username,
                     password=my_password)
subreddit = reddit.subreddit("Pigrow")
print(subreddit.title)

# Getting most recent temp and humid reading
try:
    with open(link_dht_log, "r") as f:
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
    raise
print("Temp:"+str(temp)+" Humid:"+str(hum)+" Date:" + str(date))

page_text = '#Pigrow Live Updated Grow Tracker \n\n'
page_text += 'name of box will probably go here  \n'
page_text += "Most recent sensor data; "
page_text += "Temp:"+str(temp)+" ^o C Humid:"+str(hum)+"%  Date:" + str(date) + " UTC\n"
page_text += '  \n'
page_text += '##Most Recent Photo  \n'
page_text += 'just testing for now, will get some plants in and a timelapse started soon..  \n  \n'


filelist = []
for filefound in os.listdir(caps_path):
    if filefound.endswith("jpg"):
        filelist.append(filefound)
filelist.sort()
img_photo = str(caps_path+filelist[-1])


####bit messy below here - needs tidy-up
                        #should probably close some of those images or use the same image every time
                        #move temp images into temp folder with absolute path

res_photo='./res_photo.png'
photo = Image.open(img_photo)
wpercent = (photo_basewidth/float(photo.size[0]))
hsize = int((float(photo.size[1])*float(wpercent)))
photo = photo.resize((photo_basewidth,hsize), Image.ANTIALIAS)
photo.save(res_photo)
phota_loc = reddit.subreddit('Pigrow').stylesheet.upload('photo', res_photo)
page_text += '![most recent photo](%%photo%%)  \n'

### Graphs
resizeda='./temp_graphar.png'
grapha = Image.open(img_graph1)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(resizeda)

res_temp='./res_temp.png'
grapha = Image.open(img_graph2)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_temp)

res_humid='./res_humid.png'
grapha = Image.open(img_graph3)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_humid)

res_up='./res_s_s_up.png'
grapha = Image.open(img_graph4)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_up)

res_step='./res_step.png'
grapha = Image.open(img_graph5)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_step)

res_s_b_u='./res_s_b_u.png'
grapha = Image.open(img_graph6)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_s_b_u)

res_s_b_c='./res_s_b_c.png'
grapha = Image.open(img_graph7)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_s_b_c)

res_f_s_d='./res_f_s_d.png'
grapha = Image.open(img_graph8)
wpercent = (graph_basewidth/float(grapha.size[0]))
hsize = int((float(grapha.size[1])*float(wpercent)))
grapha = grapha.resize((graph_basewidth,hsize), Image.ANTIALIAS)
grapha.save(res_f_s_d)


graph1 = reddit.subreddit('Pigrow').stylesheet.upload('test', resizeda)
graph2 = reddit.subreddit('Pigrow').stylesheet.upload('temp', res_temp)
graph3 = reddit.subreddit('Pigrow').stylesheet.upload('humid', res_humid)
graph4 = reddit.subreddit('Pigrow').stylesheet.upload('ssup', res_up)
graph5 = reddit.subreddit('Pigrow').stylesheet.upload('step', res_step)
graph6 = reddit.subreddit('Pigrow').stylesheet.upload('sbu', res_s_b_u)
graph7 = reddit.subreddit('Pigrow').stylesheet.upload('sbc', res_s_b_c)
graph8 = reddit.subreddit('Pigrow').stylesheet.upload('fsd', res_f_s_d)

page_text += '\n\n##Graphs \n  \n'
page_text += '![temp](%%temp%%) '
page_text += '![humidity](%%humid%%)  \n'
page_text += '###System Graphs  \n'
page_text += '![sec since up](%%ssup%%) '
page_text += '![step graph](%%step%%) '
page_text += '![sec between up](%%sbu%%) '
page_text += '![sec between comps](%%sbc%%)  \n'
page_text += '###camera graphs  \n'
page_text += 'This is a graph of the file sizes  \n ![file sizes of the camera images](%%test%%) '
page_text += '![file time dif](%%fsd%%)  \n'
page_text += '  \nIf you can\'t tell this is a very much inprogress bit of work here...'

praw.models.WikiPage(reddit, subreddit, 'livegrow_test').edit(page_text)


#praw.models.Redditor(reddit, 'The3rdWorld').message('this is the subject', 'tesing bot', from_subreddit='Pigrow')
