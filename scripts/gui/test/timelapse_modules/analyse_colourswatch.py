
from PIL import Image

def analyse_set(ani_frame_list, out_file):
    # Ensure there are images in the list
    if not ani_frame_list:
        print("No images in the list.")
        return False

    # Open the first image to get dimensions
    first_image = Image.open(ani_frame_list[0])
    width, height = first_image.size

    # Set the maximum image size
    max_image_size = 10000

    # Check if the resulting image would exceed the maximum size
    bar_size = 25
    result_width = len(ani_frame_list) * bar_size
    while result_width > max_image_size:
        bar_size = bar_size - 2
        if bar_size <= 0:
            print("Frame list too long to create swatch, sorry")
            return "error - frame list too long"
        result_width = len(ani_frame_list) * bar_size
    print("Bar size set to", bar_size)


    # Create a background image to paste strips onto
    result_image = Image.new("RGBA", (result_width, height), (0, 0, 0, 0))

    # Iterate through the image list and paste strips onto the result image
    for i, image_path in enumerate(ani_frame_list):
        # Open each image and extract a 25-pixel-wide strip from the center
        current_image = Image.open(image_path)
        left = (width - bar_size) // 2
        right = left + bar_size
        strip = current_image.crop((left, 0, right, height))

        # Paste the strip onto the result image
        result_image.paste(strip, (i * bar_size, 0))

    # Save or display the result image as needed
    result_image.save(out_file)
    print(f"Analysis complete. Result saved to {out_file}")
    return True
