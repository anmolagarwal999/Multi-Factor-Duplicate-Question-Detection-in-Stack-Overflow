import argparse
import os
import glob
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
    parser.add_argument('--data', '-d', help='Folder with json files', required=True)
    # parser.add_argument('--output', '-o', help='Folder with output json', default='output')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if not os.path.isdir(args.data):
        print("no such dir")
        exit(1)
    db = Database()
    db.refresh_questions()
    files = sorted(glob.glob(os.path.join(args.data, '*.json')), key=alphanum_key)
    print(files)
    for file_name in files:
        print(f'Processing {file_name}...')
        raw = None
        with open(file_name) as f:
            raw = json.load(f)
        db.add_questions(list(raw.values()))

    db.conn.close()


if __name__ == '__main__':
    main()
