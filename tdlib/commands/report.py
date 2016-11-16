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

from ..repo.repository import Repository
from ..utils import report_print

def _cmd_execute(conf, args, repo, report):
    repo.update_ids()

    repo = Repository(repo.path)

    rc = conf['reports'][report]

    columns = [('id', 'ID'), ('tags', 'Tags'), ('urgency', 'Urgency'), ('text', 'Description')]

    if len(rc['filter']) > 0 and len(args.filter) > 0:
        filter = ['('] + args.filter + [')', 'and', '('] + rc['filter'].split() + [')']
    elif len(rc['filter']) > 0:
        filter = rc['filter'].split()
    elif len(args.filter) > 0:
        filter = args.filter
    else:
        filter = ''

    tasks = list(repo.tasks_filter(filter))

    report_print.report_print(conf, sys.stdout, tasks, columns, rc['sort'], ' ')

class _ReportExecuteWrapper:
    _report = None
    def __init__(self, report):
        self._report = report
    def __call__(self, *args, **kwargs):
        _cmd_execute(*args, **kwargs, report = self._report)

def init_parser(config, subparsers):
    for report in config['reports']:
        parser = subparsers.add_parser(report)
        parser.set_defaults(execute = _ReportExecuteWrapper(report))
        parser.add_argument('filter', nargs = argparse.REMAINDER,
                            help = 'Tasks to show')

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}
