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
    ``subprocess.Popen`` to compile those files.

    :param files: A list of files to compile.
    :param flags: A list of flags to pass onto ``g++``. ``-o main`` will always
            be passed after these flags.
    :returns: A list of arguments appropriate to pass onto ``subprocess.Popen``.

    >>> create_compile_command(["main.cpp", "foo.cpp"], ["-Wall", "-Werror])
    ["g++", "-Wall", "-Werror", "-o", "main", "main.cpp", "foo.cpp"]

    """

    return ["g++"] + flags + ["-o", "main"] + files

def compile_program(files, flags = [], ignore_cache = False):
    """
    Compiles the provided code files. If ignore_cache is False and the program
    has already been compiled with this function, it will not be compiled
    again.

    :param files: A list of files to compile.
    :param flags: A list of flags to pass to ``g++``. See
            :func:`create_compile_command` for information on how exactly these
            are used.
    :param ignore_cache: If ``True``, the cache will not be used to service this
            query, even if an already compiled executable exists. See below for
            more information on the cache.
    :returns: A two-tuple ``(compiler output, executable path)``. If the
            executable was loaded from the cache, the compiler output will be
            ``None``. If the program did not compile successfully, the executable
            path will be ``None``.

    .. note::

        Note that this function blocks for as long as it takes to compile the
        files (which might be quite some time). Of coures if the executable is
        loaded from the cache no such long wait time will occur.

    This function caches its results so that if you give it the same files to
    compile again it will not compile them over again, but rather it will
    immediately return a prepared executable. The cache is cleared whenever the
    program exits.

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
    Used by the :func:`run_program` to create a ``Popen`` object that is
    responsible for running the exectuable.

    :param executable: An absolute path to the executable that needs to be run.
    :param temp_dir: An absolute path to a temporary directory that can be
            used as the current working directory. It will be deleted
            automatically at the end of the :func:`run_program` function. The
            executable will not be in the directory.

    This function may be overriden to override the default ``run_func`` value
    used in the :func:`run_program` function.

    .. warning::

        You **must** pass in ``subprocess.PIPE`` to the ``Popen`` constructor
        for the ``stdout`` and ``stdin`` arguments.

    You can use this function as a reference when creating your own run
    functions to pass into :func:`run_program`.

    """

    return subprocess.Popen(
        [executable],
        cwd = temp_dir,
        stdout = subprocess.PIPE,
        stdin = subprocess.PIPE
    )

def run_program(files = None, given_input = "", run_func = None,
        executable = None):
    """
    Runs a program made up of some code files by first compiling, then
    executing it.

    :param files: The code files to compile and execute. :func:`compile_program`
            is used to compile the files, so its caching applies here.
    :param given_input: Text to feed into the compiled program's standard input.
    :param run_func: A function responsible for creating the ``Popen`` object
            that actually runs the program. Defaults to
            :func:`default_run_func`.
    :param executable: If you don't need to compile any code you can pass a path
            to an executable that will be executed directly.
    :returns: A three-tuple containing the result of the program's execution
            ``(stdout, stderr, returncode)``.

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
        compile_output, executable = compile_program(files)
        if not executable:
            raise RuntimeError("Program did not compile.")

    temp_dir = tempfile.mkdtemp()

    try:
        user_program = run_func(executable, temp_dir)

        stdout, stderr = user_program.communicate(given_input)

        return (stdout, stderr, user_program.returncode)
    finally:
        shutil.rmtree(temp_dir)
