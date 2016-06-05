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

class Config:

    """Path to the repository root"""
    repo_path = None

    def __init__(self, configfile):
        self.repo_path = os.path.join(xdg.BaseDirectory.xdg_data_home, common_defs.PROGNAME)

        if configfile:
            raise NotImplementedError
