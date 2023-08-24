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

{% if visible_enums %}
    .. tab-item:: Enums

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for enum in visible_enums %}
           * - :py:class:`{{ enum.name }}`
             - {{ enum.summary }}
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
