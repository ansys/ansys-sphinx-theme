{% if obj.display %}

{{ obj.short_name }}
{{"=" * obj.name|length }}

.. py:{{ obj["type"] }}:: {{ obj["short_name"] }}{% if obj["args"] %}({{ obj["args"] }}){% endif %}

   :canonical: {{ obj["obj"]["full_name"] }}


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

overview
~~~~~~~~
.. py:currentmodule:: {{ obj.short_name }}
.. tab-set::

{% if visible_constructors %}
    .. tab-item:: Constructors

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for constructor in visible_constructors %}
          * - :py:attr:`~{{ constructor.name }}`
            - {{ constructor.summary }}
          {% endfor %}
{% endif %}

{% if visible_properties %}
    .. tab-item:: Properties

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for property in visible_properties %}
           * - :py:attr:`~{{ property.name }}`
             - {{ property.summary }}
           {% endfor %}

{% endif %}

{% if visible_attributes %}
    .. tab-item:: Attributes

        .. list-table::
           :header-rows: 0
           :widths: auto

           {% for attribute in visible_attributes %}
           * - :py:attr:`~{{ attribute.name }}`
             - {{ attribute.summary }}
           {% endfor %}
            
{% endif %}

{% if visible_methods %}
    .. tab-item:: Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}
{% if visible_instance_methods %}
    .. tab-item:: Instance Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_instance_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}

{% if visible_class_methods %}
    .. tab-item:: Class Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_class_methods %}
          * - :py:attr:`~{{ method.name }}`
            - {{ method.summary }}
          {% endfor %}
{% endif %}

{% if visible_static_methods %}
    .. tab-item:: Static Methods

       .. list-table::
          :header-rows: 0
          :widths: auto

          {% for method in visible_static_methods %}
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

{% endif %}
{% endif %}

import detail
~~~~~~~~~~~~~~

.. code-block:: python

    from {{ obj.obj["full_name"] }} import {{ obj["short_name"] }}

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