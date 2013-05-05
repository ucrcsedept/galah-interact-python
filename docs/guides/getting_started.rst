Getting Started
==========================================

Step 1 - Installing Galah Interact
------------------------------------------

Galah Interact is a Python library. As such, the first thing you need to do is
get it installed and get to the point where you can import the library.

Note that Galah Interact only officially supports Linux at this point as the
developers don't have access to Macs. If you have a Mac and would like to help
us test the library, please let us know. Windows users, if you have a great
desire to use Galah Interact please let us know and we will try to add support.

If you want to avoid affecting the entire system, you can use a
`virtualenv <http://www.virtualenv.org/en/latest/>`_ with any of the methods,
though unless you are already familiar with Python virtual environments it may
be more trouble than its worth.

*To install Galah Interact you can choose from one of the three methods
below.*

Method 1 - Installing through pip
*******************************************

Galah Interact may be installed simply using the Python package manager pip (to
get pip see
`this page <http://www.pip-installer.org/en/latest/installing.html>`_). This
method of installation is the recommended method as it will make it a little
easier to upgrade your installation in the future, but if you do not already
have pip set up and want to go the easiest route, try Method 2 instead.

After getting pip installed, you should be able to execute
``pip install galah-interact`` on the command line. After doing so Galah Interact
will be installed automatically.

Method 2 - Installing from Source
*******************************************

If you do not wish to install pip, you can install Galah Interact a little more
directly, just follow the steps below.

 1. Go and download an archive containing Galah Interact's source either from
    the
    `list of tagged releases <https://www.github.com/galah-group/galah-interact-python/tags>`_
    or from the
    `main project page <https://www.github.com/galah-group/galah-interact-python>`_
    (this will grab the latest code in the repo).
 2. Unpack the archive somewhere.
 3. Find the file ``setup.py`` in the top-level directory and set its executable
    bit (``chmod +x setup.py``).
 4. Execute ``./setup.py install``.

Method 3 - Using Directly
******************************************

If you don't want to deal with installing the library, you can use it directly
by unpacking the archive as above, and then just copying the ``interact/``
directory into the same directory as your test harness.

Step 2 - Hello World
------------------------------------------

The typical first program for Computer Science students is the "Hello World"
program. The first Test Harness we create, then, will be a Test Harness that
grades a "Hello World" assignment. The harness is below, you can go ahead and
place it in a file with a ``.py`` extension, set the executable bit
(``chmod +x file.py``) and then run it with ``./file.py --mode test``.

The comments document each line thoroughly and make up the contents of this
tutorial, so please read through them carefully. I assume minimal Python
knowledge, so I try to describe any advanced Python features enough that you
can search for more information on them online.

.. literalinclude:: examples/simple_output.py

You can download the code above :download:`here <examples/simple_output.py>`.

When you execute a test harness file directly during testing/development, you
should always execute it with the command line arguments
``--mode test``. If you do not do this, when you run the test harness it will
appear to freeze up. It is actually waiting for JSON from standard input. This
is how the test servers in Galah communicate with test harnesses. If you
encounter this, just use ``Ctrl+C`` to kill the program and start it again
properly.

.. seealso::

	For more information on command line arguments, check out
	:doc:`../interact/cli`.

Advanced users can also use the
`Sheep Simulator <https://github.com/galah-group/galah-sheep-simulator>`_ to run
the test harnesses as if the harness was actually within a Galah test server
(which are called sheep). This should be unnecessary in most cases however, and
the simulator was created before Galah Interact had the capability to be run in
this testing mode.

