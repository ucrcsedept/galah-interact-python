# Copyright (c) 2013 Galah Group LLC
# Copyright (c) 2013 Other contributers as noted in the CONTRIBUTERS file
#
# This file is part of galah-interact-python.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains very useful functions you can use while unittesting
student's code.

.. note::

    In order to use the :mod:`unittest` module, you need to make sure that you
    have SWIG installed, and that you have *Python development headers*
    installed, both of which are probably available through your distribution's
    package manager (``apt-get`` or ``yum`` for example).

"""

import interact._utils as _utils
import os
import imp
import inspect
import atexit
import shutil
import tempfile
import subprocess
import os.path
import distutils.core
import capture
from clang import cindex

#: The absolute path to the swig executable. When this module is imported, the
#: environmental variable ``PATH`` is searched for a file named ``swig``, this
#: variable will be set to the first one that is found. This variable will equal
#: ``None`` if no such file could be found.
swig_path = _utils.which("swig")

class CouldNotCompile(RuntimeError):
    """
    Exception raised when a student's code could not be compiled into a single
    library file.

    :ivar message: A short message describing the exception.
    :ivar stderr: The output that was received through standard error. This is
            output by ``distutils.core.setup``.

    """

    def __init__(self, message, stderr):
        self.message = message
        self.stderr = stderr
        RuntimeError.__init__(self)

    def __str__(self):
        output = [
            self.message,
            "---BEGIN STDERR---",
            self.stderr,
            "---END STDERR---"
        ]

        return "\n".join(output)

def _build_extension(module, mod_ext, working_directory):
    os.chdir(working_directory)
    distutils.core.setup(
        name = module,
        ext_modules = [mod_ext],
        py_modules = [module],
        script_name = "setup.py",
        script_args = ["build_ext", "--inplace"]
    )

def _generate_shared_libraries(modules, wrapper_directory):
    """
    Compiles modules and wrappers to shared libraries using distutils.

    :raises: :class:`CouldNotCompile` if the extension could not be compiled.

    """

    wrapper_directory = _utils.resolve_path(wrapper_directory)

    for module in modules:
        so_name = "_%s" % (module, )
        wrapper_file = os.path.join(wrapper_directory, module + "_wrap.cxx")
        mod_ext = distutils.core.Extension(
            str(so_name), sources = [str(wrapper_file)]
        )

        try:
            captured = capture.capture_function(
                _build_extension, str(module), mod_ext, str(wrapper_directory)
            )
            captured.wait()
        except SystemExit:
            # Setup will call exit which can make the running script exit rather
            # suddenly. At least give the user an error with a traceback.
            raise CouldNotCompile(
                "Could not compile extension module.",
                stderr = captured.stderr.read()
            )

def _generate_swig_wrappers(interface_files, output_directory):
    """
    Generates SWIG Wrapper files (.cxx) and python modules that can be
    compiled into a shared library by distutils.

    :raises: ``EnvironmentError`` if swig is not installed.

    """

    if swig_path is None:
        raise EnvironmentError("No swig executable found.")

    output_directory = _utils.resolve_path(output_directory)

    for current_file in interface_files:
        module_name = _utils.file_name(current_file)
        output_file = os.path.join(
            output_directory, "%s_wrap.cxx" % (module_name, )
        )

        # Let swig generate the wrapper files.
        subprocess.check_call(
            [swig_path, "-c++", "-python", "-o", output_file, current_file],
            cwd = output_directory,
            stdout = _utils.DEVNULL,
            stderr = subprocess.STDOUT
        )

# These are necessary to allow STL types in python
STD_INTERFACES = [
    "std_deque.i", "std_list.i", "std_map.i", "std_pair.i", "std_set.i",
    "std_string.i", "std_vector.i", "std_sstream.i"
]

# Template types that will always be given an interface along with the amount of template
# parameters they can take.
STL_TEMPLATES = {
    "deque": 1, 
    "list": 1, 
    "map": 2,
    "pair": 2,
    "set": 1,
    "vector": 1
}

# Basic types to expose to templates
BASIC_TYPES = [
    # Need to think of way to add support for `long long` or `long int`, etc
    "char", "double", "float", "int", "long", "string"
]

# C++ Directives that expose extra functionality in the underlying C++ code.
EXPOSURE_DIRECTIVES = [
    "#define private public", # Expose private member variables to module
    "#define protected public",
    "#define class struct" # Expose unmarked private member variables
]

def _generate_swig_interface(file_path, output_directory):
    """
    Generates a SWIG Interface file (.i) that can be compiled with SWIG to
    a shared library file that can be imported into python for testing.

    """

    file_path = _utils.resolve_path(file_path)
    output_directory = _utils.resolve_path(output_directory)

    # Figure out what this module will be named by getting just the filename
    # (minus extension) of the code file.
    module_name = _utils.file_name(file_path)

    # Parse the source file's path and get the local includes.
    index = cindex.Index.create()

    # Cut off a little time preprocessing by caching the included files.
    tu = index.parse(file_path,
                     options=cindex.TranslationUnit.PARSE_PRECOMPILED_PREAMBLE)
    dependencies = [i.include.name for i in tu.get_includes() \
                        if _utils.is_local_include(file_path, i.include.name)]

    # Must always include the original source file as well.
    dependencies.append(file_path)

    necessary_includes = []
    for include in dependencies:
        necessary_includes.append("#include \"%s\"" % (include))

        # TODO: Add comment describing what's going on here.
        if ".h" in include:
            include = include.replace(".hpp", ".h")
            include = include.replace(".h", ".cpp")

            if file_path not in include and os.path.isfile(include):
                necessary_includes.append("#include \"%s\"" % (include))

    types_tuple = _utils.discover_types(tu.cursor, tu.spelling,
                                        BASIC_TYPES, STL_TEMPLATES)
    final_non_templates, final_templates = types_tuple
    template_wrappers = _utils.generate_template_wrappers(final_non_templates,
                                                          final_templates)

    with open(os.path.join(output_directory, module_name + ".i"), "w") as f:
        f.write("%%module %s\n\n" % (module_name, ))

        # Ensure we include all of the special swig interface files that allow
        # us to interop with the C++ Standard Library.
        for interface in STD_INTERFACES:
            f.write("%%include \"%s\"\n" % (interface, ))

        # Write directives inside and out of wrapper for consistency in wrapped
        # file.
        f.write("\n".join(EXPOSURE_DIRECTIVES) + "\n")
        f.write("using namespace std;\n\n")
        f.write("%{\n")
        f.write("\n".join(EXPOSURE_DIRECTIVES) + "\n")
        for include in necessary_includes:
            f.write("%s\n" % include)
        f.write("%}\n\n")

        # SWIG cannot import global include like iostream, but it does need
        # all local includes
        local_includes = \
            (include for include in necessary_includes if '<' not in include)
        for include in local_includes:
            f.write("%s\n" % include.replace("#", "%"))
        for type_name, instance in template_wrappers.iteritems():
            f.write("%%template(%s) %s;\n" % (type_name, instance))

    return module_name

to_delete = []

def _cleanup():
    for i in to_delete:
        shutil.rmtree(i)
atexit.register(_cleanup)

def load_files(files):
    """
    Compiles and loads functions and classes in code files and makes them
    callable from within Python.

    :param files: A list of file paths. All of the files will be compiled and
            loaded together.
    :returns: A ``dict`` where every file that was passed in is a key in the
            dictionary (without its file extension) and the value is another
            ``dict`` where each key is the name of a function or class in the
            file and the value is a callable you can use to actually execute
            or create an instance of that function or class.

    :raises: ``EnvironmentError`` if swig is not properly installed.
    :raises: :class:`CouldNotCompile` if the student's code could not be
            compiled into a library file.

    .. warning::

        During testing, oftentimes the execution of loaded code's ``main()``
        function failed. We haven't determined what the problem is yet so for
        now don't use this function to test ``main()`` functions (the
        :mod:`interact.execute` module should work well instead).

    .. code-block:: python

        >>> print open("main.cpp").read()
        #include <iostream>

        using namespace std;

        class Foo {
            int a_;
        public:
            Foo(int a);
            int get_a() const;
        };

        Foo::Foo(int a) : a_(a) {
            // Do nothing
        }

        int Foo::get_a() const {
            return a_;
        }

        int bar() {
            Foo foo(3);
            cout << "foo.get_a() = " << foo.get_a() << endl;
            return 2;
        }

        int main() {
            return 0;
        }
        >>> students_code = interact.unittest.load_files(["main.cpp"])
        >>> Foo = students_code["main"]["Foo"]
        >>> bar = students_code["main"]["bar"]
        >>> b = Foo(3)
        >>> b.get_a()
        3
        >>> rvalue = b.bar()
        foo.get_a() = 3
        >>> print rvalue
        2

    If you want to test a function that prints things to stdout or reads from
    stdin (like the ``bar()`` function in the above example) you can use the
    :mod:`interact.capture` module.

    """

    module_dict = {}

    # Get a directory we can work within.
    temp_dir = tempfile.mkdtemp()

    modules = []
    for f in files:
        modules.append(_generate_swig_interface(f, temp_dir))

    interface_files = ((module + ".i") for module in modules)
    _generate_swig_wrappers(interface_files, temp_dir)
    _generate_shared_libraries(modules, temp_dir)

    for module in modules:
        module_dict[module] = {}

        # Load up the python module we created whose function will let us access
        # the C++ ones.
        created_module = os.path.join(temp_dir, module + ".py")
        mod = imp.load_source(module, created_module)

        # Get all functions and classes in this module
        filter_func = lambda a: inspect.isbuiltin(a) or inspect.isclass(a)
        for name, impl in inspect.getmembers(mod, filter_func):
            module_dict[module][name] = impl

    to_delete.append(temp_dir)

    return module_dict
