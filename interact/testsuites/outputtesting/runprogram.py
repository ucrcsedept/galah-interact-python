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
import compilation
import shutil
import os

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
