from _helper import config_file
from unittest import mock
import lively_lights
import os
import unittest


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

    def test_float_conversion(self):
        config = lively_lights.Configuration(config_file_path=config_file)
        self.assertEqual(config.get('location', 'latitude'), 49.455556)
