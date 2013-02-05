import tempfile
import subprocess
from os.path import join
import os

NULL_FILE = open("/dev/null", "w")

directories_to_delete = []
def run_unittest(config, user_files, unittest, inputs = ""):
	if not isinstance(inputs, (list, tuple)):
		inputs = [inputs]

	temp_dir = tempfile.mkdtemp()
	directories_to_delete.append(temp_dir)

	compilation_jobs = []

	# Compile the main file but hide the main with a dirty define.
	compilation_jobs.append(subprocess.Popen(
		[
			"g++",
			"-c",
			"-Dmain=user_main",
			join(config.testables_directory, user_files[0])
		],
		cwd = temp_dir,
		stdout = NULL_FILE,
		stderr = subprocess.STDOUT
	))

	compilation_jobs.append(subprocess.Popen(
		["g++", "-c", join(config.harness_directory, unittest)],
		cwd = temp_dir
	))

	# Compile each of the other supplied files normally.
	for i in user_files[1:]:
		compilation_jobs.append(subprocess.Popen(
			["g++", "-c", join(config.testables_directory, i)],
			cwd = temp_dir,
			stdout = NULL_FILE,
			stderr = subprocess.STDOUT
		))

	# Wait until all the files are compiled into object files.
	for i in compilation_jobs:
		i.wait()
		if i.returncode != 0:
			return None

	# Grab all the generated object files
	object_files = [
		join(temp_dir, i) for i in os.listdir(temp_dir) if i.endswith(".o")
	]

	# Link the files together
	linking_job = subprocess.Popen(
		["g++", "-o", "main"] + object_files,
		cwd = temp_dir,
		stdout = NULL_FILE,
		stderr = subprocess.STDOUT
	)
	linking_job.wait()

	if linking_job.returncode != 0:
		return None

	main_binary_path = join(temp_dir, "main")
	if not os.path.isfile(main_binary_path):
		return None

	main_jobs = []
	for i in inputs:
		main_jobs.append(subprocess.Popen(
			[main_binary_path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.STDOUT
		))

		main_jobs[-1].stdin.write(i)
		main_jobs[-1].stdin.close()

	resulting_output = []
	for i in main_jobs:
		i.wait()
		resulting_output.append(i.stdout.read())

	return resulting_output


import shutil
def cleanup():
	"""Removes any temporary files/directories created by the module."""

	for i in directories_to_delete:
		shutil.rmtree(i)