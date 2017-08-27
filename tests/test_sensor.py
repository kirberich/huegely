import unittest
import mock
from datetime import datetime

from huegely import (
    bridge,
    sensors,
)

from . import (
    fake_data,
    test_utils
)


class SensorTests(unittest.TestCase):
    def setUp(self):
        self.fake_bridge = bridge.Bridge('127.0.0.1', 'fake_token')
        self.temperature_sensor = sensors.TemperatureSensor(self.fake_bridge, 1)
        self.motion_sensor = sensors.MotionSensor(self.fake_bridge, 2)

    @mock.patch('huegely.bridge.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_SENSORS['1']))
    def test_get_state(self, mock_request):
        state = self.temperature_sensor.state()

        self.assertTrue('temperature' in state)

    @mock.patch('huegely.bridge.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_SENSORS['1']))
    def test_temperature(self, mock_request):
        self.assertEqual(self.temperature_sensor.temperature(), 22.14)

    @mock.patch('huegely.bridge.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_SENSORS['2']))
    def test_presence(self, mock_request):
        self.assertEqual(self.motion_sensor.presence(), False)

    @mock.patch('huegely.bridge.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_SENSORS['2']))
    def test_last_updated(self, mock_request):
        self.assertEqual(self.motion_sensor.last_updated(), datetime(year=2017, month=8, day=27, hour=18, minute=22, second=21))

    @mock.patch('huegely.bridge.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_SENSORS['1']))
    def test_cache(self, mock_request):
        """Test sensor caching - requests should only be made if the data is older than specified."""
        # Set up the sensor - this should cause no requests
        sensor = sensors.MotionSensor(self.fake_bridge, 2, state=fake_data.BRIDGE_SENSORS['1']['state'])
        assert mock_request.call_count == 0

        # Get the state - because the sensor was instantiated with data and we're specifying max_age, this shouldn't cause a request.
        sensor.state(max_age=10)
        assert mock_request.call_count == 0

        # Now we ask for the state with no max_age, a request should be made.
        sensor.state()
        assert mock_request.call_count == 1
