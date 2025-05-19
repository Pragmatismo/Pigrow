import os

def trim_list(original_frame_list, block_size):
    most_ave_file_list = []
    for x in range(0, len(original_frame_list), block_size):
        temp_list = []
        for y in range(0, block_size):
            try:
                temp_list.append(original_frame_list[x+y])
            except:
                #print("index out of range - because of the y probably")
                pass
        # find rolling average file size
        total_file_size = 0
        for file in temp_list:
            total_file_size = total_file_size + int(os.path.getsize(file))
        average_file_size = total_file_size / len(temp_list)
        #print("Average file size:", average_file_size)

        # find smallest difference from average
        smallest_diff = average_file_size + 1
        for file in temp_list:
            size = int(os.path.getsize(file))
            size_diff = abs(average_file_size - size)
            if smallest_diff > size_diff:
                #print("smaller size diference - ", size_diff)
                most_average_file = file
                smallest_diff = size_diff
            #else:
                #print("nope", size_diff)
        most_ave_file_list.append(most_average_file)
    return most_ave_file_list
