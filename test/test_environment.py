import unittest
from lively_lights.environment import Weather, DayNight
from _helper import config_file
from lively_lights import Configuration


class TestClassDayNight(unittest.TestCase):

    def test_day_light(self):
        config = Configuration(config_file_path=config_file)
        day_light = DayNight(config)
        self.assertTrue(day_light)


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
