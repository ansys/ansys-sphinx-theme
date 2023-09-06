{% if obj.display %}

{{ obj.short_name }}
{{"=" * obj.name|length }}

.. py:{{ obj["type"] }}:: {{ obj["short_name"] }}{% if obj["args"] %}({{ obj["args"] }}){% endif %}

   :canonical: {{ obj["obj"]["full_name"] }}


{% for (args, return_annotation) in obj.overloads %}
    {{ " " * (obj.type | length) }}   {{ obj.short_name }}{% if args %}({{ args }}){% endif %}
{% endfor %}


{% if obj.bases %}
{% if "show-inheritance" in autoapi_options %}
Bases: {% for base in obj.bases %}{{ base|link_objs }}{% if not loop.last %}, {% endif %}{% endfor %}
{% endif %}

{% if "show-inheritance-diagram" in autoapi_options and obj.bases != ["object"] %}
.. autoapi-inheritance-diagram:: {{ obj.obj["full_name"] }}
   :parts: 1
   {% if "private-members" in autoapi_options %}
   :private-bases:
   {% endif %}

{% endif %}
{% endif %}

{% if obj.docstring -%}
{{ obj.summary|indent(3) }}
{% endif %}

{% if "inherited-members" in autoapi_options %}
{% set visible_classes = obj.classes|selectattr("display")|list %}
{% else %}
{% set visible_classes = obj.classes|rejectattr("inherited")|selectattr("display")|list %}
{% endif %}

{% for klass in visible_classes %}
{{ klass.render()|indent(3) }}
{% endfor %}

{% if "inherited-members" in autoapi_options %}
{% set visible_properties = obj.properties|selectattr("display")|list %}
{% else %}
{% set visible_properties = obj.properties|rejectattr("inherited")|selectattr("display")|list %}
{% endif %}

{% if "inherited-members" in autoapi_options %}
{% set visible_attributes = obj.attributes|selectattr("display")|list %}
{% else %}
{% set visible_attributes = obj.attributes|rejectattr("inherited")|selectattr("display")|list %}
{% endif %}

{% if "inherited-members" in autoapi_options %}
{% set visible_methods = obj.methods|selectattr("display")|list %}
{% else %}
{% set visible_methods = obj.methods|rejectattr("inherited")|selectattr("display")|list %}
{% endif %}

{% set visible_abstract_methods = [] %}
{% set visible_special_methods = [] %}
{% set visible_static_methods = [] %}
{% set visible_instance_methods = [] %}
{% set visible_class_methods = [] %}
{% set visible_constructors = [] %}

{% for element in visible_methods %}
    {% if "abstractmethod" in element.properties %}
        {% set _ = visible_abstract_methods.append(element) %}
    {% elif "staticmethod" in element.properties %}
        {% set _ = visible_static_methods.append(element) %}
    {% elif "classmethod" in element.properties %}
        {% set _ = visible_class_methods.append(element) %}
    {% elif element.name.startswith("__") and ("init" not in element.name) %}
        {% set _ = visible_special_methods.append(element) %}
    {% elif ("init" not in element.name) %}
        {% set _ = visible_instance_methods.append(element) %}
    {% elif ("init" in element.name) %}
        {% set _ = visible_constructors.append(element) %}
    {% endif %}
{% endfor %}


{% set class_objects = visible_properties + visible_attributes + visible_methods %}

{% if class_objects %}

{% macro get_list_table(table_objs, title="") -%}
    .. tab-item:: {{ title }}

        .. list-table::
          :header-rows: 0
          :widths: auto

          {% for table_obj in table_objs %}
          * - :py:attr:`~{{ table_obj.name }}`
            - {{ table_obj.summary }}
          {% endfor %}
{%- endmacro %}

Overview
--------
.. py:currentmodule:: {{ obj.short_name }}
.. tab-set::

{% if visible_properties %}
    {{ get_list_table(visible_properties, "Properties") }}
{% endif %}

{% if visible_attributes %}
    {{ get_list_table(visible_attributes, "Attributes") }}      
{% endif %}

{% if visible_methods %}
    {{ get_list_table(visible_methods, "Methods") }}
{% endif %}

{% if visible_instance_methods %}
    {{ get_list_table(visible_instance_methods, "Instance methods") }}
{% endif %}

{% if visible_class_methods %}
    {{ get_list_table(visible_class_methods, "Class methods") }}
{% endif %}

{% if visible_static_methods %}
    {{ get_list_table(visible_static_methods, "Static methods") }}
{% endif %}

{% if visible_special_methods %}
    {{ get_list_table(visible_special_methods, "Special methods") }}
{% endif %}
{% if visible_abstract_methods %}
    {{ get_list_table(visible_abstract_methods, "Abstract methods") }}
{% endif %}

{% endif %}
{% endif %}

Import detail
-------------
{% set split_parts = obj.obj["full_name"].split('.') %}
{% set joined_parts = '.'.join(split_parts[:-1]) %}

.. code-block:: python

    from {{ joined_parts }} import {{ obj["short_name"] }}

{% if visible_properties  %}

Property detail
---------------
{% for property in visible_properties %}
{{ property.render() }}
{% endfor %}
{% endif %}


{% if visible_attributes  %}
Attribute detail
----------------
{% for attribute in visible_attributes %}
{{ attribute.render() }}
{% endfor %}
{% endif %}

{% if visible_methods  %}
Method detail
-------------
{% for method in visible_methods %}
{{ method.render() }}
{% endfor %}
{% endif %}
