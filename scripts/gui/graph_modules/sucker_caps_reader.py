
def run_sucker():
    #
    #   Very Basic Image Analasis Data Sucker
    #
    #           This takes a folder and reads all the image files in it
    #           and gathers some basic data which can be loaded into the
    #           gui and used to graph or make comparison graphs
    #
    # Settings
    file_folder_path = "/home/odaf/frompigrow/Bedroom/caps/"
    file_type = "jpg"
    #use_values_set = "pixel value" # "pixel value" or "file size"
    use_values_set = "file size"   # using pixel value on large sets might take a really long time
    use_dates_set = "file name"    # "file name" or "modified"
    #use_dates_set = "modified"
    limit_to_last = None            # a number or None
    #
    import os
    import numpy
    import datetime
    from PIL import Image

    print("Reading image inforamtion from " + file_folder_path)

    def date_from_fn(thefilename):
        #
        # Read the filename date and return a datetime object
        #
        if "." in thefilename and "_" in thefilename:
            fdate = thefilename.split(".")[0].split("_")[-1]
            if len(fdate) == 10 and fdate.isdigit():
                fdate = datetime.datetime.utcfromtimestamp(float(fdate))
            else:
                return None
            return fdate

    def get_pixel_values(c_photo):
        # Very basic image analasis
        #     - it just adds up all the pixel values
        #       and returns the totals for R, G, B amd all three combined
        pil_c_photo = Image.open(c_photo)
        numpy_pic = numpy.array(pil_c_photo)
        r_sum = numpy_pic[:,:,0].sum()
        g_sum = numpy_pic[:,:,1].sum()
        b_sum = numpy_pic[:,:,2].sum()
        tot_sum = r_sum + g_sum + b_sum
        #print("Pixel Values of; " + str(c_photo))
        #print("Red:" + str(r_sum))
        #print("Green:" + str(g_sum))
        #print("Blue:" + str(b_sum))
        #print("Total;" + str(tot_sum))
        return r_sum, g_sum, b_sum, tot_sum

    # define empty lists to fill
    # date info
    file_name_dates = []
    mod_dates = []
    # values info
    pixel_values = []
    file_sizes = []
    # key info
    keys = []

    # read the folder, sort through all the jpgs and analise them
    files = os.listdir(file_folder_path)
    files.sort()
    if not limit_to_last == None:
        if not limit_to_last > len(files):
            files = files[-limit_to_last:]
    counter = 1
    for file in files:
        if file.split(".")[-1] == file_type:
            file_path = os.path.join(file_folder_path, file)
            # Pixel Values
            if use_values_set == "pixel value":
                r, g, b, t = get_pixel_values(file_path)
                pixel_values.append(t)
            else:
                # File Size
                statinfo = os.stat(file_path)
                file_sizes.append(statinfo.st_size)
            # File last modified time
            moddate = os.path.getmtime(file_path)
            moddate = datetime.datetime.fromtimestamp(moddate)
            mod_dates.append(moddate)
            # Date from File name
            file_name_date = date_from_fn(file)
            file_name_dates.append(file_name_date)
            # Set filename as key
            keys.append(file)

    # Choose which sets to return
    # Values
    if use_values_set == "pixel value":
        values = pixel_values
    elif use_values_set == "file size":
        values = file_sizes
    # Dates
    if use_dates_set == "file name":
        dates = file_name_dates
    elif use_dates_set == "modified":
        dates = mod_dates
    # Keys
    keys = keys

    # sort them into date order so we can take the last n amount, this for testing only
    zipped = zip(dates, values, keys)
    zipped = sorted(zipped, key=lambda x: x[0])
    unzipped = list(zip(*zipped))
    print("--------------")
    print (len(unzipped))
    print (len(unzipped[0]))
    dates, values, keys = unzipped[0], unzipped[1], unzipped[2]

    # Hand back the values to the gui,they must be even sized lists
    return values, dates, keys
