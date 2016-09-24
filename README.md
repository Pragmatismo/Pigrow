# Pigrow
Raspberry Pi Grow Box Control Software

This is the software required to control a pigrow2, if you don't
know what a pigrow2 is then check out the videos and guides on 
                https://www.patreon.com/Pigrow2

Currently everything is at an alpha development stage, a stable release
will happen as soon as possible, in the mean time anyone intereted in
setting up a pigrow should message me personally and i'll help you
directly. 

----------

Install and Setup

------

Test and config scripts; 

            - LED - test_led.py - simply turns the LED on for 30 seconds
 
            - Relay - test_relay.py - cycles the relays turning them all on then when they're all on it starts turning them off again.
      !!!!!!!!      - config_relay.py - set's and test's which terminal (normally on or normally off) the sockets were plugged into, allows you to assign functions to relays 

            - Camera - cam_config.py - creates the persistant settings for use when recording a timelapse or viewing the pi.




scripts to be called by cron;

To add a one of the following timelapse programs to cron simply use;
   
       sudo crontab -e

and at the bottom of the file after the explanation of how it works add the line;

       */1 * * * * python /home/pi/Pigrow/scripts/camcap_text_simple.py

This will run the script and take an image every one min.

              Camera -
                     - camcap.py - captures just a single image for
                     - camcap_text_simple.py - captures image and adds date and sensor data to it. 
            !!!!     - camcap_text_colour.py - text colour changes according to sensor data. 


To set up a 12:12 light cycle simple add the two lines;

     0 10 * * * python /home/pi/pigrow3/lamp_on.py
     0 22 * * * python /home/pi/pigrow3/lamp_off.py     

This turns the lamp on at ten am and off at ten pm. Try not to turn on fans and lamps at exactly the same time, it will work but both items cause power-spikes which if combined might trip your RCD.

              Relay -
                    - lamp_on / off - actuates lamp relay
                    - fan_on / off - for manual timing of fan
                    - heat_on / off - for manual timing of heat
                    - dehumi_on / off - for manual timing of dehumidifier

These scripts are run preiodically as with the camera scripts to check the health of the pi or it's friend, you can check many pi's by calling the script many times.

        Sanity Check - 
                     - self_awareness - sensor log, camera, health check
                     - nosey_neighbour - check on a brother pigrow

Scripts to be constantly running;

This is some init.d business i'll be back to explain once the script is uploaded...

          autorunlog.py - logs sensor data to file, switches heaters or fans according to sensor data





------- Useful information which might be needed before release of setup scripts

Installing 3rd party software commands;

--Adafruit DHT sensor drivers,

    git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    cd Adafruit_Python_DHT
    sudo apt-get update
    sudo apt-get install build-essential python-dev python-openssl
    sudo python setup.py install

      -more information at, https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated

--From linux Repository 

     sudo apt-get install uvccapture       #for use with camera

     sudo pip install pexpect              #for use when logging other pigrows health


directory structure 

            mkdir /home/pi/Pigrow/logs
            mkdir /home/pi/Pigrow/config
            mkdir /home/pi/Pigrow/graphs
 
to set timed events useibg cron

     crontab -e

lines to include might look like;
  
     0 7 * * * python /home/pi/pigrow2/lampon.py           #turns lamp relay on at 7 am
     0 1 * * * python /home/pi/pigrow2/lampoff.py          #turns lamp relay off at 1 am

     */5 * * * * python /home/pi/Pigrow/scripts/pi_eye_logger.py    #runs pi_eye monitoring script every 5min

