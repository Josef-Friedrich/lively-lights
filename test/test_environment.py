import unittest
from lively_lights.environment import \
    DayNight, \
    is_host_pingable, \
    is_host_reachable, \
    Weather
from _helper import config_file
from lively_lights import Configuration
import os
import pwd

INTERNET_CONNECTIFITY = is_host_reachable('8.8.8.8', 53)


def get_username():
    return pwd.getpwuid(os.getuid()).pw_name


@unittest.skipIf(not INTERNET_CONNECTIFITY or get_username() != 'root',
                 'No internet connectifity')
class TestFunctionIsHostPingable(unittest.TestCase):

    def test_is_pingable(self):
        self.assertTrue(is_host_pingable('8.8.8.8'))

    def test_is_not_pingable(self):
        self.assertFalse(is_host_pingable('192.0.0.1'))


@unittest.skipIf(not INTERNET_CONNECTIFITY, 'No internet connectifity')
class TestFunctionIsHostReachable(unittest.TestCase):

    def test_is_reachable(self):
        self.assertTrue(is_host_reachable('8.8.8.8', 53))

    def test_is_not_reachable(self):
        self.assertFalse(is_host_reachable('8.8.8.8', 52))


class TestClassDayNight(unittest.TestCase):

    def setUp(self):
        config = Configuration(config_file_path=config_file)
        self.day_light = DayNight(config)

    def test_init(self):
        self.assertTrue(self.day_light)

    def test_sunrise(self):
        self.assertTrue(int(self.day_light._sunrise().year))

    def test_sunset(self):
        self.assertTrue(int(self.day_light._sunset().year))

    def test_is_day(self):
        self.assertTrue(bool(self.day_light.is_day()) ==
                        self.day_light.is_day())

    def test_is_night(self):
        self.assertTrue(bool(self.day_light.is_night()) ==
                        self.day_light.is_night())


@unittest.skipIf(not INTERNET_CONNECTIFITY, 'No internet connectifity')
class TestClassWeather(unittest.TestCase):

    def setUp(self):
        config = Configuration(config_file_path=config_file)
        self.weather = Weather(config)

    def test_init(self):
        config = Configuration(config_file_path=config_file)
        self.assertTrue(Weather(config))

    def test_method_get_wind(self):
        self.assertTrue(self.weather.get_wind())

    def test_method_get_temperature(self):
        self.assertTrue(self.weather.get_temperature())

    def test_location(self):
        self.assertEqual(self.weather._location.get_name(), 'Nuremberg')
