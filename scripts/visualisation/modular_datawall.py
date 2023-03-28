#!/usr/bin/python3
# encoding: utf-8
import sys
import datetime
import time
import os
import io
import subprocess
homedir = os.getenv("HOME")
graph_modules_path = os.path.join(homedir, "Pigrow/scripts/gui/graph_modules/")
info_modules_path = os.path.join(homedir, "Pigrow/scripts/gui/info_modules/")
graph_presets_path = os.path.join(homedir, "Pigrow/scripts/gui/graph_presets/")
datawall_presets_path = os.path.join(homedir, "Pigrow/scripts/gui/datawall_presets/")
graph_base_save_path = os.path.join(homedir, "Pigrow/graphs/")
sys.path.append(graph_modules_path)
#sys.path.append(info_modules_path)


def read_graph_preset(preset_name):
    '''
    Reads a graph preset file and returns a dictionary of settings.
    '''
    print(" - Loading Preset " + preset_name)
    # read file
    graph_preset_path = os.path.join(graph_presets_path, preset_name)
    with open(graph_preset_path) as f:
        graph_presets = f.read()
    graph_presets = graph_presets.splitlines()
    # extract settings
    preset_settings = {}
    for setting in graph_presets:
        if "=" in setting:
            split_pos = setting.find("=")
            set_key = setting[:split_pos].strip()
            set_val = setting[split_pos + 1:].strip()
            preset_settings[set_key] = set_val
    return preset_settings

def load_log_backwards(preset_settings):
    # create path to log
    log_base_path = os.path.join(homedir, "Pigrow/logs/")
    log_to_load = os.path.join(log_base_path, preset_settings['log_path'])
    # settings
    if "end_time" in preset_settings:
        last_datetime = read_date(preset_settings["end_time"])
    if "start_time" in preset_settings:
        first_datetime = read_date(preset_settings["start_time"])
    else:
        first_datetime = False
    # define empty list
    loaded_dvks = []
    # read through the file line by line backwards
    with open(log_to_load, 'r') as file:
        file.seek(0, 2)  # Move the file pointer to the end of the file
        position = file.tell()  # Get the current position of the file pointer
        line = ''
        while position >= 0:
            file.seek(position)
            char = file.read(1)
            if char == '\n' or position == 0:
                if position != 0:
                    line = line[::-1]
                else:
                    line = char + line[::-1]
                line_date,line_value,line_key = parse_line(line.strip(), preset_settings)
                if first_datetime:
                    if line_date < first_datetime:
                        print("stopped at " + str(line_date))
                        break
                    else:
                        if not line_date == None:
                            loaded_dvks.append([line_date, line_value, line_key])
                else:
                    if not line_date == None:
                        loaded_dvks.append([line_date, line_value, line_key])
                line = ''
            else:
                line += char
            position -= 1
    print(" - Found " + str(len(loaded_dvks[0])) + " graphable values.")
    return loaded_dvks

def parse_line(line, preset_settings):
    if line.strip() == "":
        return None, None, None
    try:
        line_items = line.split(preset_settings["split_chr"])
        # date
        date_item  = line_items[int(preset_settings["date_pos"])]
        date_val   = date_item.split(preset_settings["date_split"])[int(preset_settings["date_split_pos"])]
        date = read_date(date_val)
        # key
        key_text = preset_settings["key_pos"]
        #value
        value_split    = preset_settings["value_split"]
        value_split_pos = int(preset_settings["value_split_pos"])
        if value_split_pos == 0:
            t_value_pos = 1
            t_key_pos = 0
        else:
            t_value_pos = 0
            t_key_pos = 1
        if 'rem_from_val' in preset_settings:
            rem_from_val = preset_settings['rem_from_val']
        else:
            rem_from_val = ""

        for item in line_items:
            if value_split in item:
                item_items = item.split(value_split)
                if item_items[t_key_pos] == key_text:
                    value = item_items[t_value_pos]
                    key = item_items[t_key_pos]
                    # remove from value
                    if not rem_from_val == "":
                        value = value.replace(rem_from_val, "")
                    # check it's a number by converting type to float
                    value = float(value)

        if "key_manual" in preset_settings:
            if not preset_settings["key_manual"] == "":
                key_text = preset_settings["key_manual"]
        return date, value, key_text
    except:
        raise
        return None, None, None

def read_date(date_str):
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d',
    ]

    for date_format in formats:
        try:
            return datetime.datetime.strptime(date_str, date_format)
        except ValueError:
            continue
    # Check if the input is a timestamp
    if len(date_str) == 10:
        try:
            timestamp = float(date_str)
            return dateteime.datetime.fromtimestamp(timestamp)
        except ValueError:
            print("Invalid date format.")
            return None


#####  below is code i didn't write today


def load_log(preset_settings):
    print(" - Reading log " + preset_settings['log_path'])
    # Load data from the log
    log_base_path = os.path.join(homedir, "Pigrow/logs/")
    log_to_load = os.path.join(log_base_path, preset_settings['log_path'])
    with open(log_to_load) as f:
        log_to_parse = f.read()
    log_to_parse = log_to_parse.splitlines()
    if len(log_to_parse) == 0:
        print(" --- Log file is empty")
    return log_to_parse

def parse_log(log_to_parse, preset_settings):
    print(" - Extracting data from log " + preset_settings['log_path'])
    # date positions
    split_chr      = preset_settings["split_chr"]
    date_pos       = int(preset_settings["date_pos"])
    date_split     = preset_settings["date_split"]
    date_split_pos = int(preset_settings["date_split_pos"])
    # value and key positions
    value_split    = preset_settings["value_split"]
    value_split_pos = int(preset_settings["value_split_pos"])
    if value_split_pos == 0:
        t_value_pos = 1
        t_key_pos = 0
    else:
        t_value_pos = 0
        t_key_pos = 1
    key_text       = preset_settings["key_pos"]
    # optional settings
    #   removing string from the value
    if "value_rem" in preset_settings:
        rem_from_val = preset_settings["value_rem"]
    else:
        rem_from_val = ""
    #   time and date limiting
    if "limit_date" in preset_settings:
        limit_date = preset_settings["limit_date"] #day, week ,etc
    if "end_time" in preset_settings:
        last_datetime = preset_settings["end_time"]
        last_datetime = datetime.datetime.strptime(last_datetime, '%Y-%m-%d %H:%M:%S')
    if "start_time" in preset_settings:
        first_datetime = preset_settings["start_time"]
        first_datetime = datetime.datetime.strptime(first_datetime, '%Y-%m-%d %H:%M:%S')
    if "key_manual" in preset_settings:
        key_manual = preset_settings["key_manual"]
    else:
        key_manual = ""
    # check if we should limit to a certain date range
    limit_by_date = False # currently not written so setting to false

    # cycle through each line and fill the lists
    date_list = []
    value_list = []
    key_list = []
    for line in log_to_parse:
        date = ""
        value = ""
        key = ""
        if split_chr in line:
            line_items = line.split(split_chr)
            for item in line_items:
                # date - by positional argument only at the moment
                date = line_items[date_pos]
                if not date_split == "":
                    date = date.split(date_split)[date_split_pos]
                if "." in date:
                    date = date.split(".")[0]
                # Check date is valid and ignore if not
                try:
                    date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    if limit_by_date == True:
                        if date > last_datetime or date < first_datetime:
                            date = ""
                except:
                    #raise
                    print("! Date not valid -" + str(date))
                    date = ""
                #value
                if value_split in item:
                    item_items = item.split(value_split)
                    if item_items[t_key_pos] == key_text:
                        value = item_items[t_value_pos]
                        key = item_items[t_key_pos]
                        # remove from value
                        if not rem_from_val == "":
                            value = value.replace(rem_from_val, "")
                        # check it's a number and convert type to float
                        try:
                            value = float(value)
                        except:
                            print("! Value not a valid number; " + str(value))
                            value = ""
        # set key to manual
        if not key_manual == "":
            key = key_manual
        # add to lists
        if not date == "" and not value == "" and not key == False:
            date_list.append(date)
            value_list.append(value)
            key_list.append(key)
    print(" - Found " + str(len(date_list)) + " graphable values.")
    return [date_list, value_list, key_list]

def build_graph(graph_module, log_lists, save_path, graph_settings):
    print(" - Making log using " + graph_module)
    print(" ")
    # import graph_module
    if not "graph_" in graph_module:
        graph_module = "graph_" + graph_module
    exec("from " + graph_module + " import make_graph", globals())
    #
    ymax = ""
    ymin = ""
    size_h = 12
    size_v = 9
    toohot = ""
    dangerhot = ""
    toocold = ""
    dangercold = ""
    if "ymax" in graph_settings:
        ymax = graph_settings['ymax']
    if "ymin" in graph_settings:
        ymin = graph_settings['ymin']
    if "size_h" in graph_settings:
        size_h = int(graph_settings['size_h'])
    if "size_v" in graph_settings:
        size_v = int(graph_settings['size_v'])
    if "toohot" in graph_settings:
        toohot = graph_settings['toohot']
    if "dangerhot" in graph_settings:
        dangerhot = graph_settings['dangerhot']
    if "toocold" in graph_settings:
        toocold = graph_settings['toocold']
    if "dangercold" in graph_settings:
        dangercold = graph_settings['dangercold']
    make_graph(log_lists, save_path, ymax, ymin, size_h, size_v, dangerhot, toohot, toocold, dangercold, graph_settings)

def read_datawall_preset(datawall_preset_name):
    print(" - Reading datawall preset - " + datawall_preset_name)
    # Load data from the log
    datawall_base_path = os.path.join(homedir, "Pigrow/scripts/gui/datawall_presets/")
    datawall_path = os.path.join(datawall_base_path, datawall_preset_name)
    with open(datawall_path) as f:
        datawall_file = f.read()
    datawall_list = datawall_file.splitlines()
    return datawall_list

def process_datawall(datawall_list):
    #
    #preset_settings = {}
    preset_name = ""
    graph_module = ''
    graphable_data = [] # list of lists of lists of date,val,key
    made_graph_list  = []
    info_text_dict = {}

    #
    print(" - Creating datawall ")
    graph_count = 0
    for line in datawall_list:
        if line == "load_log":
            log_to_parse = load_log(preset_settings)
            log = parse_log(log_to_parse, preset_settings)
            graphable_data.append(log)
        if line == "load_log_back":
            log = load_log_backwards(preset_settings)
            graphable_data.append(log)

        if line == "make_graph":
            save_path = os.path.join(graph_base_save_path, "datawall_graph_" + str(len(made_graph_list)) + ".png")
            build_graph(graph_module, graphable_data, save_path, graph_options)
            made_graph_list.append(save_path)

        # options settings
        if "=" in line:
            equals_pos = line.find("=")
            key = line[:equals_pos].strip()
            value = line[equals_pos + 1:].strip()
            # Starting a new graph and clearing everything
            if key == "graph_name":
                print( " Datawall - Starting graph - " + value)
                current_graph = value
                log_to_parse = ""
                preset_settings = {}
                graph_module = ""
                graphable_data = []
            # changing settings
            elif "_" in key:
                equals_pos = key.find("_")
                key_type = key[:equals_pos].strip()
                key_job  = key[equals_pos + 1:].strip()
                # handling loading of logs
                if key_type == "log":
                    if key_job == "preset":
                        preset_name = value
                        preset_settings = read_graph_preset(preset_name)
                        # preset_name = value.split(",")
                        # for x in preset_name:
                        #     dw_log_presets.append(x)
                    if key_job == "setting":
                        logset_key, logset_value = value.split(":")
                        preset_settings[logset_key] = logset_value
                        print(" - Setting log " + logset_key + " to " + logset_value)

                # handling making of graphs
                if key_type == "graph":
                    if key_job == "module":
                        graph_module = value
                        # read default options from graph module
                        if not "graph_" in graph_module:
                            graph_module = "graph_" + graph_module
                        exec("from " + graph_module + " import read_graph_options", globals())
                        graph_options = read_graph_options()

                    if key_job == "setting":
                        graph_key, graph_val = value.split(":")
                        graph_options[graph_key] = graph_val
                        print(" - Graph Settings " + value)
                        #print("     - " + graph_key + " = " + graph_val)
                # handling info modules
                if key_type == "info":
                    if key_job == "read":
                        print(" - Info module reading " + value)
                        info_tu = read_info_module(value)
                        info_text_dict[info_tu[0]] = info_tu[1].strip()
                # picture loading preset
                if key_type == "picture":
                    if key_job == "path":
                        info_tu = read_info_module(value, "picture_")
                        info_text_dict[info_tu[0]] = info_tu[1].strip()

    return made_graph_list, info_text_dict, graphable_data

def read_info_module(info_module_name, prefix="info_"):
    # get args
    args = ""
    if " " in info_module_name:
        e_pos = info_module_name.find(" ")
        args = info_module_name[e_pos:]
        info_module_name = info_module_name[:e_pos]

    # check name is in module format
    if not prefix in info_module_name:
        info_module_name = prefix + info_module_name
    if not ".py" in info_module_name:
        info_module_name += ".py"

    cmd = info_modules_path + info_module_name + " " + args
    info_text = subprocess.check_output(cmd, shell=True).decode(sys.stdout.encoding).strip()

    # import and run module
    #exec("from " + info_module_name + " import show_info", globals())
    #info_text = show_info()


    info_module_name = info_module_name.replace("info_", "").replace(".py", "").strip()
    return [info_module_name, info_text]

if __name__ == '__main__':
    # Load settings from command line arguments
    datawall_module_name = ""
    datawall_preset_name = ""
    datawall_save_path = os.path.join(homedir, "Pigrow/graphs/datawall.png")
    for argu in sys.argv[1:]:
        if "=" in argu:
            thearg = str(argu).split('=')[0]
            theval = str(argu).split('=')[1]
            if  thearg == 'preset':
                datawall_preset_name = theval
            elif thearg == 'module':
                datawall_module_name = theval
            elif thearg == 'out':
                datawall_save_path = theval
        elif argu == 'h' or argu == '-h' or argu == 'help' or argu == '--help':
            print("")
            print("  preset=")
            print("      the name of the preset e.g. datawall_Selflog.txt")
            print("      found in ~/Pigrow/scripts/gui/datawall_presets/")
            print("  module=")
            print("      the name of the datwall modul e.g. selflog or datawall_selflog.py")
            print("      found in ~/Pigrow/scripts/gui/graph_modules/")
            print(" out=")
            print("      the full path to the desired location of the created datawall")
            print("      default is ~/Pigrow/graphs/datawall.png")
            print("")
            print(" example:")
            print("     modular_datawall preset=datawall_selflog.txt module=selflog")
            sys.exit()
        elif argu == '-flags':
            print("preset=")
            print("module=")
            print("out=~/Pigrow/graphs/datawall.png")
            sys.exit()

    # Preset graph list
    if datawall_preset_name == "":
        print("  !!! select a datawall preset using preset=")
        datawall_preset_list = os.listdir(datawall_presets_path)
        for item  in datawall_preset_list:
            if "datawall_" in item:
                print ("    - " + item.replace("datawall_", "").replace(".txt", ""))
    elif not "datawall_" in datawall_preset_name:
        datawall_preset_name = "datawall_" + datawall_preset_name

    if not datawall_preset_name == "" and not ".txt" in datawall_preset_name:
        datawall_preset_name = datawall_preset_name + ".txt"

    # Module
    if datawall_module_name == "":
        print("  !!! select a datawall module using module= ")
        module_list = os.listdir(graph_modules_path)
        for item  in module_list:
            if "datawall_" in item:
                print ("    - " + item.replace("datawall_", "").replace(".py", ""))
    elif not "datawall_" in datawall_module_name:
        datawall_module_name = "datawall_" + datawall_module_name
    datawall_module_name = datawall_module_name.replace(".py", "")

    # check save path folder exists
    without_filename = os.path.split(datawall_save_path)[0]
    if not os.path.isdir(without_filename):
        os.makedirs(without_filename)

    # Run everything
    print ("-----------------------------------")
    print ("-----Modular Datawall Maker--------")
    print ("-----------------------------------")
    # test graph making
    datawall_list = read_datawall_preset(datawall_preset_name)
    list_of_graphs_made, info_text_dict, graphable_data = process_datawall(datawall_list)
    print(" ")
    print(" - Created " + str(len(list_of_graphs_made)) + " graphs")
    print(" - read " + str(len(info_text_dict)) + " info modules")
    print(" - passing " + str(len(graphable_data)) + " loaded logs")
    # create datawall
    if not datawall_module_name == "":
        exec("from " + datawall_module_name + " import make_datawall", globals())
        make_datawall(list_of_graphs_made, datawall_save_path, graphable_data, infolist=info_text_dict)
