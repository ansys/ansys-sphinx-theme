************
Installation
************
`Sphinx <https://www.sphinx-doc.org/en/master/>`_. is a Python
documentation generator for creating documentation. If you are new to
using Sphinx, see `Sphinx Getting Started <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_.

Install the Ansys Sphinx theme with:

.. code::

   pip install ansys-sphinx-theme

Configuration
-------------
To use this theme, you must modify your Sphinx ``conf.py`` file::

   html_theme ='ansys_sphinx_theme'

Consider using the ``conf.py`` for this repository:

.. literalinclude:: ./conf.py
   :language: python
   
Customization
-------------
The other sections of this guide provide information on how you can
customize the Ansys Sphinx theme. For more information, see `Configuration
<https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/configuring.html>`_
for the PyData Sphinx theme on which the Ansys Sphinx theme is based.
