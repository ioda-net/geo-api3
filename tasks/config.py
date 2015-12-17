#!/usr/bin/env python3

import json
import sys
import toml

from os.path import exists


def load_config():
    dist = toml.load('config/config.dist.toml')
    if exists('config/config.toml'):
        conf = toml.load('config/config.toml')

        update(dist, conf)

    return dist


def update(dest, source):
    for key, value in source.items():
        if key not in dest:
            print('WARNING: Key {} not in dest'.format(key), file=sys.stderr)
        if isinstance(value, dict):
            update(dest.setdefault(key), value)
        else:
            dest[key] = value


if __name__ == '__main__':
    config = load_config()
    print(json.dumps(config))
