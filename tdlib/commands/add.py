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
import datetime

from ..repo import task
from ..repo.repository_mod import TaskWrite

def cmd_execute(conf, args, repo):
    t = task.Task()

    t.completed = False

    t.date_created = datetime.datetime.now(datetime.timezone.utc)

    if args.args:
        t.modify(t.parse_modifications(args.args))

    repo.modify([TaskWrite(t)], 'add %s' % t.text)

def add_init_parser(subparsers):
    parser = subparsers.add_parser('add')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('args', nargs = argparse.REMAINDER,
                        help = 'New task specification')

    return parser

cmd = {
    'init_parser' : add_init_parser,
    'open_repo'   : True,
}
