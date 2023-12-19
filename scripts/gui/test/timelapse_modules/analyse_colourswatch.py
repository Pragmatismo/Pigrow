
from PIL import Image

def analyse_set(ani_frame_list, temp_folder):
    # Ensure there are images in the list
    if not ani_frame_list:
        print("No images in the list.")
        return

    # Open the first image to get dimensions
    first_image = Image.open(ani_frame_list[0])
    width, height = first_image.size

    # Create a background image to paste strips onto
    result_image = Image.new("RGBA", (len(ani_frame_list) * 25, height), (0, 0, 0, 0))

    # Iterate through the image list and paste strips onto the result image
    for i, image_path in enumerate(ani_frame_list):
        # Open each image and extract a 25-pixel-wide strip from the center
        current_image = Image.open(image_path)
        left = (width - 25) // 2
        right = left + 25
        strip = current_image.crop((left, 0, right, height))

        # Paste the strip onto the result image
        result_image.paste(strip, (i * 25, 0))

    # Save or display the result image as needed
    result_image.save(temp_folder + "/result_image.png")
    print(f"Analysis complete. Result saved to {temp_folder}/result_image.png")
    return temp_folder + "/result_image.png"
