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
import interact._utils as _utils

class Block:
    """Represents a block of code."""

    def __init__(self, lines, sub_blocks = None):
        if sub_blocks is None:
            sub_blocks = []

        self.lines = lines
        self.sub_blocks = sub_blocks

    def _to_str_list(self, indent_level = 0):
        result = [("\t" * indent_level) + repr(i) for i in self.lines]
        for i in self.sub_blocks:
            result += i._to_str_list(indent_level = indent_level + 1)

        return result

    def __str__(self):
        return "\n".join(self._to_str_list())

class Line:
    """Represents a line of code."""

    def __init__(self, line_number, code):
        self.code = code
        self.line_number = line_number

    def __str__(self):
        return self.code

    def __repr__(self):
        return "Line(%d, %s)" % (self.line_number, repr(self.code))

    def indent_level(self):
        """
        Determine the indentation level of the current line. Does this by
        counting the number of tabs and spaces at the start of the line and
        adding the two numbers together. If the line is blank (not including
        white space), None is returned.

        """

        # Iterates through the line character by character until a
        # non-whitespace character is hit.
        for i, c in enumerate(self.code):
            if c not in [" ", "\t"]:
                break
        else:
            # If we never hit a non-whitespace character...
            return None

        # i is the position of the first non-whitespace character, and because i
        # is zero-indexed, i is also the number of whitespace characters we saw.
        return i

    @classmethod
    def make_lines(cls, lines, start = 1):
        return (cls(n, line) for n, line in enumerate(lines))

    @staticmethod
    def lines_to_str_list(lines):
        return (i.code for i in lines)

    @staticmethod
    def lines_to_str(lines):
        return "\n".join(Line.lines_to_str_list(lines))

    def __eq__(self, other):
        return self.code == other.code and self.line_number == other.line_number

def grab_blocks(lines):
    """
    Finds all blocks created using curly braces (does not handle two line if
    statements for example). Returns a single Block object which can be treated
    as a tree.

    """

    # The number of nested blocks the current line is in relative to our
    # starting point. We will only look at the indentation for lines with
    # in_block == 0, all other lines we will recursively defer.
    in_block = 0

    # These are all of the lines that are within the current block (and not
    # within any sub blocks).
    lines_to_check = []

    # Contains the actual result (the list of two-tuples).
    sub_blocks = []

    # When we encounter code that is in a sub block, we push it onto this list.
    # Then when we get out of that sub block, we recurse on these lines and then
    # empty the list.
    unhandled_chunk = []

    for line in lines:
        # Remove all quoted strings from the line, that way when we search for
        # a curly brace we know it's an actual curly brace.
        stripped_line = _utils.cleanse_quoted_strings(line.code)

        # Will be set to true if the the current line is in the current block.
        include_current_line = False

        # Figure out if we are ending a block here
        for char in stripped_line:
            # If at any point we reach 0, that means we want to include this
            # line in the current block. This may occur if you have something
            # like "} else {".
            if in_block == 0:
                include_current_line = True

            # See comment above the in_block initialization.
            if char == "{":
                in_block += 1
            elif char == "}":
                in_block -= 1

        # Check if we ended a block here.
        if in_block == 0:
            include_current_line = True

        if include_current_line:
            # If we were just looking at a chunk of code in a sub block,
            # recurse properly.
            if unhandled_chunk:
                unhandled_block = grab_blocks(unhandled_chunk)
                if unhandled_block:
                    sub_blocks.append(unhandled_block)

                unhandled_chunk = []

            lines_to_check.append(line)
        else:
            unhandled_chunk.append(line)

    if not lines_to_check and not sub_blocks:
        return None
    else:
        return Block(lines_to_check, sub_blocks)
