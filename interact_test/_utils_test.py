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

from interact._utils import *
import interact_test.testcore as testcore

import unittest
class TestIndentChecking(unittest.TestCase):
    def test_cleanse_quoted_strings(self):
        test_cases = (
            (r"""this "is" some "quoted" 'strings"all"'""", "this  some  "),
            ("", ""),
            ("""'""""""hi'hi""", "hi"),
            ("''''''''''''''''", ""),
            ('""""""""""""""""', "")
        )

        testcore.test_cases(self, test_cases, cleanse_quoted_strings)
