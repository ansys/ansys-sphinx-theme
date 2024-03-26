{# ------------------------- Begin macros definition ----------------------- #}

{% macro tab_item_from_objects_list(objects_list, title="") -%}

    .. tab-item:: {{ title }}

        .. list-table::
          :header-rows: 0
          :widths: auto

          {% for obj in objects_list %}
          * - :py:attr:`~{{ obj.name }}`
            - {{ obj.summary }}
          {% endfor %}
{%- endmacro %}

{# --------------------------- End macros definition ----------------------- #}

{% if obj.display %}
   {% if is_own_page %}
:class:`{{ obj.id }}`
========={{ "=" * obj.id | length }}

   {% endif %}
   {% set visible_children = obj.children|selectattr("display")|list %}
   {% set own_page_children = visible_children|selectattr("type", "in", own_page_types)|list %}
   {% if is_own_page and own_page_children %}
.. toctree::
   :hidden:

      {% for child in own_page_children %}
   {{ child.include_path }}
      {% endfor %}

   {% endif %}
.. py:{{ obj.type }}:: {% if is_own_page %}{{ obj.id }}{% else %}{{ obj.short_name }}{% endif %}{% if obj.args %}({{ obj.args }}){% endif %}

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
   {% if obj.docstring %}

   {{ obj.docstring|indent(3) }}
   {% endif %}
   {% for obj_item in visible_children %}
      {% if obj_item.type not in own_page_types %}

   {{ obj_item.render()|indent(3) }}
      {% endif %}
   {% endfor %}
   {% if is_own_page and own_page_children %}
        {% set visible_attributes = own_page_children|selectattr("type", "equalto", "attribute")|list %}
        {% set visible_properties = own_page_children|selectattr("type", "equalto", "property")|list %}
        {% set all_visible_methods = own_page_children|selectattr("type", "equalto", "method") |list %}

        {% set visible_abstract_methods = [] %}
        {% set visible_constructor_methods = [] %}
        {% set visible_instance_methods = [] %}
        {% set visible_special_methods = [] %}
        {% set visible_static_methods = [] %}

        {% for element in all_visible_methods %}
            {% if "abstractmethod" in element.properties %}
                {% set _ = visible_abstract_methods.append(element) %}

            {% elif "staticmethod" in element.properties %}
                {% set _ = visible_static_methods.append(element) %}

            {% elif "classmethod" in element.properties or element.name in ["__new__", "__init__"] %}
                {% set _ = visible_constructor_methods.append(element) %}

            {% elif element.name.startswith("__") and element.name.endswith("__") and element.name not in ["__new__", "__init__"] %}
                {% set _ = visible_special_methods.append(element) %}

            {% else %}
                {% set _ = visible_instance_methods.append(element) %}

            {% endif %}
        {% endfor %}


        {% set class_objects = visible_properties + visible_attributes + all_visible_methods %}

        {# ------------------------ Begin tabset definition ----------------------- #}

        {% if class_objects %}

Overview
--------

.. tab-set::

            {% if visible_abstract_methods %}
    {{ tab_item_from_objects_list(visible_abstract_methods, "Abstract methods") }}
            {% endif %}

            {% if visible_constructor_methods %}
    {{ tab_item_from_objects_list(visible_constructor_methods, "Constructors") }}
            {% endif %}

            {% if visible_instance_methods %}
    {{ tab_item_from_objects_list(visible_instance_methods, "Methods") }}
            {% endif %}

            {% if visible_properties %}
    {{ tab_item_from_objects_list(visible_properties, "Properties") }}
            {% endif %}

            {% if visible_attributes %}
    {{ tab_item_from_objects_list(visible_attributes, "Attributes") }}      
            {% endif %}

            {% if visible_static_methods %}
    {{ tab_item_from_objects_list(visible_static_methods, "Static methods") }}
            {% endif %}

            {% if visible_special_methods %}
    {{ tab_item_from_objects_list(visible_special_methods, "Special methods") }}
            {% endif %}

        {% endif %}
{# ---------------------- End class tabset -------------------- #}
{# ---------------------- Begin class datails -------------------- #}

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

        {% if all_visible_methods  %}
Method detail
-------------
            {% for method in all_visible_methods %}
{{ method.render() }}
            {% endfor %}
        {% endif %}
    {% endif %}
{% endif %}

{# ---------------------- End class details -------------------- #}
