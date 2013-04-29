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

from distutils.core import setup, Extension
from distutils.cmd import Command
from interact._utils import resolve_path

def generate_shared_libraries(modules = ['main'], wrapper_directory = '.'):
    """
    Compiles modules and wrappers to shared libraries using distutils.

    """

    wrapper_directory = resolve_path(wrapper_directory)
    for module in modules:
        so_name = '_%s' % module
        wrapper_file = '%s/%s_wrap.cxx' % (wrapper_directory, module)
        mod_ext = Extension(so_name, sources=[wrapper_file],
                            )
        setup(name = module,
              ext_modules = [mod_ext],
              py_modules = [module],
              script_name = 'setup.py',
              script_args = ['build_ext', '--inplace']
              )
