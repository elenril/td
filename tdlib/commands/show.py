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

def cmd_execute(conf, args, repo):
    for t in repo.tasks_filter(' '.join(args.filter)):
        sys.stdout.write('UUID:\t%s\n' % t.uuid)

        sys.stdout.write('Status:\t%s\n' % ('completed' if t.completed else 'pending'))

        if t.text:
            sys.stdout.write('Text:\t%s\n' % t.text)

        if t.date_created:
            created_localts = t.date_created.astimezone()
            sys.stdout.write('Created:\t%s\n' % created_localts.isoformat())

        if t.date_due:
            due_localts = t.date_due.astimezone()
            sys.stdout.write('Due:\t%s\n' % due_localts.isoformat())

        if t.date_scheduled:
            scheduled_localts = t.date_scheduled.astimezone()
            sys.stdout.write('Scheduled:\t%s\n' % scheduled_localts.isoformat())


def init_parser(subparsers):
    parser = subparsers.add_parser('show')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to show')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}
