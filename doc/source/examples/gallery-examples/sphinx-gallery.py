# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This is a gallery example.

.. _sphinx_gallery_example:

Sphinx gallery
==============

This example shows how to add a new example to the PyAnsys `Sphinx-Gallery
<https://sphinx-gallery.github.io/>`_.

To add sphinx-gallery in to your project, you need to install the following packages:

.. code-block:: bash

        pip install sphinx-gallery

then add the following to your ``conf.py`` file:

.. code-block:: python

        extensions = [
            "sphinx_gallery.gen_gallery",
        ]
"""

import pyvista as pv

###############################################################################
# Section title
# ~~~~~~~~~~~~~
#
# Code blocks can be broken up with text sections, which are interpreted as
# ReStructuredText.
#
# The text sections are also translated into a markdown cell in the generated Jupyter
# notebook or in the HTML documentation.
#
# Text sections can contain any information that you may have regarding the example,
# such as step-by-step comments and notes regarding motivations.
#
# As in Jupyter notebooks, if a statement is unassigned at the end of a code
# block, output is generated and printed to the screen according to its
# ``__repr__`` method. Otherwise, you can use the ``print()`` function to output text.

# Create a dataset and exercise its ``__repr__`` method

dataset = pv.Sphere()
dataset

###############################################################################
# Plots and images
# ~~~~~~~~~~~~~~~~
# If you use anything that outputs an image (for example, the
# :func:`pyvista.Plotter.show` function), the resulting image is rendered in the
# HTML documentation.
#
# .. note::
#
#    Unless ``sphinx_gallery_thumbnail_number = <int>`` is included at the top
#    of the example script, the first figure (this one) is used for the
#    gallery thumbnail image.
#
#    Also note that this image number uses one-based indexing.

dataset.plot(text="Example Figure")

###############################################################################
# Caveat - plotter must be within one cell
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# It's not possible to have a single :class:`pyvista.Plotter` object across
# multiple cells because these are closed out automatically at the end of a
# cell.
#
# This code exercise the :class:`pyvista.Actor` ``repr`` to demonstrate
# why you might want to instantiate a plotter without showing it in the same
# cell:

pl = pv.Plotter()
actor = pl.add_mesh(dataset)
actor

###############################################################################
# This cell cannot run the plotter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Because the plotter is already closed by Sphinx-Gallery, the following code
# would raise an error:
#
# >>> pl.show()

# You can, however, close out the plotter or access other attributes.

pl.close()

###############################################################################
