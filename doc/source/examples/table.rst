.. _table:

Table
=====
The rendering of table directive with ansys sphinx theme.

Data table
----------
Here is the data table.

.. code:: rst

    .. table::
        :class: datatable

        =====  =====  =======
        A      B      A and B
        =====  =====  =======
        False  False  False
        True   False  False
        False  True   False
        True   True   True
        =====  =====  =======

.. table::
    :class: datatable

    =====  =====  =======
    A      B      A and B
    =====  =====  =======
    False  False  False
    True   False  False
    False  True   False
    True   True   True
    =====  =====  =======

Longtable-centered
------------------
Here is the long table. 

.. code:: rst

    .. table:: 
        :class: longtable-centered

        +---------------------------+-------------------+
        |                           | MAPDL Command     |
        +===========================+===================+
        | **GUI commands**          | * ``*ASK``        |
        |                           |                   |
        | **GUI commands**          | * ``*ASK``        |
        |                           |                   |
        | **GUI commands**          | * ``*ASK``        |
        +---------------------------+-------------------+

.. table:: 
   :class: longtable-centered

   +---------------------------+-------------------+
   |                           | MAPDL Command     |
   +===========================+===================+
   | **GUI commands**          | * ``*ASK``        |
   |                           |                   |
   | **GUI commands**          | * ``*ASK``        |
   |                           |                   |
   | **GUI commands**          | * ``*ASK``        |
   +---------------------------+-------------------+

Table-centered
--------------
Here is the table centered.

.. code:: rst

    .. table:: 
        :class: table-centered

        +---------------------------+-------------------+
        |                           | MAPDL Command     |
        +===========================+===================+
        | **GUI commands**          | * ``*ASK``        |
        +---------------------------+-------------------+
        | **GUI commands**          | * ``*ASK``        |
        +---------------------------+-------------------+
        | **GUI commands**          | * ``*ASK``        |
        +---------------------------+-------------------+

.. table::
    :class: table-centered

    +---------------------------+-------------------+
    |                           | MAPDL Command     |
    +===========================+===================+
    | **GUI commands**          | * ``*ASK``        |
    +---------------------------+-------------------+
    | **GUI commands**          | * ``*ASK``        |
    +---------------------------+-------------------+
    | **GUI commands**          | * ``*ASK``        |
    +---------------------------+-------------------+