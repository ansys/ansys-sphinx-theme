*********
404 pages
*********
Because Sphinx does not create a 404 page by default, you can use the
`sphinx-notfound-page
<https://sphinx-notfound-page.readthedocs.io/en/latest/index.html>`_ extension
for 404 pages. While originally developed to be used with `Read the Docs <https://readthedocs.org/>`_,
this extension can be used in other hosting services. For more
information, see the extension's `documentation <https://sphinx-notfound-page.readthedocs.io/en/latest/how-it-works.html>`_. 

Installation 
------------
Install and enable the ``sphinx-notfound-page`` extension with:

.. code-block:: text

    python -m pip install sphinx-notfound-page

Consider adding this extension to your ``requirements_doc.txt`` file.

Configuration
-------------
After installing the ``sphinx-notfound-page`` extension, add it to
your ``conf.py`` file:

.. code-block:: python

    # Add the extension
    extensions = [
        ...,
        "notfound.extension",
    ]

    # Add a contact mail to the theme options
    html_theme_options = {
        ...,
        "contact_mail": "pyansys.support@ansys.com",
    }

Default 404 page
----------------
To use the default 404 page that the ``ansys-sphinx-theme`` package supplies,
add the following lines in ``conf.py``:

.. code-block:: 

    from ansys_sphinx_theme import page_404


    # Configure sphinx-notfound-page
    notfound_template = page_404

.. _sphinx-notfound-page: https://sphinx-notfound-page.readthedocs.io/en/latest/index.html

Custom 404 page
---------------
To create a custom 404 page for your project, start by creating a ``404.rst``
file next to the ``conf.py`` file. Make sure you include the ``:orphan:`` attribute
at the top of this ``404.rst`` file to suppress the spurious ``document isn't
included in any toctree`` Sphinx warning.

.. code-block:: rst

    :orphan:
    
    Error 404 Not Found
    ===================
    The page you are requesting does not exist.

Update the ``notfound_template`` variable in the ``conf.py`` to the location of your
``404.rst`` file:

.. code-block:: rst

    # Configure sphinx-notfound-page
    notfound_template = "path/to/404.rst"
