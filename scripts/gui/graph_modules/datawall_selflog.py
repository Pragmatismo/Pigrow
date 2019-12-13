

def make_datawall(list_of_graphs, datawall_path="datawall_test.png", list_of_datasets=[]):
    x = 1800
    y = 600
    print(" ---------------------------------------- ")
    print("        DATA WALL SELFLOG DISPLAY")
    print(" ---------------------------------------- ")
    print(list_of_graphs)
    from PIL import Image
    from PIL import ImageDraw, ImageFont

    def find_high_lows(list_of_values):
        high = list_of_values[0]
        low  = list_of_values[1]
        for x in list_of_values:
            if x > high:
                high = x
            if x < low:
                low = x
        return high, low

    cputemp_pic = Image.open(list_of_graphs[0])
    uptime_pic = Image.open(list_of_graphs[1])
    disk_pic = Image.open(list_of_graphs[2])
    mem_pic = Image.open(list_of_graphs[3])
    loadave_pic = Image.open(list_of_graphs[4])
    num_checkdht_pic = Image.open(list_of_graphs[5])

    img_width = (cputemp_pic.size[0] * 2) + 50
    img_heigh = (cputemp_pic.size[1] * 3) + 50
    new_base = Image.new('RGBA', (img_width,img_heigh), color=(240,255,240))
    # place graphs
    # top row
    new_base.paste(cputemp_pic, (0, 0))
    new_base.paste(disk_pic, (cputemp_pic.size[0] + 50, 0))
    # middle Row
    new_base.paste(loadave_pic, (0, cputemp_pic.size[1] + 25))
    new_base.paste(mem_pic, (cputemp_pic.size[0] + 50, cputemp_pic.size[1] + 25))
    # lower row
    new_base.paste(uptime_pic, (0, (cputemp_pic.size[1] + 25)*2))
    new_base.paste(num_checkdht_pic, (cputemp_pic.size[0] + 50, (cputemp_pic.size[1] + 25)*2))
    # place text
    # outside_log  = list_of_datasets[0]
    # inside_log   = list_of_datasets[1]
    # sideroom_log = list_of_datasets[2]
    # outside_high, outside_low = find_high_lows(outside_log[1])
    # inside_high, inside_low = find_high_lows(inside_log[1])
    # sideroom_high, sideroom_low = find_high_lows(sideroom_log[1])
    # inside_text  = "Inside \n"
    # inside_text += "      High : " + str(inside_high) + "\n"
    # inside_text += "      Low  : " + str(inside_low)
    # outside_text  = "Outside \n"
    # outside_text += "      High : " + str(outside_high) + "\n"
    # outside_text += "      Low  : " + str(outside_low)
    # sideroom_text  = "Sideroom \n"
    # sideroom_text += "      High : " + str(sideroom_high) + "\n"
    # sideroom_text += "      Low  : " + str(sideroom_low)

    # font = ImageFont.truetype("../../resources/Caslon.ttf", 28)
    # d = ImageDraw.Draw(new_base)
    # d.text((left_pic.size[0] + 10,30), inside_text, font=font, fill=(50,200,50,255))
    # d.text((left_pic.size[0] + 10,120), outside_text, font=font, fill=(50,200,50,255))
    # d.text((left_pic.size[0] + 10,210), sideroom_text, font=font, fill=(50,200,50,255))

    # save datawall
    new_base.save(datawall_path)



    print(" --- datawall_test.py done and saved to " + datawall_path)
