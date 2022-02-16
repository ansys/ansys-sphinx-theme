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
the body of documentation pages to make navigation easier. These 
breadcrumbs are disabled by default. To add
breadcrumbs to the pages of your documentation, in the ``conf.py``
file, add ``"show_breadcrumbs": True`` to the ``html_theme_options`` dictionary.

If you want to add additional 'root' breadcrumbs, such as to the PyAnsys
Documentation homepage, add them to the ``html_theme_options`` dictionary as a
list of tuples with the ``"additional_breadcrumbs"`` key. The tuples are of the
form ``("Link text", "url")``.

For example, this theme uses the following ``html_theme_options``:

.. code:: python

   html_theme_options = {
       "github_url": "https://github.com/pyansys/pyansys-sphinx-theme",
       "show_prev_next": False,
       "show_breadcrumbs": True,
       "additional_breadcrumbs": 
   }

When on the module homepage, a breadcrumb will be displayed with the homepage
title.  However, this title is not accessible to Sphinx from other
documentation pages. Therefore, the ``html_short_title`` is used as the display
text for the documentation homepage breadcrumb. To ensure a consistent user
experience you should ensure the ``html_short_title`` (or optionally
``html_title`` if ``html_short_title`` is not used) is set to the same value as
the title of the ``index.rst`` page. For example:

.. code:: python

   html_short_title = html_title = 'PyAnsys Sphinx Theme'

If you want to use the version number in
the ``index.rst`` title, use ``|version|`` to include the package version
number.
