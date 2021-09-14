#!/usr/bin/python3
import os

def show_info():

    #
    # New improved low power warning
    #
    out =  os.popen("vcgencmd get_throttled").read()
    out = out.strip().strip("throttled=")
    display_message = ""
    if out == "0x0":
        display_message = " No Temp or Volt Alerts"
    #
    out_int = int(out, 16)
    #display_message += "\nint-" + str(out_int)
    bit_nums = [[0, "Under_Voltage detected"],
                [1, "Arm frequency capped"],
                [2, "Currently throttled"],
                [3, "Soft temperature limit active"],
                [16, "Under-voltage has occurred"],
                [17, "Arm frequency capping has occurred"],
                [18, "Throttling has occurred"],
                [19, "Soft temperature limit has occurred"]]
    for x in range(0, len(bit_nums)):
        bit_num  = bit_nums[x][0]
        bit_text = bit_nums[x][1]
        if (out_int & ( 1 << bit_num )):
            display_message += "\n  - " + bit_text
            #display_message += "\n(bit-" + str(bit_num) + ") " + bit_text

    return display_message


if __name__ == '__main__':
    print(show_info())
