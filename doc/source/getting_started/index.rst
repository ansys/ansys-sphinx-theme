.. _ref_getting_started:

Getting started
###############

This section explains how to install the Ansys Sphinx theme and then set up your
Sphinx ``conf.py`` file to use this theme to generate your documentation.
If you are interested in contributing to the theme, see the `PyAnsys Contributing <Pyansys_contributing>`_ for
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
   `user guide <autoapi>`_.

Install the theme
=================

#. Before installing `ansys-sphinx-theme` make sure that you have the latest version of pip with this command:

.. code::

   python -m pip install --upgrade pip

#. Install the theme using pip:

.. code::

   pip install ansys-sphinx-theme

For installing the optional dependencies, use:

.. code::

   pip install ansys-sphinx-theme[autoapi]


Add the theme to your Sphinx project
=====================================

To use the Ansys Sphinx theme, you need to modify your Sphinx ``conf.py`` file.

.. code:: python

   html_theme = "ansys_sphinx_theme"

.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _Sphinx_PyPI: https://pypi.org/project/Sphinx/
.. _PyData_PyPI: https://pypi.org/project/pydata-sphinx-theme/
.. _Jinja2_PyPI: https://pypi.org/project/Jinja2/
.. _Sphinx_AutoAPI_PyPI: https://pypi.org/project/sphinx-autoapi/
.. _Sphinx_Design_PyPI: https://pypi.org/project/sphinx-design/
.. _Sphinx_Jinja_PyPI: https://pypi.org/project/sphinx-jinja/
.. _pip: https://pypi.org/project/pip/
.. _Pyansys_contributing: https://dev.docs.pyansys.com/how-to/contributing.html