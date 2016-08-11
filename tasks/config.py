#!/usr/bin/env python3

import json
import logging
import subprocess
import sys
import toml

from os.path import exists


def load_config(git_branch=''):
    logging.info('INFO: loaded config file: config/config.dist.toml')
    dist = toml.load('config/config.dist.toml')

    if exists('config/config.' + git_branch + '.toml'):
        logging.info('INFO: loaded config file: config/config.' + git_branch + '.toml')
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
            if not (key == 'file_path' and source.get('type', '') == 'sqlite'):
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
