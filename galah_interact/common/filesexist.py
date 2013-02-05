import os.path
from ..pretty import plural_if, pretty_list
def files_exist(config, files, all_or_nothing = True, critical = True):
	message = "The %s %s must be present in your submission." % (
		plural_if("file", len(files)), pretty_list(files)
	)

	if critical:
		message += " If any file is missing no further tests will be performed."

	extant_files = [i for i in files if
			os.path.isfile(os.path.join(config.testables_directory, i))]

	if all_or_nothing:
		score = 1 if len(extant_files) == len(files) else 0
		max_score = 1
	else:
		score = len(extant_files)
		max_score = len(files)

	return {
		"score": score,
		"max_score": max_score,
		"message": message,
		"critical": critical and score != max_score
	}