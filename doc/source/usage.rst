****************
Using this Theme
****************

Install this theme with:

.. code::

   pip install pyansys-sphinx-theme

If you are are new to Sphinx, see the
`Sphinx Getting Started
<https://www.sphinx-doc.org/en/master/usage/quickstart.html>`_ documentation.
Next, modify your Sphinx ``conf.py`` file to use ``html_theme =
'pyansys_sphinx_theme'``. Consider using the following ``conf.py`` for this repository:

.. literalinclude:: ./conf.py
   :language: python
   

For additional configuration options, see the `Configuration
<https://pydata-sphinx-theme.readthedocs.io/en/latest/user_guide/configuring.html>`_
topic for the PyData Sphinx theme, which is the basis for the style of this 
PyAnsys theme.


Editing the CSS
~~~~~~~~~~~~~~~

If you need to edit or append to the css, create a directory named ``_static/css``
next to your ``conf.py`` file . Create your ``custom.css`` file in this directory.
For example:

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


Next, add the following to your ``conf.py`` file:

.. code:: python

    html_static_path = ['_static']
    html_css_files = ['css/custom.css']

Use your ``custom.css`` file to override the CSS style of this theme.

Adding Breadcrumbs
~~~~~~~~~~~~~~~~~~
The PyAnsys Sphinx theme supports the display of breadcrumbs on
the body of documentation pages to make navigation easier. To add
breadcrumbs to the pages of your documentation, in the ``theme.conf``
file, set ``html_theme_option`` to ``"show_breadcrumbs": True``.

If you want to add additional 'root' breadcrumbs, such as to the 
PyAnsys root page, you set ``html_theme_option`` to
``"additional_breadcrumbs": [("Link text", "href")]``.

You must manually add the breadcrumb that links to the module homepage when on
a page within the documentation. Because there is no way to get the title of the
``index.rst`` page, you must use the ``html_title`` set in the ``conf.py``
file. The problem is that this isn't necessarily the same as the title of the
``index.rst`` page.
