# Copyright (c) 2013 Galah Group LLC
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of galah-interact-python.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

def default_repr(obj):
    """
    Returns a string that would be appropriate to return from a repr() call. The
    string will be of the form `ClassName(attribute1 = value, ...)`.

    """

    attributes = sorted(obj.__dict__.items(), key = lambda x: x[0])
    attribute_strings = []
    for key, value in attributes:
        if not key.startswith("_"):
            attribute_strings.append(key + " = " + repr(value))

    return "%s(%s)" % (obj.__class__.__name__, ", ".join(attribute_strings))

import os.path
def resolve_path(path):
    return os.path.abspath(os.path.expanduser(path))

def escape_shell_string(str):
    """
    Escapes a shell string such that it is suitable to be displayed to the user.
    This function **should not** be used to actually feed arguments into a shell
    as this function **is not** secure enough.

    """

    escaped = str.replace("\\", "\\\\").replace("\"", "\\\"")
    if " " in escaped:
        escaped = "\"" + escaped + "\""

    return escaped

def craft_shell_command(command):
    """
    Returns a shell command from a list of arguments suitable to be passed into
    subprocess.Popen. The returned string should only be used for display
    purposes and is not secure enough to actually be sent into a shell.

    """

    return " ".join([escape_shell_string(i) for i in command])

def limit_string_length(string, max_lines = 20, max_characters = 20 * 72):
    # If the string is empty, we don't need to do anything.
    # if not string:
        # return string

    # Negative values are bad
    if max_lines < 0:
        raise TypeError("max_lines cannot be negative, got %d." % (max_lines, ))
    elif max_characters < 0:
        raise TypeError(
            "max_characters cannot be negative, got %d." % (max_lines, )
        )

    nlines_truncated = 0
    lines = string.splitlines()
    if len(lines) > max_lines:
        nlines_truncated = len(lines) - max_lines
        lines = lines[:max_lines]

    ncharacters_truncated = 0
    if len(string) > max_characters:
        ncharacters_truncated = len(string) - max_characters
        string = string[:max_characters]

    return (string, nlines_truncated, ncharacters_truncated)

def truncate_string(string, max_lines = 20, max_characters = 20 * 72):
    new_string, nlines_truncated, ncharacters_truncated = limit_string_length(
        string, max_lines, max_characters
    )

    if ncharacters_truncated == 0 and nlines_truncated == 0:
        return new_string
    else:
        return new_string + "\n---Remaining text truncated---"
