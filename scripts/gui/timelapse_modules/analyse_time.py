import matplotlib.pyplot as plt
import os
from datetime import datetime

def analyse_set(ani_frame_list, out_file):
    # Ensure there are images in the list
    if not ani_frame_list:
        print("No images in the list.")
        return False

    # Get creation dates for each image
    file_dates = [date_from_filename(image_path)[1] for image_path in ani_frame_list]

    # Calculate time differences from the first date
    time_diffs = [(file_date - file_dates[0]).total_seconds() for file_date in file_dates]

    # Set the figure size based on the number of data points
    num_data_points = len(time_diffs)
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

    # Create a line graph
    plt.plot(range(len(time_diffs)), time_diffs, color='blue', marker='o', markersize=5)

    # Adjust the layout to reduce empty space
    plt.subplots_adjust(left=0.005, right=0.99, top=0.9, bottom=0.1)

    plt.xlabel('Frame Index')
    plt.ylabel('Time Difference (seconds)')

    plt.savefig(out_file)
    plt.close()
    print(f"Analysis complete. Result saved to {out_file}")
    return True

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
