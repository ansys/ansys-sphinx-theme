.. _ref_getting_started:

Getting started
###############

This section explains how to install the Ansys Sphinx theme and then set up your
Sphinx ``conf.py`` file to use this theme to generate your documentation.
If you are interested in contributing to the theme, see the `PyAnsys Contributing <dev_guide_contributing_>`_ for
information on installing the theme in development mode.

Package dependencies
====================
Ansys sphinx theme build on top of ``pydata sphinx theme``.
The theme requires the following dependencies:

- `Sphinx <Sphinx_PyPI_>`_
- `pydata-sphinx-theme <PyData_PyPI_>`_
- `Jinja2 <Jinja2_PyPI_>`_

Optional dependencies
---------------------
Ansys Sphinx theme includes optional dependencies for autoapi documentation.
To utilize `sphinx-autoapi` with `autoapi` extension provided by the theme,
you need to install the following dependencies:

- `sphinx-autoapi <Sphinx_AutoAPI_PyPI_>`_
- `sphinx-design <Sphinx_Design_PyPI_>`_
- `sphinx-jinja <Sphinx_Jinja_PyPI_>`_

.. note::
   To see how to use the autoapi extension with the Ansys sphinx theme, refer to the
   :ref:`ref_user_guide_autoapi`.

Install the theme
=================

#. Before installing `ansys-sphinx-theme` make sure that you have the latest version of pip with this command:

.. code-block:: bash

   python -m pip install --upgrade pip

#. Install the theme using pip:

.. code-block:: bash

   pip install ansys-sphinx-theme

For installing the optional dependencies, use:

.. code-block:: bash

   pip install ansys-sphinx-theme[autoapi]


Add the theme to your Sphinx project
=====================================

To use the Ansys Sphinx theme, you need to modify your Sphinx ``conf.py`` file.

Add the following lines to your ``conf.py`` file::

   html_theme = 'ansys_sphinx_theme'