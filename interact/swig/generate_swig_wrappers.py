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

import os
from subprocess import call
from interact._utils import resolve_path

def generate_swig_wrappers(interface_files = ['main.i'],
                           output_directory = '.'):
    """
    Generates SWIG Wrapper files (.cxx) and python modules that can be
    compiled into a shared library by distutils.

    """

    output_directory = resolve_path(output_directory)
    try:
        os.makedirs(output_directory)
    except OSError:
        pass

    for interface in interface_files:
        module_name = interface.split('/')[-1].strip('.i')
        call(["swig", "-c++", "-python", "-o",
              "%s/%s_wrap.cxx" % (output_directory, module_name), interface])
