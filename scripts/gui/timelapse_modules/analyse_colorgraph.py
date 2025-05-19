import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from concurrent.futures import ProcessPoolExecutor, as_completed

# Move the process_image function outside of the main function
def process_image(image_path):
    return color_intensity_ranges(image_path)

def color_intensity_ranges(image_path):
    # Open the image using PIL
    img = Image.open(image_path)

    # Convert the image to a NumPy array
    img_array = np.array(img)

    # Extract color channels
    red_channel = img_array[:, :, 0]
    green_channel = img_array[:, :, 1]
    blue_channel = img_array[:, :, 2]

    # Calculate differences in red, green, and blue intensities
    red_diff = red_channel - np.maximum(green_channel, blue_channel)
    green_diff = green_channel - np.maximum(red_channel, blue_channel)
    blue_diff = blue_channel - np.maximum(red_channel, green_channel)

    # Count pixels in different intensity ranges for each color (every 5% increment)
    counts_red = []
    counts_green = []
    counts_blue = []

    for i in range(0, 101, 5):
        lower_bound = i
        upper_bound = i + 5
        counts_red.append(np.sum((red_diff > lower_bound) & (red_diff <= upper_bound)))
        counts_green.append(np.sum((green_diff > lower_bound) & (green_diff <= upper_bound)))
        counts_blue.append(np.sum((blue_diff > lower_bound) & (blue_diff <= upper_bound)))

    return counts_red, counts_green, counts_blue

def analyse_set(ani_frame_list, out_file, progress_interval=50):
    # Graph display settings
    make_red = True
    make_green = True
    make_blue = True
    show_key = True

    # Ensure there are images in the list
    frame_count = len(ani_frame_list)
    if not ani_frame_list:
        print("No images in the list.")
        return False

    print(f"Preparing to process {frame_count} frames...")

    # Set up lists to store intensity counts
    red_intensity_counts = []
    green_intensity_counts = []
    blue_intensity_counts = []

    # Use ProcessPoolExecutor for parallel processing of images
    with ProcessPoolExecutor() as executor:
        # Submit all image processing tasks
        future_to_image = {executor.submit(process_image, image): image for image in ani_frame_list}

        # Iterate over completed tasks as they finish
        for i, future in enumerate(as_completed(future_to_image)):
            # Get the result (color intensities) from the future
            red, green, blue = future.result()

            # Append the results to the intensity count lists
            red_intensity_counts.append(red)
            green_intensity_counts.append(green)
            blue_intensity_counts.append(blue)

            # Print progress after every 'progress_interval' frames
            if (i + 1) % progress_interval == 0:
                print(f"Processed {i + 1} of {frame_count} frames...")

    print("Image data complete, creating graphs...")

    # Convert the results to NumPy arrays for easier manipulation
    red_intensity_counts = np.array(red_intensity_counts)
    green_intensity_counts = np.array(green_intensity_counts)
    blue_intensity_counts = np.array(blue_intensity_counts)

    # Set the figure size based on the number of data points and intensity ranges
    num_data_points = len(green_intensity_counts)
    num_intensity_ranges = green_intensity_counts.shape[1] - 1  # Ignore the last bin (100-105%)

    # Count how many graphs we need to make based on the options
    num_plots = sum([make_red, make_green, make_blue])

    # Define maximum size limits for the figure
    max_width_pixels = 20000  # Maximum width in pixels
    max_height_pixels = 15000  # Maximum height in pixels

    # Calculate the appropriate figure width and height dynamically based on data
    bar_width_per_data_point = 10
    fig_width = max(10, min(num_data_points * bar_width_per_data_point / 100, max_width_pixels / 100))

    # For height, we scale it based on the number of plots
    bar_height_per_graph = 1000  # Base height per graph
    fig_height = min(bar_height_per_graph * num_plots / 100, max_height_pixels / 100)

    # Create a figure with subplots, stacking vertically
    fig, axs = plt.subplots(num_plots, 1, figsize=(fig_width, fig_height))

    # Handle the case when there is only one plot
    if num_plots == 1:
        axs = [axs]  # Convert to a list to keep the indexing logic consistent

    # Color maps for Red, Green, and Blue
    cmaps = {
        'red': plt.get_cmap('Reds'),
        'green': plt.get_cmap('Greens'),
        'blue': plt.get_cmap('Blues')
    }

    # Track the current subplot index
    subplot_index = 0

    # Plot Red intensity graph (if enabled)
    if make_red:
        cmap = cmaps['red']
        bottom = np.zeros(len(red_intensity_counts))  # Initialize the bottom to start from zero
        for i in range(num_intensity_ranges-1, -1, -1):  # Loop in reverse order (highest intensity at bottom)
            color = cmap((i + 1) / (num_intensity_ranges + 1))
            axs[subplot_index].bar(
                range(len(red_intensity_counts)),
                red_intensity_counts[:, i],
                color=color,
                label=f'{i * 5}-{(i + 1) * 5}%',
                bottom=bottom  # Stack bars on top of previous ones
            )
            bottom += red_intensity_counts[:, i]  # Update the bottom for the next range
        axs[subplot_index].set_ylabel('Red Pixel Count')
        if show_key:
            axs[subplot_index].legend()
        axs[subplot_index].set_title('Red Intensity')
        subplot_index += 1

    # Plot Green intensity graph (if enabled)
    if make_green:
        cmap = cmaps['green']
        bottom = np.zeros(len(green_intensity_counts))  # Initialize the bottom to start from zero
        for i in range(num_intensity_ranges-1, -1, -1):  # Loop in reverse order (highest intensity at bottom)
            color = cmap((i + 1) / (num_intensity_ranges + 1))
            axs[subplot_index].bar(
                range(len(green_intensity_counts)),
                green_intensity_counts[:, i],
                color=color,
                label=f'{i * 5}-{(i + 1) * 5}%',
                bottom=bottom  # Stack bars on top of previous ones
            )
            bottom += green_intensity_counts[:, i]  # Update the bottom for the next range
        axs[subplot_index].set_ylabel('Green Pixel Count')
        if show_key:
            axs[subplot_index].legend()
        axs[subplot_index].set_title('Green Intensity')
        subplot_index += 1

    # Plot Blue intensity graph (if enabled)
    if make_blue:
        cmap = cmaps['blue']
        bottom = np.zeros(len(blue_intensity_counts))  # Initialize the bottom to start from zero
        for i in range(num_intensity_ranges-1, -1, -1):  # Loop in reverse order (highest intensity at bottom)
            color = cmap((i + 1) / (num_intensity_ranges + 1))
            axs[subplot_index].bar(
                range(len(blue_intensity_counts)),
                blue_intensity_counts[:, i],
                color=color,
                label=f'{i * 5}-{(i + 1) * 5}%',
                bottom=bottom  # Stack bars on top of previous ones
            )
            bottom += blue_intensity_counts[:, i]  # Update the bottom for the next range
        axs[subplot_index].set_ylabel('Blue Pixel Count')
        if show_key:
            axs[subplot_index].legend()
        axs[subplot_index].set_title('Blue Intensity')
        subplot_index += 1

    # Set common x-label and adjust layout to reduce whitespace
    for ax in axs:
        ax.set_xlabel('Frame Index')

    plt.tight_layout()  # Ensures the layout is tight to the edges

    # Save the figure
    plt.savefig(out_file)
    plt.close()

    print(f"Analysis complete. Result saved to {out_file}")
    return True
