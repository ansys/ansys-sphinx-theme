{# ------------------------- Begin macros definition ----------------------- #}

{% macro tab_item_from_objects_list(objects_list, title="") -%}
    .. tab-item:: {{ title }}

        .. list-table::
          :header-rows: 0
          :widths: auto

          {% for obj in objects_list %}
          * - :py:mod:`{{ obj.name }}`
            - {{ obj.summary }}
          {% endfor %}
{%- endmacro %}

{% macro toctree_from_objects_list(objects_list, icon="", needs_index="false") -%}

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :hidden:

{% for obj in objects_list %}
    {% if needs_index == "true" %}
    {{ icon }} {{ obj.short_name }}<{{ obj.short_name }}/index.rst>
    {% else %}
    {{ icon }} {{ obj.short_name }}<{{ obj.short_name }}>
    {% endif %}
{% endfor %}
{%- endmacro %}

{# --------------------------- End macros definition ----------------------- #}

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

.. tab-set::

{% if visible_subpackages %}
    {{ tab_item_from_objects_list(visible_subpackages, "Subpackages") }}
{% endif %}

{% if visible_submodules %}
    {{ tab_item_from_objects_list(visible_submodules, "Submodules") }}
{% endif %}

{% if visible_classes %}
    {{ tab_item_from_objects_list(visible_classes, "Classes") }}
{% endif %}

{% if visible_interfaces %}
    {{ tab_item_from_objects_list(visible_interfaces, "Interfaces") }}
{% endif %}

{% if visible_enums %}
    {{ tab_item_from_objects_list(visible_enums, "Enums") }}
{% endif %}

{% if visible_exceptions %}
    {{ tab_item_from_objects_list(visible_exceptions, "Exceptions") }}
{% endif %}

{% if visible_functions %}
    {{ tab_item_from_objects_list(visible_functions, "Functions") }}
{% endif %}

{% if visible_constants %}
    {{ tab_item_from_objects_list(visible_constants, "Constants") }}
{% endif %}

{% if visible_attributes %}
    {{ tab_item_from_objects_list(visible_attributes, "Attributes") }}
{% endif %}
{% endif %}

{% block subpackages %}
{% if visible_subpackages %}
{{ toctree_from_objects_list(visible_subpackages, "🖿", needs_index="true") }}
{% endif %}
{% endblock %}

{% block submodules %}
{% if visible_submodules %}
{{ toctree_from_objects_list(visible_submodules, "🗎", needs_index="true") }}
{% endif %}
{% endblock %}

{% if "class" in render_in_single_page %}
{% if visible_interfaces %}
{{ toctree_from_objects_list(visible_interfaces, "🝆") }}
{% endif %}

{% if visible_classes %}
{{ toctree_from_objects_list(visible_classes, "🝆") }}
{% endif %}

{% if visible_enums %}
{{ toctree_from_objects_list(visible_enums, "≔") }}
{% endif %}
{% endif %}

{% if visible_constants and "constant" in render_in_single_page %}
{{ toctree_from_objects_list(visible_constants, "π") }}
{% endif %}

{# Include the description for the module #}

{% if obj.docstring %}
Description
-----------

{{ obj.docstring }}
{% endif %}