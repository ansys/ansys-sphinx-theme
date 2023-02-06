Sphinx design
=============
The rendering of sphinx design with ansys sphinx theme. To use this see 
the full document of `sphinx design <https://sphinx-design.readthedocs.io/en/latest/index.html>`_.

.. jinja:: examples

    {% for filename in inputs_examples %}
    {% set title = filename.split('.')[0] %}

    {{ title[0].upper() }}{{ title[1:] }}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        .. literalinclude:: sphinx_examples/{{ filename }}
           :language: bash
        
    This directive renders the as follow:

        .. include:: sphinx_examples/{{ filename }}

    {% endfor %}
