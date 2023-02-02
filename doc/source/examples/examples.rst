.. article-info::
    :avatar: images/ebp-logo.png
    :avatar-link: https://executablebooks.org/
    :avatar-outline: muted
    :author: Executable Books
    :date: Jul 24, 2021
    :read-time: 5 min read
    :class-container: sd-p-2 sd-outline-muted sd-rounded-1
:bdg:`plain badge`

:bdg-primary:`primary`, :bdg-primary-line:`primary-line`

:bdg-secondary:`secondary`, :bdg-secondary-line:`secondary-line`

:bdg-success:`success`, :bdg-success-line:`success-line`

:bdg-info:`info`, :bdg-info-line:`info-line`

:bdg-warning:`warning`, :bdg-warning-line:`warning-line`

:bdg-danger:`danger`, :bdg-danger-line:`danger-line`

:bdg-light:`light`, :bdg-light-line:`light-line`

:bdg-dark:`dark`, :bdg-dark-line:`dark-line`
:bdg-link-primary:`https://example.com`

:bdg-link-primary-line:`explicit title <https://example.com>`
.. button-link:: https://example.com

.. button-link:: https://example.com

    Button text

.. button-link:: https://example.com
    :color: primary
    :shadow:

.. button-link:: https://example.com
    :color: primary
    :outline:

.. button-link:: https://example.com
    :color: secondary
    :expand:
.. card:: Card Title

    Card content
.. card-carousel:: 2

    .. card:: card 1

        content

    .. card:: card 2

        Longer

        content

    .. card:: card 3

    .. card:: card 4

    .. card:: card 5

    .. card:: card 6
.. card:: Card Title

    Header
    ^^^
    Card content
    +++
    Footer
.. grid:: 2 3 3 4

    .. grid-item::

        .. card:: Title
            :img-background: images/particle_background.jpg
            :class-card: sd-text-black

            Text

    .. grid-item-card:: Title
        :img-top: images/particle_background.jpg

        Header
        ^^^
        Content
        +++
        Footer

    .. grid-item-card:: Title
        :img-bottom: images/particle_background.jpg

        Header
        ^^^
        Content
        +++
        Footer
.. _cards-clickable:

Cards Clickable
...............

.. card:: Clickable Card (external)
    :link: https://example.com

    The entire card can be clicked to navigate to https://example.com.

.. card:: Clickable Card (internal)
    :link: cards-clickable
    :link-type: ref

    The entire card can be clicked to navigate to the ``cards`` reference target.
.. _target:
.. card:: Card Title https://example.com :ref:`link <target>`

    Card content
.. div:: sd-text-center sd-font-italic sd-text-primary

    Some CSS styled text
.. dropdown::

    Dropdown content

.. dropdown:: Dropdown title

    Dropdown content

.. dropdown:: Open dropdown
    :open:

    Dropdown content
.. dropdown:: Title
    :name: target
    :color: info
    :icon: alert
    :margin: 1
    :class-container: class-container
    :class-title: class-title
    :class-body: class-body

    Dropdown content

:ref:`target`, :ref:`text <target>`
.. grid:: 1 2 3 4
    :outline:

    .. grid-item::

        A

    .. grid-item::

        B

    .. grid-item::

        C

    .. grid-item::

        D
.. grid:: 2

    .. grid-item-card::
        :columns: auto

        A

    .. grid-item-card::
        :columns: 12 6 6 6

        B

    .. grid-item-card::
        :columns: 12

        C
.. grid:: 2

    .. grid-item-card::  Title 1

        A

    .. grid-item-card::  Title 2

        B
.. grid:: 2
    :gutter: 1

    .. grid-item-card::

        A

    .. grid-item-card::

        B

.. grid:: 2
    :gutter: 3 3 4 5

    .. grid-item-card::

        A

    .. grid-item-card::

        B
.. grid:: 1 1 2 2
    :gutter: 1

    .. grid-item::

        .. grid:: 1 1 1 1
            :gutter: 1

            .. grid-item-card:: Item 1.1

                Multi-line

                content

            .. grid-item-card:: Item 1.2

                Content

    .. grid-item::

        .. grid:: 1 1 1 1
            :gutter: 1

            .. grid-item-card:: Item 2.1

                Content

            .. grid-item-card:: Item 2.2

                Content

            .. grid-item-card:: Item 2.3

                Content
An icon :fas:`spinner;sd-bg-primary sd-bg-text-primary`, some more text.
- A regular icon: :material-regular:`data_exploration;2em`, some more text
- A coloured regular icon: :material-regular:`settings;3em;sd-text-success`, some more text.
- A coloured outline icon: :material-outlined:`settings;3em;sd-text-success`, some more text.
- A coloured sharp icon: :material-sharp:`settings;3em;sd-text-success`, some more text.
- A coloured round icon: :material-round:`settings;3em;sd-text-success`, some more text.
- A coloured two-tone icon: :material-twotone:`settings;3em;sd-text-success`, some more text.
- A fixed size icon: :material-regular:`data_exploration;24px`, some more text.
A coloured icon: :octicon:`report;1em;sd-text-info`, some more text.
.. tab-set::

    .. tab-item:: Label1

        Content 1

    .. tab-item:: Label2

        Content 2
.. tab-set-code::

    .. literalinclude:: ./snippet.py
        :language: python

    .. code-block:: javascript

        a = 1;
.. tab-set::
    :class: class-set

    .. tab-item:: Label
        :name: target
        :selected:
        :class-container: class-container
        :class-label: class-label
        :class-content: class-content

        Content

:ref:`target`, :ref:`text <target>`
.. tab-set::

    .. tab-item:: Label1
        :sync: key1

        Content 1

    .. tab-item:: Label2
        :sync: key2

        Content 2

.. tab-set::

    .. tab-item:: Label1
        :sync: key1

        Content 1

    .. tab-item:: Label2
        :sync: key2

        Content 2
