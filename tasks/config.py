#!/usr/bin/env python3

import json
import subprocess
import sys
import toml

from os.path import exists


def load_config(git_branch=''):
    dist = toml.load('config/config.dist.toml')
    if exists('config/config.toml'):
        conf = toml.load('config/config.toml')
        update(dist, conf)

    if exists('config/config.' + git_branch + '.toml'):
        conf = toml.load('config/config.' + git_branch + '.toml')
        update(dist, conf)

    return dist


def get_git_branch():
    return subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=subprocess.PIPE)\
        .stdout\
        .read()\
        .decode('utf-8')\
        .strip()


def update(dest, source):
    for key, value in source.items():
        if key not in dest:
            print('WARNING: Key {} not in dest'.format(key), file=sys.stderr)
        if isinstance(value, dict):
            update(dest.setdefault(key), value)
        else:
            dest[key] = value


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        git_branch = sys.argv[1]
    config = load_config(git_branch)
    print(json.dumps(config))
