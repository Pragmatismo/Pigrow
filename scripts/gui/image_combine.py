#!/usr/bin/python3
import sys
from PIL import Image
from PIL import ImageChops

class config():
    styles = ["slice", "Vslice", "dice"]
    combine_styles = ["stack", "diff"]

    def find_styles():
        print("styles=slice")

def combine(path_list, style, output_path="test_combine.jpg"):
    # load images
    im_a = Image.open(path_list[0])
    im_b = Image.open(path_list[1])
    if not im_a.size == im_b.size:
        print(" Images are not the same size!")
    # Perform the requested operation
    if style == "slice":
        final_image = ab_slice(im_a, im_b)
    elif style == "Vslice":
        final_image = ab_v_slice(im_a, im_b)
    elif style == "dice":
        final_image = ab_dice(im_a, im_b)
    # Save image and return path
    final_image.save(output_path)
    return output_path

def multi_combine(path_list, style, output_path="test_combine.jpg"):
    if style == "diff":
        final_image = combine_diff(path_list)
    elif style == "stack":
        final_image = stack_slices(path_list)
    # Save image and return path
    final_image.save(output_path)
    return output_path



# 2 image combiners
def ab_slice(im_a, im_b):
    '''
    Slices two images down the middle and puts them next to each other.
    '''
    print("slicing!")
    w, h = im_a.size
    middle = int(w / 2)
    im_a_crop = im_a.crop((0, 0, middle, h))
    #im_b_crop = im_b.crop((middle, 0, w, h))
    im_b_crop = im_b.crop((0, 0, middle, h))
    final_image = Image.new(im_a.mode, (w,h))
    final_image.paste(im_a_crop)
    final_image.paste(im_b_crop, (middle,0))
    return final_image

def ab_v_slice(im_a, im_b):
    '''
    Slices two images down the middle and puts them next to each other.
    '''
    print("slicing!")
    w, h = im_a.size
    middle = int(h / 2)

    im_a_crop = im_a.crop((0, 0, w, middle))
    #im_b_crop = im_b.crop((middle, 0, w, h))
    im_b_crop = im_b.crop((0, middle, w, h))
    final_image = Image.new(im_a.mode, (w,h))
    final_image.paste(im_a_crop)
    final_image.paste(im_b_crop, (0,middle))
    return final_image

def ab_dice(im_a, im_b):
    '''
    Dices the images into sections and combines them in stripes.
    '''
    print("dicing!")
    w, h = im_a.size
    slices = 10
    size_per_slice = int(w / slices)
    # cut into slices and add to a list
    current_pos = 0
    slice_list = []
    im_to_crop = im_a
    for x in range(0, slices):
        crop_w_end  = current_pos + size_per_slice
        img_crop = im_to_crop.crop((current_pos, 0, crop_w_end, h))
        slice_list.append(img_crop)
        current_pos = crop_w_end
        if im_to_crop == im_a:
            im_to_crop = im_b
        else:
            im_to_crop = im_a
    # cycle through list of slices adding them to a new image
    final_image = Image.new(im_a.mode, (w,h))
    current_pos = 0
    for slice in slice_list:
        final_image.paste(slice, (current_pos, 0))
        current_pos = current_pos + size_per_slice
    # return image
    return final_image


# multi image combiners
def combine_diff(im_set):
    '''
    This works through the set finding the differnces and adding them to a blank image.
    '''
    first_img = im_set[0]
    im_a = Image.open(im_set[0])
    w, h = im_a.size
    final_image = Image.new(im_a.mode, (w,h))
    for img in im_set:
        im_b = Image.open(img)
        diff_im = ImageChops.subtract(im_a, im_b)
        final_image = ImageChops.add(final_image, diff_im)
    return final_image

# multi image combiners
def stack_slices(im_set):
    '''
    Slices each image into strips and combine to make a single image.
    '''
    # find slice size
    im_a = Image.open(im_set[0])
    w, h = im_a.size
    slices = len(im_set)
    size_per_slice = int(w / slices)
    # cycle through cropping the images into slices
    current_pos = 0
    slice_list = []
    for x in range(0, slices):
        im_to_crop = Image.open(im_set[x])
        crop_w_end  = current_pos + size_per_slice
        img_crop = im_to_crop.crop((current_pos, 0, crop_w_end, h))
        slice_list.append(img_crop)
        current_pos = crop_w_end
    # construct new image
    final_image = Image.new(im_a.mode, (w,h))
    current_pos = 0
    for slice in slice_list:
        final_image.paste(slice, (current_pos, 0))
        current_pos = current_pos + size_per_slice
    # return image
    return final_image




if __name__ == '__main__':
    '''
    When ran from command line this must have path and style or combine set.
    '''
    # check for command line arguments
    sensor_location = ""
    request = ""
    setting_string = ""
    path_list = []
    style = ""
    combine = ""
    for argu in sys.argv[1:]:
        if "=" in argu:
            equals_pos = argu.find("=")
            thearg = argu[:equals_pos]
            thevalue = argu[equals_pos + 1:]
            if thearg == 'path':
                path_list = thevalue.split(",")
            if thearg == 'style':
                style = thevalue
            if thearg == 'combine':
                combine = thevalue
        elif 'help' in argu or argu == '-h':
            print(" Combines images for use in datawalls, and gui display")
            print("")
            print("  path=file1,file2,file3")
            print("      Supply two images for basic two image combiners")
            print("      or a list of images for multi-combine styles")
            print(" style=slice,Vslice,dice")
            print("      Combination of two images into a single image")
            print(" combine=diff")
            print("      Combine sets of images into more complex images.")
            sys.exit(0)
        elif argu == "-flags":
            print("path=file1,file2,file3")
            print("style=slice,Vslice,dice")
            print("combine=diff")
            print("")
            sys.exit(0)
        elif argu == "-styles":
            config.find_styles()
            sys.exit()

    if len(path_list) > 1:
        if not style == "" or not combine == "":
            if not style == "":
                out_file = combine(path_list, style)
            if not combine == "":
                out_file = multi_combine(path_list, combine)
        else:
            print("Must select a style")
            print("   image_combine path=image1.png,image2.png style=slice")
            sys.exit(1)
        print(" Image created and saved to " + out_file)
    else:
        print("You must supply at least two images to be combined")
        print("   image_combine path=image1.png,image2.png style=slice")
