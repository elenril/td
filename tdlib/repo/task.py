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

    def __init__(self, other = None):
        self._data = []

        if other is not None:
            for it in other:
                self.add(it)

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

    def __contains__(self, tag):
        if tag in self._data:
            return True

        taglen = len(tag)

        for tag_other in self._data:
            if (tag_other.startswith(tag) and
                tag_other[taglen] == '.'):
                return True

        return False

    def __str__(self):
        return ' '.join(self._data)

class InvalidDependencyIDError(Exception):
    id      = None

    def __init__(self, id):
        self.id = id

class _Dependencies(_OrderedSet):
    def add(self, dep):
        try:
            uuid.UUID(dep)
            self._data.append(dep)
        except ValueError:
            raise InvalidDependencyIDError(dep)


class _AbstractTask:
    # task UUID as a string
    uuid = None

    # task description
    text = None

    # a set of tags
    tags = None

    # a set of dependencies of this task
    dependencies = None

    # the task has been completed
    completed = None

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

    def __init__(self):
        self.uuid = str(uuid.uuid4())

        self.completed = False

        self.tags         = _Tags()
        self.dependencies = _Dependencies()


class RepositoryTask(_AbstractTask):
    # task short ID (non-negative integer), None if not assigned
    id = None

    # the task depends on at least one other uncompleted task
    blocked = None

    # at least one other task depends on this one
    blocking = None

    # a set of tasks that depend on this one
    dependents = None

    urgency = None

    ### private ###
    "the repository the task is attached to"
    _repo = None

    def __init__(self, repo):
        super().__init__()

        self._repo = repo

        self.dependents = _Dependencies()

        self.blocked  = False
        self.blocking = False


class StandaloneTask(_AbstractTask):
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

    def __init__(self, **kwargs):
        super().__init__()

        if 'parent' in kwargs:
            parent = kwargs['parent']

            self.uuid           = parent.uuid
            self.text           = parent.text
            self.tags           = _Tags(parent.tags)
            self.dependencies   = _Dependencies(parent.dependencies)
            self.completed      = parent.completed
            self.date_created   = parent.date_created
            self.date_completed = parent.date_completed
            self.date_due       = parent.date_due
            self.date_scheduled = parent.date_scheduled
            self.tw_extra       = parent.tw_extra

    @classmethod
    def parse_modifications(cls, mod_desc):
        ret = []

        for it in mod_desc:
            if it.startswith('+'):
                ret.append((cls._MOD_TAG_ADD, it[1:]))
            elif it.startswith('-'):
                ret.append((cls._MOD_TAG_DEL, it[1:]))
            elif not ':' in it:
                ret.append((cls._MOD_TEXT, it))
            else:
                it, val = it.split(':', maxsplit = 1)
                if it == 'text':
                    ret.append((cls._MOD_TEXT, val))
                elif it == 'tag+':
                    ret.append((cls._MOD_TAG_ADD, val))
                elif it == 'tag-':
                    ret.append((cls._MOD_TAG_DEL, val))
                elif it == 'tag':
                    ret.append((cls._MOD_TAG_SET, val.split(',')))
                elif it == 'created':
                    ts = dateutil.parser.parse(val)
                    ret.append((cls._MOD_CREATED, ts))
                elif it == 'due':
                    ts = dateutil.parser.parse(val)
                    ret.append((cls._MOD_DUE, ts))
                elif it == 'scheduled':
                    ts = dateutil.parser.parse(val)
                    ret.append((cls._MOD_SCHEDULED, ts))

        return ret

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
