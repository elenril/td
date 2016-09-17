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

from ..repo import repository

def cmd_execute(conf, args, repo):
    repository.init(conf['repo_path'])

def cmd_init_parser(subparsers):
    parser = subparsers.add_parser('init')
    parser.set_defaults(execute = cmd_execute)

    return parser

cmd = {
    'init_parser' : cmd_init_parser,
    'open_repo'   : False,
}
