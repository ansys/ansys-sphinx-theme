.. _ref_user_guide_configuration:

Basic configuration
===================

To use the Ansys Sphinx Theme, add the following line to your project's Sphinx ``conf.py`` file:

.. code-block:: python

   html_theme = "ansys_sphinx_theme"

The Ansys Sphinx Theme provides these features:

- `PyAnsys and Ansys logos`_
- `Version switcher`_
- `PDF cover page`_
- `Custom CSS`_

PyAnsys and Ansys logos
~~~~~~~~~~~~~~~~~~~~~~~

The Ansys Sphinx Theme includes the PyAnsys and Ansys logos. All the logos
are available in the
`ansys_sphinx_theme/static/ <static_files_>`_
directory. You can use the following code to add the logos to your documentation:

.. code-block:: python

    from ansys_sphinx_theme import pyansys_logo_black, ansys_logo_black, ansys_favicon

    html_logo = pyansys_logo_black
    html_favicon = ansys_favicon

The ``favicon`` setting specifies the icon that appears in the browser tab.

Version switcher
~~~~~~~~~~~~~~~~

The Ansys Sphinx Theme includes a version switcher for switching between different versions of the documentation.
To show the version switcher in your documentation, add the following code to your project's Sphinx ``conf.py`` file:

.. code-block:: python

   from ansys_sphinx_theme import get_version_match

   version = "0.1.0"
   switcher_versions = get_version_match(version)
   cname = "your_name"
   html_theme_options = {
       "switcher": {
           "json_url": f"https://{cname}/versions.json",
           "version_match": switcher_version,
       },
   }

The switcher requires a ``versions.json`` file that contains the versions of the documentation and their URLs in the given ``json_url``.
For more information, see `PyAnsys multi-version documentation <dev_guide_multi_version_>`_ in the
*PyAnsys developer's guide*.

PDF cover page
~~~~~~~~~~~~~~

The Ansys Sphinx Theme includes a PDF cover page that you can customize.
To customize the PDF cover page, see :ref:`ref_user_guide_pdf_cover`.

Custom CSS
~~~~~~~~~~

You can add custom CSS to the Ansys Sphinx Theme by creating a directory named ``_static/css`` in
your documentation and adding the following code to your project's Sphinx ``conf.py`` file:

.. code-block:: python

   html_static_path = ["_static"]
   html_css_files = ["css/custom.css"]

Here is an example of a custom CSS file that changes the background color
of the body to black and the text color to white:

.. code-block:: css

   .body {
       background-color: black;
      color: white;
   }

