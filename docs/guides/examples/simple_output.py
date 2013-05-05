#!/usr/bin/env python

import interact
import os.path

# The Harness class is an idempotent object you should only ever make one of
# that takes care of a lot of the boilerplate for you. You should always copy
# and paste these two lines of code to the top of every test harness you create.
harness = interact.Harness()
harness.start()

# Get a list of absolute paths to the student's files (in this case, we only
# care about their main.cpp file).
student_files = harness.student_files("main.cpp")

# The line below starting with @harness.test is how we designate that certain
# functions are test functions that return TestResult objects (more on this
# in a bit). The argument here is what the user sees as the name of the test
# that is run, the function name has no real significance and is only used to
# reference the test function when needed.
@harness.test("Proper files exist.")
def check_files():
	# Checking to make sure certain files exist is a very typical thing for
	# Test Harnesses to do so Galah Interact ships with a standard test to do
	# it for you. The * before student files is expanding the list student_files
	# such that each item in the list will be treated as a seperate argument to
	# the function (this is because check_files_exist takes in variadic
	# arguments, ex: check_files_exist("main.cpp", "foo.cpp", "bar.cpp")).
    return interact.standardtests.check_files_exist(*student_files)

# Notice the `depends = [check_files]` line here. This is how you can create
# dependencies between tests. Here we are saying that this test should only be
# run if the check_files test passed. Any number of tests can be given there
# (this is a Python list) and Galah Interact will make sure to run things in the
# correct order.
@harness.test("Program compiles correctly.", depends = [check_files])
def check_compilation():
	# Similar to checking if files exist, checking to see if a student's code
	# compiles is also a very common test, so Galah Interact has a function to
	# make it very simple.
    return interact.standardtests.check_compiles(student_files)

@harness.test("Program prints out hello world.", depends = [check_compilation])
def check_output():
	# This is the first time you actually get a good look at a TestResult
	# object. The standard tests above actually return an instance of this
	# class. The brief argument is some text that is always displayed no matter
	# what the result of the testing is. You should try to describe the test
	# that is being run briefly here, so students are not confused. The
	# default message argument is only displayed if you don't add any other
	# messages to the TestResult object.
	result = interact.TestResult(
		brief = "This test ensures that your program prints out a single line "
		        "of output that reads `Hello World!`.",
		default_message = "**Great job!** Your program correctly prints out "
		                  "`Hello World!`.",
		max_score = 10
	)

	# Interact has a handy function that will automatically compile and run
	# some code files. If the code has already been compiled by interact, it
	# will not recompile it, but rather it will use the executable that was
	# already compiled, so don't worry about extraneous work being done here.
	# run_program returns a tuple and it is being unpacked into the variables
	# output, stderr, and return_code.
	output, stderr, return_code = \
		interact.execute.run_program(student_files)

	# Get a list of lines in the output, ignoring any blank lines. The thing
	# surrounded by square brackets is called a list comprhension and is a very
	# useful Python feature that you should familiarize yourself with.
	output_lines = [i for i in output.splitlines() if i]

	# Here is my first actual test. I see if the user printed out any extra
	# lines.
	if len(output_lines) != 1:
		# By adding this message, the default message I defined when I created
		# the TestResult instance will not be shown. Notice how I insert nlines
		# into the messages, you can do this with any number of values. dscore
		# is a special value that you can set to assign a "change of score", or
		# delta score, to the message. Here I am signifying that if this message
		# is added, the score should shrink by 5.
		result.add_message(
			"Your program output {nlines} line(s), remember, your program "
			"should print out exactly 1 line of output.",
			nlines = len(output_lines),
			dscore = -5
		)

	# This is another Python construct that may look strange to those
	# unfamiliar with it. Notice that the for loop actually has an else attached
	# to it. The code in the else block will only be executed if we never break
	# from within the for loop.
	for i in output_lines:
		if i == "Hello World!":
			break
	else:
		# If we add this message along with the one above they will simply be
		# displayed one after the other in a bulleted list (even if only one
		# is displayed they will still be put into a bulletted list for
		# consitency, though it is possible to override this behavior).
		result.add_message(
			"Your program did not print out a line that reads `Hello World!`.",
			dscore = -5
		)

	# calculate_score() is a convenience function that automatically tallies up
	# the dscores of the various messages that have been added and assigns an
	# appropriate total score to the TestResult. It takes a couple of optional
	# arguments to suite most styles of grading, so check out the reference
	# material on this function.
	result.calculate_score()

	# Test functions always return TestResult. All of the standard tests return
	# TestResult objects (and you can actually inspect the TestResult objects
	# they return in order to customize the grading scale and such).
	return result

# This function will execute each of the test functions in the proper order
# based on their dependencies and save the results within the Harness object.
harness.run_tests()

# This function will output the results (either as readable text if you used
# the --test . . arguments to start the test harness, or as JSON appropriate
# for Galah's test servers to read in if not). Make sure to set the max_score
# appropriately because unfortunately the harness will not be able to correctly
# guess the appropriate max_score in all cases (notably when some test functions
# aren't run due to dependencies failing).
harness.finish(max_score = 21)
