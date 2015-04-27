#!/usr/bin/env python3

try:
    # Python 3 name
    import configparser
except ImportError:
    import ConfigParser as configparser

import argparse
import subprocess
import sys


def main(args):
    if args.init:
        init()

    config = configparser.ConfigParser()
    config.read(args.config_file)

    branch = get_branch(args, config)
    clean_repo = get_clean_repo(args, config)

    deploy(args.config_file, branch, clean_repo)


def init():
    cmd = ['python', 'bootstrap.py', '--version', '1.5.2', '--distribute',
        '--download-base', 'http://pypi.camptocamp.net/distribute-0.6.22_fix-issue-227/',
        '--setup-source', 'http://pypi.camptocamp.net/distribute-0.6.22_fix-issue-227/distribute_setup.py'
    ]
    subprocess.call(cmd)


def get_branch(args, config):
    if args.branch is not None:
        return args.branch
    elif config.has_option('deploy', 'branch'):
        return config.get('deploy', 'branch')


def get_clean_repo(args, config):
    if args.clean_repo is not None:
        return args.clean_repo
    elif config.has_option('deploy', 'clean_repo'):
        return config.getboolean('deploy', 'clean_repo')
    else:
        return False


def deploy(config_file, branch, clean_repo):
    git_output = subprocess.Popen(["git", "status", "--porcelain"], stdout=subprocess.PIPE)\
                    .communicate()[0]
    if clean_repo and git_output:
        print('You specified that you want to deploy from a clean repo. Please commit or stash your '
            'changes')
        sys.exit(1)

    if branch:
        subprocess.Popen(['git', 'checkout', branch]).communicate()

    subprocess.call(['buildout/bin/buildout', '-c', config_file])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy geo-api3. All values passed as arguments '
        'override those from the configuration')
    parser.add_argument('-i', '--init', help='Initialize buildout', dest='init', action='store_true',
        default=False)
    parser.add_argument('-c', '--config', help='Config file to use', default='buildout_config.cfg',
        dest='config_file')
    parser.add_argument('-b', '--branch', help='Deploy the specified branch',
        dest='branch')
    parser.add_argument('--clean-repo', help='If the working directory is not clean, exit',
        dest='clean_repo', action='store_true')

    main(parser.parse_args())
