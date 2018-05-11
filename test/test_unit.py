import unittest
import lively_lights
import os
from unittest import mock
import uuid


class TestClassHue(unittest.TestCase):

    def setUp(self):
        if 'LIVELY_LIGHTS_BRIDGE_IP' in os.environ:
            self.old_ip = os.environ['LIVELY_LIGHTS_BRIDGE_IP']

        if 'LIVELY_LIGHTS_BRIDGE_USERNAME' in os.environ:
            self.old_username = os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME']

        self.config_path = os.path.expanduser('~/.lively-lights.ini')
        if os.path.exists(self.config_path):
            self.backup_path = '{}_{}'.format(self.config_path, uuid.uuid1())
            os.rename(self.config_path, self.backup_path)

    def tearDown(self):
        if hasattr(self, 'old_ip'):
            os.environ['LIVELY_LIGHTS_BRIDGE_IP'] = self.old_ip

        if hasattr(self, 'old_username'):
            os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME'] = self.old_username

        if hasattr(self, 'backup_path'):
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            os.rename(self.backup_path, self.config_path)

    def _del_environs(self, *keys):
        for key in keys:
            if key in os.environ:
                del os.environ[key]

    @mock.patch('lively_lights.Bridge')
    def test_environ(self, bridge):
        os.environ['LIVELY_LIGHTS_BRIDGE_IP'] = '1.2.3.4'
        self.assertEqual(os.environ['LIVELY_LIGHTS_BRIDGE_IP'], '1.2.3.4')

        os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME'] = 'test'
        self.assertEqual(os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME'], 'test')

        lively_lights.Hue()
        bridge.assert_called_with('1.2.3.4', 'test')

    @mock.patch('lively_lights.Bridge')
    def test_ini(self, bridge):
        config = open(self.config_path, 'w')
        config.write('[bridge]\nip = 5.6.7.8\nusername = test2\n')
        config.close()

        self._del_environs('LIVELY_LIGHTS_BRIDGE_IP',
                           'LIVELY_LIGHTS_BRIDGE_USERNAME')

        lively_lights.Hue()
        os.remove(self.config_path)
        bridge.assert_called_with('5.6.7.8', 'test2')


class TestClassConfiguration(unittest.TestCase):

    def setUp(self):
        if 'LIVELY_LIGHTS_BRIDGE_IP' in os.environ:
            self.old_ip = os.environ['LIVELY_LIGHTS_BRIDGE_IP']

        if 'LIVELY_LIGHTS_BRIDGE_USERNAME' in os.environ:
            self.old_username = os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME']

        self.config_path = os.path.expanduser('~/.lively-lights.ini')
        if os.path.exists(self.config_path):
            self.backup_path = '{}_{}'.format(self.config_path, uuid.uuid1())
            os.rename(self.config_path, self.backup_path)

    def tearDown(self):
        if hasattr(self, 'old_ip'):
            os.environ['LIVELY_LIGHTS_BRIDGE_IP'] = self.old_ip

        if hasattr(self, 'old_username'):
            os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME'] = self.old_username

        if hasattr(self, 'backup_path'):
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            os.rename(self.backup_path, self.config_path)

    def _del_environs(self, *keys):
        for key in keys:
            if key in os.environ:
                del os.environ[key]

    def test_environ(self):
        os.environ['LIVELY_LIGHTS_BRIDGE_IP'] = '1.2.3.4'
        os.environ['LIVELY_LIGHTS_BRIDGE_USERNAME'] = 'test'
        config = lively_lights.Configuration()
        self.assertEqual(config.get('bridge', 'ip'), '1.2.3.4')
        self.assertEqual(config.get('bridge', 'username'), 'test')
