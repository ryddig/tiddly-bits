# code_reviewers.py
# @author tberg
# @date 01.15.2016
#
# This python script will accept a git project folder argument, a git commit,
# and optionally a max-authors parameter (default is 5).  With those arguments
# the script will get the list of files changed for the git commit and then
# check each of those files for up to the MAX-AUTHORS number of authors for
# each file, sorted from highest to lowest.  The goal is to list major
# contributors to each file in order to identify good candidates to ask for a
# code review.
import os, sys, subprocess

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print "Usage: code_reviewers.py <folder> <git-ref> [<max-authors>]"
    exit(1)

root_dir = os.path.abspath(sys.argv[1])
try:
    with open(os.devnull, 'w') as devnull:
        f = subprocess.check_output("git --no-pager -C " + root_dir + \
        " diff-tree --no-commit-id --name-only -r " + sys.argv[2], \
        stderr=devnull, shell=True)
except:
    print "Error: unable to get git commit details"
    exit(1)

maxAuthors = 5
if len(sys.argv) == 4:
    try:
        maxAuthors = int(sys.argv[3])
    except:
        print "Error: <max-authors> argument must be an integer"
        exit(1)

# generate dictionary of total commits and files for a given a author
user_dict = {}
for filename in f.split():
    file_path = os.path.join(root_dir, filename)

    with open(os.devnull, 'w') as devnull:
        p = subprocess.check_output("git --no-pager -C " + os.path.abspath(root_dir) + \
        " blame --line-porcelain " + file_path + " | sed -n 's/^author-mail //p' | sort | uniq -c | sort -rn", \
        stderr=devnull, shell=True)

    freq_list = map(lambda s: s.strip(), p.split('\n'))

    if len(freq_list) > maxAuthors:
        freq_list = freq_list[0:maxAuthors]
    elif freq_list[-1] == '':
        freq_list = freq_list[0:-1]

    freq_list = map(lambda s: s.split(), freq_list)

    for commits, user in freq_list:
        if not user in user_dict.keys():
            user_dict[user] = {"commits":0, "files":[]}

        user_dict[user]["commits"] += int(commits)
        user_dict[user]["files"].append(filename)

# reorganize results into a reverse sorted list by # of commits
user_list = []
for key, value in user_dict.iteritems():
    user_list.append([key, value["commits"], value["files"]])
user_list = sorted(user_list, key = lambda user: (user[1], len(user[2]), user[0]))
user_list.reverse()

# now lets output the results in a nice to read format
for user in user_list:
    print user[0], user[1], "committed lines in files:", user[2]
