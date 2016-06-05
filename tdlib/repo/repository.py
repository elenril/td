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


import collections
import json
import os
import os.path
import pygit2
import shutil

from . import pending
from . import task


SUPPORTED_VERSION = 0


class UnsupportedVersionError(Exception):
    repo_version      = None
    supported_version = None
    def __init__(self, repo_version, supported_version):
        self.repo_version      = repo_version
        self.supported_version = supported_version

class DirtyRepositoryError(Exception):
    pass

class Repository:

    ### private ###
    """path to the repository root"""
    _path = None

    """the underlying git repo"""
    _repo = None

    """repository version"""
    _ver  = None

    """a Pending instance identifying pending tasks"""
    _pending = None

    """Task fields to pack into JSON"""
    _field_maps = ('text',)

    def __init__(self, path):
        self._repo = pygit2.Repository(path)
        for filepath, flags in self._repo.status().items():
            if flags & ~(pygit2.GIT_STATUS_CURRENT | pygit2.GIT_STATUS_IGNORED):
                raise DirtyRepositoryError()

        with open(os.path.join(path, 'version'), 'r') as ver_file:
            self._ver  = int(ver_file.read())
            if self._ver != SUPPORTED_VERSION:
                raise UnsupportedVersionError(self._ver, SUPPORTED_VERSION)

        # create the directories if they do not exist
        # this could happen if they do not contain anything, since git does
        # not track empty dirs
        for d in ('tasks',):
            dirpath = os.path.join(path, d)
            if not os.path.isdir(dirpath):
                os.mkdir(dirpath)

        self._pending = pending.Pending(os.path.join(path, 'pending'))
        self._path    = path

    def _commit_index(self, message):
        parent  = self._repo.head.peel()
        sig = pygit2.Signature('td', 'td@localhost')

        self._repo.index.write()
        tree    = self._repo.index.write_tree()

        self._repo.create_commit('HEAD', sig, sig, message, tree, [parent.hex])

    def _task_pack(self, task):
        data = collections.OrderedDict()
        for fm in self._field_maps:
            val = getattr(task, fm)
            if val is not None:
                data[fm] = val
        return data

    def task_write(self, task):
        path = os.path.join(self._path, 'tasks', task.uuid)
        path_tmp = path + '.tmp'

        with open(path_tmp, 'wt', newline = '\n') as tmpfile:
            data = self._task_pack(task);
            json.dump(data, tmpfile, ensure_ascii = False, indent = 4)
            tmpfile.flush()
            os.fsync(tmpfile.fileno())
        os.replace(path_tmp, path)

        self._repo.index.add(os.path.relpath(path, self._path))

        if task.completed == (task.uuid in self._pending):
            if task.uuid in self._pending:
                del self._pending[task.uuid]
            else:
                self._pending.add(task.uuid)

            self._repo.index.add(os.path.relpath(self._pending.path, self._path))

        self._repo.index.write()
        commit = True
        for filepath, flags in self._repo.status().items():
            if filepath == path and flags & pygit2.GIT_STATUS_INDEX_MODIFIED:
                commit = True
                break
        if commit:
            self._commit_index('Update task %s' % task.uuid)

    def _task_read(self, stuff):
        self._data = json.load(fp, object_pairs_hook = collections.OrderedDict)

        for fm in self._field_maps:
            if fm in self._data:
                setattr(self, fm, self._data[fm])

    def task_open(self, querystr):
        raise NotImplementedError

    def tasks_filter(self, querystr):
        raise NotImplementedError

def init(path):
    """
    Init a new empty td repository at path.
    """
    os.mkdir(path)

    try:
        repo = pygit2.init_repository(path, flags = pygit2.GIT_REPOSITORY_INIT_NO_REINIT)

        with open(os.path.join(path, 'version'), 'x') as ver_file:
            ver_file.write(str(SUPPORTED_VERSION))
            ver_file.flush()
            os.fsync(ver_file.fileno())
        repo.index.add('version')

        with open(os.path.join(path, 'pending'), 'x') as pending_file:
            pass
        repo.index.add('pending')

        sig = pygit2.Signature('td', 'td@localhost')
        repo.index.write()
        tree = repo.index.write_tree()
        repo.create_commit('refs/heads/master', sig, sig, 'Initial commit.', tree, [])
    except:
        shutil.rmtree(path)
        raise

def check(path):
    raise NotImplementedError
