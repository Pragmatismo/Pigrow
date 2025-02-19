#!/usr/bin/python3
import os

homedir = os.getenv("HOME")

def show_info():
    # define relay pin status checker
    def check_gpio_status(gpio_pin, on_power_state):
        gpio_path = f"/sys/class/gpio/gpio{gpio_pin}"
        
        # Ensure the GPIO pin is exported
        if not os.path.isdir(gpio_path):
            cmd = f"echo {gpio_pin} > /sys/class/gpio/export"
            os.popen(cmd).read()
        
        # Check if the GPIO pin is accessible
        if not os.path.isdir(gpio_path):
            return f"GPIO {gpio_pin} could not be exported or accessed."
        
        # Check the direction of the GPIO pin
        direction_path = f"{gpio_path}/direction"
        if os.path.exists(direction_path):
            with open(direction_path, "r") as f:
                direction = f.read().strip()
            if direction == "out":
                return f"GPIO {gpio_pin} is set as OUTPUT and cannot be read."
        
        # Read the GPIO pin value
        value_path = f"{gpio_path}/value"
        if os.path.exists(value_path):
            with open(value_path, "r") as f:
                gpio_status = f.read().strip()
        else:
            return f"GPIO {gpio_pin} value file does not exist."
        
        # Determine device status based on GPIO value and power state
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
                device_status = "settings error"
        else:
            device_status = f"read error -{gpio_status}-"
        
        return device_status

    # Load GPIO settings from config file
    gpio_dict = {}
    gpio_on_dict = {}
    pigrow_config_file = os.path.join(homedir, "Pigrow/config/pigrow_config.txt")
    
    if not os.path.exists(pigrow_config_file):
        return f"Config file not found: {pigrow_config_file}"
    
    with open(pigrow_config_file, "r") as f:
        pigrow_settings = f.read().splitlines()
    
    for item in pigrow_settings:
        equals_pos = item.find("=")
        if equals_pos == -1:
            continue  # Skip malformed lines
        setting_value = item[equals_pos + 1:]
        setting_name = item[:equals_pos]
        
        if "gpio_" in setting_name:
            device_name = setting_name.split("_")[1]
            if "_on" not in setting_name:
                gpio_dict[device_name] = setting_value
            else:
                gpio_on_dict[device_name] = setting_value
    
    # Generate status report
    text_out = ""
    for key in sorted(gpio_on_dict):
        if key in gpio_dict:
            status = check_gpio_status(gpio_dict[key], gpio_on_dict[key])
            text_out += f"{key} is {status}\n"
    
    return text_out.strip()

if __name__ == '__main__':
    print(show_info())
