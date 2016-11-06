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
import sys

from ..repo.repository_mod import TaskWrite
from ..repo.task           import StandaloneTask

def cmd_execute(conf, args, repo):
    mod_list = []
    for t in repo.tasks_filter(args.filter):
        t = StandaloneTask(t)
        t.completed = True
        t.date_completed = datetime.datetime.now(datetime.timezone.utc)
        mod_list.append(TaskWrite(t))
    repo.modify(mod_list, 'done ' + ' '.join(args.filter))

def init_parser(subparsers):
    parser = subparsers.add_parser('done')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to show')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}

