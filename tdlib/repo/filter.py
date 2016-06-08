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

import dateutil.parser
import uuid

class _FilterElement:
    type = None
    val  = None

    def __init__(self, type, val):
        self.type = type

        if (type == TaskFilter._FILTER_UUID or
            type == TaskFilter._FILTER_TEXT or
            type == TaskFilter._FILTER_TAG):
            self.val = val
        elif type == TaskFilter._FILTER_ID:
            self.val = int(val)
        else:
            self.val = dateutil.parser.parse(val)

    def task_match(self, task):
        if self.type == TaskFilter._FILTER_UUID:
            return task.uuid == self.val
        if self.type == TaskFilter._FILTER_ID:
            return task.id == self.val
        if self.type == TaskFilter._FILTER_TEXT:
            return (task.text is not None) and self.val in task.text
        if self.type == TaskFilter._FILTER_TAG:
            if self.val in task.tags:
                return True

            taglen = len(self.val)
            for tag in task.tags:
                if (tag.startswith(self.val) and
                    tag[taglen] == '.'):
                    return True

            return False

        raise NotImplementedError

class TaskFilter:

    # filter types
    _FILTER_UUID      = 0
    _FILTER_ID        = 1
    _FILTER_TEXT      = 2
    _FILTER_CREATED   = 3
    _FILTER_DUE       = 4
    _FILTER_SCHEDULED = 5
    _FILTER_TAG       = 6

    _elems = None

    def __init__(self, filter_expr):
        self._elems = []

        text_match = []

        for word in filter_expr:
            type = None
            val  = None

            if ':' in word:
                prefix, val = word.split(':', maxsplit = 1)

                prefix = prefix.lower()
                if prefix == 'uuid':
                    type = self._FILTER_UUID
                elif prefix == 'id':
                    type = self._FILTER_ID
                elif prefix == 'text':
                    type = self._FILTER_TEXT
                elif prefix == 'created':
                    type = self._FILTER_CREATED
                elif prefix == 'due':
                    type = self._FILTER_DUE
                elif prefix == 'scheduled':
                    type = self._FILTER_SCHEDULED
                elif prefix == 'tag':
                    type = self._FILTER_TAG

            if type is None and word.isdigit():
                type = self._FILTER_ID
                val  = word

            if type is None and word.startswith('+'):
                type = self._FILTER_TAG
                val = word[1:]

            if type is None:
                text_match.append(word)
            else:
                self._elems.append(_FilterElement(type, val))

        if text_match:
            self._elems.append(_FilterElement(self._FILTER_TEXT,
                                              ' '.join(text_match)))

    def task_match(self, task):
        for elem in self._elems:
            if not elem.task_match(task):
                return False
        return True
