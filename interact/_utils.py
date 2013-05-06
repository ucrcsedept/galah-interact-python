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

import os
#: An open file descriptor ready for writing that goes directly to the null file
#: device (``/dev/null`` on Linux).
DEVNULL = open(os.devnull, "wb")

def default_repr(obj):
    """
    :returns: A string that would be appropriate to return from a repr() call.
            The string will be of the form `ClassName(attribute1 = value, ...)`.

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

import inspect
def get_root_script_path():
    """
    :returns: An absolute path to the file that is actually being executed.
            As in if this module is imported by some other module that was
            imported by a script ``/tmp/bla.py``, this function will return
            ``/tmp/bla.py``.

    """

    return resolve_path(inspect.stack()[-1][1])

import os.path
def file_name(file_path):
    """
    :param file_path: A relative or absolute file path.
    :returns: The name of the file, without the extension.

    >>> utils.get_file_name("/tmp/applesauce.tgz")
    "applesauce"
    >>> utils.get_file_name("../../foo.txt")
    "foo"

    """

    return os.path.splitext(os.path.basename(file_path))[0]

import os
import os.path
def which(program_name):
    """
    Simulates the Linux utility ``which``.

    :param program_name: The name of the program to search for, should include
            any necessary extensions.
    :returns: An absolute path to the found program.

    This is done by searching for a file with ``program_name`` in the path.

    """

    path = os.environ.get("PATH", "").split(":")
    for i in path:
        possible_path = os.path.join(i, program_name)

        if os.path.exists(possible_path):
            return possible_path

    return None
