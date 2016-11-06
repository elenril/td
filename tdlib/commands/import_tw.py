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
import dateutil.parser
import json
import sys

from ..repo.repository_mod import TaskWrite
from ..repo.task           import StandaloneTask

def cmd_execute(conf, args, repo):
    mod_list = []
    for line in sys.stdin:
        line = line.rstrip('\n,')
        tw_task = json.loads(line)
        td_task = StandaloneTask()

        if 'status' in tw_task and tw_task['status'] == 'deleted':
            continue

        extra = {}
        annotations = []

        for key, val in tw_task.items():
            if (key == 'id' or key == 'urgency'):
                continue
            elif key == 'status':
                if val == 'completed':
                    td_task.completed = True
                elif val == 'pending':
                    td_task.completed = False
                else:
                    print('unknown status %s' % val)
            elif key == 'description':
                td_task.text = val
            elif key == 'uuid':
                td_task.uuid = val
            elif key == 'entry':
                td_task.date_created = dateutil.parser.parse(val)
            elif key == 'end':
                td_task.date_completed = dateutil.parser.parse(val)
            elif key == 'due':
                td_task.date_due = dateutil.parser.parse(val)
            elif key == 'scheduled':
                td_task.date_scheduled = dateutil.parser.parse(val)
            elif key == 'tags':
                for tag in val:
                    td_task.tags.add(tag)
            elif key == 'project':
                td_task.tags.add('projects.%s' % val)
            elif key == 'depends':
                for dep in val.split(','):
                    td_task.dependencies.add(dep)
            elif key == 'annotations':
                for it in val:
                    annotations.append('%s -- %s' % (it['entry'], it['description']))
            else:
                extra[key] = val
        if annotations:
            if td_task.text is None:
                td_task.text = ''

            td_task.text = '\n\n'.join([td_task.text] + annotations)

        if extra:
            td_task.tw_extra = extra
        mod_list.append(TaskWrite(td_task))

    repo.modify(mod_list, 'Import Taskwarrior tasks')

def init_parser(subparsers):
    parser = subparsers.add_parser('import_tw')
    parser.set_defaults(execute = cmd_execute)

    return parser

cmd = {
    'init_parser' : init_parser,
    'open_repo'   : True,
}
