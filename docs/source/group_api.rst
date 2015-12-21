*********
Group API
*********

There are four classes for groups: ``DimmableGroup``, ``ColorTemperatureGroup``, ``ColorGroup`` and ``ExtendedColorGroup``. They behave exactly like the analogous classes for lights, in fact they use the same feature classes to implement their behaviour.

.. WARNING::
  In general, group behaviour is not very consistent. Setting attributes on a group where not all lights support the attribute is allowed by the hue API, just be aware that any action on a group may have an effect on none, some, or all of the lights, without raising an error.


**Group Example**::

    group.on()     # Turns all lights in group on
    group.is_on()  # True
    group.off()    # Turns all lights in group off
    group.is_on()  # False

    group.brightness(254)  # all lights in group are now at maximum brightness
    group.darker(54)       # Brightness is now 200
    group.darker(200)      # group is now off

    group.set_state(on=True, brightness=100)

    # Get all lights of this group
    lights = group.lights()


.. toctree::
   :maxdepth: 2

   dimmable_group
   color_temperature_group
   color_group
   extended_color_group
   base_classes