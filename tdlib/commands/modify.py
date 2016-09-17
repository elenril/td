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

from ..repo import task

def cmd_execute(conf, args, repo):
    if not '--' in args.filter:
        raise ValueError('The filter and the modifier need to be separated by "--"')

    sep_idx = args.filter.index('--')
    filter_expr = args.filter[:sep_idx]
    mod_expr    = args.filter[sep_idx + 1:]
    mod         = task.Task.parse_modifications(mod_expr)

    for t in repo.tasks_filter(filter_expr):
        t.modify(mod)
        repo.task_write(t)

    repo.commit_changes('modify %s' % args.filter)


def init_parser(subparsers):
    parser = subparsers.add_parser('modify')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to show')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}