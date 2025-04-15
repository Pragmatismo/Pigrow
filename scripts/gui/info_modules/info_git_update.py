#!/usr/bin/env python3
import os
import sys
try:
    from git import Repo
except:
    print(" Unable to import git module, install using;")
    print("      sudo pip3 install GitPython")
    print("    or the pigrow_remote gui install tools.")
    sys.exit()

repo_branch = 'master'
r_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(r_path))
not_git = True
while not_git:
    cwd = os.getcwd()
    if not os.path.isdir( os.path.join( cwd, ".git"  )) :
        os.chdir('..')
    else:
        not_git = False
repo = Repo()

def show_info():
    def update_status_text():
        current_hash = repo.head.object.hexsha
        remote_repo = repo.remotes.origin
        remote_repo.fetch()
        has_update = remote_repo.refs[repo_branch].object.hexsha != current_hash
        if has_update:
            status_text = "Status; Update Available\n\n"
        else:
            status_text = "Status; local version upto date\n\n"
        return status_text, remote_text(remote_repo)

    def local_text():
        # create index diff to list locally modified files
        idx = repo.index.diff(None)
        # create text display
        local_text = "Local; " + str(len(idx)) + " files changed.\n"
        for x in idx:
            local_text += "    " + x.a_path + "\n"

        # check for untracked scripts
        script_list = []
        for x in repo.untracked_files:
            if "." in x:
                if x.split(".")[1] == "py":
                    script_list.append(x)
        # create note for user
        if len(script_list) > 0:
            local_text += "\n Plus " + str(len(script_list)) + " untracked .py files."
            for x in script_list:
                local_text += "\n    " + str(x)

        return local_text

    def remote_text(remote_repo):

        diff = repo.head.commit.diff(remote_repo.refs[repo_branch].object.hexsha)
#        print ( diff )
        remote_text = "Remote; " + str(len(diff)) + " files changed.\n"
        for x in diff:
                    remote_text += "    " + x.a_path + "\n"
    #    return remote_text + "\n"

        # remote_repo.refs[repo_branch].object.hexsha
        # remote_text +=  + x.summary + "\n"
        head = repo.head.ref
        tracking = head.tracking_branch()
        remote_text += "\nCommits to be applied;\n"
        for x in tracking.commit.iter_items(repo, f'{head.path}..{tracking.path}'):
            remote_text += " --  " + x.summary + "\n"
            for item in x.stats.files.keys():
                remote_text +=  "  - " + item + "\n"
            remote_text += "      " + str(x.authored_datetime) + "\n\n"
        return remote_text


    status_text, remote_text = update_status_text()
    local_text = local_text()
    info_text = "Git Repo: " + repo.working_tree_dir + " from " + repo.remotes.origin.url + " " + repo_branch
    info_text += "\n"
    info_text += status_text + remote_text + local_text
    return info_text


if __name__ == '__main__':
    print(show_info())
