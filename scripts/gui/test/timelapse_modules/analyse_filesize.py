
import matplotlib.pyplot as plt
import os

def analyse_set(ani_frame_list, temp_folder):
    # Ensure there are images in the list
    if not ani_frame_list:
        print("No images in the list.")
        return

    # Get file sizes for each image
    file_sizes = [os.path.getsize(image_path) for image_path in ani_frame_list]

    # Set the figure size based on the number of data points
    num_data_points = len(file_sizes)
    fig_width = max(1, num_data_points * 0.15)  # Adjust the minimum figure width as needed

    # Set the maximum image size
    max_image_size = 75000

    # Check if the resulting image would exceed the maximum size
    result_width = int(fig_width * 100)  # Assuming each bar has a width of 100 pixels
    result_height = 1000  # Assuming the height of the bar graph is 1000 pixels
    if result_width > max_image_size or result_height > max_image_size:
        print("Error: Resulting image exceeds the maximum allowed size.")
        return

    plt.figure(figsize=(fig_width, 10))

    # Create a bar graph
    plt.bar(range(len(file_sizes)), file_sizes, color='blue', width=0.6)

    # Adjust the layout to reduce empty space
    plt.subplots_adjust(left=0.005, right=0.99, top=0.9, bottom=0.1)

    plt.savefig(temp_folder + "/file_size_graph.png")
    plt.close()
    print(f"Analysis complete. Result saved to {temp_folder}/file_size_graph.png")
    return temp_folder + "/file_size_graph.png"
