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

    def __init__(self, score = None, messages = None):
        if messages is None:
            messages = []

        self.score = score
        self.messages = messages

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


