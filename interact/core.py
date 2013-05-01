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

import _utils

class TestResult:
    """
    Represents the result of one unit of testing. The goal is to generate a
    number of these and then pass them all out of the test harness with a final
    score.

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

    def set_passing(self, passing):
        self.score = 1 if passing else 0
        self.max_score = 1

    def is_passing(self):
        return self.score != 0

    def is_failing(self):
        return self.score == 0

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
