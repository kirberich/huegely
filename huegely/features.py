from abc import ABCMeta

from . import exceptions


class Dimmer(metaclass=ABCMeta):
    """ Abstract base class for lights that allow dimming (which is all Hue lights currently being sold.) """

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
        return self.state(on=True, bri_inc=step)['bri']

    def darker(self, step=25):
        """ Makes the light gradually darker. Turns off the lamp if the brightness goes down to 0.

            Returns the new brightness value.
        """
        step = max(0, min(254, step))

        try:
            response = self.state(bri_inc=step * -1)
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

        # Turn the lamp off if the brightness reaches 0
        if response['bri'] == 0:
            self.off()

        return response['bri']

    def _set_brightness(self, brightness):
        """ Sets brightness to specific value (0-254). Values are clamped to allowed range.

            Returns the new brightness value.
        """
        brightness = max(0, min(255, brightness))
        on = brightness != 0

        try:
            return self.state(on=on, bri=brightness)['bri']
        except exceptions.HueError as e:
            if e.error_code == exceptions.CANNOT_MODIFY_WHILE_OFF:
                return 0
            raise

    def _get_brightness(self):
        """ Gets current brightness value (0-254). """
        return self.state()['bri']

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
        return self.state(sat=saturation)['sat']

    def _get_saturation(self):
        """ Gets current saturation value (0-254). """
        return self.state()['sat']

    def saturation(self, saturation=None):
        """ Returns the current saturation value if called without *saturation* argument,
            otherwise sets and returns the new value.

            The valid range for saturation is 0 - 254, passed-in values are clamped to that range.
        """
        return self._set_saturation(saturation=saturation) if saturation is not None else self._get_saturation()


class TemperatureController(metaclass=ABCMeta):
    """ Abstract base class for lights that allow setting a color temperature for their white light. """

    def _set_temperature(self, mireds):
        """ Sets color temperature to new value in mireds (154-500).
            Values are clamped to the allowed range.

            Returns new temperature.
        """
        mireds = max(154, min(500, mireds))
        return self.state(ct=mireds)['ct']

    def _get_temperature(self):
        """ Gets current color temperature in mireds (154-500). """
        return self.state()['ct']

    def temperature(self, mireds=None):
        """ Returns the current color temperature (in mireds) if called without *mireds* argument,
            otherwise sets and returns the new value.

            The valid range for color temperatures is 154 - 500, passed-in values are clamped to that range.
        """
        return self._set_temperature(mireds=mireds) if mireds is not None else self._get_temperature()
