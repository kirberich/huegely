------------
Base Classes
------------

These are the bases which all light/group classes are built upon. Each class describes the behaviour of one specific light feature-set, which are mixed and matched in different hue lights.

.. autoclass:: huegely.lights.Light
    :members:
    :undoc-members:

    .. attribute:: bridge
        :annotation:  - Instance of huegely.Bridge this light belongs to

    .. attribute:: light_id
        :annotation:  - Identifier for this light in the hue bridge

.. autoclass:: huegely.groups.Group
    :members:
    :undoc-members:

    .. attribute:: bridge
        :annotation:  - Instance of huegely.Bridge this group belongs to

    .. attribute:: group_id
        :annotation:  - Identifier for this group in the hue bridge

.. autoclass:: huegely.features.Dimmer
    :members:
    :undoc-members:

.. autoclass:: huegely.features.ColorController
    :members:
    :undoc-members:

.. autoclass:: huegely.features.TemperatureController
    :members:
    :undoc-members:
