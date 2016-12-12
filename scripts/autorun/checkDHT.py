
import os, sys
sys.path.append('/home/pragmo/pigitgrow/Pigrow/scripts/')
import pigrow_defs
loc_dic = pigrow_defs.load_locs("/home/pragmo/pigitgrow/Pigrow/config/dirlocs.txt")
set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
#print set_dic



#    try:
#        humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_pin)
#        if humidity is not None and temperature is not None:
#            timno = datetime.datetime.now()
