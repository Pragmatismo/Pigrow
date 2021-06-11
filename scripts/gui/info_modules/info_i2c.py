#!/usr/bin/python3
import os

def show_info():
    def i2c_check_bus():
        # checking for i2c folder in /dev/
        out =  os.popen("ls /dev/*i2c*").read()
        #
        if "/dev/i2c-1" in out:
            i2c_text = ("found i2c bus 1")
            i2c_bus_number = 1
        elif "/dev/i2c-0" in out:
            i2c_bus_number = 0
            i2c_text = ("found i2c bus 0")
        elif "/dev/i2c-" in out:
            # when not found on most likely spaces look for others
            i2c_bus_number = out.split("/dev/i2c-")[1]
            if i2c_bus_number.isdigit():
                i2c_bus_number = int(i2c_bus_number)
                i2c_text = "found i2c bus " + str(i2c_bus_number)
        else:
            return "", "i2c bus not found\n"
        # if i2c bus found perform aditional checks, updates the textbox and returns the bus number
        # check if baurdrate is changed in Config
        i2c_baudrate = check_i2c_baudrate(i2c_bus_number)
        i2c_text += " baudrate " + str(i2c_baudrate) + "\n"
        #
        #  also might be worth looking at  sudo cat /sys/module/i2c_bcm2708/parameters/baudrate
        #                                     though it reads 0 when unset, I think
        #
        return i2c_bus_number, i2c_text

    def check_i2c_baudrate(i2c_bus_number):
        # ask pi to read the pi's boot congif file for i2c baudrate info
        #print("looking at /boot/config.txt file for baudrate setting;")
        # dtparam=i2c_baudrate
        #out, error = self.link_pnl.run_on_pi("cat /boot/config.txt | grep i2c" + str(i2c_bus_number) + "_baudrate=") #if it wants to know bus num
    #    out, error = self.link_pnl.run_on_pi("cat /boot/config.txt | grep i2c_baudrate=")
        out = os.popen("cat /boot/config.txt | grep i2c_baudrate=").read()
        out = out.replace("dtparam=i2c_baudrate=", "").strip()
        if out == "" or out == None:
            #print("Baudrate not changed in /boot/config.txt")
            return "default"
        #else:
            #print("Baudrate changed to;" + str(out))
        return out

    # this has to be run by a button press because it might
    # in some situations confuse i2c sensors so best
    # not to call it needlessly
    # returns a list of i2c addresses which may be useful at some point
    #                                 when doing live readings or some such
    #                                 but isn't currently used
    ##
    # calsl i2c_check to locate the active i2c bus
    i2c_bus_number, i2c_text = i2c_check_bus()
    if not i2c_bus_number == "":
        #print ("reading i2c bus ", i2c_bus_number)
        # check i2c bus with i2cdetect and list found i2c devices
        out = os.popen("/usr/sbin/i2cdetect -y " + str(i2c_bus_number)).read()
        #print(out)
        i2c_devices_found = out.splitlines()
        # trimming text and sorting into a list
        i2c_addresses = []
        for line in i2c_devices_found[1:]:
            line = line[3:].replace("--", "").strip()
            if not line == "":
                if not len(line) > 2: #only lines with 1 item in
                    i2c_addresses.append(line)
                else: #lines with more than one item
                    for item in line.split("  "):
                        i2c_addresses.append(item)
        # changing text on screen
        if len(i2c_addresses) > 0:
            i2c_text += "Found " + str(len(i2c_addresses)) + " devices at; " + str(i2c_addresses)
        else:
            i2c_text += "No devices found"

    return i2c_text



if __name__ == '__main__':
    print(show_info())
