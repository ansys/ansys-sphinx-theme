{% macro table_summary(objs, title='') -%}

.. list-table:: {{ title }}
    :header-rows: 1
    :widths: auto

    * - Name
      - Description
{% for obj in objs %}
    * - obj.name
      - obj.summary
{% endfor %}

{% endmacro %}
