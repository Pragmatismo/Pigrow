#!/bin/bash

sudo -u 'pragmo' python /home/pragmo/pigitgrow/Pigrow/linux_baseunit/download_logs.py
sudo -u 'pragmo' python /home/pragmo/pigitgrow/Pigrow/scripts/visualisation/assemble_datawall.py o=/home/pragmo/pigitgrow/Pigrow/graphs/datawall.png g1=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/Temperature.png g2=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/file_size_graph.png g3=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/consecutive_pi_time_graph.png g4=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/Humidity.png g5=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/sec_since_up_graph.png g6=/home/pragmo/pigitgrow/Pigrow/frompi/pi@192.168.1.2/graphs/step_graph.png pbw=900 gbw=500
/home/pragmo/pigitgrow/Pigrow/linux_baseunit/wallpaper_update.sh /home/pragmo/pigitgrow/Pigrow/graphs/datawall.png
