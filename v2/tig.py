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


def __set_master_commit(commit_sha1sum):
    __write_file(".tig/master", commit_sha1sum)


def __get_master_commit():
    return __read_file(".tig/master")


def init():
    os.makedirs(".tig/objects")
    
    __set_master_commit("0")


def branch():
    pass


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
    sha1sum_parent = __get_master_commit()
    sha1sum_content = __storedb(__read_file("file.txt"))
    sha1sum_commit = __create_commit(sha1sum_content, [sha1sum_parent], msg)
    __set_master_commit(sha1sum_commit)

    print sha1sum_commit


def __update_working_copy(start_point):
    content_sha1sum = __content_from_commit(start_point)
    content = __getdb(content_sha1sum)
    
    __write_file("file.txt", content)


def checkout(start_point, new_branch):
    start_point = __get_master_commit()
    __update_working_copy(start_point)
        

def diff():
    commit_sha1sum = __get_master_commit()
    content_sha1sum = __content_from_commit(commit_sha1sum)

    orig_content = __getdb(content_sha1sum)
    orig_content = orig_content.splitlines(True)

    curr_content = __read_file("file.txt")
    curr_content = curr_content.splitlines(True)
        
    lines = difflib.unified_diff(orig_content, curr_content, "a/file.txt", "b/file.txt")
    print("".join(lines))


def log():
    commit_sha1sum = __get_master_commit()
    
    while True:
        commit = json.loads(__getdb(commit_sha1sum))
        print commit_sha1sum[:6], commit["log-msg"]
        commit_sha1sum = commit["parent"][0]
        if commit_sha1sum == "0":
            break


def merge(branch):
    pass


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
