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

import tempfile
import subprocess
import shutil
import os
import os.path
import interact.core
import atexit

# Create and set up cleanup code for the cache. The cache stores as keys a
# sorted (alphabetically) tuple of the absolute file paths used to create the
# executable whose absolute path is stored in the value. The directory,
# as returned by os.path.dirname will be deleted once the program exits.
_cache = {}
def _cleanup():
    for i in _cache.values():
        shutil.rmtree(os.path.dirname(i))
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
        return (None, _cache[file_tuple])

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

def default_run_func(executable, temp_dir):
    """
    Used by the run_program function to create a Popen object that is
    responsible for running the exectuable. temp_dir will be an absolute path to
    a temporary directory that can be used as the current working directory. It
    will be deleted automatically at the end of the run_program function. The
    executable will not be in the directory.

    This function may be overriden to override the default run_func value used
    in the run_program function.

    """

    return subprocess.Popen(
        [executable],
        cwd = os.path.dirname(executable),
        stdout = subprocess.PIPE,
        stdin = subprocess.PIPE
    )

def run_program(files = None, given_input = "", run_func = None,
        executable = None):
    """
    Executes the given program (if files was specified, the program will be
    compiled first via the compile_program function) and returns a three-tuple
    with standard output first, standard error output second, and the return
    code third (ie: (stdout, stderr, returncode)).

    """

    if (files is None and executable is None) or \
            (files is not None and executable is not None):
        raise TypeError(
            "Either files or executable must be specified, but not both nor "
            "neither."
        )

    # Doing this each time the function runs rather than putting the default
    # in the function header allows users to override default_run_func.
    if run_func is None:
        run_func = default_run_func

    # Compile the given files if we weren't given an executable.
    if executable is None:
        compile_output, executable = compilation.compile_program(files)
        if not executable:
            raise RuntimeError("Program did not compile.")

    temp_dir = tempfile.mkdtemp()

    try:
        user_program = run_func(executable, temp_dir)

        stdout, stderr = user_program.communicate(given_input)

        return (stdout, stderr, user_program.returncode)
    finally:
        shutil.rmtree(temp_dir)
