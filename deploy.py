#!/usr/bin/env python3

try:
    # Python 3 name
    import configparser
except ImportError:
    import ConfigParser as configparser

import argparse
import subprocess
import sys

from shutil import rmtree
from glob import glob


def main(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)

    branch = get_branch(args, config)
    clean_repo = get_clean_repo(args, config)
    must_clean = get_clean(args, config)
    redeploy = get_deploy(args, config)

    if must_clean:
        clean()

    if args.init or (must_clean and redeploy):
        init()

    if (must_clean and redeploy) or not must_clean:
        deploy(args.config_file, branch, clean_repo)


def init():
    cmd = ['python', 'bootstrap.py', '--version', '1.5.2', '--distribute',
        '--download-base', 'http://pypi.camptocamp.net/distribute-0.6.22_fix-issue-227/',
        '--setup-source', 'http://pypi.camptocamp.net/distribute-0.6.22_fix-issue-227/distribute_setup.py'
    ]
    subprocess.call(cmd)


def get_branch(args, config):
    if args.branch:
        return args.branch
    elif config.has_option('deploy', 'branch'):
        return config.get('deploy', 'branch')


def get_clean_repo(args, config):
    if args.clean_repo:
        return args.clean_repo
    elif config.has_option('deploy', 'clean_repo'):
        return config.getboolean('deploy', 'clean_repo')
    else:
        return False


def get_clean(args, config):
    if args.clean:
        return args.clean
    elif config.has_option('deploy', 'clean'):
        return config.getboolean('deploy', 'clean')
    else:
        return False


def get_deploy(args, config):
    if args.deploy:
        return args.deploy
    # If the clean is from config, always deploy
    elif not args.clean and config.has_option('deploy', 'clean'):
        return True
    else:
        return False


def clean():
    try:
        # Used to clean generated files
        subprocess.call(['buildout/bin/buildout', '-c', 'buildout_cleaner.cfg'])
    except OSError:
        print('buildout has not been reinstalled since last clean')
    try:
        # Clean the rest
        rmtree('node_modules')
        rmtree('chsdi.egg-info')
        for file in glob('buildout/*'):
            rmtree(file)
    except OSError:
        print('You must reinit the project before cleaning it')


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
    parser.add_argument('-C', '--clean', help='Remove all downloaded files and folders and all '
        'generated files', dest='clean', action='store_true')
    parser.add_argument('-d', '--deploy', help='Use this flag to deploy after a clean',
        dest='deploy', action='store_true')

    main(parser.parse_args())
