.. Galah Interact documentation master file, created by
   sphinx-quickstart on Thu May  2 23:05:56 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Galah Interact
==========================================

This is the main documentation for the Galah Interact project. The contents of this site are automatically generated via `Sphinx <http://sphinx-doc.org/>`_ based on
the Python docstrings throughout the code and the reStructuredText documents in
the
`docs/ directory <https://github.com/galah-group/galah-interact-python/tree/master/docs>`_
of the git repository. If you find an error in the documentation, please report
it in the bug tracker `here <https://www.github.com/galah-group/galah/issues>`__
(which we share with the Galah project), or even better, submit a pull request!

What is Galah Interact
------------------------------------------

Galah Interact is a library designed to make it very easy to create Test
Harnesses that grade student's assignments. It provides code to perform a
number of tests that many instructors care about (such as checking that code is
properly indented, or that code compiles without any warnings) along with
providing utilities to make more complicated testing much easier (unit testing
for example is extremely easy with this library, as you can
:doc:`simply import all of the student's functions and classes into Python <guides/unittesting>`).

The reason for Galah Interact's creation was to make it easier to create Test
Harnesses for `Galah <http://www.github.com/galah-group/galah>`_, however, we
don't have any intention on locking in this library's use (this is why we've
released it under the very permissive :ref:`licensing`). The real goal of
Galah Interact is to provide a powerful framework for creating excellent
test harnesses no matter what the submission system you are using for your
class is.

**Galah Interact can only test C++ code right now.** We would really like to
support other languages as well, so if you are interested in using this library
at your university that teaches using a different language, please let us know
so we can work with you.

Tutorials, Examples, and Guides
------------------------------------------

If you have not used this library before, you should start your journey by going
through these tutorials.

.. toctree::
	:maxdepth: 2

	guides/getting_started
	guides/unittesting

Reference Material
------------------------------------------

To get documentation on a specific function or module, or if you just want to
browse through all of what Galah Interact has to offer, check out the below
pages.

.. toctree::
   :maxdepth: 2

   interact/interact
   interact/cli

Quick Sample
------------------------------------------

To give you an idea of what using this library feels like, below is a simple but
fairly complete test harness for an assignment where the students must make a
``foo()`` function that takes in two numbers and returns their sum.

:download:`teaser.py <guides/examples/teaser/teaser.py>`

.. literalinclude:: guides/examples/teaser/teaser.py

When running this harness with ``./teaser.py --mode test``, and a correctly
implemented ``main.cpp``
(:download:`example here <guides/examples/teaser/main.cpp>`), the following is
output:

.. literalinclude:: guides/examples/teaser/teaser_output.txt

.. _licensing:

Licensing
---------------------------------------------

The code is licensed under the Apache 2.0 license, which is a very permissive
license. You can read a summary of its specific terms on the wikipedia page
for the license
`here <http://en.wikipedia.org/wiki/Apache_License#Licensing_conditions>`_. The
entire license text is also contained within this repository if you'd like to
read the license itself.

In short, the license is very permissive and lets you do basically whatever you
want with the code as long as you properly attribute the contributers. So as
long as you don't rip out the code and say you wrote it, your probably staying
within the terms of the license.

Note that this license is very different than the license that covers
`Galah <http://www.github.com/galah-group/galah>`_ itself. Please don't confuse
the two.
