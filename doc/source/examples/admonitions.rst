.. _admonitions:

Admonitions
===========

Admonitions are a way to highlight important information in your documentation. They are a way to draw attention to important information,
and can be used to provide additional context or information to the reader.

This page shows how the admonitions are rendered in the documentation with ansys sphinx theme.

Credits and acknowledgments
---------------------------
The examples shown below is downloaded from the pydata sphinx theme project.
The original page can be found at `Pydata sphinx theme <https://pydata-sphinx-theme.readthedocs.io/en/stable/examples/kitchen-sink/index.html>`_ .


.. jinja:: admonitions

    {% for filename in inputs_admonitions %}

    .. include:: sphinx_examples/{{ filename }}

    {% endfor %}