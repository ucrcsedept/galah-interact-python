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

import interact.core
import interact._utils as _utils
import tempfile
import subprocess
import os.path
import atexit
import shutil

# Create and set up cleanup code for the cache. The cache stores as keys a
# sorted (alphabetically) tuple of the absolute file paths used to create the
# executable whose absolute path is stored in the value. The directory,
# as returned by os.path.dirname will be deleted once the program exits.

def check_compiles(files, flags = [], ignore_cache = False):
    # Try to compile the program
    compiler_output, executable_path = compile_program(
        files, flags = flags, ignore_cache = ignore_cache
    )

    command = _utils.craft_shell_command(create_compile_command(files, flags))
    result = interact.core.TestResult(
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
