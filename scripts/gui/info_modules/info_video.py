#!/usr/bin/python3
import os

def show_info():
    # display power
    out =  os.popen("vcgencmd display_power").read()
    out = out.strip().strip("display_power=")
    if out == "0":
        power_message = "Video power off"
    else:
        out =  os.popen("tvservice -s").read()
        power_message = "Video power on\n" + tv_out.strip()

    # Screen res and colour pallet
    out =  os.popen("vcgencmd get_lcd_info").read()
    lcd_info_message = out.strip().strip("")
    lcd_info_message = "Resolution; " + lcd_info_message

    # items being displayed
    out =  os.popen("vcgencmd dispmanx_list").read().strip()
    if not out == "":
        dispmanx_items = "Dispmanx Items;\n" +  out.strip("")
    else:
        dispmanx_items = ""

    info_text = power_message + '\n' + lcd_info_message + '\n' + dispmanx_items

    return info_text


if __name__ == '__main__':
    print(show_info())
