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

{# Include the description for the module #}

{% if obj.docstring %}
Description
-----------

{{ obj.docstring }}
{% endif %}

Contents
--------

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
{% for element in visible_classes_and_interfaces %}
    {% if element.name.startswith("I") and element.name[1].isupper() %}
        {% set _ = visible_interfaces.append(element) %}
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

{% if visible_subpackages or visible_submodules or visible_classes or visible_functions or visible_constants or visible_attributes or visible_interfaces or visible_exceptions %}
.. tab-set::

{% if visible_subpackages %}
    .. tab-item:: Subpackages

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for subpackage in visible_subpackages %}
           * - :py:mod:`{{ subpackage.name }}`
             - {{ subpackage.summary }}
           {% endfor %}
{% endif %}

{% if visible_submodules %}
    .. tab-item:: Submodules

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for submodule in visible_submodules %}
           * - :py:mod:`{{ submodule.name }}`
             - {{ submodule.summary }}
           {% endfor %}
{% endif %}

{% if visible_classes %}
    .. tab-item:: Classes

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for klass in visible_classes if not (klass in visible_interfaces) %}
           * - :py:class:`{{ klass.name }}`
             - {{ klass.summary }}
           {% endfor %}
{% endif %}

{% if visible_interfaces %}
    .. tab-item:: Interfaces

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for iface in visible_interfaces %}
           * - :py:class:`{{ iface.name }}`
             - {{ iface.summary }}
           {% endfor %}
{% endif %}

{% if visible_exceptions %}
    .. tab-item:: Exceptions

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for exc in visible_exceptions %}
           * - :py:class:`{{ exc.name }}`
             - {{ exc.summary }}
           {% endfor %}
{% endif %}

{% if visible_functions %}
    .. tab-item:: Functions

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for function in visible_functions %}
           * - :py:func:`{{ function.name }}`
             - {{ function.summary }}
           {% endfor %}
{% endif %}

{% if visible_constants %}
    .. tab-item:: Constants

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for constant in visible_constants %}
           * - :py:attr:`{{ constant.name }}`
             - {{ constant.summary }}
           {% endfor %}
{% endif %}

{% if visible_attributes %}
    .. tab-item:: Attributes

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for attribute in visible_attributes %}
           * - :py:attr:`{{ attribute.name }}`
             - {{ attribute.summary }}
           {% endfor %}
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

{% block content %}
{# ... Existing content block ... #}
{% endblock %}
