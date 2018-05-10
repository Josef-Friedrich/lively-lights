import unittest
import lively_lights
import os
from unittest import mock


class TestClassHue(unittest.TestCase):

    @mock.patch('lively_lights.Bridge')
    def test_environ(self, bridge):
        old_ip = None
        old_username = None
        if 'LIVELY_LIGHTS_IP' in os.environ:
            old_ip = os.environ['LIVELY_LIGHTS_IP']

        if 'LIVELY_LIGHTS_USERNAME' in os.environ:
            old_username = os.environ['LIVELY_LIGHTS_USERNAME']

        os.environ['LIVELY_LIGHTS_IP'] = '1.2.3.4'
        self.assertEqual(os.environ['LIVELY_LIGHTS_IP'], '1.2.3.4')

        os.environ['LIVELY_LIGHTS_USERNAME'] = 'test'
        self.assertEqual(os.environ['LIVELY_LIGHTS_USERNAME'], 'test')

        lively_lights.Hue()
        bridge.assert_called_with('1.2.3.4', 'test')

        if old_ip:
            os.environ['LIVELY_LIGHTS_IP'] = old_ip

        if old_username:
            os.environ['LIVELY_LIGHTS_USERNAME'] = old_username
