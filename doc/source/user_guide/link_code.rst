.. _ref_user_guide_link_code:
Linkcode extension
==================

The Linkcode extension automatically adds "View Source" links to the documentation for Python, C, C++, 
and JavaScript objects. It allows you to link to the source code hosted on GitHub.

Installation
------------

To use the ansys-sphinx-theme linkcode extension, you need to add it to the Sphinx configuration:

1. Open your `conf.py` file.

2. Add the following line to the file:

   .. code-block:: python

      extensions = ["ansys_sphinx_theme.extension.linkcode"]

Configuration options
---------------------

The Linkcode extension supports the following configuration options in your `conf.py` file:

- ``link_code_library`` (str, optional):
  The user/repository name where the source code is hosted. For example, ``ansys/ansys-sphinx-theme``.

- ``link_code_source`` (str, optional):
  The relative path of the source code file within the repository. For example, ``src``.

- ``link_code_branch`` (str, optional, default: 'main'):
  The GitHub branch. It can be a specific version like ``main`` or ``dev``.

You can also set the `link_code_library`, `link_code_source`, `link_code_branch`,
and other GitHub-related configuration options directly in the `html_context` dictionary in your `conf.py` file.
By doing so, you can avoid redundancy and centralize the GitHub-related information for the extension:

.. code-block:: python

   # Example of setting GitHub-related configuration in conf.py
   html_context = {
       # "github_url": "https://github.com", # or your GitHub Enterprise site
       "github_user": "<your-github-org>",
       "github_repo": "<your-github-repo>",
       "github_version": "<your-branch>",
       "source_path": "<path-from-root-to-your-source_file>",
   }
