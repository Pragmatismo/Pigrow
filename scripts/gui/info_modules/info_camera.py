#!/usr/bin/python3
import os

def show_info():
    #check pi to determin os version


    # picam info
    out =  os.popen("vcgencmd get_camera").read()
    if "detected=" in out:
        out = out.split('detected=')[1].strip()
        if out == "0":
            # If no cam detected check if camera module is enabled
            get_cam =  os.popen("sudo raspi-config nonint get_camera").read()
            if get_cam.strip() == "1":
                picam_text = "Picam Module Not Enabled\n"
            elif get_cam.strip() == "0":
                picam_text = 'Picam Enabled, None detected\n'
            else:
                picam_text = "Unable to determine if picam module is enabled"
        elif out == "1":
            picam_text = "1 Picam\n"
        elif out == "2":
            picam_text = "Dual Picams\n"
        else:
            picam_text = 'Multipul Picams\n'
    else:
        picam_text = " Command line output did not match expected format, possibly because vcgencmd is not installed"
        picam_text += " or possibly because your language is set to something other than english."

    # web camera info
    cam_text = "No webcam detected"
    out =  os.popen("ls /dev/video*").read()
    if "No such file or directory" in out:
        cam_text = "No webcams"
    else:
        camera_list = []
        possible_cams = out.strip().split()
        list_of_fake_video_channels = ['/dev/video10', '/dev/video11', '/dev/video12']
        for x in possible_cams:
            if not x in list_of_fake_video_channels:
                camera_list.append(x)
        try:
            #if len(camera_list) == 1:
            #    out =  os.popen("udevadm info --query=all /dev/video0 |grep ID_MODEL=").read()
            #    cam_name = out.split("=")[1].strip()
            #    cam_text = cam_name
            #elif len(camera_list) > 1:
            for cam in camera_list:
                out =  os.popen("udevadm info --query=all " + cam + " |grep ID_MODEL=").read()
                if not "=" in out:
                    cam_name = "unknown device"
                else:
                    cam_name = out.split("=")[1].strip()
                    cam_text = cam_name + "\n       on " + cam + "\n"
        except:
            #print("Failed to identify video source")
            cam_text = "Error reading webcams"
    info_text = picam_text + cam_text
    return info_text


if __name__ == '__main__':
    print(show_info())
