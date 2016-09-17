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

from . import add
from . import delete
from . import done
from . import import_tw
from . import init
from . import modify
from . import show
from . import tags

commands = {
    'add'       : add.cmd,
    'delete'    : delete.cmd,
    'done'      : done.cmd,
    'import_tw' : import_tw.cmd,
    'init'      : init.cmd,
    'modify'    : modify.cmd,
    'show'      : show.cmd,
    'tags'      : tags.cmd
}
