#!/usr/bin/python3
import os
homedir = os.getenv("HOME")

def show_info():
    # define relay pin status checker
    def check_gpio_status(gpio_pin, on_power_state):
        if not os.path.isdir("/sys/class/gpio/gpio" + str(gpio_pin)):
            cmd = "echo " + str(gpio_pin) + " > /sys/class/gpio/export"
            out =  os.popen(cmd).read()
        cmd = "cat /sys/class/gpio/gpio" + str(gpio_pin) + "/value"
        out =  os.popen(cmd).read()
        gpio_status = out.strip()
        gpio_err = out.strip()
        if gpio_status == "1":
            if on_power_state == 'low':
                device_status = "OFF"
            elif on_power_state == 'high':
                device_status = 'ON'
            else:
                device_status = "settings error"
        elif gpio_status == '0':
            if on_power_state == 'low':
                device_status = "ON"
            elif on_power_state == 'high':
                device_status = 'OFF'
            else:
                device_status = "setting error"
        else:
            device_status = "read error -" + gpio_status + "-"
        return device_status
    #
    gpio_dict = {}
    gpio_on_dict = {}
    pigrow_config_file = homedir + "/Pigrow/config/pigrow_config.txt"
    cmd = "cat " + pigrow_config_file
    out =  os.popen(cmd).read()
    #out, error = MainApp.localfiles_ctrl_pannel.run_on_pi("cat " + pigrow_settings_path)
    pigrow_settings = out.splitlines()


    for item in pigrow_settings.sorted():
            equals_pos = item.find("=")
            setting_value  = item[equals_pos + 1:]
            setting_name = item[:equals_pos]
            #print(setting_name, setting_value)

            if "gpio_" in setting_name:
                device_name = setting_name.split("_")[1]
                if not "_on" in setting_name:
                    gpio_dict[device_name] = setting_value
                else:
                    gpio_on_dict[device_name] = setting_value

    text_out = ""
    for key in gpio_on_dict:
        if key in gpio_dict:
            status = check_gpio_status(gpio_dict[key], gpio_on_dict[key])
            text_out += key + " is " + status + "\n" #+ " using pin " + gpio_dict[key] + " wired " + gpio_on_dict[key] + "\n"



    return text_out.strip()

if __name__ == '__main__':
    print(show_info())
