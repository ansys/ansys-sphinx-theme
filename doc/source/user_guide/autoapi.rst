.. _ref_user_guide_autoapi:

Using ``sphinx-autoapi`` to generate API documentation
------------------------------------------------------

`sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi/>`_ is a tool that automatically generates API documentation from your source code.
It is a great way to keep your documentation up-to-date with your codebase.

The ``ansys-sphinx-theme`` includes a set of custom templates for ``sphinx-autoapi`` that is designed
to match the look and feel of the rest of the PyAnsys documentation.

Dependencies required
~~~~~~~~~~~~~~~~~~~~~

To use ``sphinx-autoapi`` with the ``ansys-sphinx-theme``, you need to install the ``autoapi`` target
of the theme. This can be done by defining your ``ansys-sphinx-theme`` dependency as
``ansys-sphinx-theme[autoapi]`` in your project's requirements location.

For example, if you are using a ``requirements.txt`` file, you would define your dependency as follows:

.. code-block: text

    ansys-sphinx-theme[autoapi]==X.Y.Z

If you are using a ``pyproject.toml`` file, you would define your dependency as follows:

.. code:: toml
    
    # For a typical PyAnsys pyproject.toml file
    [project.optional-dependencies]
    doc = [
        "ansys-sphinx-theme[autoapi]==X.Y.Z",
    ]

Configuring the Sphinx project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use ``sphinx-autoapi`` with the ``ansys-sphinx-theme``, and benefit from the shipped
templates, you need to add the following configuration to your Sphinx project's ``conf.py`` file.

.. code:: python

    from pathlib import Path

    from ansys_sphinx_theme import get_autoapi_templates_dir_relative_path

    ...

    # Configuration for Sphinx autoapi
    autoapi_type = "python"
    autoapi_dirs = ["../../src/ansys"]
    autoapi_root = "api"
    autoapi_options = [
        "members",
        "undoc-members",
        "show-inheritance",
        "show-module-summary",
        "special-members",
    ]
    autoapi_template_dir = get_autoapi_templates_dir_relative_path(Path(__file__))
    autoapi_python_use_implicit_namespaces = True
    autoapi_keep_files = True
    autoapi_own_page_level = "class"


The above configuration generates the API documentation for your package in the ``src`` directory
and places the generated files in the ``api`` directory. These files are based on the
``ansys-sphinx-theme`` templates. If you want to customize some of the previous options, you can
do so by modifying the configuration above. The line of code declaring the desired set of templates is the following one:

.. code:: python

    autoapi_template_dir = get_autoapi_templates_dir_relative_path(Path(__file__))


