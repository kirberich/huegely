import unittest
import mock

from huegely import (
    devices,
    exceptions
)

from . import (
    fake_data,
    test_utils
)


class BridgeTests(unittest.TestCase):
    def test_registration(self):
        success_data = [{"success": {"username": "test"}}]
        error_data = [{"error": {'type': 110, 'description': 'Fake button not pressed'}}]

        with mock.patch('huegely.devices.request') as mock_request:
            # Fake success
            mock_request.return_value = test_utils.MockResponse(success_data)
            bridge = devices.Bridge('192.168.1.2')
            bridge.get_token('test_app')
            self.assertTrue(mock_request.called)

            # Fake Error
            mock_request.return_value = test_utils.MockResponse(error_data)
            with self.assertRaises(exceptions.HueError):
                bridge.get_token('test_app')

    @mock.patch('huegely.devices.request')
    def test_make_request_list_response(self, mock_request):
        """ make_request doesn't attempt to do any processing with list responses, as their
            format is directly usable. (They're used for listing lights/groups/etc)
        """
        data = [{'bri': 100, 'hue': 100}]

        mock_request.return_value = test_utils.MockResponse(data)
        bridge = devices.Bridge('192.168.1.2', 'fake_token')
        response = bridge.make_request('some_path')
        self.assertEqual(data, response)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_CONF))
    def test_get_name(self, mock_request):
        bridge = devices.Bridge('192.168.1.2', 'fake_token')
        self.assertEqual(bridge.name(), fake_data.BRIDGE_CONF['name'])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"name": "new_name"}}]))
    def test_set_name(self, mock_request):
        bridge = devices.Bridge('192.168.1.2', 'fake_token')
        self.assertEqual(bridge.name('new_name'), 'new_name')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS))
    def test_lights(self, mock_request):
        bridge = devices.Bridge('192.168.1.2', 'fake_token')
        lights = bridge.lights()
        self.assertEqual([1, 2], [light.light_id for light in lights])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_GROUPS))
    def test_groups(self, mock_request):
        bridge = devices.Bridge('192.168.1.2', 'fake_token')
        groups = bridge.groups()
        self.assertEqual([1, 2, 3], [group.group_id for group in groups])