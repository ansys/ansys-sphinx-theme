.. _ref_user_guide_autoapi:

Using ``sphinx-autoapi`` to generate API documentation
------------------------------------------------------

``sphinx-autoapi`` is a tool that automatically generates API documentation from your source code.
It is a great way to keep your documentation up-to-date with your codebase.

The ``ansys-sphinx-theme`` includes a custom template for ``sphinx-autoapi`` that is designed
to match the look and feel of the rest of the PyAnsys documentation.

Dependencies required
~~~~~~~~~~~~~~~~~~~~~

To use ``sphinx-autoapi`` with the ``ansys-sphinx-theme``, you need to install the ``autoapi`` target
of the theme. This can be done by defining your ``ansys-sphinx-theme`` dependency as
``ansys-sphinx-theme[autoapi]`` in your project's requirements location.

For example, if you are using a ``requirements.txt`` file, you would define your dependency as follows::

    ansys-sphinx-theme[autoapi]

If you are using a ``pyproject.toml`` file, you would define your dependency as follows:

.. code:: toml
    
    # For a typical PyAnsys pyproject.toml file
    [project.optional-dependencies]
    doc = [
        ...
        "ansys-sphinx-theme[autoapi]==XX.YY.ZZ",
        ...
    ]

Configuring our Sphinx project
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


The above configuration will generate API documentation for your package in the ``src`` directory
and place the generated files in the ``api`` directory. The generated files will be based on the
``ansys-sphinx-theme`` templates. If you want to customize some of the previous options, you can
do so by modifying the configuration above. The main line of code to use the shipped
templates is the following.

.. code:: python

    autoapi_template_dir = get_autoapi_templates_dir_relative_path(Path(__file__))
