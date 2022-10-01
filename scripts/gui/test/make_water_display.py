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

def make_display(tank_name, tank_vol, current_vol, switch_log_path="", config_path="", pump_timings=[], days_to_show=7):
    x = 1000
    y = 800
    print(" ---------------------------------------- ")
    print("        Making watering display ")
    print(" ---------------------------------------- ")
    print(tank_name, tank_vol, pump_timings)

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
    water_times = read_switch_log(switch_log_path, config_path, tank_name)
          # water_times contains [[date, t_level, msg, pump_name], etc]
    with_xpos = switch_times(water_times, days_to_show)
          # water_times contains [[date, t_level, msg, pump_name, x_pos], etc]

    # create a list of all the bar xpos relative to bounding box
    # also includes value and color
    l_bar_list = []
    x2_p = 0  # the point at which the last bar ends becomes the start of the next one
    p_val = 0 # used to shift the values forward so bars relate to the new water level
    p_pump = with_xpos[0][3]
    pump_names = []
    for item in with_xpos:
        print("xpos item;", item)
        pump_name = item[3]
        if not pump_name in pump_names:
            pump_names.append(pump_name)
        x_p = x2_p
        x2_p = item[4] / 2   # halved because we're only using left half of graph space
        try:
            col = make_col(pump_names, p_pump)
            val = int(item[1])
        except:
            # for error make a full sized red bar
            val = tank_vol
            col = (250,150,150)
        print(p_pump, p_val, col)
        l_bar_list.append([x_p, x2_p, p_val, col, p_pump])
        p_val = val
        p_pump = pump_name
    # add final bar to current volume - as calculated from switch log
    if len(with_xpos) > 0:
        col = make_col(pump_names, p_pump)
        l_bar_list.append([x2_p, 0.5, p_val, col, p_pump])

    # create the co-ordinates for the bars relative, then shift them into the
    # bounding box, this allows them to overlap if desires (useful for markers)
    for bar in l_bar_list:
        print(bar)
        #print(bar)
        bar_x_p, bar_x2_p, val, col, pump_name = bar
        c_x, c_y, c_x2 = make_l_bar_box(bar_x_p, bar_x2_p, bb_w, bb_h, tank_vol, val)
        #print("bar_pos;", c_x, c_y, c_x2)
        c_x = (c_x + bb_x)
        c_x2 = (c_x2 + bb_x)
        c_y = c_y + bb_y
        cb_box = (c_x, c_y, c_x2, bb_y2)
        d.rectangle(cb_box, fill=col, outline=(50,50,240), width=1)
        pump_name = bar[4]
        d.text((c_x, c_y), str(pump_name), font=font, fill=(0,0,0,255))

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
        c_time_list = make_c_times(pump_timings, days_to_show)
       # creates bars for right side of graph (future)


    # return the pill image
    return main_base

def make_col(pump_names, pump_name):
    index = pump_names.index(pump_name)
    r_val = 100 + (index * 30)
    g_val = 150
    while r_val > 250:
        r_val = r_val - 250
        g_val = g_val + 50
    while g_val > 250:
        g_val = g_val - 250
    b_val = 190
    return (r_val, g_val, b_val)


def make_c_times(pump_timings, days_to_show):
    print(" It would be super fun if i made a list of times to fill out the days to show from the two cron lists, i'm not going to though :P")


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

def read_switch_log(switch_log_path, config_path, tank_name):
    if not os.path.isfile(switch_log_path):
        print(" Switch_log not found at ", switch_log_path, " not using one")
        return []
    # read switch log
    with open(switch_log_path, "r") as f:
        switch_log = f.read()
    switch_log = switch_log.splitlines()

    # get list of linked pumps
    config_dict = read_config(config_path)
    lp_key = "wtank_" + tank_name + "_pumps"
    print(lp_key)
    if lp_key in config_dict:
        linked_pumps = config_dict[lp_key].split(',')
    else:
        linked_pumps = []
    print(" LINKED PUMPS; ", linked_pumps)

    # make list of all the watering times for all linked pumps
    water_times = []
    for line in switch_log:
        if "timed_water.py" in line:
            line = line.split("@")
            date = datetime.datetime.fromisoformat(line[1])

            msg = line[2]
            if "watered for" in msg:
                words = msg.split(" ")
                t_level = words[-1]
                pump_name = words[-4]
                pump_name = pump_name.replace(",", "")
                #print(pump_name)
            else:
                t_level = "?"

            if pump_name in linked_pumps:
                print("reading;", date, t_level, msg, pump_name)
                water_times.append([date, t_level, msg, pump_name])

    return water_times

def switch_times(water_times, days_to_show=30):
    if len(water_times) == 0:
        return []
    # limit to date range, probably should be in read_switch_log
    now = datetime.datetime.now()
    toshow_delta = datetime.timedelta(days=days_to_show)
    closest_prior = [None, (now - water_times[0][0]) + datetime.timedelta(days=1)]
    in_range = []
    for item in water_times:
        age = now - item[0]
        if not age > toshow_delta:
            in_range.append(item)
        else:
            # find the closest item to the valid result
            if age < closest_prior[1]:
                closest_prior = [item, age]
    in_range.insert(0, closest_prior[0])
    # determin percentage position of switch points
    #          (for left side of graph but will be halved later
    #           so 1 = now, 0 = days_to_show days ago)
    sec_count = days_to_show * 24 * 60 * 60
    sec_p = sec_count / 100
    with_xpos = []
    for item in in_range:
        if not item == None:
            age = now - item[0]
            age = age.total_seconds()
            t_p = age / sec_count
            t_p = abs(t_p - 1)
            #print("graph pos; ", t_p, " Event was " + str(age) + " ago, ", item)
            item.append(t_p)
            with_xpos.append(item)
            print(" adding xpos to;", item)
    with_xpos[0][-1] = 0
    return with_xpos

def read_config(config_path):
    with open(config_path, "r") as f:
        conf_txt = f.read()
    conf_lines = conf_txt.splitlines()
    conf_dict = {}
    for line in conf_lines:
        if "=" in line:
            e_pos = line.find("=")
            if not e_pos == -1:
                key = line[:e_pos]
                value = line[e_pos + 1:]
                conf_dict[key] = value
                print(key, value)
    return conf_dict

if __name__ == '__main__':
    switch_log_path = "/home/pragmo/frompigrow/windowcill/logs/switch_log.txt"
    config_path = "/home/pragmo/frompigrow/windowcill/config/pigrow_config.txt"
    pump_timings = []
    days_to_show = 7
    #self.conf_dict = read_config(config_path)
    img = make_display("test_tank", 2000, 1950, switch_log_path, pump_timings, days_to_show)
    # save a copy for testing
    main_base.save("test_water_display.png")
    # display on screen
    img.show()
