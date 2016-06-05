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


import uuid

class Task:
    # task UUID as a string
    uuid = None

    # a bool indicating whether the task is completed
    completed = None

    # task description
    text = None

    # task creation date, as an aware UTC datetime object
    date_created = None

    def __init__(self):
        self.uuid      = str(uuid.uuid4())
        self.completed = False
