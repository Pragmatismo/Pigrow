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

              Camera -
                     - camcap.py - captures just a single image for
                     - camcap_text_simple.py - captures image and adds date and sensor data to it. 
            !!!!     - camcap_text_colour.py - text colour changes according to sensor data. 

              Relay -
                    - lamp_on / off - actuates lamp relay
                    - fan_on / off - for manual timing of fan
                    - heat_on / off - for manual timing of heat
                    - dehumi_on / off - for manual timing of dehumidifier

        Sanity Check - 
                     - self_awareness - sensor log, camera, health check
                     - nosey_neighbour - check on a brother pigrow

Scripts to be constantly running;

          autorunlog.py - logs sensor data to file, switches heaters or fans according to sensor data


