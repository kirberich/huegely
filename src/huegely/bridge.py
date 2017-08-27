from requests import request

from huegely import (
    exceptions,
    groups,
    utils,
)
from huegely.lights import LIGHT_TYPES
from huegely.sensors import SENSOR_TYPES


class Bridge(object):
    def __init__(self, ip, username=None, transition_time=None):
        self.ip = ip
        self.username = username
        self.base_url = 'http://{}/api/{}/'.format(ip, username)

        # Global transition time. If set, this is applied to all actions on this bridge.
        self.transition_time = transition_time

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
            Returns a processed dictionary of updated attributes/values like
            ``{'brightness': 100, 'on': True, 'name': 'new name'}``.

            For GET requests:
            Returns the unmodified api response.

            If any updates fail, a HueError is raised.
        """
        url = full_url or self.base_url + path
        response = request(method, url, json=data, timeout=10)
        response_data = response.json()

        if not response_data:
            raise exceptions.HueError(
                'Something unexpected happened and the API returned nothing, not even an error. Data: {}'.format(data)
            )

        # Get requests generally return flat and directly usable data, unless an error occured.
        # If an error occurred on a get request, follow the usual POST/GET processing logic
        if method == 'GET' and (type(response) != list or not any(['error' in result for result in response])):
            return response_data

        # POST/PUT API requests return lists of success/error responses and no helpful status codes.
        # We process the success responses into a single dictionary of updated attributes
        # e.g. {'bri': 100, 'on': True}
        processed_response = {}
        for result in response_data:
            if 'success' in result:
                resources = result['success']
                for resource_url, resource_value in resources.items():
                    attribute = utils.parse_attribute_from_url(resource_url)
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
        """ Gets all light objects for this bridge, sorted by their device_id. """
        data = self.make_request('lights')

        found_lights = []
        for device_id, light_data in data.items():
            light_type = LIGHT_TYPES[light_data['type']]
            found_lights.append(
                light_type(
                    bridge=self,
                    device_id=int(device_id),
                    name=light_data['name'],
                    transition_time=self.transition_time
                )
            )

        return sorted(found_lights, key=lambda l: l.device_id)

    def groups(self):
        """ Gets all group objects for this bridge, sorted by their device_id. """
        data = self.make_request('groups')

        found_groups = []
        for device_id, group_data in data.items():
            group_type = groups.get_group_type(group_data['action'])
            found_groups.append(
                group_type(
                    bridge=self,
                    device_id=int(device_id),
                    name=group_data['name'],
                    transition_time=self.transition_time
                )
            )

        return sorted(found_groups, key=lambda l: l.device_id)

    def sensors(self):
        data = self.make_request('sensors')

        found_sensors = []
        for device_id, sensor_data in data.items():
            sensor_type = sensor_data['type']
            if sensor_type not in SENSOR_TYPES:
                print("Sensor type {} not supported".format(sensor_type))
                continue

            sensor_type = SENSOR_TYPES[sensor_data['type']]
            found_sensors.append(
                sensor_type(
                    bridge=self,
                    device_id=int(device_id),
                    name=sensor_data['name'],
                    transition_time=self.transition_time
                )
            )

        return sorted(found_sensors, key=lambda l: l.device_id)
