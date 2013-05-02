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

