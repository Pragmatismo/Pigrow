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

def make_display(tank_name, tank_vol, current_vol, switch_log_path="", repeat_pump_times=[], timed_pump_times=[], days_to_show=7):
    x = 1000
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


    # mark previous watering
    water_times = read_switch_log(switch_log_path)
          # water_times contains [[date, t_level, msg], etc]
    with_xpos = switch_times(water_times, days_to_show)
          # water_times contains [[date, t_level, msg, x_pos], etc]

    # create a list of all the bar xpos relative to bounding box
    # also includes value and color
    l_bar_list = []
    x2_p = 0  # the point at which the last bar ends becomes the start of the next one
    p_val = 0 # used to shift the values forward so bars relate to the new water level
    for item in with_xpos:
        x_p = x2_p
        x2_p = item[3] / 2   # halved because we're only using left half of graph space
        try:
            val = int(item[1])
            col = (150,150,250)
        except:
            # for error make a full sized red bar
            val = tank_vol
            col = (250,150,150)
        l_bar_list.append([x_p, x2_p, p_val, col])
        p_val = val
    # add final bar to current volume - as calculated from switch log
    if len(with_xpos) > 0:
        l_bar_list.append([x2_p, 0.5, p_val, col])

    # create the co-ordinates for the bars relative, then shift them into the
    # bounding box, this allows them to overlap if desires (useful for markers)
    for bar in l_bar_list:
        #print(bar)
        bar_x_p, bar_x2_p, val, col = bar
        c_x, c_y, c_x2 = make_l_bar_box(bar_x_p, bar_x2_p, bb_w, bb_h, tank_vol, val)
        #print("bar_pos;", c_x, c_y, c_x2)
        c_x = (c_x + bb_x)
        c_x2 = (c_x2 + bb_x)
        c_y = c_y + bb_y
        cb_box = (c_x, c_y, c_x2, bb_y2)
        d.rectangle(cb_box, fill=col, outline=(50,50,240), width=1)
        d.text((c_x, c_y), str(val), font=font, fill=(0,0,0,255))

    # make bar labels
    lab_list = make_bar_labels(bb_w, days_to_show)
    for item in lab_list:
        txt, pos_x = item
        pos_x = pos_x + bb_x
        d.text((pos_x, bb_y + bb_h), str(txt), font=font, fill=(0,0,0,255))


    #### test text for my testing use while coding
    if len(water_times) > 1:
        final_dt = water_times[-1][0]
        first_dt = water_times[0][0]
        total_duration = final_dt - first_dt
        print("logged watering; From ", first_dt, " to ", final_dt, " which is ", total_duration)
        l_delta = datetime.datetime.now() - final_dt
        print(" Last entry was ", str(l_delta), "ago")

    # mark predicted waterings
       # read list of cron jobs into list with dates
       # creates bars for right side of graph (future)


    # return the pill image
    return main_base

def make_bar_labels(bb_w, days_to_show):
    '''
    half the width of the bounding box, divide into days
    check how many numbers will fit neatly into it
    then make a list of the the numbers and their postions to label
    '''
    left_side_space = bb_w/2
    # find max number of characters to show
    font_w = font.getmask(str(days_to_show)).getbbox()[2]
    font_w = font_w + 5
    limit_chr = False
    if font_w * days_to_show > left_side_space:
        limit_chr = True
        div_list = 2
        days_to_label = days_to_show / 2
        chr_space = font_w * days_to_label
        while chr_space > left_side_space:
            days_to_label = days_to_label / 2
            div_list += 1
            chr_space = font_w * days_to_label
        #print(" Limiting labels to", days_to_label)

    #
    day_step = left_side_space / days_to_show
    days_pos = []
    pos = bb_w/2
    for step in range(0, days_to_show + 1):
        day_text = str(step) # abs(days_to_show - step))
        days_pos.append([day_text, pos])
        pos = pos - day_step
    if limit_chr == True:
        days_pos = days_pos[0::div_list]

    return days_pos

def make_l_bar_box(c_x, c_x2, bb_w, bb_h, tank_vol, b_vol):
    '''
     creates the position for a bar in the bounding box
          x_pos       = percentage position on bar, i.e. 0.5 = mid point
          x2_pos      = percentage postion for end of bar
          bb_w, bb_h  = bounding box width, height
          tank_vol    = max level
          b_vol       = current level

    '''
    # bar start and end pos
    c_x  = bb_w * c_x
    c_x2 = bb_w * c_x2
    # bar height
    c_vol_percent = b_vol / tank_vol
    current_b_h = bb_h  * c_vol_percent
    current_bar_y = abs(current_b_h - bb_h)
    return c_x, current_bar_y, c_x2
    #print(" bar height;", b_vol, tank_vol, c_vol_percent, current_bar_y )

def make_bar_box(bar_width, c_pos, bb_w, bb_h, tank_vol, b_vol):
    '''
     creates the position for a bar in the bounding box
          c_pos       = percentage position on bar, i.e. 0.5 = mid point
          bb_w, bb_h  = bounding box width, height
          tank_vol    = max level
          b_vol       = current level

    '''
    current_bar_x = ((bb_w * c_pos) - (bar_width / 2))
    c_vol_percent = b_vol / tank_vol
    current_b_h = bb_h  * c_vol_percent
    current_bar_y = abs(current_b_h - bb_h)
    #print(bb_h, current_bar_x, c_vol_percent, current_b_h, current_bar_y)
    return (current_bar_x, current_bar_y, current_bar_x + bar_width)

def read_switch_log(switch_log_path):
    if not os.path.isfile(switch_log_path):
        print(" Switch_log not found at ", switch_log_path, " not using one")
        return []
    with open(switch_log_path, "r") as f:
        switch_log = f.read()
    switch_log = switch_log.splitlines()
    water_times = []
    for line in switch_log:
        if "timed_water.py" in line:
            line = line.split("@")
            date = datetime.datetime.fromisoformat(line[1])

            msg = line[2]
            if "watered for" in msg:
                t_level = msg.split(" ")[-1]
            else:
                t_level = "?"
            water_times.append([date, t_level, msg])
    return water_times

def switch_times(water_times, days_to_show=30):
    # limit to date range, probably should be in read_switch_log
    now = datetime.datetime.now()
    toshow_delta = datetime.timedelta(days=days_to_show)
    in_range = []
    for item in water_times:
        age = now - item[0]
        if not age > toshow_delta:
            in_range.append(item)
    # determin percentage position of switch points
    #          (for left side of graph but will be halved later
    #           so 1 = now, 0 = days_to_show days ago)
    sec_count = days_to_show * 24 * 60 * 60
    sec_p = sec_count / 100
    with_xpos = []
    for item in in_range:
        age = now - item[0]
        age = age.total_seconds()
        t_p = age / sec_count
        t_p = abs(t_p - 1)
        #print("graph pos; ", t_p, " Event was " + str(age) + " ago, ", item)
        item.append(t_p)
        with_xpos.append(item)

    return with_xpos

# def read_config(config_path):
#     with open(config_path, "r") as f:
#         conf_txt = f.read()
#     conf_lines = conf_txt.splitlines()
#     conf_dict = {}
#     for line in conf_lines:
#         if "=" in line:
#             e_pos = line.find("=")
#             if not e_pos == -1:
#                 key = e_pos[:e_pos]
#                 value = e_pos[e_pos + 1:]
#                 conf_dict[key] = value
#                 print(key, value)
#     return conf_dict

if __name__ == '__main__':
    switch_log_path = "/home/pragmo/frompigrow/windowcill/logs/switch_log.txt"
    #config_path = "/home/pragmo/frompigrow/windowcill/config/pigrow_config.txt"
    rep_test = []
    timed_test = []
    #conf_dict = read_config(config_path)
    img = make_display("test_tank", 2000, 1950, switch_log_path, rep_test, timed_test)
    # save a copy for testing
    main_base.save("test_water_display.png")
    # display on screen 
    img.show()
