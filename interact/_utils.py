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

def swig_wrapper_name(template_name, template_arguments):
    """
    Constructs a template wrapper name to be used in SWIG template generation.

    :param template_name: The name of the template itself.
    :param template_arguments: The template arguments to be considered.

    :returns: A template wrapper name needed by SWIG.

    This combines a template name and all of its arguments into a CamelCase
    pythonic class to be provided by the SWIG wrapper. The result will be in the
    following format: Arg0...Argn-1TemplateName. For example, if the template
    instance found in the C++ source is map<int, string>, the resulting wrapper
    name would be IntStringMap in the generated python module. Note that order
    matters and this is different from StringIntMap, which would be represented
    in C++ as map<string, int>.
    """
    wrapped_arguments = [i.title() for i in template_arguments \
                             if i != 'iterator']
    wrapper_name = "".join(wrapped_arguments)
    wrapper_name += template_name.title()
    return wrapper_name

import re
def filter_non_type_arguments(template_instance, non_type_args=[]):
    """
    Filters non-type arguments from a template instance.

    :param template_instance: A fully expanded template instance.
    :param non_type_args: Expected non-type arguments to be filtered out.

    :returns: An expanded template instance excluding non-type arguments.

    This steps through the template_instance's arguments and if any of the
    arguments are in the list of non_type_args, they will be excluded.
    For example, if the template_instance is
    `std::set<int, std::allocator<int>, std::less<int> >` and
    `std::allocator` and `std::less` are considered to be non_type_args,
    the resulting template will be std::set<int>.
    """
    # Get template type name and arguments
    match = re.search('(\S*)<(.*)>', template_instance)
    if not match:
        return template_instance
    template_name = match.group(1)
    template_args = match.group(2).split(', ')

    # Filter out non-type parameters.
    type_parameters = []
    for arg in template_args:
        angle_pos = arg.find('<')
        if angle_pos == -1 or arg[:angle_pos] not in non_type_args:
            type_parameters.append(arg)

    # Combine template with type parameters.
    filtered_instance = '%s<%s >' % (template_name, ', '.join(type_parameters))
    return filtered_instance

from clang import cindex
Kind = cindex.CursorKind
Token = cindex.TokenKind

# A list of class template arguments that are not types.
# These include operator classes and memory allocation classes.
STD_NON_TYPES = [
    "std::allocator", "std::less", "std::less_equal", "std::greater",
    "std::greater_equal", "std::equal_to", "std::not_equal_to"
]
def discover_template_instances(node, root_source_file, discovered_instances={}):
    """
    Discover all template instances being used in the parsed source code.

    :param node: The current node in this translation unit.
    :param root_source_file: The relative or absolute file path of the source.

    :returns: A map containing discovered template instances, with
              the SWIG wrapper name as the key and the C++ instance
              as the value.

    Recursively walks through the indexed source code to discover template
    instances. This is useful for helping us automatically wrap template
    instances with SWIG.
    """
    template_instances = discovered_instances
    children = node.get_children()
    for child in children:
        child_file = child.location.file
        if child_file is not None and \
                is_local_include(root_source_file, child_file.name):
            if child.kind in [Kind.VAR_DECL, Kind.FIELD_DECL,
                              Kind.PARM_DECL]:
                template_inst = child.type.get_declaration().displayname

                # SWIG automatically creates iterators.
                if 'iterator' in template_inst:
                    continue

                # If the template belongs to a namespace, prepend it to the type
                namespace = child.type.get_declaration().lexical_parent
                if namespace is not None and namespace.kind == Kind.NAMESPACE:
                    template_inst = '%s::%s' % (namespace.displayname,
                                                template_inst)
                template_inst = filter_non_type_arguments(template_inst,
                                                          STD_NON_TYPES)

                # If this variable declaration uses a template, it will be
                # the first child.
                try:
                    first_child = child.get_children().next()
                    if first_child.kind != Kind.TEMPLATE_REF:
                        raise StopIteration

                    # Pull out type name and arguments from tokens.
                    # Ignore all qualifiers and find identifiers.
                    tokens = child.get_tokens()
                    for token in tokens:
                        if token.kind == Token.IDENTIFIER:
                            break

                    template_type = token.spelling
                    arguments = []

                    # Pull out built-in and declared template type arguments.
                    for token in tokens:
                        if token.kind in [Token.IDENTIFIER, Token.KEYWORD]:
                            arguments.append(token.spelling)
                        elif token.spelling == '>':
                            # Finished looking at template arguments
                            break

                    # Construct SWIG template name and associate with C++
                    # instance if it doesn't already exist.
                    swig_template_name = swig_wrapper_name(template_type,
                                                           arguments)

                    if swig_template_name not in template_instances.keys():
                        template_instances[swig_template_name] = template_inst
                except StopIteration:
                    continue
        
        # Discover the types of my children.
        template_instances = discover_template_instances(child,
                                                         root_source_file,
                                                         template_instances)

    return template_instances
