import datetime

def make_datawall(list_of_graphs, datawall_path="datawall_test.png", list_of_datasets=[], infolist=[]):
    x = 850
    y = 1300
    print(" ---------------------------------------- ")
    print("        DATA WALL WEEKLY INFO ")
    print(" ---------------------------------------- ")
    print(list_of_graphs)
    import os
    from PIL import Image
    from PIL import ImageDraw, ImageFont
    bg_col = (240,255,240)
    module_dir = os.path.dirname(os.path.abspath(__file__))
    datawall_gfx_path = os.path.abspath(os.path.join(module_dir, '..', 'ui_images', 'datawall'))
    font_path = os.path.join(datawall_gfx_path, 'Caslon.ttf')
    font_big = ImageFont.truetype(font_path, 28)
    font = ImageFont.truetype(font_path, 22)

    def create_current_info_panel():
        print(" creating info panel")
        #print(infolist)
        lamp_info = infolist['check_lamp']
        lamp_info = lamp_info.replace("Config and Cron lamp timing synced.", "").strip()
        #switch_position = infolist['switch_position']
        return lamp_info + "\n" #+ switch_position

    def create_switch_dials():
        switch_positions = infolist['switch_position'].splitlines()
        # sizing
        pad = 20
        icon_width = 50
        space = x/2
        if space < pad + icon_width:
            space = pad + icon_width
        h_size = (len(switch_positions)) * (pad + icon_width)
        max_col_count = 0
        max_line_size = 0
        over_size = False
        while over_size == False:
            if max_line_size + pad + icon_width <= space:
                max_line_size += pad + icon_width
                max_col_count += 1
            else:
                over_size = True

        line_count = 2

        #
        bar_dials_base = Image.new('RGBA', (h_size, line_count * 80), color=bg_col)
        r_h_pos = pad / 2
        bar_draw = ImageDraw.Draw(bar_dials_base)
        line_pos = 0
        col_count = 0
        for switch_pos in switch_positions:
            if "is" in switch_pos:
                switch_pos = switch_pos.split(" is ")
                script = switch_pos[0].strip()
                state = switch_pos[1]
                if state == "ON":
                    indicator_img = Image.open(datawall_gfx_path + "/indicator_on.png")
                elif state == "OFF":
                    indicator_img = Image.open(datawall_gfx_path + "/indicator_off.png")
                # add to bar
                col_count += 1
                if col_count > max_col_count:
                    col_count = 0
                    line_pos += 1
                    r_h_pos = pad / 2
                bar_dials_base.paste(indicator_img, (int(r_h_pos), line_pos * 80))
                text_h = (line_pos * 80) + 50
                if text_h < 0:
                    text_h = 50
                st_width, st_height = bar_draw.textsize(script, font=font)
                v_space = ((50 + pad) - st_width)
                bar_draw.text(((r_h_pos-10) + (v_space/2), text_h), script, font=font, fill=(25,25,75,255))
                r_h_pos = r_h_pos + 50 + pad
        return bar_dials_base


    def find_hi_lows(dataset):
        #text = "Values recorded:" + str(len(dataset[1])) + "\n"
        high = dataset[1][1]
        low = dataset[1][1]
        for val in dataset[1]:
            if val > high:
                high = val
            if val < low:
                low = val
        text = "Most Recent: " + str(dataset[1][-1]) + '\n'
        text += "High: " + str(high) + '\n'
        text += "Low: " + str(low) + '\n'
        # text += dataset[2][1]

        return text

    def create_image_overlay_text():
        picture_timestamp = infolist['picture_recent'].split(".")[0].split("_")[-1]
        picture_dt = datetime.datetime.fromtimestamp(int(picture_timestamp))
        pi_dt = infolist['datetime']
        pi_dt = datetime.datetime.strptime(pi_dt, '%Y-%m-%d %H:%M:%S')
        age = pi_dt - picture_dt
        image_age = " picture is " + str(age) + " old"
        disk_space_remaining = infolist['diskusage'].splitlines()[-1]
        disk_space_remaining = disk_space_remaining.split("(")[1].replace(")", "")
        disk_space_remaining = "Disk used = " + disk_space_remaining
        return image_age + "\n" + disk_space_remaining


    def create_main():
        #
        test_base = Image.new('RGBA', (x,y), color=bg_col)
        dt = ImageDraw.Draw(test_base)
        # #
        # Sizing
        # #
        # image and status indicators
        last_pic = Image.open(infolist['picture_recent'])
        vert_pos1 = 45
        im_wid, im_hei = last_pic.size
        wpercent = ((x/2)/float(im_wid))
        hsize = int((float(im_hei)*float(wpercent)))
        last_pic = last_pic.resize((int(x/2), hsize))
        # Temp
        width, height = dt.textsize(create_current_info_panel(), font=font)
        switch_dials = create_switch_dials()
        height = height + switch_dials.size[1]
        temp = Image.open(list_of_graphs[0])
        if height > hsize:
            vert_pos2 = vert_pos1 + 10 + height
        else:
            vert_pos2 = vert_pos1 + 10 + hsize
        # humid
        humid = Image.open(list_of_graphs[1])
        vert_pos3 = vert_pos2 + 5 + temp.size[1]
        # config text
        vert_pos4 = vert_pos3 + humid.size[1]
        width, height = dt.textsize(infolist["switch_log"], font=font)
        vert_pos5 = vert_pos4 + height + 30
        el_width, height = dt.textsize(infolist["error_log"], font=font)
        vert_pos6 = vert_pos5 + height + 30
        width, height = dt.textsize(infolist["power_warnings"], font=font)
        # Tota; Image Heigh
        vert_h = vert_pos6 + height + 5

        #
        # Construct image and header
        new_base = Image.new('RGBA', (x,vert_h), color=(240,255,240))
        d = ImageDraw.Draw(new_base)
        d.text((30,10), infolist['boxname'], font=font_big, fill=(75,175,75,255))
        d.text((x - 100, 10), "Pigrow", font=font_big, fill=(75,175,75,255))
        #
        # show most recent image
        new_base.paste(last_pic, (0, vert_pos1))
        image_overlay = create_image_overlay_text()
        io_width, io_height = dt.textsize(image_overlay, font=font)
        x_pos = 0 + 15
        y_pos = vert_pos1 + hsize - (io_height + 5)
        d.text((x_pos, y_pos), image_overlay, font=font, fill=(180,180,250,255))

        # info text to right of caps image
        info_text = create_current_info_panel()
        d.text(((x/2)+15, vert_pos1 + 10), info_text, font=font, fill=(75,75,175,255))
        ip_width, ip_height = dt.textsize(info_text, font=font)
        # sizing
        d_w, d_h = switch_dials.size
        excess = int((x/2) - d_w)
        print (d_h, d_w, excess)
        #
        new_base.paste(switch_dials, (int((x/2)+(excess/2)), int(vert_pos1 + 20 + ip_height)))

        # temp
        new_base.paste(temp, (0, vert_pos2))
        temp_hilo = find_hi_lows(list_of_datasets[1])
        d.text((temp.size[0] + 5, vert_pos2 + 45), temp_hilo, font=font, fill=(75,75,175,255))
        # Humid
        new_base.paste(humid, (x - humid.size[0], vert_pos3))
        hum_hilo = find_hi_lows(list_of_datasets[0])
        d.text((5, vert_pos3 + 45), hum_hilo, font=font, fill=(75,75,175,255))
        #
        # Log poss
        d.text((15, vert_pos4), infolist["switch_log"], font=font, fill=(75,75,175,255))
        #
        d.text((x - 50 - el_width, vert_pos5), infolist["error_log"], font=font, fill=(75,75,175,255))
        d.text((15, vert_pos6), infolist["power_warnings"], font=font, fill=(75,75,175,255))


        new_base.save(datawall_path)

        print(" --- datawall_basic_info.py done and saved to " + datawall_path)

    def find_high_lows(list_of_values):
        high = list_of_values[0]
        low  = list_of_values[1]
        for x in list_of_values:
            if x > high:
                high = x
            if x < low:
                low = x
        return high, low

    #create_current_info_panel()
    create_main()
