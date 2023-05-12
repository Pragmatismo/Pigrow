#!/usr/bin/python3
import os

def show_info():
    ''' This reads the current temperature of the raspberry pi's CPU and outputs it to text'''

    try:
        # This command reads the CPU temperature
        cmd = "/opt/vc/bin/vcgencmd measure_temp"
        out =  os.popen(cmd).read()
        # Extract just the temperature number, remove "temp=" and "'C\n"
        out = out.replace("temp=","").replace("'C\n", "")
    except:
        # If the above command fails, read the temperature from /sys/class/thermal/thermal_zone0/temp
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            out = f.read()
        # Convert from millidegrees to degrees
        out = str(float(out) / 1000)

    cpu_temp = "CPU temperature: " + out + "°C"

    return cpu_temp

if __name__ == '__main__':
    print(show_info())
