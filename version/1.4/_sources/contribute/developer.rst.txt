Contributing as a developer
###########################

.. grid:: 1 1 3 3

    .. grid-item-card:: :fa:`code-fork` Fork the repository
        :padding: 2 2 2 2
        :link: fork-the-repository
        :link-type: ref

        Learn how to fork the project and get your own copy.

    .. grid-item-card:: :fa:`download` Clone the repository
        :padding: 2 2 2 2
        :link: clone-the-repository
        :link-type: ref

        Download your own copy in your local machine.

    .. grid-item-card:: :fa:`download` Install for developers
        :padding: 2 2 2 2
        :link: install-for-developers
        :link-type: ref

        Install the project in editable mode.


.. _fork-the-repository:

Fork the repository
===================

Forking the repository is the first step for contributing to the project. This
allows you to have your own copy of the project so you can make changes without
affection the main project. Once you have made your changes, you can submit a
pull-request to the main project to have your changes reviewed and merged.

.. button-link:: https://github.com/ansys/ansys-sphinx-theme/fork
    :color: primary
    :align: center

    :fa:`code-fork` Fork this project

.. note::

    If you are an Ansys employee, you can skip this step.

.. _clone-the-repository:

Clone the repository
====================

Make sure you `configure SSH`_ with your GitHub
account. This allows you to clone the repository without having to use tokens
or passwords. Also, make sure you have `git`_ installed in your machine.

To clone the repository using SSH, run:

.. code-block:: bash

    git clone git@github.com:ansys/ansys-sphinx-theme

.. _install-for-developers:

Install for developers
======================

Installing Ansys sphinx theme in development mode allows you to perform changes to the code
and see the changes reflected in your environment without having to reinstall
the library every time you make a change.

Virtual environment
-------------------

Start by navigating to the project's root directory by running:

.. code-block:: bash

    cd ansys-sphinx-theme

Then, create a new virtual environment named ``.venv`` to isolate your system's
Python environment by running:

.. code-block:: bash

    python -m venv .venv

Finally, activate this environment by running:

.. tab-set::

    .. tab-item:: Windows

        .. tab-set::

            .. tab-item:: CMD

                .. code-block:: bash

                    .venv\Scripts\activate.bat

            .. tab-item:: PowerShell

                .. code-block:: bash

                    .venv\Scripts\Activate.ps1

    .. tab-item:: macOS/Linux/UNIX

        .. code-block:: bash

            source .venv/bin/activate

Development mode
----------------

Now, install Ansys sphinx theme in editable mode by running:

.. code-block:: bash

    python -m pip install --editable .

Verify the installation by checking the version of the library:


.. code-block:: python

    from ansys_sphinx_theme import __version__
    print(f"Ansys sphinx thenme version is {__version__}")

.. jinja::

    .. code-block:: bash

       >>> Ansys sphinx theme version is {{ ANSYS_SPHINX_THEME_VERSION }}

Install ``Tox``
---------------

Once the project is installed, you can install `Tox`_. This is a cross-platform
automation tool. The main advantage of Tox is that it allows you to test your
project in different environments and configurations in a temporary and
isolated Python virtual environment. To install Tox, run:

.. code-block:: bash

    python -m pip install tox

Finally, verify the installation by listing all the different environments
(automation rules) for Ansys Sphinx theme:

.. code-block:: bash

    python -m tox list

.. jinja:: toxenvs

    .. dropdown:: Default Tox environments
        :animate: fade-in
        :icon: three-bars

        .. list-table::
            :header-rows: 1
            :widths: auto

            * - Environment
              - Description
              - usage
            {% for environment in envs %}
            {% set name, description  = environment.split("->") %}
            * - {{ name }}
              - {{ description }}
              - python -m tox -e {{ name }}
            {% endfor %}


Adhere to code style
--------------------

Ansys Sphinx theme follows the PEP8 standard as outlined in
`PEP 8 <https://dev.docs.pyansys.com/coding-style/pep8.html>`_ in
the *PyAnsys Developer's Guide* and implements style checking using
`pre-commit <https://pre-commit.com/>`_.

To ensure your code meets minimum code styling standards, run these commands::

  pip install pre-commit
  pre-commit run --all-files

or use tox as above::

    tox -e code-style

You can also install this as a pre-commit hook by running this command::

  pre-commit install

This way, it's not possible for you to push code that fails the style checks::

  $ pre-commit install
  $ git commit -am "added my cool feature"
  ruff.....................................................................Passed
  ruff-format..............................................................Passed
  codespell................................................................Passed
  prettier.................................................................Passed
  check for merge conflicts................................................Passed
  debug statements (python)................................................Passed
  check yaml...............................................................Passed
  trim trailing whitespace.................................................Passed
  Validate GitHub Workflows................................................Passed
  Add License Headers......................................................Passed


Build the documentation
-----------------------

To build documentation locally, you can either use Tox as mentioned above or
run the following commands:

1. Install the required dependencies by running::

    python -m pip install -e .[doc]

2. Build the documentation by running::

    # On Linux or macOS
    make -C doc/ html

    # On Windows
    doc\make.bat html

3. The documentation is built in the ``doc/_build/html`` directory. Open the
   ``index.html`` file in your browser to view the documentation.

You can clean the build directory by running::

    # On Linux or macOS
    make -C doc/ clean

    # On Windows
    doc\make.bat clean

.. Note::

    Use ``tox -e doc-serve`` to build the documentation and open it in your
    default browser. This command will also watch for changes in the source
    files and rebuild the documentation automatically.