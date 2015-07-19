#!/usr/bin/env python

"""
Usage:
  tig init
  tig commit <msg>
  tig checkout <rev> [-b <branch-name>]
  tig diff
  tig log
  tig branch

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


def init():
    os.makedirs(".tig/objects")
    os.makedirs(".tig/refs/heads")
    
    __write_file(".tig/refs/heads/master", "0")
    __write_file(".tig/head", "ref: refs/heads/master")


def __get_branches():
    return os.listdir(".tig/refs/heads")


def __get_current_branch():
    head_rev = __read_file(".tig/head")
    if head_rev[:4] != "ref:":
        return None

    branch_path = head_rev[4:].strip()
    branch_name = os.path.basename(branch_path)

    return branch_name


def branch():
    current = __get_current_branch()
    for branch in sorted(__get_branches()):
        star = "*" if branch == current else " "
        print "{0}{1}".format(star, branch)


def commit(msg):
    branch = __get_current_branch()
    if branch == None:
        print "tig: not at tip"
        return

    master_rev = __read_file(".tig/refs/heads/{0}".format(branch))

    sha1sum_content = __storedb(__read_file("file.txt"))
    sha1sum_commit = __storedb(json.dumps({
        "content": sha1sum_content,
        "parent": master_rev,        
        "log-msg": msg,
        "author": os.getenv("USER"),
        "time": int(time.time())
    }, indent=4))

    __write_file(".tig/refs/heads/{0}".format(branch), sha1sum_commit)
    print sha1sum_commit


def checkout(rev, branch):
    content_sha1sum = __content_from_commit(rev)
    content = __getdb(content_sha1sum)
    
    __write_file("file.txt", content)

    if branch is None:
        __write_file(".tig/head", rev)
    else:
        __write_file(".tig/refs/heads/{0}".format(branch), rev)
        __write_file(".tig/head", "ref: refs/heads/{0}".format(branch))
        

def diff():
    branch = __get_current_branch()
    if branch == None:
        commit_sha1sum = __read_file(".tig/head")
    else:
        commit_sha1sum = __read_file(".tig/refs/heads/{0}".format(branch))

    head_rev = __content_from_commit(commit_sha1sum)

    with open(".tig/objects/{0}".format(head_rev), "r") as orig_file:
        orig_content = orig_file.readlines()
    
    with open("file.txt", "r") as curr_file:
        curr_content = curr_file.readlines()
        
    lines = difflib.unified_diff(orig_content, curr_content, "a/file.txt", "b/file.txt")
    print("".join(lines))


def log():
    branch = __get_current_branch()
    if branch == None:
        commit_sha1sum = __read_file(".tig/head")
    else:
        commit_sha1sum = __read_file(".tig/refs/heads/{0}".format(branch))
    
    while True:
        commit = json.loads(__getdb(commit_sha1sum))
        print commit_sha1sum[:6], commit["log-msg"]
        commit_sha1sum = commit["parent"]
        if commit_sha1sum == "0":
            break


def main():
    args = docopt.docopt(__doc__)
    if args["commit"]:
        commit(args["<msg>"])
    elif args["checkout"]:
        checkout(args["<rev>"], args["-b"])
    elif args["init"]:
        init()
    elif args["diff"]:
        diff()
    elif args["log"]:
        log()
    elif args["branch"]:
        branch()
    else:
        # Not reached
        pass


if __name__ == "__main__":
    main()
