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

import interact.parse as parse
import testcore

import unittest
class TestCleanseQuotedStrings(unittest.TestCase):
    def test_basic(self):
        test_cases = (
            (r"""this "is" some "quoted" 'strings"all"'""", "this  some  "),
            ("", ""),
            ("""'""""""hi'hi""", "hi"),
            ("''''''''''''''''", ""),
            ('""""""""""""""""', ""),
            ("I am the 'destroyer \" of muffins'", "I am the "),
            ('Duck "duck\\\" duck" go', "Duck  go")
        )

        testcore.test_cases(
        	self, test_cases, parse.cleanse_quoted_strings
        )

class TestGrabBlocks(unittest.TestCase):
    def test_basic(self):
        from interact.parse import Line, Block
        test_cases = (
            # Simple test case
            (
                [
                    Line(0, "#include <iostream>"),
                    Line(1, ""),
                    Line(2, "using namespace std;"),
                    Line(3, ""),
                    Line(4, "int main() {"),
                    Line(5, '    cout << "Hello world" << endl;'),
                    Line(6, "    return 0"),
                    Line(7, "}")
                ],
                Block(
                    lines = [
                        Line(0, "#include <iostream>"),
                        Line(1, ""),
                        Line(2, "using namespace std;"),
                        Line(3, ""),
                        Line(4, "int main() {"),
                        Line(7, "}")
                    ],
                    sub_blocks = [
                        Block(
                            lines = [
                                Line(5, '    cout << "Hello world" << endl;'),
                                Line(6, "    return 0")
                            ]
                        )
                    ]
                )
            ),

            # Slightly tricky test case
            (
                [
                    Line(0,  "#include <iostream>"),
                    Line(1,  ""),
                    Line(2,  "using namespace std;"),
                    Line(3,  ""),
                    Line(4,  "int main() {"),
                    Line(5,  '    cout << "{" << endl;'),
                    Line(6,  "    if (true)"),
                    Line(7,  "    {"),
                    Line(8,  "        return false;"),
                    Line(9,  "    } else {"),
                    Line(10, "        return true;"),
                    Line(11, "oh noz"),
                    Line(12, "    }"),
                    Line(13, "        pinata"),
                    Line(14, "    return 0"),
                    Line(15, "}")
                ],
                Block(
                    lines = [
                        Line(0,  "#include <iostream>"),
                        Line(1,  ""),
                        Line(2,  "using namespace std;"),
                        Line(3,  ""),
                        Line(4,  "int main() {"),
                        Line(15, "}")
                    ],
                    sub_blocks = [
                        Block(
                            lines = [
                                Line(5,  '    cout << "{" << endl;'),
                                Line(6,  "    if (true)"),
                                Line(7,  "    {"),
                                Line(9,  "    } else {"),
                                Line(12, "    }"),
                                Line(13, "        pinata"),
                                Line(14, "    return 0")
                            ],
                            sub_blocks = [
                                Block(
                                    lines = [
                                        Line(8, "        return false;")
                                    ]
                                ),
                                Block(
                                    lines = [
                                        Line(10, "        return true;"),
                                        Line(11, "oh noz")
                                    ]
                                )
                            ]
                        )
                    ]
                )
            )
        )

        def compare_blocks(a, b):
            if a is None or b is None:
                return a is b

            if a.lines != b.lines:
                return False

            if len(a.sub_blocks) != len(b.sub_blocks):
                return False

            matches = []
            for i in a.sub_blocks:
                for j in b.sub_blocks:
                    if i.lines == j.lines:
                        matches.append((i, j))

            if len(matches) != len(a.sub_blocks):
                return False

            for i in matches:
                if not compare_blocks(*i):
                    return False

            return True

        for case, expected in test_cases:
            if not compare_blocks(parse.grab_blocks(case), expected):
                # TODO: Make the failure output meaningful.
                self.fail("abaabahaha")
