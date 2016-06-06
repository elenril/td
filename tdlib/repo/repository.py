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
import datetime
import json
import os
import os.path
import pygit2
import shutil
import uuid

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

    """a dict of { task uuid : short id }"""
    _ids = None

    """List of entries for the current commit"""
    _commit_msgs = None

    """Task fields to pack into JSON"""
    _field_maps = ('text',)
    _date_fields = ('date_created', 'date_due', 'date_scheduled')

    def __init__(self, path):
        self._path = path

        self._repo = pygit2.Repository(path)
        for filepath, flags in self._repo.status().items():
            if flags & ~(pygit2.GIT_STATUS_CURRENT | pygit2.GIT_STATUS_IGNORED):
                raise DirtyRepositoryError()

        with open(os.path.join(path, 'version'), 'r') as ver_file:
            self._ver  = int(ver_file.read())
            if self._ver != SUPPORTED_VERSION:
                raise UnsupportedVersionError(self._ver, SUPPORTED_VERSION)

        self._load_short_ids()

        # create the directories if they do not exist
        # this could happen if they do not contain anything, since git does
        # not track empty dirs
        for d in ('tasks',):
            dirpath = os.path.join(path, d)
            if not os.path.isdir(dirpath):
                os.mkdir(dirpath)

        self._pending     = pending.Pending(os.path.join(path, 'pending'))
        self._commit_msgs = []

    def __del__(self):
        self.commit_changes()

    def _load_short_ids(self):
        with open(os.path.join(self._path, 'ids'), 'r') as ids_file:
            self._ids = {}
            i = 0
            for line in ids_file:
                uuid = line.strip()
                self._ids[uuid] = i
                i += 1

    def _commit_index(self, message):
        parent  = self._repo.head.peel()
        sig = pygit2.Signature('td', 'td@localhost')

        self._repo.index.write()
        tree    = self._repo.index.write_tree()

        self._repo.create_commit('HEAD', sig, sig, message, tree, [parent.hex])

    def _task_pack(self, t):
        data = collections.OrderedDict()
        for fm in self._field_maps:
            val = getattr(t, fm)
            if val is not None:
                data[fm] = val

        for d in self._date_fields:
            val = getattr(t, d)
            if val is not None:
                data[d] = int(val.timestamp())

        return data

    def commit_changes(self, msg_title = 'Untitled commit'):
        commit = False
        for filepath, flags in self._repo.status().items():
            if flags & pygit2.GIT_STATUS_INDEX_MODIFIED:
                commit = True
                break
        if commit:
            commit_msg = msg_title + '\n\n' + '\n'.join(self._commit_msgs)
            self._commit_index(commit_msg)
            self._commit_msgs = []

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

                with open(os.path.join(self._path, 'ids'), 'ta', newline = '\n') as ids_file:
                    ids_file.write('%s\n' % task.uuid)
                    ids_file.flush()
                    os.fsync(ids_file.fileno())
                    self._repo.index.add('ids')

            self._repo.index.add(os.path.relpath(self._pending.path, self._path))

        self._repo.index.write()
        self._commit_msgs.append('Update task %s' % task.uuid)

    def task_delete(self, task_uuid):
        task_path = os.path.join(self._path, 'tasks', task_uuid)
        if not os.path.isfile(task_path):
            raise KeyError

        os.remove(task_path)
        self._repo.index.remove(os.path.join('tasks', task_uuid))

        if task_uuid in self._pending:
            del self._pending[task_uuid]
            self._repo.index.add(os.path.relpath(self._pending.path, self._path))

        self._repo.index.write()
        self._commit_msgs.append('Delete task %s' % task_uuid)

    def _task_list(self):
        ret = []
        for f in os.listdir(os.path.join(self._path, 'tasks')):
            try:
                u = uuid.UUID(f)
                ret.append(f)
            except ValueError:
                pass
        return ret

    def _task_load(self, task_uuid):
        t = task.Task()

        with open(os.path.join(self._path, 'tasks', task_uuid), 'rt') as task_fp:
            data = json.load(task_fp)

            for fm in self._field_maps:
                if fm in data:
                    setattr(t, fm, data[fm])

            for d in self._date_fields:
                if d in data:
                    val = datetime.datetime.fromtimestamp(data[d],
                                                          datetime.timezone.utc)
                    setattr(t, d, val)

        t.uuid      = task_uuid
        t.completed = not task_uuid in self._pending

        if task_uuid in self._ids:
            t.id = self._ids[task_uuid]

        return t

    def _task_match(self, t, querystr):
        if t.text and querystr in t.text:
            return True

        return False

    def tasks_filter(self, querystr):
        ret = []
        for task_uuid in self._pending:
            t = self._task_load(task_uuid)
            if self._task_match(t, querystr):
                ret.append(t)
        return ret

    def update_ids(self):
        shutil.copy2(self._pending.path, os.path.join(self._path, 'ids'))
        self._repo.index.add('ids')
        self._repo.index.write()
        self._commit_msgs.append('Update short IDs')

        self._load_short_ids()

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

        with open(os.path.join(path, 'ids'), 'x') as ids_file:
            pass
        repo.index.add('ids')

        sig = pygit2.Signature('td', 'td@localhost')
        repo.index.write()
        tree = repo.index.write_tree()
        repo.create_commit('refs/heads/master', sig, sig, 'Initial commit.', tree, [])
    except:
        shutil.rmtree(path)
        raise

def check(path):
    raise NotImplementedError
