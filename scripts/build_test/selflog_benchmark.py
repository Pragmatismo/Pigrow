#!/usr/bin/env python3
import datetime, time
import os, sys
import psutil
from PIL import Image
from PIL import ImageDraw

##
## Raspberry Pi Python Benchmark Tool
##    This grabs a whole load of info and sticks it in a log file
##
homedir = os.getenv("HOME")
# set log location
log_location = homedir + '/Pigrow/logs/'
if not os.path.isdir(log_location):
    os.makedirs(log_location)
log_location = log_location + 'selflog_benchmark.txt'
# set temp files location
temp_location = homedir + '/Pigrow/temp/'
frame_folder_location = temp_location + "frames/"
if not os.path.isdir(frame_folder_location):
    os.makedirs(frame_folder_location)
#
repeat_times = 3
delay = 15
#
for argu in sys.argv:
    if argu == '-h' or '-help' in argu:
        print(" Pigrow Raspberry Pi Python Benchmark")
        print(" ")
        print("Runs a series of tests using python to determine the systems capabilities")
        print("")
        print("  - Requires python dependencies;")
        print("                                 PIL")
        print("                                 psutil")
        print("  - Requires apt install of;")
        print("                            MPV     - video rendering")
        print("")
        print("The log created can be graphed with the remote_gui")
        print("")
        print("  repeat=3      Amount of times to run the tests")
        print("")
        sys.exit(0)
    if argu == '-flags':
        print("repeat=[num]")
        sys.exit(0)
    if "=" in argu:
        try:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if thearg.lower() == 'repeat':
                repeat_times = int(theval)
        except:
            print("Didn't understand - " + argu)

def get_system_data( prefix ):
    system_data = {}
    system_data[prefix + "_time"] = datetime.datetime.now()
    system_data[prefix + '_swap_in']    = psutil.swap_memory()[4]
    system_data[prefix + '_swap_out']   = psutil.swap_memory()[5]
    system_data[prefix + '_disk_read_bytes']      = psutil.disk_io_counters(perdisk=False, nowrap=True)[2]
    system_data[prefix + '_disk_write_bytes']     = psutil.disk_io_counters(perdisk=False, nowrap=True)[3]
    system_data[prefix + '_disk_read_time']       = psutil.disk_io_counters(perdisk=False, nowrap=True)[4]
    system_data[prefix + '_disk_write_time']      = psutil.disk_io_counters(perdisk=False, nowrap=True)[5]
    system_data[prefix + '_disk_busy_time']       = psutil.disk_io_counters(perdisk=False, nowrap=True)[8]
    #print(system_data)
    return system_data

def basic_tests():
    print(" -- Running Basic Tests")
    basic_test_data = {}
    count_num = 100000000
    #
    print("      -- Addition upto to " + str(count_num))
    counter = 0
    keep_counting = True
    start_time = datetime.datetime.now()
    while keep_counting == True:
        counter = counter + 1
        if counter == count_num:
            keep_counting = False
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    basic_test_data['basic_counting'] = run_time.total_seconds()
    #
    print("      -- Subtraction from " + str(count_num))
    counter = count_num
    keep_counting = True
    start_time = datetime.datetime.now()
    while keep_counting == True:
        counter = counter - 1
        if counter == 0:
            keep_counting = False
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    basic_test_data['basic_subtraction'] = run_time.total_seconds()
    #
    print("      -- Doubling " + str(int(count_num/200)) + " times")
    counter = 1
    start_time = datetime.datetime.now()
    for x in range(0, int(count_num/200)):
        counter = counter * 2
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    basic_test_data['basic_doubling'] = run_time.total_seconds()
    #
    print("      -- Halving " + str(int(count_num)) + " times")
    counter = count_num + 1
    start_time = datetime.datetime.now()
    for x in range(0, int(count_num)):
        counter = counter / 2
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    basic_test_data['basic_halving'] = run_time.total_seconds()
    #
    return basic_test_data

def test_make_grid(grid_size=25):
    start_time = datetime.datetime.now()
    #
    base_black = Image.new('RGBA', (100,100), color=(35,0,0))
    base_white = Image.new('RGBA', (100,100), color=(175,175,255))
    growing_image = Image.new('RGBA', (100,0), color=(200,10,10))
    colour = 'white'
    colour_fade = 25
    first_pass = True
    for count_rows in range(0, grid_size):
        for count in range(1, grid_size+1):
            #
            colour_fade = colour_fade + 10
            if colour_fade > 250:
                colour_fade = 0
                #
            x,y = growing_image.size
            if first_pass:
                y = y + 100
            new_base = Image.new('RGBA', (x,y), color=(100,200,50))
            new_base.paste(growing_image)

            if colour == "black":
                #print(" - Adding black square")
                new_base.paste(base_black, (x-100, (count * 100)-100))
                colour = "white"
            else:
                #print(" - Adding white square")
                new_base.paste(base_white, (x-100, (count * 100)-100))
                colour = "black"
            #
            #new_image = ImageDraw.Draw(new_base)
            #new_image.line((0, 0) + (x,(count * 100)), fill=(colour_fade,50,50,255))
            #
            growing_image = new_base
            #growing_image = Image.open(file_name)
        # move to next row
        if not count_rows == grid_size-1:
            x,y = growing_image.size
            x = x + 100
            first_pass = False
            new_base = Image.new('RGBA', (x,y), color=(100,colour_fade,50))
            new_base.paste(growing_image)
            growing_image = new_base
    #im.save(sys.stdout, "PNG")
    file_name = temp_location + "test_board.png"
    new_base.save(file_name, "PNG")
    #
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    return run_time.total_seconds()

def test_make_set(frames=500):
    start_time = datetime.datetime.now()
    #
    size = frames
    base_image = Image.new('RGBA', (size,size), color=(20,150,40))
    colour_fade  = 0
    colour_fade2 = 0
    colour_fade3 = 0
    for frame_num in range(0, frames):
        colour_fade = colour_fade + 1
        if colour_fade > 250:
            colour_fade = 0
            colour_fade3 = colour_fade3 + 50
        colour_fade2 = colour_fade2 + 3
        if colour_fade2 > 250:
            colour_fade2 = 0
        new_image = ImageDraw.Draw(base_image)
        new_image.line((0, frame_num) + (size,frame_num), fill=(colour_fade,colour_fade2,colour_fade3,255))
        new_image.line((frame_num, 0) + (frame_num,size), fill=(colour_fade,colour_fade2,colour_fade3,255))
        #

        file_name = frame_folder_location + "test_frame_" + str(frame_num) + ".png"
        base_image.save(file_name, "PNG")
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    return run_time.total_seconds(), frame_folder_location

def create_test_render(frame_folder_location, file_type="mp4"):
    print(" -- Running Test Timelapse render")
    start_time = datetime.datetime.now()
    # list files
    filelist = []
    for filefound in os.listdir(frame_folder_location):
        if filefound.endswith("png"):
            filelist.append(frame_folder_location + filefound)
    filelist = sorted(filelist, key=lambda x: int(x.split("test_frame_")[1].replace(".png","")))
    backwards_filelist = list(filelist)
    backwards_filelist.reverse()
    filelist = filelist + backwards_filelist
    # write list to text file for mpv to read
    listfile = frame_folder_location + "frame_list.txt"
    with open (listfile, "w") as f:
        for x in filelist:
            f.write(x + "\n")
    # make the movie
    outfile = temp_location + "test_render." + file_type
    cmd = "mpv mf://@"+listfile+" --mf-fps=25"
    cmd += " -o "+outfile
    os.system(cmd)
    #
    end_time   = datetime.datetime.now()
    run_time = end_time - start_time
    return run_time.total_seconds()

def image_tests():
    print(" -- Running Image Tests")
    image_test_data = {}
    #
    print("      -- Testing PIL image creation")
    make_grid_25 = test_make_grid(25)
    image_test_data['image_create_chess_25'] = make_grid_25
    make_frame_set, test_set_location = test_make_set()
    image_test_data['image_create_frame_set'] = make_frame_set
    mp4_test_render = create_test_render(test_set_location, "mp4")
    image_test_data['video_render_mp4'] = mp4_test_render
    gif_test_render = create_test_render(test_set_location, "gif")
    image_test_data['video_render_gif'] = gif_test_render
    return image_test_data

def compare_sys_data(start, end):
    print(" -- Analysing data")
    sys_data_compared = {}
    #
    sys_data_compared['total_time']              = (end['end_time']             - start['start_time']).total_seconds()
    sys_data_compared['change_swap_in']          = end['end_swap_in']          - start['start_swap_in']
    sys_data_compared['change_swap_out']         = end['end_swap_out']         - start['start_swap_out']
    sys_data_compared['change_disk_read_bytes']  = end['end_disk_read_bytes']  - start['start_disk_read_bytes']
    sys_data_compared['change_disk_write_bytes'] = end['end_disk_write_bytes'] - start['start_disk_write_bytes']
    sys_data_compared['change_disk_read_time']   = end['end_disk_read_time']   - start['start_disk_read_time']
    sys_data_compared['change_disk_write_time']  = end['end_disk_write_time']  - start['start_disk_write_time']
    sys_data_compared['change_disk_busy_time']   = end['end_disk_busy_time']   - start['start_disk_busy_time']
    return sys_data_compared


def gather_data_make_log_text():
    # collect dictionaries of log data
    initial_sys_data = get_system_data('start')
    basic_test_data = basic_tests()
    image_test_data = image_tests()
    final_sys_data = get_system_data('end')
    compared_sys_data = compare_sys_data(initial_sys_data, final_sys_data)
    # create text line for log
    line = "timenow=" + str(datetime.datetime.now()) + ">"
    #for key, value in sorted(initial_sys_data.items()):
        # print(key, value)
    #    line += str(key) + "=" + str(value) + ">"
    #
    for key, value in sorted(basic_test_data.items()):
        # print(key, value)
        line += str(key) + "=" + str(value) + ">"
    for key, value in sorted(image_test_data.items()):
        # print(key, value)
        line += str(key) + "=" + str(value) + ">"
    for key, value in sorted(compared_sys_data.items()):
        print(key, (" " * (25-len(key))), value)
        line += str(key) + "=" + str(value) + ">"
    #
    line = line[:-1] + '\n'
    return line

if __name__ == '__main__':
    print("####################################################")
    print("############ Python Benchmark Tool  ################")

    for x in range(0, repeat_times):
        if not x == 0:
            print("  - - Waiting to start another run - -  ")
            time.sleep(delay)
        initial_sys_data = {}
        basic_test_data = {}
        image_test_data = {}
        final_sys_data = {}
        compared_sys_data ={}
        log_line = gather_data_make_log_text()

        # find the log and add a line to it
        try:
            with open(log_location, "a") as f:
                f.write(log_line)
                print(" - log written - ", log_line)
        except:
            print("-LOG ERROR-")
