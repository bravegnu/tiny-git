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

import docopt


def init():
    pass


def branch():
    pass


def commit(msg):
    pass


def checkout(start_point, new_branch):
    pass


def diff():
    pass


def log():
    pass


def merge(branch):
    pass


def main():
    args = docopt.docopt(__doc__)
    
    print args
    
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
