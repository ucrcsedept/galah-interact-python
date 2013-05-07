Unit Testing
==========================================

One of the coolest modules in Galah Interact is the :mod:`unittest` module. It
allows you to "load" any number of C++ files such that all of the native C++
classes and functions become available as Python classes and functions. This is
done by leveraging the absolutely fantastic
`SWIG library <http://www.swig.org/>`_ which can automatically create bindings
from C++ to a plethora of other languages. Please give the SWIG project as much
support as you can as it is really a wonderful product.

In order to use the :mod:`unittest` module, you need to make sure that you have
SWIG installed, and that you have *Python development headers* installed, both
of which are probably available through your distribution's package manager
(``apt-get`` or ``yum`` for example).

Basic Unit Testing
------------------------------------------

Once you have it installed, you can start poking around with the following code.

:download:`main.cpp <examples/unittest_tutorial/main.cpp>`

.. literalinclude:: examples/unittest_tutorial/main.cpp

:download:`harness.py <examples/unittest_tutorial/harness.py>`

.. literalinclude:: examples/unittest_tutorial/harness.py

Running the above Python script gives the following output:

.. literalinclude:: examples/unittest_tutorial/output.txt

It should be clear that this makes it fairly easy to unit test some student's
code. You may notice that the ``bar`` function above prints out to standard
output. This is a little problematic if you want to test what that function
outputs, and it's actually even more problematic in that if your harness prints
things out to standard output when in Galah, the test server will get angry
because you'll make it so that the output is no longer proper JSON. To solve
this, there is another handy library called :mod:`interact.capture`.

Using the :mod:`interact.capture` module
------------------------------------------

The :mod:`interact.capture` module exposes a function
:func:`capture_function <interact.capture.capture_function>` that forks a
process before running a given function, and captures anything written to
``stdout`` or ``stderr`` (and even lets you control ``stdin``). All while also
allowing you to get the return value of the function and seeing any exceptions
that are raised.

Using this function, we can test the ``bar`` function trivially.

.. literalinclude:: examples/unittest_tutorial/harness_with_capture.py

Running the above Python scripts outputs:

.. literalinclude:: examples/unittest_tutorial/output_with_capture.txt
