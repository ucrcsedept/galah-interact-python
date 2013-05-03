#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "galah-interact",
    version = read("VERSION"),
    author = "Galah Group LLC and other contributers",
    author_email = "jsull003@ucr.edu",
    description = (
        "A Python framework for creating test harnesses to grade students' "
        "code."
    ),
    license = "Apache v2.0",
    keywords = "education framework",
    url = "https://www.github.com/galah-group/galah-interact-python",
    packages = ["interact", "interact_test"],
    long_description = read("README.md"),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
    ],
)
