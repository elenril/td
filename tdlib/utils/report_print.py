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

import blessed

def report_print(config, out,
                 tasks, columns, sort, col_sep):
    # sort the task list
    if sort.endswith('+'):
        sort_reverse = False
    elif sort.endswith('-'):
        sort_reverse = True
    else:
        raise ValueError('Invalid sorting specification: %s' % sort)
    sort = sort[:-1]

    tasks = sorted(tasks, key = lambda task, sort = sort: getattr(task, sort),
                   reverse = sort_reverse)

    # compute the required width for the header
    maxw = [0] * len(columns)
    for i, (col, label) in enumerate(columns):
        maxw[i] = max(maxw[i], len(label))

    # format the requested task attributes to strings and compute the required
    # width for each column
    tasks_formatted = []
    for t in tasks:
        col_vals = []
        nb_lines = 0
        for i, (col, label) in enumerate(columns):
            # the value can be multi-line, so we split it to a list of lines
            # that will be joined later when we know the final width of
            # each column
            col_val = str(getattr(t, col)).split('\n')
            maxw[i] = max(maxw[i], *map(len, col_val))
            nb_lines = max(nb_lines, len(col_val))
            col_vals.append(col_val)

        tasks_formatted.append((col_vals, nb_lines))

    # prepare the output stream
    term = blessed.Terminal(stream = out)

    #print the header
    for w, (col, label) in zip(maxw, columns):
        label_expanded = label + ' ' * (w - len(label))
        out.write(term.underline(label_expanded))
        out.write(col_sep)
    out.write('\n')

    # print the tasks
    reverse = False
    for tf, nb_lines in tasks_formatted:
        format = term.reverse if reverse else lambda x: x
        for i in range(nb_lines):
            outline = []
            for w, col in zip(maxw, tf):
                if i < len(col):
                    outline.append(col[i])
                    l = len(col[i])
                else:
                    l = 0
                outline.append(' ' * (w - l))
                outline.append(col_sep)
            out.write('%s\n' % format(''.join(outline)))
        reverse = not reverse
