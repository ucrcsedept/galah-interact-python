#!/usr/bin/env python

import interact

harness = interact.Harness()
harness.start()

student_files = harness.student_files("main.cpp")

@harness.test("Proper files exist.")
def check_files():
  return interact.standardtests.check_files_exist(*student_files)

@harness.test("Program compiles correctly.", depends = [check_files])
def check_compilation():
  return interact.standardtests.check_compiles(student_files)

@harness.test("Proper indentation is used.", depends = [check_files])
def check_indentation():
  return interact.standardtests.check_indentation(student_files)

@harness.test("foo function works correctly.", depends = [check_compilation])
def check_foo():
  result = interact.TestResult(
    brief = "This test ensures that your `foo` function correctly takes in two "
            "integer parameters and returns their sum.",
    default_message = "**Great job!** Your function works great!",
    max_score = 10
  )

  student_code = interact.unittest.load_files(student_files)

  if "foo" not in student_code["main"]:
    result.add_message("You didn't create a `foo` function.", dscore = -10)
    return result.calculate_score()

  foo = student_code["main"]["foo"]
  try:
    if foo(3, 4) != 7:
      result.add_message("Your function did not give the correct sum.")
  except TypeError:
    result.add_message("Your function does not have the correct signature.")

  return result.calculate_score(min_score = 0)

harness.run_tests()

harness.finish(max_score = 31)
