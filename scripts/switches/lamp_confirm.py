#!/usr/bin/env python3
#Flags output enabled
import re
import os
import subprocess
import sys
import time
homedir = os.path.expanduser("~")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs
err_path = homedir + "/Pigrow/logs/err_log.txt"

def list_lampconf(as_list=True):
    config_path = homedir + "/Pigrow/config/pigrow_config.txt"
    set_dic = pigrow_defs.load_settings(config_path, err_log=err_path)
    lc_list = []
    for item in set_dic:
        if "lampcon_" in item:
            name = item.split("_")[1]
            if name not in lc_list:
                lc_list.append(name)

    if len(lc_list) == 0:
        print("No lamp confirm settings found in pigrow_setting.txt")
    else:
        if as_list == False:
            print(" Found", len(lc_list), "available lamp confirm settings;")
            for item in lc_list:
                print(item)
        else:
            msg = ""
            for item in lc_list:
                msg += item + ","
            return msg[:-1]

def parse_args():
    """Parse and validate command-line arguments."""
    for argu in sys.argv[1:]:
        if argu == '-h' or argu == '--help':
            print(" Lamp Switch with Confirmation Test")
            print(" ")
            print("")
            print(" name=<lampconf name>")
            print("     choose which lampconf settings to use")
            print(" direction=<on,off>")
            print("     direction to set switch, on or off")
            print("")
            sys.exit(0)
        elif argu == "-flags":
            print("name=[" + list_lampconf() + "]")
            print("direction=[on, off]")
            sys.exit(0)
        elif argu == "-defaults":
            print("name=")
            print("direction=")
            sys.exit(0)
        elif "=" in argu:
            try:
                thearg = str(argu).split('=')[0]
                theval = str(argu).split('=')[1]
                if thearg == 'name':
                    if "" in theval:
                        name = theval
                elif thearg == 'direction':
                    direction = theval
            except:
                print("Didn't undertand " + str(argu))

    return name, direction

def load_config(name):
    """Load and filter pigrow_config.txt for named lampcon settings"""

    # Config file location
    config_path = os.path.join(homedir, "Pigrow/config/pigrow_config.txt")
    full_settings = pigrow_defs.load_settings(config_path, err_log=err_path)

    # Filter keys for this lamp_confirm script
    # Expecting settings named like "lampcon_<switch_name>_<key>"
    prefix = f"lampcon_{name}_"
    lampcon_dict = {}
    for key, value in full_settings.items():
        if key.startswith(prefix):
            short_key = key[len(prefix):]
            lampcon_dict[short_key] = value

    if not lampcon_dict:
        print(f"No settings found for '{name}' in config")
        sys.exit(1)

    try: lampcon_dict["retry_count"] = int(lampcon_dict["retry_count"])
    except: lampcon_dict["retry_count"] = 3
    try: lampcon_dict["delay"] = int(lampcon_dict["delay"])
    except: lampcon_dict["delay"] = 3

    return lampcon_dict

def trigger_relay(command):
    """Execute a relay-trigger command; return True on zero exit code."""
    try:
        result = subprocess.run(command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Relay command '{command}' succeeded")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Relay command '{command}' failed: {e.stderr}")
        return False

def test_pic(settings):
    """
    Capture & analyze an image.
    Return True if image size indicates correct light level after change.
    """
    cam_cmd = settings["cam_cmd"]
    try:    size_threshold = int(settings["size"])
    except: size_threshold = 250000

    # Extract the filename argument (supports quoted paths)
    m = re.search(r'filename=(?P<fname>"[^"]*"|\S+)', cam_cmd)
    if not m:
        print("Could not extract filename from cam_cmd: %s", cam_cmd)
        raise ValueError("filename argument not found in cam_cmd")
    image_path = m.group('fname').strip('"')

    # Delete existing test image
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
            print("Deleted existing image: %s", image_path)
        except Exception as e:
            print("Could not delete existing image '%s': %s", image_path, e)

    # Run capture, retry up to 3 times
    for attempt in range(1, 4):
        ret = subprocess.run(cam_cmd, shell=True)
        if ret.returncode == 0 and os.path.exists(image_path) and os.path.getsize(image_path) > 0:
            break
        print("Image capture failed (attempt %d)", attempt)
        if attempt < 3:
            time.sleep(3)
    else: # All retries failed
        print("Failed to capture image after 3 attempts")
        return False

    # Check file size against threshold
    file_size = os.path.getsize(image_path)
    print(f"Captured image size: {file_size} bytes")

    # check if on filesize is greater than or off filesize is less than threashold
    if settings["direction"] == "on":
        return file_size > int(size_threshold)
    else:
        return file_size < int(size_threshold)

def test_sensor(sensor_name, sensor_threshold):
    """
    Read a sensor and return True if its value exceeds the threshold.
    """
    # TODO: sensor_value = read_sensor(sensor_name)
    sensor_value = 0.0


def attempt_switch_with_confirmation(switch_cmd, throw_cmd, settings):
    """
    Try switching up to retry_count times, testing after each attempt.
    Returns (success: bool, attempts: int).
    """
    fail_count = 0

    for attempt in range(1, settings["retry_count"] + 1):
        trigger_relay(switch_cmd)
        print(f"Relay attempt {attempt}, waiting {settings['delay']} seconds before test...")
        time.sleep(settings["delay"])
        if settings["mode"] == "camera":
            passed = test_pic(settings)
        else:  # sensor
            print("Test using sensor not yet written, use camera")
            sys.exit(1)
            #passed = test_sensor(settings["sensor_name"], settings["sensor_threshold"])

        if passed:
            print("Confirmation passed!")
            return True, fail_count
        else:
            print("Confirmation failed; will retry.")
            fail_count += 1
            if settings["throw"].lower() == "true":
                print("Resetting relay before retrying...")
                trigger_relay(throw_cmd)
                time.sleep(2)

    return False, fail_count


def main():
    name, direction = parse_args()
    settings = load_config(name)
    settings["direction"] = direction

    # Map direction to commands
    if direction == "on":
        switch_cmd = settings["switch_on_cmd"]
        throw_cmd  = settings["switch_off_cmd"]
    elif direction == "off":
        switch_cmd = settings["switch_off_cmd"]
        throw_cmd  = settings["switch_on_cmd"]
    else:
        print(f"Switch direction {direction} invalid, should be 'on' or 'off'")
        sys.exit(1)

    success, failures = attempt_switch_with_confirmation(
                                         switch_cmd, throw_cmd, settings)

    if failures > 0:
        msg = (f"{name} failed {failures} times before {'succeeding' if success else 'giving up'}.")
        print(msg)

    if not success:
        print("Sending failure alert")
        alert_cmd = settings["alert_cmd"]
        subprocess.run(alert_cmd, shell=True)
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
