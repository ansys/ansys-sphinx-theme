
Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

Version `v0.12.0 <https://github.com/ansys/pymechanical/releases/tag/vv0.12.0>`_ (2024-11-07)
=============================================================================================


Whatsnew
~~~~~~~~

Launch GUI
----------
Open the current project with Mechanical GUI.

.. code:: python

    from ansys.mechanical.core import App

    app = App()
    app.save()
    app.launch_gui()

Above code opens up the temporarily saved ``.mechdb`` or ``.mechdat`` files.
The files are deleted when GUI is closed . For more info check
`launch_gui() <../api/ansys/mechanical/core/embedding/launch_gui/index.html>`_ function

Opens up the specified project file.

.. code:: python

  launch_gui("path/to/project.mechdb")


Prints Mechanical project tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This feature let you see the heirachial Mechanical project tree.
It also shows whether an object is suppressed or not.

.. code:: python

  import ansys.mechanical.core as mech

  app = mech.App()
  app.update_globals(globals())
  app.print_tree()



Changelog
---------

.. tab-set::

  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto


        * - chore(deps): bump pygithub from 2.4.0 to 2.5.0
          - `#582 <https://github.com/ansys/ansys-sphinx-theme/pull/582>`_

  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto


        * - feat: whatsnew theme option
          - `#574 <https://github.com/ansys/ansys-sphinx-theme/pull/574>`_

        * - chore: bump version 1.3.dev0
          - `#577 <https://github.com/ansys/ansys-sphinx-theme/pull/577>`_

        * - fix: CONTRIBUTORS.md
          - `#578 <https://github.com/ansys/ansys-sphinx-theme/pull/578>`_

  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto


        * - chore: update CHANGELOG for v1.2.0
          - `#576 <https://github.com/ansys/ansys-sphinx-theme/pull/576>`_

        * - Enable 'show_prev_next' in the documented defaults
          - `#580 <https://github.com/ansys/ansys-sphinx-theme/pull/580>`_

.. vale on

Older release notes
====================


.. button-ref:: changelog
    :ref-type: doc
    :color: primary
    :shadow:
    :expand:

    Go to older release notes