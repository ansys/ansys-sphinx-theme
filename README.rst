PyAnsys Sphinx Theme
====================
|pyansys| |python| |pypi| |GH-CI| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/badge/Python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue
   :target: https://pypi.org/project/pyansys-sphinx-theme/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-templates.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pyansys-sphinx-theme
   :alt: PyPI

.. |GH-CI| image:: https://github.com/pyansys/pyansys-sphinx-theme/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pyansys-sphinx-theme/actions/workflows/ci_cd.yml
   :alt: CH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code_style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


Introduction and Purpose
------------------------
The PyAnsys Sphinx theme is an extension of the popular `PyData
Sphinx Theme <https://pydata-sphinx-theme.readthedocs.io/>`_ used by
`numpy <https://numpy.org/doc/stable/>`_, `pandas
<https://pandas.pydata.org/docs/>`_, `PyVista
<https://docs.pyvista.org>`_ and a variety other packages.  This theme
was packaged so that all PyAnsys packages would look and behave
consistently. 


Documentation
~~~~~~~~~~~~~
Full documentation can be found at `PyAnsys Sphinx Theme Documentation <https://sphinxdocs.pyansys.com>`_. The webpage was
also built using the ``pyansys-sphinx-theme``, so visit the site for a
preview of the theme.

Other PyAnsys packages using the PyAnsys theme include:

- `PyMAPDL <https://mapdldocs.pyansys.com/>`__
- `PyAEDT <https://aedtdocs.pyansys.com/>`__
- `DPF-Core <https://dpfdocs.pyansys.com/>`__
- `DPF-Post <https://postdocs.pyansys.com/>`__
- `Legacy PyMAPDL Reader <https://readerdocs.pyansys.com/>`__


Getting Started
~~~~~~~~~~~~~~~
Install this theme with:

.. code::

   pip install pyansys-sphinx-theme

Next, modify your sphinx ``conf.py`` to use ``html_theme =
'pyansys_sphinx_theme'``.  If you are new to using
Sphinx, see `Sphinx Getting Started
<https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_
documentation.

For usage information, see `Using this Theme
<https://sphinxdocs.pyansys.com/usage.html>`_


Development and Contributing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Feel free to add features or post issues. To develop this theme::

   git clone https://github.com/pyansys/pyansys-sphinx-theme.git
   pip install -U pip tox
   tox -e style,doc

We use `pre-commit <https://pre-commit.com/>`_ to simplify style checks. You can
optionally use this by following the `installation
<https://pre-commit.com/#install>`_ and `usage
<https://pre-commit.com/#usage>`_ guides.


License
~~~~~~~
This theme is licensed under the `MIT License
<https://raw.githubusercontent.com/pyansys/pyansys-sphinx-theme/main/LICENSE>`_.
