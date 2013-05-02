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
Module useful for displaying nice, grammatically correct output.

"""

def pretty_list(the_list, conjunction = "and", none_string = "nothing"):
    """
    Returns a grammatically correct string representing the given list. For
    example...

    >>> pretty_list(["John", "Bill", "Stacy"])
    "John, Bill, and Stacy"
    >>> pretty_list(["Bill", "Jorgan"], "or")
    "Bill or Jorgan"
    >>> pretty_list([], none_string = "nobody")
    "nobody"

    """

    the_list = list(the_list)

    if len(the_list) == 0:
        return none_string
    elif len(the_list) == 1:
        return str(the_list[0])
    elif len(the_list) == 2:
        return str(the_list[0]) + " " + conjunction + " " + str(the_list[1])
    else:
        # Add every item except the last two together seperated by commas
        result = ", ".join(the_list[:-2]) + ", "

        # Add the last two items, joined together by a command and the given
        # conjunction
        result += "%s, %s %s" % \
            (str(the_list[-2]), conjunction, str(the_list[-1]))

        return result

def plural_if(zstring, zcondition):
    """
    Returns zstring pluralized (adds an 's' to the end) if zcondition is True or
    if zcondition is not equal to 1.

    Example usage could be ``plural_if("cow", len(cow_list))``.

    """

    # If they gave us a boolean value, just use that, otherwise, assume the
    # value is some integral type.
    if type(zcondition) is bool:
        plural = zcondition
    else:
        plural = zcondition != 1

    return zstring + ("s" if plural else "")

def limit_string_length(string, max_lines = 20, max_characters = 20 * 72):
    # If the string is empty, we don't need to do anything.
    # if not string:
        # return string

    # Negative values are bad
    if max_lines < 0:
        raise TypeError("max_lines cannot be negative, got %d." % (max_lines, ))
    elif max_characters < 0:
        raise TypeError(
            "max_characters cannot be negative, got %d." % (max_lines, )
        )

    nlines_truncated = 0
    lines = string.splitlines()
    if len(lines) > max_lines:
        nlines_truncated = len(lines) - max_lines
        lines = lines[:max_lines]

    ncharacters_truncated = 0
    if len(string) > max_characters:
        ncharacters_truncated = len(string) - max_characters
        string = string[:max_characters]

    return (string, nlines_truncated, ncharacters_truncated)

def truncate_string(string, max_lines = 20, max_characters = 20 * 72):
    new_string, nlines_truncated, ncharacters_truncated = limit_string_length(
        string, max_lines, max_characters
    )

    if ncharacters_truncated == 0 and nlines_truncated == 0:
        return new_string
    else:
        return new_string + "\n---Remaining text truncated---"

def craft_shell_command(command):
    """
    Returns a shell command from a list of arguments suitable to be passed into
    subprocess.Popen. The returned string should only be used for display
    purposes and is not secure enough to actually be sent into a shell.

    """

    return " ".join([escape_shell_string(i) for i in command])

def escape_shell_string(str):
    """
    Escapes a shell string such that it is suitable to be displayed to the user.
    This function **should not** be used to actually feed arguments into a shell
    as this function **is not** secure enough.

    """

    escaped = str.replace("\\", "\\\\").replace("\"", "\\\"")
    if " " in escaped:
        escaped = "\"" + escaped + "\""

    return escaped
