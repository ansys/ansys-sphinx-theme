{%- if obj.display %}
.. py:property:: {{ obj.short_name }}
   :canonical: {{ obj["obj"]["full_name"] }}
   {% set module_path = obj.obj["full_name"].split('.') %}
   {% set module_name = '.'.join(module_path[:2]) %}
   {% if obj.annotation and module_name in obj.annotation and "[" not in obj.annotation %}
   {% set split_parts = obj.annotation.split('.') %}
   {% set last_part = split_parts[-1] %}
   :type: {{ last_part }}
   {% else %}
   :type: {{ obj.annotation }}
   {% endif %}

   {% if obj.properties %}
   {% for property in obj.properties %}
   :{{ property }}:
   {% endfor %}
   {% endif %}

   {% if obj.docstring %}
   {{ obj.docstring|indent(3) }}
   {% endif %}
{% endif %}
