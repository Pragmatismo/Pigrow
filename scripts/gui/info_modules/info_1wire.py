#!/usr/bin/python3
import os

def show_info():

    def check_if_active():
        '''
        Checks to see if the w1 overlay is active and what's using it,
        sub info_modules are called to locate temp sensors, etc according
        to their module name - i.e. w1_therm becomes info_w1_therm.py
        '''
        # check if 1wire is running
        out =  os.popen('lsmod').read()
        for line in out.splitlines():
            # read last element of 'wire' line and split into modules using it
            if line[0:4] == "wire":
                w1_modules = line.split(" ")[-1].split(",")

        # cycle through modules checking for and running sub info modules
        info_text = ""
        for item in w1_modules:
            info_text += item + " : Enabled\n"
            info_path = "./info_" + item + ".py"
            if os.path.isfile(info_path):
                out =  os.popen(info_path).read()
                info_text += "    " + out.replace("\n", "    \n")
        # add note if not running
        if info_text == "":
            info_text = "1wire overlay not running.\n"
        return info_text

    def find_dtoverlay_w1_pins():
        '''
        reads /boot/config.txt looking for dtoverlay pins
        '''
        # functions
        def pin_in_line(line):
            if "gpiopin=" in line:
                gpio_pin = line.split("gpiopin=")[1].strip()
                if not gpio_pin.isdigit():
                    gpio_pin = 'error'
                    #err_msg += "!!! Error reading pi's /boot/config.txt could't determine gpio number -" + line + "\n"
            else:
                gpio_pin = "default (4)"
            return (gpio_pin)

        # Read boot config file
        out =  os.popen("cat /boot/config.txt").read()
        config_txt_lines = out.splitlines()
        # cycle through each line of config.txt
        gpio_pin_list = []
        for line in config_txt_lines:
            if not line.strip()[0:1] == "#":
                if "dtoverlay=w1-gpio" in line:
                    gpio_pin_list.append(pin_in_line(line))
                if "dtparam=gpiopin=" in line:
                    gpio_pin = command.split("dtparam=gpiopin=")[1]
                    if not gpio_pin.isdigit():
                        gpio_pin = "error"
                    gpio_pin_list[-1] = gpio_pin
        return gpio_pin_list


    def check_config():
        '''
        Checks the pi's /boot/config.txt file for the 1wire overlay
        '''
        gpio_pin_list = find_dtoverlay_w1_pins()
        if len(gpio_pin_list) > 0:
            msg = "1wire overlay enabled on pin"
            for pin in gpio_pin_list:
                msg += " " + str(pin) + ","
            msg = msg[:-2]
            if len(gpio_pin_list) > 1: msg = msg.replace("pin", "pins")
        else:
            msg = "1wire not enabled in /boot/config.txt"
        return msg

    return check_if_active() + check_config()


if __name__ == '__main__':
    print(show_info())
