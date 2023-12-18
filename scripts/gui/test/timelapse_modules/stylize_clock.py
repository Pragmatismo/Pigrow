from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import math


def stylize_set(ani_frame_list, out_folder, set_name, img_type="png"):
    img_type = "png"
    show_clockface = False
    image = Image.open(ani_frame_list[0])
    width, height = image.size
    if show_clockface == True:
        carry_image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    else:
        carry_image = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    clock_face = draw_clock_face(ani_frame_list[0])

    for x in range(0, len(ani_frame_list) - 1):
        _, start_time = date_from_filename(ani_frame_list[x])
        _, end_time   = date_from_filename(ani_frame_list[x + 1])
        image_path = ani_frame_list[x]
        print(start_time, end_time, image_path)
        result_image = create_clock_slice(start_time, end_time, image_path)

        epoch_time = int(start_time.timestamp())
        output_path = os.path.join(out_folder, f"{set_name}_{epoch_time}.{img_type}")

        carry_image.paste(result_image, (0, 0), mask=result_image)
        if show_clockface == True:
            carry_image.paste(clock_face, (0, 0), mask=clock_face)
        carry_image.save(output_path)

    return "Created set", out_folder, set_name, img_type

def create_clock_slice(start_time, end_time, image_path):
    # Load the image
    image = Image.open(image_path)
    width, height = image.size

    # Calculate the angles based on the start and end times
    start_angle = -90 + (start_time.hour % 24) * (360 / 24) + start_time.minute * (360 / (24 * 60))
    end_angle = -90 + (end_time.hour % 24) * (360 / 24) + end_time.minute * (360 / (24 * 60))

    # Create a black image for the clock slice
    clock_slice = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_segment = ImageDraw.Draw(clock_slice)

    # Calculate the center of the image
    center = (width // 2, height // 2)

    # Calculate the points on the circumference of the circle
    radius = max(width, height) #// 2
    start_point = (
        center[0] + int(radius * math.cos(math.radians(start_angle))),
        center[1] + int(radius * math.sin(math.radians(start_angle)))
    )
    end_point = (
        center[0] + int(radius * math.cos(math.radians(end_angle))),
        center[1] + int(radius * math.sin(math.radians(end_angle)))
    )

    # Create a polygon by connecting the center to the points on the circumference
    polygon_points = [center, start_point, end_point]
    draw_segment.polygon(polygon_points, fill=(0, 0, 0, 255), outline=None)

    # Paste the clock slice onto a transparent background
    result_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result_image.paste(clock_slice, (0, 0), mask=clock_slice)

    # Paste the source image onto the clock slice
    result_image.paste(image, (0, 0), mask=clock_slice)

    return result_image

def draw_clock_face(image_path):
    # Load the image
    image = Image.open(image_path)
    width, height = image.size

    # Create a transparent image for the clock face
    clock_face = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(clock_face)

    # Calculate the center of the image
    center = (width // 2, height // 2)

    # Calculate the radius based on the half of the image size
    radius = min(width, height) // 2

    # Draw a circle on the clock face
    draw.ellipse([(center[0] - radius, center[1] - radius),
                  (center[0] + radius, center[1] + radius)],
                 outline=(0, 0, 0, 255))

    # Label each hour from 0 to 23
    for hour in range(24):
        angle = -90 + (hour % 24) * (360 / 24)
        hour_point = (
            center[0] + int(radius * math.cos(math.radians(angle))),
            center[1] + int(radius * math.sin(math.radians(angle)))
        )
        draw.text(hour_point, str(hour), fill=(0, 0, 0, 255))

    # Paste the clock face onto the original image
    result_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result_image.paste(clock_face, (0, 0), mask=clock_face)

    # Paste the source image onto the clock face
    result_image.paste(image, (0, 0), mask=clock_face)

    return result_image

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
