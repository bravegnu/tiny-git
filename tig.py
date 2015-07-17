#!/usr/bin/env python

"""
Usage:
  tig init
  tig commit <msg>
  tig checkout <rev>
  tig diff
  tig log
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
    __write_file(".tig/master", "0")
    __write_file(".tig/head", "0")


def commit(msg):
    master_rev = __read_file(".tig/master")
    head_rev = __read_file(".tig/head")

    if master_rev != head_rev:
        print "tig: not in head revision"
        return

    sha1sum_content = __storedb(__read_file("file.txt"))
    sha1sum_commit = __storedb(json.dumps({
        "content": sha1sum_content,
        "parent": master_rev,        
        "log-msg": msg,
        "author": os.getenv("USER"),
        "time": int(time.time())
    }, indent=4))

    __write_file(".tig/master", sha1sum_commit)
    __write_file(".tig/head", sha1sum_commit)
    print sha1sum_commit


def checkout(rev):
    content_sha1sum = __content_from_commit(rev)
    content = __getdb(content_sha1sum)
    
    __write_file("file.txt", content)
    __write_file(".tig/head", rev)


def diff():
    head_rev = __content_from_commit(__read_file(".tig/head"))

    with open(".tig/objects/{0}".format(head_rev), "r") as orig_file:
        orig_content = orig_file.readlines()
    
    with open("file.txt", "r") as curr_file:
        curr_content = curr_file.readlines()
        
    lines = difflib.unified_diff(orig_content, curr_content, "a/file.txt", "b/file.txt")
    print("".join(lines))


def log():
    commit_sha1sum = __read_file(".tig/head")
    
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
        checkout(args["<rev>"])
    elif args["init"]:
        init()
    elif args["diff"]:
        diff()
    elif args["log"]:
        log()
    else:
        # Not reached
        pass


if __name__ == "__main__":
    main()
