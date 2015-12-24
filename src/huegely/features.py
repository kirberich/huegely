from huegely import (
    exceptions,
    utils
)


class FeatureBase(object):
    """ Base interface for all features, mostly concerned with device state. """
    transition_time = None
    _reset_brightness_to = None

    def __init__(self, bridge, device_id, name=None, transition_time=None):
        if not (hasattr(self, '_device_url_prefix') and hasattr(self, '_state_attribute')):
            raise Exception("Classes using FeatureBase need to define _device_url_prefix and _state_attribute")

        self.bridge = bridge
        self.device_id = device_id
        self.device_url = '{}/{}'.format(self._device_url_prefix, device_id)

        self._name = name
        self.transition_time = transition_time

    def __repr__(self):
        return "{} {} (id: {})".format(
            self.__class__.__name__,
            self._name or "(unknown name)",
            self.device_id,
        )

    def __str__(self):
        return self._name or "(unknown name)"

    @property
    def transition_time(self):
        return self._transition_time if self._transition_time is not None else self.bridge.transition_time

    @transition_time.setter
    def transition_time(self, value):
        self._transition_time = value

    def _handle_transition_times(self, state):
        """ Applies globally set transition times and deals with a bug in the hue api that causes lights
            to turn on with brightness 1 when turned off with a transition time.
        """
        transition = state.get('transition_time', self.transition_time)
        if transition is not None:
            state['transition_time'] = round(transition / 10.0)
        return state

    def _set_state(self, **state):
        url = '{}/{}'.format(self.device_url, self._state_attribute)

        # Remove any Nones from state
        state = {key: value for key, value in state.items() if value is not None}

        state = self._handle_transition_times(state)

        # Convert huegely-named state attributes to hue api naming scheme
        state = utils.huegely_to_hue_names(state)

        response = self.bridge.make_request(url, method='PUT', **state)

        # Convert hue api names back to huegely names
        return utils.hue_to_huegely_names(response)

    def _get_state(self):
        response = self.bridge.make_request(self.device_url)

        # Whenever the state is received, store the name of the object, because we get it for free.
        # This could be done in the constructor, making the name always available,
        # but that would make initialisation extremely expensive.
        self._name = response.get('name', None) or self._name

        # Convert hue-named state attribute to huegely naming scheme
        state = utils.hue_to_huegely_names(response[self._state_attribute])

        return state

    def state(self, **state):
        """ Gets or sets state attributes. Call this without any arguments to get the
            entire state as reported by the Hue bridge. Note that the state reported by groups
            is unreliable - the values mostly seem to have no relation to the real lights. It is sometimes necessary
            to get the state though, especially when using the brighter/darker commands.

            Pass in any amount of state attributes to update them, e.g. on=True, brighter=50.

            Returns a dictionary of successfully updated attributes in the format of ``{'brightness': 100, 'on': True}``
        """
        return self._set_state(**state) if state else self._get_state()

    def _get_name(self):
        """ Returns the current name of the group """
        return self.bridge.make_request(self.device_url)['name']

    def _set_name(self, name):
        """ Set a new name for the group and returns the new name. """
        return self.bridge.make_request(self.device_url, method='PUT', name=name)['name']

    def name(self, name=None):
        """ Gets or sets the current name of the group. If called without *name* argument, returns the current group name.

            If called with a name argument, sets and returns the new name of the group.
        """
        return self._set_name(name=name) if name is not None else self._get_name()


class Dimmer(FeatureBase):
    """ Abstract base class for devices that allow dimming (which is all Hue devices currently being sold.) """

    def _handle_transition_times(self, state):
        """ Applies globally set transition times and deals with a bug in the hue api that causes lights
            to turn on with brightness 1 when turned off with a transition time.
        """
        state = super(Dimmer, self)._handle_transition_times(state)

        use_transition = state.get('transition_time', None) is not None
        needs_reset = self._reset_brightness_to is not None
        turn_on = state.get('on', None) is True or state.get('brightness', None) != 0
        turn_off = state.get('on', None) is False or state.get('brightness', None) == 0

        # Remember current brightness if a transition time is being used
        if use_transition and turn_off:
            self._reset_brightness_to = self.brightness()

        # Apply remembered brightness if light is being turned on
        if needs_reset and turn_on and not self.is_on():
            state['brightness'] = self._reset_brightness_to
            self._reset_brightness_to = None

        return state

    def _set_state(self, **state):
        """ Attribute names in *state* are mapped between how huegely names them and hue API ones.
            Usually this is taken care of simply by replacing the names, but in the case of ``darker`` and ``brighter``,
            just replacing the names isn't enough, because the hue api uses ``bri_inc`` for both.
        """
        if 'darker' in state:
            decrease = state.pop('darker')
            state['bri_inc'] = -decrease
        if 'brighter' in state:
            increase = state.pop('brighter')
            state['bri_inc'] = increase

        response = super(Dimmer, self)._set_state(**state)

        # The groups endpoint for updating state behaves differently to the lights one when it comes to
        # the brighter/darker commands. Instead of returning the new brightness, it instead returns the
        # requested value directly, e.g. {'bri_inc': 10} instead of {'brightness': 240}.
        # Because of that, we need to make another request to have consistent behaviour.

        if 'bri_inc' in response:
            extra_state = self.state()
            response.pop('bri_inc')
            response['brightness'] = extra_state['brightness']

        return response

    def on(self, transition_time=None):
        """ Turns light(s) on. Returns new state (*True*). """
        return self.state(on=True, transition_time=transition_time)['on']

    def off(self, transition_time=None):
        """ Turns light(s) off. Returns new state (*False*). """
        return self.state(on=False, transition_time=transition_time)['on']

    def is_on(self):
        """ Returns True if the light(s) is on, False otherwise. """
        return self.state()['on']

    def brighter(self, step=25, transition_time=None):
        """ Makes the light(s) gradually brighter. Turns light on if necessary.

            Returns new brightness value.
        """
        step = max(0, min(254, step))

        try:
            return self.state(brighter=step, transition_time=transition_time)['brightness']
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return self.state(on=True, brighter=step, transition_time=transition_time)['brightness']
            raise

    def darker(self, step=25, transition_time=None):
        """ Makes the light(s) gradually darker. Turns off if the brightness goes down to 0.

            Returns the new brightness value.
        """
        step = max(0, min(254, step))

        try:
            response = self.state(darker=step, transition_time=transition_time)
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

        # Turn the lamp off if the brightness reaches 0
        if response['brightness'] == 0:
            self.off(transition_time=transition_time)

        return response['brightness']

    def _set_brightness(self, brightness, transition_time=None):
        """ Sets brightness to specific value (0-254). Values are clamped to allowed range.

            Returns the new brightness value.
        """
        brightness = max(0, min(255, brightness))
        on = brightness != 0

        try:
            return self.state(on=on, brightness=brightness, transition_time=transition_time)['brightness']
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

    def _get_brightness(self):
        """ Gets current brightness value (0-254). """
        return self.state()['brightness']

    def brightness(self, brightness=None, transition_time=None):
        """ Returns the current brightness level if called without *brightness* argument, otherwise sets and returns the new value.

            The valid range for brightness values is 0 - 254, passed-in values are clamped to that range.
        """
        if brightness is not None:
            return self._set_brightness(brightness=brightness, transition_time=transition_time)
        return self._get_brightness()

    def _set_alert(self, alert):
        """ Sets alert to new value. The only currently supported alerts are 'none' and 'select'.

            Returns new alert value.
        """
        if alert not in ['none', 'select']:
            raise exceptions.HueError('Cannot set alert to {}. Only "none" and "select" are supported.', device=self)
        return self.state(alert=alert)['alert']

    def _get_alert(self):
        """ Gets current alert value ('none' or 'select'). """
        return self.state()['alert']

    def alert(self, alert=None):
        """ Returns the current alert value if called without *alert* argument,
            otherwise sets and returns the new alert.

            The only currently supported alerts are 'none' and 'select'.

            Note that alerts currently seem to be broken, or at least weird, in the hue api.
            Setting a select alert will blink a light once, but the alert state will stay on "select" until manually reset.
        """
        return self._set_alert(alert=alert) if alert is not None else self._get_alert()


class ColorController(FeatureBase):
    """ Abstract base class for colored lights. """

    def _set_coordinates(self, coordinates, transition_time=None):
        """ Sets coordinates to new value (each 0 - 1). Values are clamped to valid range.
            Returns new coordinate values.
        """
        x = max(0, min(1, coordinates[0]))
        y = max(0, min(1, coordinates[1]))
        return self.state(coordinates=(x, y), transition_time=transition_time)['coordinates']

    def _get_coordinates(self):
        """ Gets current coordinate values (each 0 - 1). """
        return self.state()['coordinates']

    def coordinates(self, coordinates=None, transition_time=None):
        """ Returns the current coolor coordinates value if called without *coordinates* argument,
            otherwise sets and returns the new value.

            *coordinates* is expected to be in the format of [x (float), y (float)].

            The valid range for each coordinate is 0 - 1, passed-in values are clamped to that range.

            Note that each lamp's color space is different and will choose the color coordinate
            they can reproduce closest to the requested value.
            See http://www.developers.meethue.com/documentation/core-concepts for details.
        """
        if coordinates is not None:
            return self._set_coordinates(coordinates=coordinates, transition_time=transition_time)
        return self._get_coordinates()

    def _set_hue(self, hue, transition_time=None):
        """ Sets hue to new value (0-65534). Values are cycled, i.e. 65535 == 0.

            Returns new hue value.
        """
        hue = hue % 65535
        return self.state(hue=hue, transition_time=transition_time)['hue']

    def _get_hue(self):
        """ Gets current hue value (0-65535). """
        return self.state()['hue']

    def hue(self, hue=None, transition_time=None):
        """ Returns the current hue value if called without *hue* argument,
            otherwise sets and returns the new value.

            The valid range for hues is 0 - 65534, passed-in values are **cycled** over that range.
            I.e. ``hue(65535)`` (red) is equal to ``hue(0)`` (also red).
        """
        return self._set_hue(hue=hue, transition_time=transition_time) if hue is not None else self._get_hue()

    def _set_saturation(self, saturation, transition_time=None):
        """ Sets saturation to new value (0-254). Values are clamped to allowed range.

            Returns new saturation value.
        """
        saturation = max(0, min(254, saturation))
        return self.state(saturation=saturation, transition_time=transition_time)['saturation']

    def _get_saturation(self):
        """ Gets current saturation value (0-254). """
        return self.state()['saturation']

    def saturation(self, saturation=None, transition_time=None):
        """ Returns the current saturation value if called without *saturation* argument,
            otherwise sets and returns the new value.

            The valid range for saturation is 0 - 254, passed-in values are clamped to that range.
        """
        if saturation is not None:
            return self._set_saturation(saturation=saturation, transition_time=transition_time)
        return self._get_saturation()

    def _set_effect(self, effect):
        """ Sets effect to new value. The only currently supported effects are 'none' and 'colorloop'.

            Returns new effect value.
        """
        if effect not in ['none', 'colorloop']:
            raise exceptions.HueError('Cannot set effect to {}. Only "none" and "colorloop" are supported.', device=self)
        return self.state(effect=effect)['effect']

    def _get_effect(self):
        """ Gets current effect value ('none' or 'colorloop'). """
        return self.state()['effect']

    def effect(self, effect=None):
        """ Returns the current effect value if called without *effect* argument,
            otherwise sets and returns the new effect.

            The only currently supported effects are 'none' and 'colorloop'.
        """
        return self._set_effect(effect=effect) if effect is not None else self._get_effect()

    def color_mode(self):
        """ Returns the current color_mode value (xy or ct).

            Note that this has only been tested on an ExtendedColorLight, because I don't have others.
            It might not work on ColorLights or ColorTemperatureLights.
        """
        return self.state()['color_mode']


class TemperatureController(FeatureBase):
    """ Abstract base class for lights that allow setting a color temperature for their white light. """

    def _set_temperature(self, temperature, transition_time=None):
        """ Sets color temperature to new value in mireds (154-500).
            Values are clamped to the allowed range.

            Returns new temperature.
        """
        temperature = max(154, min(500, temperature))
        return self.state(temperature=temperature, transition_time=transition_time)['temperature']

    def _get_temperature(self):
        """ Gets current color temperature in mireds (154-500). """
        return self.state()['temperature']

    def temperature(self, temperature=None, transition_time=None):
        """ Returns the current color temperature (in mireds) if called without *temperature* argument,
            otherwise sets and returns the new value.

            The valid range for color temperatures is 154 - 500, passed-in values are clamped to that range.
        """
        if temperature is not None:
            return self._set_temperature(temperature=temperature, transition_time=transition_time)
        return self._get_temperature()
