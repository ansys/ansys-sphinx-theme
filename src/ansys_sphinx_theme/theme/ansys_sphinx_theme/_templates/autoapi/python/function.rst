{% if obj.display %}
{% if is_own_page %}
:func:`{{ obj.short_name }}`
========={{ "=" * obj.short_name | length }}

{% endif %}
.. py:{{ obj.type }}:: {% if is_own_page %}{{ obj.id }}{% else %}{{ obj.short_name }}{% endif %}{% if obj.args %}({{ obj.args }}){% endif %}{% if obj.return_annotation %} -> {{ obj.return_annotation }}{% endif %}

{% if obj.docstring %}

   {{ obj.docstring|indent(3) }}
{% endif %}

{% if is_own_page %}

Import detail
-------------
{% set split_parts = obj.obj["full_name"].split('.') %}
{% set joined_parts = '.'.join(split_parts[:-1]) %}

.. code-block:: python

    from {{ joined_parts }} import {{ obj["short_name"] }}

{# -------- Begin minigallery section -------- #}
.. ansys-minigallery:: {{ obj.id }}

{# --------- End minigallery section --------- #}
{% endif %}
{% endif %}
