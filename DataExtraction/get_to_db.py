"""
:brief: Script to read data from database and save to json file
"""

import argparse
import os
import json
from db import Database

import re


def tryint(s):
    try:
        return int(s)
    except BaseException:
        return s


def alphanum_key(s):
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def sort_nicely(l):
    l.sort(key=alphanum_key)


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument('--data', '-d', help='Folder with json files', required=True)
    parser.add_argument('--output', '-o', help='Folder with output json', default='output')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    db = Database()
    posts = 275395
    n_file = 30
    n_docs = posts // n_file
    j = 0
    for i in range(0, posts, n_docs):
        questions = db.get_questions(i, n_docs)
        outfile = os.path.join(args.output, f'{j}.json')
        with open(outfile, 'w') as f:
            json.dump(questions, f)
        j += 1

    db.conn.close()


if __name__ == '__main__':
    main()
