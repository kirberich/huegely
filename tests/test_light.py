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


class LightTests(unittest.TestCase):
    def setUp(self):
        self.fake_bridge = devices.Bridge('127.0.0.1', 'fake_token')
        self.ex_color_light = devices.ExtendedColorLight(self.fake_bridge, 1)

    def test_light_is_abstract(self):
        with self.assertRaises(TypeError):
            devices.Light(self.fake_bridge, 1)

    def test_repr(self):
        light = devices.DimmableLight(self.fake_bridge, 1)

        # Without name assigned
        self.assertEqual(repr(light), 'DimmableLight (unknown name) (id: 1)')

        # With name assigned
        light._name = 'some name'
        self.assertEqual(repr(light), 'DimmableLight some name (id: 1)')

    def test_str(self):
        light = devices.DimmableLight(self.fake_bridge, 1)

        # Without name assigned
        self.assertEqual(str(light), '(unknown name)')

        # With name assigned
        light._name = 'some name'
        self.assertEqual(str(light), 'some name')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1']))
    def test_get_state(self, mock_request):
        state = self.ex_color_light.state()

        # Check the name mapping works
        self.assertTrue('brightness' in state)
        self.assertFalse('bri' in state)

    @mock.patch('huegely.devices.request')
    def test_set_state(self, mock_request):
        mock_request.return_value = test_utils.MockResponse([{"success": {"bri": 254}}])

        state = self.ex_color_light.state(brightness=254)

        self.assertEqual(state['brightness'], 254)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1']))
    def test_get_name(self, mock_request):
        self.assertEqual(self.ex_color_light.name(), fake_data.BRIDGE_LIGHTS['1']['name'])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"name": "new_name"}}]))
    def test_set_name(self, mock_request):
        self.assertEqual(self.ex_color_light.name('new_name'), 'new_name')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1']))
    def test_is_reachable(self, mock_request):
        self.assertEqual(self.ex_color_light.is_reachable(), fake_data.BRIDGE_LIGHTS['1']['state']['reachable'])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"brightness": 254}}]))
    def test_brighter(self, mock_request):
        # light is already on
        self.assertEqual(self.ex_color_light.brighter(), 254)

        # light is off
        # Testing the light is off case is slightly tricky, the first call to request needs to make
        # make_request raise an exception, but the second should succeed.
        def side_effect(*args, **kwargs):
            def second_call(*args, **kwargs):
                return test_utils.MockResponse([{"success": {"brightness": 254}}])
            mock_request.side_effect = second_call
            return test_utils.MockResponse([{"error": {"type": 201, "address": "don't care", "description": "Don't care"}}])

        mock_request.side_effect = side_effect
        self.assertEqual(self.ex_color_light.brighter(), 254)

        # any other error
        mock_request.side_effect = None
        mock_request.return_value = test_utils.MockResponse([{"error": {"type": 0, "address": "don't care", "description": "Don't care"}}])
        with self.assertRaises(exceptions.HueError):
            self.ex_color_light.brighter()

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"brightness": 200}}]))
    def test_darker(self, mock_request):
        # light is on
        self.assertEqual(self.ex_color_light.darker(), 200)

        # light is off
        mock_request.return_value = test_utils.MockResponse([{"error": {"type": 201, "address": "don't care", "description": "Don't care"}}])
        self.assertEqual(self.ex_color_light.darker(), 0)

        # Other errors
        mock_request.return_value = test_utils.MockResponse([{"error": {"type": 0, "address": "don't care", "description": "Don't care"}}])
        with self.assertRaises(exceptions.HueError):
            self.ex_color_light.darker()

        # Brightness goes down to 0, lamp is turned off
        with mock.patch.object(self.ex_color_light, 'off'):
            mock_request.return_value = test_utils.MockResponse([{"success": {"brightness": 0}}])
            self.ex_color_light.darker()
            self.assertTrue(self.ex_color_light.off.called)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"brightness": 200}}]))
    def test_brightness(self, mock_request):
        # Set brightness
        self.assertEqual(self.ex_color_light.brightness(200), 200)

        # Get brightness
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.brightness(), 254)

        # light is off
        mock_request.return_value = test_utils.MockResponse([{"error": {"type": 201, "address": "don't care", "description": "Don't care"}}])
        self.assertEqual(self.ex_color_light.brightness(200), 0)

        # Other errors
        mock_request.return_value = test_utils.MockResponse([{"error": {"type": 0, "address": "don't care", "description": "Don't care"}}])
        with self.assertRaises(exceptions.HueError):
            self.ex_color_light.brightness(200)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"on": True}}]))
    def test_on(self, mock_request):
        self.assertEqual(self.ex_color_light.on(), True)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"on": False}}]))
    def test_off(self, mock_request):
        self.assertEqual(self.ex_color_light.off(), False)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1']))
    def test_is_on(self, mock_request):
        self.assertEqual(self.ex_color_light.is_on(), True)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"alert": 'select'}}]))
    def test_alert(self, mock_request):
        # Set alert
        self.assertEqual(self.ex_color_light.alert('select'), 'select')

        # Get alert
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.alert(), 'none')

        # Invalid value
        with self.assertRaises(exceptions.HueError):
            self.ex_color_light.alert('invalid')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"coordinates": [0.5, 0.5]}}]))
    def test_coordinates(self, mock_request):
        # Set coordinates
        self.assertEqual(self.ex_color_light.coordinates([0.5, 0.5]), [0.5, 0.5])

        # Get coordinates
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.coordinates(), [0.5, 0.5])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"hue": 14678}}]))
    def test_hue(self, mock_request):
        # Set hue
        self.assertEqual(self.ex_color_light.hue(14678), 14678)

        # Get hue
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.hue(), 14678)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"saturation": 254}}]))
    def test_saturation(self, mock_request):
        # Set saturation
        self.assertEqual(self.ex_color_light.saturation(254), 254)

        # Get saturation
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.saturation(), 254)

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"effect": 'colorloop'}}]))
    def test_effect(self, mock_request):
        # Set effect
        self.assertEqual(self.ex_color_light.effect('colorloop'), 'colorloop')

        # Get effect
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.effect(), 'none')

        # Invalid value
        with self.assertRaises(exceptions.HueError):
            self.ex_color_light.effect('invalid')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1']))
    def test_color_mode(self, mock_request):
        self.assertEqual(self.ex_color_light.color_mode(), 'hs')

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"temperature": 154}}]))
    def test_temperature(self, mock_request):
        # Set temperature
        self.assertEqual(self.ex_color_light.temperature(100), 154)

        # Get temperature
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_LIGHTS['1'])
        self.assertEqual(self.ex_color_light.temperature(), 154)
