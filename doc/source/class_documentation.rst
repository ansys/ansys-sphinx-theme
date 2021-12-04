*****************
API Documentation
*****************

User Guide Documentation Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two main ways of documenting a class using Sphinx.  The
first approach is to detail its usage via a "User Guide", or manually
created example designed to be read within documentation.  This
approach works when demonstrating the usage of a class.  For example,
using the ``.. code:: python`` directive:

.. code::

   Initialize ``my_module.MyClass`` with initial parameters.  These
   parameters are automatically assigned to the class.

    .. code:: python

       >>> from my_module import MyClass
       >>> my_obj = MyClass(parm1='apple', parm2='orange')
       >>> my_obj.parm1
       'apple'

Initialize ``my_module.MyClass`` with initial parameters.  These
parameters are automatically assigned to the class.

.. code:: python

   >>> from my_module import MyClass
   >>> my_obj = MyClass(parm1='apple', parm2='orange')
   >>> my_obj.parm1
   'apple'



Autoclass Directive
~~~~~~~~~~~~~~~~~~~

The "user guide" approach works for explaining the "why" and "how" of a class.  As
for the "what" of a class, you can describe the API automatically
using the ``autoclass`` directive:


.. code::

   .. autoclass:: pyansys_sphinx_theme.samples.ExampleClass
       :members:


.. autoclass:: pyansys_sphinx_theme.samples.ExampleClass
    :members:



Autosummary Directive
~~~~~~~~~~~~~~~~~~~~~
Simple classes can be easily represented using the ``autoclass``
directive, but more complex classes with many methods should be
documented via the ``autosummary`` directive.  For example,

.. code::

   .. autosummary::
      :toctree: _autosummary

      pyansys_sphinx_theme.samples.Complex


Will generate the following documentation:

.. autosummary::
   :toctree: _autosummary

   pyansys_sphinx_theme.samples.Complex

Each class will have its own dedicated page, and each method and
attribute in that class will also have its own page.
