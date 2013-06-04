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
This module contains useful test functions that perform full testing on input,
returning TestResult objects. These are typical tests that many harnesses need
to perform such as checking indentation or checking to see if the correct files
were submitted.

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

def check_files_exist(*files, **extra):
    """
    Checks to see if the given files provided as arguments exist. They must be
    files as defined by
    `os.path.isfile() <http://docs.python.org/2/library/os.path.html#os.path.isfile>`_.

    :param \*files: The files to check for existance. Note this is not a list,
                   rather you should pass in each file as a seperate arugment.
                   See the examples below.
    :param \*\*extra: extra parameters. If extra["basename"] is True, then os.path.basename
                      is applied to all filenames before printing.
    :returns: Returns a TestResult object that will be passing iff *all* of the
              files exist.

    .. code-block:: python

        # The current directory contains only a main.cpp file.
        >>> print check_files_exist("main.cpp", "foo.cpp", "foo.h")
        Score: 0 out of 1

        This test ensures that all of the necessary files are present.

         * You are missing foo.cpp and foo.h.

    *(Note that this function really does return a TestResult object, but
    TestResult.__str__() which transforms the TestResult into a string that can
    be printed formats it specially as seen above)*

    """
	
    if extra["basename"]:
        missing_files = [os.path.basename(i) for i in files if not os.path.isfile(i)]
    else:
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

def check_indentation(files, max_score = 10, allow_negative = False):
    """
    Checks to see if code is indented properly.

    Currently code is indented properly iff every block of code is indented
    strictly more than its parent block.

    :param files: A list of file paths that will each be opened and examined.
    :param max_score: For every improperly indented line of code, a point is
                      taken off from the total score. The total score starts at
                      ``max_score``.
    :param allow_negative: If True, a negative total score will be possible,
                           if False, 0 will be the lowest score possible.
    :returns: A ``TestResult`` object.

    .. code-block:: python

        >>> print open("main.cpp").read()
        #include <iostream>

        using namespace std;

        int main() {
            if (true) {
            foo();
            } else {
                dothings();
                while (false) {
            dootherthings();
                }
                cout << "{}{}{{{{{}}}{}{}{}}}}}}}}{{{{"<< endl;
        }
        return 0;
        }

        >>> print open("foo.cpp").read()
        #include <iostream>

        using namespace std;

        int main() {
        return 0;
        }

        >>> print check_indentation(["main.cpp", "foo.cpp"])
        Score: 6 out of 10

        This test checks to ensure you are indenting properly. Make sure that every time you start a new block (curly braces delimit blocks) you indent more.

         * Lines 14, 13, and 10 in main.cpp are not indented more than the outer block.
         * Line 5 in foo.cpp is not indented more than the outer block.

    """

    result = core.TestResult(
        brief = "This test checks to ensure you are indenting properly. Make "
                "sure that every time you start a new block (curly braces "
                "delimit blocks) you indent more.",
        default_message = "**Great job!** We didn't find any problems with "
                          "your indentation!",
        max_score = max_score
    )

    for current_file in files:
        with open(current_file) as f:
            code = f.read()

        # Transform tjhe code into a list of Line objects
        lines = parse.Line.make_lines(code.splitlines())

        # Break the code up into blocks.
        blocks = parse.grab_blocks(lines)

        # Get a list of all the badly indented lines.
        problems = parse.find_bad_indentation(blocks)

        if problems:
            result.add_message(core.TestResult.Message(
                "{lines_} {line_numbers_} in {file_name} {are_} not indented more "
                    "than the outer block.",
                line_numbers_ = pretty.pretty_list(sorted([i.line_number for i in problems], reverse = True)),
                are_ = "are" if len(problems) > 1 else "is",
                lines_ = pretty.plural_if("Line", len(problems)),
                lines = problems,
                file_name = current_file,
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
    """
    Attempts to compile some files.

    :param files: A list of paths to files to compile.
    :param flags: A list of command line arguments to supply to the compiler.
            Note that ``-o main`` will be added after your arguments.
    :param ignore_cache: If you ask Galah Interact to compile some files, it
            will cache the results. The next time you try to compile the same
            files, the executable that was cached will be used instead. Set
            this argument to ``True`` if you don't want the cache to be used.
    :returns: A ``TestResult`` object.

    .. code-block:: python

        >>> print interact.standardtests.check_compiles(["main.cpp", "foo.cpp"])
        Score: 0 out of 10

        This test ensures that your code compiles without errors. Your program was compiled with g++ -o main /tmp/main.cpp /tmp/foo.cpp.

        Your code did not compile. The compiler outputted the following errors:

        ```
        /tmp/main.cpp: In function 'int main()':
        /tmp/main.cpp:7:9: error: 'foo' was not declared in this scope
        /tmp/main.cpp:9:18: error: 'dothings' was not declared in this scope
        /tmp/main.cpp:11:19: error: 'dootherthings' was not declared in this scope

        ```

    """

    files = [_utils.resolve_path(i) for i in files]

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
            compiler_output = pretty.truncate_string(compiler_output)

            result.add_message(
                "Your code did not compile. The compiler outputted the following "
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
