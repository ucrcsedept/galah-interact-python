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
#: An open file descriptor ready for writing that goes directly to the null file
#: device (``/dev/null`` on Linux).
DEVNULL = open(os.devnull, "wb")

def default_repr(obj):
    """
    :returns: A string that would be appropriate to return from a repr() call.
            The string will be of the form `ClassName(attribute1 = value, ...)`.

    """

    attributes = sorted(obj.__dict__.items(), key = lambda x: x[0])
    attribute_strings = []
    for key, value in attributes:
        if not key.startswith("_"):
            attribute_strings.append(key + " = " + repr(value))

    return "%s(%s)" % (obj.__class__.__name__, ", ".join(attribute_strings))

import os.path
def resolve_path(path):
    return os.path.abspath(os.path.expanduser(path))

import inspect
def get_root_script_path():
    """
    :returns: An absolute path to the file that is actually being executed.
            As in if this module is imported by some other module that was
            imported by a script ``/tmp/bla.py``, this function will return
            ``/tmp/bla.py``.

    """

    return resolve_path(inspect.stack()[-1][1])

import os.path
def file_name(file_path):
    """
    :param file_path: A relative or absolute file path.
    :returns: The name of the file, without the extension.

    >>> utils.get_file_name("/tmp/applesauce.tgz")
    "applesauce"
    >>> utils.get_file_name("../../foo.txt")
    "foo"

    """

    return os.path.splitext(os.path.basename(file_path))[0]

import os
import os.path
def which(program_name):
    """
    Simulates the Linux utility ``which``.

    :param program_name: The name of the program to search for, should include
            any necessary extensions.
    :returns: An absolute path to the found program.

    This is done by searching for a file with ``program_name`` in the path.

    """

    path = os.environ.get("PATH", "").split(":")
    for i in path:
        possible_path = os.path.join(i, program_name)

        if os.path.exists(possible_path):
            return possible_path

    return None

import os
import os.path
def is_local_include(source_file_path, candidate_file_path):
    """
    Check if a file header is a local include relative to a source file.

    :param source_file_path: The relative or absolute file path of the source.
    :param candidate_file_path: The relative or absolute file path of the
                                candidate.
    :returns: True is the candidate file is a local include.

    This is done by seeing if the candidate_file_path's directory is a
    descendant of the source_file_path's directory.
    """
    return os.path.dirname(source_file_path) in \
        os.path.dirname(candidate_file_path)

from clang import cindex
Kind = cindex.CursorKind
def discover_types(node, root_source_file, known_non_template_types=[],
                   known_template_types={}):
    """
    Discover all extra types being used in the parsed source code.

    :param node: The current node in this translation unit.
    :param root_source_file: The relative or absolute file path of the source.
    :param known_non_template_types: The non-templated types that are known so
                                     far.
    :param known_template_types: The template types that are known so far with
                                 keys of template names and values of parameter
                                 count.

    :returns: A 2-tuple containing all known types, with non-templated types
              first followed by templated types.

    Recursively walks through the indexed source code to discover used types,
    new classes, new templates (classes and functions), and instantiations.
    This is useful for helping us automatically wrap template instances with
    SWIG.
    """
    final_non_template_types = known_non_template_types
    final_template_types = known_template_types

    children = node.get_children()
    for child in children:
        child_file = child.location.file
        if child_file is not None and \
                is_local_include(root_source_file, child_file.name):
            if child.kind in [Kind.CLASS_DECL, Kind.STRUCT_DECL]:
                # Add new classes to non template types.
                new_class_name = child.displayname
                if new_class_name not in final_non_template_types:
                    final_non_template_types.append(new_class_name)
            elif child.kind == Kind.CLASS_TEMPLATE:
                # Add new template types to templates.
                new_template_name = child.spelling
                if new_template_name not in final_template_types.keys():
                    # Count the amount of type parameters to template
                    types = [i for i in child.get_children() \
                                 if i.kind == Kind.TEMPLATE_TYPE_PARAMETER]
                    parameter_count = len(types)
                    final_template_types[new_template_name] = parameter_count
        
        # Discover the types of my children.
        types = discover_types(child, root_source_file,
                               final_non_template_types, final_template_types)
        final_non_template_types, final_template_types = types

    return (final_non_template_types, final_template_types)

import itertools
def generate_template_wrappers(non_template_types, template_types,
                               known_wrappers={}):
    """
    Combines template and non-template types into SWIG template wrappers.

    :param non_template_types: A list of non_template_types to be considered.
    :param template_types: A dictionary of template_types with SWIG wrappers
                           as keys and C++ instances as values

    :returns: A completed map of wrappers

    This is done by taking the two lists and computing cartesian products
    """
    completed_wrappers = known_wrappers

    argument_lengths = list(set([v for k,v in template_types.iteritems()]))
    argument_combinations = []
    # Compute cartesian products for necessary list sizes
    for i in argument_lengths:
        filtered_templates = [j[0] for j in template_types.iteritems() \
                                if j[1] == i]

        wrapper_list = [non_template_types] * i
        wrapper_list.append(filtered_templates)
        combination = itertools.product(*wrapper_list)
        argument_combinations.append(combination)

    # Add new wrappers to completed_wrappers
    for combo in argument_combinations:
        for i in combo:
            wrapped_name = "".join([j.title() for j in i])
            cpp_instance = "%s<%s>" % (
                i[-1], ", ".join(i[:-1])
            )
        
            if wrapped_name not in completed_wrappers.keys():
                completed_wrappers[wrapped_name] = cpp_instance

    return completed_wrappers
