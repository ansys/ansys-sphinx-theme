.. _ref_user_guide_extension:

Extensions
==========

This page contains the extensions shipped extensions that seamlessly integrate with this theme to enhance 
documentation functionality 

Linkcode extension
-------------------

The Linkcode extension automatically adds "View Source" links to the documentation for Python, C, C++, 
and JavaScript objects. It allows you to link to the source code hosted on GitHub.

Installation
~~~~~~~~~~~~

To use the ``ansys-sphinx-theme`` linkcode extension, you need to add it to the Sphinx configuration:

#. Add the following line in the ``conf.py`` file:
   .. code-block:: python

      extensions = ["ansys_sphinx_theme.extension.linkcode"]

Configuration options
---------------------

The Linkcode extension provides a way to configure its behavior by using certain options within your conf.py file. 
Depending on your preferred approach, you can utilize the direct 
configuration options or the html_context dictionary to streamline your settings.

Direct configuration options:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``link_code_library`` (str, optional):
  The user/repository name where the source code is hosted. For example, ``ansys/ansys-sphinx-theme``.

- ``link_code_source`` (str, optional):
  The relative path of the source code file within the repository. For example, ``src``.

- ``link_code_branch`` (str, optional, default: 'main'):
  The GitHub branch. It can be a specific version like ``main`` or ``dev``.

Using ``html_context`` dictionary:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You also have the option to centralize your GitHub-related configuration by incorporating it 
directly into the ``html_context`` dictionary within your `conf.py` file. This approach allows you to 
minimize redundancy and manage the GitHub-related information more effectively for the extension:

.. code-block:: python

   # Example of setting GitHub-related configuration in conf.py
   html_context = {
       # "github_url": "https://github.com", # or your GitHub Enterprise site
       "github_user": "<your-github-org>",
       "github_repo": "<your-github-repo>",
       "github_version": "<your-branch>",
       "source_path": "<path-from-root-to-your-source_file>",
   }

With this setup, you can fine-tune your configuration according to your preferences and requirements, 
enhancing the integration of the Linkcode extension into your documentation.