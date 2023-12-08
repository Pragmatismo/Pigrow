
def trim_list(file_list, use_every):
    print(" Trimming frame list using strict method")
    trimmed_list = []
    for frame in range(0, len(file_list), use_every):
        trimmed_list.append(file_list[frame])
    return trimmed_list
