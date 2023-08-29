Ansys Sphinx theme
==================
|ansys| |python| |pypi| |GH-CI| |MIT| |black|

.. |ansys| image:: https://img.shields.io/badge/Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://github.com/ansys
   :alt: Ansys

.. |python| image:: https://img.shields.io/badge/Python-%3E%3D3.8-blue
   :target: https://pypi.org/project/ansys-sphinx-theme/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-sphinx-theme.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-sphinx-theme
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/ansys-sphinx-theme/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/ansys-sphinx-theme/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code_style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |Downloads| image:: https://img.shields.io/pypi/dm/ansys-sphinx-theme.svg?label=PyPI%20downloads
   :target: https://pypi.org/project/ansys-sphinx-theme
   :alt: Downloads


Introduction
------------
The Ansys Sphinx theme is an extension of the popular
`PyData Sphinx theme <https://github.com/pydata/pydata-sphinx-theme>`_ 
that is used by `numpy <https://numpy.org/doc/stable/>`_,
`pandas <https://pandas.pydata.org/docs/>`_,
`pyvista <https://docs.pyvista.org>`_, and many more
scientific Python packages.

You use the Ansys Sphinx theme with `Sphinx <https://www.sphinx-doc.org/en/master/>`_,
a Python documentation generator, to create documentation.
The theme's objective is to ensure that Ansys documentation
looks and behaves consistently.

While this theme is primarily used to create documentation
for PyAnsys libraries, you can also use it to create
documentation for any Ansys project with content in
reStructuredText (RST) and Markdown (files).

If you are new to using Sphinx, see `Sphinx Getting Started
<https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_.

Documentation and issues
~~~~~~~~~~~~~~~~~~~~~~~~
In addition to installation information, the
`Ansys Sphinx theme documentation <https://sphinxdocs.ansys.com>`_
provides information on how you can customize the theme. Because
this documentation is created using this theme, viewing it is
an easy way to preview the theme itself.

On the `Issues page <https://github.com/ansys/ansys-sphinx-theme/issues>`_
for this repository, you can create issues to submit questions, report bugs,
and request new features. To reach the PyAnsys support team, email
`pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Getting started
~~~~~~~~~~~~~~~
Install the ``ansys-sphinx-theme`` package with:

.. code::

   python -m pip install ansys-sphinx-theme

Modify your Sphinx ``conf.py`` file to use ``html_theme =
'ansys_sphinx_theme'``.

Development and contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you want to contribute to the PyAnsys Sphinx theme, install
the ``ansys-sphinx-theme`` package in development mode with::

   git clone https://github.com/ansys/ansys-sphinx-theme.git
   python -m pip install -U pip tox
   tox -e style,doc

To simplify checks, this repository uses `pre-commit <https://pre-commit.com/>`_.
You can optionally install and use this tool. For more information, see its
`installation <https://pre-commit.com/#install>`_ and `usage
<https://pre-commit.com/#usage>`_ documentation.

Before contributing to a PyAnsys library, see
`Contributing <https://dev.docs.pyansys.com//how-to/contributing.html>`_ 
in the *PyAnsys Developer's Guide* for overall guidance, paying particular
attention to `How-to <https://dev.docs.pyansys.com//how-to/index.html>`_ for 
guidelines and best practices. 

License
~~~~~~~
This theme is licensed under the `MIT License
<https://raw.githubusercontent.com/ansys/ansys-sphinx-theme/main/LICENSE>`_.
