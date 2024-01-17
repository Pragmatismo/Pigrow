import os
from datetime import datetime
from collections import defaultdict
#from PIL import Image, ImageDraw
from PIL import Image, ImageDraw, ImageFont


def shrink_image(image_path, bar_width, bar_height):
    #if bar_height > 1:
    #    bar_height = bar_height + 1
    current_image = Image.open(image_path)
    return current_image.resize((bar_width, bar_height))

def find_vertical_position(hour, minute, img_height):
    return (hour * 60 + minute) * (img_height / (24 * 60))

def draw_labels_and_markers(draw, left_section_width, img_height):
    # Draw hour labels and lines
    for hour in range(0, 24):
        label_position = (left_section_width - 25, find_vertical_position(hour, 0, img_height))
        draw.text((label_position[0] + 5, label_position[1]), str(hour), fill="black")
        draw.line([(label_position[0], label_position[1]), (label_position[0] + 25, label_position[1])], fill="black", width=1)

        # Draw shorter lines for every 5-minute period
        for minute in range(5, 60, 5):
            marker_position = (left_section_width - 10, find_vertical_position(hour, minute, img_height))
            draw.line([(marker_position[0], marker_position[1]), (marker_position[0] + 10, marker_position[1])], fill="black", width=1)

def label_day_bar(top_img, day, x_pos, bar_width, bar_height):
    # Create a drawing object
    draw = ImageDraw.Draw(top_img)

    # Specify font and size
    font = ImageFont.load_default()

    # Calculate the width and height of the text
    text_width, text_height = draw.textsize(day.strftime('%b'), font=font)

    # Calculate the position to center the text in the bar
    label_position = ((x_pos + x_pos + bar_width - text_width) // 2, 5)

    # Draw the text on the image
    date_label = day.strftime('%b %d')
    draw.text(label_position, date_label, fill="black", font=font)

    # draw marker lines
    draw.line([(x_pos, bar_height - 5), (x_pos, bar_height)], fill="black", width=1)
    draw.line([(x_pos + bar_width, bar_height - 10), (x_pos + bar_width, bar_height)], fill="black", width=1)

    return top_img

def analyse_set(ani_frame_list, out_file):
    show_labels = True
    bar_width = 100
    bar_height = 25
    left_section_width = 30
    top_section = 20

    # Ensure there are images in the list
    if not ani_frame_list:
        print("No images in the list.")
        return False

    # Iterate through the image list and organize images into dict by day
    day_images = defaultdict(list)
    for image_path in ani_frame_list:
        _, date_time = date_from_filename(image_path)
        day_images[date_time.date()].append((date_time, image_path))

    # tell the user how many images per day
    for key in day_images:
        print(key, "has", len(day_images[key]), "images")

    # create background for main image
    img_width = (len(day_images) * bar_width)
    max_images_per_day = max(len(images) for images in day_images.values())
    img_height = max_images_per_day * bar_height
    result_image = Image.new("RGBA", (img_width, img_height), (255, 105, 180, 255))
    #draw = ImageDraw.Draw(result_image)

    if show_labels == True:
        # create background for left section with hour labels and 5min markers
        left_section = Image.new("RGBA", (left_section_width, img_height), (255, 255, 255, 255))
        left_draw = ImageDraw.Draw(left_section)
        # Draw hour labels and markers
        draw_labels_and_markers(left_draw, left_section_width, img_height)

        # create background for top section with day labels
        full_width = left_section_width + img_width
        full_heigh = top_section + img_height
        final_image = Image.new("RGBA", (full_width, full_heigh), (255, 255, 255, 255))


    # create display area
    # Loop through day_images dictionary
    for i, (day, images) in enumerate(sorted(day_images.items())):
        print("Processing", day)
        x_pos = (i * bar_width)
        if show_labels == True:
            label_day_bar(final_image, day, x_pos+left_section_width, bar_width, bar_height)

        for time, image_path in images:
            # Calculate the position based on the time
            time_position = int(find_vertical_position(time.hour, time.minute, img_height))
            # shrink image and overlay onto the background
            shrunk_image = shrink_image(image_path, bar_width, bar_height)
            result_image.paste(shrunk_image, (x_pos, time_position))

    if show_labels == True:
        # add left section to the result image
        label_image = Image.new("RGBA", (img_width + left_section_width, img_height), (255, 255, 255, 255))
        label_image.paste(left_section, (0, 0))
        label_image.paste(result_image, (left_section_width, 0))
        # add top bar to image
        final_image.paste(label_image, (0, top_section))

        # Save or display the result image as needed
        final_image.save(out_file)
    else:
        result_image.save(out_file)

    print(f"Analysis complete. Result saved to {out_file}")
    return True

# def analyse_set(ani_frame_list, temp_folder):
#     bar_width=100
#     bar_height=50
#
#     # Ensure there are images in the list
#     if not ani_frame_list:
#         print("No images in the list.")
#         return
#
#     # Iterate through the image list and organize images into dict by day
#     day_images = defaultdict(list)
#     for image_path in ani_frame_list:
#         _, date_time = date_from_filename(image_path)
#         day_images[date_time.date()].append((date_time, image_path))
#     # tell user how many images per day
#     for key in day_images:
#         print(key, "has", len(day_images[key]), "images")
#
#     # create background for image
#     img_width = len(day_images) * bar_width
#     max_images_per_day = max(len(images) for images in day_images.values())
#     img_height = max_images_per_day * bar_height
#     result_image = Image.new("RGBA", (img_width, img_height), (255, 105, 180, 255))
#
#     # Loop through day_images dictionary
#     for i, (day, images) in enumerate(sorted(day_images.items())):
#         print("Processing", day)
#         for time, image_path in images:
#             # Calculate the position based on the time
#             time_position = (time.hour + time.minute / 60) * bar_height * (img_height / (24 * bar_height))
#             line_start = (bar_width * i, time_position)
#             # shrink image and overlay onto background
#             shrunk_image = shrink_image(image_path, bar_width, bar_height)
#             result_image.paste(shrunk_image, (i * bar_width, int(time_position)))
#
#     # Save or display the result image as needed
#     result_image.save(temp_folder + "/result_image.png")
#     print(f"Analysis complete. Result saved to {temp_folder}/result_image.png")
#     return temp_folder + "/result_image.png"


def date_from_filename(image_path):
    # Extract the file name without extension and folders
    s_file_name, file_extension = os.path.splitext(os.path.basename(image_path))
    file_name = s_file_name + file_extension

    # Check if the file name contains an underscore
    if '_' in file_name:
        # Extract the last section after the final underscore
        last_section = s_file_name.rsplit('_', 1)[-1]

        # Try to parse the last section as a Linux epoch
        try:
            epoch_time = int(last_section)
            date = datetime.utcfromtimestamp(epoch_time)
            return file_name, date
        except ValueError:
            pass

        # Try to parse the last section as a common date string
        try:
            date = datetime.strptime(last_section, '%Y%m%d%H%M%S')
            return file_name, date
        except ValueError:
            pass

    return file_name, 'undetermined'
