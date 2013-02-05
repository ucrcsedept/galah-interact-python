import sys
import models

class TestDescription:
	def __init__(self, test_func, test_func_args = None,
			test_func_kwargs = None, error_func = None, result_args = None):
		self.test_func = test_func
		self.error_func = error_func

		if test_func_args is None:
			test_func_args = []

		if test_func_kwargs is None:
			test_func_kwargs = {}

		if result_args is None:
			result_args = {}

		self.test_func_args = test_func_args
		self.test_func_kwargs = test_func_kwargs
		self.result_args = result_args

class TestRunner:
	def __init__(self, config, test_descriptions = None,
			total_calculator = None, suppress_errors = False):
		if test_descriptions is None:
			test_descriptions = []
		self.test_descriptions = test_descriptions
		self.total_calculator = total_calculator
		self.config = config
		self.suppress_errors = suppress_errors

	def run_tests(self):
		results = models.GalahResult()

		for i in self.test_descriptions:
			# This will hold the arguments we will pass to the TestResult
			# object.
			resulting_arguments = i.result_args.copy()

			try:
				test_result = i.test_func(
					self.config, *i.test_func_args, **i.test_func_kwargs
				)
			except Exception as e:
				if isinstance(e, SyntaxError):
					raise

				# If the user supplied an error function use it to resolve this
				# error, otherwise explode or skip this test based on the user's
				# choice.
				if i.error_func is not None:
					i.error_func(i, e)
				elif self.suppress_errors:
					continue
				else:
					raise

			if isinstance(test_result, tuple):
				assert 1 <= len(test_result) <= 5

				if len(test_result) >= 1:
					resulting_arguments["score"] = test_result[0]

				if len(test_result) >= 2:
					resulting_arguments["max_score"] = test_result[1]

				if len(test_result) >= 3:
					resuling_arguments["message"] = test_result[2]

				if len(test_result) >= 4:
					resulting_arguments["parts"] = test_result[3]

				if len(test_result) >= 5:
					resulting_arguments["name"] = test_result[4]
			elif isinstance(test_result, dict):
				resulting_arguments.update(test_result)
			elif isinstance(test_result, (int, long, float)):
				# We'll assume the test_result is a number (the score).
				resulting_arguments["score"] = test_result
			else:
				raise TypeError("test_func returned invalid object.")

			critical = False
			if "critical" in resulting_arguments:
				critical = resulting_arguments["critical"]
				del resulting_arguments["critical"]

			results.tests.append(models.GalahTest(**resulting_arguments))

			if critical:
				break

		if self.total_calculator is None:
			return results
		else:
			return self.total_calculator(self.config, results)
