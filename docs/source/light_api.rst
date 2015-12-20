*********
Light API
*********

There are four classes for lights: ``DimmableLight``, ``ColorTemperatureLight``, ``ColorLight`` and ``ExtendedColorLight``. They do what their names suggest, ``ExtendedColorLight`` allows setting the color temperature as well as the actual color.

The different lights inherit from a common base class called ``Light`` and their appropriate feature sets. See below for a description of the features.

.. NOTE::
   All API requests will raise a HueError if at least one requested operation fails. There is no concept of transactions with Hue lights, so an error in one operation does not necessarily mean another action isn't applied.


**DimmableLight Example**::

    light.on()     # Turns light on
    light.is_on()  # True
    light.off()    # Turns light off
    light.is_on()  # False

    light.brightness(254)  # Light is now at maximum brightness
    light.darker(54)       # Brightness is now 200
    light.darker(200)      # Light is now off

    light.set_state(on=True, brightness=100)

    # This will raise an error, dimmers don't support setting hue values.
    light.set_state(hue=0)


**ExtendedColorLight Example**::

    # Set light to bright red
    light.set_state(on=True, brightness=255, hue=0, saturation=255)

    # Some requests are inherently impossible. This won't raise an error, but only 
    # the color temperature setting will have an effect. (Color temperature has a higher priority than color.)
    light.set_state(hue=0, temperature=500)

.. toctree::
   :maxdepth: 2

   dimmable_light
   color_temperature_light
   color_light
   extended_color_light
   base_classes