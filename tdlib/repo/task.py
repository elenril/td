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

    def add(self, tag):
        raise NotImplementedError

    def __delitem__(self, task):
        del self._data[task]

    def __contains__(self, task):
        return task in self._data

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

    # task due date (deadline), as an aware UTC datetime object
    date_due     = None

    # task scheduled date, as an aware UTC datetime object
    date_scheduled = None

    tw_extra = None

    def __init__(self):
        self.uuid         = str(uuid.uuid4())
        self.completed    = False
        self.tags         = _Tags()
        self.dependencies = _Dependencies()
