.. _ref_getting_started:

===============
Getting started
===============
`Sphinx <https://www.sphinx-doc.org/en/master/>`_ is a Python documentation
generator for creating documentation. If you are new to using Sphinx, see
`Sphinx Getting Started <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_.

This section explains how to install the Ansys Sphinx theme and then set up your
Sphinx ``conf.py`` file to use this theme to generate your documentation.

Dependencies
------------

Ansys sphinx theme build on top of ``pydata sphinx theme``. 
The theme requires the following dependencies:

- `sphinx <https://www.sphinx-doc.org/en/master/>`_
- `pydata-sphinx-theme <https://pydata-sphinx-theme.readthedocs.io/en/latest/>`_
- `Jinja2 <https://jinja.palletsprojects.com/en/2.11.x/>`_

Optional dependencies
---------------------

Ansys Sphinx theme includes optional dependencies for autoapi documentation. 
To utilize `sphinx-autoapi` with custom templates provided by the theme, 
you need to install the following dependencies:

- `sphinx-autoapi <https://sphinx-autoapi.readthedocs.io/en/latest/>`_
- `sphinx-design <https://sphinx-design.readthedocs.io/en/latest/>`_

An example page demonstrating autoapi rendering with the Ansys sphinx theme template can
be found found on the ``API Reference`` page of the 
`PyAnsys Geometry documentation <https://geometry.docs.pyansys.com/>`_.

Install the theme
-----------------
Install the Ansys Sphinx theme with:

.. code::

   pip install ansys-sphinx-theme

For installing the optional dependencies, use:

.. code::

   pip install ansys-sphinx-theme[autoapi]

Modify the ``conf.py`` file
---------------------------
To use this theme, modify your Sphinx ``conf.py`` file::

   html_theme = "ansys_sphinx_theme"

Consider using the ``conf.py`` for this repository:

.. literalinclude:: ../conf.py
   :language: python
   :end-before: # ONLY FOR ANSYS-SPHINX-THEME

.. toctree::
   :hidden:
   :maxdepth: 2
