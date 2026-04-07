.. _sphinx-autosummary:

Sphinx Autosummary with Minigallery
====================================

This page demonstrates the **ansys-minigallery** integration with
``sphinx.ext.autosummary``.

Each generated API page below includes a minigallery thumbnail grid at the
bottom that links back to every example (Jupyter notebook or sphinx-gallery
script) that references the documented object.  The
:doc:`minigallery-demo notebook </examples/nbsphinx/minigallery-demo>` imports
both ``ExampleClass`` and ``func``, so both pages will show a card for it.

Classes
-------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/class.rst

   ansys_sphinx_theme.examples.samples.ExampleClass
   ansys_sphinx_theme.examples.samples.Complex
   ansys_sphinx_theme.examples.samples.ExampleDataClass
   ansys_sphinx_theme.examples.samples.ExamplePydanticClass

Functions
---------

.. autosummary::
   :toctree: _autosummary
   :template: autosummary/base.rst

   ansys_sphinx_theme.examples.sample_func.func
   ansys_sphinx_theme.examples.type_hint_example.type_hint_func
