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

# noqa: D205, D400
"""
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
###############################################################################
# Plotting a simple sphere using pyvista
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example demonstrates how to plot a simple sphere using PyVista.

import pyvista as pv

pv.set_jupyter_backend("html")

sphere = pv.Sphere()
sphere.plot()

###############################################################################
# Plotting a simple sphere using pyvista with a plotter

plotter = pv.Plotter(notebook=True)
plotter.add_mesh(sphere, color="white", show_edges=True)
plotter.title = "3D Sphere Visualization"
plotter.show()

###############################################################################
# Rending equations using Math
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example demonstrates how to render equations using Math.

from IPython.display import Math, display

# LaTeX formatted equation
equation = r"\int\limits_{-\infty}^\infty f(x) \delta(x - x_0) \, dx = f(x_0)"
# Display the equation
display(Math(equation))

###############################################################################
from IPython.display import Latex

Latex(r"This is a \LaTeX{} equation: $a^2 + b^2 = c^2$")

###############################################################################
# Rendering a table in markdown
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This is an example to render the table inside the notebook
#
# ====== ====== =======
# A      B      A and B
# ====== ====== =======
# False  False  False
# True   False  False
# False  True   False
# True   True   True
# ====== ====== =======

###############################################################################
