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

import os.path
import interact._utils as _utils
import sys
import interact.core as core

class FailedDependencies(core.TestResult):
    def __init__(self, max_score = 10):
        core.TestResult.__init__(
            self,
            brief = "This test will only be run if all of the other tests it "
                    "depends on pass first. Fix those tests *before* worrying "
                    "about this one.",
            score = 0,
            max_score = 10
        )

class Harness:
    class Test:
        def __init__(self, name, depends, func, result = None):
            self.name = name
            self.depends = depends
            self.func = func
            self.result = result

    def __init__(self):
        self.sheep_data = {}
        self.tests = {}

    def start(self):
        """
        Marks the start of the test harness. When no command line arguments are
        present, this command will block and read JSON in from stdin. If
        command line arguments are present information will be gathered from
        them.

        """

        if len(sys.argv) == 4 and sys.argv[1] == "--test":
            self.sheep_data["harness_directory"] = \
                _utils.resolve_path(sys.argv[2])

            self.sheep_data["testables_directory"] = \
                _utils.resolve_path(sys.argv[3])
        else:
            import json
            self.sheep_data = json.load(sys.stdin)

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

        if len(sys.argv) == 4 and sys.argv[1] == "--test":
            for i in self.tests.values():
                if i.result:
                    print i.result
                    print "-------"
            print "Final result: %d out of %d" % (score, max_score)
        else:
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

    def run_tests(self):
        """
        Runs all of the tests the user has registered.

        If there is a cyclic dependency a RuntimeError will be raised.

        """

        remaining_tests = list(self.tests.keys())

        # Naively execute each test in proper order based on their
        # dependencies.
        while remaining_tests:
            # Figure out the next test to run
            to_test = None
            for i in remaining_tests:
                current_test = self.tests[i]

                # If the current test doesn't have any dependencies, let's run
                # it now.
                if not current_test.depends:
                    to_test = current_test
                    break
                else:
                    # Check all the dependencies of the current test, if they
                    # are all passing, we're done.
                    for j in current_test.depends:
                        # If one of the dependencies hasn't been run or it's
                        # failing
                        if self.tests[j].result is None:
                            break
                        elif self.tests[j].result.is_failing():
                            if not isinstance(current_test.result,
                                    FailedDependencies):
                                current_test.result = FailedDependencies()

                            current_test.result.add_message(
                                "Dependency *{dependency_name}* failed.",
                                dependency_name = self.tests[j].name
                            )
                    else:
                        if isinstance(current_test.result, FailedDependencies):
                            remaining_tests.remove(current_test.func)
                        else:
                            to_test = current_test

            if to_test is not None:
                self.tests[to_test.func].result = to_test.func()
                remaining_tests.remove(to_test.func)
            elif remaining_tests:
                raise RuntimeError("Cyclic dependencies!")
            else:
                break

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
