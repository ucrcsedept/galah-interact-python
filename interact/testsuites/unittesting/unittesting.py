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

from interact._utils import resolve_path
from interact.swig import *

import os
import imp
import inspect

import atexit
import shutil
import tempfile

to_delete = []

def cleanup():
    for i in to_delete:
        shutil.rmtree(i)
atexit.register(cleanup)

def load_cpp_files(cpp_files):
    module_dict = {}
    modules = []

    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)

    for f in cpp_files:
        modules.append(generate_swig_interface(f))

    interface_files = ("%s.i" % (module) for module in modules)
    generate_swig_wrappers(interface_files)
    generate_shared_libraries(modules)

    for module in modules:
        module_dict[module] = {}
        mod = imp.load_source(module, '%s.py' %
                              (temp_dir + '/' + module))

        # Get all functions and classes in this module
        for name, impl in inspect.getmembers(mod,
                                             lambda a: (inspect.isbuiltin(a) or
                                                        inspect.isclass(a))):
            module_dict[module][name] = impl

    to_delete.append(temp_dir)

    return module_dict
