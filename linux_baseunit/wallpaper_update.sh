#!/bin/bash
caps_dir=/home/pragmo/frompigrow/caps/
#caps_dir=/home/pragmo/pigitgrow/Pigrow/graphs/

mode="folder"
feh="false"
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -feh|--feh)
    echo "using feh to set wallpaper"
    feh="true"
    shift # past argument
    ;;
    *)
    if [ -d $key ]
      then
        echo "using $key as caps folder"
        caps_dir="$key"
        mode="folder"
    fi
    if [ -f $key ]
      then
        echo "using $key for wallpaper image"
        caps_img=$key
        mode="image"

    fi
    ;;
esac
shift
done

echo "feh is $feh"

if [ "$mode" = "folder" ]
then
  echo "File not spesified, using most recent camcaps"
  #lists the most recent file after download
  echo ----------
  echo "most recent..."
  #lastfile=$(ls $caps_dir | sort -V | tail -n 1)
  #echo $caps_dir$lastfile
  lastfile=$(ls $caps_dir | sort -V | tail -n 1)
  echo $caps_dir$lastfile
  echo ------------
  echo "updaiting background"
  # this bit allows it to work from cron
  if [ "$feh" = "false" ]
  then
    PID=$(pgrep gnome-session)
    export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)
    # set's the background in gnome, unity and derivitives
    #gsettings set org.gnome.desktop.background picture-uri file://$caps_dir$lastfile
    gsettings set org.gnome.desktop.background picture-uri file://"$caps_dir$lastfile"
    echo "updated with gsettings"
  else
    feh --bg-max $caps_dir$lastfile
    echo "updated with feh"
  fi
fi

if [ "$mode" = "image" ]
then
  echo "Changing destop to file,,"
  if [ "$feh" = "false" ]
  then
    PID=$(pgrep gnome-session)
    export DBUS_SESSION_BUS_ADDRESS=$(grep -z DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ|cut -d= -f2-)
    gsettings set org.gnome.desktop.background picture-uri file://$caps_img
  else
    feh --bg-max $caps_img
    echo "updated with feh"
  fi
fi
echo "done"
