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

from ..utils import report_print

def cmd_execute(conf, args, repo):
    repo.update_ids()
    repo.commit_changes('Update short ids')

    columns = [('id', 'ID'), ('tags', 'Tags'), ('urgency', 'Urgency'), ('text', 'Description')]

    tasks = list(repo.tasks_filter(args.filter))
    report_print.report_print(sys.stdout, tasks, columns, 'id', ' ')

def init_parser(subparsers):
    parser = subparsers.add_parser('list')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to show')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}
