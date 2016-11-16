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

def cmd_execute(conf, args, repo):
    repo.update_ids()

    repo = Repository(repo.path)

    for t in repo.tasks_filter(args.filter):
        task_formatted = []

        task_formatted.append(('UUID', (t.uuid,)))

        if t.id is not None:
            task_formatted.append(('ID', (str(t.id),)))

        if t.completed:
            status = 'completed'
        else:
            status = 'pending'
            if t.blocked:
                status += ' blocked'

        task_formatted.append(('Status', (status,)))

        if t.text:
            task_formatted.append(('Text', t.text.split('\n')))

        if t.date_created:
            created_localts = t.date_created.astimezone()
            task_formatted.append(('Created', (created_localts.isoformat(),)))

        if t.date_completed:
            completed_localts = t.date_completed.astimezone()
            task_formatted.append(('Completed', (completed_localts.isoformat(),)))

        if t.date_due:
            due_localts = t.date_due.astimezone()
            task_formatted.append(('Due', (due_localts.isoformat(),)))

        if t.date_scheduled:
            scheduled_localts = t.date_scheduled.astimezone()
            task_formatted.append(('Scheduled', (scheduled_localts.isoformat(),)))

        if len(t.tags):
            task_formatted.append(('Tags', (' '.join(t.tags),)))

        if len(t.dependencies):
            deps = []
            for dep in t.dependencies:
                try:
                    dep_task = repo.tasks_filter(['uuid:%s' % dep])[0]
                    dep_desc = str(dep_task.id)
                    if dep_task.text is not None:
                        dep_desc += ' %s' % (dep_task.text.split('\n')[0])
                    deps.append(dep_desc)
                except IndexError:
                    deps.append(dep)
            task_formatted.append(('This task depends on', deps))

        if len(t.dependents):
            deps = []
            for dep in t.dependents:
                try:
                    dep_task = repo.tasks_filter(['uuid:%s' % dep])[0]
                    dep_desc = str(dep_task.id)
                    if dep_task.text is not None:
                        dep_desc += ' %s' % (dep_task.text.split('\n')[0])
                    deps.append(dep_desc)
                except IndexError:
                    deps.append(dep)
            task_formatted.append(('This task is blocking', deps))

        # compute the required column width
        maxw = 0
        for key, val in task_formatted:
            maxw = max(maxw, len(key))

        for key, lines in task_formatted:
            for i in range(len(lines)):
                if i == 0:
                    sys.stdout.write('%s%s' % (key,  ' ' * (maxw - len(key))))
                else:
                    sys.stdout.write(' ' * maxw)
                sys.stdout.write(' | %s\n' % lines[i])

        sys.stdout.write('=' * 80 + '\n')


def init_parser(config, subparsers):
    parser = subparsers.add_parser('show')
    parser.set_defaults(execute = cmd_execute)

    parser.add_argument('filter', nargs = argparse.REMAINDER,
                        help = 'Tasks to show')

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}
