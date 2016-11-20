#!/bin/bash
import os
import sys
from PIL import Image, ImageDraw, ImageFont

print("--------- Pigrow -------")
print("  --Data Wall Assembler--")
print("   -- --------------- --")

output_path = "./datawall.jpg"       #default use o= to set via command line
caps_path = "/home/pragmo/camcaps/"

g1 = "../../graphs/temp_graph.png"
g2 = "../../graphs/sec_since_up_graph.png"
g3 = "../../graphs/sec_between_up_graph.png"
g4 = "../../graphs/humid_graph.png"
g5 = "../../graphs/consecutive_pi_time_graph.png"
g6 = "../../graphs/sec_between_comps.png"

photo_basewidth = 800
graph_basewidth = 450

for argu in sys.argv:
    thearg = str(argu).split('=')[0]
    if  thearg == 'o':
        output_path = str(argu).split('=')[1]
    elif thearg == "g1":
            g1 = str(argu).split('=')[1]
    elif thearg == "g2":
            g2 = str(argu).split('=')[1]
    elif thearg == "g3":
            g3 = str(argu).split('=')[1]
    elif thearg == "g4":
            g4 = str(argu).split('=')[1]
    elif thearg == "g5":
            g5 = str(argu).split('=')[1]
    elif thearg == "g6":
            g6 = str(argu).split('=')[1]
    elif thearg == "caps":
            caps_path = str(argu).split('=')[1]
    elif thearg == "pbw":
            photo_basewidth = int(str(argu).split('=')[1])
    elif thearg == "gbw":
            graph_basewidth = int(str(argu).split('=')[1])

if not os.path.exists(caps_path):
    print("Unable to locate graph directory, is the path correct?")
    #sys.exit()

filelist = []
for filefound in os.listdir(caps_path):
    if filefound.endswith("jpg"):
        filelist.append(filefound)
filelist.sort()
newest_photo = str(caps_path+filelist[-1])


##Making The Image


newest_photo = Image.open(newest_photo)
wpercent = (photo_basewidth/float(newest_photo.size[0]))
hsize = int((float(newest_photo.size[1])*float(wpercent)))
newest_photo = newest_photo.resize((photo_basewidth,hsize), Image.ANTIALIAS)




g1 = Image.open(g1)
wpercent = (graph_basewidth/float(g1.size[0]))
hsize = int((float(g1.size[1])*float(wpercent)))
g1 = g1.resize((graph_basewidth,hsize), Image.ANTIALIAS)

g2 = Image.open(g2)
wpercent = (graph_basewidth/float(g2.size[0]))
hsize = int((float(g2.size[1])*float(wpercent)))
g2 = g2.resize((graph_basewidth,hsize), Image.ANTIALIAS)

g3 = Image.open(g3)
wpercent = (graph_basewidth/float(g3.size[0]))
hsize = int((float(g3.size[1])*float(wpercent)))
g3 = g3.resize((graph_basewidth,hsize), Image.ANTIALIAS)

g4 = Image.open(g4)
wpercent = (graph_basewidth/float(g4.size[0]))
hsize = int((float(g4.size[1])*float(wpercent)))
g4 = g4.resize((graph_basewidth,hsize), Image.ANTIALIAS)

g5 = Image.open(g5)
wpercent = (graph_basewidth/float(g5.size[0]))
hsize = int((float(g5.size[1])*float(wpercent)))
g5 = g5.resize((graph_basewidth,hsize), Image.ANTIALIAS)

g6 = Image.open(g6)
wpercent = (graph_basewidth/float(g6.size[0]))
hsize = int((float(g6.size[1])*float(wpercent)))
g6 = g6.resize((graph_basewidth,hsize), Image.ANTIALIAS)

base = Image.new("RGBA", (graph_basewidth+photo_basewidth+graph_basewidth+15, 15+newest_photo.size[1]), "white")

#left side
base.paste(g1,(0,0))
base.paste(g2,(0,g1.size[1]+1))
base.paste(g3,(0,g2.size[1]+g2.size[1]+1))
#central pannel
base.paste(newest_photo, (graph_basewidth+15,2))
#right side
base.paste(g4,(graph_basewidth+photo_basewidth+30,0))
base.paste(g5,(graph_basewidth+photo_basewidth+30,g4.size[1]+1))
base.paste(g6,(graph_basewidth+photo_basewidth+30,g4.size[1]+g5.size[1]+1))

base.save(output_path)
print("File saved to " + str(output_path))
base.show()
