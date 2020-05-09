#!/usr/bin/python3
import datetime, sys, os
homedir = os.getenv("HOME")
sys.path.append(homedir + '/Pigrow/scripts/')
import pigrow_defs

for argu in sys.argv[1:]:
    if argu == '-h' or argu == '--help':
        print("Pigrow RX off switch")
        print("")
        sys.exit()
    if argu == "-flags":
        print("")

def RF_off(set_dic, switch_log):
    script = 'RF_off.py'
    msg =("\n")
    msg +=("      #############################################\n")
    msg +=("      ##         Turning the RF - OFF          ##\n")
    if 'gpio_RF' in set_dic and not str(set_dic['gpio_RF']).strip() == '':
        gpio_pin = int(set_dic['gpio_RF'])
        from rpi_rf import RFDevice
        rfdevice = RFDevice(gpio_pin)
        rfdevice.enable_tx()
        rfdevice.tx_code(15465750, 1, 432)
        rfdevice.tx_repeat=5
        msg +=("      ##            by switching GPIO "+str(gpio_pin)+" to "+gpio_pin_dir+"  ##\n")
        msg +=("      #############################################\n")
        pigrow_defs.set_condition(condition_name="RF", trig_direction="off", cooldown="none")
        pigrow_defs.write_log(script, 'RF turned off', switch_log)
        return msg
    else:
        msg +=("      !!               NO RF PIN SET            !!\n")
        msg +=("      !!  run config program or edit config.txt !!\n")
        msg +=("      !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        pigrow_defs.write_log(script, 'Failed - due to none set in config', switch_log)
        return msg

if __name__ == '__main__':

    ### default settings
    loc_dic = pigrow_defs.load_locs(homedir + "/Pigrow/config/dirlocs.txt")
    set_dic = pigrow_defs.load_settings(loc_dic['loc_settings'], err_log=loc_dic['err_log'],)
    msg = RF_off(set_dic, loc_dic['loc_switchlog'])
    print (msg)
