****************
Transition Times
****************

The hue API supports setting transition times per operation, but not globally. Huegely extends this with three different ways of setting transition times. All of these work the same on groups and lights.

.. NOTE::
  Setting transition times does not cause any additonal requests, so performance-wise it shouldn't be a consideration. *However*, there is a bug in the hue API that that causes any light that is turned off with a transition specified to be at minimum brightness when turned back on. Huegely deals with this by remembering the brightness and re-applying it when the light is turned on, which causes one extra request.

  This will work fine if only huegely is used to control the lights, but there are scenarios where it will still cause problems:

  - If a light is turned off with a transition and some other app turns it back on, the brightness won't be applied.
  - If a light is turned off with a transition, some other app turns it on, modifies the brightness and turns it back off, the next time huegely turns it on the saved brightness will be applied.

  ** Basically, if in doubt, don't use transition times for turning lights off. **

.. NOTE::
  The hue API uses decaseconds for transition-times, but huegely uses seconds.

1. Set a default transition time on the bridge:

    bridge.transition_time = 50
    light.brightness(10) # 5s

2. Set a default transition time on the light/group, which overrides defaults on the bridge::

    light.transition_time = 50
    light.brightness(10)

3. Set the transition time on any action directly, which overrides any defaults::

    light.state(brightness=10, transition_time=50)
    group.brightness(10, transition-time=10)
