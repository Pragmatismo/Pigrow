import os

def trim_list(original_frame_list, block_size):
    #find average of all files
    total_file_size = 0
    for cap_file in original_frame_list:
        total_file_size = total_file_size + int(os.path.getsize(cap_file))
    average_file_size = total_file_size / len(original_frame_list)
    print("Average file size:", average_file_size)
    
    most_ave_file_list = []
    for x in range(0, len(original_frame_list), block_size):
        temp_list = []
        for y in range(0, block_size):
            try:
                temp_list.append(original_frame_list[x+y])
            except:
                pass

        # find smallest difference from average
        smallest_diff = average_file_size + 1
        for cap_file in temp_list:
            size = int(os.path.getsize(cap_file))
            size_diff = abs(average_file_size - size)
            if smallest_diff > size_diff:
                #print("smaller size diference - ", size_diff)
                most_average_file = cap_file
                smallest_diff = size_diff
            #else:
                #print("nope", size_diff)
        most_ave_file_list.append(most_average_file)
    return most_ave_file_list
