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

class _ConfigSectionTemplate:
    """A dict/section of defaults used for any child elements"""
    child_defaults   = None
    """
    A dict of children created by default (possibly overriding the
    defaults from child_defaults
    """
    default_children = None

    def __init__(self, child_defaults, default_children):
        self.child_defaults   = child_defaults
        self.default_children = default_children

_config_defaults = {
    'repo_path' : os.path.join(xdg.BaseDirectory.xdg_data_home, common_defs.PROGNAME),

    'colors' : {
        'alternate_bg' : 'bright_black',
    },

    'reports' : _ConfigSectionTemplate(
        {
            'description' : '',
            'filter'      : '',
            'columns'     : 'id ID|tags Tags|urgency Urgency|text Description',
            'sort'        : 'id+',
        },
        {
            'list.description'  : 'All pending tasks, sorted by short ID.',

            'ready.description' : 'Tasks ready to be worked upon, sorted by urgency',
            'ready.filter'      : 'not flag:blocked',
            'ready.sort'        : 'urgency-',

            'next.description'  : 'Most pressing tasks currently available',
            'next.filter'      : 'not flag:blocked and urgency.above:0.0',
            'next.sort'        : 'urgency-',
        },
    ),
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
            elif isinstance(val, _ConfigSectionTemplate):
                self._data[key] = _ConfigSectionTemplated(val.child_defaults)
                for child, childval in val.default_children.items():
                    self._data[key][child] = childval
            elif val is None:
                self._data[key] = {}
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
            if (not isinstance(self._data[key], _ConfigSection) and
                not isinstance(self._data[key], dict)):
                raise InvalidConfigItem('Attempted to set "%s", but "%s" is not a section' % ('.'.join((key, remainder)), key))
            self._data[key][remainder] = val
        else:
            if isinstance(self._data[key], _ConfigSection):
                raise InvalidConfigItem('Key "%s" refers to a config section, not a single item' % key)
            self._data[key] = val

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return repr(self._data)

class _ConfigSectionTemplated(_ConfigSection):
    _defaults_template = None

    def __init__(self, defaults_template):
        super().__init__({})
        self._defaults_template = defaults_template

    def __setitem__(self, key, val):
        if not '.' in key:
            raise InvalidConfigItem('Attemted to assign directly to "%s", '
                                    'but "%s" is a templated section' % (key, key))
        key, remainder = key.split('.', maxsplit = 1)

        if not key in self._data:
            tmp = _ConfigSection(self._defaults_template)
            tmp[remainder] = val
            self._data[key] = tmp
        else:
            self._data[key][remainder] = val

class Config(_ConfigSection):
    def __init__(self):
        super().__init__(_config_defaults)
