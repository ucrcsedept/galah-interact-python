Test Harness Command Line Interface
===========================================

When you run your test harness from the command line, certain command
line arguments have significance, and are parsed when
:func:`interact.core.Harness.start` is called.

You can find a brief description of the command line arguments available
by running your harness with the ``--help`` option (ex:
``./my_harness.py --help``). This document attempts to be a more thorough
description of behavior.

Basic Usage
------------------------------------------

When you run your harness (that you created using the Galah Interact library)
you use the following flags to control the behavior of the harness.

``-m``, ``--mode`` *MODE*
    Use this flag to set the execution mode of the harness. The default mode
    is ``galah``. See :ref:`execution-mode` for more information.

``-s``, ``--set-value`` *KEY* *VALUE*
    Use this flag (multiple times if desired) to set "configuration" values
    when in ``test`` mode.  See :ref:`configuration-values` for more
    information.

Examples
******************************************

If we want to start a harness in ``test`` mode and let the harness guess all of
the values...

.. code-block:: bash

    ./my_harness.py --mode test

If we want to start a harness in ``test`` mode and set the testables directory
(where the student's code is) to another directory...

.. code-block:: bash

    ./my_harness.py --mode test --set-value testables_directory ./student1/

If we want to start a harness in ``test`` mode and set the testables directory
along with providing a fake submission object...

.. code-block:: bash

    ./my_harness.py --mode test --set-value testables_directory ./student1/ --set-value raw_submission "{'id': 'junk', 'user': 'john'}"

.. _execution-mode:

Execution Modes
------------------------------------------

The mode of execution (set with the ``--mode`` option) determines how the
test harness will gather the information it needs to run, and how it
outputs the results once they are available.

``galah`` mode
******************************************

In ``galah`` mode, when the test harness starts it will try to read in JSON
from standard input, and when it finishes the output will be sent to
standard output as JSON. This is not a very human-friendly process and
generally you don't want to set it to this mode during development of
a test harness.

**If you harness seems like it's not responding when you start it, it's probably
running in this mode and is waiting for an entire JSON object to be placed into
stdin.**

This mode exists for when the test harness is being run within Galah.

``test`` mode
******************************************

In ``test`` mode, the test harness will try to guess any values it needs
(and you can specify values explictly using ``--set-value``) and then print
out the results in a human-friendly way. You should always use this mode
during the development of your test harness.

.. _configuration-values:

Configuration Values
------------------------------------------

Test harnesses need certain information in order to function
properly. In galah mode, you must specify them all with JSON, but in
test mode the harness will attempt to guess some values, and you can
override any of the guesses by using the ``--set-value`` command line
argument. If you use ``--set-value`` with any argument that expects a
list or dictionary, the value you set will be assumed to be JSON and
will be deserialized.

These values are available in
:class:`interact.core.Harness.sheep_data <interact.core.Harness>` from within
the test harness.

.. note::

    The below keys are case-sensitive.

**KEY** (*DEFAULT VALUE*):
    DESCRIPTION

**testables_directory** (*current directory*):
    The directory that contains the student's code.

**harness_directory** (*directory of the running test harness*):
    The directory that contains the test harness itself.

**raw_submission** (*None*):
    A submission object with meta data on the student's submission. In
    Galah, this is a dictionary with at least the following fields:

    .. code-block:: python

        {
            "id": "ID of submission in database",
            "assignment": "ID of assignment in database",
            "user": "username of student",
            "timestamp": "submission time in ISO format"
        }

    If specified with --set-value, the string supplied will be assumed
    to be a valid JSON object and will be deserialized.

**raw_assignment** (*None*):
    An assignment object with meta data on the assignment this harness
    is attached to. In Galah, this is a dictionary with at least the
    following fields:

    .. code-block:: python

        {
            "name": "The name of the assignment",
            "due": "due date in ISO format",
            "due_cutoff": "cutoff date in ISO format",
            "hide_until": "hide until field in ISO format"
        }

**raw_harness** (*None*):
    A harness object with meta data about the test harness. In Galah,
    this is a dictionary with at least the following fields:

    .. code-block:: python

        {
            "config": "dictionary supplied when harness was uploaded",
            "id": "ID of harness in database"
        }

**actions** (*instance of* :class:`interact.core.UniverseSet`):
    A list of actions that the test harness should perform. This is not yet
    fully supported within Galah. As such there's not full support for it in
    Galah Interact yet.
