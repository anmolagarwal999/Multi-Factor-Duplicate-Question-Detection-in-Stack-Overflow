import argparse
import os
import glob
import json
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
    args = parser.parse_args()
    return args


DUP_CHECK = re.compile(r'\[\s*duplicate\s*\]', flags=re.IGNORECASE)


def check_duplicate(title):
    return re.search(r'\[\s*duplicate\s*\]', title, flags=re.IGNORECASE) is not None


def main():
    args = parse_args()
    if not os.path.isdir(args.data):
        print("no such dir")
        exit(1)
    if not os.path.isdir(args.output):
        os.mkdir(args.output)

    files = sorted(glob.glob(os.path.join(args.data, '*.json')), key=alphanum_key)
    print(files)
    i = 0
    p_global = {}
    for file_name in files:
        print(f'Processing {file_name}...')
        raw = None
        with open(file_name) as f:
            raw = json.load(f)
        processed = {}
        for obj in raw.values():
            try:
                if obj['PostTypeId'] == '1':
                    q_raw = get_question(obj)
                    # is_duplicate = False
                    if check_duplicate(title=q_raw.title):
                        q = preprocess(obj)
                        processed[q.qid] = q.__dict__
                        p_global[q.qid] = q.__dict__
            except Exception:
                pass
        print(f'Processed {file_name}...found {len(processed.values())} questions')
        outfile = os.path.join(args.output, f'{i}.json')
        print(f'Writing to {outfile}')
        with open(outfile, 'w') as f:
            json.dump(processed, f)
        i += 1

    outfile = os.path.join(args.output, 'duplicates.json')
    with open(outfile, 'w') as f:
        json.dump(p_global, f)


if __name__ == '__main__':
    main()
