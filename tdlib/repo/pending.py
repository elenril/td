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

import os

class Pending:

    """path to the pending file"""
    path = None

    ### private ###
    """list of pending tasks UUIDs"""
    _data = None

    def __init__(self, path):
        with open(path, 'r') as pending_file:
            self._data = list(map(str.strip, pending_file.readlines()))

        self.path = path

    def __len__(self):
        return len(self._data)

    def __contains__(self, taskid):
        return taskid in self._data

    def __iter__(self):
        return iter(self._data)

    def __delitem__(self, taskid):
        del self._data[self._data.index(taskid)]
        self._write()

    def add(self, taskid):
        self._data.append(taskid)
        self._write()

    def _write(self):
        tmpname = self.path + '.tmp'
        with open(tmpname, 'wt', newline = '\n') as tmpfile:
            for l in self._data:
                tmpfile.write(l)
                tmpfile.write('\n')
            tmpfile.flush()
            os.fsync(tmpfile.fileno())
        os.replace(tmpname, self.path)
