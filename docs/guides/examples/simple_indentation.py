#!/usr/bin/env python

import interact
import os.path

harness = interact.Harness()
harness.start()

student_files = harness.student_files("main.cpp")

@harness.test("Proper files exist.")
def check_files():
    return interact.standardtests.check_files_exist(*student_files)

@harness.test("Proper indentation is used.", depends = [check_files])
def check_indentation():
    return interact.standardtests.check_indentation(student_files)

harness.run_tests()

harness.finish(max_score = 11)
