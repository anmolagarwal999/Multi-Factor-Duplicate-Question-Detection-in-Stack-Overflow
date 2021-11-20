import argparse
import os
import glob
import json
from types import prepare_class
from question import get_question

from preprocess import preprocess

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
    parser.add_argument('--output', '-o', help='Folder with output json', default='output')
    parser.add_argument('--relations', '-r', help='File with dup relations', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if not os.path.isdir(args.data):
        print("no such dir")
        exit(1)
    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    relations = None
    with open(args.relations, 'r') as f:
        relations = json.load(f)
    files = sorted(glob.glob(os.path.join(args.data, '*.json')), key=alphanum_key)
    # print(files)
    i = 0
    p_global = {}
    for file_name in files:
        print(f'Processing {file_name}...')
        raw = None
        with open(file_name) as f:
            raw = json.load(f)
        processed = {}

        for _id, post in raw.items():
            try:
                relation = relations.get(_id, {'ChildOf': [], 'ParentOf': []})
                processed[_id] = {
                    **post,
                    **relation,
                    'isDuplicate': len(relation['ChildOf']) > 0 or len(relation['ParentOf']) > 0
                }
                if processed[_id]['isDuplicate']:
                    p_global[_id] = processed[_id]
            except Exception as err:
                print("Error for id", _id)
                print(err)

        print(f'Processed {file_name}...found {len(processed.values())} questions')
        outfile = os.path.join(args.output, f'{i}.json')
        print(f'Writing to {outfile}')
        with open(outfile, 'w') as f:
            json.dump(processed, f)
        with open(os.path.join(args.output, 'duplicates.json'), 'w') as f:
            json.dump(p_global, f)
        i += 1


if __name__ == '__main__':
    main()
