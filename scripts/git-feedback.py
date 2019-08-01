#!/usr/bin/env python3
# Script to push nbgrader html feedback reports to student repos for a given
# assignment in a GitHub classroom course
# Script provided by @jedbrown
# assumes that cwd is nbgrader course dir

import glob
import pandas as pd
import os
import shutil
import subprocess

def read_roster(filename):
    roster = pd.read_csv(args.roster, usecols=('identifier', 'github_username')).set_index('identifier')
    return roster

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--roster', help='CSV roster file', default='roster.csv')
    parser.add_argument('--assignment', help='Name of assignment, e.g., hw1-rootfinding', required=True)
    parser.add_argument('-n', '--dry-run', help='Print git statements but do not run', action='store_true')
    args = parser.parse_args()

    assignment = args.assignment

    roster = read_roster(args.roster)
    for identikey, (github_username,) in roster.iterrows():
        try:
            (source,) = glob.glob(os.path.join('feedback', identikey, assignment, '*.html'))
        except ValueError: # Lack of feedback usually means student did not submit homework
            print(f'No feedback for {identikey}')
            continue

        destdir = os.path.join('submitted', github_username, assignment)
        dest = os.path.join(destdir, 'feedback.html')
        if os.path.exists(destdir):
            print("Copying feedback from {} to {}".format(source,destdir))
            shutil.copyfile(source, dest)
        else:
            print('Destination directory does not exist: {}'.format(destdir))
        git = ['git', '-C', destdir]

        if (args.dry_run):
            print("{} add {}".format(git,os.path.basename(dest)))
            print("{} commit -m \"Add feedback\"".format(git))
            print("{} push".format(git))
        else:
            try:
                subprocess.check_call(git + ['add', os.path.basename(dest)])
                subprocess.check_call(git + ['commit', '-mAdd feedback'])
                subprocess.check_call(git + ['push'])
            except subprocess.CalledProcessError:
                print('Skipping {}'.format(destdir))
