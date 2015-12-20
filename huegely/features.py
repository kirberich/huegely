from abc import ABCMeta

from . import exceptions


class Dimmer(metaclass=ABCMeta):
    """ Abstract base class for lights that allow dimming (which is all Hue lights currently being sold.) """

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

        return super(Dimmer, self)._set_state(**state)

    def on(self):
        """ Turns light on. Returns new state (*True*). """
        return self.state(on=True)['on']

    def off(self):
        """ Turns light off. Returns new state (*False*). """
        return self.state(on=False)['on']

    def is_on(self):
        """ Returns True if the light is on, False otherwise. """
        return self.state()['on']

    def brighter(self, step=25):
        """ Makes the lamp gradually brighter. Turns the light on if it was off before.

            Returns new brightness value.
        """
        step = max(0, min(254, step))
        return self.state(on=True, brighter=step)['brightness']

    def darker(self, step=25):
        """ Makes the light gradually darker. Turns off the lamp if the brightness goes down to 0.

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


class ColorController(metaclass=ABCMeta):
    """ Abstract base class for colored lights. """

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
