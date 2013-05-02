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
Test suites that perform full testing on input, returning TestResult objects.
These are typical tests that many harnesses need to perform. Such as checking
indentation or checking to see if the correct files were submitted.

"""

import os
import os.path
import re
import tempfile
import subprocess
import atexit
import shutil

import _utils
import core
import pretty
import parse
import execute

def check_files_exist(*files):
    """
    Checks to see if the given files provided as arguments exist. They must be
    files as defined by os.path.isfile(). Returns a TestResult.

    The TestResult will be passing if and only if all of the files exist.

    """

    missing_files = [i for i in files if not os.path.isfile(i)]

    result = core.TestResult(
        brief = "This test ensures that all of the necessary files are "
                "present.",
        default_message = "Great job! All the necessary files are present."
    )

    if missing_files:
        result.add_message(core.TestResult.Message(
            "You are missing {missing_files_}.",
            missing_files_ = pretty.pretty_list(missing_files),
            missing_files = missing_files,
            dscore = -1,
            type = "interact/filesexist/basic_files_exist"
        ))
        result.set_passing(False)
    else:
        result.set_passing(True)

    return result

def indentation(code, file_name, max_score = 10, allow_negative = False):
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
    lines = parse.Line.make_lines(code.splitlines())

    # Break the code up into blocks.
    blocks = parse.grab_blocks(lines)

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

    result = core.TestResult(
        brief = "This test checks to ensure you are indenting properly. Make "
                "sure that every time you start a new block (curly braces "
                "delimit blocks) you indent more.",
        default_message = "Great job! You have perfect indentation!",
        max_score = max_score
    )

    problems = check(blocks)
    if problems:
        result.add_message(core.TestResult.Message(
            "{lines_} {line_numbers_} in {file_name} {are_} not indented more "
                "than the outer block.",
            line_numbers_ = pretty.pretty_list(i.line_number for i in problems),
            are_ = "are" if len(problems) > 1 else "is",
            lines_ = _utils.plural_if("Line", problems),
            lines = problems,
            file_name = file_name,
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

def check_compiles(files, flags = [], ignore_cache = False):
    # Try to compile the program
    compiler_output, executable_path = execute.compile_program(
        files, flags = flags, ignore_cache = ignore_cache
    )

    command = pretty.craft_shell_command(
        execute.create_compile_command(files, flags)
    )

    result = core.TestResult(
        brief = "This test ensures that your code compiles without errors. "
                "Your program was compiled with %s." % (command, ),
        default_message = "**Great job!** Your code compiled cleanly without "
                          "any problems.",
        max_score = 10,
        bulleted_messages = False
    )

    # If the compilation failed
    if executable_path is None:
        if compiler_output:
            compiler_output = _utils.truncate_string(compiler_output)

            result.add_message(
                "Your code did not compile. The compiler output the following "
                "errors:\n\n```\n{compiler_output}\n```\n",
                compiler_output = compiler_output,
                dscore = -10
            )
        else:
            result.add_message(
                "Your code did not compile but the compiler did not output "
                "any errors or warnings."
            )

        result.score = 0
    else:
        result.score = 10

    return result;
