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

@harness.test("Program compiles correctly.", depends = [check_files])
def check_compilation():
    return outputtesting.check_compiles(student_files)

@harness.test("Program prints out hello world.", depends = [check_compilation])
def check_output():
	result = interact.core.TestResult(
		brief = "This test ensures that your program prints out a single line "
		        "of output that reads `Hello World!`.",
		default_message = "**Great job!** Your program correctly prints out "
		                  "`Hello World!`.",
		max_score = 10
	)

	output, stderr, return_code = outputtesting.run_program(student_files)

	# Get a list of lines in the output, ignoring any blank lines.
	output_lines = [i for i in output.splitlines() if i]

	if len(output_lines) != 1:
		result.add_message(
			"Your program output {nlines} line(s), remember, your program "
			"should print out exactly 1 line of output.",
			nlines = len(output_lines),
			dscore = -5
		)

	for i in output_lines:
		if i == "Hello World!":
			break
	else:
		result.add_message(
			"Your program did not print out a line that reads `Hello World!`.",
			dscore = -5
		)

	result.calculate_score()

	return result

harness.run_tests()

harness.finish(max_score = 21)
