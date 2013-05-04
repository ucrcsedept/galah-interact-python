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

"""
This module is useful when attempting to roughly parse students' code (ex:
trying to check that indentation was properly used). This module does not
attempt to, and never will, try and fully parse C++. If such facilities are
added to Galah Interact they will probably be added as a seperate module that
provides a nice abstraction to Clang.

"""

class Block:
    """
    Represents a block of code.

    :ivar lines: A list of ``Line`` objects that make up this block.
    :ivar sub_blocks: A list of ``Block`` objects that are children of
            this block.

    """

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
    """
    Represents a line of code.

    :ivar code: The contents of the line.
    :ivar line_number: The line number.

    """

    def __init__(self, line_number, code):
        self.code = code
        self.line_number = line_number

    def __str__(self):
        return self.code

    def __repr__(self):
        return "Line(%d, %s)" % (self.line_number, repr(self.code))

    def indent_level(self):
        """
        Determines the indentation level of the current line.

        :returns: The sum of the number of tabs and the number of spaces at the
                  start of the line. Iff the line is blank (not including
                  whitespace), ``None`` is returned.

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
        """
        Creates a list of Line objects from a list of strings representing
        lines in a file.

        :param lines: A list of strings where each string is a line in a file.
        :param start: The line number of the first line in ``lines``.
        :returns: A list of line objects.

        >>> Line.make_lines(["int main() {", "   return 0;", "}"], 1)
        [
            Line(1, "int main() {"),
            Line(2, "   return 0;"),
            Line(3, "}")
        ]

        """

        return (cls(n, line) for n, line in enumerate(lines))

    @staticmethod
    def lines_to_str_list(lines):
        """
        Creates a list of strings from a list of ``Line`` objects.

        :param lines: A list of ``Line`` objects.
        :returns: A list of strings.

        >>> my_lines = [
            Line(1, "int main() {"),
            Line(2, "   return 0;"),
            Line(3, "}")
        ]
        >>> Line.lines_to_str_list(my_lines)
        [
            "int main() {",
            "    return 0;",
            "}"
        ]

        """
        return [i.code for i in lines]

    @staticmethod
    def lines_to_str(lines):
        """
        Creates a single string from a list of ``Line`` objects.

        :param lines: A list of ``Line`` objects.
        :returns: A single string.

        >>> my_lines = [
            Line(1, "int main() {"),
            Line(2, "   return 0;"),
            Line(3, "}")
        ]
        >>> Line.lines_to_str(my_lines)
        "int main() {\\n    return 0\\n}\\n"

        """

        return "\n".join(Line.lines_to_str_list(lines))

    def __eq__(self, other):
        """
        Determines if two lines are equal.

        :returns: ``True`` if the two lines have the same code in them and the
                  same line number, ``False`` otherwise.

        >>> Line("foo()", 2) == Line("foo()", 2)
        True
        >>> Line("foo()", 2) == Line("foo()", 3)
        False
        >>> Line("foo()", 2) == Line("    foo()", 2)
        False

        """

        return self.code == other.code and self.line_number == other.line_number

def grab_blocks(lines):
    """
    Finds all blocks created using curly braces (does not handle two line if
    statements for example).

    :param lines: A list of ``Line`` objects.
    :returns: A single ``Block`` object which can be traversed like a tree.

    >>> my_lines = [
    ...     Line(0, "#include <iostream>"),
    ...     Line(1, ""),
    ...     Line(2, "using namespace std;"),
    ...     Line(3, ""),
    ...     Line(4, "int main() {"),
    ...     Line(5, '    cout << "Hello world" << endl;'),
    ...     Line(6, "    return 0"),
    ...     Line(7, "}")
    ... ]
    >>> grab_blocks(my_lines)
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
                ],
                sub_blocks = None
            )
        ]
    )

    *(Note that I formatted the above example specially, it won't actually
    print out so beautifully if you try it yourself, but the content will be
    the same)*

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
        stripped_line = cleanse_quoted_strings(line.code)

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

def cleanse_quoted_strings(line):
    """
    Removes all quoted strings from a line. Single quotes are treated the same
    as double quotes.

    Escaped quotes are handled. A forward slash is assumed to be the escape
    character. Escape sequences are not processed (meaning `\"` does not become
    `"`, it just remains as `\"`).

    :param line: A string to be cleansed.
    :returns: The line without any quoted strings.

    >>> cleanse_quoted_strings("I am 'John Sullivan', creator of worlds.")
    "I am , creator of worlds."
    >>> cleanse_quoted_strings(
    ...     'I am "John Sullivan \\"the Destroyer\\", McGee", fear me.'
    ... )
    "I am , fear me."

    This function is of particular use when trying to detect curly braces or
    other language constructs, and you don't want to be fooled by the symbols
    appearing in string literals.

    """

    # Returns ' if " is given, returns " if ' is given.
    inv_quote = lambda x: "'" if x == "\"" else "\""

    is_quote = lambda x: x in ["\"", "'"]

    # Will be a list of characters that we will join together to get the
    # resulting string sans quoted strings.
    unquoted_string = []

    in_quotes = None
    for i, char in enumerate(line):
        # Check to see if this character is escaped (this will occur if there is
        # an odd number of back slashes in front of it).
        num_slashes = 0
        for j in reversed(range(0, i)):
            if line[j] == "\\":
                num_slashes += 1
            else:
                break
        escaped = num_slashes % 2 == 1

        if char == in_quotes and not escaped:
            in_quotes = None
            continue
        elif is_quote(char) and in_quotes is None:
            in_quotes = char
            continue

        if in_quotes is None:
            unquoted_string.append(char)

    return "".join(unquoted_string)

def find_bad_indentation(block, minimum = None):
    """
    Detects blocks of code that are not indented more than their parent blocks.

    :param block: The top-level block of code. Sub-blocks will be recursively
                  checked.
    :param minimum: The minimum level of indentation required for the top-level
                    block. Mainly useful due to this function's recursive
                    nature.
    :returns: A list of ``Line`` objects where each ``Line`` had a problem with
              its indentation.

    >>> my_block = Block(
    ...     lines = [
    ...         Line(0,  "#include <iostream>"),
    ...         Line(1,  ""),
    ...         Line(2,  "using namespace std;"),
    ...         Line(3,  ""),
    ...         Line(4,  "int main() {"),
    ...         Line(15, "}")
    ...     ],
    ...     sub_blocks = [
    ...         Block(
    ...             lines = [
    ...                 Line(5,  '    cout << "{" << endl;'),
    ...                 Line(6,  "    if (true)"),
    ...                 Line(7,  "    {"),
    ...                 Line(9,  "    } else {"),
    ...                 Line(12, "    }"),
    ...                 Line(13, "        pinata"),
    ...                 Line(14, "    return 0")
    ...             ],
    ...             sub_blocks = [
    ...                 Block(
    ...                     lines = [
    ...                         Line(8, "        return false;")
    ...                     ]
    ...                 ),
    ...                 Block(
    ...                     lines = [
    ...                         Line(10, "        return true;"),
    ...                         Line(11, "oh noz")
    ...                     ]
    ...                 )
    ...             ]
    ...         )
    ...     ]
    ... )
    >>> find_bad_indentation(my_block)
    [Line(11, "oh noz")]

    """

    problems = []

    # Check that each line in the current block has an indentation level
    # strictly greater than the minimum.
    for i in block.lines:
        indent_level = i.indent_level()
        if minimum is not None and indent_level is not None and \
                indent_level <= minimum:
            problems.append(i)

    # Find the indent level of the least indented line in the current block
    levels = []
    for i in block.lines:
        level = i.indent_level()
        if level is not None:
            levels.append(level)
    new_minimum = min(levels)

    # Recurse into every sub block
    for i in block.sub_blocks:
        problems += find_bad_indentation(i, new_minimum)

    return problems
