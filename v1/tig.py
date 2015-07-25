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


def __set_master_commit(commit_sha1sum):
    __write_file(".tig/master", commit_sha1sum)


def __get_master_commit():
    return __read_file(".tig/master")


def init():
    os.makedirs(".tig/objects")
    
    __set_master_commit("0")


def branch():
    pass


def commit(msg):
    sha1sum_content = __storedb(__read_file("file.txt"))
    __set_master_commit(sha1sum_content)

    print sha1sum_content


def __update_working_copy(start_point):
    content = __getdb(start_point)
    
    __write_file("file.txt", content)


def checkout(start_point, new_branch):
    start_point = __get_master_commit()
    __update_working_copy(start_point)
        

def diff():
    content_sha1sum = __get_master_commit()
    orig_content = __getdb(content_sha1sum)
    orig_content = orig_content.splitlines(True)

    curr_content = __read_file("file.txt")
    curr_content = curr_content.splitlines(True)
        
    lines = difflib.unified_diff(orig_content, curr_content, "a/file.txt", "b/file.txt")
    print("".join(lines))


def log():
    pass


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
