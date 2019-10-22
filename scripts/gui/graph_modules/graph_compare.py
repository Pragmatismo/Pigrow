
#
# This is an example script which can be used as a template to make your own graphs which intergrate with the pigrow remote gui
#
# Copy this file, remane it something that fits the pattern  graph_[name].py and save it into the graph_modules folder
#
# All code must happen within the make_graph function,
# Save the graph using the exact path given by graph_path
#
#
#

def make_graph(list_of_datasets, graph_path, ymax="", ymin="", size_h="", size_v="", dh="", th="", tc="", dc="", extra=[]):


    import matplotlib
    matplotlib.use('agg')
    import matplotlib.pyplot as plt


    def directionless_timedelta(time1, time2):
        if time1 > time2:
            return time1 - time2
        else:
            return time2 - time1

    if len(list_of_datasets) < 2:
        print("!!! You need two logs loaded to run this script ")
        return None

    # This compares onyl the first two datasets
    log_1_date_list = list_of_datasets[0][0]
    log_1_value_list = list_of_datasets[0][1]
    key_list_1 = list_of_datasets[0][2]
    log_2_date_list = list_of_datasets[1][0]
    log_2_value_list = list_of_datasets[1][1]
    key_list_2 = list_of_datasets[1][2]

    print("First log;", len(log_1_date_list), " Second log;", len(log_2_date_list))
    print("Want's to create a compare graph using the compare module")
    # group two lists so can calculate differences and etc

    matched_list_a_v = []
    matched_list_a_d = []
    matched_list_b_v = []
    matched_list_b_d = []
    time_diffs = []
    value_diffs = []
    # cycle through first set finding matching data
    log_2_counter = 0
    for x in range(0, len(log_1_date_list)):
        log_1_item_date =  log_1_date_list[x]
        first_log_after = 'None'
        #print(log_2_counter, len(log_2_date_list))
        if not log_2_counter > len(log_2_date_list) - 2:
            while first_log_after == 'None':
                log_2_item_date = log_2_date_list[log_2_counter]
                date_diff = log_1_item_date - log_2_item_date
                #print(x, log_1_item_date, log_2_counter, log_2_item_date)
                if log_1_item_date < log_2_item_date:
                    first_log_after = log_2_counter
                else:
                    log_2_counter += 1
                if log_2_counter > len(log_2_date_list):
                    first_log_after = None

            if log_2_counter > 0:

                time_diff_forward = directionless_timedelta(log_2_date_list[log_2_counter], log_1_date_list[x]).total_seconds()
                time_diff_back = directionless_timedelta(log_1_date_list[x], log_2_date_list[log_2_counter - 1]).total_seconds()
                if time_diff_forward < time_diff_back:
                    #print(" forward dif; ", time_diff_forward, " backward dif: ", time_diff_back)
                    #print("using forward")
                    matched_list_a_v.append(log_1_value_list[x])
                    matched_list_a_d.append(log_1_date_list[x])
                    matched_list_b_v.append(log_2_value_list[log_2_counter])
                    matched_list_b_d.append(log_2_date_list[log_2_counter])
                    time_diffs.append(time_diff_forward)
                    value_diff = log_1_value_list[x] - log_2_value_list[log_2_counter]
                    value_diffs.append(value_diff)
                else:
                    #print("using back")
                    matched_list_a_v.append(log_1_value_list[x])
                    matched_list_a_d.append(log_1_date_list[x])
                    matched_list_b_v.append(log_2_value_list[log_2_counter - 1])
                    matched_list_b_d.append(log_2_date_list[log_2_counter - 1])
                    time_diff_back = time_diff_back - time_diff_back - time_diff_back
                    time_diffs.append(time_diff_back)
                    value_diff = log_1_value_list[x] - log_2_value_list[log_2_counter - 1]
                    value_diffs.append(value_diff)





    # start making the graph
    fig, ax = plt.subplots(figsize=(size_h, size_v))
    # Top graph, the two data sets overlaid
    ax1 = plt.subplot(311)
    ax1.plot(log_1_date_list, log_1_value_list, color='blue', label=key_list_1[0], lw=1)
    ax1.plot(log_2_date_list, log_2_value_list, color='green', label=key_list_2[0], lw=1)
    #ax1.plot(matched_list_a_d, matched_list_a_v, color='blue', lw=1)
    #ax1.plot(matched_list_b_d, matched_list_b_v, color='black', lw=1)
    plt.title("Both Logs Overlaid")
    plt.grid(True)
    if key_list_1[0] == key_list_2[0]:
        plt.ylabel(key_list_1[0])
    else:
        ax1.legend()
    ax1.xaxis_date()
    # Second graph, the value difference
    ax2 = plt.subplot(312, sharex=ax1)
    ax2.plot(matched_list_a_d, value_diffs, color='black', lw=1)
    plt.title("Difference between closest log values")
    plt.ylabel("Difference")
    plt.grid(True)
    # Third graph, the time difference
    ax3 = plt.subplot(313, sharex=ax1)
    ax3.plot(matched_list_a_d, time_diffs, color='black', lw=1)
    plt.title("Time Difference between closest log values")
    plt.ylabel("Time Difference in Seconds")
    plt.grid(True)





    # create plot
    # Set y axis min and max range
    if not ymax == "":
        plt.ylim(ymax=int(ymax))
    if not ymin == "":
        plt.ylim(ymin=int(ymin))
    # format x axis to date
    fig.autofmt_xdate()
    # save the graph
    plt.savefig(graph_path)
    # tidying up after ourselves
    fig.clf()

    print("compare graph created and saved to " + graph_path)
