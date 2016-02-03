# access_stats.py
# @author tberg
# @date 02.03.2820c4356852ddd5da10736b78273ca1
#
# **NOTE**: Do not use this script as-is unless you trust your input.  I'm
# using the lazy way of opening the subprocess without sanitizing inputs.
# This could easily be used to execute other commands if you don't know where
# your args are coming from.
#
# This python script will roll through apache access logs and split apart the
# time, method, path, response code, and size.  Then with that data, it will
# show you in a user friendly format the various paths in one minute chunks.
# A little tweaking to the script and you can see counts for unique paths, etc.
#
# I'm using this for finding 500 errors so I'm filtering on that response code.
# If you want all traffic you'll need to remove that.
import os, sys, subprocess
from collections import defaultdict

replay = False
replay_url = ""
ignore_list = [] # for healthchecks and "noise" that you don't want to see

logs = sys.argv[2:]
requests_by_time_dict = defaultdict(dict)
requests_by_path_dict = defaultdict(dict)
for log in logs:
    with open(os.devnull, 'w') as devnull:
        p = subprocess.check_output("cat " + os.path.abspath(log) + \
        " | sed -e 's/^[0-9]*.[0-9]*.[0-9]*.[0-9]* - - \[[0-9]*\/Jan\/[0-9]*://'",
        stderr=devnull, shell=True)

    # I've got my server name as part of the logfile name as I'm pulling from
    # multiple machines and aggregating results.
    server = log.split('_')[0]
    for line in p.split('\n'):
        if line:
            time, _, method, path, _, code, size = line.split()
            if path not in ignore_list and int(code) == 500:
                time = time[0:5]
                method = method[1:]

                if "total" not in requests_by_time_dict[time].keys():
                    requests_by_time_dict[time]["total"] = 0
                requests_by_time_dict[time]["total"] += 1

                if path not in requests_by_time_dict[time].keys():
                    requests_by_time_dict[time][path] = 0
                requests_by_time_dict[time][path] += 1

sorted_keys = requests_by_time_dict.keys()
sorted_keys.sort()
for key in sorted_keys:
    print key
    for path in requests_by_time_dict[key].keys():
        if path != "total":
            print "\t", path

            if replay:
                with open(os.devnull, 'w') as devnull:
                    p = subprocess.check_output("curl '" + replay_url + path + "'",
                    stderr=devnull, shell=True)
