
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
    plt.figure(figsize=(fig_width, 10))

    # Create a bar graph
    plt.bar(range(len(file_sizes)), file_sizes, color='blue', width=0.6)

    plt.savefig(temp_folder + "/file_size_graph.png")
    plt.close()
    print(f"Analysis complete. Result saved to {temp_folder}/file_size_graph.png")
    return temp_folder + "/file_size_graph.png"
