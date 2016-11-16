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

import dateutil.parser
import uuid

class _FilterTerm:
    _type = None
    _val  = None
    _mod  = None

    # filter types
    _FILTER_UUID      = 0
    _FILTER_ID        = 1
    _FILTER_TEXT      = 2
    _FILTER_CREATED   = 3
    _FILTER_DUE       = 4
    _FILTER_SCHEDULED = 5
    _FILTER_TAG       = 6
    _FILTER_BLOCKED   = 7
    _FILTER_BLOCKING  = 8
    _FILTER_URGENCY   = 9

    # filter modifiers
    _MOD_ABOVE = 0
    _MOD_BELOW = 1

    def __init__(self, term):
        type = None
        val  = None

        if ':' in term:
            prefix, val = term.split(':', maxsplit = 1)

            prefix = prefix.lower()
            if prefix == 'uuid':
                type = self._FILTER_UUID
            elif prefix == 'id':
                type = self._FILTER_ID
                val  = (int(val),)
            elif prefix == 'text':
                type = self._FILTER_TEXT
            elif prefix == 'created':
                type = self._FILTER_CREATED
            elif prefix == 'due':
                type = self._FILTER_DUE
            elif prefix == 'scheduled':
                type = self._FILTER_SCHEDULED
            elif prefix == 'tag':
                type = self._FILTER_TAG
                val  = (val,)
            elif prefix == 'flag':
                if val == 'blocked':
                    type = self._FILTER_BLOCKED
                elif val == 'blocking':
                    type = self._FILTER_BLOCKING
                else:
                    raise ValueError('Unknown flag: %s' % val)
            elif prefix.startswith('urgency'):
                type = self._FILTER_URGENCY
                if prefix == 'urgency.below':
                    self._mod = self._MOD_BELOW
                elif prefix == 'urgency.above':
                    self._mod = self._MOD_ABOVE
                else:
                    raise ValueError('Unknown urgency modifier: %s' % prefix)

        if type is None:
            try:
                val = list(map(int, term.split(',')))
                type = self._FILTER_ID
            except ValueError:
                pass

        if type is None and term.startswith('+'):
            type = self._FILTER_TAG
            val = term[1:].split(',')

        if type is None:
            type = self._FILTER_TEXT
            val  = term

        self._type = type

        if (type == self._FILTER_UUID or
            type == self._FILTER_TEXT):
            self._val = val
        elif (type == self._FILTER_TAG or
              type == self._FILTER_ID):
            self._val = set(val)
        elif (type == self._FILTER_BLOCKED or
              type == self._FILTER_BLOCKING):
            pass
        elif (type == self._FILTER_URGENCY):
            self._val = float(val)
        else:
            self._val = dateutil.parser.parse(val)

    def task_match(self, task):
        if self._type == self._FILTER_UUID:
            return task.uuid == self._val
        if self._type == self._FILTER_ID:
            return task.id in self._val
        if self._type == self._FILTER_TEXT:
            return (task.text is not None) and self._val in task.text
        if self._type == self._FILTER_BLOCKED:
            return task.blocked
        if self._type == self._FILTER_BLOCKING:
            return task.blocking
        if self._type == self._FILTER_URGENCY:
            if self._mod == self._MOD_ABOVE:
                return task.urgency >= self._val
            elif self._mod == self._MOD_BELOW:
                return task.urgency <= self._val
        if self._type == self._FILTER_TAG:
            for tag in self._val:
                if tag in task.tags:
                    return True

                taglen = len(tag)
                for tag_other in task.tags:
                    if (tag_other.startswith(tag) and
                        tag[taglen] == '.'):
                        return True

            return False

        raise NotImplementedError

class FilterSyntaxError(Exception):
    pass

# the following is based on http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#shunting_yard

class _Tree:
    _operator = None
    _op0      = None
    _op1      = None

    def __init__(self, operator, op0, op1 = None):
        self._operator = operator
        self._op0      = op0
        self._op1      = op1

    def __repr__(self):
        if self._op1 != None:
            return '%s(%s, %s)' % (self._operator, self._op0, self._op1)
        return '%s(%s)' % (self._operator, self._op0)

    def task_match(self, task):
        if self._operator == 'and':
            return self._op0.task_match(task) and self._op1.task_match(task)
        elif self._operator == 'or':
            return self._op0.task_match(task) or self._op1.task_match(task)
        elif self._operator == 'not':
            return not self._op0.task_match(task)

_unary_operators = ('not',)
_binary_operators = ('or', 'and')

def _gt(arg0, arg1):
    if arg0 in _binary_operators and arg1 in _binary_operators:
        idx0 = _binary_operators.index(arg0)
        idx1 = _binary_operators.index(arg1)
        return idx0 >= idx1
    elif arg0 in _unary_operators and arg1 in _binary_operators:
        return True
    elif arg1 in _unary_operators:
        return False
    raise ValueError

def _next(query):
    idx = query[1]
    if idx >= len(query[0]):
        return None
    return query[0][idx]

def _consume(query):
    query[1] += 1

def _pop_operator(operator_stack, tree_stack):
    op = operator_stack.pop()
    if op in _binary_operators:
        arg1 = tree_stack.pop()
        arg0 = tree_stack.pop()
        tree_stack.append(_Tree(op, arg0, arg1))
    else:
        arg0 = tree_stack.pop()
        tree_stack.append(_Tree(op, arg0))

def _push_operator(op, operator_stack, tree_stack):
    while len(operator_stack) and _gt(operator_stack[-1], op):
        _pop_operator(operator_stack, tree_stack)
    operator_stack.append(op)

def _p(query, operator_stack, tree_stack):
    n = _next(query)
    if n == '(':
        _consume(query)

        op_stack1, tree_stack1 = [], []
        _e(query, op_stack1, tree_stack1)
        n = _next(query)
        if n != ')':
            raise FilterSyntaxError('Missing ")"')
        _consume(query)

        tree_stack.append(tree_stack1.pop())
    elif n in _unary_operators:
        _push_operator(n, operator_stack, tree_stack)
        _consume(query)
        _p(query, operator_stack, tree_stack)
    else:
        tree_stack.append(_FilterTerm(n))
        _consume(query)

def _e(query, operator_stack, tree_stack):
    _p(query, operator_stack, tree_stack)
    while _next(query) in _binary_operators:
        _push_operator(_next(query), operator_stack, tree_stack)
        _consume(query)
        _p(query, operator_stack, tree_stack)
    while len(operator_stack):
        _pop_operator(operator_stack, tree_stack)

def _parse_filter_expr(query):
    operator_stack = []
    tree_stack     = []

    query = [query, 0]

    _e(query, operator_stack, tree_stack)
    if _next(query) != None:
        raise FilterSyntaxError()

    return tree_stack[-1]

class TaskFilter:

    _parse_tree = None

    def __init__(self, filter_expr):
        if len(filter_expr):
            self._parse_tree = _parse_filter_expr(filter_expr)

    def task_match(self, task):
        if self._parse_tree != None:
            return self._parse_tree.task_match(task)
        return True
