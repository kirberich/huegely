from abc import ABCMeta

from . import exceptions


class Dimmer(metaclass=ABCMeta):
    """ Abstract base class for devices that allow dimming (which is all Hue devices currently being sold.) """

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

    def on(self):
        """ Turns light(s) on. Returns new state (*True*). """
        return self.state(on=True)['on']

    def off(self):
        """ Turns light(s) off. Returns new state (*False*). """
        return self.state(on=False)['on']

    def is_on(self):
        """ Returns True if the light(s) is on, False otherwise. """
        return self.state()['on']

    def brighter(self, step=25):
        """ Makes the light(s) gradually brighter. Turns light on if necessary.

            Returns new brightness value.
        """
        step = max(0, min(254, step))

        try:
            return self.state(brighter=step)['brightness']
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return self.state(on=True, brighter=step)['brightness']
            raise

    def darker(self, step=25):
        """ Makes the light(s) gradually darker. Turns off if the brightness goes down to 0.

            Returns the new brightness value.
        """
        step = max(0, min(254, step))

        try:
            response = self.state(darker=step)
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

        # Turn the lamp off if the brightness reaches 0
        if response['brightness'] == 0:
            self.off()

        return response['brightness']

    def _set_brightness(self, brightness):
        """ Sets brightness to specific value (0-254). Values are clamped to allowed range.

            Returns the new brightness value.
        """
        brightness = max(0, min(255, brightness))
        on = brightness != 0

        try:
            return self.state(on=on, brightness=brightness)['brightness']
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

    def _get_brightness(self):
        """ Gets current brightness value (0-254). """
        return self.state()['brightness']

    def brightness(self, brightness=None):
        """ Returns the current brightness level if called without *brightness* argument, otherwise sets and returns the new value.

            The valid range for brightness values is 0 - 254, passed-in values are clamped to that range.
        """
        return self._set_brightness(brightness=brightness) if brightness is not None else self._get_brightness()

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


class ColorController(metaclass=ABCMeta):
    """ Abstract base class for colored lights. """

    def _set_coordinates(self, coordinates):
        """ Sets coordinates to new value (each 0 - 1). Values are clamped to valid range.
            Returns new coordinate values.
        """
        x = max(0, min(1, coordinates[0]))
        y = max(0, min(1, coordinates[1]))
        return self.state(coordinates=(x, y))['coordinates']

    def _get_coordinates(self):
        """ Gets current coordinate values (each 0 - 1). """
        return self.state()['coordinates']

    def coordinates(self, coordinates=None):
        """ Returns the current coolor coordinates value if called without *coordinates* argument,
            otherwise sets and returns the new value.

            *coordinates* is expected to be in the format of [x (float), y (float)].

            The valid range for each coordinate is 0 - 1, passed-in values are clamped to that range.

            Note that each lamp's color space is different and will choose the color coordinate
            they can reproduce closest to the requested value.
            See http://www.developers.meethue.com/documentation/core-concepts for details.
        """
        return self._set_coordinates(coordinates=coordinates) if coordinates is not None else self._get_coordinates()

    def _set_hue(self, hue):
        """ Sets hue to new value (0-65534). Values are cycled, i.e. 65535 == 0.

            Returns new hue value.
        """
        hue = hue % 65535
        return self.state(hue=hue)['hue']

    def _get_hue(self):
        """ Gets current hue value (0-65535). """
        return self.state()['hue']

    def hue(self, hue=None):
        """ Returns the current hue value if called without *hue* argument,
            otherwise sets and returns the new value.

            The valid range for hues is 0 - 65534, passed-in values are **cycled** over that range.
            I.e. ``hue(65535)`` (red) is equal to ``hue(0)`` (also red).
        """
        return self._set_hue(hue=hue) if hue is not None else self._get_hue()

    def _set_saturation(self, saturation):
        """ Sets saturation to new value (0-254). Values are clamped to allowed range.

            Returns new saturation value.
        """
        saturation = max(0, min(254, saturation))
        return self.state(saturation=saturation)['saturation']

    def _get_saturation(self):
        """ Gets current saturation value (0-254). """
        return self.state()['saturation']

    def saturation(self, saturation=None):
        """ Returns the current saturation value if called without *saturation* argument,
            otherwise sets and returns the new value.

            The valid range for saturation is 0 - 254, passed-in values are clamped to that range.
        """
        return self._set_saturation(saturation=saturation) if saturation is not None else self._get_saturation()

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


class TemperatureController(metaclass=ABCMeta):
    """ Abstract base class for lights that allow setting a color temperature for their white light. """

    def _set_temperature(self, temperature):
        """ Sets color temperature to new value in mireds (154-500).
            Values are clamped to the allowed range.

            Returns new temperature.
        """
        temperature = max(154, min(500, temperature))
        return self.state(temperature=temperature)['temperature']

    def _get_temperature(self):
        """ Gets current color temperature in mireds (154-500). """
        return self.state()['temperature']

    def temperature(self, temperature=None):
        """ Returns the current color temperature (in mireds) if called without *temperature* argument,
            otherwise sets and returns the new value.

            The valid range for color temperatures is 154 - 500, passed-in values are clamped to that range.
        """
        return self._set_temperature(temperature=temperature) if temperature is not None else self._get_temperature()
