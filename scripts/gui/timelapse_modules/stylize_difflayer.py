from PIL import Image, ImageChops
from datetime import datetime
import os
import math


def stylize_set(ani_frame_list, out_folder, set_name, img_type="png"):
    img_type = "png"
    bg_white = False
    test_image    = Image.open(ani_frame_list[0])
    width, height = test_image.size
    if bg_white == True:
        carry_image = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    else:
        carry_image = Image.new("RGBA", (width, height), (0, 0, 0, 255))

    carry_image = Image.open(ani_frame_list[0]).convert("RGBA")

    for x in range(0, len(ani_frame_list) - 1):
        image_path1 = ani_frame_list[x]
        image_path2 = ani_frame_list[x+1]
        print(x, image_path1, image_path2)

        img1 = Image.open(image_path1).convert("RGBA")
        img2 = Image.open(image_path2).convert("RGBA")
        #result_image = ImageChops.add_modulo(img1, img2)
        result_image = ImageChops.difference(img1, img2)
        result_image.putalpha(0)

        filename = os.path.splitext(os.path.basename(image_path2))[0]
        epoch_time = filename.split("_")[-1]
        output_path = os.path.join(out_folder, f"{set_name}_{epoch_time}.{img_type}")


        #carry_image.paste(result_image)
        final_img = ImageChops.add_modulo(carry_image, result_image)

        carry_image = final_img
        carry_image.save(output_path)

    return "Created set", out_folder, set_name, img_type
