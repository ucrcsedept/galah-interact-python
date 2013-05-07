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
Functions and classes that are essential when using this library. Is imported
by ``interact/__init__.py`` such that ``interact.core.x`` and ``interact.x``
are equivalent.

"""

import _utils
import os.path
import sys

class TestResult:
    """
    Represents the result of one unit of testing. The goal is to generate a
    number of these and then pass them all out of the test harness with a final
    score.

    :ivar brief: A brief description of the test that was run. This will always
            be displayed to the user.
    :ivar score: The score the student received from this test.
    :ivar max_score: The maximum score the student could have received from this
            test.
    :ivar messages: A list of :class:`TestResult.Message` objects that will be
            joined together appropriately and displayed to the user. Use
            :meth:`add_message` to add to this list.
    :ivar default_message: A string that will be displayed if there are no
            messages. Useful to easily create a "good job" message that is shown
            when no problems were detected.
    :ivar bulleted_messages: A boolean. If ``True``, all of the messages will be
            printed out in bullet point form (a message per bullet). If
            ``False``, they will simply be printed out one-per-line. You can
            set this to ``False`` if only one message will ever be displayed to
            the user, otherwise bullet points usually look better.

    """

    class Message:
        """
        A message to the user. This is the primary mode of giving feedback to
        users.

        """

        def __init__(self, text, *args, **kwargs):
            # We have some special keyword arguments that we want to snatch if
            # present.
            self.dscore = kwargs.get("dscore", None)
            self.type = kwargs.get("type", None)

            self.args = args
            self.kwargs = kwargs

            self.text = text

        def __str__(self):
            return self.text.format(*self.args, **self.kwargs)

        def __repr__(self):
            return _utils.default_repr(self)

    def __init__(
            self, brief = None, score = None, max_score = None, messages = None,
            default_message = None, bulleted_messages = True):
        if messages is None:
            messages = []

        self.brief = brief
        self.score = score
        self.max_score = max_score
        self.messages = messages
        self.default_message = default_message
        self.bulleted_messages = bulleted_messages

    def add_message(self, *args, **kwargs):
        """
        Adds a message object to the TestResult. If a Message object that is
        used, otherwise a new Message object is constructed and its constructor
        is passed all the arguments.

        """

        if len(args) == 1 and isinstance(args[0], TestResult.Message):
            self.messages.append(args[0])
        else:
            self.messages.append(TestResult.Message(*args, **kwargs))

    def calculate_score(self, starting_score = None, max_score = None,
            min_score = None):
        """
        Automatically calculates the score by adding up the ``dscore`` of
        each message and setting the score of the :class:`TestResult`
        appropriately.

        :param starting_score: This score is added to the sum of every message's
                ``dscore``. If ``None``, ``max_score`` is used.
        :param max_score: The ``max_score`` field of the object is set to this
                value. If ``None``, the current ``max_score`` is used, i.e. no
                change is made.
        :param min_score: If the calculated score is less than this value, this
                value is used instead.
        :returns: ``self``. This allows you to return the result of this
                function from test functions.

        >>> a = TestResult(max_score = 4)
        >>> a.add_message("Foo", dscore = -1)
        >>> a.add_message("Bar!", dscore = -5)
        >>> print a.calculate_score().score
        -2
        >>> print a.score
        -2
        >>> print a.calculate_score(min_score = 0).score
        0
        >>> print a.calculate_score(starting_score = 8, max_score = 6).score
        2
        >>> print a.max_score
        6

        """

        if max_score is None:
            max_score = self.max_score

        if starting_score is None:
            starting_score = max_score

        self.score = starting_score
        self.max_score = max_score

        for i in self.messages:
            if i.dscore is not None:
                self.score += i.dscore

        if self.score < min_score:
            self.score = min_score

        return self

    def set_passing(self, passing):
        """
        :param passing: Whether the test is passing or not.
        :returns: ``self``. This allows you to return the result of this
                function directly, leading to more concise test functions.

        This function sets ``score`` to either 1 (if ``passing`` is ``True``) or
        0 (if ``passing`` is ``False``). It also sets the ``max_score`` to
        ``1``.

        .. seealso::

            :meth:`is_passing` and :meth:`is_failing`.

        """

        self.score = 1 if passing else 0
        self.max_score = 1

        return self

    def is_passing(self):
        """
        :returns: ``True`` if the score is not ``0`` (note this function *will*
                return ``True`` if the score is negative).

        This function is most useful when dealing with a ``TestResult`` that you
        want to consider either passing or failing, and never anything in
        between.

        .. seealso::

            :meth:`set_passing` and :meth:`is_failing`.

        """

        return self.score != 0

    def is_failing(self):
        """
        :returns: The inverse of what :meth:`is_passing` returns.

        This function is most useful when dealing with a ``TestResult`` that you
        want to consider either passing or failing, and never anything in
        between.

        .. seealso::

            :meth:`set_passing` and :meth:`is_passing`.

        """

        return not self.is_passing()

    def to_galah_dict(self, name):
        return {
            "name": name,
            "score": 0 if self.score is None else self.score,
            "max_score": 0 if self.max_score is None else self.max_score,
            "message": self.to_str(show_score = False)
        }

    def to_str(self, show_score = True):
        result = []

        quick_status = ""
        if show_score and self.score is not None:
            quick_status += "Score: %d" % self.score

            if self.max_score is not None and self.max_score != 0:
                quick_status += " out of %d" % self.max_score

            result += [quick_status, ""]

        if self.brief:
            result += [str(self.brief), ""]

        if self.messages:
            for i in self.messages:
                if self.bulleted_messages:
                    result.append(" * " + str(i))
                else:
                    result.append(str(i))
            result.append("")
        elif self.default_message:
            result += [self.default_message, ""]

        return "\n".join(result[:-1])

    def __str__(self):
        return self.to_str()

    def __repr__(self):
        return _utils.default_repr(self)

class UniverseSet(set):
    """
    A special ``set`` such that every ``in`` query returns ``True``.

    >>> a = UniverseSet()
    >>> "hamster" in a
    True
    >>> "apple sauce" in a
    True
    >>> 3234 in a
    True
    >>> "taco" not in a
    False

    """

    def __init__(self, iterable = None):
        set.__init__(self, iterable if iterable is not None else [])

    def __contains__(self, item):
        return True

def json_module():
    """
    A handy function that will try to find a suitable JSON module to import and
    return that module (already loaded).

    Basically, it tries to load the ``json`` module, and if that doesn't exist
    it tries to load the ``simplejson`` module. If that doesn't exist, a
    friendly ``ImportError`` is raised.

    """

    try:
        import json
    except ImportError:
        try:
            import simplejson as json
        except ImportError:
            raise ImportError(
                "Could not load a suitable JSON module. You can try upgrading "
                "your version of Python or installing the simplejson library."
            )

    return json


class Harness:
    """
    An omniscient object responsible for driving the behavior of any Test
    Harness created using Galah Interact. Create a single one of these when
    you create your Test Harness and call the ``start()`` method.

    A typical Test Harness will roughly follow the below format.

    .. code-block:: python

        import interact
        harness = interact.Harness()
        harness.start()

        # Your code here

        harness.run_tests()
        harness.finish(max_score = some_number)

    :ivar sheep_data: The "configuration" values received from outside the
            harness (either from Galah or command line arguments). See
            :doc:`cli`.
    :ivar execution_mode: The mode of execution the harness is running in. Is
            set by :meth:`Harness.start` and is ``None`` before it is set. For
            information on the different modes, check out :doc:`cli`.

    """

    class Test:
        """
        Meta information on a single test.

        """

        def __init__(self, name, depends, func, result = None):
            self.name = name
            self.depends = [] if depends is None else depends
            self.func = func
            self.result = result

    def __init__(self):
        self.sheep_data = {}
        self.tests = {}
        self.execution_mode = None

    def _parse_arguments(self, args = sys.argv[1:]):
        """
        _parse_arguments(args = sys.argv[1:])

        Parses command line arguments.

        :param args: A list of command line arguments to parse. Should not
                include the usual zeroeth argument specifying the executable's
                name.
        :returns: A two tuple, ``(options, args)``. For the meaning of each item
                in the tuple, see the documentation for
                `optparse.OptionParser.parse_args() <http://docs.python.org/2/library/optparse.html#parsing-arguments>`.

        """

        from optparse import OptionParser, make_option

        option_list = [
            make_option(
                "-m", "--mode", dest = "mode", action = "store",
                default = "galah", choices = ("galah", "test"),
                help = "Specify the mode of execution the Test Harness is in. "
                       "Default mode is %default."
            ),
            make_option(
                "-s", "--set-value", dest = "values", action = "append",
                nargs = 2, metavar = "KEY VALUE",
                help = "Sets one of the 'configuration' values."
            )
        ]

        parser = OptionParser(
            description =
                "A test harness created with the Galah Interact library.",
            option_list = option_list
        )

        options, args = parser.parse_args(args)

        return (options, args)

    @staticmethod
    def _guess_values():
        """
        Guesses values for the key value pairs in sheep_data. For more
        information on this check out :doc:`cli`.

        """

        return {
            "testables_directory": os.getcwd(),
            "harness_directory": os.path.dirname(_utils.get_root_script_path()),
            "raw_submission": None,
            "raw_assignment": None,
            "raw_harness": None,
            "actions": UniverseSet()
        }

    def start(self, arguments = sys.argv[1:]):
        """
        start(self, arguments = sys.argv[1:])

        Takes in input from the proper source, initializes the harness with
        values it needs to function correctly.

        :param arguments: A list of command line arguments that will be read to
                determine the harness's behavior. See below for more information
                on this.
        :returns: ``None``

        .. seealso::

            :doc:`cli`

        """

        options, args = self._parse_arguments(arguments)

        self.execution_mode = options.mode
        if options.mode == "galah":
            json = json_module()
            self.sheep_data = json.load(sys.stdin)
        elif options.mode == "test":
            self.sheep_data = Harness._guess_values()

            if options.values is not None:
                JSON_FIELDS = (
                    "raw_submission", "raw_assignment", "raw_harness", "actions"
                )

                for k, v in options.values:
                    value = v
                    if k in JSON_FIELDS:
                        json = json_module()
                        value = json.loads(v)

                    self.sheep_data[k] = value
        else:
            raise ValueError(
                "Execution mode is set to a value that is not recognized: %s",
                    (options.mode, )
            )

    def finish(self, score = None, max_score = None):
        """
        Marks the end of the test harness. When start was not initialized via
        command line arguments, this command will print out the test results in
        a human readable fashion. Otherwise it will print out JSON appropriate
        for Galah to read.

        """

        if score is None or max_score is None:
            new_score = 0
            new_max_score = 0
            for i in self.tests.values():
                if i is not None:
                    if i.result.score:
                        new_score += i.result.score

                    if i.result.max_score:
                        new_max_score += i.result.max_score

            if score is None:
                score = new_score

            if max_score is None:
                max_score = new_max_score

        if self.execution_mode == "test":
            for i in self.tests.values():
                if i.result:
                    print i.result
                    print "-------"
            print "Final result: %d out of %d" % (score, max_score)
        elif self.execution_mode == "galah":
            import json
            results = {
                "score": score,
                "max_score": max_score,
                "tests": []
            }

            for i in self.tests.values():
                if i is not None:
                    results["tests"].append(i.result.to_galah_dict(i.name))

            json.dump(results, sys.stdout)
        else:
            # A bad execution mode should be detected in the start() function.
            # This is our fault if a user encounters this (and didn't set
            # execution_mode themselves).
            raise AssertionError("Unknown execution mode.")

    def test(self, name, depends = None):
        """
        A decorator that takes in a test name and some dependencies and makes
        the harness aware of it all.

        """

        def test_decorator(func):
            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            self.tests[inner] = Harness.Test(name, depends, inner)

            return inner

        return test_decorator

    class CyclicDependency(RuntimeError):
        def __init__(self, *args, **kwargs):
            RuntimeError.__init__(self, *args, **kwargs)

    class FailedDependencies(TestResult):
        """
        A special :class:`TestResult` used by :meth:`Harness.run_tests` whenever
        a test couldn't be run do to one of its dependencies failing.

        .. code-block:: python

            >>> a = interact.Harness.FailedDependencies()
            >>> a.add_failure("Program compiles")
            >>> a.add_failure("Program is sane")
            >>> print a
            Score: 0 out of 10

            This test will only be run if all of the other tests it depends on pass first. Fix those tests *before* worrying about this one.

             * Dependency *Program compiles* failed.
             * Dependency *Program is sane* failed.

        """

        def __init__(self, max_score = 10):
            TestResult.__init__(
                self,
                brief = "This test will only be run if all of the other tests it "
                        "depends on pass first. Fix those tests *before* worrying "
                        "about this one.",
                score = 0,
                max_score = 10
            )

        def add_failure(self, test_name):
            """
            Adds a new failure message to the test result signifying a
            particular dependency has failed.

            """

            self.add_message(
                "Dependency *{dependency_name}* failed.",
                dependency_name = test_name
            )

    def run_tests(self):
        """
        Runs all of the tests the user has registered.

        :raises: :class:`Harness.CyclicDependency` if a cyclic dependency exists
                among the test functions.

        Any tests that can't be run due to failed dependencies will have
        instances of :class:`Harness.FailedDependencies` as their result.

        """

        # Do a topological sort with a simple depth-first-search algorithm.
        # Thank you wikipedia for the pseudocodeand inspiration:
        # http://en.wikipedia.org/wiki/Topological_sorting
        temporary_marks = set()
        permanent_marks = set()

        def visit(node):
            if node in temporary_marks:
                raise Harness.CyclicDependency(
                    "One or more cyclic dependencies exist among your test "
                    "functions."
                )

            if node not in permanent_marks:
                # Temporarily mark the node. This is necessary because if we
                # end up hitting a node that has a temporary mark as we recurse
                # through the "DAG", it means we have a cycle. Hitting a
                # permanently marked node when we're recursing is fine because
                # all that means is two nodes share the same dependency.
                temporary_marks.add(node)

                dependencies_failed = []
                for dependency in (self.tests[i] for i in node.depends):
                    if visit(dependency).result.is_failing():
                        dependencies_failed.append(dependency)

                temporary_marks.remove(node)
                permanent_marks.add(node)

                if not dependencies_failed:
                    node.result = node.func()
                else:
                    node.result = Harness.FailedDependencies()
                    for i in dependencies_failed:
                        node.result.add_failure(i.name)

            return node

        for test in self.tests.values():
            visit(test)

    def student_file(self, filename):
        """
        Given a path to a student's file relative to the root of the student's
        submission, returns an absolute path to that file.

        """

        testables_directory = \
            self.sheep_data.get("testables_directory", "../submission/")

        path = os.path.join(testables_directory, filename)

        # Ensure that we return an absolute path.
        return _utils.resolve_path(path)

    def student_files(self, *args):
        """
        Very similar to student_file. Given many files as arguments, will return
        a list of absolute paths to those files.

        """

        return [self.student_file(i) for i in args]
