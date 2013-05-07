import interact
from interact.capture import capture_function

student_code = interact.unittest.load_files(["main.cpp"])

captured_function = capture_function(student_code["main"]["bar"], 3, 4)

# Wait for the function to end.
captured_function.wait()

print "The function returned:", repr(captured_function.return_value)
print "The function wrote to stdout:", repr(captured_function.stdout.read())
print "The function wrote to stderr:", repr(captured_function.stderr.read())
