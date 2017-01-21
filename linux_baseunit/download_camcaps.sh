#!/bin/bash

# This script downloads files from the pi and sets the most recent as
# your desktop background image, it is designed to be run via cron.
#   $crontab -e
#           */5 * * * * sudo -u magimo /home/USER/Pigrow/linux_baseunit/download_cam_wallpaper.sh
#
# user changeable variables
local_dir=/home/pragmo/camcaps/
remote_dir=/hpme/pi/cam_caps/*.jpg #shpi;d be /home/pi/cam_caps/ normally
remote_add=pi@192.168.1.2                      #address of the pi
rasppas=raspberry

echo ----
echo Scripted downloader and background up-dater
echo --------

#lists the most recent file in directory before download
echo current most recent...
echo $(ls $local_dir | sort -V | tail -n 1)
echo ---------
#downloads files
rsync --ignore-existing -ratlz --rsh="/usr/bin/sshpass -p $rasppas ssh -o StrictHostKeyChecking=no -l $remote_add" $remote_add:/home/pi/cam_caps/text_*.jpg $local_dir
# To see what it's doing after --ignore-existing add --progress

echo downloaded
