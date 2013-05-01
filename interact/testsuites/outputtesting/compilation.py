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
_cache = {}
def _cleanup():
    for i in _cache.values():
        print "Deleting", os.path.dirname(i)
        # shutil.rmtree(os.path.dirname(i))
atexit.register(_cleanup)

def create_compile_command(files, flags):
    """
    From a list of files and flags, crafts a list suitable to pass into
    subprocess.Popen to compile those files.

    """

    return ["g++"] + flags + ["-o", "main"] + files

def compile_program(files, flags = [], ignore_cache = False):
    """
    Compiles the provided code files. If ignore_cache is False and the program
    has already been compiled with this function, it will not be compiled
    again.

    Returns a two-tuple with the compiler output first and an absolute path to
    the executable second. If the executable was loaded from the cache, the
    compiler output will be None. If the program did not compile, the path will
    be None.

    Note that this function blocks for as long it takes to compile the files
    (unless of course the results are loaded from the cache).

    """

    # If we've already compiled these files don't do it again
    file_tuple = tuple(sorted(files))
    if not ignore_cache and file_tuple in _cache:
        return (None, _cache(file_tuple))

    temp_dir = tempfile.mkdtemp()

    try:
        # We want to always override the name of the output file otherwise we
        # won't know what it's named (though we could try to detect it if it
        # becomes a desirable features.)
        command = create_compile_command(files, flags)

        compiler_job = subprocess.Popen(
            command,
            cwd = temp_dir,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        )

        compiler_job.wait()
        if compiler_job.returncode != 0:
            return (compiler_job.stdout.read(), None)

        executable_path = os.path.join(temp_dir, "main")
        _cache[file_tuple] = executable_path

        return (compiler_job.stdout.read(), executable_path)
    except:
        shutil.rmtree(temp_dir)
        raise

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
