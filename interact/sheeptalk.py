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

import sys

def recv_json(source = sys.stdin):
    """
    Listens to standard input and parses what comes in as a JSON object then
    returns that object. This is the preferred method of receiving data from
    the sheep when inside of a virtual machine.

    """

    import json
    values = json.load(source)

def send_json(obj, out = sys.stdout):
    """
    Sends json through the given output. This is the preferred method of sending
    results to the sheep when inside of a virtual machine.

    """

    import json
    json.dump(obj, out)
