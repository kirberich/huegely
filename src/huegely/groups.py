from huegely import (
    features,
    utils,
)


class Group(object):
    _identifier_actions = []  # Minimum set of group actions required to identify the group type

    def __init__(self, bridge, group_id, name=None):
        self.bridge = bridge
        self.group_id = group_id
        self.group_url = 'groups/{}'.format(group_id)

        self._name = name

    def __repr__(self):
        return "{} {} (id: {})".format(
            self.__class__.__name__,
            self._name or "(unknown name)",
            self.group_id,
        )

    def __str__(self):
        return self._name or "(unknown name)"

    def lights(self):
        """ Returns all lights that belong to this group. """
        light_ids = [int(light_id) for light_id in self.bridge.make_request(self.group_url)['lights']]
        return [light for light in self.bridge.lights() if light.light_id in light_ids]

    def _set_state(self, **state):
        url = self.group_url + '/action'

        # Convert huegely-named state attributes to hue api naming scheme
        state = utils.huegely_to_hue_names(state)

        response = self.bridge.make_request(url, method='PUT', **state)

        # Convert hue api names back to huegely names
        return utils.hue_to_huegely_names(response)

    def _get_state(self):
        response = self.bridge.make_request(self.group_url)

        # Whenever the state is received, store the name of the object, because we get it for free.
        # This could be done in the constructor, making the name always available,
        # but that would make initialisation extremely expensive.
        self._name = response.get('name', None) or self._name

        # Convert hue-named state attribute to huegely naming scheme
        state = utils.hue_to_huegely_names(response['action'])

        return state

    def state(self, **state):
        """ Gets or sets state attributes on a group. Call this without any arguments to get the
            entire state of the group as reported by the Hue bridge. Note that the state reported by groups
            is unreliable - the values mostly seem to have no relation to the real lights. It is sometimes necessary
            to get the state though, especially when using the brighter/darker commands.

            Pass in any amount of state attributes to update them, e.g. on=True, brighter=50.

            Returns a dictionary of successfully updated attributes in the format of ``{'brightness': 100, 'on': True}``
        """
        return self._set_state(**state) if state else self._get_state()


    def _get_name(self):
        """ Returns the current name of the group """
        return self.bridge.make_request(self.group_url)['name']

    def _set_name(self, name):
        """ Set a new name for the group and returns the new name. """
        return self.bridge.make_request(self.group_url, method='PUT', name=name)['name']

    def name(self, name=None):
        """ Gets or sets the current name of the group. If called without *name* argument, returns the current group name.

            If called with a name argument, sets and returns the new name of the group.
        """
        return self._set_name(name=name) if name is not None else self._get_name()


class DimmableGroup(features.Dimmer, Group):
    _identifier_actions = ['brightness']


class ColorGroup(features.Dimmer, features.ColorController, Group):
    _identifier_actions = ['hue']


class ColorTemperatureGroup(features.Dimmer, features.TemperatureController, Group):
    _identifier_actions = ['temperature']


class ExtendedColorGroup(features.Dimmer, features.TemperatureController, features.ColorController, Group):
    _identifier_actions = ['temperature', 'hue']


def get_group_type(group_actions):
    """ Gets the appropriate group type for a group of lamps.
        The API doesn't identify the different types of groups directly, it only returns the available actions.
        So, we go through the options and return the most-fitting group.
    """
    group_actions = utils.hue_to_huegely_names(group_actions)
    for group_type in [ExtendedColorGroup, ColorTemperatureGroup, ColorGroup, DimmableGroup]:
        if all([id_action in group_actions for id_action in group_type._identifier_actions]):
            return group_type
    raise Exception("No group type could be found for actions {}".format(group_actions))
