*******
Options
*******
The PyAnsys Sphinx theme is generally used as is. However, the following
sections describe how you can customize it.

Add breadcrumbs
~~~~~~~~~~~~~~~
The ``ansys-sphinx-theme`` supports the display of breadcrumbs on
the body of documentation pages to make navigation easier. These 
breadcrumbs are hidden by default. To show breadcrumbs on the pages
of your documentation, in the ``conf.py`` file, add ``"show_breadcrumbs": True``
to the ``html_theme_options`` dictionary.

If you want to add additional *root* breadcrumbs, such as to the Ansys
documentation homepage, add them to the ``html_theme_options`` dictionary as a
list of tuples with the ``"additional_breadcrumbs"`` key. The tuples are of the
form ``("Link text", "url")``.

Here is how you use ``html_theme_options`` to add breadcrumbs to the Ansys Sphinx theme:

.. code:: python

   html_theme_options = {
       "github_url": "https://github.com/ansys/ansys-sphinx-theme",
       "show_prev_next": False,
       "show_breadcrumbs": True,
       "additional_breadcrumbs": 
   }

When you are on the module homepage, the breadcrumb displays the homepage
title. However, this title is not accessible to Sphinx from other
documentation pages. Therefore, the ``html_short_title`` is used as the display
text for the breadcrumb on the documentation homepage. To ensure a consistent user
experience, you should ensure that the ``html_short_title`` (or optionally
``html_title`` if ``html_short_title`` is not used) is set to the same value as
the title of the ``index.rst`` page. For example:

.. code:: python

   html_short_title = html_title = 'Ansys Sphinx Theme'

If you want to include the package version in the ``index.rst`` title,
use ``|version|``.


Customize icons
~~~~~~~~~~~~~~~
The Ansys Sphinx theme allows you to control what icons are shown in the
navigation bar.

- Comprehensive information on customizing icons is available in
  `Configure icon links <https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/configuring.html?highlight=icons#configure-icon-links>`_
  in the documentation for the PyData Sphinx theme.
- For information on using `Font Awesome <https://fontawesome.com/>`, an icon
  library and toolkit, see its `documentation <https://fontawesome.com/v6/docs>`_,
  particularly `How to Add Icons <https://fontawesome.com/v6/docs/web/add-icons/how-to#contentHeader>`_.

The following sections describe how you can perform basic icon customizations.

Add icons
---------
To add icons to the navigation bar, in ``html_theme_options``, you add them to the ``icon_links``
dictionary. For each icon to add, you must specify its ``name``, the associated ``url``,
the ``icon``, and the ``type``. This example adds an icon for sending an email:

.. code-block:: python

    html_theme_options = {
     "icon_links": [
         dict(name="Mail", url="mailto:me", icon="fas fa-envelope")
     ],
     ...
    }

Hide icons
----------
To hide icons so that they do not show in the navigation bar, add their names
to the ``hidden_icons`` list:

.. code-block:: python

    html_theme_options = {
        "hidden_icons": ["GitHub"],
        ...
    }


If you want to hide all icons, use the ``show_icons`` Boolean variable:

.. code-block:: python

    html_theme_options = {
        "show_icons": False,
        ...
    }

Customize PDF cover page
~~~~~~~~~~~~~~~~~~~~~~~~
You can use the ``generate_preamble`` function in the
``ansys_sphinx_theme.latex`` module to customize the cover page for
a PDF of the documentation:

.. autofunction:: ansys_sphinx_theme.latex.generate_preamble

You use this function to generate the value for the ``preamble`` key in the
``latex_elements`` variable declared in the ``conf.py`` file:

.. code-block:: python

    latex_elements = {
        "preamble": ansys_sphinx_theme.latex.generate_preamble(
            <title_of_coverpage>,
            <watermark_for_titlepage>,
            <date_to_be_printed>,
        )
    }

To use the logo and watermark provided by Ansys on the cover page, you must
import them and then add them in ``latex_additional_files``:

.. code-block:: python

    from ansys_sphinx_theme import (
       ansys_logo_white,
       ansys_logo_white_cropped,
       watermark,
    )

.. code-block:: python

    latex_additional_files = [
       watermark, ansys_logo_white, ansys_logo_white_cropped
    ]
