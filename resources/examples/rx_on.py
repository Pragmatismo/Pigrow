#!/usr/bin/python3
import datetime, sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow RF switch")
        print("")
        print("This turns the RF Device ON")
        #print("To use this program you must have the devices GPIO and wiring direction")
        #print("set in the pigrow configuration file /config/pigrow_config.txt")
        #print("use the setup tool /scripts/config/setup.py or the remote gui")
        sys.exit()
    elif argu == "-flags":
        print("")

def RF_on(set_dic, switch_log):
    script = 'RF_on.py'
    msg = ("")
    msg +=("      #############################################\n")
    msg +=("      ##         Turning the RF - ON           ##\n")
    from rpi_rf import RFDevice
    if 'gpio_RF' in set_dic:
        if not str(set_dic['gpio_RF']).strip() == '':
            gpio_pin = int(set_dic['gpio_RF'])
        else:
            print(" - RF gpio pin not set")
    else:
        msg +=("      !!               NO RF SET             !!\n")
        msg +=("      !!  run config program or edit config.txt  !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, 'Failed - due to none set in config', switch_log)
        return msg

    rfdevice = RFDevice(gpio_pin)
    rfdevice.enable_tx()
    rfdevice.tx_code(15465751, 1, 432)
    rfdevice.tx_repeat=5
    msg +=("      ##            using GPIO "+str(gpio_pin)+"      ##\n")
    msg +=("      #############################################\n")
    pigrow_defs.set_condition(condition_name="RF", trig_direction="on", cooldown="none")
    pigrow_defs.write_log(script, 'RF turned on', switch_log)
    return msg

if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    msg = RF_on(set_dic, loc_dic['loc_switchlog'])
    print (msg)
