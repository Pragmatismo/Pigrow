#!/bin/bash

#downlaod from pi
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/caps_downloader.py
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/logs_downloader.py ta=pi@192.168.1.10
#make graphs
# --> make caps graph
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/caps_graph.py caps=/home/pragmo/frompigrow/caps/ out=/home/pragmo/frompigrow/
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/temp_graph.py log=/home/pragmo/frompigrow/logs/dht22_log.txt out=/home/pragmo/frompigrow/dht_temp_graph.png
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/humid_graph.py log=/home/pragmo/frompigrow/logs/dht22_log.txt out=/home/pragmo/frompigrow/dht_humid_graph.png
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/selflog_graph.py log=/home/pragmo/frompigrow/logs/self_log.txt out=/home/pragmo/frompigrow/
#make data wall
/home/pragmo/pigitgrow/Pigrow/scripts/visualisation/assemble_datawall.py gp=/home/pragmo/frompigrow/ caps=/home/pragmo/frompigrow/caps/ o=/home/pragmo/frompigrow/datawall.png null=/home/pragmo/pigitgrow/Pigrow/resources/null.png
#update wallpaper
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/wallpaper_update.sh /home/pragmo/pigitgrow/Pigrow/graphs/datawall.png
