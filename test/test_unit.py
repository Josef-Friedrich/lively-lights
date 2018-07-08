from _helper import config_file
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


def mock_light(light_id, reachable=True):
    light = mock.MagicMock()
    light.light_id = light_id
    light.reachable = reachable
    return light


def mock_get_item(self, key):
    for light in self.lights:
        if light.light_id == key:
            return light


def mock_bridge(light_configs):
    lights = []
    for light_config in light_configs:
        lights.append(mock_light(light_config[0], light_config[1]))
    bridge = mock.MagicMock()
    bridge.lights = lights
    bridge.__getitem__ = mock_get_item
    return bridge


class TestClassReachableLights(unittest.TestCase):

    def test_init(self):
        ReachableLights(mock.MagicMock())

    def test_method_list(self):
        bridge = mock_bridge([[1, True], [2, True]])
        lights = ReachableLights(bridge)
        self.assertEqual(lights.list_light_ids(), [1, 2])

    def test_iterator_all_reachable(self):
        lights = ReachableLights(mock_bridge([[1, True], [2, True]]))
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [1, 2])

    def test_iterator_all_unreachable(self):
        lights = ReachableLights(mock_bridge([[1, False], [2, False]]))
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [])

    def test_iterator_last_reachable(self):
        lights = ReachableLights(mock_bridge([[3, False], [2, True]]))
        result = []
        for light in lights:
            result.append(light.light_id)
        self.assertEqual(result, [2])
