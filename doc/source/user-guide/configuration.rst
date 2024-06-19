.. _ref_user_guide_configuration:

Basic configuration
===================

Add the following to your `conf.py` file to use the Ansys Sphinx theme:

.. code-block:: python

   html_theme = "ansys_sphinx_theme"

From ansys sphinx theme you can use the following features:

1. PyAnsys and Ansys logos
~~~~~~~~~~~~~~~~~~~~~~~~~~

The Ansys Sphinx theme includes the PyAnsys and Ansys logos. All The logos
are available in the
`ansys_sphinx_theme/static/ <static_files_>`_
directory. You can use the following code to add the logos to your documentation:

.. code-block:: python

    from ansys_sphinx_theme import pyansys_logo_black, ansys_logo_black, ansys_favicon

    html_logo = pyansys_logo_black
    html_favicon = ansys_favicon

``favicon`` is the icon that appears in the browser tab.

#. **Version switcher**

   The Ansys Sphinx theme includes a version switcher that allows users to switch between different versions of the documentation.
   To use the version switcher, add the following code to your `conf.py` file:

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

   The switcher requires a `versions.json` file that contains the versions of the documentation and their URLs in the given ``json_url``.
   see `PyAnsys multi-version documentation <dev_guide_multi_version_>`_
   for more information.

#. **PDF cover page**

   The Ansys Sphinx theme includes a PDF cover page that you can customize.
   To customize the PDF cover page, see :ref:`ref_user_guide_pdf_cover`.

#. **Custom CSS**

   You can add custom CSS to the Ansys Sphinx theme by creating a directory called `_static/css` in
   your documentation and adding the following code to your `conf.py` file:

   .. code-block:: python

    html_static_path = ["_static"]
    html_css_files = ["css/custom.css"]

   Here is an example of a custom CSS file:

   .. code-block:: css

    .body {
        background-color: black;
        color: white;
    }

   which changes the background color of the body to black and the text color to white.
