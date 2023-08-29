{% if not obj.display %}
:orphan:
{% endif %}

{% if obj.name.split(".") | length == 3 %}
The ``{{ obj.name }}`` library
{{ "================" + "=" * obj.name|length }}
{% else %}
{% if obj.type == "package" %}
The ``{{ obj.short_name }}`` package 
{{ "====================" + "=" * obj.short_name|length }}
{% else %}
The ``{{ obj.short_name }}.py`` module
{{ "==================" + "=" * obj.short_name|length }}
{% endif %}
{% endif %}

.. py:module:: {{ obj.name }}

Summary
-------

{% if obj.all is not none %}
{% set visible_children = obj.children|selectattr("short_name", "in", obj.all)|list %}
{% elif obj.type is equalto("package") %}
{% set visible_children = obj.children|selectattr("display")|list %}
{% else %}
{% set visible_children = obj.children|selectattr("display")|rejectattr("imported")|list %}
{% endif %}

{% set visible_subpackages = obj.subpackages|selectattr("display")|list %}
{% set visible_submodules = obj.submodules|selectattr("display")|list %}

{% set visible_classes_and_interfaces = visible_children|selectattr("type", "equalto", "class")|list %}
{% set visible_functions = visible_children|selectattr("type", "equalto", "function")|list %}
{% set visible_attributes_and_constants = visible_children|selectattr("type", "equalto", "data")|list %}
{% set visible_exceptions = visible_children|selectattr("type", "equalto", "exception")|list %}

{% set visible_classes = [] %}
{% set visible_interfaces = [] %}
{% set visible_enums = [] %}
{% for element in visible_classes_and_interfaces %}
    {% if element.name.startswith("I") and element.name[1].isupper() and ("enum.Enum" not in element.bases) %}
        {% set _ = visible_interfaces.append(element) %}
    {% elif "enum.Enum" in element.bases %}
        {% set _ = visible_enums.append(element) %}
    {% else %}
        {% set _ = visible_classes.append(element) %}
    {% endif %}
{% endfor %}

{% set visible_attributes = [] %}
{% set visible_constants = [] %}
{% for element in visible_attributes_and_constants %}
    {% if element.name.isupper() %}
        {% set _ = visible_constants.append(element) %}
    {% else %}
        {% set _ = visible_attributes.append(element) %}
    {% endif %}
{% endfor %}

{% set module_objects = visible_subpackages + visible_submodules + visible_classes + visible_interfaces + visible_enums + visible_functions + visible_constants + visible_attributes %}

{% if module_objects %}

{% macro module_get_list_table(table_objs, title="") -%}
    .. tab-item:: {{ title }}

        .. list-table::
          :header-rows: 0
          :widths: auto

          {% for table_obj in table_objs %}
          * - :py:mod:`{{ table_obj.name }}`
            - {{ table_obj.summary }}
          {% endfor %}
{%- endmacro %}

.. tab-set::

{% if visible_subpackages %}
    {{ module_get_list_table(visible_subpackages, "Subpackages") }}
{% endif %}

{% if visible_submodules %}
    {{ module_get_list_table(visible_submodules, "Submodules") }}
{% endif %}

{% if visible_classes %}
    {{ module_get_list_table(visible_classes, "Classes") }}
{% endif %}

{% if visible_interfaces %}
    {{ module_get_list_table(visible_interfaces, "Interfaces") }}
{% endif %}

{% if visible_enums %}
    {{ module_get_list_table(visible_enums, "Enums") }}
{% endif %}

{% if visible_exceptions %}
    {{ module_get_list_table(visible_exceptions, "Exceptions") }}
{% endif %}

{% if visible_functions %}
    {{ module_get_list_table(visible_functions, "Functions") }}
{% endif %}

{% if visible_constants %}
    {{ module_get_list_table(visible_constants, "Constants") }}
{% endif %}

{% if visible_attributes %}
    {{ module_get_list_table(visible_attributes, "Attributes") }}
{% endif %}
{% endif %}

{% block subpackages %}
{% if visible_subpackages %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for subpackage in visible_subpackages %}
    🖿 {{subpackage.short_name}}<{{ subpackage.short_name }}/index.rst>
{% endfor %}
{% endif %}
{% endblock %}

{% block submodules %}
{% if visible_submodules %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for submodule in visible_submodules %}
    🗎 {{submodule.short_name}}.py <{{ submodule.short_name }}/index.rst>
{% endfor %}
{% endif %}
{% endblock %}

{% if visible_interfaces %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for interface in visible_interfaces %}
    🝆 {{interface.name}} <{{ interface.name }}>
{% endfor %}
{% endif %}

{% if visible_classes%}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for klass in visible_classes %}
    🝆 {{klass.name}} <{{ klass.name }}>
{% endfor %}
{% endif %}

{% if visible_enums %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for enum in visible_enums %}
    ≔ {{enum.name}} <{{ enum.name }}>
{% endfor %}
{% endif %}

{% if visible_constants %}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for constant in visible_constants %}
    π {{constant.name}} <{{ constant.name }}>
{% endfor %}
{% endif %}


{# Include the description for the module #}

{% if obj.docstring %}
Description
-----------

{{ obj.docstring }}
{% endif %}
