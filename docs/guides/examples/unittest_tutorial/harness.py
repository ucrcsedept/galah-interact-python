import interact

student_code = interact.unittest.load_files(["main.cpp"])

print "---Running bar(3, 4)---"
return_value = student_code["main"]["bar"](3, 4)
print return_value

print "---Creating new Foo objects---"
Foo = student_code["main"]["Foo"]
new_foo = Foo(3)
new_foo_default = Foo()

print "---Printing get_a() on each foo instance---"
print new_foo.get_a()
print new_foo_default.get_a()

print "---Printing a_ value directly on each foo instance---"
print new_foo.a_
print new_foo_default.a_
