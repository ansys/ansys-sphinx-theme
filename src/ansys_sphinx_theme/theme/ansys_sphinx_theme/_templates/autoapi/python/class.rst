{% if obj.display %}

{{ obj.short_name }}
{{"=" * obj.name|length }}

.. py:{{ obj["type"] }}:: {{ obj["short_name"] }}{% if obj["args"] %}({{ obj["args"] }}){% endif %}

   :canonical: {{ obj["obj"]["full_name"] }}.{{ obj["short_name"] }}


{% for (args, return_annotation) in obj.overloads %}
    {{ " " * (obj.type | length) }}   {{ obj.short_name }}{% if args %}({{ args }}){% endif %}
{% endfor %}

{% set testing = 'it worked' %}

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

{% for element in visible_methods %}
    {% if "abstractmethod" in element.properties %}
        {% set _ = visible_abstract_methods.append(element) %}
    {% elif element.is_special %}
        {% set _ = visible_special_methods.append(element) %}
    {% endif %}
{% endfor %}


{% set class_objects = visible_properties + visible_attributes + visible_methods %}

{% if class_objects %}
.. py:currentmodule:: {{ obj.short_name }}
.. tab-set::

{% if visible_properties %}
    .. tab-item:: Properties

        .. list-table::
           :header-rows: 1
           :widths: auto

           * - Property
             - Summary

           {% for property in visible_properties %}
           * - :py:attr:`~{{ property.name }}`
             - {{ property.summary }}
           {% endfor %}

{% endif %}

{% if visible_attributes %}
    .. tab-item:: Attributes

        .. list-table::
           :header-rows: 1
           :widths: auto
            
           * - Attribute
             - Summary

           {% for attribute in visible_attributes %}
           * - :py:attr:`~{{ attribute.name }}`
             - {{ attribute.summary }}
           {% endfor %}
            
{% endif %}

{% if visible_methods %}
    .. tab-item:: All Methods

       .. list-table::
          :header-rows: 1
          :widths: auto

          * - Method
            - Summary

          {% for method in visible_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}

{% if visible_abstract_methods %}
    .. tab-item:: Abstract Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_abstract_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}

{% if visible_special_methods %}
    .. tab-item:: Special Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_special_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}

{% endif %}
{% endif %}


{% if visible_properties  %}

Property detail
~~~~~~~~~~~~~~~
{% for property in visible_properties %}
{{ property.render()|indent(3) }}
{% endfor %}
{% endif %}


{% if visible_attributes  %}
Attribute detail
~~~~~~~~~~~~~~~~
{% for attribute in visible_attributes %}
{{ attribute.render()|indent(3) }}
{% endfor %}
{% endif %}

{% if visible_methods  %}
Method detail
~~~~~~~~~~~~~
{% for method in visible_methods %}
{{ method.render()|indent(3) }}
{% endfor %}
{% endif %}