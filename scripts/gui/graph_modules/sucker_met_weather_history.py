
def run_sucker():
    #
    #   Example log reader
    #

    #
    log_to_load = "heathrowdata.txt"
    # https://www.metoffice.gov.uk/pub/data/weather/uk/climate/stationdata/heathrowdata.txt
    #
    #    Mean daily maximum temperature (tmax)
    #    Mean daily minimum temperature (tmin)
    #    Days of air frost (af)
    #    Total rainfall (rain)
    #    Total sunshine duration (sun)
    #
    import os
    import datetime

    graph_modules_folder = os.path.join(os.getcwd(), "graph_modules")
    log_path = os.path.join(graph_modules_folder, log_to_load)




    # read the log into lines
    with open(log_path) as f:
        log_to_read = f.read()
    log_to_read = log_to_read.splitlines()
    # remove the header text at the top
    log_to_read = log_to_read[7:]
    #
    # define empty lists to fill
    line_dates = []
    line_tmaxs = []
    line_tmins = []
    line_afdayss = []
    line_rains = []
    line_suns = []
    keys = []
    # loop through spliting the lines and grabbing the data
    for line in log_to_read:
        line = line.split(" ")
        field_to_fill = 0
        for item in line:
            if len(item) > 0:
                if field_to_fill == 0:
                    line_year = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 1:
                    line_month = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 2:
                    line_tmax = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 3:
                    line_tmin = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 4:
                    line_afdays = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 5:
                    line_rain = item
                    field_to_fill = field_to_fill + 1
                elif field_to_fill == 6:
                    line_sun = item
                    field_to_fill = field_to_fill + 1
        try:
            date = datetime.datetime(year = int(line_year), month = int(line_month), day = 1, hour = 0, minute = 0, second = 0)
            line_tmax = float(line_tmax)
            line_tmin = float(line_tmin)
            line_afdays = float(line_afdays)
            line_rain = float(line_rain)
            line_sun = line_sun.replace("#", "")
            line_sun = float(line_sun)
            # now we know they're valid numbers add to the lists
            # doing it first helps make sure our lists remain even.
            line_dates.append(date)
            line_tmaxs.append(line_tmax)
            line_tmins.append(line_tmin)
            line_afdayss.append(line_afdays)
            line_rains.append(line_rain)
            line_suns.append(line_sun)
            keys.append(log_to_load)
        except:
            print("Line failed to read ", line)

    # Choose which sets to return
    values = line_tmaxs
    dates = line_dates
    # Keys
    keys = keys


    # Hand back the values to the gui,they must be even sized lists
    return values, dates, keys
