from huegely.features import (
    FeatureBase,
    Dimmer,
    ColorController,
    TemperatureController,
)


class Light(FeatureBase):
    """ Abstract base class for all lights.
        All lights inherit from ``Light`` and any appropriate feature classes.
    """
    _state_attribute = 'state'
    _device_url_prefix = 'lights'

    def is_reachable(self):
        """ Returns True if the light is currently reachable, False otherwise. """
        return self._get_state()['is_reachable']


class DimmableLight(Dimmer, Light):
    pass


class ColorLight(Dimmer, ColorController, Light):
    pass


class ColorTemperatureLight(Dimmer, TemperatureController, Light):
    pass


class ExtendedColorLight(Dimmer, TemperatureController, ColorController, Light):
    pass


LIGHT_TYPES = {
    'Dimmable light': DimmableLight,
    'Color light': ColorLight,
    'Color temperature light': ColorTemperatureLight,
    'Extended color light': ExtendedColorLight
}
