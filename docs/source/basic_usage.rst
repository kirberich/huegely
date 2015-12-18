-----------
Basic Usage
-----------

""""""
Tokens
""""""

Get started by instantiating a ``Bridge`` object. In normal use, this requires an authentication token (called ``username`` by Hue). When starting a new application, getting this token is usually the first step. 

**Obtaining a token**::

    import huegely
    bridge = huegely.Bridge(brige_ip)
    token = bridge.get_token('my_new_app')

**Normal usage**::

    import huegely
    bridge = huegely.Bridge(bridge_ip, token)


""""""""""""""""
Accessing Lights
""""""""""""""""

You can get a list of all connected lights via ``bridge.lights()``. This makes a single API request and instantiates the appropriate light objects. Different types of lights have different functionality, see :doc:`light_api` for details.

::

    bridge.lights()

    # [ExtendedColorLight Light one (id: 1),
    #  ExtendedColorLight Light two (id: 2),
    #  ExtendedColorLight Another light (id: 3),
    #  DimmableLight Boring no-color light (id: 4)]

"""""""""""""""""""
Working with Lights
"""""""""""""""""""

Once you have a light object, you can either get/set attributes one at a time, or request/update the entire light state.

::

    # Note this is assuming an ExtendedColorLight
    light.on()
    True

    light.off()
    False

    light.is_on()
    False

    # Get current brightness
    light.brightness()
    200

    light.brighter()
    225

    light.brighter(step=50)
    254

    light.darker()
    229

    light.brightness(254)
    254

    light.hue(50000)
    50000

    light.saturation(127)
    127

    # Set the color temperature in mireds
    light.temperature(500)
    500

    # Get the current state of the light
    light.state()
    {'colormode': 'ct', 'reachable': True, 'effect': 'none', 'hue': 12510, 'ct': 500, 'on': True, 'alert': 'none', 'sat': 226, 'xy': [0.5268, 0.4133], 'bri': 254}

    # Set multiple attributes at once
    light.state(hue=0, bri=255, sat=0, on=True)
    {'sat': 0, 'hue': 0, 'bri': 254, 'on': True}
