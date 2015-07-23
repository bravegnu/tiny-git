#!/usr/bin/env python

"""
Usage:
  tig init
  tig commit <msg>
  tig checkout <start-point> [-b <branch-name>]
  tig diff
  tig log
  tig branch
  tig merge <branch>

Options:
  -b <branch-name>    Branch name to checkout.
"""

import sys
import docopt
import os
import shutil
import difflib
import hashlib
import json
import time
import tempfile
import subprocess


def __sha1(content):
    sha1sum = hashlib.sha1()
    sha1sum.update(content)
    return sha1sum.hexdigest()


def __read_file(filename):
    with open(filename) as my_file:
        return my_file.read()


def __write_file(filename, content):
    with open(filename, "w") as my_file:
        return my_file.write(content)


def __storedb(content):
    sha1sum = __sha1(content)
    __write_file(".tig/objects/{0}".format(sha1sum), content)
    return sha1sum


def __getdb(sha1sum):
    return __read_file(".tig/objects/{0}".format(sha1sum))


def __content_from_commit(sha1sum):
    return json.loads(__getdb(sha1sum))["content"]


def __get_branches():
    return os.listdir(".tig/refs/heads")


def __set_head(rev):
    if rev in __get_branches():
        __write_file(".tig/HEAD", "ref: refs/heads/{0}".format(rev))
    else:
        __write_file(".tig/HEAD", rev)


def __get_current_branch():
    head_rev = __read_file(".tig/HEAD")
    if head_rev[:4] != "ref:":
        return None

    branch_path = head_rev[4:].strip()
    branch_name = os.path.basename(branch_path)

    return branch_name


def __get_head_commit():
    branch = __get_current_branch()
    if branch == None:
        return __read_file(".tig/HEAD")
    else:
        return __read_file(".tig/refs/heads/{0}".format(branch))


def __set_branch_commit(branch, commit_sha1sum):
    __write_file(".tig/refs/heads/{0}".format(branch), commit_sha1sum)


def __get_branch_commit(branch):
    return __read_file(".tig/refs/heads/{0}".format(branch))


def init():
    os.makedirs(".tig/objects")
    os.makedirs(".tig/refs/heads")
    
    __set_branch_commit("master", "0")
    __set_head("master")


def branch():
    current = __get_current_branch()
    for branch in sorted(__get_branches()):
        star = "*" if branch == current else " "
        print "{0}{1}".format(star, branch)


def __create_commit(content_sha1sum, parents, msg):
    sha1sum_commit = __storedb(json.dumps({
        "content": content_sha1sum,
        "parent": parents,
        "log-msg": msg,
        "author": os.getenv("USER"),
        "time": int(time.time())
    }, indent=4))
    return sha1sum_commit


def commit(msg):
    branch = __get_current_branch()
    if branch == None:
        print "tig: not at tip"
        return

    master_rev = __get_branch_commit(branch)
    sha1sum_content = __storedb(__read_file("file.txt"))
    sha1sum_commit = __create_commit(sha1sum_content, [master_rev], msg)
    __set_branch_commit(branch, sha1sum_commit)

    print sha1sum_commit


def __is_branch(start_point):
    return start_point in __get_branches()


def __commit_from_start_point(start_point):
    if __is_branch(start_point):
        return __get_branch_commit(start_point)

    return start_point


def __update_working_copy(start_point):
    commit_sha1sum = __commit_from_start_point(start_point)
    content_sha1sum = __content_from_commit(commit_sha1sum)
    content = __getdb(content_sha1sum)
    
    __write_file("file.txt", content)
    return commit_sha1sum

def checkout(start_point, new_branch):
    commit_sha1sum = __update_working_copy(start_point)

    if new_branch is None:
        __set_head(start_point)
    else:
        __set_branch_commit(new_branch, commit_sha1sum)
        __set_head(new_branch)
        

def diff():
    commit_sha1sum = __get_head_commit()
    content_sha1sum = __content_from_commit(commit_sha1sum)

    orig_content = __getdb(content_sha1sum)
    orig_content = orig_content.splitlines(True)

    curr_content = __read_file("file.txt")
    curr_content = curr_content.splitlines(True)
        
    lines = difflib.unified_diff(orig_content, curr_content, "a/file.txt", "b/file.txt")
    print("".join(lines))


def log():
    commit_sha1sum = __get_head_commit()
    
    while True:
        commit = json.loads(__getdb(commit_sha1sum))
        print commit_sha1sum[:6], commit["log-msg"]
        commit_sha1sum = commit["parent"][0]
        if commit_sha1sum == "0":
            break


def __get_common_ancestor(commit1, commit2):
    if commit1 == commit2:
        return

    ancestors1 = [commit1]
    ancestors2 = [commit2]

    while True:
        commit_obj = json.loads(__getdb(commit1))
        parent_commit = commit_obj["parent"][0]
        if parent_commit in ancestors2:
            return parent_commit

        ancestors1.append(parent_commit)
        commit1 = parent_commit

        commit_obj = json.loads(__getdb(commit2))
        parent_commit = commit_obj["parent"][0]
        if parent_commit in ancestors1:
            return parent_commit

        ancestors2.append(parent_commit)
        commit2 = parent_commit

    return None


def __diff3(mine_sha1sum, orig_sha1sum, your_sha1sum):
    tmpdir = tempfile.mkdtemp()

    diff3_files = [("mine", mine_sha1sum),
                   ("orig", orig_sha1sum),
                   ("your", your_sha1sum)]

    for filename, sha1sum in diff3_files:
        path = os.path.join(tmpdir, filename)
        content_sha1sum = __content_from_commit(sha1sum)
        __write_file(path, __getdb(content_sha1sum))

    conflicted = False
    merged_path = os.path.join(tmpdir, "merged")
    with open(merged_path, "w") as merged_file:
        ret = subprocess.call(["diff3", "-A", "-m", "mine", "orig", "your"],
                              cwd=tmpdir, stdout=merged_file)
        if ret != 0:
            conflicted = True

    return __read_file(os.path.join(merged_path)), conflicted


def merge(branch):
    mine_sha1sum = __get_head_commit()
    your_sha1sum = __get_branch_commit(branch)

    ca_sha1sum = __get_common_ancestor(mine_sha1sum, your_sha1sum)
    if not ca_sha1sum:
        print "tig: failed to find common ancestor"
        return

    if ca_sha1sum == your_sha1sum:
        print "tig: up-to-date"
        return

    if ca_sha1sum == mine_sha1sum:
        print "tig: fast-forward merge"
        mine_branch = __get_current_branch()
        __set_branch_commit(mine_branch, your_sha1sum)
        __update_working_copy(mine_branch)
        return

    # True Merge
    merged, conflicted = __diff3(mine_sha1sum, ca_sha1sum, your_sha1sum)
    __write_file("file.txt", merged)

    if not conflicted:
        content_sha1sum = __storedb(merged)
        commit_sha1sum = __create_commit(content_sha1sum,
                                         [mine_sha1sum, your_sha1sum],
                                         "Merged changes from '{0}'".format(branch))
        mine_branch = __get_current_branch()
        __set_branch_commit(mine_branch, commit_sha1sum)
        print commit_sha1sum
    else:
        # FIXME: This needs to be handled.
        print "tig: merge conflict occurred"


def main():
    args = docopt.docopt(__doc__)
    if args["commit"]:
        commit(args["<msg>"])
    elif args["checkout"]:
        checkout(args["<start-point>"], args["-b"])
    elif args["init"]:
        init()
    elif args["diff"]:
        diff()
    elif args["log"]:
        log()
    elif args["branch"]:
        branch()
    elif args["merge"]:
        merge(args["<branch>"])
    else:
        # Not reached
        pass


if __name__ == "__main__":
    main()
