import unittest
import mock

from huegely import (
    devices,
    groups,
    utils
)

from . import (
    fake_data,
    test_utils
)


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.fake_bridge = devices.Bridge('127.0.0.1', 'fake_token')
        self.ex_color_group = groups.ExtendedColorGroup(self.fake_bridge, 1)

    def test_group_is_abstract(self):
        with self.assertRaises(TypeError):
            groups.Group(self.fake_bridge, 1)

    def test_repr(self):
        group = groups.DimmableGroup(self.fake_bridge, 1)

        # Without name assigned
        self.assertEqual(repr(group), 'DimmableGroup (unknown name) (id: 1)')

        # With name assigned
        group._name = 'some name'
        self.assertEqual(repr(group), 'DimmableGroup some name (id: 1)')

    def test_str(self):
        group = groups.DimmableGroup(self.fake_bridge, 1)

        # Without name assigned
        self.assertEqual(str(group), '(unknown name)')

        # With name assigned
        group._name = 'some name'
        self.assertEqual(str(group), 'some name')

    @mock.patch('huegely.devices.request')
    def test_brighter(self, mock_request):
        # Brighter/darker require two api requests because the new brightness isn't returned by the first request
        def side_effect(*args, **kwargs):
            def second_call(*args, **kwargs):
                return test_utils.MockResponse(fake_data.BRIDGE_GROUPS['1'])
            mock_request.side_effect = second_call
            return test_utils.MockResponse([{"success": {"bri_inc": 10}}])
        mock_request.side_effect = side_effect

        self.assertEqual(self.ex_color_group.brighter(10), 254)

    @mock.patch('huegely.devices.request')
    def test_darker(self, mock_request):
        # Brighter/darker require two api requests because the new brightness isn't returned by the first request
        def side_effect(*args, **kwargs):
            def second_call(*args, **kwargs):
                return test_utils.MockResponse(fake_data.BRIDGE_GROUPS['1'])
            mock_request.side_effect = second_call
            return test_utils.MockResponse([{"success": {"bri_inc": -10}}])
        mock_request.side_effect = side_effect

        self.assertEqual(self.ex_color_group.darker(10), 254)


    @mock.patch('huegely.devices.request')
    def test_lights(self, mock_request):

        # Getting lights from a group requires two api requests: one to get the list of lights for the group,
        # and one to get the light objects from the api
        def side_effect(*args, **kwargs):
            def second_call(*args, **kwargs):
                return test_utils.MockResponse(fake_data.BRIDGE_LIGHTS)
            mock_request.side_effect = second_call
            return test_utils.MockResponse(fake_data.BRIDGE_GROUPS['3'])
        mock_request.side_effect = side_effect

        # Group for has one light (DimmableLight with id 4)
        group = groups.DimmableGroup(self.fake_bridge, 3)
        lights = group.lights()
        self.assertEqual([2], [light.light_id for light in lights])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"brightness": 200}}]))
    def test_state(self, mock_request):
        # Set state
        self.assertEqual(self.ex_color_group.state(brightness=200), {'brightness': 200})

        # Get state
        mock_request.return_value = test_utils.MockResponse(fake_data.BRIDGE_GROUPS['1'])
        self.assertEqual(self.ex_color_group.state(), utils.hue_to_huegely_names(fake_data.BRIDGE_GROUPS['1']['action']))

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse(fake_data.BRIDGE_GROUPS['1']))
    def test_get_name(self, mock_request):
        self.assertEqual(self.ex_color_group.name(), fake_data.BRIDGE_GROUPS['1']['name'])

    @mock.patch('huegely.devices.request', return_value=test_utils.MockResponse([{"success": {"name": "new_name"}}]))
    def test_set_name(self, mock_request):
        self.assertEqual(self.ex_color_group.name('new_name'), 'new_name')

    def test_get_group_type(self):
        """ Tests the determination of group light types by checking a set of available actions. """
        self.assertEqual(groups.get_group_type({
            'alert': 'none',
            'bri': 254,
            'colormode': 'hs',
            'ct': 331,
            'effect': 'none',
            'hue': 15910,
            'on': True,
            'sat': 112,
            'xy': [0.4374, 0.4063]
        }), groups.ExtendedColorGroup)

        self.assertEqual(groups.get_group_type({'bri': 200}), groups.DimmableGroup)
        self.assertEqual(groups.get_group_type({'bri': 200, 'ct': 200}), groups.ColorTemperatureGroup)
        self.assertEqual(groups.get_group_type({'bri': 200, 'hue': 100}), groups.ColorGroup)
        with self.assertRaises(Exception):
            groups.get_group_type({'i_dont_exist': 200})
