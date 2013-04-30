#!/usr/bin/env python

import interact
from interact.testsuites import *
import os.path

harness = interact.Harness()
harness.start()

student_files = harness.student_files("main.cpp")

@harness.test("Proper files exist.")
def check_files():
    return checkfiles.check_files_exist(*student_files)

@harness.test("Proper indentation is used.", depends = [check_files])
def check_indentation():
    student_files_text = [open(i).read() for i in student_files]

    results = []
    for i in range(len(student_files)):
        results.append(
            checkstyle.indentation(
                student_files_text[i],
                os.path.basename(student_files[i])
            )
        )

    return results[0]

harness.run_tests()

harness.finish(max_score = 11)
