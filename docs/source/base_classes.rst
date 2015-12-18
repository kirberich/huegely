------------
Base Classes
------------

These are the bases which all light classes are built upon. Each class describes the behaviour of one specific light feature-set, which are mixed and matched in different hue lights.

.. autoclass:: huegely.devices.Light
    :members:
    :undoc-members:

    .. attribute:: bridge
        :annotation:  - Instance of huegely.Bridge this light belongs to

    .. attribute:: light_id
        :annotation:  - Identifier for this light in the hue bridge

.. autoclass:: huegely.features.Dimmer
    :members:
    :undoc-members:

.. autoclass:: huegely.features.ColorController
    :members:
    :undoc-members:

.. autoclass:: huegely.features.TemperatureController
    :members:
    :undoc-members:
