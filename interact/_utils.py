def default_repr(obj):
    """
    Returns a string that would be appropriate to return from a repr() call. The
    string will be of the form `ClassName(attribute1 = value, ...)`.

    """

    attributes = sorted(obj.__dict__.items(), key = lambda x: x[0])
    attribute_strings = []
    for key, value in attributes:
        if not key.startswith("_"):
            attribute_strings.append(key + " = " + repr(value))

    return "%s(%s)" % (obj.__class__.__name__, ", ".join(attribute_strings))

def cleanse_quoted_strings(line):
    """
    Removes all quoted strings from the line. Single quotes are treated the
    same as double quotes.

    """

    # Returns ' if " is given, returns " if ' is given.
    inv_quote = lambda x: "'" if x == "\"" else "\""
    is_quote = lambda x: x in ["\"", "'"]

    unquoted_string = []

    in_quotes = None
    for i, char in enumerate(line):
        # Check to see if this character is escaped (this will occur if there is
        # an odd number of back slashes in front of it).
        num_slashes = 0
        for j in reversed(range(0, i)):
            if line[j] == "\\":
                num_slashes += 1
            else:
                break
        escaped = num_slashes % 2 == 1

        if char == in_quotes and not escaped:
            in_quotes = None
            continue
        elif is_quote(char) and in_quotes is None:
            in_quotes = char
            continue

        if in_quotes is None:
            unquoted_string.append(char)

    return "".join(unquoted_string)

cleanse_quoted_strings(r'hi "bob\"by" hi "billy" joe')

import unittest
class TestIndentChecking(unittest.TestCase):
    def test_indent_level(self):
        # Specific inputs to run through
        test_cases = (
            (r"""this "is" some "quoted" 'strings"all"'""", "this  some  "),
            ("", ""),
            ("""'""""""hi'hi""", "hi"),
            ("''''''''''''''''", ""),
            ('""""""""""""""""', "")
        )

        for case, expected in test_cases:
            self.assertEqual(cleanse_quoted_strings(case), expected)
