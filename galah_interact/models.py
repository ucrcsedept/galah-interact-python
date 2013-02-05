import json
import sys

class GalahTestPart:
    def __init__(self, name = "", score = 0, max_score = 0):
        self.name = name
        self.score = score
        self.max_score = max_score

    def to_list(self):
        return [self.name, self.score, self.max_score]

class GalahTest:
    def __init__(self, name = "", score = 0, max_score = 0, message = "",
            parts = None):
        if parts is None:
            parts = []

        self.name = name
        self.score = score
        self.max_score = max_score
        self.message = message
        self.parts = parts

    def to_dict(self):
        return {
            "name": self.name,
            "score": self.score,
            "max_score": self.max_score,
            "message": self.message,
            "parts": [i.to_list() for i in self.parts]
        }

class GalahResult:
    def __init__(self, score = 0, max_score = 0, tests = None):
        if tests is None:
            tests = []

        self.score = score;
        self.max_score = max_score
        self.tests = tests

    def to_dict(self):
        return {
            "score": self.score,
            "max_score": self.max_score,
            "tests": [i.to_dict() for i in self.tests]
        }

    def calculate_scores(self):
        """
        Sets score and max_score by summing up the scores and maximum scores of
        each test, respectively.

        """

        self.score = sum(i.score for i in self.tests)
        self.max_score = sum(i.max_score for i in self.tests)

    def send(self, send_to = sys.stdout):
        "Sends the test results out of the virtual machine to the sheep."

        json.dump(self.to_dict(), send_to)

class GalahConfig:
    def __init__(self, testables_dir = None, harness_dir = None,
            submission = None, assignment = None, harness = None,
            actions = None):
        if actions is None:
            actions = []
        self.testables_directory = testables_dir
        self.harness_directory = harness_dir
        self.submission = submission
        self.harness = harness
        self.actions = actions

    @staticmethod
    def recv(source = sys.stdin):
        "Recieves test results from outside of the virtual machine."

        values = json.load(source)

        # TODO: raw_* will all be converted into mirroredmodels that will allow
        #       access to them as if we were inside of Galah. ObjectIDs will not
        #       be deserialized because that would introduce a BSON dependency
        #       but all datetimes and other objects will be deserialized. This
        #       is not yet necessary in the test harnesses I'm creating and I
        #       don't even access those objects so this will be added later as
        #       needed.

        return GalahConfig(
            testables_dir = values["testables_directory"],
            harness_dir = values["harness_directory"],
            submission = values["raw_submission"],
            assignment = values["raw_assignment"],
            harness = values["raw_harness"],
            actions = values["actions"]
        )