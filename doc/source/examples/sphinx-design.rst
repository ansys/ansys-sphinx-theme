.. _sphinx-design:

Sphinx design
=============
The rendering of sphinx design with ansys sphinx theme.
To access the full documentation for the sphinx design package,
please refer `sphinx design <sphinx_design_docs>`_.

credits and acknowledgments
---------------------------

The examples presented below are sourced from the Sphinx Design project
Copyright (c) by Chris Sewell (2023),
available at `sphinx design examples <sphinx_design_examples>`_.
This project is licensed under the MIT License.

.. jinja:: examples

    {% for filename in inputs_examples %}
    {% set title = filename.split('.')[0] %}

    {{ title[0].upper() }}{{ title[1:] }}
    {{ '~' * (title | length) }}

    .. literalinclude:: sphinx_examples/{{ filename }}
       :language: rst

    This directive renders as follows:

    .. include:: sphinx_examples/{{ filename }}

    {% endfor %}
