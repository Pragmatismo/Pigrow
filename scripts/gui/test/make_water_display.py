import os
import datetime
from PIL import Image
from PIL import ImageDraw, ImageFont

##
##
##    Needs to take all tank information and collate into a single image
##
##
font_size = 30
font = ImageFont.truetype("../ui_images/datawall/Caslon.ttf", 35)
ascent, descent = font.getmetrics()
font_h = font.getmask("A").getbbox()[3] + descent
font_w = font.getmask("A").getbbox()[2]
print(font_h)

def make_display(tank_name, tank_vol, current_vol, repeat_pump_times, timed_pump_times):
    x = 800
    y = 800
    print(" ---------------------------------------- ")
    print("        Making watering display ")
    print(" ---------------------------------------- ")
    print(tank_name, tank_vol, repeat_pump_times, timed_pump_times)

    # make base
    bg_col = (240,255,240)
    main_base = Image.new('RGBA', (x,y), color=bg_col)
    d = ImageDraw.Draw(main_base)


    vol_text = str(tank_vol) + "ml"

    # draw box for graph
    bb_x = font.getmask(vol_text).getbbox()[2] + 10
    bb_y = font_h + 5 + 15 #gap over and under name text
    bb_x2 = x - 50
    bb_y2 = y - 50
    bb_w = bb_x2 - bb_x
    bb_h = bb_y2 - bb_y
    box_pos = (bb_x, bb_y, bb_x2, bb_y2)
    d.rectangle(box_pos, fill=None, outline=(0,0,0), width=5)


    # label max tank vol
    name_text = "Tank; " + tank_name
    d.text((50, 5), name_text, font=font, fill=(0,0,0,255))
    d.text((10, bb_y), vol_text, font=font, fill=(0,0,0,255))
    d.text((10, bb_y2-font_h), "0 ml", font=font, fill=(0,0,0,255))

    # mark mid line (current vol)
    bar_width = 20
    # current_bar_x = ((bb_w / 2) - (bar_width / 2)) + bb_x
    # c_vol_percent = current_vol / tank_vol
    # current_b_h = bb_h  * c_vol_percent
    #
    # current_bar_y = abs(current_b_h - bb_h) + bb_y
    # print(bb_h, current_bar_x, c_vol_percent, current_b_h, current_bar_y)
    #
    # cb_box = (current_bar_x, current_bar_y, current_bar_x + bar_width, bb_y2)
    bar_c_pos = 0.5
    b_vol = current_vol
    #cb_box = make_bar_box(bar_width, bar_c_pos, bb_w, bb_h, tank_vol, b_vol)
    test_list = [[0, 1500], [0.1, 1000], [0.2, 500], [0.3, 2000], [0.4, 1500], [0.5, 1500], [1, 1000]]
    bar_count = 10
    bar_width = bb_w / bar_count
    for bar in test_list:
        bar_c_pos, b_vol = bar
        # Make the bar and draw to the image
        b_x, b_y, b_x2 = make_bar_box(bar_width, bar_c_pos, bb_w - bar_width, bb_h, tank_vol, b_vol)
        # shift to fit in graph bounding box (yes i should make a pnl, shut up)
        b_x = b_x + bb_x + (bar_width/2)
        b_x2 = b_x2 + bb_x + (bar_width/2)
        b_y = b_y + bb_y
        cb_box = (b_x, b_y, b_x2, bb_y2)
        d.rectangle(cb_box, fill=(150,150,250), outline=(50,50,240), width=5)


    # mark previous watering

    # mark predicted waterings

    main_base.save("test_water_display.png")
    return main_base

def make_bar_box(bar_width, c_pos, bb_w, bb_h, tank_vol, b_vol):
    '''
     creates the position for a bar in the bounding box
          c_pos       = percentage position on bar, i.e. 0.5 = mid point
          bb_w, bb_h  = bounding box width, height
          tank_vol    = max level
          b_vol       = current level

    '''
    current_bar_x = ((bb_w * c_pos) - (bar_width / 2)) #+ bb_x
    c_vol_percent = b_vol / tank_vol
    current_b_h = bb_h  * c_vol_percent
    current_bar_y = abs(current_b_h - bb_h) #+ bb_y
    #print(bb_h, current_bar_x, c_vol_percent, current_b_h, current_bar_y)
    return (current_bar_x, current_bar_y, current_bar_x + bar_width)




rep_test = []
timed_test = []

img = make_display("test_tank", 2000, 1950, rep_test, timed_test)
img.show()
