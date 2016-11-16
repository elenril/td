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
import sys

from ..repo.repository_mod import TaskDelete

def cmd_execute(conf, args, repo):
    repo_state = repo.load()

    mod_list = []
    for t in repo_state.tasks_filter(args.filter):
        mod_list.append(TaskDelete(t.uuid))

    repo_state.modify(mod_list, 'delete %s' % (' '.join(args.filter)))


def init_parser(config, subparsers):
    parser = subparsers.add_parser('delete')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to delete')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}

