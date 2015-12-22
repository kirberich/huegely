from huegely import (
    utils
)
from huegely.features import (
    Dimmer,
    ColorController,
    TemperatureController,
)


class Light(object):
    """ Abstract base class for all lights.
        All lights inherit from ``Light`` and any appropriate feature classes.
    """

    def __init__(self, bridge, light_id, name=None):
        self.bridge = bridge
        self.light_id = light_id
        self.light_url = 'lights/{}'.format(light_id)

        self._name = name

    def __repr__(self):
        return "{} {} (id: {})".format(
            self.__class__.__name__,
            self._name or "(unknown name)",
            self.light_id,
        )

    def __str__(self):
        return self._name or "(unknown name)"

    def _set_state(self, **state):
        url = self.light_url + '/state'

        # Convert huegely-named state attributes to hue api naming scheme
        state = utils.huegely_to_hue_names(state)

        response = self.bridge.make_request(url, method='PUT', **state)

        # Convert hue api names back to huegely names
        return utils.hue_to_huegely_names(response)

    def _get_state(self):
        response = self.bridge.make_request(self.light_url)

        # Whenever the state is received, store the name of the object, because we get it for free.
        # This could be done in the constructor, making the name always available,
        # but that would make initialisation extremely expensive.
        self._name = response.get('name', None) or self._name

        # Convert hue-named state attribute to huegely naming scheme
        state = utils.hue_to_huegely_names(response['state'])

        return state

    def state(self, **state):
        """ Gets or sets state attributes on a light. Call this without any arguments to get the
            entire state of the light as reported by the Hue bridge.

            Pass in any amount of state attributes to update them, e.g. on=True, brighter=50.

            Returns a dictionary of successfully updated attributes in the format of ``{'brightness': 100, 'on': True}``
        """
        return self._set_state(**state) if state else self._get_state()

    def _get_name(self):
        """ Returns the current name of the light """
        return self.bridge.make_request(self.light_url)['name']

    def _set_name(self, name):
        """ Set a new name for the light and returns the new name. """
        return self.bridge.make_request(self.light_url, method='PUT', name=name)['name']

    def name(self, name=None):
        """ Gets or sets the current name of the hue bridge. If called without *name* argument, returns the current bridge name.

            If called with a name argument, sets and returns the new name of the bridge.
        """
        return self._set_name(name=name) if name is not None else self._get_name()

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
