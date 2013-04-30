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

import os, re
from interact._utils import resolve_path
from subprocess import Popen, PIPE

# These are necessary to allow STL types in python
std_interfaces = ['std_deque.i', 'std_list.i', 'std_map.i', 'std_pair.i',
                  'std_set.i', 'std_string.i', 'std_vector.i']

def generate_swig_interface(cpp_file = 'main.cpp', output_directory = '.'):
    """
    Generates a SWIG Interface file (.i) that can be compiled with SWIG to
    a shared library file that can be imported into python for testing.

    """

    output_directory = resolve_path(output_directory)
    module_name = cpp_file.split('/')[-1].strip('.cpp')
    module_path = resolve_path(cpp_file[:cpp_file.find(module_name)])
    necessary_includes = []

    # -MM flag returns all dependencies needed to compile file.
    p = Popen(['g++', '-MM', cpp_file], stdout=PIPE)
    
    # Get dependencies, minus the .o file and the white space
    depend_string = p.communicate()[0]
    depend_string = depend_string.split(':')[1].strip()
    dependencies = depend_string.split(' ')[::2]

    for include in dependencies:
        necessary_includes.append('#include "%s"' % (include))
        if '.h' in include:
            include = include.replace('.hpp', '.h')
            include = include.replace('.h', '.cpp')

            if cpp_file not in include and os.path.isfile(include):
                necessary_includes.append('#include "%s"' % (include))

    # Now, generate SWIG interface file.
    try:
        os.makedirs(output_directory)
    except OSError:
        pass

    f = open('%s/%s.i' % (output_directory, module_name), 'w')
    f.write('%%module %s\n\n' % module_name)
    for interface in std_interfaces:
        f.write('%%include "%s"\n' % interface)

    f.write('using namespace std;\n\n')
    f.write('%{\n')
    for include in necessary_includes:
        f.write('%s\n' % include)
    f.write('%}\n\n')

    # SWIG cannot import global include like iostream, but it does need
    # all local includes
    local_includes = (include for include in necessary_includes 
                      if '<' not in include)
    for include in local_includes:
        f.write('%s\n' % include.replace('#', '%'))
    f.close()

    return module_name
