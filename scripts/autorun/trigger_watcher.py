#!/usr/bin/python3
import time
import datetime
import os
import sys
import subprocess
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

trigger_events_path     = homedir + "/Pigrow/config/trigger_events.txt"
trigger_conditions_path = homedir + "/Pigrow/logs/trigger_conditions.txt"

class config_data:
    def __init__():
        config_data.trigger_conditions = []
        config_data.logs_to_check = []

    def load_trigger_events(trigger_file):
        print_limit(" - Loading trigger events", 1)
        if not os.path.isfile(trigger_file):
            print_limit(" - Trigger file not fonnd, nothing to monitor - exiting.",0 )
            sys.exit()
        with open(trigger_file) as f:
            lines = f.read().splitlines()
        trigger_conditions = []
        for line in lines:
            if "," in line:
                # locate commas, done this awkward way so the last one can include commas too
                first_comma = line.find(",")
                second_comma  = first_comma + 1 + line[first_comma+1:].find(",")
                third_comma   = second_comma + 1 + line[second_comma+1:].find(",")
                fourth_comma  = third_comma + 1 + line[third_comma+1:].find(",")
                fifth_comma   = fourth_comma + 1 + line[fourth_comma+1:].find(",")
                sixth_comma   = fifth_comma + 1 + line[fifth_comma+1:].find(",")
                seventh_comma = sixth_comma + 1 + line[sixth_comma+1:].find(",")
                eighth_comma = seventh_comma + 1 + line[seventh_comma+1:].find(",")
                # find values between commas
                log_name        = line[:first_comma].strip()
                value_label     = line[first_comma  +1 :second_comma].strip()
                trigger_type    = line[second_comma +1 :third_comma].strip()
                trigger_value   = line[third_comma  +1 :fourth_comma].strip()
                condition_name  = line[fourth_comma +1 :fifth_comma].strip()
                trig_direction  = line[fifth_comma  +1 :sixth_comma].strip()
                trig_cooldown   = line[sixth_comma  +1 :seventh_comma].strip()
                cmd            = line[seventh_comma+1:].strip()
                trigger_conditions.append([log_name, value_label, trigger_type, trigger_value, condition_name, trig_direction, trig_cooldown, cmd])
        config_data.trigger_conditions = trigger_conditions

        # make a list of logs we've got confitions for
        logs_to_check = []
        for item in config_data.trigger_conditions:
            if not item[0] in logs_to_check:
                logs_to_check.append(item[0])
        config_data.logs_to_check = logs_to_check
        print_limit(" - Checking logs;" + str(logs_to_check), 2)

def print_limit(text, level=1):
    print_level = 2
    if level <= print_level:
        print(text)

def check_condition(condition_name, trig_direction):
    '''
    This reads the trigger_conditions file to determine if it should activate the trigger,
    it is stored as a seperate file rather than a list stored in memory so that it can be edited remotely
    for example it mighty be useful to turn something off until user intervention turns it on
    or for something to be controlled by a switch, button or remote interface -
    only creaing graphs while a screen is on for example ot having a control to give a short boost of heat.
    '''
    # read conditions file
    if not os.path.isfile(trigger_conditions_path):
        print_limit(" - Conditions file not fonnd, no conditions currently set",1 )
        return True
    else:
        with open(trigger_conditions_path, 'r') as f:
            trigger_conditions = f.readlines()
        # find trigger
        trigger_state = "none"
        for line in trigger_conditions:
            line_split = line.split(",")
            if len(line_split) == 3:
                if line_split[0] == condition_name:
                    trigger_state = line_split[1].strip()
                    trigger_cooldown = line_split[2].strip()
        # check if condition is met
        if not trigger_state == "none":
            # convert timestamp to datetime
            if not trigger_cooldown == "none" and not trigger_cooldown == "":
                try:
                    trigger_datetime = datetime.datetime.fromtimestamp(float(trigger_cooldown))
                    if trigger_datetime > datetime.datetime.now():
                        print_limit("Trigger still cooling down, wont fire again for " + str(trigger_datetime - datetime.datetime.now()), 1)
                        return False
                except:
                    print_limit(" !! Failed to convert cooldown to date, it should be a timestamp")        
            # check if trigger state is already set
            if trigger_state == trig_direction:
                print_limit("  - Not triggering because condition is already set...", 2)
                return False
            else:
                print_limit(" - Trigger state doesn't match trigger direction, triggering!", 2)
                return True
        else:
            return True


def check_value(log_path):
    split_chr = ">"
    second_split_chr = "="
    value_side = 1
    date_text = "time"

    # Check the conditions for this log
    # read log
    log_name = os.path.split(log_path)[1]
    print_limit(" - log changed - " + log_path, 1)
    if log_name in config_data.logs_to_check:
        with open(log_path, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode()

        # create list of trigger conditions
        # this should be outside the loop
        conditions = []
        for item in config_data.trigger_conditions:
            #print_limit(item)
            if item[0] == log_name:
                conditions.append([item[1], item[2], item[3], item[4], item[5], item[6], item[7]])


        if split_chr in last_line:
            line_items = last_line.split(split_chr)
            line_date = None
            line_value = None
            # find the datetime the last log was written
                  # current this is not used for anything....
            for item in line_items:
                if second_split_chr in item:
                    if date_text in item:
                        line_date = item.split(second_split_chr)[value_side]
            # check each trigger assocaiated wit this log
            for condition in conditions:
                val_label      = condition[0]
                trigger        = condition[1]
                value          = condition[2]
                condition_name = condition[3]
                trig_direction = condition[4]
                trig_cooldown  = condition[5]
                cmd            = condition[6]
                # check trigger state
                if check_condition(condition_name, trig_direction) == True:
                    # find the selected value in the log
                    for item in line_items:
                        if second_split_chr in item:
                            if val_label in item:
                                line_value = item.split(second_split_chr)[value_side].strip()

                    # perform logic to see if value causes a trigger condition
                    if not line_date == None or not line_value == None:
                        # Above
                        if trigger == "above":
                            if float(value) < float(line_value):
                                print_limit(" Vakue " + line_value + " larger than trigger value of " + str(value) + " running " + cmd, 1)
                                os.system(cmd + " &")
                                pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)
                            else:
                                print_limit(" - trigger value conditions not met, no action", 2)
                        # Below
                        elif trigger == "below":
                            if float(value) > float(line_value):
                                print_limit(" Value " + line_value + " smaller than trigger value of " + str(value) + " running " + cmd, 1)
                                os.system(cmd + " &")
                                pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)
                            else:
                                print_limit(" - trigger value conditions not met, no action", 2)
                        # Window
                        #    Trigger inside a window
                        elif trigger == "window":
                            if ":" in value:
                                val_min, val_max = value.split(":")
                                if float(line_value) > float(val_min) and float(line_value) < float(val_max):
                                    print_limit("Value greater than " + val_min + " and less than " + val_max + ", running " + cmd, 1)
                                    os.system(cmd + " &")
                                    pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)
                                else:
                                    print_limit(" - trigger value conditions not met, no action", 2)
                        # Frame
                        #    trigger outside a window
                        elif trigger == "frame":
                            if ":" in value:
                                val_min, val_max = value.split(":")
                                if float(line_value) < float(val_min) and float(line_value) > float(val_max):
                                    print_limit("Value less than " + val_min + " and greater than " + val_max + ", running " + cmd, 1)
                                    os.system(cmd + " &")
                                    pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)
                                else:
                                    print_limit(" - trigger value conditions not met, no action", 2)
                        # Any
                        #    trigger on any value being recorded
                        elif trigger == "all":
                            os.system(cmd + " &")
                            print_limit("Trigger set to all, running " + cmd, 1)
                            pigrow_defs.set_condition(condition_name, trig_direction, trig_cooldown)

def on_created(event):
    check_value(event.src_path)

def on_deleted(event):
    pass

def on_modified(event):
    check_value(event.src_path)

def on_moved(event):
    pass

def trig_change(event):
    if "trigger_events.txt" in event.src_path:
        print_limit(" - - - Trigger events file changed - - -", 2)
        config_data.load_trigger_events(trigger_events_path)

def observe_trig_file():
    print_limit(" - Enabling Trigger Events Config File Observation -", 2)
    path = homedir + "/Pigrow/config/"
    trig_events_handler = PatternMatchingEventHandler("*.txt", "", True, False)
    trig_events_handler.on_created = trig_change
    trig_events_handler.on_modified = trig_change
    trig_events_ob = Observer()
    trig_events_ob.schedule(trig_events_handler, path, recursive=True)
    trig_events_ob.start()


if __name__ == "__main__":
    # set path from locs file
    config_data.load_trigger_events(trigger_events_path)
    print_limit(" - Loaded trigger events;", 1)
    print_limit(config_data.trigger_conditions, 2)
    # Set up and run log file watcher
    path = homedir + "/Pigrow/logs/"
    patterns = "*.txt"
    ignore_patterns = ""
    trig_e_handler = PatternMatchingEventHandler(patterns, ignore_patterns, True, False)
    trig_e_handler.on_created = on_created #,
    trig_e_handler.on_deleted = on_deleted
    trig_e_handler.on_modified = on_modified
    trig_e_handler.on_moved = on_moved
    trig_observer = Observer()
    trig_observer.schedule(trig_e_handler, path, recursive=True)
    trig_observer.start()
    # set up and run trigger config file watcher
    observe_trig_file()
    # loop forever waiting for file changes to happen.
    while True:
        time.sleep(1)
