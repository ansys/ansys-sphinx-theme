Ansys Sphinx Theme documentation
################################

**Date**: |today| **Version**: |version|

**Useful links**:

`Source Repository <https://github.com/ansys/ansys_sphinx_theme>`_ |
`Issues <https://github.com/ansys/ansys_sphinx_theme/issues>`_ |
:ref:`ref-getting-started`

The Ansys Sphinx Theme is a custom Ansys-branded theme for use with Sphinx, a documentation
generator for creating project documentation from reStructuredText source files.

This theme is specifically tailored for documentation related to Ansys projects
helping to ensure consistency in its look and feel. Various useful extensions
are included in the theme to make documentation more appealing and user-friendly.

.. jinja:: main_toctree

    .. grid:: 1 2 3 3
        :gutter: 1 2 3 3
        :padding: 1 2 3 3

        .. grid-item-card:: Getting started :fa:`person-running`
            :link: getting-started
            :link-type: doc

            Learn how to install the Ansys Sphinx Theme.

        .. grid-item-card:: User guide :fa:`book-open-reader`
            :link: user-guide
            :link-type: doc

            Learn how to use the capabilities and features of this theme.

        {% if build_examples %}

        .. grid-item-card:: Examples :fa:`laptop-code`
            :link: examples
            :link-type: doc

            Explore examples that show how to integrate third-party extensions with this theme.

        {% endif %}

        .. grid-item-card:: Changelog :fa:`history`
            :link: changelog
            :link-type: doc

            View the history of changes made to the theme.

.. jinja:: main_toctree

    .. toctree::
       :hidden:
       :maxdepth: 3

       getting-started.rst
       user-guide.rst
       {% if build_examples %}
       examples.rst
       {% endif %}
       changelog
