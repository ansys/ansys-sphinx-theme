****************
Using this Theme
****************

Install this theme with:

.. code::

   pip install pyansys-sphinx-theme

If you are just getting started using sphinx, follow the directions at `Sphinx
Quickstart <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_.
Next, modify your sphinx ``conf.py`` to use ``html_theme =
'pyansys_sphinx_theme'``.


Configurating this Theme
~~~~~~~~~~~~~~~~~~~~~~~~
This theme extends the PyData-Sphinx-Theme theme and can be configured by
following the directions at `PyData Theme Configuration`_.

The PyAnsys Sphinx also theme includes extra configuration parameters, including
a top of page "breadcrumb" link tree that can be helpful when navigating
documentation. This webpage uses the following configuration:

.. code:: python

   html_title = 'PyAnsys Sphinx Theme'

   html_theme_options = {
       "show_breadcrumbs": True,
       "additional_breadcrumbs": [('PyAnsys', 'https://docs.pyansys.com')],
   }

This provides links back to the main PyAnsys documentation page at
`docs.pyansys.com <https://docs.pyansys.com>`_ while also providing the reader
with a clear location of where they are within the documentation. Note that the
title of the project should be configured with ``html_title`` as the default
html title may be less than ideal.


Example Configuration
~~~~~~~~~~~~~~~~~~~~~

This theme uses the following configuration found at `conf.py <https://github.com/pyansys/pyansys-sphinx-theme/blob/main/doc/source/conf.py>`_:

.. literalinclude:: ./conf.py
   :language: python   

For additional configuration options, see `PyData Theme Configuration`_.


Editing the CSS
~~~~~~~~~~~~~~~

If you need to edit or append to the css, create a directory next to
your ``conf.py`` named ``_static/css`` containing your ``custom.css``
file.  For example:

.. code::

   body {
    font-family: 'Source Sans Pro', sans-serif;
    color: black;
    padding-top:calc(var(--pst-header-height))
   }
   footer{display:none}
   main{
     overflow: auto;
     height: calc(100vh - 3.8rem);
     overflow-y: scroll;
   }  
   .prev-next-bottom{margin-bottom: 6rem}


Next, add the following to ``conf.py``:

.. code:: python

    html_static_path = ['_static']
    html_css_files = ['css/custom.css']

This way you can override the CSS style of this theme.


.. _PyData Theme Configuration: https://pydata-sphinx-theme.readthedocs.io/en/v0.4.2/user_guide/configuring.html
