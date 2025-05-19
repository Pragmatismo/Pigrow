import os
from datetime import datetime
from datetime import time as dt_time
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont

# Import get_suntimes function from suntime library
from suntime import Sun
sun = Sun(51.509865, -0.118092)  # Example coordinates (London)

def shrink_image(image_path, bar_width, bar_height):
    current_image = Image.open(image_path)
    return current_image.resize((bar_width, bar_height))

def find_vertical_position(hour, minute, img_height):
    return (hour * 60 + minute) * (img_height / (24 * 60))

def draw_labels_and_markers(draw, left_section_width, img_height):
    # Dynamically calculate the available height between hours and set the font size
    hour_height = img_height / 24
    font_size = int(hour_height * 0.5)  # Set font size to 50% of the available hour height
    font = ImageFont.truetype("Antonio-Regular.ttf", font_size)

    for hour in range(0, 24):
        label_position = (left_section_width - 120, find_vertical_position(hour, 0, img_height))
        draw.text((label_position[0] + 5, label_position[1]), str(hour), fill="black", font=font)
        draw.line([(label_position[0], label_position[1]), (label_position[0] + 35, label_position[1])], fill="black", width=2)

        # Draw shorter lines for every 5-minute period
        for minute in range(5, 60, 5):
            marker_position = (left_section_width - 20, find_vertical_position(hour, minute, img_height))
            draw.line([(marker_position[0], marker_position[1]), (marker_position[0] + 20, marker_position[1])], fill="black", width=1)


def label_day_bar(top_img, day, x_pos, bar_width, top_section):
    draw = ImageDraw.Draw(top_img)

    # Dynamically calculate the font size based on 80% of the bar width (since the text is rotated)
    font_size = int(bar_width * 0.5)  # Set the font size to 50% actually (as per your code)
    font = ImageFont.truetype("Antonio-Regular.ttf", font_size)

    text = day.strftime('%b %d')

    # Use textbbox to measure the text instead of textsize
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create an image for the rotated text
    rotated_text = Image.new('RGBA', (top_section, text_height), (255, 255, 255, 0))
    rotated_draw = ImageDraw.Draw(rotated_text)
    rotated_draw.text((0, 0), text, font=font, fill="black")
    rotated_text = rotated_text.rotate(90, expand=True)

    # Paste the rotated text onto the top image
    top_img.paste(rotated_text, (x_pos, 0), rotated_text)

    # Draw vertical lines around the day label
    draw.line([(x_pos, top_section - 100), (x_pos, top_section)], fill="black", width=2)
    draw.line([(x_pos + bar_width, top_section - 10), (x_pos + bar_width, top_section)], fill="black", width=2)

    return top_img


def analyse_set(ani_frame_list, out_file):
    show_labels = True
    bar_width = 150
    left_section_width = 150
    top_section = 290
    full_day_minutes = 24 * 60

    if not ani_frame_list:
        print("No images in the list.")
        return False

    day_images = defaultdict(list)
    for image_path in ani_frame_list:
        _, date_time = date_from_filename(image_path)
        day_images[date_time.date()].append((date_time, image_path))

    for key in day_images:
        print(key, "has", len(day_images[key]), "images")

    img_width = len(day_images) * bar_width
    img_height = full_day_minutes  # Full height for 24 hours (1440 minutes)
    result_image = Image.new("RGBA", (img_width, img_height), (255, 105, 180, 255))  # Background is shown where missing

    if show_labels:
        left_section = Image.new("RGBA", (left_section_width, img_height), (255, 255, 255, 255))
        left_draw = ImageDraw.Draw(left_section)
        draw_labels_and_markers(left_draw, left_section_width, img_height)
        full_width = left_section_width + img_width
        full_height = top_section + img_height
        final_image = Image.new("RGBA", (full_width, full_height), (255, 255, 255, 255))

    for i, (day, images) in enumerate(sorted(day_images.items())):
        print("Processing", day)
        x_pos = i * bar_width
        if show_labels:
            label_day_bar(final_image, day, x_pos + left_section_width, bar_width, top_section)

        # Sort the images by time to ensure correct order
        images.sort(key=lambda x: x[0])

        # Calculate the time gap between the first two images to set a standard slice height
        if len(images) > 1:
            first_image_time = images[0][0]
            second_image_time = images[1][0]
            time_gap = (second_image_time - first_image_time).total_seconds() / 60  # Time gap in minutes
        else:
            # If there's only one image, default the time gap to 30 minutes for reasonable scaling
            time_gap = 30

        # Scale the image height based on the time gap
        slice_height = int((time_gap / full_day_minutes) * img_height)

        for j, (time, image_path) in enumerate(images):
            # Determine the time position of the current image
            time_position = int(find_vertical_position(time.hour, time.minute, img_height))

            # Shrink the image to fit the calculated slice height
            shrunk_image = shrink_image(image_path, bar_width, slice_height)
            result_image.paste(shrunk_image, (x_pos, time_position))

        # Draw red lines for sunrise and sunset
        day_datetime = datetime.combine(day, dt_time.min)
        sunrise = sun.get_sunrise_time(day_datetime)
        sunset = sun.get_sunset_time(day_datetime)

        sunrise_position = find_vertical_position(sunrise.hour, sunrise.minute, img_height)
        sunset_position = find_vertical_position(sunset.hour, sunset.minute, img_height)

        draw = ImageDraw.Draw(result_image)
        draw.line([(x_pos, sunrise_position), (x_pos + bar_width, sunrise_position)], fill="red", width=10)
        draw.line([(x_pos, sunset_position), (x_pos + bar_width, sunset_position)], fill="red", width=10)

    if show_labels:
        label_image = Image.new("RGBA", (img_width + left_section_width, img_height), (255, 255, 255, 255))
        label_image.paste(left_section, (0, 0))
        label_image.paste(result_image, (left_section_width, 0))
        final_image.paste(label_image, (0, top_section))
        final_image.save(out_file)
    else:
        result_image.save(out_file)

    print(f"Analysis complete. Result saved to {out_file}")
    return True



# Function to extract date from filename
def date_from_filename(image_path):
    s_file_name, file_extension = os.path.splitext(os.path.basename(image_path))
    file_name = s_file_name + file_extension

    if '_' in file_name:
        last_section = s_file_name.rsplit('_', 1)[-1]

        try:
            epoch_time = int(last_section)
            date = datetime.utcfromtimestamp(epoch_time)
            return file_name, date
        except ValueError:
            pass

        try:
            date = datetime.strptime(last_section, '%Y%m%d%H%M%S')
            return file_name, date
        except ValueError:
            pass

    return file_name, 'undetermined'
