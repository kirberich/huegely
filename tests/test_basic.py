import unittest
import mock

from huegely import (
    devices,
    exceptions
)


class MockResponse(object):
    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data


class BasicTests(unittest.TestCase):
    def test_registration(self):
        success_data = [{"success": {"username": "test"}}]
        error_data = [{"error": {'type': 110, 'description': 'Fake button not pressed'}}]

        with mock.patch('huegely.devices.request') as mock_request:
            # Fake success
            mock_request.return_value = MockResponse(success_data)
            bridge = devices.Bridge('192.168.1.2')
            bridge.get_token('test_app')
            self.assertTrue(mock_request.called)

            # Fake Error
            mock_request.return_value = MockResponse(error_data)
            with self.assertRaises(exceptions.HueError):
                bridge = devices.Bridge('192.168.1.2')
                bridge.get_token('test_app')
