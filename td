#!/usr/bin/env python3

# Copyright (C) 2016 Anton Khirnov <anton@khirnov.net>
#
# td is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# td is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along
# with td. If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import os.path
import sys
import xdg.BaseDirectory

import tdlib.commands
import tdlib.common_defs
import tdlib.config
import tdlib.repo.repository

CONFIG_OVERRIDE = 'TD_CONFIG'

def _read_config(config_path):
    conf = tdlib.config.Config()

    if config_path != None and os.path.isfile(config_path):
        with open(config_path, 'r') as cf:
            for line in cf:
                line = line.strip()
                if line.startswith('#'):
                    continue

                entry, val = line.split('=', maxsplit = 1)
                conf[entry] = val

    return conf

def main(argv):
    parser = argparse.ArgumentParser(prog = argv[0])

    config_path = None
    config_dir = os.path.join(xdg.BaseDirectory.xdg_config_home, tdlib.common_defs.PROGNAME)
    if config_dir:
        config_path = os.path.join(config_dir, 'config')
    if CONFIG_OVERRIDE in os.environ:
        config_path = os.environ[CONFIG_OVERRIDE]

    parser.add_argument('-c', '--config', default = config_path,
                        help = 'Path to the config file.')

    parser.set_defaults(execute = lambda conf, args, repo, parser = parser: parser.print_usage())

    subparsers = parser.add_subparsers(dest = 'parser')
    for cmd_dict in tdlib.commands.commands.values():
        cmd_dict['init_parser'](subparsers)

    args = parser.parse_args(argv[1:])

    conf = _read_config(args.config)

    repo = None
    if args.parser and tdlib.commands.commands[args.parser]['open_repo']:
        repo = tdlib.repo.repository.Repository(conf['repo_path'])

    args.execute(conf, args, repo)

if __name__ == '__main__':
    main(sys.argv)
