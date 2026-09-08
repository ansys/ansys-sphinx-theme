# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Sphinx-Gallery
==============

This example shows how to add a new example when using `Sphinx-Gallery
<https://sphinx-gallery.github.io/>`_.

To use Sphinx-Gallery, first install the package with this command:

.. code-block:: bash

        pip install sphinx-gallery

Then, add the package to the ``extensions`` variable in your Sphinx ``conf.py`` file:

.. code-block:: python

        extensions = [
            "sphinx_gallery.gen_gallery",
        ]
"""
###############################################################################
# Plot a simple sphere using PyVista
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This code plots a simple sphere using PyVista.

import pyvista as pv

pv.set_jupyter_backend("html")

sphere = pv.Sphere()
sphere.plot()

###############################################################################
# Plot a simple sphere using PyVista with a plotter

plotter = pv.Plotter(notebook=True)
plotter.add_mesh(sphere, color="white", show_edges=True)
plotter.title = "3D Sphere Visualization"
plotter.show()

###############################################################################
# Figures with Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~
# This example shows how to render a figure using Matplotlib.

import matplotlib.pyplot as plt
import numpy as np

time = np.linspace(0, 2 * np.pi, 100)

fig, ax = plt.subplots()
ax.plot(time, np.cos(time), color="blue", label=r"$\cos{(t)}$")
ax.plot(time, np.sin(time), color="red", label=r"$\sin{(t)}$")

ax.set_xlabel("Time [time units]")
ax.set_ylabel("Amplitude [distance units]")
ax.set_title("Trigonometric functions")

plt.show()

###############################################################################
# Figures with Plotly
# ~~~~~~~~~~~~~~~~~~~
# This example shows how to render a figure using Plotly.

import plotly.graph_objs as go

# More info: https://plotly.com/python/renderers/

time = np.linspace(0, 2 * np.pi, 100)

cos_trace = go.Scatter(x=time, y=np.cos(time), mode="lines", name="cos(t)")
sin_trace = go.Scatter(x=time, y=np.sin(time), mode="lines", name="sin(t)")

fig = go.Figure(data=[cos_trace, sin_trace])

fig
###############################################################################

import numpy as np
import plotly.express as px

df = px.data.tips()
fig = px.bar(
    df,
    x="sex",
    y="total_bill",
    facet_col="day",
    color="smoker",
    barmode="group",
    template="presentation+plotly",
)
fig.update_layout(height=400)
fig

###############################################################################
# Render equations using IPython ``math``
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example shows how to render equations using the IPython ``math`` module.

from IPython.display import Math, display

# LaTeX formatted equation
equation = r"\int\limits_{-\infty}^\infty f(x) \delta(x - x_0) \, dx = f(x_0)"
# Display the equation
display(Math(equation))

###############################################################################
from IPython.display import Latex

Latex(r"This is a \LaTeX{} equation: $a^2 + b^2 = c^2$")

###############################################################################
# Render a table
# ~~~~~~~~~~~~~~
# This is an example to render a table with Sphinx-Gallery.
#
# +--------------------------------+--------------------------------+------------------------------+
# | A                              | B                              | A and B                      |
# +================================+================================+==============================+
# | False                          | False                          | False                        |
# +--------------------------------+--------------------------------+------------------------------+
# | True                           | False                          | False                        |
# +--------------------------------+--------------------------------+------------------------------+
# | False                          | True                           | False                        |
# +--------------------------------+--------------------------------+------------------------------+
# | True                           | True                           | True                         |
# +--------------------------------+--------------------------------+------------------------------+
#

###############################################################################
# Render a table using pandas

import pandas as pd

# Create a dictionary of data
data = {
    "A": [True, False, True, False],
    "B": [False, True, False, True],
    "C": [True, True, False, False],
}

# Create DataFrame from the dictionary
df = pd.DataFrame(data)

# Display the DataFrame
df.head()

###############################################################################

# %%
# sphinx_gallery_tags = ["sphinx-gallery-rendered"]
