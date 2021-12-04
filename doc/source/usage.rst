****************
Using this Theme
****************

Install this theme with:

.. code::

   pip install pyansys-sphinx-theme

If you are just getting started using sphinx, follow the directions at
`Sphinx Quickstart
<https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_.  Next,
modify your sphinx ``conf.py`` to use ``html_theme =
'pyansys_sphinx_theme'``.  Consider using the following ``conf.py`` used in this repository:

.. literalinclude:: ./conf.py
   :language: python
   

For additional configuration options, see `Configuring The PyData
Sphinx Theme
<https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/configuring.html>`_,
which forms the basis for the style of this theme.


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
