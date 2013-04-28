# Copyright (c) 2013 Galah Group LLC
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
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

import interact
import interact._utils as _utils
import re
from parsing import Block, Line, grab_blocks

def indentation(code, max_score = 10, allow_negative = False):
    """
    Given a chunk of code as a string, this function will determine if the
    student indented properly. Returns a TestResult object.

    Tests:
        * A student's code is correctly indented if every line of each sub-block
          is indented strictly more than the least indented line on the parent
          block.

          If any problems are found, a single TestMessage will be added to the
          returned TestResult object with type
          `interact/indentation/basic_indent_level`. The lines property of this
          message is a list of every Line that had a problem.

    Test Result:
        The test result object that is returned

    """

    # Transform the code into a list of Line objects
    lines = Line.make_lines(code.splitlines())

    # Break the code up into blocks.
    blocks = grab_blocks(lines)

    # Recursive helper function.
    def check(block, minimum = None):
        problems = []

        # Check that each line in the current block has an indnetation level
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
            problems += check(i, new_minimum)

        return problems

    result = interact.TestResult(
        brief = "This test checks to ensure you are indenting properly. Make "
                "sure that every time you start a new block (curly braces "
                "delimit blocks) you indent more.",
        default_message = "Great job! You have perfect indentation!",
        max_score = max_score
    )

    problems = check(blocks)
    if problems:
        result.add_message(interact.TestResult.Message(
            "{lines_} {line_numbers_} {are_} not indented more than the outer "
                "block.",
            line_numbers_ = _utils.pretty_list(i.line_number for i in problems),
            are_ = "are" if len(problems) > 1 else "is",
            lines_ = _utils.plural_if("Line", problems),
            lines = problems,
            dscore = -len(problems),
            type = "interact/indentation/basic_indent_level"
        ))
    
    # The score is just the sum of the dscores for each message plus the max
    # score (since dscores are negative this makes sense).
    score = max_score + sum(i.dscore for i in result.messages)
    if not allow_negative:
        score = max(0, score)
    result.score = score

    return result

test_case = \
"""#include <iostream>

using namespace std;

int main() {
    cout << "hi"
         << "bob";
    foo(
        "apple",
        "sauce"
    );

    if (balsa wood) {
        apple sauce;
        duck face;
            applce face;
        sauce.
    duck;
    how now brown cow
        if (true) {
            done.
        }
    }
}"""

print indentation(test_case, 0, True)

# def block_indent_level(lines):
#     """
#     Determine what indent level the block of lines is at. This is done by
#     checking the indent level of each individual line, and then taking the most
#     common indent level and returning that. None is returned if lines is empty.

#     Blank lines are not taken into consideration (ie: they are not counted as
#     lines with 0 indentation, rather they are not counted at all).

#     """

#     # Create a dictionary with keys corresponding to indentation levels, and
#     # values corresponding to the number of lines we encountered at that
#     # indentation level.
#     indent_levels = {}
#     for i in lines:
#         current_level = indent_level(i)
#         if current_level is None:
#             continue

#         if current_level in indent_levels:
#             indent_levels[current_level] += 1
#         else:
#             indent_levels[current_level] = 1

#     # Sorts the various levels from greatest to least by occurence.
#     sorted_items = \
#         sorted(indent_levels.items(), key = lambda x: x[1], reverse = True)

#     # The top item in the list is the indent level with the greatest number of
#     # occurences. Return the indent level of that item.
#     if sorted_items:
#         return sorted_items[0][0]
#     else:
#         # The list is empty.
#         return None




# import unittest
# class TestIndentChecking(unittest.TestCase):
#     def test_indent_level(self):
#         # Specific inputs to run through
#         test_cases = (
#             ("   foo\t \t", 3),
#             ("\t \t foobar  ", 4),
#             ("  \t \t    ", None),
#             ("", None),
#             ("foo bar baz qux \t \t", 0)
#         )

#         for case, expected in test_cases:
#             self.assertIs(indent_level(case), expected)

#     def test_block_indent_level(self):
#         test_cases = (
#             (
#                 Line.make_lines(
#                     "#include <iostream>\n"
#                     "\n"
#                     "using namspace std;"
#                     "\n"
#                     "int main() {\n"
#                     """    cout << "Hello world!" << endl;\n"""
#                     "    return 0;\n"
#                     "}",
#                 ),
#                 0
#             ),
#             (
#                 "    Hello, joe\n"
#                 "    my name is.\n"
#                 "john.",
#                 4
#             ),
#             (
#                 "    Hello, joe\n"
#                 "my name is",
#                 (4, 0) # It is undefined which should be returned.
#             ),
#             (
#                 "Hello, joe\n"
#                 "    my name is",
#                 (4, 0)
#             ),
#             (
#                 "\n"
#                 "\n"
#                 "\n",
#                 None
#             ),
#             (
#                 "\n"
#                 "\n"
#                 " hi"
#                 "\n",
#                 1
#             ),
#             (
#                 "",
#                 None
#             )
#         )

#         for case, expected in test_cases:
#             if isinstance(expected, tuple):
#                 result = block_indent_level(case)
#                 for i in expected:
#                     if result is i:
#                         break
#                 else:
#                     self.fail(
#                         "Expected one of %s, got %s." %
#                             (str(expected), repr(result))
#                     )
