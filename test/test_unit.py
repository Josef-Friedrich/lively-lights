from _helper import config_file, mock_bridge, get_day_night
from unittest import mock
import lively_lights
import os
import unittest
from lively_lights import ReachableLights


class TestClassHue(unittest.TestCase):

    @mock.patch('lively_lights.Bridge')
    def test_environ(self, bridge):
        os.environ['LL_BRIDGE_IP'] = '1.2.3.4'
        os.environ['LL_BRIDGE_USERNAME'] = 'test'

        lively_lights.Hue(config_environ_prefix='LL')
        bridge.assert_called_with('1.2.3.4', 'test', colorize_output=False,
                                  verbosity_level=0)

    @mock.patch('lively_lights.Bridge')
    def test_ini(self, bridge):
        lively_lights.Hue(config_environ_prefix='XX',
                          config_file_path=config_file)
        bridge.assert_called_with('192.168.3.60', 'joseffriedrich',
                                  colorize_output=False, verbosity_level=0)


class TestClassConfiguration(unittest.TestCase):

    def test_environ(self):
        os.environ['AAA_BRIDGE_IP'] = '1.2.3.4'
        os.environ['AAA_BRIDGE_USERNAME'] = 'test'
        config = lively_lights.Configuration(config_environ_prefix='AAA')
        self.assertEqual(config.get('bridge', 'ip'), '1.2.3.4')
        self.assertEqual(config.get('bridge', 'username'), 'test')

    def test_exception(self):
        config = lively_lights.Configuration(config_environ_prefix='AAA')
        with self.assertRaises(ValueError) as cm:
            config.get('lol', 'lol')
        self.assertEqual(
            str(cm.exception),
            'Configuration value could not be found (section “lol” key '
            '“lol”).',
        )


class TestClassReachableLights(unittest.TestCase):

    def get_reachable_lights(self, *light_configs):
        return ReachableLights(mock_bridge(light_configs), get_day_night())

    def test_method_list(self):
        lights = self.get_reachable_lights([1, True], [2, True])
        self.assertEqual(lights.list_light_ids(), [1, 2])

    def test_iterator_all_reachable(self):
        lights = self.get_reachable_lights([1, True], [2, True])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [1, 2])

    def test_iterator_all_unreachable(self):
        lights = self.get_reachable_lights([1, False], [2, False])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [])

    def test_iterator_last_reachable(self):
        lights = self.get_reachable_lights([3, False], [2, True])
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [2])
