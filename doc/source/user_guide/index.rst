.. _ref_user_guide:

User guide
##########

This section provides information on how to customize the Ansys Sphinx theme.

Basic usage
===========
Add the following to your `conf.py` file to use the Ansys Sphinx theme:

.. code-block:: python

   html_theme = "ansys_sphinx_theme"

From ansys sphinx theme you can use the following features:

#. **PyAnsys and Ansys logos**

   The Ansys Sphinx theme includes the PyAnsys and Ansys logos. All The logos
   are available in the
   `ansys_sphinx_theme/static/ <https://github.com/ansys/ansys-sphinx-theme/blob/main/src/ansys_sphinx_theme/theme/ansys_sphinx_theme/static/logos>`_
   directory. You can use the following code to add the logos to your documentation:

   .. code-block:: python

      from ansys_sphinx_theme import pyansys_logo_black, ansys_logo_black, ansys_favicon

      html_logo = pyansys_logo_black
      html_favicon = ansys_favicon

   ``favicon`` is the icon that appears in the browser tab.

#. **Version switcher**

   The Ansys Sphinx theme includes a version switcher that allows users to switch between different versions of the documentation.
   To use the version switcher, add the following code to your `conf.py` file:

   .. code::

      from ansys_sphinx_theme import get_version_match

      version = "<your_version>"
      switcher_versions = get_version_match(version)
      cname = "<your_cname>"
      html_theme_options = {
      "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },

   The switcher requires a `versions.json` file that contains the versions of the documentation and their URLs in the given ``json_url``.
   see `PyAnsys multi-version documentation <https://dev.docs.pyansys.com/how-to/documenting.html#enable-multi-version-documentation>`_
   for more information.

#. PDF cover page

   The Ansys Sphinx theme includes a PDF cover page that you can customize.
   To customize the PDF cover page, see :ref:`ref_user_guide_pdf_cover`.


.. grid:: 1 1 2 2
   :gutter: 2
   :padding: 2
   :margin: 2

   .. grid-item-card:: :octicon:`file-code` :ref:`ref_user_guide_css`
      :link: css
      :link-type: doc

      css customization

   .. grid-item-card:: :octicon:`gear` :ref:`ref_user_guide_html_theme`
      :link: options
      :link-type: doc

      theme options

   .. grid-item-card:: :octicon:`file` :ref:`ref_user_guide_pdf_cover`
      :link: pdf
      :link-type: doc

      PDF customization

   .. grid-item-card:: :octicon:`alert` :ref:`ref_user_guide_404_page`
      :link: 404_page
      :link-type: doc

      404 page customization

   .. grid-item-card:: :octicon:`package` :ref:`ref_user_guide_extension`
      :link: extensions
      :link-type: doc

      extensions

   .. grid-item-card:: :octicon:`code` :ref:`ref_user_guide_autoapi`
      :link: autoapi
      :link-type: doc

      autoapi

.. toctree::
   :maxdepth: 2
   :hidden:

   css
   options
   pdf
   404_page
   extensions
   autoapi

