from abc import ABCMeta
from requests import request

from . import exceptions
from .utils import parse_attribute_from_url
from .features import (
    Dimmer,
    ColorController,
    TemperatureController,
)


class Light(metaclass=ABCMeta):
    """ Abstract base class for all lights.
        All lights inherit from ``Light`` and any appropriate feature classes.
    """

    def __init__(self, bridge, light_id, name=None):
        if type(self) is Light:
            raise TypeError("Base class 'Light' should never be instantiated directly.")

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
        return self.bridge.make_request(url, method='PUT', **state)

    def _get_state(self):
        response = self.bridge.make_request(self.light_url)

        # Whenever the state is received, store the name of the object, because we get it for free.
        # This could be done in the constructor, making the name always available,
        # but that would make initialisation extremely expensive.
        self._name = response.get('name', None) or self._name

        return response['state']

    def state(self, **state):
        """ Gets or sets state attributes on a light. Call this without any arguments to get the
            entire state of the light as reported by the Hue bridge.

            Pass in any amount of state attributes to update them, e.g. on=True, bri=100.

            Returns a dictionary of successfully updated attributes in the format of ``{'bri': 100, 'on': True}``
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


class DimmableLight(Light, Dimmer):
    pass


class ColorLight(Light, Dimmer, ColorController):
    pass


class ColorTemperatureLight(Light, Dimmer, TemperatureController):
    pass


class ExtendedColorLight(Light, Dimmer, TemperatureController, ColorController):
    pass


LIGHT_TYPES = {
    'Dimmable light': DimmableLight,
    'Color light': ColorLight,
    'Color temperature light': ColorTemperatureLight,
    'Extended color light': ExtendedColorLight
}


class Bridge(object):
    def __init__(self, ip, username=None):
        self.ip = ip
        self.username = username
        self.base_url = 'http://{}/api/{}/'.format(ip, username)

    def get_token(self, app_identifier):
        """ Gets a new authorisation token. Use this token to initialize a bridge object.

            Arguments:
            ip: ip of bridge
            app_identifier: name of the app (should be unique per bridge)
        """
        url = 'http://{}/api'.format(self.ip)
        response = self.make_request(method='POST', full_url=url, devicetype=app_identifier)
        return response['username']

    def make_request(self, path=None, method='GET', full_url=None, **data):
        """ Utility function for HTTP GET/PUT requests for the API.

            Instead of calling this with the "path" argument which uses the bridge's base url with authentication included,
            you can pass in "full_url" to bypass this behaviour.

            For POST/PUT requests:
            Returns a processed dictionary of updated attributes/values like ``{'bri': 100, 'on': True, 'name': 'new name'}``.

            For GET requests:
            Returns the unmodified api response.

            If any updates fail, a HueError is raised.
        """
        url = full_url or self.base_url + path
        response = request(method, url, json=data, timeout=10)
        data = response.json()

        # Get requests generally return flat and directly usable data, unless an error occured.
        # If an error occurred on a get request, follow the usual POST/GET processing logic
        if method == 'GET' and (type(response) != list or not any(['error' in result for result in response])):
            return data

        # POST/PUT API requests return lists of success/error responses and no helpful status codes.
        # We process the success responses into a single dictionary of updated attributes
        # e.g. {'bri': 100, 'on': True}
        processed_response = {}
        for result in data:
            if 'success' in result:
                resource = result['success']
                resource_url, resource_value = list(resource.items())[0]
                attribute = parse_attribute_from_url(resource_url)
                processed_response[attribute] = resource_value
            else:
                error = result['error']
                raise exceptions.HueError(error['description'], error['type'], device=self)
        return processed_response

    def _get_name(self):
        # There is no hue-specific error handling here because the config endpoint requires no authentication.
        # The only thing that should go wrong here are network errors.
        return self.make_request('config')['name']

    def _set_name(self, name):
        """ Sets a new name for the bridge. Returns the new name. """
        return self.make_request('config', method='PUT', name=name)['name']

    def name(self, name=None):
        """ Gets current name of bridge if called without *name*, sets and returns new name otherwise. """
        return self._set_name(name=name) if name is not None else self._get_name()

    def lights(self):
        """ Gets all light objects for this bridge, sorted by their light_id. """
        data = self.make_request('lights')

        lights = []
        for light_id, light_data in data.items():
            light_type = LIGHT_TYPES[light_data['type']]
            lights.append(light_type(bridge=self, light_id=light_id, name=light_data['name']))

        return sorted(lights, key=lambda l: l.light_id)
