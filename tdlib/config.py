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

import os.path
import xdg.BaseDirectory

from . import common_defs

_config_defaults = {
    'repo_path' : os.path.join(xdg.BaseDirectory.xdg_data_home, common_defs.PROGNAME),
}

class InvalidConfigItem(Exception):
    pass

class _ConfigSection:
    _data = None

    def __init__(self, defaults):
        self._data = {}

        for key, val in defaults.items():
            if isinstance(val, dict):
                self._data[key] = _ConfigSection(val)
            else:
                self._data[key] = val

    def __getitem__(self, key):
        remainder = None
        if '.' in key:
            key, remainder = key.split('.', maxsplit = 1)

        if not key in self._data:
            raise InvalidConfigItem('No such config item: %s' % key)

        val = self._data[key]
        if remainder != None:
            if not isinstance(val, _ConfigSection):
                raise InvalidConfigItem('Attempted to get "%s", but "%s" is not a section' % ('.'.join(key, remainder), key))
            return val[remainder]
        return val

    def __setitem__(self, key, val):
        remainder = None
        if '.' in key:
            key, remainder = key.split('.', maxsplit = 1)

        if not key in self._data:
            raise InvalidConfigItem('No such config item: %s' % key)

        if remainder != None:
            if not isinstance(val, _ConfigSection):
                raise InvalidConfigItem('Attempted to set "%s", but "%s" is not a section' % ('.'.join(key, remainder), key))
            self._data[key][remainder] = val
        else:
            if isinstance(self._data[key], _ConfigSection):
                raise InvalidConfigItem('Key "%s" refers to a config section, not a single item' % key)
            self._data[key] = val

class Config(_ConfigSection):
    def __init__(self):
        super().__init__(_config_defaults)
