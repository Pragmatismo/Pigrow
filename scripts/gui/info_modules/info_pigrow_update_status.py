#!/usr/bin/python3
import os

def show_info():

    update_needed = False
    #
    # read git update info
    #
    out =  os.popen("git -C ~/Pigrow/ remote -v update").read()
    git_text = out.split("\n")
    # check for masterbranch
    count = 0
    for line in git_text:
        if "origin/master" in line:
            master_branch = line
            count = count + 1
    # check to confirm master branch was detected and set flags
    if count > 1:
        print("ERROR ERROR TWO MASTER BRANCHES WTF?")
    elif count == 0:
        install_needed = True
    elif count == 1:
        if "[up to date]" in master_branch:
            update_needed = False
        else:
            update_needed = True

    # Read git status
    if update_needed == True:
        out =  os.popen("git -C ~/Pigrow/ status --untracked-files no").read()

        if "Your branch and 'origin/master' have diverged" in out:
            update_needed = 'diverged'
        elif "Your branch is" in out:
            git_line = out.split("\n")[1]
            git_update = git_line.split(" ")[3]
            if git_update == 'behind':
                update_needed = True
                git_num = git_line.split(" ")[6]
            elif git_update == 'ahead':
                update_needed = 'ahead'
        else:
            update_needed = 'error'


    # construct output message.
    if update_needed == True:
        msg = "update required, " + str(git_num) + " updates behind"
        #update_type = "clean"

    elif update_needed == False:
        msg = "Pigrow code is upto date"
        #update_type = "none"

    elif update_needed == 'ahead':
        msg = "Caution Required!\nYou modified your Pigrow code"
        #update_type = "merge"

    elif update_needed == 'diverged':
        msg = "Caution Required!\nYou modified your Pigrow code"
        #update_type = "merge"

    elif update_needed == 'error':
        if install_needed == True:
            msg = "Error reading git"
            #update_type = "error"

    else:
        msg = "Some confusion with git, sorry."
        #update_type = "error"

    return msg

if __name__ == '__main__':
    print(show_info())
