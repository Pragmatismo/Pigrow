import os

def trim_list(original_frame_list, block_size):
    largest_file_list = []
    for x in range(0, len(original_frame_list), block_size):
        temp_list = []
        for y in range(0, block_size):
            try:
                temp_list.append(original_frame_list[x+y])
            except:
                pass
                #print("index out of range - because of the y probably")
        largest_file_size = 0
        for item in temp_list:
            filesize = os.path.getsize(item)
            if largest_file_size < int(filesize):
                largest_file_size = int(filesize)
                largset_file = (item)
        largest_file_list.append(largset_file)
    return largest_file_list
