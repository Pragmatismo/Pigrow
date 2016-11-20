#!/bin/bash

local_dir=/home/pragmo/camcaps/
#local_dir=/home/pragmo/pigitgrow/Pigrow/graphs/

if [ -z $1 ]
    then
      echo File not spesified, using most recent camcaps


#lists the most recent file after download
echo ----------
echo most recent...
lastfile=$(ls $local_dir | sort -V | tail -n 1)
echo $lastfile

echo ------------
echo updaiting background
# this bit allows it to work from cron
PID=$(pgrep gnome-session)
export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)
# set's the background in gnome, unity and derivitives
gsettings set org.gnome.desktop.background picture-uri file://$local_dir$lastfile


fi



gsettings set org.gnome.desktop.background picture-uri file://$1
echo updated wallpaper
