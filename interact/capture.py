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
This module provides the tools for easily running a Python function in a
seperate process in order to capture its standard input, output, and error.

"""

class _ExceptionCarrier:
    def __init__(self, exception):
        self.exception = exception

class CapturedFunction:
    """
    The type of object returned by :func:`capture_function`. Provides access to
    a captured function's stdin, stdout, stderr, and return value.

    :ivar pid: The process ID of the process that is running/ran the function.
    :ivar stdin: A file object (opened for writing) that the captured function
            is using as stdin.
    :ivar stdout: A file object (opened for reading) that the captured function
            is using as stdout.
    :ivar stderr: A file object (opened for reading) that the captured function
            is using as stderr.
    :ivar return_value: Whatever the function returned. Will not be set until
            :meth:`CapturedFunction.wait` is called. Will contain the value
            :attr:`CapturedFunction.NOT_SET` if it has not been set by a call to
            :meth:`CapturedFunction.wait`.

    The correct way to check if ``return_value`` is set is to compare with
    :attr:`CapturedFunction.NOT_SET` like so:

    .. code-block:: python

        if my_captured_function.return_value is CapturedFunction.NOT_SET:
            print "Not set yet!"
        else:
            print "It's set!"

    """

    class _NotSet:
        """
        A sentinel class used by :class:`CapturedFunction` to denote that the
        ``return_value`` has not yet been set.

        """

        def __str__(self):
            return "<NOTSET>"

    #: A sentinel value used to denote that a ``return_value`` has not been set
    #: yet.
    NOT_SET = _NotSet()

    def __init__(self, pid, stdin_pipe, stdout_pipe, stderr_pipe,
            returnvalue_pipe):
        self.pid = pid
        self.stdin = stdin_pipe
        self.stdout = stdout_pipe
        self.stderr = stderr_pipe
        self._returnvalue_pipe = returnvalue_pipe
        self.return_value = CapturedFunction.NOT_SET

    def wait(self):
        """
        Blocks until the process running the captured function exits (which
        will be when the function returns). Sets ``return_value``.

        If the function raised an exception, this function will raise that
        exception.

        """

        returned = pickle.load(self._returnvalue_pipe)
        os.waitpid(self.pid, 0)

        if isinstance(returned, _ExceptionCarrier):
            raise returned.exception
        else:
            self.return_value = returned

import os
import multiprocessing
import pickle
import sys
def capture_function(func, *args, **kwargs):
    """
    Executes a function and captures anything it prints to standard output or
    standard error, along with capturing its return value.

    :param func: The function to execute and capture.
    :param \*args,\*\*kwargs: The arguments to pass to the function.
    :returns: An instance of :class:`CapturedFunction`.

    >>> def foo(x, c = 3):
    ...     print x, "likes", c
    ...     return x + c
    >>> a = capture_function(foo, 2, c = 9)
    >>> a.stdout.read()
    "2 likes 9\\n"
    >>> a.wait()
    >>> print a.return_value
    11

    """

    # I'm using a dict here to avoid copying and pasting code for each pipe
    pipes = {}
    for i in ("stdin", "stdout", "stderr", "return_value"):
        read_end, write_end = os.pipe()
        pipes[i] = (os.fdopen(read_end, "r"), os.fdopen(write_end, "w"))

    child_pid = os.fork()
    if child_pid == 0:
        # We are in the child process.

        # Make sure all of our standard descriptors redirect to pipes controlled
        # by our parent.
        # sys.stdin = stdin_read
        # sys.stdout = stdout_write
        # sys.stderr = stderr_write
        os.dup2(pipes["stdin"][0].fileno(), 0)
        os.dup2(pipes["stdout"][1].fileno(), 1)
        os.dup2(pipes["stderr"][1].fileno(), 2)

        try:
            return_value = func(*args, **kwargs)

            pickle.dump(
                return_value,
                pipes["return_value"][1],
                protocol = pickle.HIGHEST_PROTOCOL
            )
        except:
            raised = sys.exc_info()[0]
            pickle.dump(
                _ExceptionCarrier(raised),
                pipes["return_value"][1],
                protocol = pickle.HIGHEST_PROTOCOL
            )

        for i in (pipes["stdout"][1], pipes["stderr"][1], pipes["return_value"][1]):
            i.flush()

        os._exit(0)
    else:
        # We are in the parent process
        return CapturedFunction(
            child_pid,
            pipes["stdin"][1],
            pipes["stdout"][0],
            pipes["stderr"][0],
            pipes["return_value"][0]
        )
