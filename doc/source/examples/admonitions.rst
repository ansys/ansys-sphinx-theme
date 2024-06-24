.. _admonitions:

Admonitions
===========

Admonitions are a way to highlight important information in your documentation. They are a way to draw attention to important information,
and can be used to provide additional context or information to the reader.

This page shows how the admonitions are rendered in the documentation with ansys sphinx theme.


.. jinja:: admonitions

    {% for filename in inputs_admonitions %}

    .. include:: sphinx_examples/{{ filename }}

    {% endfor %}

Credits and Copyright
---------------------

The examples shown below are derived from the PyData Sphinx Theme project, copyrighted by pandas, 2018.
Original examples can be found at `PyData sphinx theme examples <pydata_examples>`_.
These examples are licensed under the BSD 3-Clause License.

Original Copyright
~~~~~~~~~~~~~~~~~~

The examples included here were originally copyrighted and licensed as follows:

- Copyright (c) 2021, Pradyun Gedam. Licensed under the Creative Commons Attribution-ShareAlike 4.0 International License
  (SPDX-License-Identifier: CC-BY-SA-4.0), as specified by PyData Sphinx theme in their examples.