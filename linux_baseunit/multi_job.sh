#!/bin/bash
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/caps_downloader.py
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/logs_downloader.py ta=pi@192.168.1.10 
#make caps graph
#make temp graph
#make humid graph
#make self log graphs
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/assemble_datawall.py
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/wallpaper_update.sh /home/pragmo/pigitgrow/Pigrow/graphs/datawall.png
