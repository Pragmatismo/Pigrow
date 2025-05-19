#!/usr/bin/python3
"""
datawall_example.py

This script builds a datawall image using the data package passed in.
It now creates a switch display that appears in the left panel of the high/low & graph row.
For each switch (from the info_switch_position output), it draws a colored circle (green for “on”,
red for “off”), the text “ON”/“OFF” inside the circle, and below the circle the switch name.
The switch name is extracted from the text by taking the section before " is ".
"""
def read_datawall_options():
    '''
    Returns a dictionary of settings and their default values for use by the gui
    '''
    module_settings_dict = {
             "font_size":"18",
             }
    preset_req = {"info_read":["boxname",
                               "datetime",
                               "check_lamp",
                               "power_warnings",
                               "diskusage percent_only=true",
                               "switch_position",
                               "switch_log  duration=day7",
                               "error_log"],
                  "graphs":[("temp","weeksagemoss")],
                  "logs":[("temphumid","sibothmon")],
                  "pictures":[("recent","recent")]
                  }

    return module_settings_dict, preset_req

def make_datawall(data, opts=None):
    print(opts.get("font_size", "10"))
    import os
    from PIL import Image, ImageDraw, ImageFont

    # Determine appropriate resampling filter.
    try:
        resample_filter = Image.Resampling.LANCZOS  # Pillow 10+
    except AttributeError:
        resample_filter = Image.LANCZOS  # Older Pillow versions

    # --------------------------
    # HELPER FUNCTIONS
    # --------------------------
    def get_text_size(draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    def break_long_word(word, font, draw, max_width):
        pieces = []
        current_piece = ""
        for char in word:
            if get_text_size(draw, current_piece + char, font)[0] <= max_width:
                current_piece += char
            else:
                if current_piece:
                    pieces.append(current_piece)
                current_piece = char
        if current_piece:
            pieces.append(current_piece)
        return pieces

    def wrap_text(text, font, draw, max_width):
        words = text.split(" ")
        if not words:
            return []
        lines = []
        current_line = ""
        for word in words:
            if get_text_size(draw, word, font)[0] > max_width:
                word_parts = break_long_word(word, font, draw, max_width)
            else:
                word_parts = [word]
            for part in word_parts:
                if current_line:
                    candidate = current_line + " " + part
                else:
                    candidate = part
                if get_text_size(draw, candidate, font)[0] <= max_width:
                    current_line = candidate
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = part
        if current_line:
            lines.append(current_line)
        return lines

    # --------------------------
    # SETTINGS & FONTS
    # --------------------------
    datawall_width = 1024
    bg_color = (188, 184, 138)  # Sageish background
    text_color = (0, 0, 0)
    padding = 20  # Margins and spacing
    line_spacing = 5

    # Font sizes
    title_size = 40
    subtitle_size = 25
    normal_size = 20

    try:
        title_font = ImageFont.truetype("Antonio-Regular.ttf", title_size)
    except IOError:
        print("font error")
        title_font = ImageFont.load_default()
    try:
        subtitle_font = ImageFont.truetype("Antonio-Regular.ttf", subtitle_size)
    except IOError:
        subtitle_font = ImageFont.load_default()
    try:
        normal_font = ImageFont.truetype("Antonio-Regular.ttf", normal_size)
    except IOError:
        normal_font = ImageFont.load_default()

    # --------------------------
    # EXTRACT DATA FROM THE PACKAGE
    # --------------------------
    info = data.get("info", {})
    images = data.get("images", {})
    graphs = data.get("graphs", {})
    log_data = data.get("data", {})  # log preset data

    boxname = info.get("boxname", "Box Name")
    datetime_text = info.get("datetime", "")
    check_lamp = info.get("check_lamp", "")
    power_warn = info.get("power_warnings", "")
    diskusage = info.get("diskusage percent_only=true", "Not Found")
    switch_pos = info.get("switch_position", "")
    switch_log = info.get("switch_log  duration=day7", "")
    error_log = info.get("error_log", "")

    recent_image_path = images.get("recent", None)
    graph_image_path = graphs.get("temp", None)
    #graph_image_path = None
    #if graphs:
    #    graph_image_path = list(graphs.values())[0]

    # --------------------------
    # PROCESS THE DATASET (log preset)
    # --------------------------
    # We assume log_data["sibothmon"] is a list of dataset dictionaries.
    dataset = log_data.get("temphumid", None)
    highlow_lines = []
    if dataset:
        for ds in dataset:
            data_key = ds.get("key", "no key")
            tup_list = ds.get("trimmed_data", [])
            if tup_list:
                values = [val for (_, val) in tup_list]
                high_val = max(values)
                low_val = min(values)
            else:
                high_val, low_val = "N/A", "N/A"
            highlow_lines.append(f"{data_key}\n")
            highlow_lines.append(f"High: {high_val}")
            highlow_lines.append(f"Low: {low_val}")
            highlow_lines.append("\n\n")
        if highlow_lines and highlow_lines[-1] == "":
            highlow_lines.pop()
    else:
        highlow_lines = ["No dataset found"]

    highlow_text = "\n".join(highlow_lines)

    # --------------------------
    # LOAD AND SCALE IMAGES
    # --------------------------
    pic_image = None
    pic_new_width = datawall_width // 2  # 512 pixels
    pic_new_height = 0
    if recent_image_path and os.path.isfile(recent_image_path):
        try:
            pic_image = Image.open(recent_image_path)
            orig_w, orig_h = pic_image.size
            pic_new_height = int(orig_h * (pic_new_width / orig_w))
            pic_image = pic_image.resize((pic_new_width, pic_new_height), resample=resample_filter)
        except Exception as e:
            print("Error loading recent image:", e)
            pic_image = None

    left_col_width = datawall_width // 3
    right_col_x = left_col_width + 2 * padding
    graph_target_width = datawall_width - padding - right_col_x

    graph_img = None
    graph_new_height = 0
    if graph_image_path and os.path.isfile(graph_image_path):
        try:
            graph_img = Image.open(graph_image_path)
            orig_w, orig_h = graph_img.size
            graph_new_height = int(orig_h * (graph_target_width / orig_w))
            graph_img = graph_img.resize((graph_target_width, graph_new_height), resample=resample_filter)
        except Exception as e:
            print("Error loading graph image:", e)
            graph_img = None

    # --------------------------
    # MEASURE TEXT SIZES & DETERMINE LAYOUT
    # --------------------------
    dummy_img = Image.new("RGB", (datawall_width, 1000))
    draw_dummy = ImageDraw.Draw(dummy_img)

    boxname_size = get_text_size(draw_dummy, boxname, title_font)
    row1_height = boxname_size[1]

    datetime_size = get_text_size(draw_dummy, datetime_text, subtitle_font)
    row2_height = datetime_size[1]

    # --------------------------
    # ROW 3: Recent Image (left) and Info Text (right)
    # --------------------------
    left_x = padding
    image_height = pic_new_height if pic_image else 0
    right_x = left_x + pic_new_width + padding
    max_text_width = datawall_width - right_x - padding

    data_items = [
        f"Check Lamp: {check_lamp}",
        f"Power Warnings: {power_warn}",
        f"Disk Usage: {diskusage}"  # This line triggers our custom dial drawing.
    ]
    wrapped_lines = []
    for item in data_items:
        lines = wrap_text(item, normal_font, draw_dummy, max_text_width)
        wrapped_lines.extend(lines)
        wrapped_lines.append("")  # blank line separator
    if wrapped_lines and wrapped_lines[-1] == "":
        wrapped_lines.pop()

    standard_line_height = get_text_size(draw_dummy, "A", normal_font)[1]
    text_block_height = 0
    for line in wrapped_lines:
        if line == "":
            text_block_height += standard_line_height
        else:
            text_block_height += get_text_size(draw_dummy, line, normal_font)[1]
        text_block_height += line_spacing
    if wrapped_lines:
        text_block_height -= line_spacing

    if image_height > text_block_height:
        text_start_y = (image_height - text_block_height) // 2
    else:
        text_start_y = 0

    row3_height = max(image_height, text_block_height)

    # --------------------------
    # ROW 4: High/Low, "Switch Positions" Label, and Switch Circles (Left Panel) versus Graph (Right Panel)
    # --------------------------
    # Left panel dimensions:
    region_x = left_x
    region_width = right_col_x - region_x

    # Compute high/low block height.
    high_low_lines = highlow_text.split("\n")
    high_low_block_height = 0
    for line in high_low_lines:
        high_low_block_height += get_text_size(draw_dummy, line, normal_font)[1]
    if high_low_lines:
        high_low_block_height += line_spacing * (len(high_low_lines) - 1)

    # Measure the label "Switch Positions".
    switch_label_text = "Switch Positions"
    switch_label_size = get_text_size(draw_dummy, switch_label_text, normal_font)

    # Process the switch info (from switch_pos).
    switch_lines = switch_pos.splitlines()
    switches = []
    for line in switch_lines:
        parts = line.split(" is ")
        if len(parts) == 2:
            switch_name = parts[0].strip()
            status = parts[1].strip().lower()
            switches.append((switch_name, status))
    if switches:
        circle_diameter = 80
        spacing = 40
        # Compute total width and maximum name height.
        total_circles_width = len(switches) * circle_diameter + (len(switches) - 1) * spacing
        # For centering within the left panel region:
        circles_start_x = region_x + (region_width - total_circles_width) // 2
        max_name_height = 0
        for (name, _) in switches:
            tw, th = get_text_size(draw_dummy, name, normal_font)
            if th > max_name_height:
                max_name_height = th
        circles_area_height = circle_diameter + spacing + max_name_height  # circle plus vertical gap and name text
    else:
        circles_area_height = 0

    # Define vertical gaps.
    gap1 = 10  # gap between high/low block and label
    gap2 = 10  # gap between label and circles

    # Compute total left panel height.
    left_panel_height = high_low_block_height + gap1 + switch_label_size[1] + gap2 + circles_area_height
    # The row height is the maximum of the left panel and the graph image height.
    row4_height = max(left_panel_height, graph_new_height)

    # --------------------------
    # ROW 5: Log text (switch_log and error_log)
    # --------------------------
    switch_log_size = get_text_size(draw_dummy, switch_log, normal_font)
    error_log_size = get_text_size(draw_dummy, error_log, normal_font)
    row5_height = max(switch_log_size[1], error_log_size[1])

    # --------------------------
    # TOTAL IMAGE HEIGHT CALCULATION
    # --------------------------
    total_height = (padding + row1_height +
                    padding + row2_height +
                    padding + row3_height +
                    padding + row4_height +
                    padding + row5_height +
                    padding)
    final_img = Image.new("RGB", (datawall_width, total_height), color=bg_color)
    draw = ImageDraw.Draw(final_img)
    cur_y = padding

    # Row 1: Draw boxname (centered)
    x_boxname = (datawall_width - boxname_size[0]) // 2
    draw.text((x_boxname, cur_y), boxname, font=title_font, fill=text_color)
    cur_y += row1_height + padding

    # Row 2: Draw datetime text (centered)
    x_datetime = (datawall_width - datetime_size[0]) // 2
    draw.text((x_datetime, cur_y), datetime_text, font=subtitle_font, fill=text_color)
    cur_y += row2_height + padding

    # Row 3: Draw recent image (left) and info text (right)
    row3_y = cur_y
    if pic_image:
        final_img.paste(pic_image, (left_x, row3_y))
    text_y = row3_y + text_start_y
    for line in wrapped_lines:
        if line.startswith("Disk Usage:"):
            parts = line.split(":", 1)
            label = parts[0] + ":"
            draw.text((right_x, text_y), label, font=normal_font, fill=text_color)
            label_width, label_height = get_text_size(draw_dummy, label, normal_font)
            gap_inner = 5
            dial_x = right_x + label_width + gap_inner
            dial_width = 150
            dial_height = label_height + 8
            try:
                usage_percent = float(diskusage)
            except:
                usage_percent = 0.0
            bar_width = int(dial_width * (usage_percent / 100.0))
            if usage_percent < 75:
                bar_color = (0, 255, 0)
            elif usage_percent < 85:
                bar_color = (255, 165, 0)
            elif usage_percent < 98:
                bar_color = (139, 0, 0)
            else:
                bar_color = (255, 0, 0)
            dial_rect = [dial_x, text_y, dial_x + dial_width, text_y + dial_height]
            draw.rectangle(dial_rect, fill="white", outline="black")
            bar_rect = [dial_x, text_y, dial_x + bar_width, text_y + dial_height]
            draw.rectangle(bar_rect, fill=bar_color)
            percentage_text = f"{usage_percent:.0f}%"
            text_size = get_text_size(draw_dummy, percentage_text, normal_font)
            text_x_inner = dial_x + (dial_width - text_size[0]) // 2
            text_y_inner = text_y - 4 + (dial_height - text_size[1]) // 2
            draw.text((text_x_inner, text_y_inner), percentage_text, font=normal_font, fill=text_color)
            text_y += dial_height + line_spacing
        else:
            draw.text((right_x, text_y), line, font=normal_font, fill=text_color)
            if line == "":
                text_y += standard_line_height + line_spacing
            else:
                text_y += get_text_size(draw_dummy, line, normal_font)[1] + line_spacing
    cur_y += row3_height + padding

    # Row 4: Draw left panel and graph side-by-side.
    row4_y = cur_y
    # Left panel drawing:
    left_panel_y = row4_y
    # Draw high/low block:
    cur_y_left = left_panel_y
    for line in high_low_lines:
        line_size = get_text_size(draw_dummy, line, normal_font)
        line_x = region_x + (region_width - line_size[0]) // 2
        draw.text((line_x, cur_y_left), line, font=normal_font, fill=text_color)
        cur_y_left += line_size[1] + line_spacing
    # Gap between high/low block and label.
    cur_y_left += gap1
    # Draw "Switch Positions" label:
    label_x = region_x + (region_width - switch_label_size[0]) // 2
    draw.text((label_x, cur_y_left), switch_label_text, font=normal_font, fill=text_color)
    cur_y_left += switch_label_size[1] + gap2
    # Draw switch circles (if any):
    if switches:
        current_x = circles_start_x
        for (name, status) in switches:
            if status == "on":
                fill_color = (0, 255, 0)
            elif status == "off":
                fill_color = (255, 0, 0)
            else:
                fill_color = (128, 128, 128)
            circle_box = (current_x, cur_y_left, current_x + circle_diameter, cur_y_left + circle_diameter)
            draw.ellipse(circle_box, fill=fill_color, outline="black")
            status_text = status.upper()
            tw, th = get_text_size(draw, status_text, normal_font)
            text_x_circle = current_x + (circle_diameter - tw) // 2
            text_y_circle = cur_y_left + (circle_diameter - th) // 2
            draw.text((text_x_circle, text_y_circle), status_text, font=normal_font, fill="black")
            # Draw the switch name below the circle.
            name_tw, name_th = get_text_size(draw, name, normal_font)
            name_x = current_x + (circle_diameter - name_tw) // 2
            name_y = cur_y_left + circle_diameter
            draw.text((name_x, name_y), name, font=normal_font, fill=text_color)
            current_x += circle_diameter + spacing
    # End of left panel drawing.
    # Graph image: paste onto right side.
    if graph_img:
        final_img.paste(graph_img, (right_col_x, row4_y))
    cur_y += row4_height + padding

    # Row 5: Draw switch_log (left) and error_log (right)
    draw.text((padding, cur_y), switch_log, font=normal_font, fill=text_color)
    draw.text((datawall_width // 2 + padding, cur_y), error_log, font=normal_font, fill=text_color)
    cur_y += row5_height + padding

    # --------------------------
    # SAVE THE FINAL IMAGE
    # --------------------------
    output_path = './test_datawall.png'
    try:
        final_img.save(output_path)
    except Exception as e:
        print("Error saving datawall image:", e)
        return ""
    return output_path

