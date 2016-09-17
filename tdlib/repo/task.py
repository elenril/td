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


import string
import uuid
import unicodedata

class InvalidTagNameError(Exception):
    tag      = None
    charname = None

    def __init__(self, tag, charname):
        self.tag      = tag
        self.charname = charname

class _OrderedSet:
    _data = None

    def __init__(self):
        self._data = []

    def add(self, item):
        raise NotImplementedError

    def __delitem__(self, item):
        del self._data[self._data.index(item)]

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

class _Tags(_OrderedSet):
    def add(self, tag):
        for char in string.whitespace:
            if char in tag:
                charname = unicodedata.name(char, "Unknown character name")
                raise InvalidTagNameError(tag, '\'%s\' (%s)' % (char, charname))

        if not tag in self._data:
            self._data.append(tag)

    def __str__(self):
        return ' '.join(self._data)

class InvalidDependecyIDError(Exception):
    id      = None

    def __init__(self, id):
        self.id = id

class _Dependencies(_OrderedSet):
    def add(self, dep):
        try:
            uuid.UUID(dep)
            self._data.append(dep)
        except ValueError:
            raise InvalidDependecyIDError(dep)

class Task:
    # task UUID as a string
    uuid = None

    # task short ID (non-negative integer), None of not assigned
    id = None

    # a bool indicating whether the task is completed
    completed = None

    # task description
    text = None

    # a set of tags
    tags = None

    # a set of dependencies of this task
    dependencies = None

    # task creation date, as an aware UTC datetime object
    date_created = None

    # task completion date, as an aware UTC datetime object
    # None if completed is False
    date_completed = None

    # task due date (deadline), as an aware UTC datetime object
    date_due     = None

    # task scheduled date, as an aware UTC datetime object
    date_scheduled = None

    tw_extra = None

    ### private ###
    _MOD_TEXT      = 0
    _MOD_TAG_ADD   = 1
    _MOD_TAG_DEL   = 2
    _MOD_TAG_SET   = 3
    #_MOD_DEP_ADD   = 4 TODO
    #_MOD_DEP_DEL   = 5
    _MOD_CREATED   = 6
    _MOD_COMPLETED = 7
    _MOD_DUE       = 8
    _MOD_SCHEDULED = 9

    def __init__(self):
        self.uuid         = str(uuid.uuid4())

        self.completed    = False
        self.blocked      = False
        self.blocking     = False

        self.tags         = _Tags()
        self.dependencies = _Dependencies()

    def modify(self, mod_desc):
        for it, val in mod_desc:
            if it == self._MOD_TEXT:
                self.text = val
            elif it == self._MOD_TAG_ADD:
                self.tags.add(val)
            elif it == self._MOD_TAG_DEL:
                if val in self.tags:
                    del self.tags[val]
            elif it == self._MOD_TAG_SET:
                self.tags = _Tags()
                for tag in val:
                    self.tags.add(tag)
            elif it == self._MOD_CREATED:
                self.date_created = val
            elif it == self._MOD_COMPLETED:
                self.date_completed = val
            elif it == self._MOD_DUE:
                self.date_due = val
            elif it == self._MOD_SCHEDULED:
                self.date_scheduled = val
            else:
                raise ValueError('Invalid modification code: %d' % it)

    @property
    def urgency(self):
        return 0.0

    @staticmethod
    def parse_modifications(mod_desc):
        ret = []

        for it in mod_desc:
            if it.startswith('+'):
                ret.append((Task._MOD_TAG_ADD, it[1:]))
            elif it.startswith('-'):
                ret.append((Task._MOD_TAG_DEL, it[1:]))
            elif not ':' in it:
                ret.append((Task._MOD_TEXT, it))
            else:
                it, val = it.split(':', maxsplit = 1)
                if it == 'text':
                    ret.append((Task._MOD_TEXT, val))
                elif it == 'tag+':
                    ret.append((Task._MOD_TAG_ADD, val))
                elif it == 'tag-':
                    ret.append((Task._MOD_TAG_DEL, val))
                elif it == 'tag':
                    ret.append((Task._MOD_TAG_SET, val.split(',')))
                elif it == 'created':
                    ts = dateutil.parser.parse(val)
                    ret.append((Task._MOD_CREATED, ts))
                elif it == 'due':
                    ts = dateutil.parser.parse(val)
                    ret.append((Task._MOD_DUE, ts))
                elif it == 'scheduled':
                    ts = dateutil.parser.parse(val)
                    ret.append((Task._MOD_SCHEDULED, ts))

        return ret
