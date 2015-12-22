from huegely import (
    features,
    utils,
)


class Group(object):
    _identifier_actions = []  # Minimum set of group actions required to identify the group type
    _state_attribute = 'action'

    def __init__(self, bridge, device_id, name=None):
        self.bridge = bridge
        self.device_id = device_id
        self.device_url = 'groups/{}'.format(device_id)

        self._name = name

    def lights(self):
        """ Returns all lights that belong to this group. """
        light_ids = [int(light_id) for light_id in self.bridge.make_request(self.device_url)['lights']]
        return [light for light in self.bridge.lights() if light.device_id in light_ids]


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
